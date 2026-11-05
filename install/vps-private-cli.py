#!/usr/bin/env python3
"""Copy locally installed Ubuntu CLI tools and their libraries into Ferrari only.

Copies existing, already installed Ubuntu executables; never calls apt, sudo,
pip or npm. All writes are under /srv/projects/skill-universal/tools/ubuntu-cli.
"""
from __future__ import annotations

import argparse
import os
import sys
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
            "r2", "vips", "vipsheader", "tshark", "inkscape",
            "binwalk", "ansible-inventory", "ocrmypdf", "ebook-convert",
            "darktable-cli", "krita", "gimp-console-2.10", "scribus",
            "lmms", "melt", "Xvfb", "xvfb-run", "xauth")
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


def private_python() -> dict:
    """Copy Ubuntu 3.12 Python/stdlib and point only Ferrari's two venvs to it."""
    source=Path("/usr/bin/python3.12").resolve(strict=True)
    stdlib=Path("/usr/lib/python3.12")
    target=ROOT/"runtimes/python3.12"
    private=target/"bin/python3.12"
    if not stdlib.is_dir() or not ROOT.is_dir() or target.is_symlink():
        raise RuntimeError("Ubuntu Python 3.12 or private Ferrari project not available")
    copy_one(source,private)
    private_stdlib=target/"lib/python3.12"
    if not private_stdlib.exists():
        shutil.copytree(stdlib,private_stdlib,symlinks=False,
                        ignore=shutil.ignore_patterns("__pycache__","*.pyc","*.pyo"))
    check=subprocess.run(["ldd",str(source)],capture_output=True,text=True,timeout=15,check=False)
    if check.returncode or "not found" in check.stdout:
        raise RuntimeError("Unable to inspect Python runtime libraries")
    for match in LIB_PATTERN.finditer(check.stdout):
        lib=Path(match.group(1))
        copy_one(lib,target/"lib"/lib.name)
    changed=[]
    for name in ("duckdb","polars"):
        venv=ROOT/".runtime/venvs/extended"/name
        cfg=venv/"pyvenv.cfg"
        if not cfg.is_file() or not venv.is_dir() or venv.is_symlink():
            raise RuntimeError("Ferrari private Python environment missing: "+name)
        for executable in ("python","python3","python3.12"):
            link=venv/"bin"/executable
            if not link.is_symlink():
                if not link.is_file():
                    raise RuntimeError("Missing Ferrari Python venv executable: "+str(link))
                continue
            current=link.resolve(strict=True)
            if current==private.resolve(strict=True):
                continue
            if current!=source:
                raise RuntimeError("Unrecognized Python venv target: "+str(current))
            replacement=link.with_name(link.name+".ferrari-new")
            if replacement.exists() or replacement.is_symlink():
                raise RuntimeError("Python swap path already exists: "+str(replacement))
            replacement.symlink_to(private)
            os.replace(replacement,link)
            changed.append(str(link))
        old=cfg.read_text(encoding="utf-8")
        lines=[]
        for line in old.splitlines():
            if line.startswith("home = "):
                line="home = "+str(private.parent)
            elif line.startswith("executable = "):
                line="executable = "+str(private)
            lines.append(line)
        result="\n".join(lines)+"\n"
        if result!=old:
            cfg.write_text(result,encoding="utf-8")
        env=os.environ.copy()
        env.pop("PYTHONHOME",None)
        env["PYTHONNOUSERSITE"]="1"
        env["LD_LIBRARY_PATH"]=str(target/"lib")
        probe=subprocess.run([str(venv/"bin/python"),"-c",
           "import sys, "+name+"; assert sys.base_prefix.startswith('/srv/projects/skill-universal/runtimes/python3.12'); print(sys.base_prefix)"],
           capture_output=True,text=True,env=env,timeout=45)
        if probe.returncode:
            raise RuntimeError("Private Python "+name+" failed: "+probe.stderr[-500:])
    return {"runtime":str(target),"venvs":["duckdb","polars"],"links_updated":changed}


def install_private_python_modules() -> dict:
    """Copy selected Ubuntu-owned Python modules, never the global site-packages tree."""
    source=Path("/usr/lib/python3/dist-packages")
    dest=TARGET/"lib/python"
    if not source.is_dir() or dest.is_symlink():
        raise RuntimeError("Ubuntu Python packages or private destination unavailable")
    names=("binwalk","ansible","ocrmypdf","yaml","jinja2","markupsafe",
           "cryptography","packaging","resolvelib","pikepdf","PIL",
           "img2pdf","jp2","pluggy","magic","capstone","reportlab",
           "psutil","lxml","attr","attrs","click","rich","distro",
           "dateutil","six","defusedxml","tqdm","numpy","cffi",
           "_cffi_backend","idna","certifi","chardet","charset_normalizer","pypdf",
           "typing_extensions","sortedcontainers","ocrmypdf_plugins",
           "pdfminer","deprecation","deprecated","wrapt","olefile","pdf2image","colorama",
           "setuptools","pkg_resources","importlib_metadata","zipp",
           "shellingham","cryptography","pytesseract")
    copied=[]
    for name in dict.fromkeys(names):
        candidates=[source/name,source/(name+".py")]
        candidates.extend(source.glob(name+".cpython-312-*.so"))
        candidates.extend(source.glob(name+".abi3.so"))
        for item in candidates:
            if not item.exists() or item.is_symlink():
                continue
            target=dest/item.name
            if item.is_dir():
                if not target.exists():
                    size=sum(p.stat().st_size for p in item.rglob("*") if p.is_file() and not p.is_symlink())
                    if size>200_000_000:
                        raise RuntimeError("Refuse oversized global Python module: "+name)
                    shutil.copytree(item,target,symlinks=False,
                                    ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
                copied.append(item.name)
            elif item.is_file():
                copy_one(item,target)
                copied.append(item.name)
        names_to_match={name.casefold().replace("_","-")}
        aliases={"yaml":"pyyaml","PIL":"pillow","ansible":"ansible-core"}
        if name in aliases:
            names_to_match.add(aliases[name])
        for info in source.iterdir():
            if info.is_symlink() or not info.name.endswith((".dist-info",".egg-info")):
                continue
            normalized=info.name.casefold().replace("_","-")
            if not any(normalized.startswith(n+"-") for n in names_to_match):
                continue
            target=dest/info.name
            if info.is_dir() and not target.exists():
                shutil.copytree(info,target,symlinks=False)
            elif info.is_file() and not target.exists():
                copy_one(info,target)
    for required in ("binwalk","ansible","ocrmypdf"):
        if not (dest/required).is_dir():
            raise RuntimeError("Missing installed Ubuntu Python module "+required)
    return {"private_python_modules_root":str(dest),
            "module_count":len(copied),"modules":sorted(copied)}


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
        "ebook-convert": (("/usr/lib/calibre", "lib/calibre"),
                           ("/usr/share/calibre", "share/calibre")),
        "binwalk": (("/usr/share/binwalk", "share/binwalk"),),
        "darktable-cli": (("/usr/share/darktable", "share/darktable"),
                             ("/usr/lib/x86_64-linux-gnu/darktable", "lib/darktable")),
        "krita": (("/usr/share/krita", "share/krita"),),
        "gimp-console-2.10": (("/usr/share/gimp", "share/gimp"),
                              ("/usr/lib/gimp/2.0", "lib/gimp/2.0")),
        "scribus": (("/usr/share/scribus", "share/scribus"),),
        "lmms": (("/usr/share/lmms", "share/lmms"),
                 ("/usr/lib/x86_64-linux-gnu/lmms", "lib/lmms")),
        "melt": (("/usr/share/mlt-7", "share/mlt-7"),
                 ("/usr/lib/x86_64-linux-gnu/mlt-7", "lib/mlt-7")),
        "Xvfb": (("/usr/lib/x86_64-linux-gnu/qt5/plugins", "lib/qt5/plugins"),),

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
    # GUI and MLT load native plugin libraries at runtime. Include the plugin
    # dependencies inside Ferrari rather than borrowing another project copy.
    optional_plugin_deps=set()
    modules=(TARGET/"lib/mlt-7", TARGET/"lib/lmms", TARGET/"lib/gimp/2.0",
             TARGET/"lib/darktable", TARGET/"lib/qt5/plugins")
    for folder in modules:
        if not folder.is_dir() or folder.is_symlink():
            continue
        for plugin in folder.rglob("*.so"):
            if plugin.is_symlink() or not plugin.is_file():
                continue
            probe=subprocess.run(["ldd",str(plugin)],capture_output=True,
                                 text=True,timeout=15,check=False)
            if "not found" in probe.stdout+probe.stderr:
                raise RuntimeError("Incomplete Ferrari plugin libraries: "+plugin.name)
            for match in LIB_PATTERN.finditer(probe.stdout+probe.stderr):
                dep=Path(match.group(1))
                if not dep.is_file():
                    roots=(TARGET/"lib/lmms", TARGET/"lib/darktable", TARGET/"lib/mlt-7",
                           TARGET/"lib/gimp/2.0", TARGET/"lib/qt5/plugins",
                           Path("/usr/lib/x86_64-linux-gnu/lmms"),
                           Path("/usr/lib/x86_64-linux-gnu/darktable"),
                           Path("/usr/lib/x86_64-linux-gnu/mlt-7"),
                           Path("/usr/lib/lmms"),Path("/usr/lib/darktable"),
                           Path("/usr/lib/mlt-7"))
                    alternatives=tuple(folder/dep.name for folder in roots)
                    dep=next((candidate for candidate in alternatives if candidate.is_file()),dep)
                if not dep.is_file():
                    # Optional plugins may reference libraries absent on a headless host.
                    # Do not certify them; real actions still have to pass below.
                    optional_plugin_deps.add(dep.name)
                    continue
                if dep.is_relative_to(TARGET):
                    continue
                copy_one(dep,library_dir/dep.name)
    python_result=private_python()
    python_packages=install_private_python_modules()
    return {"root": str(TARGET), "binaries": sorted(installed),
            "private_libraries": len(all_libs), "private_resources": assets,
            "python": python_result,
            "python_packages": python_packages,
            "optional_plugin_dependencies_unresolved": sorted(optional_plugin_deps),
            "magic_database": str(TARGET / "share/magic.mgc"),
            "system_installation": False, "other_projects_touched": False}


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true")
    p.add_argument("--python-only", action="store_true")
    args = p.parse_args()
    if args.python_only:
        if not ROOT.is_dir() or ROOT.is_symlink() or TARGET.is_symlink() or not TARGET.is_dir():
            raise RuntimeError("Ferrari private project must exist")
        result=install_private_python_modules()
        print("FERRARI_PRIVATE_PYTHON_MODULES=PASS")
        print(json.dumps(result,sort_keys=True))
        return
    if not args.apply:
        print(json.dumps({"mode": "preview", "target": str(TARGET), "binaries": BINARIES}))
        return
    result = install()
    print("FERRARI_PRIVATE_CLI_COPY=PASS")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
