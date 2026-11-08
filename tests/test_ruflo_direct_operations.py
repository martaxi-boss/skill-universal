"""Ruflo host-led teams call real Ferrari base-operation interfaces, not shell."""
import base64
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import agent_team, skill_job


class FakeRuflo:
    calls = []

    def __init__(self, _workspace):
        self.agents = 0
        self.tasks = 0

    def start(self):
        self.calls.append("start")

    def close(self):
        self.calls.append("close")

    def tool(self, name, _args):
        self.calls.append(name)
        if name == "swarm_init":
            return {"success": True, "swarmId": "temporary-ruflo"}
        if name == "agent_spawn":
            self.agents += 1
            return {"success": True, "agentId": str(self.agents)}
        if name == "task_create":
            self.tasks += 1
            return {"success": True, "taskId": str(self.tasks)}
        return {"success": True}


def start_request():
    data = b"$fn=32; difference() { cylinder(d=20,h=10); cylinder(d=10,h=10); }\n"
    return {
        "version": 1, "id": "cad-operation-start", "kind": "ruflo-team",
        "team_id": "direct-cad-operation", "phase": "start",
        "host": "ChatGPT", "mission": "Make a real CAD STL and verify it independently",
        "roles": [
            {"id": "maker", "type": "coder", "actions": ["operation:cad-stl"]},
            {"id": "reviewer", "type": "reviewer", "actions": []},
        ],
        "tasks": [{
            "id": "cad", "role": "maker", "reviewer": "reviewer",
            "goal": "Export a private OpenSCAD STL with Ferrari cad-stl",
            "depends_on": [],
        }],
        "input": {"name": "fixture.scad", "content_base64": base64.b64encode(data).decode()},
    }


def turn(revision, role, kind, **fields):
    return {
        "version": 1, "id": "direct-operation-round-" + str(revision),
        "kind": "ruflo-team", "team_id": "direct-cad-operation",
        "phase": "turn", "revision": revision,
        "turn": {"task": "cad", "role": role, "kind": kind,
                 "message": "Execute and verify the selected Ferrari CAD operation.", **fields},
    }


class RufloCatalogOperationTests(unittest.TestCase):
    def setUp(self):
        folder = TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.home = Path(folder.name)
        (self.home / ".runtime").mkdir()
        self.upload = self.home / "fixture.scad"
        self.upload.write_text("$fn=32; cylinder(d=20,h=10);\n")
        self.patch_home = patch.object(agent_team, "HOME", self.home)
        self.patch_sessions = patch.object(
            agent_team, "SESSION_PARENT", self.home / ".runtime" / "ruflo-team-sessions")
        self.patch_ruflo = patch.object(agent_team.ruflo_host, "RufloMCP", FakeRuflo)
        for p in (self.patch_home, self.patch_sessions, self.patch_ruflo):
            p.start()
            self.addCleanup(p.stop)
        self.counter = 0
        FakeRuflo.calls = []

    def call(self, request, uploaded=None):
        self.counter += 1
        destination = self.home / ("response-" + str(self.counter))
        output = agent_team.run(request, destination, uploaded=uploaded)
        self.assertTrue(output["confirmed"])
        return json.loads((destination / "ruflo-team-status.json").read_text())

    def journal(self):
        file = self.home / ".runtime/ruflo-team-sessions/direct-cad-operation/state.json"
        return json.loads(file.read_text())

    def fake_cad(self, operation, folder, source=None, title=None, layout=None):
        self.assertEqual(operation, "cad-stl")
        self.assertEqual(Path(source).suffix, ".scad")
        self.assertTrue(Path(source).is_file())
        self.assertEqual(title, "Ferrari Skill")
        self.assertEqual(layout, "landing")
        out = Path(folder)
        out.mkdir(parents=True)
        file = out / "fixture.stl"
        file.write_bytes(b"solid synthetic\nendsolid synthetic\n")
        return {"confirmed": True, "artifacts": [str(file)],
                "executor": "/srv/projects/skill-universal/tools/openscad"}

    def test_cad_operation_runs_inside_ruflo_team_and_requires_review(self):
        self.assertEqual(self.call(start_request(), self.upload)["revision"], 0)
        with patch.object(agent_team.ferrari, "run", side_effect=self.fake_cad) as engine:
            result = self.call(turn(0, "maker", "operation",
                                    operation="cad-stl", input_from="$input"))
            engine.assert_called_once()
        self.assertEqual(result["tool_calls_verified"], 1)
        self.assertEqual(result["tasks"]["cad"], "awaiting_review")
        evidence = self.journal()["tasks"]["cad"]["evidence"]
        self.assertEqual(len(evidence), 1)
        path = Path(evidence[0]["path"])
        self.assertEqual(path.suffix, ".stl")
        self.assertEqual(evidence[0]["sha256"], hashlib.sha256(path.read_bytes()).hexdigest())
        with self.assertRaisesRegex(ValueError, "stale or incorrect"):
            self.call(turn(1, "reviewer", "review", verdict="approved",
                           evidence_sha256=["0" * 64]))
        result = self.call(turn(1, "reviewer", "review", verdict="approved",
                                evidence_sha256=[evidence[0]["sha256"]]))
        self.assertEqual(result["tasks"]["cad"], "approved")
        final = self.call({
            "version": 1, "id": "direct-cad-finish", "kind": "ruflo-team",
            "team_id": "direct-cad-operation", "phase": "finish", "revision": 2,
            "approval": "I checked the actual CAD evidence and accept the finished task.",
        })
        self.assertEqual(final["status"], "completed")
        self.assertEqual(final["tool_calls_verified"], 1)
        self.assertEqual(final["reviews_recorded"], 1)
        self.assertEqual(final["autonomous_agent_model_calls"], 0)
        self.assertEqual(FakeRuflo.calls.count("swarm_shutdown"), 3)

    def test_catalog_generator_can_run_without_uploaded_source(self):
        start = start_request()
        start.pop("input")
        start["roles"][0]["actions"] = ["operation:svg-poster"]
        self.call(start)
        def fake_poster(op, folder, source=None, title=None, layout=None):
            self.assertEqual(op, "svg-poster")
            self.assertIsNone(source)
            out = Path(folder)
            out.mkdir(parents=True)
            file = out / "poster.svg"
            file.write_text("<svg xmlns='http://www.w3.org/2000/svg'></svg>")
            return {"confirmed": True, "artifacts": [str(file)],
                    "executor": "ferrari-private"}
        with patch.object(agent_team.ferrari, "run", side_effect=fake_poster):
            result = self.call(turn(0, "maker", "operation", operation="svg-poster"))
        self.assertEqual(result["tool_calls_verified"], 1)
        self.assertEqual(result["tasks"]["cad"], "awaiting_review")

    def test_unknown_and_unapproved_operations_are_rejected(self):
        start = start_request()
        start["roles"][0]["actions"] = ["operation:not-a-catalog-operation"]
        with self.assertRaisesRegex(ValueError, "catalog"):
            agent_team.validate_job(start)
        start = start_request()
        start["roles"][0]["actions"] = []
        self.call(start, self.upload)
        with self.assertRaisesRegex(ValueError, "not authorized"):
            self.call(turn(0, "maker", "operation",
                           operation="cad-stl", input_from="$input"))
        self.assertEqual(self.journal()["tasks"]["cad"]["status"], "pending")

    def test_invalid_inputs_are_rejected_before_side_effects(self):
        cases = [
            {"operation": "not-a-real-operation", "input_from": "$input"},
            {"operation": "cad-stl"},
            {"operation": "cad-stl", "input_from": "$input", "query": "rm -rf /"},
            {"operation": "cad-stl", "input_from": "$input", "layout": "shell"},
            {"operation": "cad-stl", "input_from": "$input", "layout": {}},
            {"operation": "svg-poster", "input_from": "$input"},
        ]
        for example in cases:
            with self.subTest(example=example):
                with self.assertRaises(ValueError):
                    agent_team.validate_job(turn(0, "maker", "operation", **example))
        self.call(start_request(), self.upload)
        with self.assertRaisesRegex(ValueError, "approved dependency"):
            self.call(turn(0, "maker", "operation",
                           operation="cad-stl", input_from="/etc/passwd"))
        # The base-operation name is nested in the authorized host turn;
        # no unvalidated root-level arbitrary operation is admitted.
        with self.assertRaises(ValueError):
            skill_job.validate_job({**turn(0, "maker", "operation",
                                          operation="cad-stl", input_from="$input"),
                                    "operation": "shell"})

    def test_escaping_result_causes_failure_and_recovery_gate(self):
        self.call(start_request(), self.upload)
        def escape(_op, folder, source=None, title=None, layout=None):
            Path(folder).mkdir(parents=True)
            return {"confirmed": True, "artifacts": ["/etc/passwd"]}
        with patch.object(agent_team.ferrari, "run", side_effect=escape):
            with self.assertRaisesRegex(RuntimeError, "Unsafe"):
                self.call(turn(0, "maker", "operation",
                               operation="cad-stl", input_from="$input"))
        saved = self.journal()
        self.assertEqual(saved["tasks"]["cad"]["status"], "failed")
        self.assertEqual(saved["revision"], 1)
        with self.assertRaisesRegex(ValueError, "ready agent"):
            self.call(turn(1, "maker", "operation",
                           operation="cad-stl", input_from="$input"))


if __name__ == "__main__":
    unittest.main()
