"""Safety tests for the read-only Ferrari old-release state audit."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SRC = Path(__file__).resolve().parents[1] / "install/vps-universal-release-deep-audit.py"
spec = importlib.util.spec_from_file_location("ferrari_deep_audit", SRC)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

ACTIVE = "a" * 40
FALLBACK = "b" * 40
OLD = "c" * 40

class FerrariOldReleaseDeepAuditTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/"skill-universal"
        releases = self.root/"releases"
        releases.mkdir(parents=True)
        for sha in (ACTIVE,FALLBACK,OLD):
            engine = releases/sha/"engine"
            engine.mkdir(parents=True)
            (engine/"ferrari.py").write_text("# Ferrari")
            (engine/"catalog.json").write_text(json.dumps(
                {"counts":{"all_catalog_entries":450},"functions":[{}]*272}
                if sha==ACTIVE else {"counts":{"all_catalog_entries":394}}))
        (self.root/"current").symlink_to(releases/ACTIVE)
        self.state = releases/OLD/".runtime"
        self.state.mkdir()
        (self.state/"state.dat").write_bytes(b"private")
        self.outside=Path(self.temp.name)/"other-project"
        self.outside.mkdir()
        (self.outside/"keep.txt").write_text("unaltered")
        (self.state/"external").symlink_to(self.outside,target_is_directory=True)

    def test_audit_reports_without_following_or_revealing_filenames(self):
        result=module.audit(self.root, ACTIVE, FALLBACK)
        self.assertEqual(result["status"],"PASS")
        self.assertEqual(result["releases_flagged"],1)
        self.assertEqual(result["files_modified"],0)
        self.assertFalse(result["deletion_authorized"])
        self.assertFalse(result["other_projects_touched"])
        state=result["releases_with_private_or_untracked_folders"][0]["state_directories"][".runtime"]
        self.assertEqual(state["bytes"],len(b"private"))
        self.assertEqual(state["files"],1)
        self.assertEqual(state["symlinks"],1)
        self.assertNotIn("state.dat",str(result))
        self.assertTrue((self.root/"releases"/OLD).exists())
        self.assertTrue((self.outside/"keep.txt").exists())

    def test_reject_wrong_release_and_missing_fallback(self):
        with self.assertRaisesRegex(RuntimeError,"not active"):
            module.audit(self.root, OLD, FALLBACK)
        (self.root/"releases"/FALLBACK/"engine/ferrari.py").unlink()
        with self.assertRaisesRegex(RuntimeError,"Fallback"):
            module.audit(self.root,ACTIVE,FALLBACK)

    def test_untracked_state_not_confused_with_other_projects(self):
        extra=self.root/"releases"/("d"*40)
        (extra/"engine").mkdir(parents=True)
        (extra/"engine/ferrari.py").write_text("present")
        (extra/"data").mkdir()
        (extra/"data"/"small.bin").write_bytes(b"123")
        rows=module.audit(self.root,ACTIVE,FALLBACK)["releases_with_private_or_untracked_folders"]
        self.assertEqual({r["release"] for r in rows},{OLD,"d"*40})
        self.assertEqual((extra/"data"/"small.bin").read_bytes(),b"123")

if __name__ == "__main__":
    unittest.main()
