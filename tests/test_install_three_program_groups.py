"""Regression checks for the 33-program expansion on Ferrari Ubuntu 24.04."""
from pathlib import Path
import re
import unittest
from engine import ferrari

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"install/vps-expand-services-gui.sh"

class ExpansionTests(unittest.TestCase):
    def test_there_are_15_missing_gui_and_two_headless_candidates(self):
        selected=ferrari.ubuntu_selection()
        gui={x["id"] for x in selected if x["curated_tier"]=="desktop_candidate"}
        self.assertEqual(len(gui),17)
        self.assertEqual(gui-{"blender","openscad"},
                         {"gimp","krita","kdenlive","scribus","darktable","librecad",
                          "qgis","audacity","obs","lmms","solvespace","synfig",
                          "openshot","calibre","inkscape"})
        services={x["id"] for x in selected if x["id"] in ("prometheus","valkey")}
        self.assertEqual(services,{"prometheus","valkey"})

    def test_gui_install_uses_official_ubuntu_packages_and_no_legacy_rea(self):
        script=SCRIPT.read_text()
        for pkg in ("gimp","krita","kdenlive","scribus","darktable","librecad",
                    "qgis","audacity","obs-studio","lmms","solvespace",
                    "synfigstudio","openshot-qt","calibre","inkscape"):
            self.assertRegex(script,r"\b"+re.escape(pkg)+r"\b")
        self.assertIn("PRIVATE_INSTALL_REQUIRED",script)
        self.assertNotIn("apt-get install -y",script)
        self.assertNotIn("sudo -n apt-get install",script)
        self.assertIn('ROOT="/srv/projects/skill-universal"',script)
        self.assertNotIn("~/.rea",script)
        self.assertNotIn("/opt/rea",script)

    def test_no_automatic_service_activation(self):
        script=SCRIPT.read_text()
        for forbidden in ("systemctl start","systemctl enable","service prometheus start",
                          "service valkey-server start","docker run",
                          "apt-get install -y prometheus valkey-server"):
            self.assertNotIn(forbidden,script)
        self.assertIn('SERVICES=(prometheus valkey-server)',script)
        self.assertIn('dpkg-deb -x "$deb" "$work/unpacked"',script)
        self.assertIn('out="$ROOT/tools/ferrari-services/$pkg"',script)

    def test_expansion_called_by_ferrari_release_only(self):
        script=(ROOT/"install/vps-delivery.sh").read_text()
        self.assertIn("BLOCKED_LEGACY_GLOBAL_APT",script)
        self.assertNotIn("bash install/vps-expand-services-gui.sh",script)
        self.assertIn("FERRARI_ONLY_HYGIENE", (ROOT/"install/ferrari-hygiene.py").read_text())

if __name__=="__main__":
    unittest.main()
