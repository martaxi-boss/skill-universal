"""Static safety contract for read-only REA MCP catalog comparison."""
from pathlib import Path
import unittest

P = Path(__file__).resolve().parents[1] / "install/vps-rea-mcp-parity-audit.py"

class ReaMcpParityAudit(unittest.TestCase):
    def test_audit_reads_only_catalog_not_tools(self):
        src = P.read_text()
        self.assertIn('"tools/list"', src)
        self.assertIn('"initialize"', src)
        self.assertIn('"notifications/initialized"', src)
        self.assertNotIn('"tools/call"', src)
        self.assertNotIn("shutil.rmtree", src)
        self.assertNotIn('subprocess.run(["rm"', src)
        self.assertIn("rea-final-runtime/bin/rea-mcp", src)
        self.assertIn(".runtime/npm/rea/node_modules/.bin/rea", src)
        self.assertIn("rea-providers/ghidra-12.1.4", src)
        self.assertIn("jadx-headless-mcp-0.7.1-all.jar", src)
        self.assertIn("PARITY_NOT_PROVEN", src)

if __name__ == "__main__":
    unittest.main()
