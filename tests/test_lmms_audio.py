"""LMMS offline, original two-note WAV export through the existing Ferrari runtime."""
import subprocess
import wave
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import tool_runtime


class LmmsAudioTests(unittest.TestCase):
    def test_typed_action_routes_one_local_project(self):
        actions=tool_runtime.specs()
        self.assertEqual(len(actions),35)
        spec=actions["lmms-project-wav"]
        self.assertEqual((spec["tool"],spec["binary"],spec["artifact"]),
                         ("lmms","lmms","lmms-render.wav"))
        self.assertEqual(spec["extensions"],[".mmp",".mmpz"])
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/lmms"):
            result=tool_runtime.auto("lmms para wav","/tmp/audio.mmp")
            self.assertEqual(result["selected"]["action"],"lmms-project-wav")

    def test_invocation_confines_state_and_validates_audio(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            inp=root/"music.mmp"
            inp.write_text('<lmms-project type="song"/>',encoding="utf-8")
            out=root/"render"
            def run(args,**kwargs):
                self.assertEqual(args,["/usr/bin/lmms","render",str(inp),
                                       "-o",str(out/"lmms-render.wav"),"-f","wav"])
                self.assertFalse(kwargs.get("shell",False))
                env=kwargs["env"]
                self.assertEqual(env["QT_QPA_PLATFORM"],"offscreen")
                for key in ("HOME","XDG_CACHE_HOME","XDG_CONFIG_HOME",
                            "XDG_DATA_HOME","XDG_RUNTIME_DIR"):
                    self.assertTrue(env[key].startswith(str(out)),key)
                with wave.open(str(out/"lmms-render.wav"),"wb") as audio:
                    audio.setnchannels(2)
                    audio.setsampwidth(2)
                    audio.setframerate(44100)
                    audio.writeframes(b"\\x01\\x00\\x02\\x00"*1024)
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/lmms"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                    result=tool_runtime.invoke("lmms-project-wav",str(inp),str(out))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["tool"],"lmms")

    def test_empty_or_invalid_wav_not_certified(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            src=root/"song.mmp";src.write_text("<lmms-project/>")
            out=root/"out"
            def run(args,**kwargs):
                (out/"lmms-render.wav").write_bytes(b"not a wave file"+b"x"*200)
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/lmms"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                    with self.assertRaisesRegex(RuntimeError,"valid PCM WAV"):
                        tool_runtime.invoke("lmms-project-wav",str(src),str(out))

    def test_wrong_format_and_missing_cli_rejected(self):
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            src=root/"song.txt";src.write_text("Ferrari")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/lmms"):
                with self.assertRaisesRegex(ValueError,"Input format"):
                    tool_runtime.invoke("lmms-project-wav",str(src),str(root/"out"))
            src=root/"song.mmp";src.write_text("<lmms-project/>")
            with patch.object(tool_runtime,"executable",return_value=None):
                with self.assertRaisesRegex(RuntimeError,"Executor not installed"):
                    tool_runtime.invoke("lmms-project-wav",str(src),str(root/"out2"))

    def test_real_smoke_checks_audio_and_not_just_exit_status(self):
        script=(Path(__file__).resolve().parents[1]/
                "install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn("--action lmms-project-wav",script)
        self.assertIn("FERRARI_LMMS_WAV_REAL=PASS",script)
        self.assertIn("getnframes()",script)


if __name__=="__main__":
    unittest.main()
