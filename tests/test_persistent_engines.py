"""Ferrari's optional runtime persists without depending on REA."""
from pathlib import Path
import unittest
R=Path(__file__).resolve().parents[1]

class PersistentEngines(unittest.TestCase):
    def test_persistent_ruflo_isolated_and_rea_removed(self):
        s=(R/"install/install-agent-engines.sh").read_text()
        self.assertIn(".local/share/motor-ferrari/.runtime/npm",s)
        self.assertIn("FERRARI_RUFLO_REUSE=EXACT_PINNED_VERSION",s)
        self.assertNotIn("FERRARI_REA_REUSE=EXACT_PINNED_VERSION",s)
        self.assertNotIn("rea-agents@",s)
        self.assertIn("case \"$PROFILE\" in ruflo)",s)

    def test_ferrari_agents_launcher_never_uses_rea(self):
        s=(R/"install/vps-external-agents.sh").read_text()
        self.assertIn('RUFLO="$ROOT/.runtime/npm/ruflo/node_modules/.bin/ruflo"',s)
        self.assertIn("--profile ruflo --apply",s)
        self.assertNotIn('REA="$ROOT/',s)
        self.assertIn("FERRARI_REA_DEPENDENCY=NONE",s)

if __name__ == "__main__":
    unittest.main()
