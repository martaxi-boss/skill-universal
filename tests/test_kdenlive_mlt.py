"""Render an MLT/Kdenlive project into MP4 using the installed MLT CLI."""
import json
import subprocess
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from engine import tool_runtime

class MltVideoTests(unittest.TestCase):
    def test_manifest_and_route(self):
        actions=tool_runtime.specs()
        self.assertEqual(len(actions),40)
        spec=actions["kdenlive-mlt-mp4"]
        self.assertEqual((spec["tool"],spec["binary"],spec["artifact"]),
                         ("kdenlive","melt","mlt-video.mp4"))
        self.assertEqual(spec["extensions"],[".mlt",".kdenlive"])
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/melt"):
            result=tool_runtime.auto("kdenlive mlt para mp4","/tmp/test.mlt")
            self.assertEqual(result["selected"]["action"],"kdenlive-mlt-mp4")

    def test_render_and_ffprobe_use_installed_tools(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            src=base/"sample.mlt"
            src.write_text("<mlt/>",encoding="utf-8")
            out=base/"output"
            seen=[]
            def run(args,**kwargs):
                seen.append(args)
                self.assertFalse(kwargs.get("shell",False))
                if args[0]=="/usr/bin/melt":
                    self.assertEqual(args[1],str(src))
                    self.assertEqual(args[2:4],["-consumer","avformat:"+str(out/"mlt-video.mp4")])
                    self.assertIn("vcodec=libx264",args)
                    env=kwargs["env"]
                    self.assertEqual(env["LC_NUMERIC"],"C")
                    for key in ("HOME","XDG_CONFIG_HOME","XDG_DATA_HOME","XDG_RUNTIME_DIR"):
                        self.assertTrue(env[key].startswith(str(out)),key)
                    (out/"mlt-video.mp4").write_bytes(b"movie"+b"x"*1600)
                    return subprocess.CompletedProcess(args,0,b"",b"")
                self.assertEqual(args[0],"/usr/bin/ffprobe")
                data={"streams":[{"codec_type":"video","codec_name":"h264",
                                  "width":320,"height":180}],"format":{"duration":"2.0"}}
                return subprocess.CompletedProcess(args,0,json.dumps(data).encode(),b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/melt"):
                with patch.object(tool_runtime.shutil,"which",return_value="/usr/bin/ffprobe"):
                    with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                        result=tool_runtime.invoke("kdenlive-mlt-mp4",str(src),str(out))
            self.assertTrue(result["confirmed"])
            self.assertEqual(len(seen),2)

    def test_corrupt_video_not_accepted(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            src=base/"sample.mlt";src.write_text("<mlt/>")
            out=base/"out"
            def run(args,**kwargs):
                if args[0]=="/usr/bin/melt":
                    (out/"mlt-video.mp4").write_bytes(b"fake"+b"x"*1800)
                    return subprocess.CompletedProcess(args,0,b"",b"")
                return subprocess.CompletedProcess(args,1,b"",b"bad codec")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/melt"):
                with patch.object(tool_runtime.shutil,"which",return_value="/usr/bin/ffprobe"):
                    with patch.object(tool_runtime.subprocess,"run",side_effect=run):
                        with self.assertRaisesRegex(RuntimeError,"FFprobe"):
                            tool_runtime.invoke("kdenlive-mlt-mp4",str(src),str(out))

    def test_missing_melt_and_bad_input_rejected(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp);src=base/"x.txt";src.write_text("Ferrari")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/melt"):
                with self.assertRaisesRegex(ValueError,"Input format"):
                    tool_runtime.invoke("kdenlive-mlt-mp4",str(src),str(base/"out"))
            src=base/"x.mlt";src.write_text("<mlt/>")
            with patch.object(tool_runtime,"executable",return_value=None):
                with self.assertRaisesRegex(RuntimeError,"Executor not installed"):
                    tool_runtime.invoke("kdenlive-mlt-mp4",str(src),str(base/"out2"))

    def test_real_vps_smoke_command_and_probe(self):
        text=(Path(__file__).resolve().parents[1]/
              "install/vps-tool-runtime-smoke.sh").read_text()
        self.assertIn("--action kdenlive-mlt-mp4",text)
        self.assertIn("FERRARI_KDENLIVE_MLT_MP4_REAL=PASS",text)
        self.assertIn("ffprobe",text)

if __name__=="__main__":
    unittest.main()
