"""Ferrari phase 2: independent publishing command-line adapters."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest
from unittest.mock import patch

from engine import tool_runtime


class PublishingAdapterTests(unittest.TestCase):
    def test_manifest_has_distinct_typed_inputs_and_results(self):
        specs=tool_runtime.specs()
        self.assertEqual(len(specs),33)
        for key,tool,ext,out in (
            ("calibre-md-epub","calibre",".md","calibre-book.epub"),
            ("darktable-jpeg-tiff","darktable",".jpg","darktable-export.tif"),
            ("krita-image-png","krita",".jpg","krita-export.png"),
        ):
            with self.subTest(key=key):
                action=specs[key]
                self.assertEqual(action["tool"],tool)
                self.assertIn(ext,action["extensions"])
                self.assertEqual(action["artifact"],out)
                self.assertEqual(action["mode"],"file")
                if tool=="krita":
                    self.assertEqual(action["args"][:2],["-platform","offscreen"])
                self.assertIn("{input}",action["args"])
                self.assertIn("{output}",action["args"])

    def test_natural_route_selects_correct_publishing_tool(self):
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/fake"):
            cases=(
                ("converter markdown para epub","/tmp/book.md","calibre-md-epub"),
                ("darktable jpeg para tiff","/tmp/photo.jpg","darktable-jpeg-tiff"),
                ("krita para png","/tmp/photo.jpg","krita-image-png"),
            )
            for phrase,source,expected in cases:
                with self.subTest(phrase=phrase):
                    self.assertEqual(tool_runtime.auto(phrase,source)["selected"]["action"],expected)
            self.assertEqual(tool_runtime.route("krita para png","/tmp/source.md")["suggestions"],[])

    def test_each_application_keeps_config_inside_job(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            source=root/"photo.jpg"
            source.write_bytes(b"\xff\xd8\xff"+b"\x00"*32)
            for action,tool,magic in (
                    ("darktable-jpeg-tiff","darktable",b"II*\x00"),
                    ("krita-image-png","krita",b"\x89PNG\r\n\x1a\n")):
                with self.subTest(action=action):
                    out=root/tool
                    def run(args,**kwargs):
                        self.assertFalse(kwargs.get("shell",False))
                        self.assertTrue(kwargs["env"]["XDG_CONFIG_HOME"].startswith(str(out)))
                        self.assertTrue(kwargs["env"]["XDG_CACHE_HOME"].startswith(str(out)))
                        self.assertTrue(kwargs["env"]["XDG_DATA_HOME"].startswith(str(out)))
                        if tool=="krita":
                            self.assertEqual(kwargs["env"]["QT_QPA_PLATFORM"],"offscreen")
                        (out/tool_runtime.specs()[action]["artifact"]).write_bytes(magic+b"\x00"*60)
                        return subprocess.CompletedProcess(args,0,b"",b"")
                    with patch.object(tool_runtime,"executable",return_value="/usr/bin/mock"):
                        with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                            result=tool_runtime.invoke(action,str(source),str(out))
                    self.assertTrue(result["confirmed"])
                    self.assertEqual(result["tool"],tool)

    def test_calibre_config_isolated_and_document_output_confirmed(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            source=root/"book.md"
            source.write_text("# Test\n\nFerrari test.\n")
            out=root/"result"
            def run(args,**kwargs):
                self.assertIn(str(source),args)
                self.assertIn(str(out/"calibre-book.epub"),args)
                self.assertEqual(kwargs["env"]["CALIBRE_CONFIG_DIRECTORY"],
                                 kwargs["env"]["XDG_CONFIG_HOME"])
                self.assertEqual(kwargs["env"]["QT_QPA_PLATFORM"],"offscreen")
                (out/"calibre-book.epub").write_bytes(b"PK\x03\x04"+b"\x00"*80)
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/ebook-convert"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                    result=tool_runtime.invoke("calibre-md-epub",str(source),str(out))
            self.assertTrue(result["confirmed"])

    def test_phase2_smoke_only_uses_ferrari_synthetic_fixtures(self):
        script=(Path(__file__).resolve().parents[1]/
                "install/vps-tool-runtime-smoke.sh").read_text()
        for action in ("calibre-md-epub","darktable-jpeg-tiff","krita-image-png"):
            self.assertIn("--action "+action,script)
        for marker in ("FERRARI_CALIBRE_MD_EPUB_REAL=PASS",
                       "FERRARI_DARKTABLE_JPEG_TIFF_REAL=PASS",
                       "FERRARI_KRITA_JPEG_PNG_REAL=PASS"):
            self.assertIn(marker,script)
        self.assertNotIn("rea-final-runtime",script)


if __name__=="__main__":
    unittest.main()
