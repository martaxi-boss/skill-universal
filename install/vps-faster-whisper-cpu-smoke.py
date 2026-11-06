#!/usr/bin/env python3
"""One-shot *real* faster-whisper CPU proof using licensed public test speech.

No server, no global ffmpeg/pip/apt. Download only a pinned public JFK FLAC
fixture with a verified Git blob digest, transcribe it with the private CTranslate2
tiny model and export TXT+SRT+JSON inside the Ferrari project folder.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import resource
import sys
import tempfile
import time
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
VENV = ROOT / ".runtime/venvs/extended/faster-whisper"
MODEL = ROOT / ".runtime/models/faster-whisper-tiny-d90ca5fe"
OUTPUT = ROOT / ".runtime/faster-whisper-proof-20261106"
MODEL_SHA256 = "dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1"
SOURCE_REVISION = "2a3a857737d17d974f30d818ebec69ce11929e5c"
AUDIO_SHA1_GITBLOB = "e44b7c13897eae7f78beb220c61fe77429a3961d"
AUDIO_SIZE = 1_152_693
AUDIO_URL = (
    "https://raw.githubusercontent.com/SYSTRAN/faster-whisper/"
    + SOURCE_REVISION + "/tests/data/jfk.flac"
)


def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as file:
        for data in iter(lambda:file.read(2*1024*1024), b""):
            h.update(data)
    return h.hexdigest()


def timestamp(seconds: float) -> str:
    ms=round(max(0,seconds)*1000)
    h,ms=divmod(ms,3_600_000)
    m,ms=divmod(ms,60_000)
    s,ms=divmod(ms,1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main() -> int:
    if not ROOT.is_dir() or ROOT.is_symlink():
        raise RuntimeError("FERRARI_WHISPER_PROJECT_MISSING")
    if Path(sys.prefix).resolve(strict=True) != VENV.resolve(strict=True):
        raise RuntimeError("FERRARI_WHISPER_PRIVATE_VENV_NOT_SELECTED")
    if not VENV.is_dir() or VENV.is_symlink() or not VENV.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("FERRARI_WHISPER_VENV_OUTSIDE_PROJECT")
    if not MODEL.is_dir() or MODEL.is_symlink():
        raise RuntimeError("FERRARI_WHISPER_MODEL_NOT_INSTALLED")
    if sha256(MODEL/"model.bin") != MODEL_SHA256:
        raise RuntimeError("FERRARI_WHISPER_MODEL_INTEGRITY_MISMATCH")
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("FERRARI_WHISPER_PROOF_OUTPUT_ALREADY_EXISTS")
    # Follow the *actual* systemd scope of the current process; no invocation
    # is accepted if resource isolation was omitted by the VPS workflow.
    cgroup=Path("/sys/fs/cgroup")
    rows=Path("/proc/self/cgroup").read_text().splitlines()
    path=next((row.split("::",1)[1] for row in rows if "::" in row),None)
    if not path or ".." in path:
        raise RuntimeError("FERRARI_WHISPER_CGROUP_PATH_INVALID")
    limit_path=cgroup/path.lstrip("/")/"memory.max"
    limit=limit_path.read_text().strip() if limit_path.is_file() else "max"
    if limit=="max" or not 512*1024**2<int(limit)<=2_500_000_000:
        raise RuntimeError("FERRARI_WHISPER_RESOURCE_CGROUP_NOT_BOUNDED="+limit)
    os.environ.update({
        "HF_HUB_OFFLINE":"1",
        "TRANSFORMERS_OFFLINE":"1",
        "CUDA_VISIBLE_DEVICES":"",
        "OMP_NUM_THREADS":"2",
        "MKL_NUM_THREADS":"2",
        "OPENBLAS_NUM_THREADS":"2",
        "PYTHONNOUSERSITE":"1",
        "HOME":str(ROOT/".runtime"),
        "XDG_CACHE_HOME":str(ROOT/".runtime"),
    })
    start=time.monotonic()
    work_parent=ROOT/".runtime"
    with tempfile.TemporaryDirectory(prefix=".ferrari-whisper-input-",dir=work_parent) as tmp:
        audio=Path(tmp)/"jfk.flac"
        with urllib.request.urlopen(
            urllib.request.Request(AUDIO_URL,headers={"User-Agent":"Ferrari-ASR-P3/1.0"}),
            timeout=60,
        ) as inp, audio.open("xb") as dst:
            total=0
            for data in iter(lambda:inp.read(2*1024*1024),b""):
                total+=len(data)
                if total>AUDIO_SIZE:
                    raise RuntimeError("FERRARI_WHISPER_FIXTURE_SIZE_EXCEEDED")
                dst.write(data)
        if total!=AUDIO_SIZE:
            raise RuntimeError("FERRARI_WHISPER_FIXTURE_SIZE_MISMATCH")
        content=audio.read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(content)).encode()+b"\0"+content).hexdigest()
        if blob!=AUDIO_SHA1_GITBLOB:
            raise RuntimeError("FERRARI_WHISPER_FIXTURE_GIT_BLOB_MISMATCH")
        print("FERRARI_WHISPER_PUBLIC_AUDIO_SHA1=PASS",flush=True)
        from faster_whisper import WhisperModel
        model=WhisperModel(
            str(MODEL),device="cpu",compute_type="int8",
            cpu_threads=2,num_workers=1,local_files_only=True,
        )
        print("FERRARI_WHISPER_PRIVATE_MODEL_LOADED=PASS",flush=True)
        segments,info=model.transcribe(
            str(audio),language="en",beam_size=1,
            condition_on_previous_text=False,vad_filter=False,
            temperature=0.0,
        )
        found=list(segments)
    if not found:
        raise RuntimeError("FERRARI_WHISPER_EMPTY_TRANSCRIPT")
    text=" ".join(s.text.strip() for s in found).strip()
    normalized=text.lower()
    if len(text)<65 or not all(t in normalized for t in ("ask","country","americans")):
        raise RuntimeError("FERRARI_WHISPER_TRANSCRIPT_CONTENT_MISMATCH")
    if info.language!="en" or any(s.end<=s.start for s in found):
        raise RuntimeError("FERRARI_WHISPER_SEGMENT_OR_LANGUAGE_INVALID")
    srts=[]
    for i,s in enumerate(found,1):
        srts.append(f"{i}\n{timestamp(s.start)} --> {timestamp(s.end)}\n{s.text.strip()}\n")
    OUTPUT.mkdir(mode=0o700,parents=False)
    txt=OUTPUT/"transcript.txt"
    srt=OUTPUT/"subtitles.srt"
    txt.write_text(text+"\n",encoding="utf-8")
    srt.write_text("\n".join(srts)+"\n",encoding="utf-8")
    report={
        "status":"completed",
        "engine":"faster-whisper",
        "device":"cpu",
        "compute_type":"int8",
        "model_repository":"Systran/faster-whisper-tiny",
        "model_revision":"d90ca5fe260221311c53c58e660288d3deb8d356",
        "model_sha256":MODEL_SHA256,
        "input_repository":"SYSTRAN/faster-whisper",
        "input_git_commit":SOURCE_REVISION,
        "input_git_blob_sha1":AUDIO_SHA1_GITBLOB,
        "language":info.language,
        "duration_seconds":round(info.duration,2),
        "segments":len(found),
        "time_seconds":round(time.monotonic()-start,2),
        "peak_rss_mib":round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1),
        "artifacts":{
            "transcript.txt":sha256(txt),
            "subtitles.srt":sha256(srt),
        },
    }
    (OUTPUT/"report.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print("FERRARI_WHISPER_REAL_ASR=PASS language=en segments="+str(len(found)),flush=True)
    print("FERRARI_WHISPER_TEXT="+text[:240],flush=True)
    print("FERRARI_WHISPER_ELAPSED_SECONDS="+str(report["time_seconds"]),flush=True)
    print("FERRARI_WHISPER_PEAK_RSS_MIB="+str(report["peak_rss_mib"]),flush=True)
    return 0


if __name__=="__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("FERRARI_WHISPER_REAL_ASR_FAILED="+str(exc)[:700],file=sys.stderr)
        raise
