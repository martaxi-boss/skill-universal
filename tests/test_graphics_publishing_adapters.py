"""Ferrari phase 2: real Ubuntu GUI/CLI image and publishing adapters."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from engine import tool_runtime


class FerrariGraphicsPublishingTests(unittest.TestCase):
    def test_three_adapters_are_typed_for_explicit_formats(self):
        specs=tool_runtime.specs()
        expected={
            "krita-png-jpeg":("krita","krita",".png","krita-export.jpg"),
            "darktable-photo-jpeg":("darktable","darktable-cli",".jpg","darktable-export.jpg"),
            "calibre-text-epub":("calibre","ebook-convert",".txt","calibre-book.epub"),
        }
        self.assertEqual(len(specs),33)
        for action,(tool,binary,ext,output) in expected.items():
            with self.subTest(action=action):
                x=specs[action]
                self.assertEqual((x["tool"],x["binary"],x["artifact"]),
                                 (tool,binary,output))
                self.assertEqual(x["mode"],"file")
                self.assertIn(ext,x["extensions"])
                self.assertIn("{input}",x["args"])
                self.assertIn("{output}",x["args"])

    def test_auto_selects_each_real_program_without_ambiguous_guess(self):
        cases=(
            ("krita png para jpeg","/tmp/ferrari.png","krita-png-jpeg"),
            ("darktable fotografia","/tmp/ferrari.jpg","darktable-photo-jpeg"),
            ("calibre epub","/tmp/ferrari.txt","calibre-text-epub"),
        )
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/fake"):
            for request,path,expected in cases:
                with self.subTest(request=request):
                    proposal=tool_runtime.auto(request,path)
                    self.assertEqual(proposal["selected"]["action"],expected)
            self.assertEqual(tool_runtime.route("calibre epub","/tmp/ferrari.jpg")["suggestions"],[])

    def test_execute_real_binary_no_shell_and_private_app_state(self):
        binaries={"krita-png-jpeg":"/usr/bin/krita",
                  "darktable-photo-jpeg":"/usr/bin/darktable-cli",
                  "calibre-text-epub":"/usr/bin/ebook-convert"}
        inputs={"krita-png-jpeg":("image.png",b"\x89PNG\r\n\x1a\n"),
                "darktable-photo-jpeg":("image.jpg",b"\xff\xd8\xff\xe0"),
                "calibre-text-epub":("book.txt",b"Ferrari text publication")}
        outputs={"krita-png-jpeg":b"\xff\xd8\xff\xe0",
                 "darktable-photo-jpeg":b"\xff\xd8\xff\xe0",
                 "calibre-text-epub":b"PK\x03\x04"}
        for action,exe in binaries.items():
            with self.subTest(action=action), tempfile.TemporaryDirectory() as d:
                root=Path(d)
                name,data=inputs[action]
                src=root/name
                src.write_bytes(data)
                dest=root/"work"
                def fake(args,**opts):
                    self.assertEqual(args[0],exe)
                    self.assertFalse(opts.get("shell",False))
                    self.assertIn(str(src),args)
                    env=opts["env"]
                    for key in ("XDG_CACHE_HOME","XDG_CONFIG_HOME","XDG_DATA_HOME"):
                        self.assertTrue(env[key].startswith(str(dest)))
                    if action=="krita-png-jpeg":
                        self.assertEqual(env["QT_QPA_PLATFORM"],"offscreen")
                        self.assertIn("--export",args)
                    elif action=="darktable-photo-jpeg":
                        self.assertIn("--width",args)
                    else:
                        self.assertEqual(args[1:],[str(src),str(dest/"calibre-book.epub")])
                    artifact=dest/tool_runtime.specs()[action]["artifact"]
                    artifact.write_bytes(outputs[action]+b"ferrari output")
                    return subprocess.CompletedProcess(args,0,b"",b"")
                with patch.object(tool_runtime,"executable",return_value=exe):
                    with patch.object(tool_runtime.subprocess,"run",side_effect=fake):
                        result=tool_runtime.invoke(action,str(src),str(dest))
                self.assertTrue(result["confirmed"])
                self.assertEqual(result["executor"],exe)
                self.assertTrue(Path(result["artifacts"][0]).is_file())

    def test_wrong_format_refused_before_invocation(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"malformed.txt"
            p.write_text("text")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/krita"):
                with self.assertRaisesRegex(ValueError,"Input format not supported"):
                    tool_runtime.invoke("krita-png-jpeg",str(p),str(Path(d)/"out"))
            self.assertFalse((Path(d)/"out").exists())

    def test_missing_executable_does_not_generate_fake_artifact(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"document.txt"
            p.write_text("Ferrari")
            with patch.object(tool_runtime,"executable",return_value=None):
                with self.assertRaisesRegex(RuntimeError,"Executor not installed"):
                    tool_runtime.invoke("calibre-text-epub",str(p),str(Path(d)/"out"))
            self.assertFalse((Path(d)/"out").exists())

    def test_gimp_script_fu_is_noninteractive_with_escaped_file_paths(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            src=root/'picture"quoted.png'
            src.write_bytes(b"\\x89PNG\\r\\n\\x1a\\n" + b"1"*24)
            dest=root/"gimp-output"
            def fake(args,**opts):
                self.assertEqual(args[0],"/usr/bin/gimp-console-2.10")
                self.assertEqual(args[1:4],["-i","-n","-s"])
                self.assertFalse(opts.get("shell",False))
                expression=args[5]
                self.assertIn("gimp-file-load",expression)
                self.assertIn("gimp-xcf-save",expression)
                self.assertIn('picture\\\\"quoted.png',expression)
                self.assertEqual(args[-1],"(gimp-quit 0)")
                (dest/"gimp-editable.xcf").write_bytes(b"gimp xcf v011\\0"+"Ferrari".encode())
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/gimp-console-2.10"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=fake):
                    result=tool_runtime.invoke("gimp-png-xcf",str(src),str(dest))
            self.assertTrue(result["confirmed"])
            self.assertTrue((dest/"gimp-editable.xcf").read_bytes().startswith(b"gimp xcf "))

    def test_vps_smoke_must_prove_three_real_file_signatures(self):
        root=Path(__file__).resolve().parents[1]
        smoke=(root/"install/vps-tool-runtime-smoke.sh").read_text()
        for action in ("krita-png-jpeg","darktable-photo-jpeg","calibre-text-epub","gimp-png-xcf"):
            self.assertIn("--action "+action,smoke)
        for marker in ("FERRARI_KRITA_JPEG_REAL=PASS",
                       "FERRARI_DARKTABLE_JPEG_REAL=PASS",
                       "FERRARI_CALIBRE_EPUB_REAL=PASS","FERRARI_GIMP_XCF_REAL=PASS"):
            self.assertIn(marker,smoke)


if __name__=="__main__":
    unittest.main()
