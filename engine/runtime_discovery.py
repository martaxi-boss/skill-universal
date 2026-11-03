"""Bounded, read-only discovery of Ferrari-owned Python, npm and containers.

A module/package/container being present is not a working adapter or a
functional certification. Only inspect explicit Ferrari roots, system-wide
package directories, and containers with Ferrari's ownership label.
Never import third-party modules, execute npm packages, or install anything.
"""
from __future__ import annotations

import importlib.util
from itertools import islice
import json
from pathlib import Path
import re
import shutil
import subprocess

FERRARI_HOME = Path.home() / ".local/share/motor-ferrari"
PYTHON_MODULES = {
    "opencv": "cv2", "duckdb": "duckdb", "polars": "polars",
    "streamlit": "streamlit", "gradio": "gradio", "prefect": "prefect",
    "docling": "docling", "faster-whisper": "faster_whisper",
    "ifcopenshell": "ifcopenshell", "bpy": "bpy",
}
NPM_PACKAGES = {
    "ruflo": ("ruflo",),
    "nextjs": ("next",), "vite": ("vite",),
    "tailwind": ("tailwindcss",), "bootstrap": ("bootstrap",),
    "playwright": ("playwright", "@playwright/test"),
    "shadcn": ("shadcn",),
}
CONTAINER_TOOLS = frozenset({
    "penpot", "comfyui", "grafana", "prometheus", "valkey",
    "qdrant", "supabase", "medusa", "saleor", "appwrite",
    "gitea", "homeassistant", "immich", "jellyfin",
})
SYSTEM_NPM_ROOTS = (Path("/usr/local/lib/node_modules"), Path("/usr/lib/node_modules"))
LABEL = "org.motor-ferrari.managed=true"
TOOL_LABEL = "org.motor-ferrari.tool"


def _is_dir(path):
    return path.is_dir() and not path.is_symlink()


def _site_packages(home):
    """Only Ferrari venvs, with fixed nesting and a finite scan budget."""
    roots = [
        home / ".runtime/venv", home / ".runtime/python",
        home / "venv", home / ".venv",
    ]
    parent = home / ".runtime/venvs"
    if _is_dir(parent):
        roots.extend(p for p in islice(parent.iterdir(), 24) if _is_dir(p))
    for root in roots:
        if not _is_dir(root):
            continue
        for lib in ("lib", "lib64"):
            folder = root / lib
            if not _is_dir(folder):
                continue
            for version in islice(folder.glob("python*"), 12):
                candidate = version / "site-packages"
                if _is_dir(candidate):
                    yield candidate


def python_presence(module, home=FERRARI_HOME):
    """Find a known top-level module without importing or calling its code."""
    if not re.fullmatch(r"[a-zA-Z_][a-zA-Z_0-9]*", module):
        return None
    try:
        spec = importlib.util.find_spec(module)
    except (ImportError, ValueError, AttributeError):
        spec = None
    if spec is not None:
        return {
            "scope": "current_python", "location": str(spec.origin or "namespace:" + module),
            "verification": "module_spec_not_imported",
        }
    for site in _site_packages(Path(home)):
        package = site / module
        file = site / (module + ".py")
        compiled = any(islice(site.glob(module + ".*.so"), 1))
        if (package.is_dir() and not package.is_symlink()) or (file.is_file() and not file.is_symlink()) or compiled:
            return {
                "scope": "ferrari_venv", "location": str(package if package.is_dir() else file if file.is_file() else site),
                "verification": "files_present_not_import_tested",
            }
    return None


def _npm_roots(home, system_roots=SYSTEM_NPM_ROOTS):
    base = Path(home) / ".runtime/npm"
    roots = [base / "node_modules"]
    if _is_dir(base):
        roots.extend(p / "node_modules" for p in islice(base.iterdir(), 32) if _is_dir(p))
    roots.extend(Path(p) for p in system_roots)
    return [p for p in roots if _is_dir(p)]


def npm_presence(tool, home=FERRARI_HOME, system_roots=SYSTEM_NPM_ROOTS):
    """Read package.json existence only; never run npm lifecycle hooks."""
    packages = NPM_PACKAGES.get(tool, ())
    base = Path(home) / ".runtime/npm"
    for root in _npm_roots(home, system_roots):
        for name in packages:
            manifest = root.joinpath(*name.split("/")) / "package.json"
            if manifest.is_file() and not manifest.is_symlink():
                return {
                    "scope": "ferrari_npm" if root == base / "node_modules" or base in root.parents else "system_npm",
                    "package": name, "location": str(manifest),
                    "verification": "manifest_present_not_executed",
                }
    return None


def _labels(row):
    value = row.get("Labels", "")
    if isinstance(value, dict):
        return value
    return dict(part.split("=", 1) for part in str(value).split(",") if "=" in part)


def container_discovery():
    """Query ONLY explicitly Ferrari-labelled containers; do not inspect others."""
    runtimes, matched = {}, {}
    for name in ("docker", "podman"):
        binary = shutil.which(name)
        if not binary:
            runtimes[name] = {"cli_found": False, "probe": "no_cli"}
            continue
        args = [
            binary, "ps", "-a", "--filter", "label=" + LABEL,
            "--format", "{{json .}}",
        ]
        try:
            proc = subprocess.run(args, shell=False, capture_output=True,
                                  text=True, timeout=4, check=False)
        except (OSError, subprocess.TimeoutExpired):
            runtimes[name] = {"cli_found": True, "probe": "unavailable"}
            continue
        if proc.returncode != 0:
            runtimes[name] = {"cli_found": True, "probe": "unavailable"}
            continue
        count = 0
        for line in proc.stdout.splitlines()[:100]:
            try:
                row = json.loads(line)
            except (ValueError, TypeError):
                continue
            if not isinstance(row, dict):
                continue
            labels = _labels(row)
            if labels.get("org.motor-ferrari.managed") != "true":
                continue
            count += 1
            tool = labels.get(TOOL_LABEL)
            if tool not in CONTAINER_TOOLS:
                continue
            state = str(row.get("State") or row.get("Status") or "").lower()
            matched.setdefault(tool, []).append({
                "runtime": name,
                "state": "running" if state == "running" or state.startswith("up") else "present_not_running",
                "verification": "ferrari_labelled_container_only",
            })
        runtimes[name] = {
            "cli_found": True, "probe": "read_only_success",
            "ferrari_managed_containers": count,
        }
    return {"runtimes": runtimes, "tools": matched,
            "scope": "Ferrari-labelled containers only; never scans other projects or all images"}


def browser_discovery(home=FERRARI_HOME):
    """Read-only browser probe. No browser launched or cross-project scan.

    System command paths and explicitly Ferrari-owned Playwright caches are
    *presence evidence only*, not proof that Chromium can render a page.
    """
    names = ("chromium", "chromium-browser", "google-chrome", "firefox", "firefox-esr")
    system = {}
    for name in names:
        candidate = shutil.which(name)
        if candidate:
            system[name] = {"path": candidate, "verification": "binary_path_only_not_launched"}
    root = Path(home) / ".runtime/browsers"
    owned = []
    if _is_dir(root):
        for folder in islice(root.iterdir(), 40):
            if not _is_dir(folder):
                continue
            if not re.fullmatch(r"(chromium|chromium_headless_shell|firefox)-[0-9]+", folder.name):
                continue
            for relative in ("chrome-linux/headless_shell", "chrome-linux/chrome",
                             "chrome-linux64/chrome",
                             "chrome-headless-shell-linux64/chrome-headless-shell"):
                # Do not traverse outside the Ferrari browser cache.
                candidate = folder / relative
                if candidate.is_file() and not candidate.is_symlink():
                    owned.append({"path": str(candidate),
                                  "verification": "ferrari_cache_file_only_not_launched"})
                    break
    return {
        "system_browser_executables": system,
        "ferrari_browser_cache": owned,
        "ferrari_cache_root": str(root),
        "scope": "read-only PATH and Ferrari-owned browser cache, no installation or execution",
    }


def discover(home=FERRARI_HOME, system_npm_roots=SYSTEM_NPM_ROOTS):
    python = {}
    npm = {}
    for tool, module in PYTHON_MODULES.items():
        evidence = python_presence(module, home=home)
        if evidence:
            python[tool] = {"module": module, **evidence}
    for tool in NPM_PACKAGES:
        evidence = npm_presence(tool, home=home, system_roots=system_npm_roots)
        if evidence:
            npm[tool] = evidence
    return {
        "python": {"tools": python, "detected": len(python),
                   "scope": "current interpreter and Ferrari-owned virtual environments"},
        "npm": {"tools": npm, "detected": len(npm),
                "scope": "Ferrari-owned and system-global node_modules only"},
        "containers": container_discovery(),
        "browsers": browser_discovery(home=home),
        "note": "Read-only presence evidence, not functionality, certification or permission to install.",
    }
