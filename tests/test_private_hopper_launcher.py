"""Ferrari-private Hopper launcher isolation tests (no download or privileged operations)."""
from pathlib import Path
import tempfile
import unittest

from engine.rea_mcp import _private_hopper_launcher


class PrivateHopperLauncherTests(unittest.TestCase):
    def test_missing_private_launcher_not_selected(self):
        with tempfile.TemporaryDirectory() as t:
            self.assertIsNone(_private_hopper_launcher(Path(t)))

    def test_only_executable_inside_project_selected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            hopper = root / "tools/hopper-6.6.1/opt/hopper/bin/Hopper"
            hopper.parent.mkdir(parents=True)
            hopper.write_bytes(b"ELF fixture")
            hopper.chmod(0o600)
            self.assertIsNone(_private_hopper_launcher(root))
            hopper.chmod(0o700)
            self.assertEqual(_private_hopper_launcher(root), str(hopper))

    def test_symlink_outside_project_not_selected(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            other = root / "out-of-project"
            other.write_bytes(b"fixture")
            other.chmod(0o700)
            hopper = root / "tools/hopper-6.6.1/opt/hopper/bin/Hopper"
            hopper.parent.mkdir(parents=True)
            hopper.symlink_to(other)
            self.assertIsNone(_private_hopper_launcher(root))


if __name__ == "__main__":
    unittest.main()
