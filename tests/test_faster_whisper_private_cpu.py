"""Ferrari P3: network-free regressions for private, pinned CPU ASR.

Actual decoder/model inference is proven independently by a VPS GitHub Action.
"""
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
INSTALL=ROOT/"install/vps-faster-whisper-tiny-model.py"
SMOKE=ROOT/"install/vps-faster-whisper-cpu-smoke.py"


class WhisperP3Tests(unittest.TestCase):
    def test_model_pin_and_origin(self):
        code=INSTALL.read_text(encoding="utf-8")
        self.assertIn("d90ca5fe260221311c53c58e660288d3deb8d356",code)
        self.assertIn("dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1",code)
        self.assertIn("Systran/faster-whisper-tiny",code)
        self.assertIn("/srv/projects/skill-universal",code)
        self.assertIn("FERRARI_WHISPER_GLOBAL_APT_PIP_CHANGES=ZERO",code)
        self.assertNotIn("pip install",code)
        self.assertNotIn("apt-get",code)
        compile(code,str(INSTALL),"exec")

    def test_only_four_pinned_model_inputs(self):
        scope=runpy.run_path(str(INSTALL))
        self.assertEqual(set(scope["FILES"]),{
            "model.bin","config.json","tokenizer.json","vocabulary.txt"})
        self.assertEqual(scope["REPO"],"Systran/faster-whisper-tiny")
        self.assertEqual(scope["REV"],"d90ca5fe260221311c53c58e660288d3deb8d356")
        self.assertEqual(scope["MODEL_SHA256"],"dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1")

    def test_private_manifest_integrity_rejects_tampering(self):
        scope=runpy.run_path(str(INSTALL))
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            staging=root/"model"
            staging.mkdir()
            inputs={
              "model.bin":b"synthetic-model-data",
              "config.json":json.dumps({"lang_ids":list(range(100))}).encode(),
              "tokenizer.json":b'{"model":{}}',
              "vocabulary.txt":b"word\n"*24_000,
            }
            for name,contents in inputs.items():
                (staging/name).write_bytes(contents)
            hashbin=hashlib.sha256(inputs["model.bin"]).hexdigest()
            provenance={
              "repository":scope["REPO"],
              "revision":scope["REV"],
              "model_sha256":hashbin,
              "all_file_sha256":{n:hashlib.sha256(b).hexdigest() for n,b in inputs.items()},
            }
            (staging/"FERRARI_PROVENANCE.json").write_text(json.dumps(provenance))
            with patch.dict(scope["verify"].__globals__,{
                "ROOT":root,"MODEL_SHA256":hashbin,
                "FILES":{n:(len(v)+100,max(0,len(v)-2)) for n,v in inputs.items()},
            }):
                self.assertTrue(scope["verify"](staging))
                (staging/"vocabulary.txt").write_bytes(b"modified"+inputs["vocabulary.txt"])
                self.assertFalse(scope["verify"](staging))

    def test_transcription_is_restricted_to_private_cpu_and_verified_fixture(self):
        code=SMOKE.read_text(encoding="utf-8")
        compile(code,str(SMOKE),"exec")
        for token in ("compute_type=\"int8\"","device=\"cpu\"",
                      "cpu_threads=2","num_workers=1","local_files_only=True",
                      "FERRARI_WHISPER_REAL_ASR=PASS",
                      "e44b7c13897eae7f78beb220c61fe77429a3961d",
                      "2a3a857737d17d974f30d818ebec69ce11929e5c",
                      "memory.max","transcript.txt","subtitles.srt"):
            self.assertIn(token,code,token)
        self.assertNotIn("ffmpeg -i",code)
        self.assertNotIn("pip install",code)

    def test_subtitle_timestamp(self):
        scope=runpy.run_path(str(SMOKE))
        self.assertEqual(scope["timestamp"](0),"00:00:00,000")
        self.assertEqual(scope["timestamp"](62.125),"00:01:02,125")


if __name__=="__main__":
    unittest.main()
