"""Scribus publication uses its actual Scripter CLI without global runtime state."""
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import tool_runtime


def _fake_private_xvfb(root):
    private=root/"private-cli"
    (private/"bin").mkdir(parents=True,exist_ok=True)
    for name in ("xvfb-run","Xvfb"):
        (private/"bin"/name).write_text("private test fixture")
    return private


class ScribusPublicationTests(unittest.TestCase):
    def test_typed_manifest_and_natural_route(self):
        specs = tool_runtime.specs()
        self.assertEqual(len(specs), 40)
        action = specs["scribus-text-publication"]
        self.assertEqual((action["tool"],action["binary"],action["mode"]),
                         ("scribus","scribus","directory"))
        self.assertEqual(action["extensions"],[".txt"])
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/scribus"):
            result=tool_runtime.auto("scribus texto pdf","/tmp/teste.txt")
            self.assertEqual(result["selected"]["action"],"scribus-text-publication")

    def test_scripter_uses_short_lived_xvfb_and_private_state(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            source=root/"publicacao.txt"
            source.write_text("Ferrari: publicacao de teste",encoding="utf-8")
            out=root/"result"
            private=_fake_private_xvfb(root)
            def run(args,**kwargs):
                self.assertEqual(args[:6],[str(private/"bin/xvfb-run"),"-a",
                                          "/usr/bin/scribus","-g","-ns","-py"])
                self.assertTrue(args[6].endswith("engine/scribus_job.py"))
                self.assertIs(kwargs["shell"] if "shell" in kwargs else False,False)
                env=kwargs["env"]
                self.assertEqual(env["FERRARI_SCRIBUS_INPUT"],str(source))
                self.assertEqual(env["FERRARI_SCRIBUS_OUTPUT"],str(out/"scribus-publication"))
                self.assertEqual(env["QT_QPA_PLATFORM"],"xcb")
                for key in ("HOME","XDG_CACHE_HOME","XDG_CONFIG_HOME",
                            "XDG_DATA_HOME","XDG_RUNTIME_DIR","TMPDIR"):
                    self.assertTrue(env[key].startswith(str(out)),key)
                target=out/"scribus-publication"
                (target/"publication.pdf").write_bytes(b"%PDF-1.7\n"+b"x"*256)
                (target/"publication.sla").write_bytes(
                    b'<?xml version="1.0"?>\n<SCRIBUSUTF8NEW>'+b"x"*256)
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/scribus"):
                with patch.object(tool_runtime,"PRIVATE_CLI_ROOT",private):
                    with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                        result=tool_runtime.invoke("scribus-text-publication",str(source),str(out))
            self.assertTrue(result["confirmed"])
            self.assertTrue((out/"scribus-publication/publication.sla").exists())
            self.assertEqual(result["artifacts"],[str(out/"scribus-publication")])

    def test_missing_display_refuses_to_claim_success(self):
        with TemporaryDirectory() as folder:
            src=Path(folder)/"input.txt"
            src.write_text("Ferrari",encoding="utf-8")
            dest=Path(folder)/"out"
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/scribus"):
                with patch.object(tool_runtime.shutil,"which",return_value=None):
                    with self.assertRaisesRegex(RuntimeError,"Xvfb"):
                        tool_runtime.invoke("scribus-text-publication",str(src),str(dest))
            self.assertFalse((dest/"scribus-publication/publication.pdf").exists())

    def test_unverified_pdf_is_not_success(self):
        with TemporaryDirectory() as folder:
            src=Path(folder)/"input.txt"
            src.write_text("Ferrari",encoding="utf-8")
            dest=Path(folder)/"out"
            private=_fake_private_xvfb(Path(folder))
            def run(args,**kwargs):
                folder=dest/"scribus-publication"
                (folder/"publication.pdf").write_bytes(b"fake pdf"+b"x"*256)
                (folder/"publication.sla").write_bytes(b"<SCRIBUS>"+b"x"*256)
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/scribus"):
                with patch.object(tool_runtime.shutil,"which",return_value="/usr/bin/xvfb-run"):
                    with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                        with self.assertRaisesRegex(RuntimeError,"valid PDF"):
                            tool_runtime.invoke("scribus-text-publication",str(src),str(dest))

    def test_scripter_source_and_smoke_evidence(self):
        root=Path(__file__).resolve().parents[1]
        code=(root/"engine/scribus_job.py").read_text()
        compile(code,"scribus_job.py","exec")
        self.assertIn("scribus.PDFfile()",code)
        self.assertIn("scribus.saveDocAs",code)
        self.assertIn("scribus.newDoc",code)
        smoke=(root/"install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn("--action scribus-text-publication",smoke)
        self.assertIn("FERRARI_SCRIBUS_PDF_SLA_REAL=PASS",smoke)


if __name__=="__main__":
    unittest.main()
