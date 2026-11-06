"""Conservative regression suite for Ferrari-only universal catalog hygiene."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SCRIPT = (Path(__file__).resolve().parents[1] /
          "install/vps-universal-catalog-hygiene.py")
spec = importlib.util.spec_from_file_location("ferrari_universal_hygiene", SCRIPT)
hygiene = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hygiene)

NEW = "a" * 40
FALLBACK = "b" * 40
OLD = "c" * 40


class UniversalHygieneTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "skill-universal"
        for child in ("releases", "tools", "runtimes", ".runtime"):
            (self.root / child).mkdir(parents=True)
        self._release(NEW, universal=True)
        self._release(FALLBACK)
        self._release(OLD)
        (self.root / "current").symlink_to(
            self.root / "releases" / NEW, target_is_directory=True)
        (self.root / "tools" / "private-bin").write_text("remain")
        (self.root / ".runtime" / "private-state").write_text("remain")

    def _release(self, sha, universal=False):
        release = self.root / "releases" / sha
        (release / "engine").mkdir(parents=True)
        (release / "engine" / "ferrari.py").write_text("# private Ferrari")
        catalog = (
            {"functions_schema": 1, "functions": [{}] * 272,
             "tools": [{}] * 173, "mcp_capabilities": {},
             "counts": {"all_catalog_entries": 450}}
            if universal else {"counts": {"all_catalog_entries": 394}})
        (release / "engine" / "catalog.json").write_text(json.dumps(catalog))
        return release

    def test_preview_is_read_only_and_universal_catalog_is_active(self):
        report = hygiene.audit(self.root, NEW, FALLBACK)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["active_catalog_entries"], 450)
        self.assertTrue(report["universal_catalog_active"])
        self.assertEqual(report["eligible_old_releases"], [OLD])
        self.assertTrue((self.root / "releases" / OLD).exists())
        self.assertFalse(report["other_projects_or_ubuntu_modified"])

    def test_apply_prunes_only_obsolete_source_snapshot(self):
        report = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertEqual(report["removed_old_releases"], [OLD])
        self.assertFalse((self.root / "releases" / OLD).exists())
        self.assertTrue((self.root / "releases" / NEW).exists())
        self.assertTrue((self.root / "releases" / FALLBACK).exists())
        self.assertTrue((self.root / "tools" / "private-bin").exists())
        self.assertTrue((self.root / ".runtime" / "private-state").exists())
        self.assertEqual(hygiene.audit(self.root, NEW, FALLBACK, apply=True)
                         ["removed_old_releases"], [])

    def test_apply_requires_exact_active_release_and_clean_catalog(self):
        with self.assertRaisesRegex(RuntimeError, "not the clean universal"):
            hygiene.audit(self.root, OLD, FALLBACK, apply=True)
        (self.root / "releases" / NEW / "engine" / "tool_actions.json").write_text("{}")
        with self.assertRaisesRegex(RuntimeError, "not the clean universal"):
            hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertTrue((self.root / "releases" / OLD).exists())

    def test_deletion_refused_when_fallback_missing(self):
        (self.root / "releases" / FALLBACK / "engine" / "ferrari.py").unlink()
        with self.assertRaisesRegex(RuntimeError, "fallback absent"):
            hygiene.audit(self.root, NEW, FALLBACK, apply=True)

    def test_preserves_unknown_stateful_and_symlink_releases(self):
        stateful = self._release("d" * 40)
        (stateful / ".runtime").mkdir()
        outside = Path(self.tmp.name) / "not-ferrari"
        outside.mkdir()
        (self.root / "releases" / ("e" * 40)).symlink_to(outside)
        report = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertEqual(report["removed_old_releases"], [OLD])
        self.assertTrue(stateful.exists())
        self.assertTrue(outside.exists())
        self.assertTrue((self.root / "releases" / ("e" * 40)).is_symlink())

    def test_ferrari_auxiliary_pointer_protects_old_release(self):
        (self.root / "previous").symlink_to(
            self.root / "releases" / OLD, target_is_directory=True)
        report = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertEqual(report["removed_old_releases"], [])
        self.assertTrue((self.root / "releases" / OLD).exists())

    def test_audited_completely_empty_runtime_can_be_pruned(self):
        audited = "0b50e1d403deff8f3ccb421edd0b41c397d66b9b"
        release = self._release(audited)
        (release / ".runtime").mkdir()
        preview = hygiene.audit(self.root, NEW, FALLBACK)
        self.assertIn(audited, preview["eligible_old_releases"])
        self.assertTrue(release.exists())
        applied = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertIn(audited, applied["removed_old_releases"])
        self.assertFalse(release.exists())
        self.assertTrue((self.root / "releases" / NEW).exists())
        self.assertTrue((self.root / "releases" / FALLBACK).exists())

    def test_audited_runtime_refuses_added_data_or_symlink(self):
        audited = "0b50e1d403deff8f3ccb421edd0b41c397d66b9b"
        release = self._release(audited)
        folder = release / ".runtime"
        folder.mkdir()
        self.assertIn(audited, hygiene.audit(self.root, NEW, FALLBACK)
                      ["eligible_old_releases"])
        (folder / "new-real-state.json").write_text("{}")
        report = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertNotIn(audited, report["removed_old_releases"])
        self.assertTrue(release.exists())
        (folder / "new-real-state.json").unlink()
        (folder / "outside").symlink_to(self.root / "runtimes", target_is_directory=True)
        report2 = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertNotIn(audited, report2["removed_old_releases"])
        self.assertTrue(release.exists())

    def test_unknown_empty_runtime_release_is_still_preserved(self):
        release = self._release("d" * 40)
        (release / ".runtime").mkdir()
        result = hygiene.audit(self.root, NEW, FALLBACK, apply=True)
        self.assertNotIn(release.name, result["removed_old_releases"])
        self.assertTrue(release.exists())

    def test_refuses_unsafe_top_level_project_links(self):
        (self.root / "current").unlink()
        (self.root / "current").symlink_to(
            Path(self.tmp.name) / "unrelated", target_is_directory=True)
        with self.assertRaises((RuntimeError, OSError)):
            hygiene.audit(self.root, NEW, FALLBACK, apply=True)


if __name__ == "__main__":
    unittest.main()
