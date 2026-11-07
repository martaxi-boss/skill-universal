"""Host-driven Ruflo team: real state, reviewed evidence and no invented LLMs."""
import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import agent_team, skill_job


class FakeRuflo:
    """Exercise the actual MCP call contract without contacting a provider."""
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
            return {"success": True, "swarmId": "private-swarm"}
        if name == "agent_spawn":
            self.agents += 1
            return {"success": True, "agentId": "agent-" + str(self.agents)}
        if name == "task_create":
            self.tasks += 1
            return {"success": True, "taskId": "task-" + str(self.tasks)}
        return {"success": True}


def start():
    return {
        "version": 1, "id": "team-start-example", "kind": "ruflo-team",
        "phase": "start", "team_id": "real-role-work", "host": "ChatGPT",
        "mission": "Process and review a synthetic JSON document",
        "roles": [
            {"id": "architect", "type": "architect", "actions": []},
            {"id": "coder", "type": "coder", "actions": ["jq-format-json"]},
            {"id": "tester", "type": "tester", "actions": ["jq-format-json"]},
            {"id": "reviewer", "type": "reviewer", "actions": []}
        ],
        "tasks": [
            {"id": "design", "role": "architect", "reviewer": "reviewer",
             "goal": "Define a precise transformation acceptance checklist",
             "depends_on": []},
            {"id": "implement", "role": "coder", "reviewer": "reviewer",
             "goal": "Transform the JSON file and produce real evidence",
             "depends_on": ["design"]},
            {"id": "verify", "role": "tester", "reviewer": "reviewer",
             "goal": "Check transformed JSON independently",
             "depends_on": ["implement"]}
        ],
        "input": {"name": "sample.json",
                  "content_base64": base64.b64encode(b'{"safe":true}\n').decode("ascii")}
    }


def turn(task, role, revision, kind, message, **fields):
    return {"version": 1, "id": "team-round-" + str(revision),
            "kind": "ruflo-team", "team_id": "real-role-work", "phase": "turn",
            "revision": revision, "turn": {"task": task, "role": role,
                                         "kind": kind, "message": message, **fields}}


class AgentTeamTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home / ".runtime").mkdir()
        self.fake = patch.object(agent_team, "HOME", self.home)
        self.fake.start(); self.addCleanup(self.fake.stop)
        self.parent = patch.object(agent_team, "SESSION_PARENT",
                                   self.home / ".runtime" / "ruflo-team-sessions")
        self.parent.start(); self.addCleanup(self.parent.stop)
        self.mcp = patch.object(agent_team.ruflo_host, "RufloMCP", FakeRuflo)
        self.mcp.start(); self.addCleanup(self.mcp.stop)
        self.tool = patch.object(agent_team.tool_runtime, "invoke", side_effect=self.synthetic_tool)
        self.tool.start(); self.addCleanup(self.tool.stop)
        FakeRuflo.calls = []
        self.index = 0
        self.src = self.home / "original.json"
        self.src.write_bytes(b'{"safe":true}\n')

    def synthetic_tool(self, _name, source, dest, _query=None):
        self.assertTrue(Path(source).is_file())
        output = Path(dest)
        output.mkdir(parents=True)
        data = output / "transformed.json"
        data.write_bytes(Path(source).read_bytes())
        return {"confirmed": True, "artifacts": [str(data)],
                "executor": str(self.home / "tools/ubuntu-cli/bin/jq")}

    def execute(self, request):
        self.index += 1
        dest = self.home / ("result-" + str(self.index))
        result = agent_team.run(request, dest,
                                self.src if request["phase"] == "start" else None)
        self.assertTrue(result["confirmed"])
        return json.loads((dest / "ruflo-team-status.json").read_text())

    def seeded(self):
        s = self.execute(start())
        self.assertEqual(s["revision"], 0)
        self.assertEqual(s["host_inbox"][0]["role"], "architect")
        self.assertEqual(s["autonomous_agent_model_calls"], 0)
        return s

    def test_full_shared_host_collaboration_review_and_finish(self):
        self.seeded()
        s = self.execute(turn("design", "architect", 0, "submit",
                          "Plan the JSON transformation and acceptance checklist."))
        self.assertEqual(s["tasks"]["design"], "awaiting_review")
        self.assertEqual(s["host_inbox"][0]["role"], "reviewer")
        s = self.execute(turn("design", "reviewer", 1, "review",
                          "Design checklist verified against the requested output.",
                          verdict="approved"))
        self.assertEqual(s["tasks"]["design"], "approved")
        self.assertEqual(s["host_inbox"][0]["role"], "coder")
        s = self.execute(turn("implement", "coder", 2, "invoke",
                          "Formatting JSON using private Ferrari jq action.",
                          action="jq-format-json", input_from="$input"))
        self.assertEqual(s["tool_calls_verified"], 1)
        s = self.execute(turn("implement", "reviewer", 3, "review",
                          "Checked the SHA256, transformed bytes and trace.",
                          verdict="approved"))
        self.assertEqual(s["host_inbox"][0]["role"], "tester")
        s = self.execute(turn("verify", "tester", 4, "invoke",
                          "Check format again using the prior approved artifact.",
                          action="jq-format-json", input_from="implement"))
        self.assertEqual(s["tool_calls_verified"], 2)
        s = self.execute(turn("verify", "reviewer", 5, "review",
                          "Verified tested output and actual artifact checksum.",
                          verdict="approved"))
        self.assertEqual(s["tasks"]["verify"], "approved")
        result = self.execute({"version": 1, "id": "team-finish", "kind": "ruflo-team",
             "phase": "finish", "team_id": "real-role-work", "revision": 6,
             "approval": "I inspected the actual checked files and accept the output."})
        self.assertEqual(result["status"], "completed")
        self.assertEqual(result["tool_calls_verified"], 2)
        self.assertEqual(result["reviews_recorded"], 3)
        self.assertEqual(result["autonomous_agent_model_calls"], 0)
        self.assertEqual(FakeRuflo.calls.count("swarm_init"), 7)
        self.assertEqual(FakeRuflo.calls.count("swarm_shutdown"), 7)

    def test_stale_rounds_and_self_review_fail_closed(self):
        self.seeded()
        wrong = turn("design", "architect", 0, "review",
                     "Trying to self-approve this unsubmitted design.",
                     verdict="approved")
        with self.assertRaises(ValueError):
            self.execute(wrong)
        self.execute(turn("design", "architect", 0, "submit",
                          "Prepare the agreed work and acceptance checklist."))
        with self.assertRaisesRegex(ValueError, "Stale"):
            self.execute(turn("design", "reviewer", 0, "review",
                              "This revision has already been consumed.", verdict="approved"))
        with self.assertRaises(ValueError):
            self.execute(turn("design", "architect", 1, "review",
                              "Owner trying to approve own work.", verdict="approved"))

    def test_denied_tool_and_no_premature_final_acceptance(self):
        self.seeded()
        with self.assertRaises(ValueError):
            self.execute(turn("design", "architect", 0, "invoke",
                 "Attempt a tool that the architect is not authorized to use.",
                 action="jq-format-json", input_from="$input"))
        with self.assertRaises(ValueError):
            self.execute({"version": 1, "id": "finish", "kind": "ruflo-team",
                          "team_id": "real-role-work", "phase": "finish",
                          "revision": 0,
                          "approval": "This is an invalid premature approval."})
        invalid = start()
        invalid["roles"][0]["actions"] = ["shell"]
        with self.assertRaises(ValueError):
            agent_team.validate_job(invalid)

    def test_reject_and_correct_then_approve(self):
        self.seeded()
        self.execute(turn("design", "architect", 0, "submit",
                          "First attempt at a clear documented design."))
        s = self.execute(turn("design", "reviewer", 1, "review",
                          "Design misses explicit acceptance criteria.",
                          verdict="changes_requested"))
        self.assertEqual(s["tasks"]["design"], "pending")
        self.execute(turn("design", "architect", 2, "submit",
                          "Corrected design with explicit acceptance criteria."))
        s = self.execute(turn("design", "reviewer", 3, "review",
                          "Corrected design contains the required criteria.",
                          verdict="approved"))
        self.assertEqual(s["tasks"]["design"], "approved")

    def test_mutated_evidence_cannot_be_reviewed(self):
        self.seeded()
        self.execute(turn("design", "architect", 0, "submit",
                          "Documented design requiring real review evidence."))
        folder = self.home / ".runtime/ruflo-team-sessions/real-role-work"
        saved = json.loads((folder / "state.json").read_text())
        evidence = Path(saved["tasks"]["design"]["evidence"][0]["path"])
        evidence.write_text("tampered")
        with self.assertRaisesRegex(ValueError, "modified"):
            self.execute(turn("design", "reviewer", 1, "review",
                              "Would have approved modified evidence.", verdict="approved"))

    def test_corrupt_tool_output_requires_explicit_recovery(self):
        self.seeded()
        self.execute(turn("design", "architect", 0, "submit",
                          "A documented transformation and verification plan."))
        self.execute(turn("design", "reviewer", 1, "review",
                          "Plan reviewed and approved for tool execution.",
                          verdict="approved"))
        def malicious(_name, _input, _out, _query):
            return {"confirmed": True, "artifacts": ["/etc/passwd"]}
        with patch.object(agent_team.tool_runtime, "invoke", side_effect=malicious):
            with self.assertRaises(RuntimeError):
                self.execute(turn("implement", "coder", 2, "invoke",
                    "Do not accept evidence that escapes the Ferrari root.",
                    action="jq-format-json", input_from="$input"))
        session = self.home / ".runtime/ruflo-team-sessions/real-role-work/state.json"
        state = json.loads(session.read_text())
        self.assertEqual(state["tasks"]["implement"]["status"], "failed")
        self.assertEqual(state["revision"], 3)
        s = self.execute({"version": 1, "id": "recover",
            "kind": "ruflo-team", "phase": "recover", "revision": 3,
            "team_id": "real-role-work", "task": "implement",
            "reason": "Verified the failed operation had no external side effects.",
            "acknowledge_risk": True})
        self.assertEqual(s["tasks"]["implement"], "pending")

    def test_symlinked_work_folder_cannot_escape_private_team(self):
        self.seeded()
        session = self.home / ".runtime/ruflo-team-sessions/real-role-work"
        elsewhere = self.home / "outside-session"
        elsewhere.mkdir()
        (session / "work").symlink_to(elsewhere, target_is_directory=True)
        with self.assertRaisesRegex(RuntimeError, "Unsafe"):
            self.execute(turn("design", "architect", 0, "submit",
                         "Attempted to write through a disallowed symlink."))

    def test_host_notes_alone_can_never_certify_a_team(self):
        manifest = start()
        manifest["tasks"] = [manifest["tasks"][0]]
        self.execute(manifest)
        self.execute(turn("design", "architect", 0, "submit",
                          "A complete plan, but no real Ferrari tool was executed."))
        self.execute(turn("design", "reviewer", 1, "review",
                          "The documentation has been reviewed.", verdict="approved"))
        with self.assertRaisesRegex(ValueError, "real Ferrari tool"):
            self.execute({"version": 1, "id": "finish-no-tool",
                     "kind": "ruflo-team", "team_id": "real-role-work",
                     "phase": "finish", "revision": 2,
                     "approval": "Final approval has no actual executor evidence."})

    def test_cycles_unknown_roles_and_no_automatic_llm(self):
        invalid = start()
        invalid["tasks"][0]["depends_on"] = ["verify"]
        with self.assertRaisesRegex(ValueError, "Cyclic"):
            agent_team.validate_job(invalid)
        invalid = start()
        invalid["roles"][0]["actions"] = ["some-paid-remote-model"]
        with self.assertRaises(ValueError):
            agent_team.validate_job(invalid)
        invalid = start()
        invalid["host"] = "automatic_api_without_consent"
        with self.assertRaises(ValueError):
            agent_team.validate_job(invalid)
        with self.assertRaises(ValueError):
            agent_team.validate_job({"version": 1, "kind": "ruflo-team",
                "team_id": "job", "phase": "autopilot"})

    def test_single_ferrari_zip_envelope_uses_new_team_protocol(self):
        with TemporaryDirectory() as root:
            output = Path(root) / "ferrari-response"
            report, code = skill_job.execute(start(), output)
            self.assertEqual(code, 0, report)
            self.assertEqual(report["status"], "completed")
            self.assertTrue((output / "response.zip").is_file())
            self.assertTrue((output / "artifacts/ruflo-team-status.json").is_file())


if __name__ == "__main__":
    unittest.main()
