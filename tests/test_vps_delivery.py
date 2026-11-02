"""VPS deployment script contract: never silently mix central VPS projects."""
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

class VpsDeploymentContract(unittest.TestCase):
    def test_dedicated_local_install(self):
        s=(ROOT/"install/vps-delivery.sh").read_text()
        for fragment in ("$HOME/.local/share/motor-ferrari",
                         "install/ferrari-ubuntu.sh --profile maximum --headless --apply",
                         "python3 -m engine.orchestrator", "FERRARI_VPS_INSTALL=",
                         "sudo -n", "FERRARI_APT_BLOCKED_DISK"):
            self.assertIn(fragment,s)
        for forbidden in ("curl | bash", "rm -rf /", "npm install -g", "apt-get upgrade", "reboot"):
            self.assertNotIn(forbidden,s)

if __name__=="__main__":
    unittest.main()
