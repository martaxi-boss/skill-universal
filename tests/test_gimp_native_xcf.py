"""GIMP 2.10 editable XCF export through existing Ferrari typed runtime."""
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import tool_runtime


class GimpNativeExportTests(unittest.TestCase):
    def test_manifest_and_route_keep_gimp_separate_from_other_32_actions(self):
        actions=tool_runtime.specs()
        self.assertEqual(len(actions),36)
        x=actions["gimp-png-xcf"]
        self.assertEqual((x["tool"],x["binary"],x["artifact"],x["extensions"]),
                         ("gimp","gimp-console-2.10","gimp-editable.xcf",[".png"]))
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/gimp-console-2.10"):
            result=tool_runtime.auto("gimp png xcf","/tmp/picture.png")
            self.assertEqual(result["selected"]["action"],"gimp-png-xcf")

    def test_real_command_construction_is_headless_and_paths_are_escaped(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            source=root/'image"quoted.png'
            source.write_bytes(b"\x89PNG\r\n\x1a\n"+b"test")
            out=root/"render"
            def mock_run(args,**kwargs):
                self.assertEqual(args[:4],["/usr/bin/gimp-console-2.10","-i","-n","-s"])
                self.assertFalse(kwargs.get("shell",False))
                self.assertIn("gimp-file-load",args[5])
                self.assertIn("gimp-xcf-save",args[5])
                self.assertIn(chr(92)+chr(34),args[5])
                self.assertNotIn('image"quoted.png',args[5])
                self.assertEqual(args[-1],"(gimp-quit 0)")
                for key in ("XDG_CONFIG_HOME","XDG_CACHE_HOME","XDG_DATA_HOME"):
                    self.assertTrue(kwargs["env"][key].startswith(str(out)))
                (out/"gimp-editable.xcf").write_bytes(b"gimp xcf v011\x00"+b"sample")
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/gimp-console-2.10"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=mock_run):
                    result=tool_runtime.invoke("gimp-png-xcf",str(source),str(out))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["tool"],"gimp")
            self.assertTrue((out/"gimp-editable.xcf").read_bytes().startswith(b"gimp xcf "))

    def test_missing_cli_never_builds_fake_artifact(self):
        with TemporaryDirectory() as tmp:
            src=Path(tmp)/"image.png"
            src.write_bytes(b"\x89PNG\r\n\x1a\n")
            dest=Path(tmp)/"out"
            with patch.object(tool_runtime,"executable",return_value=None):
                with self.assertRaisesRegex(RuntimeError,"Executor not installed"):
                    tool_runtime.invoke("gimp-png-xcf",str(src),str(dest))
            self.assertFalse(dest.exists())

    def test_invalid_input_extension_rejected(self):
        with TemporaryDirectory() as tmp:
            src=Path(tmp)/"image.jpg"
            src.write_bytes(b"\xff\xd8\xff")
            dest=Path(tmp)/"out"
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/gimp-console-2.10"):
                with self.assertRaisesRegex(ValueError,"Input format not supported"):
                    tool_runtime.invoke("gimp-png-xcf",str(src),str(dest))
            self.assertFalse(dest.exists())

    def test_real_vps_smoke_proves_native_xcf_signature(self):
        script=(Path(__file__).resolve().parents[1] /
                "install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn('assert x["registered_actions"]==36',script)
        self.assertIn("--action gimp-png-xcf",script)
        self.assertIn("FERRARI_GIMP_XCF_REAL=PASS",script)


if __name__=="__main__":
    unittest.main()
