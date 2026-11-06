#!/usr/bin/env python3
"""Ferrari F9: isolate Ubuntu 24.04 GPL-3.0 SolveSpace package.

Downloads only the exact distro package through signed APT index metadata,
extracts into the Ferrari project, never uses apt install/sudo/global PATH
fallback. A private executable is not a full GUI-functional certification.
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

ROOT = Path("/srv/projects/skill-universal")
TOOLS = ROOT / "tools"
RUNTIME = ROOT / ".runtime"
PACKAGE = "solvespace"
VERSION = "3.1+ds1-3.1build2"
TARGET = TOOLS / "solvespace-3.1-ubuntu24"
EXECUTABLE = TARGET / "usr/bin/solvespace"
OS_PACKAGE = TARGET / "package.deb"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def guard() -> None:
    require(os.geteuid() != 0, "F9_SOLVESPACE_MUST_BE_UNPRIVILEGED")
    require(os.uname().machine == "x86_64", "F9_SOLVESPACE_ARCH_MISMATCH")
    release = Path("/etc/os-release").read_text(encoding="utf-8")
    require("ID=ubuntu" in release and 'VERSION_ID="24.04"' in release,
            "F9_SOLVESPACE_REQUIRES_UBUNTU_2404")
    require(ROOT.resolve(strict=True) == Path("/srv/projects/skill-universal"),
            "F9_SOLVESPACE_ROOT_MISMATCH")
    for directory in (ROOT, TOOLS, RUNTIME):
        require(directory.is_dir() and not directory.is_symlink(),
                "F9_SOLVESPACE_UNSAFE_DIRECTORY:" + str(directory))
    require(not TARGET.is_symlink(), "F9_SOLVESPACE_TARGET_SYMLINK")


def call(argv: list[str], *, cwd: Path | None = None, timeout: int = 50) -> subprocess.CompletedProcess:
    require(all(isinstance(x, str) for x in argv), "F9_SOLVESPACE_INVALID_ARGS")
    env = {"PATH": "/usr/bin:/bin", "LC_ALL": "C", "DEBIAN_FRONTEND": "noninteractive",
           "HOME": str(RUNTIME), "TMPDIR": str(RUNTIME)}
    result = subprocess.run(argv, cwd=cwd, env=env,
                            capture_output=True, text=True, timeout=timeout, check=False)
    require(result.returncode == 0,
            "F9_SOLVESPACE_COMMAND_FAILED:" + argv[0] + ":" + result.stderr[-200:])
    return result


def apt_metadata() -> dict:
    output = call(["/usr/bin/apt-cache", "show", PACKAGE]).stdout
    stanzas = output.strip().split("\n\n")
    for stanza in stanzas:
        fields = {}
        for line in stanza.splitlines():
            if ": " in line and not line.startswith((" ", "\t")):
                name, value = line.split(": ", 1)
                fields[name] = value
        if (fields.get("Package") == PACKAGE and fields.get("Version") == VERSION
                and fields.get("Architecture") == "amd64" and
                len(fields.get("SHA256", "")) == 64 and fields.get("Size", "").isdigit()):
            require(int(fields["Size"]) <= 40 * 1024 * 1024,
                    "F9_SOLVESPACE_ARCHIVE_SIZE_LIMIT")
            return {"sha256": fields["SHA256"], "bytes": int(fields["Size"]),
                    "source": fields.get("Filename", ""),
                    "version": VERSION, "package": PACKAGE}
    raise RuntimeError("F9_SOLVESPACE_SIGNED_APT_METADATA_MISSING")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check() -> dict:
    require(TARGET.is_dir() and not TARGET.is_symlink(),
            "F9_SOLVESPACE_PRIVATE_NOT_PRESENT")
    pkg = apt_metadata()
    require(OS_PACKAGE.is_file() and not OS_PACKAGE.is_symlink(),
            "F9_SOLVESPACE_DEB_MISSING")
    require(OS_PACKAGE.stat().st_size == pkg["bytes"] and sha256(OS_PACKAGE) == pkg["sha256"],
            "F9_SOLVESPACE_DEB_SHA_MISMATCH")
    require(EXECUTABLE.is_file() and not EXECUTABLE.is_symlink() and
            os.access(EXECUTABLE, os.X_OK) and
            EXECUTABLE.resolve(strict=True).is_relative_to(TARGET.resolve(strict=True)),
            "F9_SOLVESPACE_PRIVATE_EXE_INVALID")
    marker = TARGET / "manifest.json"
    require(marker.is_file() and not marker.is_symlink() and marker.stat().st_size < 4096,
            "F9_SOLVESPACE_MANIFEST_MISSING")
    doc = json.loads(marker.read_text(encoding="utf-8"))
    require(doc == {**pkg, "license": "GPL-3.0",
                    "verification": "signed_apt_metadata_sha256_and_private_elf",
                    "gui_runtime_certified": False,
                    "dependency_isolation_certified": False},
            "F9_SOLVESPACE_MANIFEST_MISMATCH")
    linker = call(["/usr/bin/ldd", str(EXECUTABLE)], timeout=25).stdout
    require("not found" not in linker and "libGL" in linker,
            "F9_SOLVESPACE_PRIVATE_LDD_MISSING_OR_UNEXPECTED")
    return {"status": "private_ubuntu_package_verified", "package": PACKAGE,
            "version": VERSION, "package_bytes": pkg["bytes"], "sha256": pkg["sha256"],
            "private_binary": str(EXECUTABLE), "ldd_resolved_on_host": True,
            "gui_runtime_certified": False, "dependency_isolation_certified": False,
            "global_apt_changed": False}


def install() -> dict:
    guard()
    if TARGET.exists():
        return check()
    metadata = apt_metadata()
    space = os.statvfs(RUNTIME)
    require(space.f_bavail * space.f_frsize > 3 * 1024 ** 3,
            "F9_SOLVESPACE_NOT_ENOUGH_DISK")
    with tempfile.TemporaryDirectory(prefix=".f9-solvespace-", dir=RUNTIME) as t:
        scratch = Path(t)
        stage = scratch / "stage"
        stage.mkdir(mode=0o700)
        call(["/usr/bin/apt-get", "download", PACKAGE + "=" + VERSION],
             cwd=stage, timeout=180)
        files = list(stage.glob("*.deb"))
        require(len(files) == 1 and files[0].is_file() and not files[0].is_symlink(),
                "F9_SOLVESPACE_UNEXPECTED_PACKAGE_FILES")
        downloaded = files[0]
        require(downloaded.stat().st_size == metadata["bytes"]
                and sha256(downloaded) == metadata["sha256"],
                "F9_SOLVESPACE_OFFICIAL_PACKAGE_SHA_MISMATCH")
        container = scratch / "package"
        container.mkdir(mode=0o700)
        call(["/usr/bin/dpkg-deb", "-x", str(downloaded), str(container)], timeout=100)
        bin_path = container / "usr/bin/solvespace"
        require(bin_path.is_file() and not bin_path.is_symlink() and
                os.access(bin_path, os.X_OK) and
                bin_path.resolve(strict=True).is_relative_to(container.resolve(strict=True)),
                "F9_SOLVESPACE_INVALID_EXTRACTED_BINARY")
        # Core GTK/OpenGL system libraries still need a runtime test with a display.
        call(["/usr/bin/ldd", str(bin_path)], timeout=25)
        downloaded.rename(container / "package.deb")
        doc = {**metadata, "license": "GPL-3.0",
               "verification": "signed_apt_metadata_sha256_and_private_elf",
               "gui_runtime_certified": False, "dependency_isolation_certified": False}
        (container / "manifest.json").write_text(json.dumps(doc, indent=2) + "\n")
        require(not TARGET.exists() and not TARGET.is_symlink(),
                "F9_SOLVESPACE_CONCURRENT_INSTALL")
        os.replace(container, TARGET)
    return check()


def main() -> int:
    parser = argparse.ArgumentParser()
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument("--install", action="store_true")
    modes.add_argument("--check", action="store_true")
    args = parser.parse_args()
    try:
        result = install() if args.install else (guard() or check())
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[-260:],
                          "global_apt_changed": False}, sort_keys=True), flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
