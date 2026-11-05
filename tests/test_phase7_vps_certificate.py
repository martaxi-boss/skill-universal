"""F7 acceptance: no global installs, no false Ruflo claims, one owned directory."""
import ast
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "install/vps-phase7-certify.py"


class Phase7CertificateRules(unittest.TestCase):
    def test_source_is_syntactically_valid(self):
        ast.parse(SOURCE.read_text(encoding="utf-8"))

    def test_root_and_active_release_are_checked(self):
        s = SOURCE.read_text(encoding="utf-8")
        self.assertIn('ROOT = Path("/srv/projects/skill-universal")', s)
        self.assertIn('(ROOT/"current").resolve(strict=True)', s)
        self.assertIn('F6_FALLBACK', s)
        self.assertIn('FERRARI_PHASE7_DAG_PRIVATE_CERT=PASS', s)

    def test_no_install_uninstall_or_service_commands(self):
        s = SOURCE.read_text(encoding="utf-8")
        for forbidden in ("apt-get install", "apt-get remove", "sudo ",
                          "systemctl stop", "systemctl start",
                          "shutil.rmtree(", "os.system(",
                          "subprocess.Popen("):
            self.assertNotIn(forbidden, s)

    def test_ruflo_is_optional_without_paid_provider_claim(self):
        s = SOURCE.read_text(encoding="utf-8")
        self.assertIn('"agent_workflow_certified":False', s)
        self.assertIn('"model_or_provider_called":False', s)
        self.assertIn('".runtime/npm/ruflo/node_modules/ruflo/package.json"', s)
        self.assertIn('"--version"', s)

    def test_uninstall_rehearsal_is_read_only_only_scoped_metadata(self):
        s = SOURCE.read_text(encoding="utf-8")
        self.assertIn('"uninstall_executed":False', s)
        self.assertIn('"global_package_removal_authorized":False', s)
        self.assertIn('"other_project_files_touched":False', s)
        self.assertIn('"unscanned_or_unreadable_possible":incomplete', s)


if __name__ == "__main__":
    unittest.main()
