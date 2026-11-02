"""New typed CAD and document operations, without arbitrary scripts."""
import unittest
from pathlib import Path
from engine import ferrari
from engine import cad_tools

ROOT=Path(__file__).resolve().parents[1]

class CadOfficeTests(unittest.TestCase):
    def test_supported_domain_operations(self):
        for op in ("cad-stl","blender-house","office-pdf"):
            self.assertIn(op,ferrari.OPS)
    def test_no_input_forgery_or_arbitrary_shell(self):
        self.assertNotIn("shell=True",(ROOT/"engine/cad_tools.py").read_text())
        self.assertNotIn("eval(",(ROOT/"engine/cad_tools.py").read_text())
        self.assertIn("--python-exit-code",(ROOT/"engine/cad_tools.py").read_text())
        self.assertIn("QT_QPA_PLATFORM",(ROOT/"engine/cad_tools.py").read_text())
    def test_cad_rejects_non_scad(self):
        with self.assertRaises(ValueError):
            cad_tools.scad_to_stl(Path("other.py"),Path("/tmp/ferrari-check-not-created"))
    def test_office_rejects_unsupported_extension(self):
        with self.assertRaises(ValueError):
            cad_tools.office_pdf(Path("script.sh"),Path("/tmp/ferrari-check-not-created"))
    def test_script_and_install_exist(self):
        self.assertTrue((ROOT/"engine/blender_house.py").is_file())
        self.assertTrue((ROOT/"install/vps-cad-3d.sh").is_file())

if __name__=="__main__":
    unittest.main()
