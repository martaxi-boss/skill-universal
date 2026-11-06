#!/usr/bin/env python3
"""Ferrari F9: privacy-preserving, read-only audit of remaining GLOBAL APT apps.

This is an evidence collector, not a purge command. It does not read file
contents outside text executable/config files, follow symlinks, change service
state, update packages, or modify any project. Any incomplete coverage is NO-GO.
"""
from __future__ import annotations

from collections import Counter
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import time

ROOT = Path("/srv/projects/skill-universal")
EXPECTED = "7bf6dcecf15da26502c5969b5eee54d5e116fc32"
FALLBACK = "952b0a75ba798471b07053677d53791bd078ed56"
PACKAGES = ("yt-dlp", "librecad", "qgis", "audacity", "obs-studio",
            "solvespace", "synfigstudio", "openshot-qt")
SERVICES = ("pink-iptv-backend", "pink-vpn", "fadego-staging", "lowcost-europa",
            "pm2-iptvpn-bot", "pm2-telegram-robot-leads", "nginx",
            "postgresql@16-main")
PROJECTS = ("Codex", "VPS", "fadego", "iptvpn-bot", "lowcost-europa",
            "pink-iptv", "telegram-robot-leads")
EXTS = {".py", ".js", ".jsx", ".ts", ".tsx", ".sh", ".bash", ".zsh",
        ".json", ".yml", ".yaml", ".toml", ".xml", ".service",
        ".ini", ".conf", ".cfg", ".php", ".pl", ".rb", ".go", ".rs",
        ".properties", ".ps1", ".sql", ".desktop", ".env.example"}
SPECIAL = {"Dockerfile", "Makefile", "Procfile", "Caddyfile", "Gemfile"}
MAX_FILE = 32 * 1024 * 1024
MAX_PATHS = 280000
MAX_SECONDS = 160
TERMS = re.compile(rb"(?<![A-Za-z0-9_-])("
                   rb"yt-dlp|librecad|qgis|audacity|obs-studio|"
                   rb"solvespace|synfigstudio|openshot-qt"
                   rb")(?![A-Za-z0-9_-])", re.I)
READ_BLOCK = 262144


def command(args: list[str], timeout: int = 40) -> subprocess.CompletedProcess:
    return subprocess.run(args, text=True, capture_output=True,
                          check=False, timeout=timeout,
                          env={**os.environ, "LC_ALL": "C", "LANG": "C"})


def require(value: bool, message: str) -> None:
    if not value:
        raise RuntimeError(message)


def verify_release() -> dict:
    require(ROOT.is_dir() and not ROOT.is_symlink(), "F9_FERRARI_ROOT_UNSAFE")
    current = ROOT / "current"
    require(current.is_symlink(), "F9_CURRENT_NOT_A_POINTER")
    actual = current.resolve(strict=True)
    require(actual == ROOT / "releases" / EXPECTED, "F9_CURRENT_SHA_MISMATCH")
    require((ROOT / "releases" / FALLBACK / "engine/ferrari.py").is_file(),
            "F9_FALLBACK_MISSING")
    doc = json.loads((actual / "engine/catalog.json").read_text(encoding="utf-8"))
    require(doc.get("counts", {}).get("all_catalog_entries") == 450
            and len(doc.get("functions", [])) == 272
            and len(doc.get("tools", [])) == 173, "F9_CATALOG_DRIFT")
    for path in ("tools", "runtimes", ".runtime"):
        p = ROOT / path
        require(p.is_dir() and not p.is_symlink(), "F9_RUNTIME_ROOT_UNSAFE")
    return {"active": EXPECTED, "fallback": FALLBACK, "catalog_entries": 450}


def package_state() -> tuple[dict, set[str], bool]:
    state = {}
    files = set()
    for name in PACKAGES:
        q = command(["dpkg-query", "-W", "-f=${Status}|${Version}", name], timeout=12)
        present = q.returncode == 0 and q.stdout.startswith("install ok installed|")
        state[name] = {"installed": present,
                       "version": q.stdout.split("|", 1)[1].strip() if present else None}
        if not present:
            continue
        q = command(["dpkg-query", "-L", name], timeout=15)
        require(q.returncode == 0, "F9_DPKG_FILES_UNKNOWN:" + name)
        for raw in q.stdout.splitlines():
            if raw.startswith(("/usr/bin/", "/usr/sbin/", "/usr/lib/", "/usr/libexec/")):
                files.add(raw)
                try:
                    files.add(str(Path(raw).resolve(strict=False)))
                except (OSError, RuntimeError):
                    pass
    sim = command(["apt-get", "-s", "purge", *PACKAGES], timeout=120)
    require(sim.returncode == 0, "F9_PURGE_SIMULATION_FAILED")
    steps = [l.split()[:2] for l in sim.stdout.splitlines()
             if l.startswith(("Purg ", "Remv ", "Inst ", "Conf "))]
    removal = [row[1] for row in steps if row[0] in {"Purg", "Remv"} and len(row) > 1]
    installs = [row[1] for row in steps if row[0] == "Inst" and len(row) > 1]
    exact = set(removal) == set(PACKAGES) and len(removal) == 8 and not installs
    return state, files, exact


def independent_dpkg_package_state(name: str) -> dict:
    """Cross-check dpkg -s against a separate status-query output contract."""
    first = command(["dpkg", "-s", name], timeout=12)
    first_installed = first.returncode == 0 and any(
        row.strip() == "Status: install ok installed"
        for row in first.stdout.splitlines())
    second = command(["dpkg-query", "-W", "-f=${Status}", name], timeout=12)
    second_installed = (second.returncode == 0
                        and second.stdout.strip() == "install ok installed")
    require(first_installed == second_installed,
            "F9_DPKG_STATUS_METHODS_DISAGREE:" + name)
    return {"installed": first_installed,
            "dpkg_status_matches_query": True}


def verify_packages_only() -> dict:
    require(os.geteuid() == 0, "F9_AUDIT_REQUIRES_ROOT_READ_ONLY")
    identity = verify_release()
    states = {name: independent_dpkg_package_state(name) for name in PACKAGES}
    services = {}
    for name in SERVICES:
        p = command(["systemctl", "is-active", name], timeout=10)
        services[name] = p.returncode == 0 and p.stdout.strip() == "active"
    require(all(services.values()), "F9_PROTECTED_SERVICES_UNHEALTHY")
    return {
        "status": "PASS", "mode": "independent_dpkg_validation", **identity,
        "packages": states, "methods_agree": True,
        "installed_count": sum(item["installed"] for item in states.values()),
        "protected_services_active": len(SERVICES),
        "apt_changes": 0, "file_changes": 0,
        "other_projects_modified": False,
        "purge_authorized": False,
    }


def consumer_scan(project: Path, deadline: float, owned: set[str]) -> dict:
    count = content = large = errors = unexpected_symlinks = paths_seen = 0
    references: Counter[str] = Counter()
    def error(_):
        nonlocal errors
        errors += 1

    for base, dirs, filenames in os.walk(project, topdown=True,
                                          followlinks=False, onerror=error):
        if time.monotonic() > deadline or paths_seen > MAX_PATHS:
            errors += 1
            break
        dirs[:] = [d for d in dirs if d != ".git" and
                   not (Path(base) / d).is_symlink()]
        for name in filenames:
            paths_seen += 1
            if paths_seen > MAX_PATHS or time.monotonic() > deadline:
                errors += 1
                break
            p = Path(base) / name
            if p.is_symlink():
                try:
                    if str(p.resolve(strict=True)) in owned:
                        unexpected_symlinks += 1
                except (OSError, RuntimeError):
                    errors += 1
                continue
            if p.suffix not in EXTS and name not in SPECIAL:
                continue
            try:
                st = p.stat()
                if not p.is_file():
                    continue
                if st.st_size > MAX_FILE:
                    large += 1
                    continue
                count += 1
                with p.open("rb") as stream:
                    tail = b""
                    while block := stream.read(READ_BLOCK):
                        content += len(block)
                        for match in TERMS.finditer(tail + block):
                            references[match.group(1).decode("ascii").lower()] += 1
                        tail = block[-70:]
            except (OSError, PermissionError):
                errors += 1
        if errors or paths_seen > MAX_PATHS:
            break
    return {
        "project": project.name, "candidate_paths": paths_seen,
        "config_and_source_files_checked": count,
        "source_bytes_checked": content, "large_code_files_unchecked": large,
        "read_errors_or_timeouts": errors, "global_executable_symlinks": unexpected_symlinks,
        "mentions_of_global_program_names": dict(sorted(references.items())),
        "complete_for_selected_source_types": errors == 0 and large == 0,
    }


def live_reference_count(owned: set[str]) -> dict:
    by_type = Counter()
    # No raw command-line/environment text is written to logs.
    for p in Path("/proc").iterdir():
        if not p.name.isdecimal():
            continue
        try:
            if os.readlink(p / "exe") in owned:
                by_type["live_executables"] += 1
        except (OSError, PermissionError):
            pass
        try:
            maps = (p / "maps").read_text(errors="replace")
            if any(len(parts := line.split()) >= 6
                   and parts[-1] in owned
                   for line in maps.splitlines()):
                by_type["loaded_package_libraries"] += 1
        except (OSError, PermissionError):
            pass
    return dict(by_type)


def audit() -> dict:
    require(os.geteuid() == 0, "F9_AUDIT_REQUIRES_ROOT_READ_ONLY")
    identity = verify_release()
    states, owned, exact = package_state()
    active = {}
    for name in SERVICES:
        q = command(["systemctl", "is-active", name], timeout=10)
        active[name] = q.returncode == 0 and q.stdout.strip() == "active"
    services_ok = all(active.values())
    deadline = time.monotonic() + MAX_SECONDS
    root_projects = ROOT.parent
    observed = {p.name for p in root_projects.iterdir()
                if p.is_dir() and not p.is_symlink() and p.name != ROOT.name}
    missing = sorted(set(PROJECTS) - observed)
    unknown = sorted(observed - set(PROJECTS))
    projects = [consumer_scan(root_projects / name, deadline, owned)
                for name in PROJECTS if name in observed]
    live = live_reference_count(owned)
    scanned_fully = (len(projects) == len(PROJECTS)
                     and not missing and not unknown
                     and all(x["complete_for_selected_source_types"] for x in projects))
    program_mentions = sum(sum(x["mentions_of_global_program_names"].values())
                           for x in projects)
    blockers = []
    if not all(x["installed"] for x in states.values()):
        blockers.append("expected_global_package_missing")
    if not exact:
        blockers.append("apt_simulation_changes_unapproved_packages")
    if not services_ok:
        blockers.append("protected_services_unhealthy")
    if not scanned_fully:
        blockers.append("cross_project_scan_incomplete")
    if program_mentions:
        blockers.append("cross_project_named_references_need_manual_classification")
    if live or any(x["global_executable_symlinks"] for x in projects):
        blockers.append("global_executable_or_shared_lib_consumer_found")
    # Read-only APT references do not prove all GUI features or runtime ABI compatibility.
    blockers.append("gui_and_transitive_dependency_certification_not_yet_complete")
    return {
        "status": "PASS", "mode": "read_only", **identity,
        "packages": states, "apt_simulation_only_eight": exact,
        "all_eight_services_healthy": services_ok,
        "protected_service_count": sum(active.values()),
        "project_scans": projects,
        "missing_project_dirs": missing,
        "unreviewed_project_dirs": unknown,
        "scan_complete": scanned_fully, "global_runtime_consumers": live,
        "source_program_mentions": program_mentions,
        "package_purge_authorized": False,
        "remaining_blockers": blockers,
        "file_changes": 0, "apt_changes": 0, "other_projects_modified": False,
    }


if __name__ == "__main__":
    try:
        if sys.argv[1:] == ["--verify-packages"]:
            report = verify_packages_only()
            marker = "FERRARI_F9_APT_INDEPENDENT_DPKG=PASS"
        elif len(sys.argv) == 1:
            report = audit()
            marker = "FERRARI_F9_GLOBAL_APT_READONLY=PASS"
        else:
            raise RuntimeError("F9_UNKNOWN_MODE")
        print(json.dumps(report, sort_keys=True, indent=2))
        print(marker, file=sys.stderr)
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "BLOCKED", "reason": str(exc),
                          "apt_changes": 0}), file=sys.stderr)
        raise SystemExit(2)
