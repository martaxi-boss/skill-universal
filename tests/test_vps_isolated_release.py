"""Controlled Ferrari release deployment must be reversible and project-only."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class PrivateReleaseGateTests(unittest.TestCase):
    def test_private_release_only(self):
        text=(ROOT/"install/vps-isolated-release.sh").read_text()
        for value in (
            'ROOT="/srv/projects/skill-universal"',
            '[[ "$MODE" == "--check" || "$MODE" == "--activate" ]]',
            'FERRARI_PRIVATE_ACTIONS=40/40_PASS',
            'FERRARI_OFFICE_RELEASE_SMOKE=PASS',
            'FERRARI_CAD_3D_RELEASE_SMOKE=PASS',
            'FERRARI_PRIVATE_SKILL_JOB_RESPONSE_ZIP=PASS',
            'FERRARI_RELEASE_ROLLBACK=PASS',
            'FERRARI_PREVIOUS_RELEASE_PRESERVED=',
            'FERRARI_PRIVATE_RELEASE_ACTIVE=',
            'mv -Tf "$NEXT" "$ROOT/current"',
            'trap cleanup EXIT',
        ):
            self.assertIn(value,text)
        for forbidden in ('apt-get install','apt install','snap install',
                          'sudo ','systemctl restart','npm install -g',
                          '/opt/ferrari','/root/.local/share/motor-ferrari'):
            self.assertNotIn(forbidden,text)
    def test_fails_closed_if_unverified_tools(self):
        text=(ROOT/"install/vps-isolated-release.sh").read_text()
        self.assertIn('assert not missing and not external',text)
        self.assertIn('FERRARI_RELEASE_REGRESSION_TESTS=PASS',text)
        self.assertIn('FERRARI_RELEASE_NOT_ACTIVATED_CHECK_ONLY',text)
        self.assertIn('if [[ "$SWITCHED" == 1 && "$PASSED" != 1 ]]',text)

if __name__=="__main__":
    unittest.main()
