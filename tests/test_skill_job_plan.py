"""End-to-end checks for the existing Ferrari Skill -> orchestrator path."""
import base64
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from engine import skill_job


def request(steps, **extra):
    return {"version": 1, "id": "plan-real-test", "kind": "plan",
            "plan": {"version": 1, "steps": steps}, **extra}


class SkillPlanTests(unittest.TestCase):
    def _execute(self, data, directory):
        # The actual GitHub Actions runner is Ubuntu; make the unit test
        # independent of the developer machine distribution.
        with patch.object(skill_job.orchestrator.ferrari, "system",
                          return_value={"distro": "ubuntu"}):
            return skill_job.execute(data, Path(directory) / "job")

    def test_two_real_generators_and_returned_zip(self):
        data = request([
            {"id": "site", "operation": "web-template", "title": "Ferrari Loja", "layout": "store"},
            {"id": "cartaz", "operation": "svg-poster", "title": "Ferrari Campanha"}])
        with tempfile.TemporaryDirectory() as directory:
            result, code = self._execute(data, directory)
            self.assertEqual(code, 0, result)
            self.assertEqual(result["status"], "completed")
            self.assertEqual(result["executor"], "ferrari-orchestrator")
            with zipfile.ZipFile(Path(directory) / "job" / "response.zip") as response:
                names = response.namelist()
                self.assertIn("report.json", names)
                self.assertTrue(any(x.endswith(".html") for x in names), names)
                self.assertTrue(any(x.endswith(".svg") for x in names), names)
                self.assertTrue(any(x.endswith("/report.json") and "ferrari-" in x for x in names))
                self.assertIn("Ferrari Loja", b" ".join(response.read(x)
                    for x in names if x.endswith(".html")).decode("utf-8"))

    def test_parallel_dag_outputs_are_zipped_when_workspace_uses_project_alias(self):
        data = request([
            {"id": "site", "operation": "web-template", "title": "Ferrari Root Alias"},
            {"id": "cartaz", "operation": "svg-poster", "title": "Ferrari Root Alias"}
        ], max_parallel=2)
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            physical=root/"srv/projects/skill-universal/.runtime/skill-results"
            physical.mkdir(parents=True)
            alias=root/"home/ubuntu/.local/share/motor-ferrari/.runtime/skill-results"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(physical,target_is_directory=True)
            with patch.object(skill_job.orchestrator.ferrari, "system",
                              return_value={"distro":"ubuntu"}):
                response,code=skill_job.execute(data,alias/"job")
            self.assertEqual(code,0,response)
            self.assertEqual(response["status"],"completed")
            self.assertNotIn("error",response)
            self.assertTrue(all(x.startswith("artifacts/") for x in response["artifacts"]))
            with zipfile.ZipFile(alias/"job/response.zip") as archive:
                names=archive.namelist()
                self.assertIn("report.json",names)
                self.assertTrue(any(n.endswith(".html") for n in names),names)
                self.assertTrue(any(n.endswith(".svg") for n in names),names)
                manifest=json.loads(archive.read("report.json"))
                self.assertEqual(manifest["artifacts"],response["artifacts"])

    def test_report_cannot_claim_completed_when_output_outside_job(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            foreign=root/"other-project/secret.txt"
            foreign.parent.mkdir()
            foreign.write_text("sensitive")
            fake={"result":{"status":"completed","failed":{},"completed":{}},
                  "report_file":str(foreign)}
            with patch.object(skill_job.orchestrator,"orchestrate",return_value=fake):
                result,code=self._execute(request([
                    {"id":"site","operation":"web-template"}]),directory)
            self.assertEqual(code,2)
            self.assertEqual(result["status"],"failed")
            self.assertIn("outside",result.get("error",""))
            self.assertTrue(foreign.is_file())

    def test_dependent_generators_without_new_coordinator(self):
        data = request([
            {"id": "site", "operation": "web-template", "title": "Ferrari Dependencia"},
            {"id": "extrair", "operation": "binary-strings",
             "depends_on": ["site"], "input_from": "site"}])
        with tempfile.TemporaryDirectory() as directory:
            result, code = self._execute(data, directory)
            self.assertEqual(code, 0, result)
            with zipfile.ZipFile(Path(directory) / "job" / "response.zip") as response:
                texts = [response.read(x) for x in response.namelist() if x.endswith("strings.txt")]
                self.assertEqual(len(texts), 1)
                self.assertIn(b"Ferrari Dependencia", texts[0])

    @unittest.skipUnless(shutil.which("file"), "The file binary is unavailable")
    def test_uploaded_file_passes_to_existing_tool_action(self):
        file_bytes = b'{"ferrari":true}\n'
        data = request([{"id": "identificar", "operation": "tool",
                         "tool": "file", "action": "file-mime", "input": "$input"}],
                       input={"name": "teste.json",
                              "content_base64": base64.b64encode(file_bytes).decode("ascii")})
        with tempfile.TemporaryDirectory() as directory:
            result, code = self._execute(data, directory)
            self.assertEqual(code, 0, result)
            with zipfile.ZipFile(Path(directory) / "job" / "response.zip") as response:
                found = [response.read(x) for x in response.namelist() if x.endswith("mime.txt")]
                self.assertEqual(len(found), 1)
                self.assertIn(b"json", found[0])

    def test_plan_rejects_host_paths_and_unknown_operations(self):
        bad_steps = [
            [{"id": "host", "operation": "pdf-text", "input": "/etc/passwd"}],
            [{"id": "host", "operation": "pdf-text", "input": "../outside.pdf"}],
            [{"id": "host", "operation": "pdf-text", "input": "$input"}],
            [{"id": "shell", "operation": "shell"}],
            [{"id": "a", "operation": "web-template", "depends_on": ["b"]},
             {"id": "b", "operation": "svg-poster", "depends_on": ["a"]}]]
        for steps in bad_steps:
            with self.subTest(steps=steps), self.assertRaises(ValueError):
                skill_job.validate_job(request(steps))

    def test_invalid_parallelism_and_extra_top_level_fields(self):
        steps = [{"id": "site", "operation": "web-template"}]
        for extra in ({"max_parallel": True}, {"max_parallel": 5},
                      {"max_parallel": 0}, {"command": "echo hello"}):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                skill_job.validate_job(request(steps, **extra))
        with self.assertRaises(ValueError):
            skill_job.validate_job({"version": 1, "id": "x", "kind": "inventory",
                                    "plan": {"version": 1, "steps": steps}})

    def test_bad_stage_does_not_report_completed(self):
        steps = [{"id": "site", "operation": "web-template"}]
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(skill_job.orchestrator.ferrari, "run",
                              side_effect=RuntimeError("failure from actual executor")):
                result, code = self._execute(request(steps), directory)
            self.assertEqual(code, 2)
            self.assertEqual(result["status"], "failed")
            self.assertIn("failure from actual executor", result.get("error", ""))
            self.assertTrue((Path(directory) / "job" / "response.zip").is_file())


if __name__ == "__main__":
    unittest.main()
