#!/usr/bin/env python3
"""Conservative Ferrari-only release cleanup; default report-only.

Never touches any other project. Only verified Ferrari release directories and known disposable smoke folders,
verified beneath /srv/projects/skill-universal/releases, can be pruned.
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

PROJECT_ROOT=Path("/srv/projects/skill-universal")

def clean(apply=False):
    alias=Path.home()/".local"/"share"/"motor-ferrari"
    # The legacy link is optional, but a present unexpected link or physical
    # duplicate outside the canonical project root still blocks hygiene.
    if alias.is_symlink():
        if (not PROJECT_ROOT.is_dir() or PROJECT_ROOT.is_symlink() or
                alias.resolve(strict=True)!=PROJECT_ROOT):
            raise RuntimeError("Ferrari project alias is outside its isolated directory")
    elif alias.exists():
        raise RuntimeError("Ferrari project alias is outside its isolated directory")
    root=PROJECT_ROOT
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
    # Preserve the exact two releases certified on the live Ferrari VPS.
    # Never guess the fallback by mtime: that could delete the known-good F5.
    fallback_sha="40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
    fallback=release_root/fallback_sha
    keep={active.name,fallback_sha}
    if fallback not in all_dirs:
        raise RuntimeError("Certified Ferrari phase-5 fallback missing: refusing cleanup")
    if active.name!="146145d5ada9c13e368df18727e4dbf4f5807664":
        raise RuntimeError("Unexpected Ferrari active SHA: refusing phase-6 hygiene")
    candidates=[p for p in all_dirs if p.name not in keep]
    # Do not prune release code referenced by a current process.
    # Only inspect pid cwd/exe/cmdline locally; do not print them or read secrets.
    used=set()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdigit():
            continue
        try:
            refs=[os.readlink(proc/"cwd"),os.readlink(proc/"exe")]
            refs.extend(arg.decode("utf-8","replace") for arg in
                        (proc/"cmdline").read_bytes().split(b"\x00")[:9] if arg)
        except (OSError,PermissionError):
            continue
        for p in candidates:
            if any(str(p) in ref for ref in refs):
                used.add(p.name)
    if used:
        raise RuntimeError("Old Ferrari releases currently referenced by processes: "+str(len(used)))
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
        if not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError("Safe Ferrari release cleanup requires fd-safe rmtree")
        if pointer.resolve(strict=True) != active or not fallback.is_dir():
            raise RuntimeError("Ferrari active/fallback changed during cleanup")
        for p in candidates:
            if p == active or p.is_symlink() or p.resolve(strict=True).parent!=releases_real:
                raise RuntimeError("Unsafe cleanup target")
            shutil.rmtree(p)
            removed.append(p.name)
    # Delete only known disposable Ferrari certification workspaces.
    # Never touch provider runtimes, npm node_modules, other project names or
    # arbitrary folders: these names are exclusively Ferrari smoke artefacts.
    runtime=root_real/".runtime"
    scratch_names=("private-gui-test","python-tools-smoke","private-python-smoke",
                   "private-cli-cert","private-media-cert","native-cli-cert",
                   "python-cli-cert","private-python-cert","private-gui-cert",
                   "browser-release-smoke","isolation-release-smoke",
                   "native-cli-release-smoke","media-cli-release-smoke",
                   "private-cli-release-smoke","python-cli-release-smoke")
    scratch_targets=[]
    if runtime.exists():
        if runtime.is_symlink() or not runtime.is_dir():
            raise RuntimeError("Unsafe Ferrari private runtime root")
        for name in scratch_names:
            p=runtime/name
            if p.is_symlink():
                raise RuntimeError("Unsafe Ferrari smoke symlink: "+name)
            if p.is_dir():
                # fd-safe rmtree removes nested symlinks themselves, never
                # their targets. The top-level directory is never a symlink.
                scratch_targets.append(p)
    scratch_sizes={p.name:size(p) for p in scratch_targets}
    scratch_removed=[]
    if apply:
        if not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError("Safe Ferrari scratch cleanup requires fd-safe rmtree")
        for p in scratch_targets:
            if p.parent!=runtime or p.is_symlink() or not p.is_dir():
                raise RuntimeError("Unsafe Ferrari smoke cleanup target")
            shutil.rmtree(p)
            scratch_removed.append(p.name)
    if pointer.resolve(strict=True)!=active or not fallback.is_dir():
        raise RuntimeError("Ferrari production release/fallback changed during hygiene")
    after=shutil.disk_usage(root_real).free
    report={
        "mode":"apply" if apply else "preview",
        "scope":str(releases_real),
        "active":active.name,
        "preserved_releases":sorted(keep),
        "eligible_old_releases":[p.name for p in candidates],
        "removed_releases":removed,
        "removed_smoke_directories":scratch_removed,
        "eligible_smoke_directories":[p.name for p in scratch_targets],
        "estimated_reclaim_bytes":sum(sizes.values())+sum(scratch_sizes.values()),
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
