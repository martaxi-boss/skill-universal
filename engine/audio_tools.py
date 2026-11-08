"""Ferrari audio-to-text: real private faster-whisper CPU operation.

An installed Python package is NOT an integrated workflow. This operation
converts a bounded user audio file into TXT + timed SRT + JSON proof using the
already certified, Ferrari-owned tiny CTranslate2 model. No external network,
global Python, model download, host daemon or arbitrary command arguments.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

HOME = Path("/srv/projects/skill-universal")
VENV = HOME / ".runtime/venvs/extended/faster-whisper"
PYTHON = VENV / "bin/python"
MODEL = HOME / ".runtime/models/faster-whisper-tiny-d90ca5fe"
MODEL_SHA256 = "dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1"
AUDIO_SUFFIXES = frozenset({".wav", ".flac", ".mp3", ".m4a", ".ogg"})
MAX_AUDIO_BYTES = 2_000_000
MAX_SECONDS = 60
MAX_SAMPLES = 16000 * MAX_SECONDS


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1_048_576), b""):
            digest.update(block)
    return digest.hexdigest()


def available() -> bool:
    """Private runtime readiness, NOT a substitute for the real ASR test."""
    try:
        root = HOME.resolve(strict=True)
        return bool(
            VENV.is_dir() and not VENV.is_symlink()
            and PYTHON.is_file() and os.access(PYTHON, os.X_OK)
            and PYTHON.resolve(strict=True).is_relative_to(root)
            and (VENV / "lib/python3.12/site-packages/faster_whisper").is_dir()
            and MODEL.is_dir() and not MODEL.is_symlink()
            and (MODEL / "model.bin").is_file()
            and (MODEL / "config.json").is_file()
            and MODEL.resolve(strict=True).is_relative_to(root))
    except (OSError, RuntimeError):
        return False


def _timestamp(seconds: float) -> str:
    ms = round(max(0.0, seconds) * 1000)
    hours, ms = divmod(ms, 3_600_000)
    minutes, ms = divmod(ms, 60_000)
    sec, ms = divmod(ms, 1000)
    return f"{hours:02d}:{minutes:02d}:{sec:02d},{ms:03d}"


def transcribe(source: Path, output_dir: Path):
    """Execute private ASR. No TTS, no claim of natural or accurate speech."""
    source = Path(source)
    output_dir = Path(output_dir)
    if (source.is_symlink() or not source.is_file()
            or source.suffix.lower() not in AUDIO_SUFFIXES
            or not 200 <= source.stat().st_size <= MAX_AUDIO_BYTES):
        raise ValueError("Ferrari ASR requires a regular WAV/FLAC/MP3/M4A/OGG file up to 2 MB")
    if not available():
        raise RuntimeError("Ferrari private faster-whisper CPU/model is unavailable")
    if output_dir.is_symlink() or not output_dir.resolve().is_relative_to(HOME.resolve()):
        raise ValueError("Ferrari ASR output must be inside the project")
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    names = ["transcript.txt", "subtitles.srt", "transcript-report.json"]
    if any((output_dir / n).exists() or (output_dir / n).is_symlink() for n in names):
        raise FileExistsError("Ferrari refuses to overwrite ASR artifacts")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    env.update({
        "PYTHONNOUSERSITE": "1", "HF_HUB_OFFLINE": "1",
        "TRANSFORMERS_OFFLINE": "1", "HF_HUB_DISABLE_TELEMETRY": "1",
        "CUDA_VISIBLE_DEVICES": "", "OMP_NUM_THREADS": "2",
        "MKL_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "2",
        "HOME": str(output_dir), "TMPDIR": str(output_dir),
        "XDG_CACHE_HOME": str(output_dir), "XDG_CONFIG_HOME": str(output_dir),
        "XDG_DATA_HOME": str(output_dir), "XDG_RUNTIME_DIR": str(output_dir),
    })
    try:
        completed = subprocess.run(
            [str(PYTHON), "-I", str(Path(__file__).resolve(strict=True)),
             "--worker", str(source), str(output_dir)],
            shell=False, capture_output=True, text=True, errors="replace",
            timeout=180, cwd=str(output_dir), env=env, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Ferrari private ASR exceeded the 180-second limit") from exc
    if completed.returncode:
        raise RuntimeError("Ferrari private ASR failed: " + completed.stderr[-600:])
    paths = [output_dir / n for n in names]
    if any(p.is_symlink() or not p.is_file() or p.stat().st_size < 10 for p in paths):
        raise RuntimeError("Ferrari ASR failed to produce real TXT/SRT/JSON files")
    report = json.loads(paths[2].read_text(encoding="utf-8"))
    if (report.get("status") != "completed" or report.get("model") != "faster-whisper-tiny"
            or not report.get("segments") or not report.get("duration_s")
            or report.get("text_sha256") != _sha256(paths[0])
            or report.get("srt_sha256") != _sha256(paths[1])):
        raise RuntimeError("Ferrari ASR output or provenance verification failed")
    return str(PYTHON) + ":faster-whisper-cpu", paths


def _worker(source: Path, output_dir: Path) -> int:
    if (Path(sys.prefix).resolve(strict=True) != VENV.resolve(strict=True)
            or not available() or MODEL.is_symlink()
            or _sha256(MODEL / "model.bin") != MODEL_SHA256):
        raise RuntimeError("Ferrari private Whisper interpreter/model integrity failed")
    if (source.is_symlink() or not source.is_file()
            or source.suffix.lower() not in AUDIO_SUFFIXES
            or not 200 <= source.stat().st_size <= MAX_AUDIO_BYTES):
        raise ValueError("Unapproved Ferrari audio input")
    started = time.monotonic()
    import av
    import numpy as np
    from av.audio.resampler import AudioResampler
    from faster_whisper import WhisperModel
    chunks = []
    sample_count = 0
    with av.open(str(source), mode="r") as container:
        streams = [s for s in container.streams if s.type == "audio"]
        if not streams:
            raise ValueError("Input has no audio stream")
        resampler = AudioResampler(format="s16", layout="mono", rate=16000)
        for frame in container.decode(audio=streams[0].index):
            for chunk in resampler.resample(frame):
                signal = chunk.to_ndarray().reshape(-1)
                sample_count += len(signal)
                if sample_count > MAX_SAMPLES:
                    raise ValueError("Ferrari transcription is limited to 60 seconds")
                chunks.append(signal)
        for chunk in resampler.resample(None):
            signal = chunk.to_ndarray().reshape(-1)
            sample_count += len(signal)
            if sample_count > MAX_SAMPLES:
                raise ValueError("Ferrari transcription is limited to 60 seconds")
            chunks.append(signal)
    if not chunks or sample_count < 1600:
        raise ValueError("Audio is empty or too short")
    samples = np.concatenate(chunks).astype(np.float32) / 32768.0
    if not np.isfinite(samples).all() or float(np.sqrt(np.mean(samples * samples))) <= 0.001:
        raise ValueError("Audio is silent or invalid; no transcript certified")
    model = WhisperModel(str(MODEL), device="cpu", compute_type="int8",
                         cpu_threads=2, num_workers=1, local_files_only=True)
    segments, info = model.transcribe(
        samples, language=None, beam_size=1,
        condition_on_previous_text=False, vad_filter=False, temperature=0.0)
    found = list(segments)
    if not found or any(x.end <= x.start for x in found):
        raise RuntimeError("No real, timestamped Whisper speech segments")
    spoken = " ".join(x.text.strip() for x in found).strip()
    if len(spoken) < 12:
        raise RuntimeError("Whisper returned no meaningful text")
    srt = "\n".join(
        f"{i}\n{_timestamp(x.start)} --> {_timestamp(x.end)}\n{x.text.strip()}\n"
        for i, x in enumerate(found, 1)) + "\n"
    output_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
    txt_file = output_dir / "transcript.txt"
    srt_file = output_dir / "subtitles.srt"
    with txt_file.open("x", encoding="utf-8") as f:
        f.write(spoken + "\n")
    with srt_file.open("x", encoding="utf-8") as f:
        f.write(srt)
    report = {
        "status": "completed", "model": "faster-whisper-tiny",
        "model_sha256": MODEL_SHA256,
        "execution": "Ferrari-owned CPU; PyAV19 offline decode; no external API",
        "input_sha256": _sha256(source),
        "language_detected": info.language,
        "language_probability": round(float(info.language_probability), 3),
        "duration_s": round(len(samples) / 16000.0, 3),
        "segments": len(found), "elapsed_s": round(time.monotonic() - started, 3),
        "text_sha256": _sha256(txt_file), "srt_sha256": _sha256(srt_file),
        "semantic_accuracy_certified": False, "speaker_identity_certified": False,
        "note": "Whisper CPU automatic transcript, not editorially approved speech or translation",
    }
    with (output_dir / "transcript-report.json").open("x", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print("FERRARI_AUDIO_TRANSCRIBE=PASS segments=" + str(len(found)), flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "--worker":
        raise SystemExit("Only the Ferrari fixed --worker SRC OUTDIR entrypoint is supported")
    try:
        raise SystemExit(_worker(Path(sys.argv[2]), Path(sys.argv[3])))
    except Exception as exc:
        print("FERRARI_AUDIO_TRANSCRIBE_FAILED=" + str(exc)[:480], file=sys.stderr)
        raise SystemExit(2)
