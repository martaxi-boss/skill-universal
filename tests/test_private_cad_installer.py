"""Regressions for private-only CAD tool downloads and unpacking."""
from pathlib import Path
import unittest
SCRIPT=Path(__file__).resolve().parents[1]/"install/vps-private-cad.sh"
class PrivateCadInstall(unittest.TestCase):
    def test_private_ubuntu_sources_only(self):
        src=SCRIPT.read_text()
        self.assertIn('ROOT="/srv/projects/skill-universal"',src)
        self.assertIn("download.blender.org/release/Blender4.5",src)
        self.assertIn("files.openscad.org",src)
        self.assertIn("sha256sum -c",src)
        self.assertIn("FERRARI_PRIVATE_CAD_INSTALL=PASS",src)
        self.assertNotIn("apt-get install",src)
        self.assertNotIn("sudo ",src)
        self.assertIn('mv -- "$WORK/blender" "$blender"',src)
        self.assertIn('mv -- "$WORK/openscad" "$scad"',src)
if __name__=="__main__":
    unittest.main()
