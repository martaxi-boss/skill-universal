#!/usr/bin/env python3
"""Pin and unpack the official OBS Studio Ubuntu 24.04 .deb in Ferrari only.

The CLI smoke and dependency isolation are reported, never assumed. This does
not enable OBS as a service or alter the Ubuntu package database.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
RUNTIME = ROOT / ".runtime"
TOOLS = ROOT / "tools"
VERSION = "32.2.2"
FILENAME = "OBS-Studio-32.2.2-Ubuntu-24.04-x86_64.deb"
URL = ("https://github.com/obsproject/obs-studio/releases/download/"
       + VERSION + "/" + FILENAME)
SHA256 = "b6557ca2059287210332accc94c267094050489cffffc5c832e746e3a418dab0"
SIZE = 134324516
TARGET = TOOLS / ("obs-studio-" + VERSION)

def require(value: bool, label: str) -> None:
    if not value:
        raise RuntimeError(label)

def guard() -> None:
    require(os.geteuid() != 0, "F9_OBS_ROOT_NOT_ALLOWED")
    require(os.uname().machine == "x86_64", "F9_OBS_X86_ONLY")
    release = Path("/etc/os-release").read_text()
    require("ID=ubuntu" in release and 'VERSION_ID="24.04"' in release,
            "F9_OBS_INCOMPATIBLE_UBUNTU")
    require(ROOT.resolve(strict=True) == Path("/srv/projects/skill-universal"),
            "F9_OBS_UNEXPECTED_PROJECT")
    for path in (ROOT, RUNTIME, TOOLS):
        require(path.is_dir() and not path.is_symlink(),
                "F9_OBS_PROJECT_DIRECTORY_UNSAFE:" + str(path))
    require(not TARGET.is_symlink(), "F9_OBS_TARGET_SYMLINK")

def digest(path: Path) -> str:
    out = hashlib.sha256()
    with path.open("rb") as inp:
        for block in iter(lambda: inp.read(1024 * 1024), b""):
            out.update(block)
    return out.hexdigest()

def retrieve(dst: Path) -> None:
    digest_acc = hashlib.sha256()
    total = 0
    req = urllib.request.Request(URL, headers={"User-Agent": "Ferrari-F9-OBS-private"})
    with urllib.request.urlopen(req, timeout=180) as src, dst.open("xb") as out:
        while block := src.read(1024 * 1024):
            total += len(block)
            require(total <= SIZE, "F9_OBS_OVERSIZED")
            digest_acc.update(block)
            out.write(block)
    require(total == SIZE and digest_acc.hexdigest() == SHA256,
            "F9_OBS_DOWNLOAD_SHA_MISMATCH")

def obs_binary(payload: Path) -> str:
    expected = (payload / "usr/bin/obs", payload / "opt/obs-studio/bin/obs",
                payload / "usr/local/bin/obs")
    candidates = list(expected)
    # The exact layout of the .deb is upstream-owned: inspect without PATH lookup.
    candidates.extend(payload.rglob("obs"))
    for item in candidates:
        if item.is_file() and os.access(item, os.X_OK):
            resolved = item.resolve(strict=True)
            if resolved.is_relative_to(payload.resolve(strict=True)):
                return str(item.relative_to(payload))
    raise RuntimeError("F9_OBS_NO_PRIVATE_EXECUTABLE")

def launcher_source() -> str:
    # Only paths verified within this exact release's payload are accepted.
    return '''#!/usr/bin/env python3
import json, os, pathlib, sys
root = pathlib.Path(__file__).resolve().parent
data = json.loads((root / "manifest.json").read_text())
payload = root / "payload"
exe = (payload / data["obs_relative_exe"]).resolve(strict=True)
if not exe.is_file() or not exe.is_relative_to(payload.resolve(strict=True)):
    raise SystemExit("F9_OBS_EXECUTABLE_ESCAPED")
env = os.environ.copy()
dirs = ("opt/obs-studio/lib", "opt/obs-studio/lib64", "usr/lib",
        "usr/lib/x86_64-linux-gnu", "usr/local/lib")
local = [str(payload / p) for p in dirs if (payload / p).is_dir()]
if local:
    env["LD_LIBRARY_PATH"] = ":".join(local)
# Do not start a remote display, service, websocket or stream implicitly.
os.execve(str(exe), [str(exe)] + sys.argv[1:], env)
'''

def check() -> dict:
    require(TARGET.is_dir() and not TARGET.is_symlink(), "F9_OBS_NOT_INSTALLED")
    package = TARGET / FILENAME
    require(package.is_file() and not package.is_symlink()
            and package.stat().st_size == SIZE and digest(package) == SHA256,
            "F9_OBS_PACKAGE_DIGEST_MISMATCH")
    marker = TARGET / "manifest.json"
    require(marker.is_file() and not marker.is_symlink() and marker.stat().st_size < 4096,
            "F9_OBS_NO_MANIFEST")
    info = json.loads(marker.read_text(encoding="utf-8"))
    require(info.get("source") == URL and info.get("sha256") == SHA256
            and info.get("version") == VERSION and info.get("bytes") == SIZE,
            "F9_OBS_PROVENANCE_MISMATCH")
    exe = TARGET / "payload" / info["obs_relative_exe"]
    require(exe.is_file() and os.access(exe, os.X_OK) and
            exe.resolve(strict=True).is_relative_to((TARGET / "payload").resolve(strict=True)),
            "F9_OBS_INVALID_BINARY")
    launcher = TARGET / "run-obs"
    require(launcher.is_file() and not launcher.is_symlink()
            and launcher.read_text(encoding="utf-8") == launcher_source()
            and os.access(launcher, os.X_OK), "F9_OBS_INVALID_LAUNCHER")
    return {"status": "private_obs_package_verified", "package_sha256": SHA256,
            "version": VERSION, "private_path": str(launcher),
            "cli_version_tested": bool(info.get("cli_version_tested", False)),
            "gui_runtime_certified": False,
            "websocket_studio_certified": False,
            "dependency_isolation_certified": False,
            "global_apt_changed": False}

def install() -> dict:
    guard()
    if TARGET.exists():
        return check()
    stat = os.statvfs(RUNTIME)
    require(stat.f_bavail * stat.f_frsize > 3 * 1024 ** 3, "F9_OBS_INSUFFICIENT_SPACE")
    with tempfile.TemporaryDirectory(prefix=".f9-obs-", dir=RUNTIME) as td:
        scratch = Path(td)
        package_dir = scratch / "package"
        package_dir.mkdir(mode=0o700)
        src = package_dir / FILENAME
        retrieve(src)
        payload = package_dir / "payload"
        payload.mkdir(mode=0o700)
        result = subprocess.run(["dpkg-deb", "-x", str(src), str(payload)],
                                env={"PATH": "/usr/bin:/bin", "HOME": str(scratch)},
                                timeout=180, capture_output=True, text=True, check=False)
        require(result.returncode == 0, "F9_OBS_DEB_EXTRACT_FAILED:" + result.stderr[-200:])
        # Refuse an archive without an independent project-private executable.
        relative = obs_binary(payload)
        version_check = subprocess.run(["dpkg-deb", "-f", str(src)],
                                       env={"PATH": "/usr/bin:/bin"}, timeout=20,
                                       capture_output=True, text=True, check=False)
        fields = dict(line.split(": ", 1) for line in version_check.stdout.splitlines()
                      if ": " in line and not line.startswith(" "))
        require(version_check.returncode == 0
                and fields.get("Package") == "obs-studio"
                and VERSION in fields.get("Version", "")
                and fields.get("Architecture") == "amd64",
                "F9_OBS_DEB_METADATA_MISMATCH:" + version_check.stdout[-150:])
        data = {"source": URL, "sha256": SHA256, "version": VERSION,
                "bytes": SIZE, "obs_relative_exe": relative,
                "cli_version_tested": False, "dependency_isolation_certified": False}
        (package_dir / "manifest.json").write_text(json.dumps(data, indent=2) + "\n")
        launcher = package_dir / "run-obs"
        launcher.write_text(launcher_source(), encoding="utf-8")
        launcher.chmod(0o700)
        # Version-only test, no camera, video capture or websocket claim.
        env = os.environ.copy()
        env.update({"HOME": str(scratch), "XDG_CACHE_HOME": str(scratch),
                    "XDG_CONFIG_HOME": str(scratch), "QT_QPA_PLATFORM": "offscreen",
                    "TMPDIR": str(scratch), "PYTHONNOUSERSITE": "1"})
        try:
            cli = subprocess.run([str(launcher), "--version"], cwd=scratch, env=env,
                                 timeout=25, capture_output=True, text=True, check=False)
            data["cli_version_tested"] = cli.returncode == 0 and VERSION in (
                cli.stdout + cli.stderr)
        except (subprocess.TimeoutExpired, OSError):
            pass
        (package_dir / "manifest.json").write_text(json.dumps(data, indent=2) + "\n")
        require(not TARGET.exists() and not TARGET.is_symlink(), "F9_OBS_CONCURRENT_INSTALL")
        os.replace(package_dir, TARGET)
    return check()

def main() -> int:
    p = argparse.ArgumentParser()
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--install", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = p.parse_args()
    try:
        if args.install:
            result = install()
        else:
            guard()
            result = check()
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[-300:],
                          "global_apt_changed": False}), flush=True)
        return 3

if __name__ == "__main__":
    sys.exit(main())
