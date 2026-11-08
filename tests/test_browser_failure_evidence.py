"""Rejected Ferrari browser work returns concrete diagnostics, not a fake PASS."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import json
import unittest
from zipfile import ZipFile

from engine import skill_job


class FailureEvidenceTests(unittest.TestCase):
    def test_browser_error_exports_bounded_only_allowlisted_diagnostics(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            outside=root/"outside-secret.txt"
            outside.write_text("DO NOT LEAK")
            def reject(_operation,output,**_kwargs):
                dest=Path(output)
                dest.mkdir()
                (dest/"browser-check.json").write_text(json.dumps({
                    "status":"failed_navigation",
                    "navigation":{"status":"findings",
                                  "findings":["Non-functional link destination: #"]}}))
                (dest/"browser-screenshot.png").write_bytes(b"browser preview")
                (dest/"browser-mobile.png").symlink_to(outside)
                (dest/"secret.txt").write_text("should not be archived")
                raise RuntimeError(
                    "Ferrari executor failed: FERRARI_BROWSER_CHECK_FAILED="
                    "Browser quality gate failed_navigation: "
                    "Non-functional link destination: #")
            job={"version":1,"id":"browser-refusal-qa","kind":"operation",
                 "operation":"vite-build"}
            with patch.object(skill_job.ferrari,"run",side_effect=reject):
                report,code=skill_job.execute(job,root/"output")
            self.assertEqual(code,2)
            self.assertEqual(report["status"],"failed")
            self.assertIn("Non-functional link destination:",report["error"])
            self.assertEqual(sorted(report["diagnostic_artifacts"]),[
                "artifacts/browser-check.json","artifacts/browser-screenshot.png"])
            archive=root/"output/response.zip"
            with ZipFile(archive) as z:
                self.assertIsNone(z.testzip())
                self.assertEqual(sorted(z.namelist()),[
                    "artifacts/browser-check.json","artifacts/browser-screenshot.png",
                    "report.json"])
                self.assertIn(b"Non-functional link destination",
                              z.read("artifacts/browser-check.json"))
                self.assertNotIn("DO NOT LEAK",z.read("report.json").decode())


if __name__=="__main__":
    unittest.main()
