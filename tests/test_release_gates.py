"""Regression tests for isolated APT release and read-only precheck gating."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReleaseGateTests(unittest.TestCase):
    def test_apt_does_not_change_global_node_or_services(self):
        script=(ROOT/"install/ferrari-ubuntu.sh").read_text(encoding="utf-8")
        self.assertIn("nodejs|npm|prometheus|valkey-server",script)
        self.assertIn("FERRARI_GLOBAL_APT_INSTALL_FORBIDDEN",script)
        self.assertNotIn("apt-get install -y",script)
        self.assertNotIn("sudo -n apt-get install",script)

    def test_push_can_only_run_read_only_precheck(self):
        workflow=(ROOT/".github/workflows/deploy-vps.yml").read_text(encoding="utf-8")
        self.assertIn(".github/ferrari-readonly-precheck.request",workflow)
        self.assertIn("github.event_name == 'workflow_dispatch' && (inputs.stage == 'DEPLOY' || inputs.stage == 'INSTALL_HEADLESS')",workflow)
        self.assertIn("github.event_name == 'workflow_dispatch' && inputs.stage == 'INSTALL_HEADLESS'",workflow)
        self.assertIn("Read-only VPS Ubuntu preflight",workflow)

if __name__=="__main__":
    unittest.main()
