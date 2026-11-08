"""Private, offline Prometheus rule validation through the existing Ferrari catalog.

Uses the promtool executable from the already installed private Prometheus
package. Never starts Prometheus, connects to a network, evaluates metrics
against remote services or accepts user-supplied commands.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

HOME = Path("/srv/projects/skill-universal")
PROMTOOL_RELATIVE = Path("tools/ferrari-services/prometheus/usr/bin/promtool")
MAX_RULE_BYTES = 64_000


def _owned(path: Path, root: Path, *, file: bool = False) -> Path:
    if path.is_symlink() or (file and not path.is_file()):
        raise ValueError("Unsafe or missing private Ferrari path")
    resolved = path.resolve(strict=file)
    if not resolved.is_relative_to(root):
        raise ValueError("Ferrari path escapes its project")
    return resolved


def check_rules(source: Path, folder: Path):
    """Check an uploaded .yml/.yaml rules file and return genuine tool evidence."""
    if not HOME.is_dir() or HOME.is_symlink():
        raise RuntimeError("Ferrari private root unavailable")
    root = HOME.resolve(strict=True)
    source = Path(source)
    if source.suffix.lower() not in {".yml", ".yaml"}:
        raise ValueError("Prometheus rule file must be .yml or .yaml")
    source = _owned(source, root, file=True)
    if not 32 <= source.stat().st_size <= MAX_RULE_BYTES:
        raise ValueError("Prometheus rule file outside safe size limit")
    data = source.read_bytes()
    if b"\x00" in data:
        raise ValueError("Binary rules are forbidden")
    try:
        data.decode("utf-8")
    except UnicodeError as exc:
        raise ValueError("Prometheus rules must be UTF-8") from exc

    tool = _owned(HOME / PROMTOOL_RELATIVE, root, file=True)
    if not os.access(tool, os.X_OK):
        raise RuntimeError("Private Ferrari promtool is not executable")
    runtime = HOME / ".runtime"
    if runtime.is_symlink() or not runtime.is_dir():
        raise RuntimeError("Ferrari private runtime missing")
    _owned(runtime, root)
    folder = Path(folder)
    if folder.is_symlink() or not folder.resolve().is_relative_to(root):
        raise ValueError("Prometheus artifacts must be inside Ferrari")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    output = folder / "promtool-check.txt"
    report = folder / "prometheus-rules-report.json"
    if any(p.exists() or p.is_symlink() for p in (output, report)):
        raise FileExistsError("Existing Prometheus result would be overwritten")

    with tempfile.TemporaryDirectory(prefix=".promtool-check-", dir=runtime) as temp:
        home = Path(temp)
        env = {
            "HOME": str(home), "TMPDIR": str(home), "XDG_CACHE_HOME": str(home),
            "XDG_CONFIG_HOME": str(home), "XDG_DATA_HOME": str(home),
            "PATH": str(tool.parent), "LANG": "C.UTF-8", "GOMAXPROCS": "2",
        }
        try:
            call = subprocess.run(
                [str(tool), "check", "rules", str(source)], shell=False,
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                errors="replace", timeout=25, cwd=temp, env=env,
                check=False, start_new_session=True,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Private promtool rule validation timed out") from exc
    observed = (call.stdout + "\n" + call.stderr)[:6000]
    matches = re.findall(r"\b([0-9]+)\s+rules?\s+found\b", observed, re.I)
    if call.returncode != 0 or not re.search(r"\bSUCCESS\b", observed, re.I) or not matches:
        raise RuntimeError("Prometheus private rule validation failed: " + observed[-500:])
    count = sum(int(x) for x in matches)
    if count < 1:
        raise RuntimeError("No Prometheus recording/alerting rules were validated")

    output.write_text(observed.strip() + "\n", encoding="utf-8")
    record = {
        "status": "completed", "program": "prometheus",
        "executor": str(tool), "operation": "promtool_check_rules",
        "rules_validated": count,
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "evidence_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "offline": True, "daemon_started": False,
        "network_used": False, "metrics_ingestion_certified": False,
        "monitoring_service_certified": False,
        "scope": "Prometheus syntax and expression rule checks only",
    }
    report.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8")
    return str(tool) + ":check-rules", [output, report]
