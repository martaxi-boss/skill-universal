#!/usr/bin/env python3
"""Copy locally installed Ubuntu CLI tools and their libraries into Ferrari only.

Copies existing, already installed Ubuntu executables; never calls apt, sudo,
pip or npm. All writes are under /srv/projects/skill-universal/tools/ubuntu-cli.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path("/srv/projects/skill-universal")
TARGET = ROOT / "tools/ubuntu-cli"
BINARIES = ("file", "jq", "rg", "readelf", "objdump", "strings",
            "ffmpeg", "ffprobe", "pdfinfo", "pdftotext",
            "pandoc", "dot", "identify", "convert", "tesseract",
            "r2", "vips", "vipsheader", "tshark", "inkscape")
LIB_PATTERN = re.compile(r"(?:=>\s*)?(/(?:usr/)?lib\S*)\s*\(")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def copy_one(source: Path, target: Path) -> None:
    if not source.is_file():
        raise RuntimeError("Missing Ubuntu package component: " + str(source))
    if not source.resolve(strict=True).is_relative_to(Path("/usr")):
        if not source.resolve(strict=True).is_relative_to(Path("/lib")):
            raise RuntimeError("Source is not from the Ubuntu OS")
    if target.exists() or target.is_symlink():
        if target.is_symlink() or sha(target) != sha(source):
            raise RuntimeError("Existing Ferrari component differs: " + str(target))
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def install() -> dict:
    if not ROOT.is_dir() or ROOT.is_symlink():
        raise RuntimeError("Ferrari project folder missing or linked")
    if TARGET.is_symlink():
        raise RuntimeError("Ferrari tools directory cannot be a symlink")
    binary_dir = TARGET / "bin"
    library_dir = TARGET / "lib"
    all_libs = {}
    installed = {}
    for name in BINARIES:
        command = shutil.which(name)
        if not command:
            raise RuntimeError("Ubuntu binary not available: " + name)
        source = Path(command).resolve(strict=True)
        if not (source.is_relative_to(Path("/usr")) or source.is_relative_to(Path("/lib"))):
            raise RuntimeError("Refusing executable outside Ubuntu: " + str(source))
        probe = subprocess.run(["ldd", str(source)], capture_output=True, text=True, timeout=15)
        result = probe.stdout + probe.stderr
        if probe.returncode and "not a dynamic executable" not in result and "statically linked" not in result:
            raise RuntimeError("Cannot inspect dependencies for " + name + ": " + result[:160])
        if "not found" in result:
            raise RuntimeError("Ubuntu binary has missing libraries: " + name)
        for match in LIB_PATTERN.finditer(result):
            lib = Path(match.group(1))
            all_libs[lib.name] = lib
        installed[name] = source
    for name, source in sorted(all_libs.items()):
        copy_one(source, library_dir / name)
    for name, source in installed.items():
        copy_one(source, binary_dir / name)
    magic = next((p for p in (Path("/usr/share/misc/magic.mgc"),
                              Path("/usr/share/file/magic.mgc")) if p.is_file()), None)
    if magic is None:
        raise RuntimeError("Ubuntu libmagic database missing")
    copy_one(magic, TARGET / "share/magic.mgc")
    # Copy application data and plugins that native tools need after migration.
    # Never change, delete or install anything outside the Ferrari directory.
    private_resources = {
        "tesseract": (("/usr/share/tesseract-ocr", "share/tesseract-ocr"),),
        "dot": (("/usr/lib/x86_64-linux-gnu/graphviz", "lib/graphviz"),),
        "identify": (("/etc/ImageMagick-6", "etc/ImageMagick-6"),),
        "vips": (("/usr/lib/vips-modules-8.15", "lib/vips-modules-8.15"),),
        "r2": (("/usr/share/radare2", "share/radare2"),),
        "inkscape": (("/usr/share/inkscape", "share/inkscape"),),
        "tshark": (("/usr/lib/x86_64-linux-gnu/wireshark", "lib/wireshark"),),
    }
    assets = {}
    for tool,entries in private_resources.items():
        if tool not in installed:
            continue
        for source_name, target_name in entries:
            source=Path(source_name)
            if not source.is_dir() or source.is_symlink():
                continue
            target=TARGET/target_name
            if target.is_symlink():
                raise RuntimeError("Ferrari resource location cannot be symlink: "+str(target))
            if not target.exists():
                shutil.copytree(source,target,symlinks=False)
            assets[target_name]=str(target)
    if "identify" in installed:
        codecs=list(Path("/usr/lib/x86_64-linux-gnu").glob("ImageMagick-*/modules-*/coders/png.so"))
        if len(codecs)!=1:
            raise RuntimeError("ImageMagick PNG plugin not unique on Ubuntu")
        root=codecs[0].parent.parent
        private=TARGET/"lib/ImageMagick"
        if not private.exists():
            shutil.copytree(root,private)
        assets["lib/ImageMagick"]=str(private)
    return {"root": str(TARGET), "binaries": sorted(installed),
            "private_libraries": len(all_libs), "private_resources": assets,
            "magic_database": str(TARGET / "share/magic.mgc"),
            "system_installation": False, "other_projects_touched": False}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    if not args.apply:
        print(json.dumps({"mode": "preview", "target": str(TARGET), "binaries": BINARIES}))
        return
    result = install()
    print("FERRARI_PRIVATE_CLI_COPY=PASS")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
