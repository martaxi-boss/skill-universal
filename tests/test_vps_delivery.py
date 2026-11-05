"""Ferrari deploy must not create or reuse global application installs."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class VpsDeploymentContract(unittest.TestCase):
    def test_legacy_delivery_is_disabled(self):
        s=(ROOT/"install/vps-delivery.sh").read_text()
        self.assertIn("BLOCKED_LEGACY_GLOBAL_APT",s)
        self.assertNotIn("apt-get install",s)
        workflow=(ROOT/".github/workflows/deploy-vps.yml").read_text()
        self.assertIn("/srv/projects/skill-universal",workflow)
        self.assertNotIn(".local/share/motor-ferrari",workflow)
    def test_project_only_cad_install(self):
        s=(ROOT/"install/vps-cad-3d.sh").read_text()
        self.assertNotIn("apt-get install",s)
        self.assertNotIn("sudo",s)
        self.assertIn("FERRARI_PRIVATE_CAD_EXECUTOR",s)

if __name__=="__main__":
    unittest.main()
