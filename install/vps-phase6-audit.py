#!/usr/bin/env python3
"""Read-only physical isolation audit for the *existing* Ferrari VPS release.

Runs under an existing Ferrari-private Python through the existing GitHub SSH
transport. It does not install, remove, chmod, restart, inspect credentials,
scan other projects' files, or modify /srv/projects/skill-universal/current.
All reported names are allowlisted executable/dependency names, not command
lines, service arguments, user data or secret values.
"""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys

HOME = Path("/srv/projects/skill-universal")
ACTIVE = sys.argv[1] if len(sys.argv) > 1 else "40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
FALLBACK = sys.argv[2] if len(sys.argv) > 2 else "87969badbde0a77c2c181bb9605357d51a4a30c0"
if not (re.fullmatch(r"[a-f0-9]{40}", ACTIVE) and re.fullmatch(r"[a-f0-9]{40}", FALLBACK)):
    raise SystemExit("FERRARI_PHASE6_INVALID_RELEASE_SHA")
GLOBAL_NAMES = {
    "libreoffice":"libreoffice", "ansible":"ansible", "ytdlp":"yt-dlp",
    "gimp":"gimp", "blender":"blender", "kdenlive":"kdenlive",
    "darktable":"darktable", "openscad":"openscad", "librecad":"librecad",
    "qgis":"qgis", "audacity":"audacity", "obs":"obs",
    "solvespace":"solvespace", "synfig":"synfigstudio",
    "openshot":"openshot-qt", "calibre":"ebook-convert",
}
ESSENTIAL_LIBS = {
    "linux-vdso.so.1","ld-linux-x86-64.so.2","libc.so.6",
    "libm.so.6","libdl.so.2","librt.so.1","libpthread.so.0",
    "libresolv.so.2","libnss_files.so.2","libgcc_s.so.1",
    "libutil.so.1",
    "libstdc++.so.6","libz.so.1","libzstd.so.1",
}


def inside(path: Path) -> bool:
    try:
        return path.resolve(strict=True).is_relative_to(HOME.resolve(strict=True))
    except (OSError, RuntimeError):
        return False


def dependencies(paths: list[Path], cap=96):
    """Use Ubuntu's ldd for inspection only, never to launch an app workload."""
    records = []
    cli = Path("/usr/bin/ldd")
    if not cli.is_file():
        return {"probe":"unavailable","records":[]}
    # Match the verified private execution environment. Plain ldd misses
    # bundled libraries such as Darktable's libdarktable.so and can falsely
    # classify Ferrari-owned FFmpeg/ImageMagick libs as system dependencies.
    private_lib_dirs = (
        HOME/"tools/ubuntu-cli/lib",
        HOME/"tools/ubuntu-cli/lib/darktable",
        HOME/"runtimes/python3.12/lib",
        HOME/"tools/blender/lib",
        HOME/"tools/libreoffice/program",
    )
    lib_path = ":".join(str(p) for p in private_lib_dirs if p.is_dir() and inside(p))
    for exe in paths[:cap]:
        try:
            with exe.open("rb") as stream:
                if stream.read(4) != b"\x7fELF":
                    continue
            probe = subprocess.run([str(cli), str(exe)], capture_output=True,
                                   text=True, timeout=7, check=False,
                                   env={"PATH":"/usr/bin:/bin","LANG":"C",
                                        "LD_LIBRARY_PATH":lib_path})
        except (OSError, subprocess.TimeoutExpired):
            records.append({"tool":exe.name,"probe":"unavailable"})
            continue
        libraries = []
        for line in probe.stdout.splitlines()[:110]:
            match = re.match(r"\s*([A-Za-z0-9_.+-]+\.so(?:\.[0-9]+)*)\s*=>\s*(/[^ ]+|not found)", line)
            if not match:
                continue
            lib, location = match.groups()
            if location == "not found":
                origin = "missing"
            elif inside(Path(location)):
                origin = "private_ferrari"
            elif lib in ESSENTIAL_LIBS:
                origin = "ubuntu_base"
            else:
                origin = "system_or_other_project_review"
            libraries.append({"library":lib,"origin":origin,
                              "resolved_to":location if location != "not found" else None})
        records.append({"tool":exe.name,"probe":"ldd_read_only",
                        "returncode":probe.returncode,
                        "libraries":libraries[:160]})
    return {"probe":"ldd_read_only","sampled":len(records),"records":records}


def process_snapshot():
    """Counts names of running global binaries, never reads args/env/credentials."""
    watched = set(GLOBAL_NAMES.values())
    tally = Counter()
    observed = 0
    for folder in list(Path("/proc").glob("[0-9]*"))[:2048]:
        try:
            link = os.readlink(folder / "exe")
        except (OSError, PermissionError):
            continue
        observed += 1
        path = Path(link.split(" (deleted)", 1)[0])
        if path.name in watched and str(path).startswith(("/usr/bin/", "/usr/local/bin/")):
            tally[path.name] += 1
    return {"examined_readable_processes":observed,
            "running_global_binary_instances":dict(sorted(tally.items())),
            "limitations":"One process snapshot only; zero running processes never proves zero consumers"}


def symlink_snapshot():
    """Inspect bounded symlink names only inside Ferrari-owned directories."""
    roots = [
        HOME/"tools", HOME/"runtimes", HOME/".runtime/npm",
        HOME/".runtime/venvs", HOME/"tools/ubuntu-cli/bin",
    ]
    escapes = []
    inspected = 0
    for root in roots:
        if not root.is_dir() or root.is_symlink() or not inside(root):
            continue
        try:
            children = list(root.iterdir())[:320]
        except OSError:
            continue
        for item in children:
            if not item.is_symlink():
                continue
            inspected += 1
            if not inside(item):
                escapes.append({"location":str(item.relative_to(HOME)),
                                "classification":"external_or_broken_symlink_review"})
    return {"sampled_symlinks":inspected,
            "external_or_broken_symlinks":escapes[:80],
            "limits":"Only five Ferrari-owned top-level directories, no foreign tree traversal"}


def main():
    if (not HOME.is_dir() or HOME.is_symlink()
            or not (HOME/"current").is_symlink()):
        raise SystemExit("FERRARI_PHASE6_BAD_OWNERSHIP")
    current = (HOME/"current").resolve(strict=True)
    if current != HOME/"releases"/ACTIVE:
        raise SystemExit("FERRARI_PHASE6_UNEXPECTED_ACTIVE_RELEASE")
    fallback = HOME/"releases"/FALLBACK
    if not (fallback.is_dir() and (fallback/"engine/ferrari.py").is_file()):
        raise SystemExit("FERRARI_PHASE6_FALLBACK_MISSING")
    sys.path.insert(0, str(current))
    from engine import cad_tools, ferrari, tool_runtime

    manifest = tool_runtime.specs()
    private = {}
    failures = []
    executables = []
    for action in manifest.values():
        tool, binary = action["tool"], action["binary"]
        path = tool_runtime.executable(tool, binary)
        if not path or not inside(Path(path)):
            failures.append(action["id"])
            continue
        if not (Path(path).is_file() and os.access(path, os.X_OK)):
            failures.append(action["id"])
            continue
        private[action["id"]] = {"tool":tool,"executable":str(Path(path).relative_to(HOME))}
        executables.append(Path(path))
    base = {}
    for name in ("blender","openscad","libreoffice"):
        try:
            exe = Path(cad_tools._binary(name))
            if not inside(exe):
                raise RuntimeError("NOT_PRIVATE")
            base[name] = str(exe.relative_to(HOME))
            executables.append(exe)
        except (OSError,RuntimeError,ValueError) as exc:
            failures.append("base:"+name)
    for name in ("pdftotext","convert","ffmpeg","ffprobe","strings","jadx"):
        try:
            exe = Path(ferrari._exe(name))
            if not inside(exe):
                raise RuntimeError("NOT_PRIVATE")
            base[name] = str(exe.relative_to(HOME))
            executables.append(exe)
        except (OSError,RuntimeError,ValueError):
            failures.append("base:"+name)
    runtimes = {}
    for name,rel in (
        ("python","runtimes/python3.12/bin/python3.12"),
        ("node","runtimes/node-22.23.4/bin/node"),
        ("java","runtimes/jdk-25.0.5_8/bin/java"),
    ):
        path = HOME/rel
        runtimes[name] = {"private":inside(path) and path.is_file() and os.access(path,os.X_OK),
                          "relative_path":rel}
    if not all(x["private"] for x in runtimes.values()):
        failures.append("runtime_missing")
    summary=tool_runtime.inventory()
    global_apps={}
    for app,binary in GLOBAL_NAMES.items():
        global_apps[app]=any(Path(folder,binary).is_file() for folder in ("/usr/bin","/usr/local/bin"))
    unique=sorted(set(executables),key=lambda p:str(p))
    report = {
        "schema":1,"phase":6,"mode":"audit_only","active_release":ACTIVE,
        "fallback_preserved":True,"directory":str(HOME),
        "registered_actions":len(manifest),
        "private_actions_confirmed":len(private),
        "missing_or_escaping_actions":sorted(set(failures)),
        "private_base_executors":base,
        "private_runtime_executors":runtimes,
        "selected_candidates":summary["selected"],
        "selected_detected_in_active_release":summary["selected_detected"],
        "selected_not_detected_in_active_release":summary["selected_not_detected"],
        "app_globals_observed_not_owned":global_apps,
        "global_app_process_snapshot":process_snapshot(),
        "symlink_audit":symlink_snapshot(),
        "shared_libraries":dependencies(unique),
        "deletion_authorized":False,
        "global_package_ownership_proven":False,
        "statement":"An installed global application is not an installed Ferrari tool. Unused cannot be proven from a process snapshot. No removal authorized.",
    }
    print(json.dumps(report,ensure_ascii=False,sort_keys=True))
    if failures or len(private)!=40:
        raise SystemExit("FERRARI_PHASE6_PRIVATE_GATE_FAILED")


if __name__=="__main__":
    main()
