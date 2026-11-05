"""F7 Ferrari only: persistent DAG, replay safety, isolation and cooperative quotas."""
import json
import os
from pathlib import Path
import tempfile
import threading
import unittest
from unittest.mock import patch

from engine import orchestrator


def step(name, **extra):
    return {"id": name, "operation": "svg-poster", "title": name, **extra}


def svg_runner(operation, folder, source=None, title="", layout="landing"):
    dest = Path(folder)
    dest.mkdir(parents=True)
    out = dest / "poster.svg"
    out.write_text("<svg>" + title + "</svg>", encoding="utf-8")
    return {"confirmed": True, "artifacts": [str(out)],
            "executor": "ferrari-private"}


class FerrariPhase7Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = str(Path(self.temp.name) / "jobs")
        self.plan = {"version": 1, "steps": [step("poster")]}

    def test_preview_has_no_side_effects_or_external_agents(self):
        target = Path(self.workspace)
        out = orchestrator.orchestrate(self.plan, self.workspace, job_key="demo")
        self.assertEqual(out["mode"], "preview")
        self.assertFalse(target.exists())
        self.assertFalse(out["external_agents_invoked"])
        self.assertFalse(out["paid_providers_invoked"])
        self.assertEqual(len(out["plan_sha256"]), 64)

    def test_same_key_does_not_run_twice_and_resume_reuses_exact_artifacts(self):
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner) as fake:
            first = orchestrator.orchestrate(
                self.plan, self.workspace, execute=True, job_key="stable")
            self.assertEqual(first["result"]["status"], "completed")
            self.assertEqual(fake.call_count, 1)
            with self.assertRaises(FileExistsError):
                orchestrator.orchestrate(self.plan, self.workspace,
                                          execute=True, job_key="stable")
            replay = orchestrator.orchestrate(self.plan, self.workspace,
                                               execute=True, job_key="stable",
                                               resume=True)
            self.assertEqual(fake.call_count, 1)
            self.assertEqual(replay["reused_steps"], ["poster"])
            self.assertEqual(replay["result"]["status"], "completed")
            job = Path(self.workspace) / "ferrari-stable"
            self.assertTrue((job / "journal.json").is_file())
            self.assertEqual(json.loads((job / "journal.json").read_text())["attempt"], 1)

    def test_recovery_of_interrupted_second_stage_does_not_repeat_first(self):
        plan = {"version": 1, "steps": [
            step("first"), step("second", depends_on=["first"])]}
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner):
            original = orchestrator.orchestrate(plan, self.workspace, execute=True,
                                                job_key="recover")
        job = Path(self.workspace) / "ferrari-recover"
        journal = job / "journal.json"
        state = json.loads(journal.read_text(encoding="utf-8"))
        state["status"] = "running"
        del state["completed"]["second"]
        journal.write_text(json.dumps(state), encoding="utf-8")
        (job / "second" / "poster.svg").write_text("PARTIAL", encoding="utf-8")
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner) as fake:
            recovered = orchestrator.orchestrate(plan, self.workspace, execute=True,
                                                 job_key="recover", resume=True)
        self.assertEqual(recovered["result"]["status"], "completed")
        self.assertEqual(recovered["reused_steps"], ["first"])
        self.assertEqual(fake.call_count, 1)
        self.assertIn("second", recovered["result"]["completed"])
        self.assertEqual(recovered["result"]["attempt"], 2)
        self.assertNotEqual((job / "second" / "poster.svg").read_text(), "PARTIAL")
        self.assertEqual(original["result"]["job_id"], recovered["result"]["job_id"])

    def test_resume_rejects_changed_plan(self):
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner):
            orchestrator.orchestrate(self.plan, self.workspace,
                                     execute=True, job_key="fixed")
        changed = {"version": 1, "steps": [step("poster", title="different")]}
        with self.assertRaisesRegex(ValueError, "plan or resource policy"):
            orchestrator.orchestrate(changed, self.workspace,
                                     execute=True, job_key="fixed", resume=True)

    def test_resume_refuses_deleted_checkpoint_artifact(self):
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner):
            orchestrator.orchestrate(self.plan, self.workspace,
                                     execute=True, job_key="private")
        (Path(self.workspace) / "ferrari-private/poster/poster.svg").unlink()
        with self.assertRaisesRegex(RuntimeError, "missing"):
            orchestrator.orchestrate(self.plan, self.workspace,
                                     execute=True, job_key="private", resume=True)

    def test_failure_blocks_dependent_step_then_explicit_retry(self):
        plan = {"version": 1, "steps": [step("first"),
                                        step("second", depends_on=["first"])]}
        with patch.object(orchestrator.ferrari, "run",
                          side_effect=RuntimeError("deliberate failure")):
            failed = orchestrator.orchestrate(plan, self.workspace,
                                              execute=True, job_key="retry")
        self.assertEqual(failed["result"]["status"], "failed")
        self.assertEqual(failed["result"]["blocked"], ["second"])
        with self.assertRaisesRegex(RuntimeError, "retry_failed"):
            orchestrator.orchestrate(plan, self.workspace,
                                     execute=True, job_key="retry", resume=True)
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner) as fake:
            replay = orchestrator.orchestrate(plan, self.workspace,
                                               execute=True, job_key="retry",
                                               resume=True, retry_failed=True)
        self.assertEqual(replay["result"]["status"], "completed")
        self.assertEqual(fake.call_count, 2)
        self.assertEqual(replay["result"]["attempt"], 2)

    def test_cancellation_marker_stops_dependents_without_daemon(self):
        plan = {"version": 1, "steps": [step("first"),
                                        step("second", depends_on=["first"])]}

        def request_cancel(*args, **kwargs):
            result = svg_runner(*args, **kwargs)
            (Path(args[1]).parent / "cancel.request").write_text("stop")
            return result

        with patch.object(orchestrator.ferrari, "run", side_effect=request_cancel):
            cancelled = orchestrator.orchestrate(plan, self.workspace,
                                                  execute=True, job_key="stop")
        self.assertEqual(cancelled["result"]["status"], "cancelled")
        self.assertEqual(cancelled["result"]["blocked"], ["second"])
        self.assertEqual(set(cancelled["result"]["completed"]), {"first"})

    def test_artifact_quota_failure_is_recorded(self):
        def oversized(*args, **kwargs):
            directory = Path(args[1])
            directory.mkdir(parents=True)
            artifact = directory / "large.txt"
            artifact.write_bytes(b"x" * 2048)
            return {"confirmed": True, "artifacts": [str(artifact)]}

        with patch.object(orchestrator.ferrari, "run", side_effect=oversized):
            answer = orchestrator.orchestrate(
                self.plan, self.workspace, execute=True,
                max_artifacts_bytes=1024)
        self.assertEqual(answer["result"]["status"], "failed")
        self.assertIn("quota", answer["result"]["failed"]["poster"]["error"])

    def test_external_output_is_rejected(self):
        external = Path(self.temp.name) / "foreign.txt"
        external.write_text("not Ferrari")

        def escaping(*args, **kwargs):
            Path(args[1]).mkdir(parents=True)
            return {"confirmed": True, "artifacts": [str(external)]}

        with patch.object(orchestrator.ferrari, "run", side_effect=escaping):
            answer = orchestrator.orchestrate(self.plan, self.workspace, execute=True)
        self.assertEqual(answer["result"]["status"], "failed")
        self.assertIn("escapes", answer["result"]["failed"]["poster"]["error"])
        self.assertEqual(external.read_text(), "not Ferrari")

    def test_invalid_resume_without_fixed_key(self):
        with self.assertRaisesRegex(ValueError, "fixed job key"):
            orchestrator.orchestrate(self.plan, self.workspace,
                                     execute=True, resume=True)

    def test_symlinked_workspace_is_rejected(self):
        actual = Path(self.temp.name) / "target"
        actual.mkdir()
        shortcut = Path(self.temp.name) / "alias"
        shortcut.symlink_to(actual)
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner):
            with self.assertRaisesRegex(ValueError, "symlink"):
                orchestrator.orchestrate(self.plan, str(shortcut), execute=True)

    def test_parallel_waves_still_run_without_second_coordinator(self):
        plan = {"version": 1, "steps": [step("a"), step("b")]}
        current = 0
        peak = 0
        gate = threading.Barrier(2)
        mutex = threading.Lock()

        def concurrent(*args, **kwargs):
            nonlocal peak, current
            with mutex:
                current += 1
                peak = max(peak, current)
            gate.wait(timeout=10)
            result = svg_runner(*args, **kwargs)
            with mutex:
                current -= 1
            return result

        with patch.object(orchestrator.ferrari, "run", side_effect=concurrent):
            result = orchestrator.orchestrate(plan, self.workspace,
                                              execute=True, max_parallel=2)
        self.assertEqual(result["result"]["status"], "completed")
        self.assertEqual(peak, 2)

    def test_cooperative_timeout_blocks_future_wave(self):
        plan = {"version": 1, "steps": [step("one"),
                                        step("two", depends_on=["one"])]}
        with patch.object(orchestrator.ferrari, "run", side_effect=svg_runner):
            with patch.object(orchestrator.time, "monotonic",
                              side_effect=[0, 0, 2]):
                response = orchestrator.orchestrate(
                    plan, self.workspace, execute=True,
                    max_runtime_seconds=1)
        self.assertEqual(response["result"]["status"], "timed_out")
        self.assertEqual(response["result"]["blocked"], ["two"])
        self.assertEqual(response["result"]["timeout_enforcement"],
                         "cooperative_between_waves")


if __name__ == "__main__":
    unittest.main()
