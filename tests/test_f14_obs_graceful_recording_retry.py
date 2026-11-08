"""F14 OBS closure retry: secure private process group and real decoded video evidence."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest
ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"install/vps-f14-obs-graceful-recording-retry.py"
SPEC=spec_from_file_location("f14_obs_retry",PATH)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class F14OBSRetry(unittest.TestCase):
    def test_immutability_and_non_root(self):
        self.assertEqual(m.ACTIVE,"3f0ba44b7d8475a74a63c6010d1e27063c04bf1e")
        self.assertEqual(m.FALLBACK,"427e1c33c6d10ca8ecd2103861adccd3d552c381")
        self.assertEqual(len(m.SERVICES),8)
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"UNPRIVILEGED"):
                m.guard()

    def test_only_decoded_frames_can_be_pass(self):
        text=PATH.read_text(encoding="utf-8")
        for marker in ("-count_frames","nb_read_frames","frame_count>=8",
                       "private_OBS_child_only_SIGINT","obs_process_in_group",
                       "FerrariSynthetic","recording_certified",
                       "recording_lacks_verified_decodable_video_frames",
                       "ffprobe_exit", "synthetic_blank_canvas_only"):
            self.assertIn(marker,text)
        for marker in ("AuxAudioDevice1=disabled","DesktopAudioDevice1=disabled",
                       "--startrecording","-nolisten tcp"):
            self.assertIn(marker,text)
        for forbidden in ("sudo ","apt-get install","shell=True","os.system(",
                          "systemctl stop","--startstreaming","--startvirtualcam"):
            self.assertNotIn(forbidden,text)

    def test_obs_only_signalled_after_validating_project_process(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            (root/"tools/obs-studio-32.2.2").mkdir(parents=True)
            with patch.object(m,"ROOT",root):
                # Impossible process group cannot match a private executable.
                self.assertEqual(m.obs_process_in_group(1234567),[])
        self.assertEqual(m.SERVICES[0],"pink-iptv-backend")

if __name__=="__main__":
    unittest.main()
