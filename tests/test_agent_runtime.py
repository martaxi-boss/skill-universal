"""Independent agent runtimes never replace system Node/Java."""
from pathlib import Path
import unittest
P=Path(__file__).resolve().parents[1]
class AgentRuntime(unittest.TestCase):
    def test_isolated_agents(self):
        s=(P/"install/vps-external-agents.sh").read_text(encoding="utf-8")
        self.assertIn("node-v$NODE_VER-linux-x64.tar.xz",s)
        self.assertIn("1805bcd35e6815559bd2eb97db438d3fdb0eb3a5e6a977b7c1badca76337e9ce",s)
        self.assertIn("sha256sum -c -",s)
        self.assertIn("install/install-agent-engines.sh --profile all --apply",s)
        self.assertIn("FERRARI_REA_CLI=PASS_HELP_ONLY",s)
        self.assertIn("FERRARI_EXTERNAL_REA_DEPENDENCY=NONE",s)
        self.assertIn('REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"',s)
        self.assertNotIn("npm install -g",s)
        self.assertNotIn("sudo ",s)
if __name__=="__main__":
    unittest.main()
