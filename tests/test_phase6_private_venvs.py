"""Phase 6 private venv migration: offline rollback and scope regression."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / "install/vps-phase6-private-venvs.py"


def load():
    spec = importlib.util.spec_from_file_location("ferrari_phase6_private_venvs", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class PrivateVenvTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.dir.cleanup)
        self.root = Path(self.dir.name) / "skill-universal"
        self.root.mkdir()
        self.global_py = Path(self.dir.name) / "ubuntu-python3.12"
        self.global_py.write_text("#!/bin/sh\nexit 0\n")
        self.global_py.chmod(0o755)
        self.private_py = self.root / "runtimes/python3.12/bin/python3.12"
        self.private_py.parent.mkdir(parents=True)
        self.private_py.write_text("#!/bin/sh\nexit 1\n")
        self.private_py.chmod(0o755)
        self.module = load()
        self.patches = [
            patch.object(self.module, "ROOT", self.root),
            patch.object(self.module, "PRIVATE", self.private_py),
            patch.object(self.module, "SYSTEM", str(self.global_py)),
            patch.object(self.module, "BACKUP", self.root / ".runtime/phase6-python-venv-migration-20261105.json"),
        ]
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)
        for version in (self.module.RELEASE, self.module.FALLBACK):
            marker = self.root / "releases" / version / "engine/ferrari.py"
            marker.parent.mkdir(parents=True)
            marker.write_text("# true release")
        (self.root / "current").symlink_to(self.root / "releases" / self.module.RELEASE)
        for rel in self.module.ENVS:
            folder = self.root / rel
            (folder / "bin").mkdir(parents=True)
            (folder / "pyvenv.cfg").write_text(
                "home = " + str(self.global_py.parent) + "\n"
                "include-system-site-packages = false\n"
                "executable = " + str(self.global_py) + "\n"
                "command = " + str(self.global_py) + " -m venv " + str(folder) + "\n")
            for name in self.module.BINARIES:
                (folder / "bin" / name).symlink_to(self.global_py)

    def test_preview_identifies_all_21_global_links_without_writing(self):
        result = self.module.do("--preview")
        self.assertEqual(result["venvs_checked"], 7)
        self.assertEqual(result["interpreter_links_checked"], 21)
        self.assertEqual(result["global_python_symlinks_before"], 21)
        self.assertEqual(result["changes_applied"], 0)
        self.assertFalse(self.module.BACKUP.exists())
        for rel in self.module.ENVS:
            self.assertEqual((self.root / rel / "bin/python3.12").resolve(), self.global_py)

    def test_adjusted_config_replaces_both_command_and_executable(self):
        before = "home = /usr/bin\nexecutable = /usr/bin/python3.12\ncommand = /usr/bin/python3.12 -m venv foo\n"
        with patch.object(self.module, "SYSTEM", "/usr/bin/python3.12"):
            after = self.module.adjusted_config(before)
        self.assertIn(str(self.private_py), after)
        self.assertNotIn("/usr/bin/python3.12", after)

    def test_system_site_packages_are_rejected(self):
        cfg = self.root / self.module.ENVS[0] / "pyvenv.cfg"
        cfg.write_text("include-system-site-packages = true\n")
        with self.assertRaisesRegex(RuntimeError, "global site packages"):
            self.module.do("--preview")

    def test_apply_rolls_back_all_links_and_configs_if_interpreter_fails(self):
        initial = {
            rel: (self.root / rel / "pyvenv.cfg").read_text()
            for rel in self.module.ENVS
        }
        with patch.object(self.module, "no_running_venv_process", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "does not start"):
                self.module.do("--apply")
        self.assertFalse(self.module.BACKUP.exists())
        for rel in self.module.ENVS:
            folder = self.root / rel
            self.assertEqual((folder / "pyvenv.cfg").read_text(), initial[rel])
            for name in self.module.BINARIES:
                self.assertEqual((folder / "bin" / name).resolve(), self.global_py)

    def test_ferrari_only_and_no_apt_removal(self):
        text = SOURCE.read_text()
        self.assertIn("global_packages_removed", text)
        self.assertNotIn("apt-get remove", text)
        self.assertNotIn("shutil.rmtree(", text)


if __name__ == "__main__":
    unittest.main()
