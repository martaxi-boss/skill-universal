"""Four independently installed Ubuntu-native Android CLIs, never global SDK fallbacks."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from engine import tool_runtime


class AndroidPrivateCliTests(unittest.TestCase):
    def test_four_actions_wired_to_catalogue_and_private_binaries(self):
        specifications = tool_runtime.specs()
        expected = {
            "android-apksigner-verify": ("apksigner", "stdout"),
            "android-aapt2-manifest": ("aapt2", "stdout"),
            "android-zipalign-apk": ("zipalign", "file"),
            "android-adb-install-apk": ("adb", "stdout"),
        }
        for action, (tool, mode) in expected.items():
            self.assertEqual(specifications[action]["tool"], tool)
            self.assertEqual(specifications[action]["mode"], mode)
            self.assertEqual(specifications[action]["extensions"], [".apk"])
        installer = (tool_runtime.ROOT / "install/vps-android-cli-isolated.sh").read_text()
        self.assertIn('/srv/projects/skill-universal', installer)
        self.assertIn("FERRARI_ANDROID_NO_GLOBAL_INSTALL=PASS", installer)
        self.assertNotIn("apt-get install", installer)
        self.assertNotIn("ln -s", installer)

    def test_private_cli_never_falls_back_to_system_or_shared_sdk(self):
        with tempfile.TemporaryDirectory() as directory:
            home = Path(directory) / "ferrari"
            private = home / "tools/android-cli-36.0.0"
            binary = private / "build-tools/36.0.0/aapt2"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"private-android-tool")
            external = Path(directory) / "external"
            external.write_bytes(b"system-android-tool")
            with patch.object(tool_runtime, "HOME", home):
                with patch.dict(tool_runtime.ISOLATED, {"aapt2": binary}):
                    with patch("engine.tool_runtime.shutil.which", return_value=str(external)):
                        self.assertEqual(tool_runtime.executable("aapt2"), str(binary))
                        binary.unlink()
                        self.assertIsNone(tool_runtime.executable("aapt2"))
                        binary.symlink_to(external)
                        self.assertIsNone(tool_runtime.executable("aapt2"))

    def test_verify_action_writes_output_and_private_runtime_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            home = root / "ferrari"
            apk = root / "sample.apk"
            apk.write_bytes(b"synthetic test")
            output = root / "result"
            private = home / "tools/android-cli-36.0.0/build-tools/36.0.0"
            private.mkdir(parents=True)
            exe = private / "apksigner"
            exe.write_text("#!/bin/sh\n")
            with patch.object(tool_runtime, "HOME", home):
                with patch.dict(tool_runtime.ISOLATED, {"apksigner": exe}):
                    def fake_run(args, **kwargs):
                        env = kwargs["env"]
                        self.assertTrue(env["HOME"].startswith(str(home)))
                        self.assertTrue(env["TMPDIR"].startswith(str(home)))
                        self.assertTrue(env["JAVA_HOME"].startswith(str(home)))
                        self.assertNotIn("/srv/projects/android-sdk", env.get("LD_LIBRARY_PATH", ""))
                        self.assertEqual(args[0], str(exe))
                        self.assertEqual(args[-1], str(apk.resolve()))
                        return subprocess.CompletedProcess(args, 0, b"Verified\n", b"")
                    with patch.object(tool_runtime.subprocess, "run", side_effect=fake_run):
                        result = tool_runtime.invoke("android-apksigner-verify", str(apk), str(output))
                        self.assertTrue(result["confirmed"])
                        self.assertEqual((output / "apk-signature.txt").read_bytes(), b"Verified\n")


if __name__ == "__main__":
    unittest.main()
