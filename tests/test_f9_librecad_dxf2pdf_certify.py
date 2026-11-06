"""F9 LibreCAD DXF->PDF must be real, private and cleanup-safe."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import ast
import unittest
import json

SOURCE = Path(__file__).resolve().parents[1] / "install/vps-f9-librecad-dxf2pdf-certify.py"
SPEC = spec_from_file_location("f9_librecad_dxf2pdf", SOURCE)
m = module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class LibreCADPrivateFunctionalCertTests(unittest.TestCase):
    def test_exact_private_binaries_and_synthetic_dxf(self):
        source = SOURCE.read_text(encoding="utf-8")
        ast.parse(source)
        self.assertEqual(m.APPHOME.name, "librecad-2.2.1.6")
        self.assertEqual(m.EXECUTABLE.name, "AppRun")
        self.assertIn("tools/ubuntu-cli/bin/pdfinfo", str(m.PDFINFO))
        self.assertEqual(m.DRAWING.count("\nLINE\n"), 4)
        self.assertEqual(m.DRAWING.count("\nCIRCLE\n"), 1)
        self.assertIn("AC1009", m.DRAWING)
        self.assertEqual(len(m.APPIMAGE_SHA256), 64)

    def test_no_global_installs_or_other_project_mutations(self):
        source = SOURCE.read_text()
        for forbidden in ("apt-get ", "sudo ", "git reset", "rm -rf",
                          "pip install", "shell=True", "os.system",
                          "/srv/projects/pink-iptv", "/srv/projects/fadego"):
            self.assertNotIn(forbidden, source)
        self.assertIn('"gui_editing_certified": False', source)
        self.assertIn('"cad_3d_certified": False', source)
        self.assertIn('"test_files_removed_after_run": True', source)
        with patch.object(m.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "NO_ROOT"):
                m.guard()

    def test_environment_is_private_and_offscreen(self):
        with TemporaryDirectory() as t:
            env = m.env(Path(t))
        self.assertEqual(env["HOME"], t)
        self.assertEqual(env["TMPDIR"], t)
        self.assertEqual(env["QT_QPA_PLATFORM"], "offscreen")
        self.assertEqual(env["LIBGL_ALWAYS_SOFTWARE"], "1")
        self.assertTrue(env["PATH"].startswith(str(m.TOOLS)))
        self.assertNotIn("LD_LIBRARY_PATH", env)
        self.assertEqual(m.env(Path(t), pdfinfo=True)["LD_LIBRARY_PATH"],
                         str(m.TOOLS / "ubuntu-cli/lib"))

    def test_pdf_validation_requires_real_pdf_and_independent_pdfinfo(self):
        with TemporaryDirectory() as t:
            work=Path(t)
            pdf=work/"sample.pdf"
            pdf.write_bytes(b"%PDF-1.4\n"+b"0"*2000+b"\n%%EOF\n")
            with patch.object(m, "run", return_value=SimpleNamespace(
                returncode=0, stdout="Pages:          1\nPage size:      297 x 210 mm\n",
                stderr="")):
                data=m.validate_pdf(pdf,work)
            self.assertTrue(data["independent_poppler_pdfinfo"])
            self.assertEqual(data["pdf_pages"],1)
            with patch.object(m, "run", return_value=SimpleNamespace(
                returncode=0, stdout="Pages: 0\n", stderr="")):
                with self.assertRaisesRegex(RuntimeError, "NOT_SINGLE_PAGE"):
                    m.validate_pdf(pdf,work)

    def test_real_converter_success_and_cleanup(self):
        with TemporaryDirectory() as t:
            private=Path(t)/"skill-universal"
            runtime=private/".runtime"
            runtime.mkdir(parents=True)
            def fake_call(args, work, timeout, pdfinfo=False):
                if "dxf2pdf" in args:
                    self.assertTrue(args[0].endswith("AppRun"))
                    self.assertEqual(args[1:4],["dxf2pdf","-a","-o"])
                    Path(args[4]).write_bytes(
                        b"%PDF-1.4\n"+b"0"*2000+b"\n%%EOF\n")
                    return SimpleNamespace(returncode=0,stdout="",stderr="")
                if pdfinfo:
                    self.assertTrue(args[0].endswith("/pdfinfo"))
                    return SimpleNamespace(returncode=0,stdout="Pages: 1\n",stderr="")
                raise AssertionError(args)
            with patch.object(m,"ROOT",private),patch.object(m,"RUNTIME",runtime),\
                 patch.object(m,"guard",return_value={
                     "active_release":"test","fallback_release":"rollback",
                     "catalog_entries":450,"appimage_sha256_verified":True}),\
                 patch.object(m,"run",side_effect=fake_call):
                result=m.certify()
            self.assertEqual(result["status"],"pass")
            self.assertTrue(result["private_dxf2pdf_certified"])
            self.assertEqual(result["pdf_evidence"]["pdf_pages"],1)
            self.assertFalse(result["gui_editing_certified"])
            self.assertEqual(list(runtime.iterdir()),[])

    def test_failed_converter_never_claims_functional_pass(self):
        with TemporaryDirectory() as t:
            private=Path(t)/"skill-universal"
            runtime=private/".runtime"
            runtime.mkdir(parents=True)
            with patch.object(m,"ROOT",private),patch.object(m,"RUNTIME",runtime),\
                 patch.object(m,"guard",return_value={
                     "active_release":"test","fallback_release":"rollback",
                     "catalog_entries":450,"appimage_sha256_verified":True}),\
                 patch.object(m,"run",return_value=SimpleNamespace(
                     returncode=1,stdout="",stderr="offscreen Qt failed")):
                report=m.certify()
            self.assertEqual(report["status"],"partial_blocked")
            self.assertFalse(report["private_dxf2pdf_certified"])
            self.assertEqual(list(runtime.iterdir()),[])

if __name__ == "__main__":
    unittest.main()
