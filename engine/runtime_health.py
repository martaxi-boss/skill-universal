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
    "python-3.12": re.compile(r"FERRARI_PYTHON_READY:3\\.12\\.[0-9]+"),
    "node-22": re.compile(r"FERRARI_NODE_READY:22\\.23\\.4"),
    "java-25": re.compile(r"(?:java|openjdk) version [\\x22']?25\\.0\\.5|openjdk 25\\.0\\.5"),
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
        observed = (result.stdout + "\\n" + result.stderr)[:4096]
        matched = result.returncode == 0 and bool(EXPECTED[name].search(observed))
        base.update({"executed": True,
                     "runtime_smoke_pass": matched,
                     "status": "runtime_smoke_pass" if matched else "runtime_smoke_failed",
                     "exit_code": result.returncode,
                     "probe": "private_runtime_version_and_minimal_stdlib"})
    except (OSError, ValueError, subprocess.TimeoutExpired):
        base["status"] = "probe_unavailable"
    return base
