#!/usr/bin/env python3
"""Install or inspect a pinned, Ferrari-private yt-dlp Linux executable.

Never uses apt, sudo, pip or the system PATH for yt-dlp; never changes any
project other than /srv/projects/skill-universal. This is an F9 preparation,
not permission to purge the global Ubuntu package.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
RUNTIME = ROOT / ".runtime"
TOOLS = ROOT / "tools"
VERSION = "2026.10.26"
URL = f"https://github.com/yt-dlp/yt-dlp/releases/download/{VERSION}/yt-dlp_linux"
SIZE = 41166968
SHA256 = "767ba9dce7052aa196f8b12652f433d76de128ba168966fa84b6394d5e6c6795"
TARGET = TOOLS / f"yt-dlp-{VERSION}" / "yt-dlp"


def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)


def root_guard() -> None:
    require(os.geteuid() != 0, "F9_YTDLP_MUST_RUN_AS_PROJECT_USER")
    require(os.uname().machine == "x86_64", "F9_YTDLP_UNSUPPORTED_CPU")
    os_release = Path("/etc/os-release").read_text(encoding="utf-8")
    require('ID=ubuntu' in os_release and 'VERSION_ID="24.04"' in os_release,
            "F9_YTDLP_UNSUPPORTED_OS")
    for directory in (ROOT, RUNTIME, TOOLS):
        require(directory.is_dir() and not directory.is_symlink(),
                "F9_YTDLP_PRIVATE_DIRECTORY_MISSING_OR_LINKED:" + str(directory))
    require(ROOT.resolve(strict=True) == Path("/srv/projects/skill-universal"),
            "F9_YTDLP_PROJECT_ROOT_MISMATCH")
    if TARGET.parent.exists() or TARGET.parent.is_symlink():
        require(TARGET.parent.is_dir() and not TARGET.parent.is_symlink(),
                "F9_YTDLP_TARGET_DIRECTORY_UNSAFE")


def file_hash(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as fh:
        for piece in iter(lambda: fh.read(1024 * 1024), b""):
            result.update(piece)
    return result.hexdigest()


def verify_file(path: Path) -> None:
    require(path.is_file() and not path.is_symlink(),
            "F9_YTDLP_EXECUTABLE_MISSING_OR_LINKED")
    require(path.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)),
            "F9_YTDLP_BINARY_OUTSIDE_FERRARI")
    require(path.stat().st_size == SIZE and file_hash(path) == SHA256,
            "F9_YTDLP_BINARY_DIGEST_MISMATCH")


def smoke(path: Path, scratch: Path) -> dict:
    env = os.environ.copy()
    for name in ("HOME", "XDG_CONFIG_HOME", "XDG_CACHE_HOME", "TMPDIR", "TMP", "TEMP"):
        env[name] = str(scratch)
    env["PYTHONNOUSERSITE"] = "1"
    version = subprocess.run([str(path), "--ignore-config", "--version"],
                             env=env, capture_output=True, text=True, timeout=50,
                             check=False)
    require(version.returncode == 0 and version.stdout.strip() == VERSION,
            "F9_YTDLP_VERSION_SMOKE_FAILED")
    extractors = subprocess.run([str(path), "--ignore-config", "--list-extractors"],
                                env=env, capture_output=True, text=True, timeout=90,
                                check=False)
    names = [x.strip().lower() for x in extractors.stdout.splitlines()]
    require(extractors.returncode == 0 and len(names) >= 500
            and "generic" in names, "F9_YTDLP_EXTRACTOR_SMOKE_FAILED")
    return {"version": VERSION, "extractors_discovered": len(names),
            "type": "cli_and_extractor_inventory", "real_media_download_tested": False}


def retrieve(destination: Path) -> None:
    request = urllib.request.Request(URL, headers={"User-Agent": "Ferrari-F9-private-installer"})
    with urllib.request.urlopen(request, timeout=90) as stream, destination.open("xb") as out:
        digest = hashlib.sha256()
        total = 0
        while True:
            chunk = stream.read(1024 * 1024)
            if not chunk:
                break
            total += len(chunk)
            require(total <= SIZE, "F9_YTDLP_DOWNLOAD_OVERSIZED")
            out.write(chunk)
            digest.update(chunk)
    require(total == SIZE and digest.hexdigest() == SHA256,
            "F9_YTDLP_DOWNLOAD_DIGEST_MISMATCH")
    destination.chmod(0o755)


def run(install: bool) -> dict:
    root_guard()
    if TARGET.exists() or TARGET.is_symlink():
        verify_file(TARGET)
        with tempfile.TemporaryDirectory(prefix=".f9-ytdlp-check-", dir=RUNTIME) as tmp:
            result = smoke(TARGET, Path(tmp))
        return {"status": "private_existing_verified", "installed_new": False,
                "path": str(TARGET), "sha256": SHA256, **result}
    if not install:
        return {"status": "private_missing", "installed_new": False,
                "path": str(TARGET)}
    with tempfile.TemporaryDirectory(prefix=".f9-ytdlp-stage-", dir=RUNTIME) as tmp:
        stage = Path(tmp)
        candidate = stage / "yt-dlp"
        retrieve(candidate)
        verify_file(candidate)
        result = smoke(candidate, stage)
        require(not TARGET.parent.exists() and not TARGET.parent.is_symlink(),
                "F9_YTDLP_TARGET_CHANGED")
        TARGET.parent.mkdir(mode=0o700)
        try:
            os.replace(candidate, TARGET)
        except BaseException:
            TARGET.parent.rmdir()
            raise
    return {"status": "private_installed_verified", "installed_new": True,
            "path": str(TARGET), "sha256": SHA256, **result}


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--check", action="store_true",
                       help="Inspect an existing Ferrari-private binary only")
    modes.add_argument("--install", action="store_true",
                       help="Download a pinned release into Ferrari only")
    args = parser.parse_args()
    try:
        print(json.dumps(run(install=args.install), sort_keys=True), flush=True)
        return 0 if args.install or TARGET.exists() else 2
    except Exception as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[:180],
                          "global_apt_changed": False}, sort_keys=True), flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
