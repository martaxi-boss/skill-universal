#!/usr/bin/env python3
"""Ferrari-only universal-catalog hygiene: read-only preview, then guarded apply.

Only removes obsolete *versioned source snapshots* under the Ferrari release
directory, NEVER the active release, its designated fallback, private programs,
runtimes, projects, services or global Ubuntu packages.  This is not a new
catalog or coordinator.  No implicit cleanup after activation.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys

ROOT = Path("/srv/projects/skill-universal")
SHA = re.compile(r"[a-f0-9]{40}\Z")
LEGACY_FILES = (
    "engine/ubuntu_selection.json", "engine/tool_actions.json",
    "engine/providers.json", "engine/ferrari_registry.json",
    "engine/ferrari_expansion.json",
)
STATE_DIRS = frozenset((".runtime", "runtimes", "tools", "data",
                        "backups", "results", "outputs", "secrets"))

# Each of these exact old source snapshots was measured in live read-only
# GitHub Actions #42296172655: its ONLY stateful directory was an EMPTY .runtime,
# with zero files, zero nested directories, zero symlinks and zero data bytes.
# All other state-bearing directories remain hard blockers to source deletion.
AUDITED_EMPTY_RUNTIME = frozenset((
    "0b50e1d403deff8f3ccb421edd0b41c397d66b9b",
    "146145d5ada9c13e368df18727e4dbf4f5807664",
    "758e1b435317fa26277b332b75bc47c67910be81",
    "7776a34e667d76ae0e980e65449d2b2cc67c2059",
    "9d0deb5d9cd919d8bf468e8cfb501c056a64c664",
    "a266b25e06a9c8acf1fdc940d22b99070cd17ded",
    "decdb5a38b0bf0e2ce66c6351a45b2d2e8e294c2",
    "f1f3b03525adec7018d7d629243e7b0fbb7f5087",
    "fe1bb6e7073fdd8a963963909127cde6d570f253",
))

# Top-level names are from the GitHub trees of all nine pinned commits.
# A newly created file/folder at release root is *not* presumed disposable.
SOURCE_ROOT_NAMES = frozenset((
    ".github", "BOOTSTRAP.md", "LICENSE", "README.md",
    "docs", "engine", "examples", "install", "integrations",
    "skill", "templates", "tests", ".runtime",
))


def _unsafe_private_state(release: Path) -> str | None:
    """Only the nine fully audited, still-empty .runtime folders are disposable."""
    if release.name in AUDITED_EMPTY_RUNTIME:
        for entry in release.iterdir():
            if entry.name not in SOURCE_ROOT_NAMES or entry.is_symlink():
                return "unexpected_file_or_symlink_at_release_root"
    for name in STATE_DIRS:
        p = release / name
        if not (p.exists() or p.is_symlink()):
            continue
        if name == ".runtime" and release.name in AUDITED_EMPTY_RUNTIME:
            # Critical: re-evaluate emptiness when applying, not just at preview.
            if p.is_dir() and not p.is_symlink() and not any(p.iterdir()):
                continue
            return "audited_runtime_now_nonempty_or_unsafe"
        return "unverified_stateful_directory_present"
    return None


def _protected_release_pointers(root: Path, releases: Path) -> set[str]:
    protected: set[str] = set()
    for p in root.iterdir():
        if p.is_symlink() and p.name != "current":
            try:
                target = p.resolve(strict=True)
            except (OSError, RuntimeError):
                continue
            if target.parent == releases:
                protected.add(target.name)
    return protected



def _inside_release(path: Path, parent: Path) -> bool:
    return (not path.is_symlink() and path.is_dir()
            and path.resolve(strict=True).parent == parent
            and bool(SHA.fullmatch(path.name)))


def _live_process_references(paths: list[Path]) -> set[str]:
    """Inspect only executable/cwd/arguments. Never inspect or print env/secrets."""
    used: set[str] = set()
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal():
            continue
        refs = []
        for name in ("cwd", "exe"):
            try:
                refs.append(os.readlink(proc / name))
            except (OSError, PermissionError):
                pass
        try:
            refs.extend(value.decode("utf-8", "replace")
                        for value in (proc / "cmdline").read_bytes().split(b"\0")[:16])
        except (OSError, PermissionError):
            pass
        for path in paths:
            prefix = str(path) + "/"
            if any(ref == str(path) or prefix in ref for ref in refs):
                used.add(path.name)
    return used


def audit(root: Path, expected_active: str, fallback_sha: str,
          apply: bool = False) -> dict:
    if not SHA.fullmatch(expected_active) or not SHA.fullmatch(fallback_sha):
        raise RuntimeError("Invalid immutable Ferrari release SHA")
    if expected_active == fallback_sha:
        raise RuntimeError("Active and fallback must differ")
    if root.is_symlink() or not root.is_dir():
        raise RuntimeError("Ferrari root missing or a symlink")
    root = root.resolve(strict=True)
    releases = root / "releases"
    current = root / "current"
    if releases.is_symlink() or not releases.is_dir() or not current.is_symlink():
        raise RuntimeError("Unsafe Ferrari release layout")
    for name in ("tools", "runtimes", ".runtime"):
        d = root / name
        if d.is_symlink() or not d.is_dir():
            raise RuntimeError("Missing or unsafe Ferrari-owned " + name)
    active = current.resolve(strict=True)
    release_real = releases.resolve(strict=True)
    if not _inside_release(active, release_real):
        raise RuntimeError("Active Ferrari release escapes releases/")
    fallback = releases / fallback_sha
    if (not _inside_release(fallback, release_real)
            or not (fallback / "engine/ferrari.py").is_file()
            or not (fallback / "engine/catalog.json").is_file()):
        raise RuntimeError("Designated fallback absent or unsafe")

    catalog_path = active / "engine/catalog.json"
    marker_path = active / "engine/ferrari.py"
    if not marker_path.is_file() or catalog_path.is_symlink() or not catalog_path.is_file():
        raise RuntimeError("Active Ferrari catalog or engine marker missing")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    new_catalog = (
        active.name == expected_active
        and catalog.get("functions_schema") == 1
        and len(catalog.get("functions", [])) == 272
        and len(catalog.get("tools", [])) == 173
        and catalog.get("counts", {}).get("all_catalog_entries") == 450
        and not "actions" in catalog
        and not "names" in catalog.get("mcp_capabilities", {})
    )
    legacy_in_active = [name for name in LEGACY_FILES if (active / name).exists()
                        or (active / name).is_symlink()]
    if apply and (not new_catalog or legacy_in_active):
        raise RuntimeError("Refusing deletion: active release is not the clean universal catalog")

    candidates: list[Path] = []
    skipped: list[dict] = []
    for p in releases.iterdir():
        if p.name in {active.name, fallback_sha}:
            continue
        if not SHA.fullmatch(p.name):
            continue
        if not _inside_release(p, release_real):
            skipped.append({"release": p.name, "reason": "unsafe_path"})
            continue
        if not (p / "engine/ferrari.py").is_file() or not (p / "engine/catalog.json").is_file():
            skipped.append({"release": p.name, "reason": "unrecognized_release"})
            continue
        reason = _unsafe_private_state(p)
        if reason:
            skipped.append({"release": p.name, "reason": reason})
            continue
        candidates.append(p)
    # Respect any source snapshot still referenced by a Ferrari-specific pointer.
    protected_links = _protected_release_pointers(root, release_real)
    used = _live_process_references(candidates)
    blocked = protected_links | used
    permitted = sorted((p for p in candidates if p.name not in blocked),
                       key=lambda path: path.name)
    for p in candidates:
        if p.name in blocked:
            skipped.append({"release": p.name, "reason": "referenced_by_process_or_pointer"})

    before = shutil.disk_usage(root).free
    removed: list[str] = []
    if apply:
        if not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError("Platform does not provide fd-safe rmtree")
        if active != current.resolve(strict=True) or not _inside_release(fallback, release_real):
            raise RuntimeError("Ferrari release changed while preparing cleanup")
        for p in permitted:
            # Every target must stay a direct child and be unreferenced at deletion time.
            if active != current.resolve(strict=True) or not _inside_release(p, release_real):
                raise RuntimeError("Ferrari cleanup path changed")
            if _unsafe_private_state(p):
                raise RuntimeError("Ferrari source gained private state after preview")
            if p.name in _live_process_references([p]):
                raise RuntimeError("Ferrari release became active in a process")
            if p.name in _protected_release_pointers(root, release_real):
                raise RuntimeError("Ferrari release became referenced by an auxiliary pointer")
            shutil.rmtree(p)
            removed.append(p.name)
    after = shutil.disk_usage(root).free
    return {
        "status": "PASS", "mode": "apply" if apply else "preview",
        "scope": str(release_real), "source": "engine/catalog.json",
        "active": active.name, "expected_active": expected_active,
        "fallback_preserved": fallback_sha, "universal_catalog_active": new_catalog,
        "active_catalog_entries": catalog.get("counts", {}).get("all_catalog_entries"),
        "legacy_catalog_files_in_active": legacy_in_active,
        "eligible_old_releases": [p.name for p in permitted],
        "skipped_old_releases": sorted(skipped, key=lambda x: x["release"]),
        "removed_old_releases": removed,
        "disk_free_before_bytes": before, "disk_free_after_bytes": after,
        "free_delta_bytes": after - before,
        "other_projects_or_ubuntu_modified": False,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--expected-active", required=True)
    p.add_argument("--fallback", required=True)
    p.add_argument("--apply", action="store_true")
    args = p.parse_args()
    try:
        report = audit(ROOT, args.expected_active, args.fallback, args.apply)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, sort_keys=True, indent=2))
    print("FERRARI_UNIVERSAL_HYGIENE=" + ("APPLY_PASS" if args.apply else "PREVIEW_PASS"), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
