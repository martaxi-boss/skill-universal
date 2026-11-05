#!/usr/bin/env python3
"""Ferrari Fase 6 independent deep certificate probe (read-only).

Trusted code arrives via a pinned GitHub checkout and runs from stdin with the
Ferrari-owned Python interpreter. No package installation, file deletion,
service control, secret reads, or reading of another project's source.
Reports only sanitized executable, package and symlink classifications.
"""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path("/srv/projects/skill-universal")
ACTIVE = "146145d5ada9c13e368df18727e4dbf4f5807664"
FALLBACK = "40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
GLOBAL_APPS = {
    "libreoffice": "libreoffice", "ansible": "ansible",
    "ytdlp": "yt-dlp", "gimp": "gimp",
    "blender": "blender", "kdenlive": "kdenlive",
    "darktable": "darktable", "openscad": "openscad",
    "librecad": "librecad", "qgis": "qgis",
    "audacity": "audacity", "obs": "obs",
    "solvespace": "solvespace", "synfig": "synfigstudio",
    "openshot": "openshot-qt", "calibre": "ebook-convert",
}
SCAN_ROOTS = (
    "tools", "runtimes", ".runtime/npm", ".runtime/venvs",
    ".runtime/browsers", ".runtime/python",
    ".runtime/venv", "releases/" + ACTIVE,
)
ENTRY_LIMIT = 220000
BASE_INTERPRETERS = ("/bin/sh", "/bin/bash", "/usr/bin/bash", "/usr/bin/env")


def command(args, max_time=6):
    try:
        p = subprocess.run(args, capture_output=True, text=True,
                           timeout=max_time, check=False, env={
                               "PATH": "/usr/bin:/bin", "LC_ALL": "C"})
        return p.returncode, p.stdout[:6000]
    except (OSError, subprocess.TimeoutExpired):
        return 98, ""


def inside(p):
    try:
        return p.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
    except (OSError, RuntimeError, ValueError):
        return False


def verify_runtime():
    if ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("Ferrari project root is not an owned directory")
    current = ROOT / "current"
    if not current.is_symlink() or current.resolve(strict=True) != ROOT / "releases" / ACTIVE:
        raise RuntimeError("Active release mismatch")
    if not (ROOT / "releases" / FALLBACK / "engine/ferrari.py").is_file():
        raise RuntimeError("Fallback is missing")
    sys.path.insert(0, str(current))
    from engine import cad_tools, ferrari, tool_runtime
    manifest = tool_runtime.specs()
    if len(manifest) != 40:
        raise RuntimeError("Unexpected action count")
    checked = {}
    escapes = []
    paths = set()
    for a in manifest.values():
        exe = tool_runtime.executable(a["tool"], a["binary"])
        if not exe or not Path(exe).is_file() or not inside(Path(exe)):
            escapes.append(a["id"])
            continue
        paths.add(str(exe))
        checked[a["id"]] = {"tool": a["tool"], "executor": str(Path(exe).relative_to(ROOT))}
    for name in ("blender", "openscad", "libreoffice"):
        try:
            exe = Path(cad_tools._binary(name))
            if not inside(exe):
                raise RuntimeError("External executable")
            paths.add(str(exe))
        except (OSError, ValueError, RuntimeError):
            escapes.append("base:" + name)
    for name in ("pdftotext", "convert", "ffmpeg", "ffprobe", "strings", "jadx"):
        try:
            exe = Path(ferrari._exe(name))
            if not inside(exe):
                raise RuntimeError("External executable")
            paths.add(str(exe))
        except (OSError, ValueError, RuntimeError):
            escapes.append("base:" + name)
    runtimes = {}
    for key,rel in {
        "python": "runtimes/python3.12/bin/python3.12",
        "node": "runtimes/node-22.23.4/bin/node",
        "java": "runtimes/jdk-25.0.5_8/bin/java",
    }.items():
        f = ROOT / rel
        runtimes[key] = f.is_file() and inside(f) and os.access(f, os.X_OK)
        if not runtimes[key]:
            escapes.append("runtime:" + key)
        else:
            paths.add(str(f))
    found = tool_runtime.inventory()
    return {
        "actions_private": len(checked),
        "actions_total": len(manifest),
        "action_escapes_or_missing": sorted(escapes),
        "runtime_private": runtimes,
        "detected_shortlist": found["selected_detected"],
        "shortlist_total": found["selected"],
    }, sorted(paths)


def scan_links():
    """Traverse only owned directory entries; never follow any symlink."""
    count = 0
    links = 0
    external = []
    broken = []
    examples = []
    by_root = {}
    truncated = False
    for label in SCAN_ROOTS:
        root = ROOT / label
        if not root.exists() or root.is_symlink() or not inside(root):
            by_root[label] = "not_owned_or_absent"
            continue
        local = 0
        for base, dirs, files in os.walk(root, followlinks=False):
            if count >= ENTRY_LIMIT:
                truncated = True
                break
            for name in dirs + files:
                count += 1
                local += 1
                p = Path(base) / name
                if not p.is_symlink():
                    continue
                links += 1
                rel = p.relative_to(ROOT).parts
                safe = "/".join(rel[:4])
                try:
                    target = p.resolve(strict=True)
                    if not inside(target):
                        external.append(safe)
                        if len(examples) < 30:
                            examples.append({"path": safe, "scope": "link_external"})
                except (OSError, RuntimeError):
                    broken.append(safe)
            if count >= ENTRY_LIMIT:
                truncated = True
                break
        by_root[label] = local
        if truncated:
            break
    return {"entries_checked": count, "symlinks_checked": links,
            "external_links_total": len(external),
            "broken_links_total": len(broken),
            "examples": examples,
            "by_root": by_root,
            "complete_under_budget": not truncated,
            "note": "links may target Ubuntu system interpreters; no foreign directory scanned"}


def interpreter_check(paths):
    entries = []
    counts = Counter()
    for name in paths:
        p = Path(name)
        if not p.is_file():
            continue
        try:
            with p.open("rb") as fh:
                row = fh.readline(240)
        except OSError:
            continue
        if not row.startswith(b"#!"):
            counts["not_script"] += 1
            continue
        shebang = row[2:].decode("utf-8", "replace").strip()
        program = shebang.split(maxsplit=1)[0] if shebang else ""
        if program in BASE_INTERPRETERS:
            cat = "ubuntu_shell_or_env"
        elif program.startswith(str(ROOT) + "/"):
            cat = "private_interpreter"
        elif program.startswith(("/usr/bin/", "/usr/local/bin/", "/bin/")):
            cat = "system_interpreter_requires_review"
        else:
            cat = "unrecognized_interpreter"
        counts[cat] += 1
        entries.append({"program": p.name, "interpreter": program, "classification": cat})
    return {"counts": dict(counts), "scripts": entries}


def global_ownership():
    """APT and process *indicators*, not proof of who installed each package."""
    entries = {}
    for app, binary in GLOBAL_APPS.items():
        exists = []
        for dirname in ("/usr/bin", "/usr/local/bin"):
            candidate = Path(dirname) / binary
            if candidate.is_file():
                exists.append(str(candidate))
        owners = []
        for path in exists[:2]:
            code, txt = command(["/usr/bin/dpkg-query", "-S", path])
            if code == 0:
                for line in txt.splitlines()[:4]:
                    if ":" in line:
                        item = line.split(":", 1)[0].strip()
                        if re.fullmatch(r"[a-zA-Z0-9.+-]{1,70}", item):
                            owners.append(item)
        reverse = {}
        for package in sorted(set(owners))[:4]:
            code, txt = command(["/usr/bin/apt-cache", "rdepends", "--installed", package])
            if code == 0:
                lines = [x.strip() for x in txt.splitlines() if x.strip() and
                         x.strip() not in (package, "Reverse Depends:")]
                reverse[package] = len(lines)
            else:
                reverse[package] = None
        entries[app] = {
            "global_path_present": bool(exists),
            "dpkg_package_owners": sorted(set(owners)),
            "installed_reverse_dependency_indicators": reverse,
            "ownership_exclusive_to_ferrari": False,
            "safe_to_remove": False,
        }
    return entries


def historical_alias():
    candidate = Path("/home/ubuntu/.local/share/motor-ferrari")
    if candidate.is_symlink():
        return "private_project_alias" if inside(candidate) else "unsafe_external_alias"
    if candidate.exists():
        return "external_physical_object_requires_review"
    return "absent"


def main():
    run, executables = verify_runtime()
    link = scan_links()
    shebangs = interpreter_check(executables)
    glob = global_ownership()
    aliases = historical_alias()
    report = {
        "schema": 1, "phase": 6, "mode": "read_only_deep_certification",
        "directory": str(ROOT), "release": ACTIVE, "fallback": FALLBACK,
        "executable_gate": run, "symlinks": link,
        "shebangs": shebangs,
        "global_apps": glob, "historical_alias": aliases,
        "global_packages_removed": 0, "files_deleted": 0,
        "all_globals_safe_to_remove": False,
        "certification_notes": [
            "40/40 typed actions plus base executors are a per-entrypoint proof, not a guarantee about optional plugins.",
            "No global package removal without independently proving consumers and ownership.",
            "System loader and base OS interpreters remain Ubuntu responsibilities.",
        ],
    }
    print(json.dumps(report, sort_keys=True, ensure_ascii=False))
    if (run["actions_private"] != 40 or
            run["action_escapes_or_missing"] or
            not all(run["runtime_private"].values()) or
            run["detected_shortlist"] < 47):
        raise SystemExit("FERRARI_PHASE6_DEEP_CERT_ENTRYPOINT_GATE_FAILED")


if __name__ == "__main__":
    main()
