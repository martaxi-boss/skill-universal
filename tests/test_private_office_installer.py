"""Private LibreOffice relocation runs offline and never writes to global app locations."""
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
class PrivateOfficeContract(unittest.TestCase):
    def test_office_no_network_or_global_writes(self):
        s=(ROOT/"install/vps-private-office.sh").read_text()
        for needle in ('ROOT="/srv/projects/skill-universal"',
                       'DEST="$ROOT/tools/libreoffice"',
                       'SOURCE="/usr/lib/libreoffice"',
                       "ignore_dangling_symlinks=True",
                       "BRAND_BASE_DIR=", "FHS_CONFIG_FILE=",
                       "FERRARI_PRIVATE_OFFICE_LOCAL_COPY=PASS",
                       "FERRARI_PRIVATE_OFFICE_INSTALL=PASS",
                       "FERRARI_PRIVATE_OFFICE_PDF_TEST=PASS",
                       "trap cleanup EXIT", "SAL_USE_VCLPLUGIN=svp"):
            self.assertIn(needle,s)
        for forbidden in ("curl ", "wget ", "apt-get install", "sudo ", "snap install",
                          "systemctl start", "pip install"):
            self.assertNotIn(forbidden,s)
    def test_private_office_is_required_by_cad_adapter(self):
        s=(ROOT/"engine/cad_tools.py").read_text()
        self.assertIn("tools/libreoffice/program/soffice",s)
        self.assertIn("FERRARI_PRIVATE_EXECUTOR_MISSING",s)
if __name__=="__main__":
    unittest.main()
