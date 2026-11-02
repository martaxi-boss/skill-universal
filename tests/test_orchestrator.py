"""Orchestrator integration tests run on the Ubuntu 24.04 GitHub Actions runner."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from engine import orchestrator


def task(name, operation="web-template", **kwargs):
    return {"id": name, "operation": operation, **kwargs}


class OrchestratorTests(unittest.TestCase):
    def test_preview_is_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "never-created"
            data = {"version": 1, "steps": [task("web", title="Preview")]}
            answer = orchestrator.orchestrate(data, str(target))
            self.assertEqual(answer["mode"], "preview")
            self.assertFalse(target.exists())
            self.assertFalse(answer["external_agents_invoked"])

    def test_reject_arbitrary_shell(self):
        with self.assertRaises(ValueError):
            orchestrator.validate_workflow(
                {"version": 1, "steps": [task("unsafe", operation="shell")]})

    def test_missing_dependency(self):
        with self.assertRaises(ValueError):
            orchestrator.validate_workflow(
                {"version": 1, "steps": [task("s1", depends_on=["unknown"])]})

    def test_reject_cycles(self):
        spec = {"version": 1, "steps": [
            task("one", depends_on=["two"]),
            task("two", depends_on=["one"])]}
        with self.assertRaises(ValueError):
            orchestrator.validate_workflow(spec)

    def test_reject_extra_fields(self):
        with self.assertRaises(ValueError):
            orchestrator.validate_workflow(
                {"version": 1, "steps": [task("one", shell="rm -rf /")]})

    def test_reject_limit(self):
        spec = {"version": 1, "steps": [task("a" + str(i)) for i in range(25)]}
        with self.assertRaises(ValueError):
            orchestrator.validate_workflow(spec)
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                orchestrator.orchestrate({"version": 1, "steps": [task("a")]},
                                         d, max_parallel=5)

    def test_parallel_real_html_and_svg(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = {"version": 1, "steps": [
                task("website", title="Motor Ferrari", layout="store"),
                task("poster", operation="svg-poster", title="Campanha Ferrari")]}
            response = orchestrator.orchestrate(data, tmp, execute=True, max_parallel=2)
            result = response["result"]
            self.assertEqual(result["status"], "completed")
            self.assertEqual(len(result["completed"]), 2)
            self.assertTrue(Path(response["report_file"]).is_file())
            a = Path(result["completed"]["website"]["artifacts"][0])
            b = Path(result["completed"]["poster"]["artifacts"][0])
            self.assertIn("Motor Ferrari", a.read_text(encoding="utf-8"))
            self.assertIn("Campanha Ferrari", b.read_text(encoding="utf-8"))
            persisted = json.loads(Path(response["report_file"]).read_text(encoding="utf-8"))
            self.assertEqual(persisted["status"], "completed")

    def test_dependent_real_string_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = {"version": 1, "steps": [
                task("website", title="Ferrari Dependencia"),
                task("extract", operation="binary-strings",
                     depends_on=["website"], input_from="website")]}
            result = orchestrator.orchestrate(data, tmp, execute=True)["result"]
            self.assertEqual(result["status"], "completed")
            self.assertIn("Ferrari Dependencia",
                          Path(result["completed"]["extract"]["artifacts"][0])
                          .read_text(encoding="utf-8"))

    def test_failed_executor_is_recorded_and_blocks_later_steps(self):
        with tempfile.TemporaryDirectory() as tmp:
            data = {"version": 1, "steps": [
                task("first"),
                task("later", depends_on=["first"])]}
            with patch.object(orchestrator.ferrari, "run",
                              side_effect=RuntimeError("simulated failure")):
                output = orchestrator.orchestrate(data, tmp, execute=True)
            self.assertEqual(output["result"]["status"], "failed")
            self.assertIn("first", output["result"]["failed"])
            self.assertEqual(output["result"]["blocked"], ["later"])
            self.assertTrue(Path(output["report_file"]).is_file())

    def test_non_ubuntu_execution_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(orchestrator.ferrari, "system",
                              return_value={"distro": "debian"}):
                with self.assertRaises(RuntimeError):
                    orchestrator.orchestrate(
                        {"version": 1, "steps": [task("one")]},
                        tmp, execute=True)


if __name__ == "__main__":
    unittest.main()
