"""Persistent independent REA/Ruflo runtimes across Ferrari releases."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]
class PersistentEngines(unittest.TestCase):
    def test_persistent_runtime_reuses_exact_pins(self):
        s=(R/"install/install-agent-engines.sh").read_text()
        self.assertIn(".local/share/motor-ferrari/.runtime/npm",s)
        self.assertIn("FERRARI_REA_REUSE=EXACT_PINNED_VERSION",s)
        self.assertIn("FERRARI_RUFLO_REUSE=EXACT_PINNED_VERSION",s)
    def test_agents_launcher_points_at_persistent_install(self):
        s=(R/"install/vps-external-agents.sh").read_text()
        self.assertIn('REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"',s)
        self.assertIn('RUFLO="$ROOT/.runtime/npm/ruflo/node_modules/.bin/ruflo"',s)
if __name__=="__main__":
    unittest.main()
