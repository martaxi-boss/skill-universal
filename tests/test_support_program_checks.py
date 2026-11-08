"""Opt-in support program runtime checks: safe fixed commands, never installation."""
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import json
import unittest
from unittest.mock import patch

from engine import runtime_health, skill_job


class SupportRuntimeTests(unittest.TestCase):
    def _private(self, root, name="godot"):
        (root/".runtime").mkdir(exist_ok=True)
        path=root/"tools"/(name+"-private")
        path.parent.mkdir(exist_ok=True)
        path.write_text("synthetic binary")
        path.chmod(0o755)
        return path

    def test_fixed_private_command_no_shell_and_private_temp_cleanup(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            path=self._private(root)
            with patch.object(runtime_health.subprocess,"run",
                    return_value=SimpleNamespace(returncode=0,
                        stdout="Godot Engine v4.7.2.stable.official",stderr="")) as run:
                reply=runtime_health.probe_support_program("godot",str(path),root)
            self.assertEqual(reply["status"],"startup_smoke_pass",reply)
            args,kwargs=run.call_args
            self.assertEqual(args[0],[str(path),"--headless","--version"])
            self.assertFalse(kwargs["shell"])
            self.assertLessEqual(kwargs["timeout"],12)
            self.assertTrue(kwargs["cwd"].startswith(str(root/".runtime")))
            self.assertEqual(list((root/".runtime").iterdir()),[])

    def test_missing_outside_and_unknown_programs_fail_closed(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)/"ferrari"
            root.mkdir()
            outsider=Path(folder)/"other"
            outsider.write_text("fake")
            outsider.chmod(0o755)
            with patch.object(runtime_health.subprocess,"run") as run:
                reply=runtime_health.probe_support_program("godot",str(outsider),root)
                self.assertFalse(reply["executed"])
                run.assert_not_called()
            with self.assertRaises(ValueError):
                runtime_health.probe_support_program("bash",str(outsider),root)

    def test_unsupported_or_duplicate_request_rejected_before_vps_execution(self):
        job={"version":1,"id":"support-program-check","kind":"runtime-check",
             "targets":["godot","qgis"]}
        self.assertIsNone(skill_job.validate_job(job))
        for targets in (["bash"],["godot","godot"],[], "godot",
                        ["godot","qgis","prometheus","valkey","ytdlp","unknown"]):
            with self.assertRaises(ValueError):
                skill_job.validate_job({**job,"targets":targets})
        with self.assertRaises(ValueError):
            skill_job.validate_job({**job,"operation":"office-pdf"})

    def test_actual_support_report_is_in_response_zip(self):
        with TemporaryDirectory() as folder:
            work=Path(folder)
            job={"version":1,"id":"support-program-pass","kind":"runtime-check",
                 "targets":["godot"]}
            def fake(_name,executable,_home):
                return {"tool":"godot","status":"startup_smoke_pass",
                        "startup_smoke_pass":True,"integrated_action_certified":False}
            with patch.object(skill_job.runtime_health,"probe_support_program",side_effect=fake):
                with patch.object(skill_job.tool_runtime,"executable",return_value="/tmp/ferrari-private"):
                    result,exit_code=skill_job.execute(job,work/"out")
            self.assertEqual(exit_code,0,result)
            self.assertEqual(result["status"],"completed")
            path=work/"out/artifacts/runtime-check.json"
            self.assertTrue(path.is_file())
            evidence=json.loads(path.read_text())
            self.assertEqual(evidence["pass_count"],1)
            self.assertEqual(evidence["requested_count"],1)
            self.assertEqual(evidence["scope"],
                "Private non-network startup checks only, NOT integrated functionality")
            self.assertTrue((work/"out/response.zip").is_file())

    def test_support_failure_is_not_called_completed(self):
        with TemporaryDirectory() as folder:
            work=Path(folder)
            job={"version":1,"id":"support-program-fail","kind":"runtime-check",
                 "targets":["prometheus"]}
            with patch.object(skill_job.runtime_health,"probe_support_program",
                    return_value={"tool":"prometheus",
                                  "status":"startup_smoke_failed",
                                  "startup_smoke_pass":False}):
                with patch.object(skill_job.tool_runtime,"executable",return_value="/tmp/private"):
                    result,exit_code=skill_job.execute(job,work/"out")
            self.assertEqual(exit_code,2)
            self.assertEqual(result["status"],"failed")
            self.assertIn("runtime-check.json",result["artifacts"][0])
            self.assertTrue((work/"out/response.zip").is_file())


if __name__=="__main__":
    unittest.main()
