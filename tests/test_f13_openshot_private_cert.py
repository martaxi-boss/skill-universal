"""Ferrari F13 private OpenShot: isolate mode, reject false positive outputs."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from contextlib import nullcontext
from unittest.mock import patch
import unittest

ROOT=Path(__file__).resolve().parents[1]
PATH=ROOT/"install/vps-f13-openshot-headless-certify.py"
SPEC=spec_from_file_location("f13_openshot",PATH)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class F13OpenShotTests(unittest.TestCase):
    def test_protected_release_and_services(self):
        self.assertEqual(m.ACTIVE,"3f0ba44b7d8475a74a63c6010d1e27063c04bf1e")
        self.assertEqual(m.FALLBACK,"427e1c33c6d10ca8ecd2103861adccd3d552c381")
        self.assertEqual(len(m.SERVICES),8)
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"NONROOT"):
                m.guard()
    def test_cli_json_requires_real_success(self):
        self.assertEqual(m.answer('{"ok":true,"result":{"id":"abcd"}}',"CHECK"),{"id":"abcd"})
        for bad in ('not JSON', '{"ok":false,"result":{}}', '[]', '{"ok":true}', '{"ok":true,"result":null}'):
            with self.subTest(value=bad):
                with self.assertRaises(RuntimeError):
                    m.answer(bad,"CHECK")
    def test_real_openshot_nested_result_ids(self):
        # Readback of real VPS blocked F13 first-run:
        # result={revision, transaction_id, data:{id,...}}.
        self.assertEqual(m.result_id({"revision":1,"transaction_id":"x",
                                      "data":{"id":"KPUDL9QPWC","name":"synthetic-source.mp4"}},"IMPORTED_FILE"),"KPUDL9QPWC")
        self.assertEqual(m.result_id({"data":{"id":"CLIP01"}},"EDITED_CLIP"),"CLIP01")
        self.assertEqual(m.result_id({"clip":{"clip_id":"CLIP02"}},"EDITED_CLIP"),"CLIP02")
        with self.assertRaisesRegex(RuntimeError,"MISSING_ID"):
            m.result_id({"transaction_id":"t","data":{"name":"missing"}},"EDITED_CLIP")

    def test_editable_project_and_video_are_distinct_evidence(self):
        s=PATH.read_text(encoding="utf-8")
        for marker in ('"session", "start"', '"file", "import"',
                       '"clip", "add"', '"project", "save"',
                       '"export", "start"', '"session", "stop"',
                       "project_osp_sha256", "edited_mp4_sha256",
                       "exported_duration_seconds", "real_edit_export_certified"):
            self.assertIn(marker,s)
        for bad in ("sudo ","apt-get install","os.system(","shell=True","rm -rf","systemctl stop","--autopilot","curl "):
            self.assertNotIn(bad,s)
    def test_probe_is_not_promoted_to_full_cert(self):
        with patch.object(m,"guard"),patch.object(m,"private_tools",return_value=("/private/openshot","/private/ffmpeg","/private/ffprobe")), \
             patch.object(m,"env_for",return_value={}), patch.object(m,"run",return_value="session clip export"):
            # A simple simulated CLI-help probe must explicitly say not certified.
            with patch.object(m.tempfile,"TemporaryDirectory",return_value=nullcontext("/tmp")):
                res=m.probe()
        self.assertFalse(res["real_edit_export_certified"])
        self.assertEqual(res["mode"],"probe")

if __name__=="__main__":
    unittest.main()
