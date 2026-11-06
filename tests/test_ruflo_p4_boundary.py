"""Ferrari Ruflo P4: fail closed on accidental second coordination layer."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class RufloP4SafetyTests(unittest.TestCase):
    def test_ruflo_not_automatically_exposed_as_typed_action(self):
        catalog=json.loads((ROOT/"engine/tool_actions.json").read_text(encoding="utf-8"))
        self.assertIsInstance(catalog["actions"],list)
        self.assertTrue(catalog["actions"])
        unsafe=[a for a in catalog["actions"] if
                str(a.get("tool","")).lower()=="ruflo"
                or str(a.get("binary","")).lower()=="ruflo"
                or str(a.get("id","")).lower().startswith("ruflo-")]
        self.assertFalse(unsafe,"Ruflo auto-spawns a background daemon on some writes")

    def test_ferrari_coordinator_never_delegates_to_external_agent_by_default(self):
        code=(ROOT/"engine/orchestrator.py").read_text(encoding="utf-8")
        self.assertIn('"external_agents_invoked": False',code)
        self.assertIn('"paid_providers_invoked": False',code)
        self.assertNotIn("ruflo start",code)
        self.assertNotIn("swarm init",code)
        self.assertNotIn("ruflo agent spawn",code)

    def test_ruflo_pinned_private_cli_without_automatic_swarm_start(self):
        installer=(ROOT/"install/install-agent-engines.sh").read_text(encoding="utf-8")
        self.assertIn("VERSION_RUFLO=3.71.0",installer)
        self.assertIn('"$RUNTIME/ruflo/node_modules/.bin/ruflo" --help',installer)
        self.assertIn('.runtime/npm',installer)
        self.assertNotIn('"$RUFLO" start',installer)
        self.assertNotIn('"$RUFLO" daemon',installer)
        self.assertNotIn('"$RUFLO" swarm',installer)

    def test_ruflo_real_limit_and_daemon_side_effect_documented(self):
        report=(ROOT/"docs/RUFLO_PONTO4_20261106.md").read_text(encoding="utf-8")
        self.assertIn("42187084139",report)
        self.assertIn("42187338181",report)
        self.assertIn("12,5%",report)
        self.assertIn("daemon",report)
        self.assertIn("MULTIAGENTES_NAO_CERTIFICADOS",report)
        self.assertIn("engine/orchestrator.py",report)


if __name__ == "__main__":
    unittest.main()
