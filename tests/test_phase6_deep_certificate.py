"""Offline regressions for read-only phase-6 certificate inspection."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest


def load_audit():
    src = Path(__file__).resolve().parents[1] / "install/vps-phase6-certify.py"
    spec = spec_from_file_location("phase6_deep_certificate", src)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeepCertificateTests(unittest.TestCase):
    def test_symlink_scan_only_traverses_own_root(self):
        audit = load_audit()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d) / "skill-universal"
            root.mkdir()
            outside = Path(d) / "other-project"
            outside.mkdir()
            (outside / "secret.txt").write_text("should never read")
            tools = root / "tools"
            tools.mkdir()
            (tools / "file.txt").write_text("inside")
            (tools / "normal-link").symlink_to("file.txt")
            (tools / "foreign-link").symlink_to(outside, target_is_directory=True)
            (tools / "dangling-link").symlink_to("nonexistent")
            with patch.object(audit, "ROOT", root):
                with patch.object(audit, "SCAN_ROOTS", ("tools",)):
                    result = audit.scan_links()
            self.assertEqual(result["symlinks_checked"], 3)
            self.assertEqual(result["external_links_total"], 1)
            self.assertEqual(result["broken_links_total"], 1)
            self.assertTrue(result["complete_under_budget"])
            self.assertFalse(any("secret.txt" in str(x) for x in result["examples"]))

    def test_scan_cap_reports_incomplete_instead_of_full_pass(self):
        audit = load_audit()
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            tools = root / "tools"
            tools.mkdir()
            for n in range(6):
                (tools / f"f{n}").write_text("dummy")
            with patch.object(audit, "ROOT", root):
                with patch.object(audit, "SCAN_ROOTS", ("tools",)):
                    with patch.object(audit, "ENTRY_LIMIT", 3):
                        result = audit.scan_links()
            self.assertFalse(result["complete_under_budget"])

    def test_shebang_classifies_system_python_as_review_not_private(self):
        audit = load_audit()
        with tempfile.TemporaryDirectory() as d:
            sample = Path(d) / "cli"
            sample.write_text("#!/usr/bin/python3\nprint('hello')\n")
            report = audit.interpreter_check([str(sample)])
            self.assertEqual(report["counts"], {"system_interpreter_requires_review": 1})
            self.assertEqual(report["scripts"][0]["interpreter"], "/usr/bin/python3")

    def test_no_global_deletion_metadata_is_in_certificate_source(self):
        content = (Path(__file__).resolve().parents[1] / "install/vps-phase6-certify.py").read_text()
        self.assertIn('"global_packages_removed": 0', content)
        self.assertIn('"files_deleted": 0', content)
        self.assertNotIn("shutil.rmtree(", content)
        self.assertNotIn("apt-get remove", content)


if __name__ == "__main__":
    unittest.main()
