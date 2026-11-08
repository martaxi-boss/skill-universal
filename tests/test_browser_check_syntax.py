"""Ensure the ONE Ferrari Playwright worker remains valid JavaScript.

Production uses the Ferrari-owned Node executable. GitHub CI may use the
runner's Node strictly for syntax testing; never execute browser scripts
from system tools in VPS production.
"""
from pathlib import Path
import os
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "engine/browser_check.js"
PRIVATE_NODE = Path("/srv/projects/skill-universal/runtimes/node-22.23.4/bin/node")


class BrowserWorkerSyntaxTests(unittest.TestCase):
    def test_ferrari_playwright_worker_compiles(self):
        if PRIVATE_NODE.is_file() and PRIVATE_NODE.stat().st_mode & 0o111:
            node = str(PRIVATE_NODE)
        elif os.environ.get("GITHUB_ACTIONS") == "true":
            node = shutil.which("node")
        else:
            node = None
        if not node:
            self.skipTest("Node not available for syntax-only check in this runtime")
        result = subprocess.run([node, "--check", str(SCRIPT)],
                                cwd=ROOT, capture_output=True, text=True,
                                shell=False, timeout=12, check=False)
        self.assertEqual(result.returncode, 0, result.stderr[:1200])


if __name__ == "__main__":
    unittest.main()
