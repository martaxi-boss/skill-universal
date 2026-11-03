"""Ferrari publishing integrations use the existing typed dispatcher."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import tool_runtime


class FerrariPublishingTests(unittest.TestCase):
    def test_manifest_has_two_real_output_actions(self):
        actions=tool_runtime.specs()
        for name, tool, ext, artifact in (
            ("calibre-html-epub","calibre",".html","calibre-book.epub"),
            ("darktable-jpeg-png","darktable",".jpg","darktable-developed.png")):
            with self.subTest(action=name):
                s=actions[name]
                self.assertEqual(s["tool"],tool)
                self.assertIn(ext,s["extensions"])
                self.assertEqual(s["artifact"],artifact)
                self.assertEqual(s["mode"],"file")
                self.assertEqual(s["args"][0],"{input}")
                self.assertEqual(s["args"][1],"{output}")

    def test_discovery_uses_specific_tool_commands(self):
        self.assertEqual(tool_runtime.BINARIES["calibre"],"ebook-convert")
        self.assertEqual(tool_runtime.BINARIES["darktable"],"darktable-cli")

    def test_auto_dispatch_matches_category_and_file_type(self):
        choices=[
            ("calibre epub","/tmp/book.html","calibre-html-epub"),
            ("darktable jpeg png","/tmp/photo.jpg","darktable-jpeg-png")
        ]
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/mock"):
            for text,path,expected in choices:
                with self.subTest(text=text):
                    result=tool_runtime.auto(text,path)
                    self.assertEqual(result["selected"]["action"],expected)
            self.assertEqual(tool_runtime.auto("calibre epub","/tmp/book.jpg")["status"],
                             "no_matching_installed_adapter")

    def test_headless_conversion_isolated_config_and_no_shell(self):
        for action,extension,header in (
            ("calibre-html-epub",".html",b"PK\x03\x04"),
            ("darktable-jpeg-png",".jpg",b"\x89PNG\r\n\x1a\n"),
        ):
            with self.subTest(action=action), tempfile.TemporaryDirectory() as tmp:
                root=Path(tmp)
                src=root/("source"+extension)
                src.write_bytes(b"<p>Ferrari</p>" if extension==".html" else b"JPEG synthetic")
                out=root/"result"
                name=tool_runtime.specs()[action]["artifact"]
                def mock_run(args,**options):
                    self.assertFalse(options.get("shell",False))
                    self.assertEqual(args[0],"/usr/bin/mock")
                    self.assertEqual(args[1:],[str(src),str(out/name)])
                    self.assertEqual(options["env"]["QT_QPA_PLATFORM"],"offscreen")
                    self.assertEqual(options["env"]["GSETTINGS_BACKEND"],"memory")
                    self.assertTrue(options["env"]["XDG_CONFIG_HOME"].startswith(str(out)))
                    self.assertTrue(options["env"]["XDG_CACHE_HOME"].startswith(str(out)))
                    (out/name).write_bytes(header+b"Ferrari-output")
                    return subprocess.CompletedProcess(args,0,b"",b"")
                with patch.object(tool_runtime,"executable",return_value="/usr/bin/mock"), \
                     patch.object(tool_runtime.subprocess,"run",side_effect=mock_run):
                    response=tool_runtime.invoke(action,str(src),str(out))
                self.assertTrue(response["confirmed"])
                self.assertEqual(response["artifacts"],[str(out/name)])
                self.assertTrue((out/name).is_file())

    def test_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            inp=root/"book.html"
            inp.write_text("<p>Ferrari</p>")
            out=root/"result"
            out.mkdir()
            (out/"calibre-book.epub").write_text("old")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/ebook-convert"):
                with self.assertRaises(FileExistsError):
                    tool_runtime.invoke("calibre-html-epub",str(inp),str(out))
            self.assertEqual((out/"calibre-book.epub").read_text(),"old")

    def test_vps_checks_real_calibre_and_darktable_result_formats(self):
        smoke=(Path(__file__).resolve().parents[1]/
               "install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn('assert x["registered_actions"]==31',smoke)
        self.assertIn('--action calibre-html-epub',smoke)
        self.assertIn('--action darktable-jpeg-png',smoke)
        self.assertIn('FERRARI_CALIBRE_HTML_EPUB_REAL=PASS',smoke)
        self.assertIn('FERRARI_DARKTABLE_JPEG_PNG_REAL=PASS',smoke)
        self.assertIn('zipfile.is_zipfile(epub)',smoke)
        self.assertIn('png.read_bytes()[:8]',smoke)
        self.assertNotIn("rea-final-runtime",smoke)


if __name__=="__main__":
    unittest.main()
