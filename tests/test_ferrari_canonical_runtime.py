"""Canonical private runtime: engine modules must not require the obsolete home alias."""
from pathlib import Path
import unittest
from engine import rea_mcp, tool_runtime, runtime_discovery, professional_tools

PHYSICAL = Path("/srv/projects/skill-universal")

class FerrariCanonicalRuntimeTests(unittest.TestCase):
    def test_ferrari_owned_roots_are_physical(self):
        self.assertEqual(rea_mcp.ROOT, PHYSICAL)
        self.assertEqual(rea_mcp.PROJECT_ROOT, PHYSICAL)
        self.assertEqual(tool_runtime.HOME, PHYSICAL)
        self.assertEqual(runtime_discovery.FERRARI_HOME, PHYSICAL)
        self.assertEqual(professional_tools.HOME, PHYSICAL)
        self.assertEqual(professional_tools.BIM_PYTHON, PHYSICAL / ".runtime/venvs/bim/bin/python")

if __name__ == "__main__":
    unittest.main()
