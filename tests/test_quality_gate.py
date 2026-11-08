"""Regression coverage for real-world Ferrari acceptance, not mere file existence."""
import base64
from array import array
import json
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import quality_gate, skill_job, ruflo_host


def encoded(name, content):
    return {"name": name, "content_base64": base64.b64encode(content).decode("ascii")}


class AcceptanceTests(unittest.TestCase):
    def test_requires_real_technical_output_not_just_extension(self):
        with TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "fake.pdf").write_bytes(b"this is not a pdf")
            report = quality_gate.inspect([root / "fake.pdf"],
                {"required_extensions": [".pdf"]})
            self.assertEqual(report["status"], "failed")
            self.assertIn("Invalid PDF signature", report["failures"])
            (root / "valid.pdf").write_bytes(b"%PDF-1.7\nmock")
            success = quality_gate.inspect([root / "valid.pdf"],
                {"required_extensions": [".pdf"]})
            self.assertEqual(success["status"], "passed")
            self.assertTrue(success["acceptance_requested"])

    def test_missing_required_format_is_not_completed(self):
        with TemporaryDirectory() as folder:
            data = {"version": 1, "id": "video-request-qa", "kind": "operation",
                    "operation": "svg-poster",
                    "acceptance": {"required_extensions": [".mp4"]}}
            outcome, code = skill_job.execute(data, Path(folder) / "job")
            self.assertEqual(code, 2)
            self.assertEqual(outcome["status"], "failed")
            self.assertEqual(outcome["quality_gate"]["status"], "failed")
            self.assertIn("Missing required artifact extension: .mp4",
                          outcome["quality_gate"]["failures"])
            self.assertTrue((Path(folder) / "job" / "response.zip").is_file())

    def test_real_artifact_satisfies_explicit_output_contract(self):
        with TemporaryDirectory() as folder:
            data = {"version": 1, "id": "poster-real-qa", "kind": "operation",
                    "operation": "svg-poster",
                    "acceptance": {"required_extensions": [".svg"]}}
            outcome, code = skill_job.execute(data, Path(folder) / "job")
            self.assertEqual(code, 0, outcome)
            self.assertEqual(outcome["quality_gate"]["status"], "passed")

    def test_invalid_acceptance_does_not_enable_arbitrary_commands(self):
        base = {"version": 1, "id": "no-arbitrary", "kind": "operation",
                "operation": "svg-poster"}
        for value in [{"shell": "run"}, {"audible_audio": "true"},
                      {"required_extensions": ["../../secret"]},
                      {"required_extensions": []}]:
            with self.assertRaises(ValueError):
                skill_job.validate_job({**base, "acceptance": value})
        for kind in ["inventory", "ruflo-team", "rea-mcp"]:
            with self.assertRaises(ValueError):
                skill_job.validate_job({**base, "kind": kind,
                    "acceptance": {"required_extensions": [".txt"]}})

    def test_silence_and_real_audio_are_distinguished(self):
        with TemporaryDirectory() as folder:
            media = Path(folder) / "video.mp4"
            media.write_bytes(b"\x00\x00\x00\x18ftypisom")
            def fake_binaries(name):
                return "/tmp/private-" + name
            def response(argv, **kwargs):
                if "ffprobe" in argv[0]:
                    return subprocess.CompletedProcess(argv, 0,
                         stdout=json.dumps({"streams": [{"index": 0, "codec_name": "aac"}]}),
                         stderr="")
                value = response.audio_value
                pcm = array("h", [value] * 8000).tobytes()
                return subprocess.CompletedProcess(argv, 0, stdout=pcm, stderr=b"")
            with patch.object(quality_gate, "_owned_binary", side_effect=fake_binaries):
                with patch.object(quality_gate.subprocess, "run", side_effect=response):
                    response.audio_value = 0
                    failed = quality_gate.inspect([media], {"audible_audio": True})
                    self.assertEqual(failed["status"], "failed")
                    self.assertTrue(any("Silent" in x for x in failed["failures"]))
                    response.audio_value = 4000
                    passed = quality_gate.inspect([media], {"audible_audio": True})
                    self.assertEqual(passed["status"], "passed")
                    self.assertTrue(next(c for c in passed["checks"]
                                         if c["check"] == "audible-audio")["audible"])

    def test_browser_evidence_requires_real_browser_results_not_just_png_and_json(self):
        with TemporaryDirectory() as folder:
            p=Path(folder)/"site.html"
            p.write_text("<html></html>")
            missing=quality_gate.inspect([p],{"browser_evidence":True})
            self.assertEqual(missing["status"],"failed")
            report=Path(folder)/"browser-check.json"
            report.write_text(json.dumps({"status":"passed"}))
            files=[p,report]
            png_header=bytes.fromhex("89504e470d0a1a0a")+"0".encode()*8+(320).to_bytes(4,"big")+(240).to_bytes(4,"big")
            for name in ("browser-screenshot.png","browser-mobile.png"):
                image=Path(folder)/name
                image.write_bytes(png_header+b"other image bytes")
                files.append(image)
            false_positive=quality_gate.inspect(files,{"browser_evidence":True})
            self.assertEqual(false_positive["status"],"failed")
            self.assertTrue(any("Mobile" in x or "Playwright" in x for x in false_positive["failures"]))
            valid={
                "status":"passed",
                "viewport":{"width":1280,"height":720},
                "body_text_chars":50,"dom_ready":"complete",
                "mobile":{"viewport":{"width":390,"height":844},
                          "viewport_meta_present":True,
                          "horizontal_overflow_px":0,
                          "spotcheck_status":"clear","findings":[]},
                "interactions":{"status":"clear","findings":[]},
                "navigation":{"status":"clear","links_total":2,
                              "internal_files_verified":1,"fragments_verified":1,
                              "external_unverified":0,"schemes_unverified":0,
                              "spa_routes_unverified":0,"findings":[]},
                "page_errors":[],"console_errors":[],"blocked_external":[]
            }
            report.write_text(json.dumps(valid))
            success=quality_gate.inspect(files,{"browser_evidence":True})
            self.assertEqual(success["status"],"passed",success)
            self.assertTrue(success["warnings"])
            for edit in (
                {"mobile":{**valid["mobile"],"horizontal_overflow_px":215}},
                {"mobile":{**valid["mobile"],"spotcheck_status":"findings",
                            "findings":["Horizontal overflow"]}},
                {"interactions":{"status":"findings","findings":["Tab did not move"]}},
                {"blocked_external":["https://invalid.example/script.js"]},
                {"console_errors":["Uncaught error"]},
                {"navigation":{**valid["navigation"],"status":"findings",
                               "findings":["Non-functional link destination: #"]}},
                {"navigation":{**valid["navigation"],"spa_routes_unverified":1}},
                {"navigation":{**valid["navigation"],"links_total":"2"}},
            ):
                report.write_text(json.dumps({**valid,**edit}))
                rejected=quality_gate.inspect(files,{"browser_evidence":True})
                self.assertEqual(rejected["status"],"failed",edit)



class _FakeMCP:
    def __init__(self, _folder):
        self.agent = 0
        self.task = 0

    def start(self):
        return None

    def close(self):
        return None

    def tool(self, name, _args):
        if name == "swarm_init":
            return {"success": True, "swarmId": "qa-ruflo"}
        if name == "agent_spawn":
            self.agent += 1
            return {"success": True, "agentId": "qa-agent-" + str(self.agent)}
        if name == "task_create":
            self.task += 1
            return {"success": True, "taskId": "qa-task-" + str(self.task)}
        return {"success": True}


class RufloQualityTests(unittest.TestCase):
    def _job(self):
        return {"version": 1, "id": "ruflo-qa", "kind": "ruflo-host",
                "host": "ChatGPT",
                "roles": [{"id": "coder", "type": "coder"},
                          {"id": "reviewer", "type": "reviewer"}],
                "input": encoded("input.json", b'{"ok":true}'),
                "steps": [
                    {"id": "transform", "role": "coder", "kind": "invoke",
                     "action": "jq-format-json"},
                    {"id": "review-output", "role": "reviewer", "kind": "review",
                     "input_from": "transform",
                     "acceptance": {"required_extensions": [".json"]}},
                ]}

    def test_review_has_real_previous_tool_evidence(self):
        job = self._job()
        self.assertTrue(ruflo_host.validate_job(job))
        with TemporaryDirectory() as folder:
            home = Path(folder)
            (home / ".runtime").mkdir()
            src = home / "source.json"
            src.write_bytes(b'{"ok":true}')
            def fake_invoke(_action, _source, dest, _query=None):
                out = Path(dest)
                out.mkdir()
                created = out / "formatted.json"
                created.write_text('{"ok":true}')
                return {"confirmed": True, "artifacts": [str(created)],
                        "executor": str(home / "tools/jq")}
            with (patch.object(ruflo_host, "HOME", home),
                  patch.object(ruflo_host, "RufloMCP", _FakeMCP),
                  patch.object(ruflo_host.tool_runtime, "invoke", side_effect=fake_invoke)):
                result = ruflo_host.run(job, home / "output", src)
            self.assertTrue(result["confirmed"])
            report = json.loads((home / "output" / "ruflo-host-report.json").read_text())
            self.assertEqual(report["verified_quality_reviews"], 1)
            self.assertFalse(report["unreviewed_roles_are_only_ledger_entries"])
            verified = json.loads((home / "output" / "review-output" / "quality-review.json").read_text())
            self.assertEqual(verified["quality"]["status"], "passed")
            self.assertEqual(verified["source_task"], "transform")
            self.assertEqual(len(verified["verified_inputs"][0]["sha256"]), 64)

    def test_unrelated_rea_step_is_not_real_review(self):
        job = self._job()
        job["steps"][1] = {"id": "unrelated", "role": "reviewer",
            "kind": "rea-mcp", "mcp_requests": [{"method": "tools/list"}]}
        self.assertTrue(ruflo_host.validate_job(job))
        with self.assertRaises(ValueError):
            bad = self._job()
            bad["steps"][1]["input_from"] = "not-completed"
            ruflo_host.validate_job(bad)


if __name__ == "__main__":
    unittest.main()
