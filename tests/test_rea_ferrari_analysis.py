"""REA is an executor inside Ferrari, using Ferrari Node and providers only."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from engine import tool_runtime


class FerrariReaAnalysisTests(unittest.TestCase):
    def test_two_real_rea_commands_are_typed_actions(self):
        specs=tool_runtime.specs()
        elf=specs["rea-elf-notes"]
        apk=specs["rea-android-resources"]
        self.assertEqual(elf["tool"],"rea")
        self.assertEqual(elf["args"],["inspect-elf-notes","{input}","--json"])
        self.assertEqual(elf["mode"],"stdout")
        self.assertEqual(apk["tool"],"rea")
        self.assertEqual(apk["extensions"],[".apk"])
        self.assertEqual(apk["args"],["decode-android-resources","{input}","--json"])

    def test_own_rea_uses_own_node_and_apktool_env(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            home=base/"motor-ferrari"
            node=home/"runtimes/node-22.23.4/bin/node"
            node.parent.mkdir(parents=True)
            node.write_text("own Ferrari Node")
            apktool=home/"tools/apktool-3.0.3/bin/apktool"
            apktool.parent.mkdir(parents=True)
            apktool.write_text("own Ferrari Apktool")
            inp=base/"example.elf"
            inp.write_bytes(b"\\x7fELF Ferrari test")
            out=base/"out"

            def run(args,**kwargs):
                self.assertEqual(args[0],str(home/".runtime/npm/rea/node_modules/.bin/rea"))
                self.assertEqual(args[1],"inspect-elf-notes")
                self.assertEqual(args[2],str(inp))
                self.assertEqual(args[3],"--json")
                self.assertFalse(kwargs.get("shell"))
                self.assertEqual(kwargs["env"]["REA_APKTOOL_COMMAND"],str(apktool))
                self.assertEqual(kwargs["env"]["JAVA_HOME"],str(home/"runtimes/jdk-25.0.5_8"))
                self.assertTrue(kwargs["env"]["PATH"].startswith(str(node.parent)+":"))
                for key,suffix in (("XDG_CACHE_HOME","rea-cache"),
                                   ("XDG_CONFIG_HOME","rea-config"),
                                   ("XDG_DATA_HOME","rea-data")):
                    self.assertEqual(kwargs["env"][key],str(home/".runtime"/suffix))
                return subprocess.CompletedProcess(args,0,b'{"ok":true,"result":{"sha256":"test","tables":[]}}',b"")

            own=str(home/".runtime/npm/rea/node_modules/.bin/rea")
            with patch.object(tool_runtime,"HOME",home):
                with patch.dict(tool_runtime.ISOLATED,{"apktool":apktool}):
                    with patch.object(tool_runtime,"executable",return_value=own):
                        with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                            result=tool_runtime.invoke("rea-elf-notes",str(inp),str(out))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["tool"],"rea")
            self.assertEqual(json.loads((out/"rea-elf-notes.json").read_text())["ok"],True)

    def test_missing_private_node_refuses_rea(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            inp=base/"test.elf"
            inp.write_bytes(b"ELF")
            with patch.object(tool_runtime,"HOME",base/"missing-ferrari"):
                with patch.object(tool_runtime,"executable",return_value="/tmp/own-rea"):
                    with self.assertRaisesRegex(RuntimeError,"Ferrari private Node"):
                        tool_runtime.invoke("rea-elf-notes",str(inp),str(base/"out"))

    def test_android_action_rejects_non_apk_input(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            inp=base/"wrong.txt"
            inp.write_text("not an APK")
            with patch.object(tool_runtime,"executable",return_value="/tmp/own-rea"):
                with self.assertRaisesRegex(ValueError,"Input format not supported"):
                    tool_runtime.invoke("rea-android-resources",str(inp),str(base/"out"))


if __name__=="__main__":
    unittest.main()
