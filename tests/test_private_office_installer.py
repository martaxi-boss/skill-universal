"""LibreOffice AppImage must be installed and tested inside Ferrari only."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
class PrivateOfficeContract(unittest.TestCase):
    def test_office_no_global_writes_and_real_file_verification(self):
        s=(ROOT/"install/vps-private-office.sh").read_text()
        self.assertIn('ROOT="/srv/projects/skill-universal"',s)
        self.assertIn('DEST="$ROOT/tools/libreoffice"',s)
        self.assertIn("appimages.libreitalia.org/LibreOffice-previous.standard-x86_64.AppImage",s)
        self.assertIn("FERRARI_PRIVATE_OFFICE_INSTALL=PASS",s)
        self.assertIn("FERRARI_PRIVATE_OFFICE_PDF_TEST=PASS",s)
        self.assertIn("sha256sum",s)
        self.assertIn('trap cleanup EXIT',s)
        self.assertIn("signature not verified",s.lower())
        for forbidden in ("apt-get install", "sudo ", "snap install",
                          "systemctl start", "/opt/libreoffice", "pip install"):
            self.assertNotIn(forbidden,s)
    def test_private_office_is_required_by_cad_adapter(self):
        s=(ROOT/"engine/cad_tools.py").read_text()
        self.assertIn('tools/libreoffice/program/soffice',s)
        self.assertIn("FERRARI_PRIVATE_EXECUTOR_MISSING",s)

if __name__=="__main__":
    unittest.main()
