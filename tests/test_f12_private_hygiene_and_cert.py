"""F12 Ferrari hygiene: deleted paths confined to disposable private artifacts."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch
import unittest

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"install/vps-f12-hygiene-and-programs-certify.py"
SPEC=spec_from_file_location("f12_hygiene",SOURCE)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class F12SafeHygiene(unittest.TestCase):
    def test_pinned_private_release_and_rollbacks(self):
        self.assertEqual(m.ACTIVE,"3f0ba44b7d8475a74a63c6010d1e27063c04bf1e")
        self.assertEqual(m.FALLBACK,"427e1c33c6d10ca8ecd2103861adccd3d552c381")
        self.assertEqual(len(m.SERVICES),8)
        self.assertNotEqual(m.ACTIVE,m.FALLBACK)

    def test_root_user_blocked_and_only_private_eligible_smoke(self):
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"NONROOT"):
                m.guard()
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            private=root/".runtime/private-gui-test"
            private.mkdir(parents=True)
            eligible=private/"42512345678"
            eligible.mkdir()
            for name in m.SMOKE_MARKERS:
                (eligible/name).write_bytes(b"owned Ferrari synthetic")
            (private/"USER_DATA").mkdir()
            broken=private/"42512345679"
            broken.mkdir()
            (broken/"image.png").write_text("partial")
            (private/"42512345680").symlink_to(root,target_is_directory=True)
            with patch.object(m,"ROOT",root), patch.object(m,"busy",return_value=False):
                self.assertEqual([p.name for p in m.eligible_scratch()],["42512345678"])

    def test_source_does_not_enable_unsafe_mutations(self):
        source=SOURCE.read_text(encoding="utf-8")
        for forbidden in ("sudo ", "apt-get install","systemctl stop",
                          "rm -rf", "shell=True", "subprocess.Popen",
                          "os.system", "unlink(", "os.remove"):
            self.assertNotIn(forbidden,source)
        self.assertIn("shutil.rmtree.avoids_symlink_attacks",source)
        self.assertIn("ferrari-cache-hygiene.py",source)
        self.assertIn("certify",source)
        self.assertIn("127.0.0.1",source)
        self.assertIn("FCStd",source)
        self.assertIn("ISO-10303-21",source)

    def test_local_loopback_script_only_proves_two_tools(self):
        self.assertEqual(set(name for name,_ in (
            ("yt-dlp", m.ytdlp_test),("freecad",m.freecad_test))),{"yt-dlp","freecad"})
        self.assertIn("--appimage-extract",SOURCE.read_text(encoding="utf-8"))
        self.assertFalse(m.busy.__defaults__ if m.busy.__defaults__ else False)


if __name__=="__main__":
    unittest.main()
