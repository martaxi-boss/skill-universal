"""Ferrari-private Apktool/Java wiring; REA is not an executable provider."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from engine import ferrari, tool_runtime, runtime_discovery

PROJECT = Path(__file__).resolve().parents[1]

class ApktoolIsolationTests(unittest.TestCase):
    def test_official_private_installer_is_pinned(self):
        installer = (PROJECT/"install/vps-apktool-isolated.sh").read_text()
        self.assertIn("v3.0.3/apktool_3.0.3.jar", installer)
        self.assertIn("dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423", installer)
        self.assertIn("sha256sum -c -", installer)
        self.assertIn("jdk-25.0.5_8/bin/java", installer)
        self.assertIn("apktool-frameworks", installer)
        self.assertIn("-Duser.home=", installer)
        self.assertNotIn("/usr/bin/java", installer)
        self.assertNotIn("rea-agents", installer)
        specialists = (PROJECT/"install/vps-specialist-engines.sh").read_text()
        self.assertIn("bash install/vps-apktool-isolated.sh", specialists)

    def test_apktool_does_not_fall_back_to_global_or_rea(self):
        with tempfile.TemporaryDirectory() as folder:
            missing = Path(folder)/"ferrari-private-does-not-exist"
            with patch.dict(tool_runtime.ISOLATED, {"apktool":missing}):
                with patch("engine.tool_runtime.shutil.which",return_value="/usr/bin/apktool"):
                    self.assertIsNone(tool_runtime.executable("apktool","apktool"))
                with patch("engine.tool_runtime.shutil.which",return_value="/usr/bin/rea"):
                    self.assertIsNone(tool_runtime.executable("rea","rea"))
            self.assertFalse(ferrari.present({"id":"rea","binary":"rea"}))
            self.assertNotIn("rea",runtime_discovery.NPM_PACKAGES)

    def test_ferrari_apktool_is_not_path_global(self):
        src=(PROJECT/"install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn('APKTOOL="$ROOT/tools/apktool-3.0.3/bin/apktool"',src)
        self.assertIn('test "$("$APKTOOL" --version)" = "3.0.3"',src)
        self.assertIn('FERRARI_APKTOOL_PRIVATE_RUNTIME=PASS',src)
        self.assertNotIn('if ! apktool b ',src)
        install=(PROJECT/"install/ferrari-ubuntu.sh").read_text()
        self.assertIn("openjdk-21-jdk-headless|apktool)",install)
        agents=(PROJECT/"install/vps-external-agents.sh").read_text()
        self.assertIn("--profile ruflo --apply",agents)
        self.assertNotIn("FERRARI_REA_CLI=PASS_HELP_ONLY",agents)

    def test_ferrari_private_runtime_path_used_when_present(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            private=root/"apktool"
            private.write_text("#!/bin/sh\nexit 0\n")
            with patch.dict(tool_runtime.ISOLATED, {"apktool":private}):
                with patch("engine.tool_runtime.shutil.which",return_value=None):
                    self.assertEqual(tool_runtime.executable("apktool","apktool"),str(private))

if __name__ == "__main__":
    unittest.main()
