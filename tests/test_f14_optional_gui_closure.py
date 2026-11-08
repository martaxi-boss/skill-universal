"""Ferrari F14 must report per-application evidence, without global writes."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import unittest
ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"install/vps-f14-final-optional-gui-certify.py"
SPEC=spec_from_file_location("f14_closure",SOURCE)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class F14Closeout(unittest.TestCase):
    def test_release_rollback_and_8_services_immutable(self):
        self.assertEqual(m.ACTIVE,"3f0ba44b7d8475a74a63c6010d1e27063c04bf1e")
        self.assertEqual(m.FALLBACK,"427e1c33c6d10ca8ecd2103861adccd3d552c381")
        self.assertEqual(len(m.SERVICES),8)
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"UNPRIVILEGED"):
                m.guard()
    def test_solvespace_fixture_has_public_native_header(self):
        data=m.SOLVESPACE_FIXTURE.encode("latin-1")
        self.assertGreater(len(data),4000)
        self.assertTrue(data.startswith(b"\xb1\xb2\xb3SolveSpaceREV"))
    def test_audacity4_is_not_falsely_promoted(self):
        with patch.object(m,"private_exe",return_value="/tmp/ferrari-audacity"):
            result=m.audacity_check(Path("/tmp"))
        self.assertEqual(result["status"],"not_certified")
        self.assertFalse(result["headless_editing_demonstrated"])
    def test_each_program_requires_real_output_and_private_sources(self):
        s=SOURCE.read_text(encoding="utf-8")
        for marker in ("real_passed", "unverified_apps_not_counted_as_pass",
           "SOLVESPACE_FIXTURE", "export-view", "svg_sha256",
           "SIF=", "frame_changed", "F14_SYNFIG_ANIMATED_FRAME_IDENTICAL",
           "camera_mic_screen_and_stream_disabled", "protected_services",
           "ffprobe", "b\"\\x89PNG", "project"):
            if marker=="project":
                self.assertIn("ROOT=",s)
            else:
                self.assertIn(marker,s)
        for forbidden in ("sudo ", "apt-get install", "systemctl stop",
          "shell=True", "os.system(", "rm -rf", "--startstreaming"):
            self.assertNotIn(forbidden,s)
        self.assertIn("AuxAudioDevice1=disabled",s)
        self.assertIn("DesktopAudioDevice1=disabled",s)
        self.assertIn("startrecording",s)

if __name__=="__main__":
    unittest.main()
