#!/usr/bin/env python3
"""Phase 6 Ferrari-only, reversible venv Python isolation (no apt, no global writes).

Two explicitly authorized modes: --preview and --apply. Every affected file
is inside /srv/projects/skill-universal/.runtime/venvs. The active release
and certified fallback may never change. Only the known Ubuntu Python 3.12
venv symlinks may be migrated. Any failed postcheck restores the originals.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
RELEASE = "146145d5ada9c13e368df18727e4dbf4f5807664"
FALLBACK = "40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
PRIVATE = ROOT / "runtimes/python3.12/bin/python3.12"
ENVS = (
    ".runtime/venvs/bim",
    ".runtime/venvs/extended/prefect",
    ".runtime/venvs/extended/streamlit",
    ".runtime/venvs/extended/comfyui",
    ".runtime/venvs/extended/gradio",
    ".runtime/venvs/extended/faster-whisper",
    ".runtime/venvs/extended/docling",
)
BINARIES = ("python", "python3", "python3.12")
SYSTEM = "/usr/bin/python3.12"
BACKUP = ROOT / ".runtime/phase6-python-venv-migration-20261105.json"


def private(path: Path) -> bool:
    try:
        return path.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
    except (OSError, RuntimeError, ValueError):
        return False


def atomic_contents(path: Path, content: str):
    fd, name = tempfile.mkstemp(prefix=".phase6.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, 0o644)
        os.replace(name, path)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


def atomic_link(path: Path, target: str):
    name = path.with_name(".phase6-temp-" + path.name)
    if os.path.lexists(name):
        raise RuntimeError("Unexpected pre-existing temp symlink")
    os.symlink(target, name)
    try:
        os.replace(name, path)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


def snapshot():
    if ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("Ferrari root is not a real directory")
    if not (ROOT / "current").is_symlink():
        raise RuntimeError("Ferrari current missing")
    if (ROOT / "current").resolve(strict=True) != ROOT / "releases" / RELEASE:
        raise RuntimeError("Ferrari active release changed")
    if not (ROOT / "releases" / FALLBACK / "engine/ferrari.py").is_file():
        raise RuntimeError("Certified fallback release missing")
    if (PRIVATE.is_symlink() or not PRIVATE.is_file()
            or not private(PRIVATE) or not os.access(PRIVATE, os.X_OK)):
        raise RuntimeError("Ferrari private Python unavailable")
    if (ROOT / ".runtime/venvs").is_symlink():
        raise RuntimeError("Ferrari virtualenv root is symlinked")
    envs, count_system = {}, 0
    for relative in ENVS:
        folder = ROOT / relative
        cfg = folder / "pyvenv.cfg"
        if (folder.is_symlink() or not folder.is_dir() or not private(folder)
                or cfg.is_symlink() or not cfg.is_file()):
            raise RuntimeError("Invalid Ferrari-owned venv: " + relative)
        cfg_data = cfg.read_text(encoding="utf-8")
        if len(cfg_data) > 16000:
            raise RuntimeError("Unexpected venv config size")
        if re.search(r"(?im)^\s*include-system-site-packages\s*=\s*true\s*$", cfg_data):
            raise RuntimeError("A Ferrari venv imports global site packages")
        links = {}
        for name in BINARIES:
            link = folder / "bin" / name
            if not link.is_symlink():
                raise RuntimeError("Expected a Python venv symlink: " + relative)
            real = link.resolve(strict=True)
            if real == PRIVATE.resolve(strict=True):
                origin = "ferrari_private"
            elif str(real) == SYSTEM:
                origin = "ubuntu_global_python"
                count_system += 1
            else:
                raise RuntimeError("Unexpected interpreter outside Ferrari: " + relative)
            links[name] = {"old_link": os.readlink(link), "origin": origin}
        envs[relative] = {"config": cfg_data, "links": links}
    return envs, count_system


def adjusted_config(original: str) -> str:
    changed = []
    for line in original.splitlines(keepends=True):
        if "=" not in line:
            changed.append(line)
            continue
        key, value = line.split("=", 1)
        clean = key.strip().lower()
        if clean == "home":
            line = key + "= " + str(PRIVATE.parent) + "\n"
        elif clean == "executable":
            line = key + "= " + str(PRIVATE) + "\n"
        elif clean == "command":
            line = line.replace(SYSTEM, str(PRIVATE))
        changed.append(line)
    return "".join(changed)


def probe_environment(folder: Path):
    code = ("import json,sys;"
            "print(json.dumps({'prefix':sys.prefix,'base':sys.base_prefix,"
            "'executable':sys.executable}))")
    result = subprocess.run(
        [str(folder / "bin/python3.12"), "-I", "-B", "-c", code],
        capture_output=True, text=True, timeout=18, check=False,
        env={
            "PATH": str(PRIVATE.parent) + ":/usr/bin:/bin",
            "LD_LIBRARY_PATH": str(ROOT / "runtimes/python3.12/lib"),
            "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1",
            "HOME": str(ROOT / ".runtime"), "LC_ALL": "C",
        })
    if result.returncode:
        raise RuntimeError("Private venv interpreter does not start: " + folder.name)
    data = json.loads(result.stdout.strip())
    if (Path(data["prefix"]).resolve(strict=True) != folder.resolve(strict=True)
            or not Path(data["base"]).resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
            or not Path(data["executable"]).resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))):
        raise RuntimeError("Python venv still depends on another project or system Python: " + folder.name)
    return {"prefix_private": True, "base_private": True, "executable_private": True}


def no_running_venv_process():
    markers = tuple(str(ROOT / name) for name in ENVS)
    for process in Path("/proc").iterdir():
        if not process.name.isdecimal() or process.name == str(os.getpid()):
            continue
        try:
            cwd = os.readlink(process / "cwd")
            exe = os.readlink(process / "exe")
            cmd = (process / "cmdline").read_bytes()[:12000].decode("utf-8", "replace")
        except (OSError, PermissionError):
            continue
        if any(mark in cwd or mark in exe or mark in cmd for mark in markers):
            raise RuntimeError("A Ferrari Python environment is in use; no migration")


def do(mode: str):
    if mode not in ("--preview", "--apply"):
        raise RuntimeError("Expected --preview or --apply")
    if os.geteuid() == 0:
        raise RuntimeError("Do not operate Ferrari as root")
    envs, count = snapshot()
    report = {
        "schema": 1, "phase": 6, "mode": mode.removeprefix("--"),
        "release": RELEASE, "fallback": FALLBACK, "project": str(ROOT),
        "venvs_checked": len(envs), "interpreter_links_checked": len(envs) * 3,
        "global_python_symlinks_before": count, "private_python": str(PRIVATE),
        "changes_applied": 0, "rollback_used": False,
        "other_projects_touched": False, "global_packages_removed": 0,
        "result": "preview_only",
    }
    if mode == "--preview":
        return report
    if BACKUP.exists() or BACKUP.is_symlink():
        raise RuntimeError("Historical migration marker exists; no repeated destructive migration")
    no_running_venv_process()
    backup = {
        "schema": 1, "phase": 6, "previous": {
            rel: {"config": d["config"],
                  "links": {k: item["old_link"] for k,item in d["links"].items()}}
            for rel,d in envs.items(),
        },
    }
    # Store rollback metadata inside Ferrari before touching any links.
    atomic_contents(BACKUP, json.dumps(backup, indent=2, sort_keys=True))
    changed = []
    try:
        for relative, entry in envs.items():
            folder = ROOT / relative
            for name in BINARIES:
                link = folder / "bin" / name
                target = os.path.relpath(PRIVATE, link.parent)
                if entry["links"][name]["origin"] == "ubuntu_global_python":
                    atomic_link(link, target)
                    changed.append(("link", link, entry["links"][name]["old_link"]))
            cfg = folder / "pyvenv.cfg"
            new_cfg = adjusted_config(entry["config"])
            if new_cfg != entry["config"]:
                atomic_contents(cfg, new_cfg)
                changed.append(("config", cfg, entry["config"]))
        post, after = snapshot()
        if after:
            raise RuntimeError("System-global Python venv symlink remains")
        report["python_venv_tests"] = {
            rel: probe_environment(ROOT / rel) for rel in ENVS
        }
        if (ROOT / "current").resolve(strict=True) != ROOT / "releases" / RELEASE:
            raise RuntimeError("Production symlink changed during venv migration")
        report["global_python_symlinks_after"] = after
        report["changes_applied"] = len(changed)
        report["result"] = "private_python_migrated"
        return report
    except BaseException:
        for kind, path, old in reversed(changed):
            if kind == "link":
                atomic_link(path, old)
            else:
                atomic_contents(path, old)
        report["rollback_used"] = True
        BACKUP.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    try:
        output = do(sys.argv[1] if len(sys.argv) == 2 else "")
        print(json.dumps(output, ensure_ascii=False, sort_keys=True))
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired,
            json.JSONDecodeError) as exc:
        print("FERRARI_PHASE6_VENV_MIGRATION_BLOCKED=" + type(exc).__name__ +
              ":" + str(exc)[:140], file=sys.stderr)
        sys.exit(2)
