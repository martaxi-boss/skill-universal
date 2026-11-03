"""REA original provider compatibility without touching the legacy REA project."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from engine import tool_runtime


class PrivateReaProviderTests(unittest.TestCase):
    def test_official_versioned_providers_and_no_legacy_fallback(self):
        root = Path(__file__).resolve().parents[1]
        script = (root / "install/vps-rea-providers.sh").read_text()
        specialist = (root / "install/vps-specialist-engines.sh").read_text()
        self.assertIn("ghidra-12.1.4", script)
        self.assertIn("jadx-headless-mcp-0.7.1-all.jar", script)
        self.assertIn("ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db", script)
        self.assertIn("6e5eacf500b64292bfb73c49797c1958f6ee44646e43e868039ae7feb573ff75", script)
        self.assertIn("sha256sum -c -", script)
        self.assertIn('"$JDK/bin/jar" tf "$JAR"', script)
        self.assertNotIn('unzip -tq "$JAR"', script)
        self.assertIn("GHIDRA_INSTALL_DIR", script)
        self.assertIn("REA_JADX_MCP_JAR", script)
        self.assertNotIn("/home/ubuntu/rea-final-runtime", script)
        self.assertNotIn("rea-chatgpt-trial", script)
        self.assertNotIn("sudo ", script)
        self.assertIn("bash install/vps-rea-providers.sh", specialist)

    def test_own_provider_environment_is_bound_only_to_private_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "motor-ferrari"
            apktool = home / "tools/apktool-3.0.3/bin/apktool"
            ghidra = home / "tools/rea-providers/ghidra-12.1.4"
            bridge = home / "tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar"
            node = home / "runtimes/node-22.23.4/bin/node"
            for p in (apktool, ghidra / "support/analyzeHeadless", bridge, node):
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("test")
            inp = Path(tmp) / "input.elf"
            inp.write_bytes(b"\x7fELF")
            outdir = Path(tmp) / "results"
            def fake_run(args, **kwargs):
                env = kwargs["env"]
                self.assertEqual(env["GHIDRA_INSTALL_DIR"], str(ghidra))
                self.assertEqual(env["REA_JADX_MCP_JAR"], str(bridge))
                self.assertEqual(env["GHIDRA_JAVA_HOME"],
                                 str(home / "runtimes/jdk-25.0.5_8"))
                self.assertEqual(env["REA_APKTOOL_COMMAND"], str(apktool))
                self.assertTrue(env["PATH"].startswith(str(node.parent)))
                self.assertNotIn("rea-final-runtime", env["PATH"])
                return subprocess.CompletedProcess(args, 0, b'{"ok":true}', b"")
            with patch.object(tool_runtime, "HOME", home), \
                 patch.dict(tool_runtime.ISOLATED, {"apktool": apktool}), \
                 patch.object(tool_runtime, "executable", return_value=str(home / ".runtime/npm/rea/node_modules/.bin/rea")), \
                 patch.dict(os.environ, {"GHIDRA_INSTALL_DIR": "/home/ubuntu/rea-final-runtime/providers/ghidra",
                                         "REA_JADX_MCP_JAR": "/home/ubuntu/rea-final-runtime/vendors/jadx"}), \
                 patch.object(tool_runtime.subprocess, "run", side_effect=fake_run):
                outcome = tool_runtime.invoke("rea-elf-notes", str(inp), str(outdir))
            self.assertTrue(outcome["confirmed"])
            self.assertTrue((outdir / "rea-elf-notes.json").is_file())

    def test_no_old_provider_environment_if_private_dependencies_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "motor-ferrari"
            node = home / "runtimes/node-22.23.4/bin/node"
            apktool = home / "tools/apktool-3.0.3/bin/apktool"
            for p in (node, apktool):
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text("test")
            inp = Path(tmp) / "input.elf"
            inp.write_bytes(b"\x7fELF")
            def fake_run(args, **kwargs):
                env = kwargs["env"]
                self.assertNotIn("GHIDRA_INSTALL_DIR", env)
                self.assertNotIn("REA_JADX_MCP_JAR", env)
                return subprocess.CompletedProcess(args, 0, b'{"ok":true}', b"")
            with patch.object(tool_runtime, "HOME", home), \
                 patch.dict(tool_runtime.ISOLATED, {"apktool": apktool}), \
                 patch.object(tool_runtime, "executable", return_value=str(home / ".runtime/npm/rea/node_modules/.bin/rea")), \
                 patch.dict(os.environ, {"GHIDRA_INSTALL_DIR": "/legacy/unwanted",
                                         "REA_JADX_MCP_JAR": "/legacy/unwanted"}), \
                 patch.object(tool_runtime.subprocess, "run", side_effect=fake_run):
                outcome = tool_runtime.invoke("rea-elf-notes", str(inp), str(Path(tmp)/"results"))
            self.assertTrue(outcome["confirmed"])


if __name__ == "__main__":
    unittest.main()
