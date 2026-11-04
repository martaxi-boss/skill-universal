#!/usr/bin/env python3
"""One-time Ferrari-private launcher migration and exact legacy symlink retirement.

Default is read-only. --apply may only run as the non-root owner of the
canonical Ferrari project. Other projects, services and releases are never edited.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import tempfile
import zipfile

ROOT = Path("/srv/projects/skill-universal")
ALIAS = Path("/home/ubuntu/.local/share/motor-ferrari")
CURRENT = ROOT / "current"
FALLBACK = ROOT / "releases/0a1a4c190a7d33752d6dc3f4418ed44735c8a7dd"
APKT = ROOT / "tools/apktool-3.0.3/bin/apktool"
VALKEY = ROOT / "tools/ferrari-services/valkey-server/bin/valkey-server"
PATCHES = (
    (APKT,
     b'ROOT="$HOME/.local/share/motor-ferrari"',
     b'ROOT="/srv/projects/skill-universal"'),
    (VALKEY,
     b'PRIVATE="$HOME/.local/share/motor-ferrari/tools/ferrari-services/valkey-server"',
     b'PRIVATE="/srv/projects/skill-universal/tools/ferrari-services/valkey-server"'),
)
SERVICES = ("ssh", "nginx", "postgresql@16-main", "pink-iptv-backend",
            "pink-vpn", "fadego-staging", "lowcost-europa",
            "pm2-iptvpn-bot", "pm2-telegram-robot-leads")


def rewrite_exact(data: bytes, old: bytes, new: bytes) -> tuple[bytes, bool]:
    """Change one known launcher assignment, never a generic HOME reference."""
    if data.count(old) == 1 and data.count(new) == 0:
        return data.replace(old, new), True
    if data.count(old) == 0 and data.count(new) == 1:
        return data, False
    raise RuntimeError("Unknown launcher content; refusing to modify")


def service_health() -> dict[str, bool]:
    return {name: subprocess.run(
        ["systemctl", "is-active", "--quiet", name],
        check=False, timeout=8).returncode == 0 for name in SERVICES}


def external_consumers() -> int:
    # Compare absolute path only. Do not print command lines, which may
    # contain secrets. Exclude the calling REA process chain from observation.
    ignored = {os.getpid()}
    pid = os.getppid()
    while pid > 1 and pid not in ignored:
        ignored.add(pid)
        try:
            line = (Path("/proc") / str(pid) / "status").read_text()
            match = re.search(r"(?m)^PPid:\s*(\d+)$", line)
            pid = int(match.group(1)) if match else 0
        except (OSError, ValueError):
            break
    value = os.fsencode(str(ALIAS))
    hits = 0
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or int(proc.name) in ignored:
            continue
        try:
            cmdline = (proc / "cmdline").read_bytes()
            cwd = os.readlink(proc / "cwd")
        except (FileNotFoundError, ProcessLookupError, PermissionError, OSError):
            continue
        if value in cmdline or cwd.startswith(str(ALIAS) + "/"):
            hits += 1
    return hits


def check_service_references() -> None:
    for service in SERVICES:
        response = subprocess.run(
            ["systemctl", "show", service,
             "--property=ExecStart,ExecStartPre,ExecStartPost,WorkingDirectory,Environment,EnvironmentFile",
             "--no-pager"], capture_output=True, text=True, timeout=10)
        if response.returncode or str(ALIAS) in response.stdout:
            raise RuntimeError("Service dependency unresolved: " + service)


def validate_installation(require_alias: bool) -> dict:
    if ROOT.is_symlink() or not ROOT.is_dir() or os.geteuid() != ROOT.stat().st_uid or os.geteuid() == 0:
        raise RuntimeError("Must run as non-root Ferrari project owner")
    if not CURRENT.is_symlink() or not re.fullmatch(r"[0-9a-f]{40}", CURRENT.resolve(strict=True).name):
        raise RuntimeError("Unexpected Ferrari current release")
    if CURRENT.resolve(strict=True).parent != (ROOT / "releases").resolve(strict=True):
        raise RuntimeError("Ferrari current escapes its private releases")
    if not FALLBACK.is_dir() or FALLBACK.is_symlink():
        raise RuntimeError("Old Ferrari fallback release missing")
    if ALIAS.is_symlink():
        if ALIAS.resolve(strict=True) != ROOT:
            raise RuntimeError("Legacy alias does not resolve to Ferrari")
    elif require_alias or ALIAS.exists():
        raise RuntimeError("Legacy alias missing or not a symlink")
    plans = {}
    for path, old, new in PATCHES:
        st = path.lstat()
        if not stat.S_ISREG(st.st_mode) or st.st_uid != os.geteuid() or st.st_nlink != 1:
            raise RuntimeError("Launcher is not an isolated owner-controlled file: " + path.name)
        if path.parent.is_symlink() or st.st_size > 20000:
            raise RuntimeError("Unexpected launcher layout")
        raw = path.read_bytes()
        updated, changed = rewrite_exact(raw, old, new)
        plans[path] = (raw, updated, changed, stat.S_IMODE(st.st_mode))
    return plans


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    fd, tmp = tempfile.mkstemp(prefix=".ferrari-retire-", dir=str(path.parent))
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(tmp, mode)
        subprocess.run(["bash", "-n", tmp], check=True, timeout=10)
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


def real_probes() -> None:
    apk = subprocess.run([str(APKT), "--version"], capture_output=True, text=True, timeout=35)
    if apk.returncode or apk.stdout.strip() != "3.0.3":
        raise RuntimeError("Ferrari-private Apktool 3.0.3 failed")
    valkey = subprocess.run([str(VALKEY), "--version"], capture_output=True, text=True, timeout=25)
    if valkey.returncode or not (valkey.stdout or valkey.stderr).strip():
        raise RuntimeError("Ferrari-private Valkey executable failed")
    doctor = subprocess.run(["python3", "-m", "engine.ferrari", "doctor"],
                            cwd=str(CURRENT), capture_output=True, text=True, timeout=55)
    if doctor.returncode:
        raise RuntimeError("Ferrari doctor failed")


def real_rea_mcp_probe() -> None:
    with tempfile.TemporaryDirectory(prefix=".ferrari-retire-smoke-", dir=str(ROOT / ".runtime")) as td:
        work = Path(td)
        request = work / "request.json"
        response = work / "response"
        request.write_text(json.dumps({
            "version": 1, "id": "ferrari-post-alias-retirement-smoke",
            "kind": "rea-mcp", "mcp_requests": [{"method": "tools/list", "params": {}}]
        }), encoding="utf-8")
        run = subprocess.run(
            ["python3", "-m", "engine.skill_job", "--request", str(request),
             "--output", str(response)],
            cwd=str(CURRENT), capture_output=True, text=True, timeout=135)
        if run.returncode or not (response / "response.zip").is_file():
            raise RuntimeError("Ferrari REA MCP canary failed")
        with zipfile.ZipFile(response / "response.zip") as archive:
            report = json.loads(archive.read("report.json"))
            if report.get("status") != "completed":
                raise RuntimeError("REA MCP canary reported failure")
            if not str(report.get("executor", "")).startswith(str(ROOT / ".runtime/npm/rea/")):
                raise RuntimeError("REA executor escaped private Ferrari root")


def retire() -> dict:
    state = {"scope": "Ferrari launchers and one exact old alias",
             "old_fallback_preserved": FALLBACK.is_dir(), "status": "BLOCKED"}
    plans = validate_installation(require_alias=True)
    before = service_health()
    if not all(before.values()):
        raise RuntimeError("An essential service is inactive")
    check_service_references()
    if external_consumers():
        raise RuntimeError("A running process still names the old alias")
    state["launchers_before"] = {p.name: ("needs_migration" if changed else "canonical")
                                  for p, (_, _, changed, _) in plans.items()}
    edited = []
    alias_removed = False
    try:
        for path, (original, replacement, changed, mode) in plans.items():
            if changed:
                atomic_write(path, replacement, mode)
                edited.append((path, original, mode))
        real_probes()
        if external_consumers():
            raise RuntimeError("A running process requires the old alias")
        # Remove exactly the verified symlink, never its target directory.
        if not ALIAS.is_symlink() or ALIAS.resolve(strict=True) != ROOT:
            raise RuntimeError("Legacy symlink changed during verification")
        ALIAS.unlink()
        alias_removed = True
        real_probes()
        real_rea_mcp_probe()
        if service_health() != before or ROOT.is_symlink() or ALIAS.exists() or ALIAS.is_symlink():
            raise RuntimeError("Ferrari isolation or essential services changed")
        state["status"] = "PASS_LAUNCHERS_CANONICAL_ALIAS_ABSENT"
        state["canonical_launchers"] = [p.name for p, *_ in PATCHES]
        state["fallback_releases_unchanged"] = FALLBACK.is_dir()
        state["services_active"] = len(before)
        state["alias_absent"] = True
    except Exception:
        # Recovery is confined to original bytes and the original exact link.
        if alias_removed and not ALIAS.exists() and not ALIAS.is_symlink():
            ALIAS.symlink_to(ROOT)
        for path, original, mode in reversed(edited):
            atomic_write(path, original, mode)
        raise
    return state


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true",
                        help="Migrate two launchers, remove exact link, test and rollback on failure")
    args = parser.parse_args()
    try:
        if args.apply:
            report = retire()
        else:
            plans = validate_installation(require_alias=False)
            report = {
                "scope": "Ferrari-only read-only preflight", "status": "AUDIT",
                "active_release": CURRENT.resolve().name,
                "alias_present": ALIAS.is_symlink(),
                "old_fallback_preserved": FALLBACK.is_dir(),
                "launchers_needing_migration": [p.name for p, (_, _, needs, _) in plans.items() if needs],
                "essential_services_active": sum(service_health().values()),
                "external_process_consumers": external_consumers(),
            }
        print(json.dumps(report, sort_keys=True))
        return 0
    except Exception as exc:
        print(json.dumps({"status": "BLOCKED_NO_SUCCESS_CLAIM", "error": str(exc)[:180]},
                         sort_keys=True))
        return 4


if __name__ == "__main__":
    raise SystemExit(main())
