"""Ferrari-private OpenPencil HTML import and web design exports.

This is the existing web-template operation's optional HTML-input mode.
The GitHub transport contract and its pinned validator remain unchanged.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess

FERRARI_HOME = Path("/srv/projects/skill-universal")
NODE = FERRARI_HOME / "runtimes/node-22.23.4/bin/node"
PACKAGE_ROOT = FERRARI_HOME / ".runtime/npm/openpencil"
CLI = PACKAGE_ROOT / "node_modules/@open-pencil/cli/bin/openpencil.js"
MANIFEST = PACKAGE_ROOT / "node_modules/@open-pencil/cli/package.json"
VERSION = "0.16.0"
MAX_HTML = 600_000
MAX_EXPORT = 15_000_000


def _private_runtime() -> tuple[str, str]:
    root = FERRARI_HOME.resolve(strict=True)
    for path in (NODE, CLI, MANIFEST):
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("Ferrari-private OpenPencil executable/manifest missing: " + path.name)
        if not path.resolve(strict=True).is_relative_to(root):
            raise RuntimeError("OpenPencil dependency escapes Ferrari project")
    version = json.loads(MANIFEST.read_text(encoding="utf-8")).get("version")
    if version != VERSION:
        raise RuntimeError("OpenPencil version mismatch; expected " + VERSION)
    if not os.access(NODE, os.X_OK):
        raise RuntimeError("Ferrari-private Node is not executable")
    return str(NODE), str(CLI)


def _source_html(source: str | Path) -> Path:
    path = Path(source)
    if path.is_symlink() or not path.is_file() or path.suffix.lower() not in {".html", ".htm"}:
        raise ValueError("OpenPencil requires one regular HTML input file")
    if not 1 <= path.stat().st_size <= MAX_HTML:
        raise ValueError("OpenPencil HTML input is outside the 600KB safety limit")
    html = path.read_text(encoding="utf-8")
    if not re.search(r"<html\b|<!doctype\s+html\b", html, flags=re.I):
        raise ValueError("OpenPencil requires a complete HTML document")
    # The bridge receives public synthetic HTML; never allow remote resource
    # loads, active scripting or local-file access from that public request.
    if re.search(r"<\s*(?:script|iframe|object|embed|link|base|meta\s+http-equiv)\b", html, flags=re.I):
        raise ValueError("Active or external HTML elements are not supported")
    if re.search(r'''\b(?:src|srcset|href|xlink:href|action|formaction|poster|background)\s*=''',
                 html,flags=re.I):
        raise ValueError("Link or resource attributes are forbidden in OpenPencil import")
    if re.search(r'''@import\b|url\s*\(''', html, flags=re.I):
        raise ValueError("External or local CSS resources are forbidden in OpenPencil input")
    return path.resolve(strict=True)


def convert_html(source: str | Path, folder: str | Path) -> tuple[str,list[Path]]:
    """Import HTML to .fig and export SVG/standalone HTML with isolated state."""
    source = _source_html(source)
    node, cli = _private_runtime()
    dest = Path(folder).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    if dest.is_symlink() or any((dest/name).exists() or (dest/name).is_symlink()
                               for name in ("design.fig","design.svg","design.html","design-info.json")):
        raise FileExistsError("Ferrari OpenPencil output path already exists")
    state = dest / ".openpencil-state"
    state.mkdir(mode=0o700)
    for name in ("home","tmp","cache","config","data"):
        (state / name).mkdir(mode=0o700)
    env = os.environ.copy()
    env.update({
        "HOME":str(state/"home"),
        "TMPDIR":str(state/"tmp"), "TMP":str(state/"tmp"),
        "XDG_CACHE_HOME":str(state/"cache"),
        "XDG_CONFIG_HOME":str(state/"config"),
        "XDG_DATA_HOME":str(state/"data"),
        "PATH":str(NODE.parent)+":/usr/bin:/bin",
        "NODE_OPTIONS":"--no-warnings",
        "CI":"1",
    })

    def invoke(args: list[str], *, info: Path | None = None) -> None:
        process = subprocess.run(
            [node, cli, *args], cwd=str(dest), env=env, shell=False,
            capture_output=True, text=True, timeout=180, check=False,
        )
        if process.returncode:
            raise RuntimeError("Private OpenPencil failed: " + process.stderr[:500])
        if info is not None:
            if len(process.stdout)>60_000:
                raise RuntimeError("OpenPencil information output too large")
            try:
                payload = json.loads(process.stdout)
            except json.JSONDecodeError as exc:
                raise RuntimeError("OpenPencil returned invalid JSON metadata") from exc
            info.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding="utf-8")

    fig=dest/"design.fig"
    svg=dest/"design.svg"
    html=dest/"design.html"
    info=dest/"design-info.json"
    invoke(["import", str(source), "-o",str(fig), "--json"])
    invoke(["info",str(fig),"--json"],info=info)
    invoke(["export",str(fig),"-f","svg","-o",str(svg)])
    invoke(["export",str(fig),"-f","html","--html","standalone","-o",str(html)])
    outputs=[fig,svg,html,info]
    for path in outputs:
        if path.is_symlink() or not path.is_file() or not 1<=path.stat().st_size<=MAX_EXPORT:
            raise RuntimeError("Ferrari OpenPencil did not produce a valid artifact: "+path.name)
        if not path.resolve(strict=True).is_relative_to(dest):
            raise RuntimeError("OpenPencil output escapes Ferrari job")
    if "<svg" not in svg.read_text(encoding="utf-8").lower():
        raise RuntimeError("OpenPencil SVG content invalid")
    if "<html" not in html.read_text(encoding="utf-8").lower():
        raise RuntimeError("OpenPencil HTML export invalid")
    return node, outputs
