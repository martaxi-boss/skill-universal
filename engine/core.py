"""Small auditable routing engine for independent Linux toolkit.

Only specifically implemented task executors run; no LLM prompt becomes a shell
command. Optional tools are detected at runtime and never silently fabricated.
"""
from __future__ import annotations

import hashlib
import html
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import unicodedata
import zipfile
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent.parent


def load_json(filename: str) -> dict:
    with (ROOT / "engine" / filename).open(encoding="utf-8") as f:
        return json.load(f)


def installed(tool: dict) -> bool:
    """Discover Ferrari-owned applications; never count a global PATH binary."""
    if tool.get("cost") == "built-in":
        return True
    name = str(tool.get("id", "")).lower()
    executable = tool.get("bin")
    if not executable:
        return False
    from engine import tool_runtime
    # Application runtimes are owned by Ferrari, not system Python/Node/Java.
    runtimes = {
        "python": ("runtimes/python3.12/bin/python3.12",),
        "node": ("runtimes/node-22.23.4/bin/node",),
        "java": ("runtimes/jdk-25.0.5_8/bin/java",),
    }
    for rel in runtimes.get(name, ()):
        candidate = tool_runtime.HOME / rel
        if (candidate.is_file() and os.access(candidate, os.X_OK)
                and candidate.resolve().is_relative_to(tool_runtime.HOME.resolve())):
            return True
    return tool_runtime.executable(name, executable) is not None


def inventory(category: str | None = None) -> list[dict]:
    items = load_json("catalog.json")["tools"]
    result = []
    for t in items:
        if category and t["category"] != category:
            continue
        result.append({**t, "installed": installed(t)})
    return result


def environment() -> dict:
    items = inventory()
    return {
        "utc": datetime.now(timezone.utc).isoformat(),
        "system": platform.system(),
        "release": platform.release(),
        "machine": platform.machine(),
        "distribution": get_linux_distro(),
        "python": platform.python_version(),
        "tool_count": len(items),
        "installed_count": sum(t["installed"] for t in items),
        "missing_count": sum(not t["installed"] for t in items),
        "installed": [t["id"] for t in items if t["installed"]],
        "unavailable": [t["id"] for t in items if not t["installed"]],
        "health": "inventory_only_not_full_certification",
    }


def get_linux_distro() -> str:
    try:
        data = Path("/etc/os-release").read_text(encoding="utf-8")
        match = re.search(r'^PRETTY_NAME="?([^"\n]+)', data, re.MULTILINE)
        return match.group(1) if match else "unknown"
    except OSError:
        return "unknown"


def normalize(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", s.casefold()) if not unicodedata.combining(c))


ROUTES = {
    "website": {
        "terms": ["site", "website", "webapp", "pagina", "landing page", "loja online", "frontend", "html", "layout", "barbearia", "portal"],
        "category": "web", "preferred": ["html-templates", "node", "vite", "astro", "tailwindcss", "shadcn-ui"],
        "executor": "website_static_template",
    },
    "creative": {
        "terms": ["imagem", "fotografia", "foto", "criativo", "cartaz", "banner", "anuncio", "flyer", "design", "poster", "logo", "svg"],
        "category": "media", "preferred": ["svg", "imagemagick", "inkscape", "gimp", "ffmpeg"],
        "executor": "creative_svg_template",
    },
    "reverse": {
        "terms": ["descompilar", "decompilar", "engenharia reversa", "reverse", "apk", "binario", "executavel", "firmware", "analisar aplicacao", "inspecionar app"],
        "category": "reverse", "preferred": ["file", "REA", "apktool", "jadx", "ghidra", "binwalk", "readelf", "strings"],
        "executor": "static_file_inspection",
    },
    "mobile": {
        "terms": ["android", "adb", "emulador", "compilar apk", "assinatura apk", "apksigner"],
        "category": "mobile", "preferred": ["adb", "aapt", "apksigner", "zipalign", "java"],
        "executor": None,
    },
    "documents": {
        "terms": ["pdf", "docx", "documento", "excel", "ocr", "relatorio", "apresentacao"],
        "category": "docs", "preferred": ["pandoc", "libreoffice", "pdftotext", "tesseract"],
        "executor": None,
    },
    "data": {
        "terms": ["base de dados", "postgresql", "sql", "sqlite", "redis", "dados", "analytics"],
        "category": "data", "preferred": ["sqlite", "postgres-client", "redis-client"],
        "executor": None,
    },
    "dev": {
        "terms": ["programar", "codigo", "desenvolver", "debug", "testes", "python", "javascript", "api", "git", "docker"],
        "category": "dev", "preferred": ["git", "python", "node", "gcc", "clang", "docker", "ripgrep"],
        "executor": None,
    },
}


def plan(request: str) -> dict:
    if not request.strip():
        raise ValueError("Pedido vazio")
    q = normalize(request)
    ranks = {route: sum(3 if (" " in word and word in q) else 1 for word in cfg["terms"] if word in q) for route, cfg in ROUTES.items()}
    # Reverse engineering takes precedence if a user asks to inspect an APK;
    # ordinary website generation takes precedence for web layouts.
    category = max(ranks, key=lambda k: (ranks[k], int(k == "reverse")))
    if ranks[category] == 0:
        category = "dev"
    cfg = ROUTES[category]
    tool_index = {t["id"]: t for t in inventory()}
    ranked = [tool_index[x] for x in cfg["preferred"] if x in tool_index]
    primary = next((t for t in ranked if t["installed"]), None)
    return {
        "request": request,
        "route": category,
        "category": cfg["category"],
        "executor": cfg["executor"],
        "execution_available": bool(cfg["executor"]),
        "preferred_tool": primary["id"] if primary else None,
        "available_tools": [t["id"] for t in ranked if t["installed"]],
        "missing_tools": [t["id"] for t in ranked if not t["installed"]],
        "explanation": "A rota local implementada e uma capacidade limitada; nao equivale a todas as funcoes dos programas do catalogo.",
    }


def providers() -> list[dict]:
    out = []
    for p in load_json("providers.json")["providers"]:
        key = p.get("env")
        # Cloud-provider configuration remains separate from executable
        # availability; a global PATH command cannot satisfy a local provider.
        if key:
            ready = bool(os.environ.get(key))
        elif p["kind"] == "local":
            from engine import tool_runtime
            binary = p.get("binary")
            ready = (binary is None or
                     tool_runtime.executable(str(p.get("id", "")).lower(), binary) is not None)
        else:
            ready = False
        out.append({**p, "configured": ready, "availability_verified": False if p["kind"] == "cloud" else ready})
    return out


def _write_text(path: Path, content: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


def _template(name: str) -> str:
    return (ROOT / "templates" / name).read_text(encoding="utf-8")


def _safe_title(title: str) -> str:
    clean = " ".join(title.split()).strip()
    if not clean or len(clean) > 90:
        raise ValueError("Titulo deve ter entre 1 e 90 caracteres")
    return html.escape(clean, quote=True)


def create_website(output: Path, title: str) -> list[Path]:
    label = _safe_title(title)
    source = _template("website.html")
    return [_write_text(output / "site" / "index.html", source.replace("{{TITLE}}", label))]


def create_creative(output: Path, title: str) -> list[Path]:
    label = _safe_title(title)
    # Preserves SVG validity: title is escaped as XML, length bounded above.
    source = _template("creative.svg")
    return [_write_text(output / "creative" / "poster.svg", source.replace("{{TITLE}}", label))]


def _first_output(argv: list[str]) -> str:
    try:
        p = subprocess.run(argv, check=False, capture_output=True, text=True, timeout=12)
        return (p.stdout or p.stderr)[:3000].strip()
    except (OSError, subprocess.TimeoutExpired) as exc:
        return f"tool_unavailable:{exc.__class__.__name__}"


def inspect_artifact(target: Path, output: Path) -> list[Path]:
    if not target.is_file():
        raise FileNotFoundError(f"Ficheiro nao encontrado: {target}")
    if target.stat().st_size > 512 * 1024 * 1024:
        raise ValueError("Protótipo limita inspeção a ficheiros de 512 MiB")
    h = hashlib.sha256()
    with target.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    from engine import tool_runtime
    private_file = tool_runtime.executable("file", "file")
    private_readelf = tool_runtime.executable("readelf", "readelf")
    result = {
        "target": str(target.resolve()),
        "size_bytes": target.stat().st_size,
        "sha256": h.hexdigest(),
        "file": _first_output([private_file, "-b", str(target)]) if private_file else "private_executor_unavailable",
        "zip_entries": [],
        "readelf_header": None,
        "warning": "Analise estatica basica apenas; nao foi executado REA, Ghidra, JADX ou decompilacao completa.",
    }
    if zipfile.is_zipfile(target):
        with zipfile.ZipFile(target) as z:
            result["zip_entries"] = z.namelist()[:100]
            result["zip_total_entries"] = len(z.infolist())
    with target.open("rb") as f:
        is_elf = f.read(4) == b"\x7fELF"
    if is_elf and private_readelf:
        result["readelf_header"] = _first_output([private_readelf, "-h", str(target)])
    report = _write_text(output / "reverse" / "report.json", json.dumps(result, ensure_ascii=False, indent=2))
    return [report]


def execute(request: str, output: Path, title: str, target: Path | None = None) -> dict:
    selected = plan(request)
    if selected["executor"] is None:
        raise NotImplementedError(f"Rota {selected['route']} ainda nao possui executor local; usar ferramenta do anfitriao devidamente autenticada.")
    output.mkdir(parents=True, exist_ok=True)
    if selected["route"] == "website":
        paths = create_website(output, title)
    elif selected["route"] == "creative":
        paths = create_creative(output, title)
    elif selected["route"] == "reverse":
        if target is None:
            raise ValueError("Para inspecionar aplicacao, adicionar --input /caminho/arquivo")
        paths = inspect_artifact(target, output)
    else:
        raise NotImplementedError(selected["route"])
    report = {"status": "completed_local_task", "route": selected["route"], "selected_tool": selected["preferred_tool"], "files": [str(p.resolve()) for p in paths], "scope": "Prototipo local; nenhum motor externo foi invocado."}
    report_path = _write_text(output / "last-run.json", json.dumps(report, ensure_ascii=False, indent=2))
    report["run_report"] = str(report_path.resolve())
    return report
