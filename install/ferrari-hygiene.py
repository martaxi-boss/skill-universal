#!/usr/bin/env python3
"""Conservative Ferrari-only release cleanup; default report-only.

Never touches any other project. Only 40-hex Ferrari release directories,
verified beneath ~/.local/share/motor-ferrari/releases, can be pruned.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys

HEX40=re.compile(r"[0-9a-f]{40}\Z")

def clean(apply=False):
    root=Path.home()/".local"/"share"/"motor-ferrari"
    release_root=root/"releases"
    pointer=root/"current"
    if root.is_symlink() or release_root.is_symlink():
        raise RuntimeError("Ferrari release root may not be symlinked")
    if not release_root.is_dir() or not pointer.is_symlink():
        raise RuntimeError("Ferrari active release symlink missing")
    root_real=root.resolve(strict=True)
    releases_real=release_root.resolve(strict=True)
    active=pointer.resolve(strict=True)
    if active.parent!=releases_real or not HEX40.fullmatch(active.name):
        raise RuntimeError("Active release is outside Ferrari releases directory")
    if not (active/"engine/ferrari.py").is_file():
        raise RuntimeError("Active Ferrari marker missing")
    if not (root_real/"runtimes").is_dir():
        raise RuntimeError("Ferrari install root missing runtime directory")
    all_dirs=[]
    for item in release_root.iterdir():
        if item.is_symlink() or not item.is_dir() or not HEX40.fullmatch(item.name):
            continue
        if item.resolve(strict=True).parent!=releases_real:
            continue
        if not (item/"engine/ferrari.py").is_file():
            continue
        all_dirs.append(item)
    # Preserve active plus last 149-test Ghidra/JADX certified Ferrari release.
    # The fallback is private Ferrari code; no provider runtimes or other projects pruned.
    fallback_sha="39267ce692edb8f40bf9621dba29a2f9642528b7"
    fallback=release_root/fallback_sha
    keep={active.name}
    if fallback in all_dirs:
        keep.add(fallback_sha)
    else:
        others=sorted((p for p in all_dirs if p.name!=active.name),
                      key=lambda p:p.stat().st_mtime,reverse=True)
        if others: keep.add(others[0].name)
    candidates=[p for p in all_dirs if p.name not in keep]
    def size(p):
        total=0
        for base, dirs, files in os.walk(p,followlinks=False):
            for name in files:
                item=Path(base)/name
                if not item.is_symlink():
                    try: total+=item.stat().st_size
                    except FileNotFoundError: pass
        return total
    before=shutil.disk_usage(root_real).free
    sizes={p.name:size(p) for p in candidates}
    # Directories may include old, separate npm node_modules; these are no longer
    # used by the active Ferrari runtime, which lives at root/.runtime/npm.
    removed=[]
    if apply:
        for p in candidates:
            if p == active or p.is_symlink() or p.resolve(strict=True).parent!=releases_real:
                raise RuntimeError("Unsafe cleanup target")
            shutil.rmtree(p)
            removed.append(p.name)
    after=shutil.disk_usage(root_real).free
    report={
        "mode":"apply" if apply else "preview",
        "scope":str(releases_real),
        "active":active.name,
        "preserved_releases":sorted(keep),
        "eligible_old_releases":[p.name for p in candidates],
        "removed_releases":removed,
        "estimated_reclaim_bytes":sum(sizes.values()),
        "actual_free_delta_bytes":after-before,
        "disk_free_after_gib":round(after/(1024**3),2),
        "outside_ferrari_touched":False,
        "status":"PASS"
    }
    return report

if __name__=="__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    opts=ap.parse_args()
    try:
        result=clean(opts.apply)
        print(json.dumps(result,indent=2))
        print("FERRARI_ONLY_HYGIENE=PASS")
    except (OSError,RuntimeError) as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc)}),file=sys.stderr)
        sys.exit(2)
