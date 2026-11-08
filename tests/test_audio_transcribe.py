"""Ferrari universal audio-transcribe: safe execution and REAL private CPU proof."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import urllib.request

from engine import audio_tools, ferrari, skill_job, tool_runtime


class AudioTranscribeTests(unittest.TestCase):
    def test_single_catalog_route_and_no_global_python(self):
        self.assertIn("audio-transcribe", ferrari.OPS)
        self.assertIn("audio-transcribe", tool_runtime.BASE_OPERATIONS["faster-whisper"])
        from engine import catalog_registry
        doc = catalog_registry.read_catalog()
        self.assertEqual(doc["counts"]["functions_base_operations"], 13)
        self.assertEqual(doc["counts"]["functions"], 273)
        self.assertEqual(doc["counts"]["all_catalog_entries"], 451)
        with self.assertRaises(ValueError):
            skill_job.validate_job({"version":1,"kind":"operation",
                                    "id":"asr-bad","operation":"not-a-real-tool"})
        self.assertIsNone(skill_job.validate_job(
            {"version":1,"kind":"operation","id":"asr-no-input",
             "operation":"audio-transcribe"}))
        self.assertEqual(audio_tools.MODEL_SHA256,
                         "dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1")
        self.assertNotIn("apt-get",Path(audio_tools.__file__).read_text())

    def test_reject_wrong_type_missing_symlink_and_oversized_audio(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            outside=root/"audio.txt"
            outside.write_bytes(b"x"*600)
            with self.assertRaises(ValueError):
                audio_tools.transcribe(outside,root/"out")
            wav=root/"audio.wav"
            wav.symlink_to(outside)
            with self.assertRaises(ValueError):
                audio_tools.transcribe(wav,root/"out")
            wav.unlink()
            wav.write_bytes(b"x"*(audio_tools.MAX_AUDIO_BYTES+1))
            with self.assertRaises(ValueError):
                audio_tools.transcribe(wav,root/"out")

    def test_real_wrapper_only_runs_private_worker_and_verifies_hashes(self):
        with TemporaryDirectory() as folder:
            root=Path(folder)
            audio=root/"hello.wav"
            audio.write_bytes(b"RIFF"+b"x"*500)
            out=root/"artifacts"
            def fake_process(args, **kw):
                self.assertEqual(args[1],"-I")
                self.assertEqual(args[3],"--worker")
                self.assertFalse(kw["shell"])
                self.assertLessEqual(kw["timeout"],180)
                self.assertEqual(kw["env"]["HF_HUB_OFFLINE"],"1")
                self.assertEqual(kw["env"]["TRANSFORMERS_OFFLINE"],"1")
                self.assertEqual(kw["env"]["HOME"],str(out))
                self.assertNotIn("PYTHONPATH",kw["env"])
                (out/"transcript.txt").write_text("Ferrari transcribes real audio\n")
                (out/"subtitles.srt").write_text("1\n00:00:00,000 --> 00:00:02,000\nFerrari transcribes real audio\n")
                (out/"transcript-report.json").write_text(json.dumps({
                    "status":"completed","model":"faster-whisper-tiny",
                    "segments":1,"duration_s":2,
                    "text_sha256":audio_tools._sha256(out/"transcript.txt"),
                    "srt_sha256":audio_tools._sha256(out/"subtitles.srt")}))
                return SimpleNamespace(returncode=0,stderr="",stdout="ok")
            with patch.object(audio_tools,"HOME",root), patch.object(
                    audio_tools,"available",return_value=True), patch.object(
                    audio_tools.subprocess,"run",side_effect=fake_process) as mock:
                ident,paths=audio_tools.transcribe(audio,out)
            self.assertIn("faster-whisper",ident)
            self.assertEqual(len(paths),3)
            mock.assert_called_once()

    def test_real_cpu_transcription_from_verifiable_public_fixture(self):
        # Runs on the VPS when the already installed private model exists.
        # CI runner without Ferrari's model does not claim proof by a mock.
        # CI containers can mount /srv/projects/skill-universal as a test
        # directory without the installed model. Only the *active release*
        # symlink identifies a real Ferrari VPS for mandatory ASR execution.
        if not (audio_tools.HOME / "current").is_symlink():
            self.skipTest("Not running on an activated Ferrari VPS release")
        self.assertTrue(audio_tools.available(),
                        "Ferrari VPS has no functional private faster-whisper model/venv")
        home=audio_tools.HOME
        fixture_commit="2a3a857737d17d974f30d818ebec69ce11929e5c"
        fixture_blob="e44b7c13897eae7f78beb220c61fe77429a3961d"
        url=("https://raw.githubusercontent.com/SYSTRAN/faster-whisper/"
             +fixture_commit+"/tests/data/jfk.flac")
        with TemporaryDirectory(prefix=".asr-functional-test-",dir=home/".runtime") as folder:
            work=Path(folder)
            src=work/"public-test-speech.flac"
            req=urllib.request.Request(url,headers={"User-Agent":"Ferrari-private-ASR-test"})
            with urllib.request.urlopen(req,timeout=50) as stream,src.open("xb") as target:
                data=stream.read(1_200_000)
                target.write(data)
            self.assertEqual(len(data),1_152_693)
            blob=hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()
            self.assertEqual(blob,fixture_blob)
            import base64
            from zipfile import ZipFile
            job={"version":1,"id":"ferrari-real-asr-jfk","kind":"operation",
                 "operation":"audio-transcribe",
                 "input":{"name":"public-test-speech.flac",
                          "content_base64":base64.b64encode(data).decode("ascii")},
                 "acceptance":{"required_extensions":[".txt",".srt",".json"]}}
            result,code=skill_job.execute(job,work/"output")
            self.assertEqual(code,0,result)
            self.assertEqual(result["status"],"completed")
            self.assertEqual(result["quality_gate"]["status"],"passed")
            self.assertTrue(result["executor"].endswith(":faster-whisper-cpu"))
            bundle=work/"output/response.zip"
            with ZipFile(bundle) as archive:
                self.assertIsNone(archive.testzip())
                self.assertTrue({"report.json","artifacts/transcript.txt",
                                 "artifacts/subtitles.srt",
                                 "artifacts/transcript-report.json"}.issubset(archive.namelist()))
                proof=json.loads(archive.read("artifacts/transcript-report.json"))
                transcript=archive.read("artifacts/transcript.txt").decode("utf-8").lower()
                subtitles=archive.read("artifacts/subtitles.srt").decode("utf-8")
            self.assertEqual(proof["status"],"completed")
            self.assertEqual(proof["language_detected"],"en")
            self.assertGreater(proof["segments"],0)
            for word in ("ask","country","americans"):
                self.assertIn(word,transcript)
            self.assertIn("-->",subtitles)
            self.assertFalse(proof["semantic_accuracy_certified"])
            print("FERRARI_REAL_ASR_SKILL_TO_ZIP=PASS segments=" +
                  str(proof["segments"]))


if __name__=="__main__":
    unittest.main()
