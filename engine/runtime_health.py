"""Bounded execution checks for the three Ferrari-owned shared runtimes.

Presence is not execution.  Run tiny, non-network, no-shell probes through
absolute paths from the ONE Ferrari catalog.  Do not run user-supplied code,
install dependencies or fall back to system or other project executables.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import tempfile

# Only exact Ferrari catalog dependency IDs and fixed command arguments.
COMMANDS = {
    "python-3.12": ("-I", "-c",
        "import ssl,sqlite3,json,hashlib,sys;print('FERRARI_PYTHON_READY:'+sys.version.split()[0])"),
    "node-22": ("-e",
        "const crypto=require('node:crypto');const fs=require('node:fs');"
        "console.log('FERRARI_NODE_READY:'+process.versions.node)"),
    "java-25": ("-version",),
}
EXPECTED = {
    "python-3.12": re.compile(r"FERRARI_PYTHON_READY:3\.12\.[0-9]+"),
    "node-22": re.compile(r"FERRARI_NODE_READY:22\.23\.4"),
    "java-25": re.compile(r"(?:java|openjdk) version [\x22']?25\.0\.5|openjdk 25\.0\.5"),
}


def probe_dependency(entry, home):
    """Return independent technical evidence, never a blanket ABI certificate."""
    name = entry["id"]
    if name not in COMMANDS:
        raise ValueError("Unknown Ferrari runtime probe")
    candidate = Path(entry["path"])
    root = Path(home)
    base = {"id": name, "version_expected": entry["version"],
            "path": str(candidate), "executed": False,
            "runtime_smoke_pass": False, "compatibility_certified": False,
            "status": "unavailable"}
    try:
        own = root.resolve(strict=True)
        binary = candidate.resolve(strict=True)
        if (not candidate.is_file() or not os.access(candidate, os.X_OK)
                or not binary.is_relative_to(own)
                or not candidate.is_relative_to(root)):
            return base
        # Bounded, fixed commands: no arbitrary tool arguments and no shell.
        environment = os.environ.copy()
        for unsafe in ("PYTHONPATH", "PYTHONHOME", "NODE_OPTIONS",
                       "JAVA_TOOL_OPTIONS", "_JAVA_OPTIONS", "JDK_JAVA_OPTIONS",
                       "LD_PRELOAD", "LD_LIBRARY_PATH"):
            environment.pop(unsafe, None)
        result = subprocess.run([str(candidate), *COMMANDS[name]],
                                shell=False, capture_output=True, text=True,
                                errors="replace", timeout=8, check=False,
                                cwd=str(root), env=environment)
        observed = (result.stdout + "\n" + result.stderr)[:4096]
        matched = result.returncode == 0 and bool(EXPECTED[name].search(observed))
        base.update({"executed": True,
                     "runtime_smoke_pass": matched,
                     "status": "runtime_smoke_pass" if matched else "runtime_smoke_failed",
                     "exit_code": result.returncode,
                     "probe": "private_runtime_version_and_minimal_stdlib"})
    except (OSError, ValueError, subprocess.TimeoutExpired):
        base["status"] = "probe_unavailable"
    return base


# Explicitly opt-in, fixed, non-network startup checks for Ferrari support
# programs.  These do NOT create a new adapter or claim product functionality.
PROGRAM_COMMANDS = {
    "ytdlp": ("--version",),
    "qgis": ("--version",),
    "godot": ("--headless", "--version"),
    "prometheus": ("--version",),
    "valkey": ("--version",),
}
PROGRAM_EXPECTED = {
    "ytdlp": re.compile(r"[0-9]{4}\.[0-9]{1,2}\.[0-9]{1,2}"),
    "qgis": re.compile(r"QGIS|[0-9]+\.[0-9]+\.[0-9]+", re.I),
    "godot": re.compile(r"4\.[0-9]+", re.I),
    "prometheus": re.compile(r"prometheus", re.I),
    # The privately installed Valkey 7.2 server prints "Server v=7.2.13".
    # --version is exit-0 and non-daemon; require the expected upstream 7.2 branch.
    "valkey": re.compile(r"(?:valkey\s+)?Server\s+v=7\.2\.[0-9]+\b", re.I),
}


def probe_support_program(tool, executable, home):
    """Launch one trusted tool with hardcoded --version options only.

    The separate Ferrari-owned temporary HOME is removed after execution.
    A smoke PASS is never a claim of an integrated Ferrari function.
    """
    if tool not in PROGRAM_COMMANDS:
        raise ValueError("Unsupported Ferrari support-program probe")
    out={"tool":tool,"executable":executable,"status":"not_detected",
         "executed":False,"startup_smoke_pass":False,
         "integrated_action_certified":False}
    if executable is None:
        return out
    root=Path(home)
    path=Path(executable)
    try:
        if (not path.is_file() or not os.access(path,os.X_OK)
                or not path.resolve(strict=True).is_relative_to(root.resolve(strict=True))):
            return out
        state=root/".runtime"
        if not state.is_dir() or state.is_symlink():
            out["status"]="private_runtime_directory_missing"
            return out
        with tempfile.TemporaryDirectory(prefix=".version-probe-",dir=state) as td:
            tmp=Path(td)
            for relative in ("cache", "config", "data", "run"):
                (tmp/relative).mkdir(mode=0o700)
            env=os.environ.copy()
            for key in ("PYTHONPATH","PYTHONHOME","NODE_OPTIONS",
                        "LD_PRELOAD","LD_LIBRARY_PATH"):
                env.pop(key,None)
            env.update({"HOME":td,"TMPDIR":td,"XDG_CACHE_HOME":str(tmp/"cache"),
                        "XDG_CONFIG_HOME":str(tmp/"config"),
                        "XDG_DATA_HOME":str(tmp/"data"),
                        "XDG_RUNTIME_DIR":str(tmp/"run"),
                        "QT_QPA_PLATFORM":"offscreen"})
            completed=subprocess.run([str(path),*PROGRAM_COMMANDS[tool]],
                capture_output=True,text=True,errors="replace",
                timeout=12,shell=False,cwd=td,env=env,check=False)
            observed=(completed.stdout+"\n"+completed.stderr)[:2048]
            success=completed.returncode==0 and bool(PROGRAM_EXPECTED[tool].search(observed))
            out.update({"status":"startup_smoke_pass" if success else "startup_smoke_failed",
                        "executed":True,"startup_smoke_pass":success,
                        "exit_code":completed.returncode,
                        "observed_version_summary":observed.splitlines()[0][:140] if observed else "",
                        "probe":"fixed_offline_version_only"})
    except (OSError,ValueError,subprocess.TimeoutExpired):
        out["status"]="probe_unavailable"
    return out
