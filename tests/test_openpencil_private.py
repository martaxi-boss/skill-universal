"""Static safety checks for the optional Ferrari-private OpenPencil CLI installer.

Functional import/export must still pass on the real VPS before certification.
"""
import subprocess
import unittest
from pathlib import Path
from engine import runtime_discovery

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "install/vps-openpencil-cli.sh"


class TestOpenPencilPrivate(unittest.TestCase):
    def test_syntax(self):
        result = subprocess.run(["bash", "-n", str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_private_paths_and_exact_version(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for expected in (
            'ROOT="/srv/projects/skill-universal"',
            'node-22.23.4/bin/node',
            'node-22.23.4/lib/node_modules/npm/bin/npm-cli.js',
            'DEST="$PARENT/openpencil"',
            'VERSION="0.16.0"',
            'PACKAGE="@open-pencil/cli"',
            '--ignore-scripts',
            'smoke_file_exports',
            'FERRARI_OPENPENCIL_REAL_SVG=PASS',
            'FERRARI_OPENPENCIL_REAL_HTML=PASS',
        ):
            self.assertIn(expected, source)
        for prohibited in ("apt-get install", "sudo npm", "npm install -g", "/usr/local/bin"):
            self.assertNotIn(prohibited, source)

    def test_read_only_inventory_is_ferrari_scoped(self):
        self.assertEqual(runtime_discovery.NPM_PACKAGES["openpencil"], ("@open-pencil/cli",))
        self.assertEqual(runtime_discovery.SYSTEM_NPM_ROOTS, ())


if __name__ == "__main__":
    unittest.main()
