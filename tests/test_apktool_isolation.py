"""Ferrari-private Apktool/Java and Ferrari-private REA; zero legacy fallback."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from engine import ferrari, tool_runtime, runtime_discovery

PROJECT=Path(__file__).resolve().parents[1]

class ApktoolIsolationTests(unittest.TestCase):
    def test_official_private_apktool_installer_is_pinned(self):
        installer=(PROJECT/"install/vps-apktool-isolated.sh").read_text()
        self.assertIn("v3.0.3/apktool_3.0.3.jar",installer)
        self.assertIn("dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423",installer)
        self.assertIn("sha256sum -c -",installer)
        self.assertIn("jdk-25.0.5_8/bin/java",installer)
        self.assertIn("apktool-frameworks",installer)
        self.assertIn("-Duser.home=",installer)
        self.assertNotIn("/usr/bin/java",installer)
        specialists=(PROJECT/"install/vps-specialist-engines.sh").read_text()
        self.assertIn("bash install/vps-apktool-isolated.sh",specialists)

    def test_apktool_does_not_fall_back_to_global(self):
        with tempfile.TemporaryDirectory() as folder:
            missing=Path(folder)/"no-private-apktool"
            with patch.dict(tool_runtime.ISOLATED,{"apktool":missing}):
                with patch("engine.tool_runtime.shutil.which",return_value="/usr/bin/apktool"):
                    self.assertIsNone(tool_runtime.executable("apktool","apktool"))

    def test_rea_detected_only_inside_ferrari_npm_tree(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            home=root/".local/share/motor-ferrari"
            modules=home/".runtime/npm/rea/node_modules"
            package=modules/"rea-agents"
            (package/"bin").mkdir(parents=True)
            (package/"package.json").write_text('{"version":"6.8.0"}')
            cli_impl=package/"bin/cli.js"
            cli_impl.write_text('console.log("Ferrari-own-REA")')
            (modules/".bin").mkdir()
            cli=modules/".bin/rea"
            cli.symlink_to(Path("../rea-agents/bin/cli.js"))
            other=root/"legacy-REA-cli"
            other.write_text("other project")
            with patch.object(tool_runtime,"HOME",home):
                with patch.dict(tool_runtime.ISOLATED,{"rea":cli}):
                    with patch("engine.tool_runtime.shutil.which",return_value=str(other)):
                        self.assertEqual(tool_runtime.executable("rea","rea"),str(cli))
            with patch.object(ferrari.Path,"home",return_value=root):
                self.assertTrue(ferrari.present({"id":"rea","binary":"rea"}))
            presence=runtime_discovery.npm_presence("rea",home=home,system_roots=(root/"global",))
            self.assertEqual(presence["scope"],"ferrari_npm")
            self.assertEqual(presence["package"],"rea-agents")
            # A symlink into the other REA's folder does not count as owned.
            cli.unlink()
            cli.symlink_to(other)
            with patch.object(tool_runtime,"HOME",home):
                with patch.dict(tool_runtime.ISOLATED,{"rea":cli}):
                    self.assertIsNone(tool_runtime.executable("rea","rea"))
            with patch.object(ferrari.Path,"home",return_value=root):
                self.assertFalse(ferrari.present({"id":"rea","binary":"rea"}))

    def test_apktool_and_rea_are_private_installs(self):
        src=(PROJECT/"install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn('APKTOOL="$ROOT/tools/apktool-3.0.3/bin/apktool"',src)
        self.assertIn('test "$("$APKTOOL" --version)" = "3.0.3"',src)
        self.assertIn('FERRARI_APKTOOL_PRIVATE_RUNTIME=PASS',src)
        self.assertNotIn('if ! apktool b ',src)
        apt=(PROJECT/"install/ferrari-ubuntu.sh").read_text()
        self.assertIn("openjdk-21-jdk-headless|apktool)",apt)
        agents=(PROJECT/"install/vps-external-agents.sh").read_text()
        self.assertIn("--profile all --apply",agents)
        self.assertIn('REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"',agents)
        self.assertIn("FERRARI_EXTERNAL_REA_DEPENDENCY=NONE",agents)
        self.assertIn("rea",runtime_discovery.NPM_PACKAGES)

    def test_ferrari_private_apktool_path_used_when_present(self):
        with tempfile.TemporaryDirectory() as folder:
            private=Path(folder)/"apktool"
            private.write_text("#!/bin/sh\nexit 0\n")
            with patch.dict(tool_runtime.ISOLATED,{"apktool":private}):
                with patch("engine.tool_runtime.shutil.which",return_value=None):
                    self.assertEqual(tool_runtime.executable("apktool","apktool"),str(private))

if __name__=="__main__":
    unittest.main()
