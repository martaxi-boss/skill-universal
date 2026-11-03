#!/usr/bin/env python3
"""One-purpose Ferrari npm download cache cleanup. Never removes installed programs."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys

RELEASE = re.compile(r"^[0-9a-f]{40}$")


def _checked_directory(p: Path, allow_missing: bool = False) -> bool:
    try:
        s = p.lstat()
    except FileNotFoundError:
        if allow_missing:
            return False
        raise RuntimeError(f"Required directory missing: {p.name}") from None
    if not stat.S_ISDIR(s.st_mode) or stat.S_ISLNK(s.st_mode):
        raise RuntimeError(f"Unsafe directory or symlink: {p.name}")
    return True


def _runtime_state(root: Path) -> str:
    for p in (root, root / ".runtime", root / ".runtime/npm",
              root / ".runtime/npm-cache", root / "releases"):
        _checked_directory(p)
    if root.stat().st_uid != os.geteuid() or os.geteuid() == 0:
        raise RuntimeError("Ferrari must be inspected by its non-root owner")
    current = root / "current"
    if not current.is_symlink():
        raise RuntimeError("Missing Ferrari current release pointer")
    release = current.resolve(strict=True)
    if release.parent != (root / "releases").resolve(strict=True) or not RELEASE.fullmatch(release.name):
        raise RuntimeError("Current release points outside Ferrari releases")
    if not (release / "engine/ferrari.py").is_file():
        raise RuntimeError("Current Ferrari engine marker missing")

    own_rea = root / ".runtime/npm/rea/node_modules/.bin/rea"
    own_modules = (root / ".runtime/npm/rea/node_modules").resolve(strict=True)
    if not own_rea.is_file() or not own_rea.resolve(strict=True).is_relative_to(own_modules):
        raise RuntimeError("Ferrari REA private CLI missing or external")
    for rel in ("runtimes/node-22.23.4/bin/node",
                "runtimes/jdk-25.0.5_8/bin/java",
                "tools/apktool-3.0.3/bin/apktool",
                ".runtime/npm/ruflo/node_modules/.bin/ruflo"):
        if not (root / rel).is_file():
            raise RuntimeError("Required Ferrari runtime missing: " + rel)
    return release.name


def _no_cache_symlinks(cache: Path):
    if not _checked_directory(cache, allow_missing=True):
        return False
    for base, folders, files in os.walk(cache, topdown=True, followlinks=False):
        for name in folders + files:
            p = Path(base) / name
            if p.is_symlink():
                raise RuntimeError("Symlink found inside npm cache; skip cleanup")
    return True


def _no_active_npm_under_ferrari(root: Path):
    prefix = str(root.resolve(strict=True)) + "/"
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit() or int(proc.name) == os.getpid():
            continue
        try:
            cmd = (proc / "cmdline").read_bytes().replace(b"\x00", b" ").decode("utf-8", "replace").lower()
            cwd = os.readlink(proc / "cwd")
        except (PermissionError, FileNotFoundError, ProcessLookupError, OSError):
            continue
        if cwd.startswith(prefix) and any(x in cmd for x in ("npm ", "npm-cli.js", "npx ", "pnpm ", "yarn ")):
            raise RuntimeError("An npm installer is active inside Ferrari; cleanup blocked")


def _disk_free(root: Path) -> int:
    s = os.statvfs(root)
    return s.f_bavail * s.f_frsize


def _allocated_size(directory: Path) -> int:
    result = subprocess.run(["du", "-sxB1", str(directory)], capture_output=True,
                            text=True, timeout=150, check=True)
    return int(result.stdout.split()[0])


def audit(root: Path, apply: bool = False) -> dict:
    root = Path(root)
    release = _runtime_state(root)
    cache = root / ".runtime/npm-cache/_cacache"
    present = _no_cache_symlinks(cache)
    before = _disk_free(root)
    bytes_before = _allocated_size(cache) if present else 0
    _no_active_npm_under_ferrari(root)
    removed = False
    if apply and present:
        # This is an npm content-addressed download cache, not node_modules,
        # a Python venv, a browser, a release, or an REA/Apktool installation.
        if not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError("No fd-safe rmtree on this platform")
        shutil.rmtree(cache)
        removed = True
        if cache.exists() or cache.is_symlink():
            raise RuntimeError("Cache removal incomplete")
    if _runtime_state(root) != release:
        raise RuntimeError("Ferrari active release or private runtime changed")
    after = _disk_free(root)
    return {
        "status": "PASS",
        "mode": "apply" if apply else "audit",
        "scope": "ferrari-private-npm-download-cache-only",
        "active_ferrari_release": release,
        "cache_present_before": present,
        "cache_allocated_bytes_before": bytes_before,
        "cache_removed": removed,
        "free_bytes_before": before,
        "free_bytes_after": after,
        "free_bytes_delta": after - before,
        "rea_apktool_node_java_ruflo_preserved": True,
        "other_projects_touched": False,
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apply", action="store_true", help="Remove Ferrari npm download cache only")
    args = p.parse_args()
    root = Path.home() / ".local/share/motor-ferrari"
    try:
        result = audit(root, apply=args.apply)
    except (OSError, RuntimeError, ValueError, subprocess.SubprocessError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    print("FERRARI_PRIVATE_NPM_CACHE_HYGIENE=PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
