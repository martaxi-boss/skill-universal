"""Regressions for the independent Ferrari engine."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import ferrari

class FerrariTests(unittest.TestCase):
    def test_registry(self):
        x=ferrari.registry()
        self.assertEqual(len(x),50)
        self.assertEqual(len(set(i["id"] for i in x)),50)
    def test_plan(self):
        x=ferrari.plan("Quero descompilar um APK")
        self.assertEqual(x["route"],"reverse")
        self.assertFalse(x["executed"])
        self.assertIn("jadx",[i["id"] for i in x["selected"]])
    def test_packages(self):
        x=ferrari.packages()
        self.assertIn("apktool",x)
        self.assertIn("tesseract-ocr",x)
        self.assertIn("ffmpeg",x)
        self.assertIn("krita",x)
        self.assertNotIn("krita",ferrari.packages(include_gui=False))
    def test_website(self):
        with tempfile.TemporaryDirectory() as d:
            x=ferrari.run("web-template",d,title="Ferrari")
            self.assertTrue(x["confirmed"])
            self.assertIn("Ferrari",Path(x["artifacts"][0]).read_text())
            with self.assertRaises(FileExistsError):
                ferrari.run("web-template",d)
    def test_layout_variants(self):
        for layout in ("store","portfolio","dashboard"):
            with tempfile.TemporaryDirectory() as d:
                result=ferrari.run("web-template",d,title="Marca Ferrari",layout=layout)
                self.assertTrue(result["confirmed"])
                self.assertIn("Marca Ferrari",Path(result["artifacts"][0]).read_text())
    def test_creative(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(ferrari.run("svg-poster",d)["confirmed"])
    def test_no_shell(self):
        with self.assertRaises(ValueError):
            ferrari.run("shell","/tmp/no-op")
    def test_invalid_apk(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not-apk.txt";p.write_text("x")
            with self.assertRaises(ValueError):
                ferrari.run("apk-decompile",d+"/out",source=p)
    def test_missing_executable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.pdf";p.write_bytes(b"%PDF")
            with patch("shutil.which",return_value=None):
                with self.assertRaises(RuntimeError):
                    ferrari.run("pdf-text",d+"/out",source=p)
    def test_doctor_no_false_cert(self):
        self.assertEqual(ferrari.doctor()["status"],"inventory_only_not_functional_certification")
if __name__=="__main__":unittest.main()
