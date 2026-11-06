#!/usr/bin/env python3
"""Install one MIT-licensed CTranslate2 Whisper tiny model inside Ferrari only.

The source is a fixed Hugging Face commit. The 75 MB model binary is checked
against the upstream SHA256. Atomic in-project staging; no apt, pip or HOME
cache, no overwrite and no files outside /srv/projects/skill-universal.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.error
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
VENV = ROOT / ".runtime/venvs/extended/faster-whisper"
MODEL_DIR = ROOT / ".runtime/models/faster-whisper-tiny-d90ca5fe"
REV = "d90ca5fe260221311c53c58e660288d3deb8d356"
REPO = "Systran/faster-whisper-tiny"
BASE_URL = "https://huggingface.co/" + REPO + "/resolve/" + REV + "/"
MODEL_SHA256 = "dcb76c6586fc06cbdac6dd21f14cfd129cc4cdd9dce19bf4ffa62e59cbe6e6d1"
FILES = {
    "config.json": (16_000, 100),
    "tokenizer.json": (5_000_000, 100_000),
    "vocabulary.txt": (1_500_000, 100_000),
    "model.bin": (90_000_000, 70_000_000),
}


def confined(path: Path, *, existing: bool = False) -> None:
    base = ROOT.resolve(strict=True)
    if not path.resolve(strict=existing).is_relative_to(base):
        raise RuntimeError("FERRARI_WHISPER_PATH_ESCAPES_PROJECT")
    cur = path
    while cur != ROOT:
        if cur.is_symlink():
            raise RuntimeError("FERRARI_WHISPER_SYMLINK_REJECTED")
        cur = cur.parent


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(2 * 1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def preflight() -> None:
    if not ROOT.is_dir() or ROOT.is_symlink() or ROOT.stat().st_uid != os.getuid():
        raise RuntimeError("FERRARI_WHISPER_PROJECT_OWNER_MISMATCH")
    confined(VENV, existing=True)
    py = VENV / "bin/python"
    if not VENV.is_dir() or not py.is_file():
        raise RuntimeError("FERRARI_WHISPER_PRIVATE_VENV_MISSING")
    if not py.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("FERRARI_WHISPER_PYTHON_OUTSIDE_PROJECT")
    if shutil.disk_usage(ROOT).free < 3 * 1024**3:
        raise RuntimeError("FERRARI_WHISPER_DISK_GUARD_FAILED")
    confined(MODEL_DIR)
    print("FERRARI_WHISPER_PRIVATE_PREFLIGHT=PASS", flush=True)


def verify(directory: Path) -> bool:
    if not directory.is_dir() or directory.is_symlink():
        return False
    try:
        for name, (max_bytes, min_bytes) in FILES.items():
            path = directory / name
            confined(path, existing=True)
            if (not path.is_file() or path.is_symlink()
                    or not min_bytes < path.stat().st_size < max_bytes):
                return False
        if sha256(directory / "model.bin") != MODEL_SHA256:
            return False
        config = json.loads((directory / "config.json").read_text("utf-8"))
        tokenizer = json.loads((directory / "tokenizer.json").read_text("utf-8"))
        if not isinstance(config.get("lang_ids"), list) or len(config["lang_ids"]) < 50:
            return False
        if not isinstance(tokenizer.get("model"), dict):
            return False
        vocabulary = (directory / "vocabulary.txt").read_text("utf-8")
        if len(vocabulary) < 100_000:
            return False
        manifest = json.loads((directory / "FERRARI_PROVENANCE.json").read_text("utf-8"))
        if (manifest.get("repository") != REPO
                or manifest.get("revision") != REV
                or manifest.get("model_sha256") != MODEL_SHA256):
            return False
        for name in FILES:
            if manifest.get("all_file_sha256", {}).get(name) != sha256(directory / name):
                return False
        expected = set(FILES) | {"FERRARI_PROVENANCE.json"}
        found = {str(p.relative_to(directory)) for p in directory.rglob("*") if p.is_file()}
        if expected != found:
            return False
    except (OSError, ValueError, UnicodeError, RuntimeError):
        return False
    return True


def download(name: str, destination: Path) -> None:
    if name not in FILES:
        raise ValueError("Only pinned Whisper model files may be downloaded")
    maximum, minimum = FILES[name]
    confined(destination)
    request = urllib.request.Request(BASE_URL + name, headers={"User-Agent": "Ferrari-Whisper-Private/1.0"})
    written = 0
    print("FERRARI_WHISPER_DOWNLOAD_START=" + name, flush=True)
    with urllib.request.urlopen(request, timeout=100) as response, destination.open("xb") as out:
        for block in iter(lambda: response.read(2 * 1024 * 1024), b""):
            written += len(block)
            if written >= maximum:
                raise RuntimeError("FERRARI_WHISPER_FILE_TOO_LARGE")
            out.write(block)
    if written <= minimum:
        raise RuntimeError("FERRARI_WHISPER_FILE_TOO_SMALL")
    if name == "model.bin" and sha256(destination) != MODEL_SHA256:
        raise RuntimeError("FERRARI_WHISPER_MODEL_SHA256_MISMATCH")
    print("FERRARI_WHISPER_DOWNLOAD_VERIFIED=" + name + " bytes=" + str(written), flush=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--check", action="store_true")
    group.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    preflight()
    if args.check:
        if not verify(MODEL_DIR):
            raise RuntimeError("FERRARI_WHISPER_MODEL_ABSENT_OR_UNVERIFIED")
        print("FERRARI_WHISPER_MODEL=PASS_PRIVATE_SHA256", flush=True)
        return 0
    if verify(MODEL_DIR):
        print("FERRARI_WHISPER_MODEL=PASS_REUSE", flush=True)
        return 0
    if MODEL_DIR.exists() or MODEL_DIR.is_symlink():
        raise RuntimeError("FERRARI_WHISPER_EXISTING_MODEL_CONFLICT")
    parent = MODEL_DIR.parent
    confined(parent)
    parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    confined(parent, existing=True)
    stage = Path(tempfile.mkdtemp(prefix=".ferrari-whisper-staging-", dir=parent))
    confined(stage, existing=True)
    try:
        for name in FILES:
            download(name, stage / name)
        manifest = {
            "repository": REPO,
            "revision": REV,
            "license": "MIT",
            "model_sha256": MODEL_SHA256,
            "all_file_sha256": {name: sha256(stage / name) for name in FILES},
            "scope": "Ferrari-private CPU ASR, no global install or model cache",
        }
        (stage / "FERRARI_PROVENANCE.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
        if not verify(stage):
            raise RuntimeError("FERRARI_WHISPER_STAGING_INTEGRITY_FAILED")
        stage.rename(MODEL_DIR)
        print("FERRARI_WHISPER_MODEL=PASS_INSTALLED_PRIVATE", flush=True)
        print("FERRARI_WHISPER_GLOBAL_APT_PIP_CHANGES=ZERO", flush=True)
    finally:
        if stage.exists() and not stage.is_symlink():
            shutil.rmtree(stage)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError, ValueError, RuntimeError, UnicodeError, urllib.error.URLError) as exc:
        print("FERRARI_WHISPER_MODEL_BLOCKED=" + str(exc)[:600], file=sys.stderr)
        sys.exit(3)
