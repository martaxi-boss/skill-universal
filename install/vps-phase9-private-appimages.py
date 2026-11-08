#!/usr/bin/env python3
"""F9: install pinned official GUI AppImages into Ferrari only, without APT or sudo.

Successful install certifies original SHA256 and mountless AppImage extraction.
It does NOT certify GUI operation without a display; record that separately.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
TOOLS = ROOT / "tools"
RUNTIME = ROOT / ".runtime"
ASSETS = {
    "librecad": {
        "version": "2.2.1.6", "repo": "LibreCAD/LibreCAD", "tag": "v2.2.1.6",
        "filename": "LibreCAD-v2.2.1.6-x86_64.AppImage", "size": 82846008,
        "sha256": "f2d86e6a40ec684b758c821eff3496a7d36e69f17519cde0b508a66d72c5754c",
    },
    "audacity": {
        "version": "4.0.2", "repo": "audacity/audacity", "tag": "Audacity-4.0.2",
        "filename": "audacity-linux-4.0.2-x86_64.AppImage", "size": 73726456,
        "sha256": "a5f8787aa13cdb500a60fc013403b986776876b960cca962bc6e7fff066172f3",
    },
    "synfig": {
        "version": "1.5.5", "repo": "synfig/synfig", "tag": "v1.5.5",
        "filename": "SynfigStudio-1.5.5-2026.03.15-linux64-79bf7.appimage",
        "size": 115539968,
        "sha256": "b85aabc26f690a0c150d2143c656c17f358b73abbedf8d01007f15a7a95740e9",
    },
    "openshot": {
        "version": "4.1.1", "repo": "OpenShot/openshot-qt", "tag": "v4.1.1",
        "filename": "OpenShot-v4.1.1-x86_64.AppImage", "size": 258921664,
        "sha256": "662d0c3cec67ddc90df6a8b0c723c0aac0d3bddf0c3c467eff562e818bb8c72f",
    },
}

def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)

def guard() -> None:
    require(os.geteuid() != 0, "F9_GUI_ROOT_NOT_ALLOWED")
    require(os.uname().machine == "x86_64", "F9_GUI_X86_64_ONLY")
    release = Path("/etc/os-release").read_text(encoding="utf-8")
    require("ID=ubuntu" in release and 'VERSION_ID="24.04"' in release,
            "F9_GUI_OS_NOT_SUPPORTED")
    require(ROOT.resolve() == Path("/srv/projects/skill-universal"), "F9_GUI_PROJECT_ROOT")
    for path in (ROOT, TOOLS, RUNTIME):
        require(path.is_dir() and not path.is_symlink(), "F9_GUI_UNSAFE_ROOT:" + str(path))

def directory(key: str) -> Path:
    return TOOLS / (key + "-" + ASSETS[key]["version"])

def url(key: str) -> str:
    a = ASSETS[key]
    return ("https://github.com/" + a["repo"] + "/releases/download/" +
            a["tag"] + "/" + a["filename"])

def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def check(key: str) -> dict:
    a = ASSETS[key]
    home = directory(key)
    require(home.is_dir() and not home.is_symlink(), "F9_GUI_NOT_INSTALLED:" + key)
    archive = home / a["filename"]
    require(archive.is_file() and not archive.is_symlink(), "F9_GUI_ARCHIVE_MISSING:" + key)
    require(archive.stat().st_size == a["size"] and hash_file(archive) == a["sha256"],
            "F9_GUI_ARCHIVE_DIGEST_MISMATCH:" + key)
    run = (archive if key == "synfig" else home / "squashfs-root" / "AppRun")
    require(run.is_file() and os.access(run, os.X_OK), "F9_GUI_EXECUTOR_NOT_EXECUTABLE:" + key)
    require(run.resolve(strict=True).is_relative_to(home.resolve(strict=True)),
            "F9_GUI_EXECUTOR_ESCAPED:" + key)
    manifest = home / "manifest.json"
    require(manifest.is_file() and not manifest.is_symlink() and manifest.stat().st_size < 4096,
            "F9_GUI_MANIFEST_MISSING:" + key)
    doc = json.loads(manifest.read_text(encoding="utf-8"))
    require(doc == {"key": key, "version": a["version"], "url": url(key),
                    "sha256": a["sha256"], "bytes": a["size"],
                    "certification": ("download_sha256_only_type1" if key == "synfig"
                                      else "download_sha256_and_appimage_extraction_only"),
                    "gui_runtime_certified": False},
            "F9_GUI_MANIFEST_MISMATCH:" + key)
    return {"status": "private_appimage_verified", "tool": key,
            "appimage_bytes": a["size"], "appimage_sha256": a["sha256"],
            "private_path": str(run), "gui_runtime_certified": False,
            "extraction_verified": key != "synfig", "global_apt_changed": False}

def fetch(key: str, to: Path) -> None:
    a = ASSETS[key]
    request = urllib.request.Request(url(key), headers={"User-Agent": "Ferrari-F9-pinned-appimage"})
    size, digest = 0, hashlib.sha256()
    with urllib.request.urlopen(request, timeout=180) as stream, to.open("xb") as dst:
        while chunk := stream.read(1024 * 1024):
            size += len(chunk)
            require(size <= a["size"], "F9_GUI_ARCHIVE_OVERSIZED:" + key)
            digest.update(chunk)
            dst.write(chunk)
    require(size == a["size"] and digest.hexdigest() == a["sha256"],
            "F9_GUI_DOWNLOAD_HASH_MISMATCH:" + key)
    to.chmod(0o700)

def install(key: str) -> dict:
    guard()
    target = directory(key)
    require(not target.is_symlink(), "F9_GUI_TARGET_IS_LINK:" + key)
    if target.exists():
        return check(key)
    a = ASSETS[key]
    free = os.statvfs(RUNTIME)
    require(free.f_bavail * free.f_frsize >= max(3 * 1024 ** 3, a["size"] * 6),
            "F9_GUI_INSUFFICIENT_PRIVATE_DISK")
    with tempfile.TemporaryDirectory(prefix=".f9-gui-" + key + "-", dir=RUNTIME) as td:
        staging = Path(td)
        pkg = staging / "package"
        pkg.mkdir(mode=0o700)
        archive = pkg / a["filename"]
        fetch(key, archive)
        # Synfig's official Type-1 AppImage does not support --appimage-extract:
        # that option launches the GTK app, which fails on a headless VPS.
        # Keep the original verified executable without claiming GUI certification.
        if key == "synfig":
            with archive.open("rb") as stream:
                header = stream.read(4)
            require(header == b"\x7fELF",
                    "F9_GUI_TYPE1_NOT_ELF:" + key)
        else:
            # Extract on the project's private filesystem, no host FUSE mount.
            env = os.environ.copy()
            env.update({"HOME": str(staging), "TMPDIR": str(staging),
                        "XDG_CACHE_HOME": str(staging), "QT_QPA_PLATFORM": "offscreen"})
            try:
                result = subprocess.run([str(archive), "--appimage-extract"], cwd=pkg,
                                        env=env, capture_output=True, text=True, timeout=240,
                                        check=False)
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("F9_GUI_APPIMAGE_EXTRACT_TIMEOUT:" + key) from exc
            require(result.returncode == 0, "F9_GUI_APPIMAGE_EXTRACT_FAILED:" + key +
                    ":" + (result.stderr or result.stdout)[-200:])
            apprun = pkg / "squashfs-root" / "AppRun"
            require(apprun.is_file() and os.access(apprun, os.X_OK),
                    "F9_GUI_EXTRACTED_APPRUN_MISSING:" + key)
            require(apprun.resolve(strict=True).is_relative_to(pkg.resolve(strict=True)),
                    "F9_GUI_EXTRACTED_APPRUN_ESCAPED:" + key)
        data = {"key": key, "version": a["version"], "url": url(key),
                "sha256": a["sha256"], "bytes": a["size"],
                "certification": ("download_sha256_only_type1" if key == "synfig"
                                  else "download_sha256_and_appimage_extraction_only"),
                "gui_runtime_certified": False}
        (pkg / "manifest.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        require(not target.exists() and not target.is_symlink(), "F9_GUI_CONCURRENT_TARGET:" + key)
        os.replace(pkg, target)
    return check(key)

def main() -> int:
    p = argparse.ArgumentParser()
    m = p.add_mutually_exclusive_group(required=True)
    m.add_argument("--install", choices=sorted(ASSETS))
    m.add_argument("--check", choices=sorted(ASSETS))
    args = p.parse_args()
    key = args.install or args.check
    try:
        if args.install:
            data = install(key)
        else:
            guard()
            data = check(key)
        print(json.dumps(data, sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "blocked", "tool": key,
                          "reason": str(exc)[-280:], "global_apt_changed": False},
                         sort_keys=True), flush=True)
        return 3

if __name__ == "__main__":
    sys.exit(main())
