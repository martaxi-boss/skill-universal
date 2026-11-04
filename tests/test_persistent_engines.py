"""Verify Ferrari REA/Ruflo runtimes are independent of the legacy REA."""
from pathlib import Path
import unittest

R=Path(__file__).resolve().parents[1]

class PersistentEngines(unittest.TestCase):
    def test_own_rea_and_ruflo_are_pinned(self):
        s=(R/"install/install-agent-engines.sh").read_text()
        self.assertIn('RUNTIME="/srv/projects/skill-universal/.runtime/npm"',s)
        self.assertIn("FERRARI_REA_REUSE=EXACT_PINNED_VERSION",s)
        self.assertIn("FERRARI_RUFLO_REUSE=EXACT_PINNED_VERSION",s)
        self.assertIn('rea-agents@$VERSION_REA',s)
        self.assertNotIn("FERRARI_NPM_RUNTIME:-",s)

    def test_own_rea_launcher_is_not_a_legacy_dependency(self):
        s=(R/"install/vps-external-agents.sh").read_text()
        self.assertIn('REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"',s)
        self.assertIn('RUFLO="$ROOT/.runtime/npm/ruflo/node_modules/.bin/ruflo"',s)
        self.assertIn("--profile all --apply",s)
        self.assertIn("FERRARI_REA_CLI=PASS_HELP_ONLY",s)
        self.assertIn("FERRARI_EXTERNAL_REA_DEPENDENCY=NONE",s)
        self.assertIn("FERRARI_REA_PRIVATE_RUNTIME=PASS",s)
        self.assertIn("FERRARI_REA_EXTERNAL_CLI_FORBIDDEN",s)

if __name__=="__main__":
    unittest.main()
