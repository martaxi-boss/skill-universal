#!/usr/bin/env python3
"""Read-only evidence about stateful folders embedded in old Ferrari releases.

No deletions, no automatic migrations, no file contents, no secret-bearing
filenames, no commands against other projects. Executed by existing Ferrari
Actions/SSH with a source revision pinned in GitHub.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import time

ROOT = Path("/srv/projects/skill-universal")
SHA = re.compile(r"[0-9a-f]{40}\Z")
STATE_NAMES = (".runtime", "runtimes", "tools", "data", "backups",
               "results", "outputs", "secrets")
MAX_FILES = 25000
MAX_SECONDS = 8


def describe(folder: Path) -> dict:
    if folder.is_symlink():
        return {"kind": "symlink_not_followed", "bytes": None,
                "files": None, "directories": None, "truncated": True}
    if not folder.is_dir():
        return {"kind": "other_not_traversed", "bytes": None,
                "files": None, "directories": None, "truncated": True}
    files = dirs = symlinks = size = 0
    truncated = False
    start = time.monotonic()
    for base, subdirs, filenames in os.walk(folder, topdown=True, followlinks=False):
        # Never follow any symlink to private or external resources.
        safe = []
        for name in subdirs:
            p = Path(base) / name
            if p.is_symlink():
                symlinks += 1
            else:
                safe.append(name)
        subdirs[:] = safe
        dirs += len(safe)
        for name in filenames:
            p = Path(base) / name
            try:
                if p.is_symlink():
                    symlinks += 1
                elif p.is_file():
                    files += 1
                    size += p.stat().st_size
            except (OSError, PermissionError):
                truncated = True
            if files >= MAX_FILES or time.monotonic() - start > MAX_SECONDS:
                truncated = True
                subdirs[:] = []
                break
        if truncated or dirs >= MAX_FILES or time.monotonic() - start > MAX_SECONDS:
            truncated = True
            break
    return {"kind": "directory", "bytes": size, "files": files,
            "directories": dirs, "symlinks": symlinks, "truncated": truncated}


def audit(root: Path, expected: str, fallback: str) -> dict:
    if not SHA.fullmatch(expected) or not SHA.fullmatch(fallback) or expected == fallback:
        raise RuntimeError("Invalid pinned Ferrari release identifiers")
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError("Invalid Ferrari root")
    root = root.resolve(strict=True)
    releases = root / "releases"
    pointer = root / "current"
    if releases.is_symlink() or not releases.is_dir() or not pointer.is_symlink():
        raise RuntimeError("Invalid Ferrari release layout")
    active = pointer.resolve(strict=True)
    if active != releases / expected:
        raise RuntimeError("Expected universal Ferrari release is not active")
    if not (releases / fallback / "engine/ferrari.py").is_file():
        raise RuntimeError("Fallback Ferrari source marker absent")
    d = json.loads((active / "engine/catalog.json").read_text(encoding="utf-8"))
    if (d.get("counts", {}).get("all_catalog_entries") != 450
            or len(d.get("functions", [])) != 272):
        raise RuntimeError("Ferrari universal catalog not verified")

    rows = []
    for version in sorted(releases.iterdir()):
        if version.name in {expected, fallback} or not SHA.fullmatch(version.name):
            continue
        if (version.is_symlink() or not version.is_dir()
                or version.resolve(strict=True).parent != releases.resolve(strict=True)
                or not (version / "engine/ferrari.py").is_file()):
            continue
        found = {}
        for name in STATE_NAMES:
            p = version / name
            if p.exists() or p.is_symlink():
                found[name] = describe(p)
        if found:
            rows.append({"release": version.name, "state_directories": found})
    return {
        "status": "PASS", "mode": "read_only", "scope": str(releases),
        "active": expected, "fallback": fallback, "catalog_entries": 450,
        "releases_with_private_or_untracked_folders": rows,
        "releases_flagged": len(rows),
        "stateful_logical_bytes_scanned": sum(
            item["bytes"] or 0 for row in rows
            for item in row["state_directories"].values()),
        "truncated_directories": sum(
            int(item["truncated"]) for row in rows
            for item in row["state_directories"].values()),
        "disk_free_bytes": shutil.disk_usage(root).free,
        "files_modified": 0, "deletion_authorized": False,
        "other_projects_touched": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--expected-active", required=True)
    parser.add_argument("--fallback", required=True)
    args = parser.parse_args()
    try:
        data = audit(ROOT, args.expected_active, args.fallback)
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "BLOCKED", "error": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(data, indent=2, sort_keys=True))
    print("FERRARI_UNIVERSAL_OLD_RELEASE_DEEP_AUDIT=PASS", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
