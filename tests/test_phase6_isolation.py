"""Ferrari phase 6: validate executable ownership and honest discovery."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch

from engine import cad_tools, core, runtime_discovery, tool_runtime


class PhaseSixPrivateDiscoveryTests(unittest.TestCase):
    def test_cad_office_are_exposed_as_private_base_operations(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            private = {
                "blender": home / "tools/blender/blender",
                "openscad": home / "tools/openscad/bin/openscad",
                "libreoffice": home / "tools/libreoffice/program/soffice",
            }
            for path in private.values():
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("#!/bin/sh\nexit 0\n")
                path.chmod(0o755)
            discovery = {
                "python": {"tools": {}, "detected": 0},
                "npm": {"tools": {}, "detected": 0},
                "containers": {"tools": {}, "runtimes": {}},
            }
            with patch.object(cad_tools, "FERRARI_HOME", home):
                with patch.object(runtime_discovery, "discover", return_value=discovery):
                    with patch("engine.professional_tools.vite_available", return_value=False):
                        with patch("engine.professional_tools.bim_available", return_value=False):
                            report = tool_runtime.inventory()
            for name, operation in (
                ("blender", "blender-house"), ("openscad", "cad-stl"),
                ("libreoffice", "office-pdf"),
            ):
                item = next(x for x in report["programs"] if x["id"] == name)
                self.assertEqual(item["path"], str(private[name]))
                self.assertEqual(item["detection"], "executable")
                self.assertEqual(item["status"], "callable")
                self.assertIn(operation, item["base_operations"])
            self.assertEqual(report["registered_actions"], 40)

    def test_legacy_core_never_uses_global_path_for_installed(self):
        for entry in (
            {"id": "ffmpeg", "bin": "ffmpeg"},
            {"id": "git", "bin": "git"},
            {"id": "libreoffice", "bin": "libreoffice"},
        ):
            with self.subTest(entry=entry["id"]):
                with patch.object(tool_runtime, "executable", return_value=None):
                    with patch("engine.core.shutil.which", return_value="/usr/bin/ffmpeg") as global_binary:
                        self.assertFalse(core.installed(entry))
                global_binary.assert_not_called()

    def test_inspection_cannot_execute_global_file_or_readelf(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d)
            data = home / "sample.elf"
            data.write_bytes(b"\x7fELF" + b"TEST" * 20)
            with patch.object(tool_runtime, "executable", return_value=None):
                with patch("engine.core.shutil.which", return_value="/usr/bin/readelf") as global_binary:
                    with patch("engine.core.subprocess.run") as attempted:
                        result = core.inspect_artifact(data, home / "report")
            details = json.loads(result[0].read_text())
            self.assertEqual(details["file"], "private_executor_unavailable")
            self.assertIsNone(details["readelf_header"])
            global_binary.assert_not_called()
            attempted.assert_not_called()

    def test_venv_parent_symlink_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            home, external = root / "ferrari", root / "other"
            home.mkdir()
            (external / "venvs/external/lib/python3.12/site-packages/cv2").mkdir(parents=True)
            (external / "venvs/external/lib/python3.12/site-packages/cv2/__init__.py").write_text("# outside")
            (home / ".runtime").symlink_to(external, target_is_directory=True)
            with patch("engine.runtime_discovery.importlib.util.find_spec", return_value=None):
                self.assertIsNone(runtime_discovery.python_presence("cv2", home=home))

    def test_npm_parent_symlink_cannot_escape_project(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            home, external = root / "ferrari", root / "other"
            home.mkdir()
            node = external / "npm/web/node_modules/vite/package.json"
            node.parent.mkdir(parents=True)
            node.write_text('{"name":"vite"}')
            (home / ".runtime").symlink_to(external, target_is_directory=True)
            self.assertIsNone(runtime_discovery.npm_presence("vite", home=home))

    def test_private_cli_parent_symlink_never_exposes_other_project(self):
        with tempfile.TemporaryDirectory() as d:
            home = Path(d) / "ferrari"
            external = Path(d) / "other"
            home.mkdir()
            fake = external / "ubuntu-cli/bin/jq"
            fake.parent.mkdir(parents=True)
            fake.write_text("#!/bin/sh\nexit 0\n")
            fake.chmod(0o755)
            (home / "tools").symlink_to(external, target_is_directory=True)
            with patch.object(tool_runtime, "HOME", home):
                with patch.object(tool_runtime, "PRIVATE_CLI_ROOT", home / "tools/ubuntu-cli"):
                    self.assertIsNone(tool_runtime.executable("jq", "jq"))


if __name__ == "__main__":
    unittest.main()
