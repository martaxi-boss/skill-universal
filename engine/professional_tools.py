"""Ferrari-owned professional adapters: IFC inventory and Vite static build.

No global Python/npm installs, arbitrary shell commands, user-supplied npm
scripts or Vite configs. Both executors live in Ferrari's isolated runtime.
"""
from __future__ import annotations

import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess
from tempfile import TemporaryDirectory
import zipfile

ROOT = Path(__file__).resolve().parents[1]
HOME = Path("/srv/projects/skill-universal")
BIM_PYTHON = HOME / ".runtime/venvs/bim/bin/python"
NODE = HOME / "runtimes/node-22.23.4/bin/node"
VITE = HOME / ".runtime/npm/vite/node_modules/vite/bin/vite.js"
PLAYWRIGHT = HOME / ".runtime/npm/playwright/node_modules/playwright"
BROWSER_CACHE = HOME / ".runtime/browsers"
ALLOWED_EXT = {
    ".html", ".css", ".js", ".mjs", ".ts", ".tsx", ".jsx",
    ".svg", ".png", ".jpg", ".jpeg", ".webp", ".ico", ".json",
    ".woff", ".woff2",
}


def bim_available() -> bool:
    site = HOME / ".runtime/venvs/bim/lib"
    return BIM_PYTHON.is_file() and any(site.glob("python*/site-packages/ifcopenshell/__init__.py"))


def vite_available() -> bool:
    return NODE.is_file() and VITE.is_file() and (VITE.parent.parent / "package.json").is_file()


def browser_available() -> bool:
    """Only the Ferrari-owned Playwright package and headless shell."""
    return (NODE.is_file() and (PLAYWRIGHT / "cli.js").is_file()
            and BROWSER_CACHE.is_dir()
            and any(p.is_file() and not p.is_symlink() for p in
                    BROWSER_CACHE.glob("chromium_headless_shell-*/chrome-headless-shell-linux64/chrome-headless-shell")))


def _run(args: list[str], *, timeout: int, cwd: Path | None = None, env=None):
    try:
        done = subprocess.run(args, shell=False, check=False, capture_output=True,
                              text=True, timeout=timeout, cwd=cwd, env=env)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Ferrari professional executor timed out") from exc
    if done.returncode:
        raise RuntimeError("Ferrari executor failed: " + (done.stderr or done.stdout)[-1400:])
    return done


def ifc_summary(source: Path, output_dir: Path):
    if source.suffix.lower() != ".ifc":
        raise ValueError("Only IFC files are supported")
    if not bim_available():
        raise RuntimeError("Isolated Ferrari IfcOpenShell is not installed")
    target = output_dir / "ifc-report.json"
    if target.exists() or target.is_symlink():
        raise FileExistsError("IFC report already exists")
    output_dir.mkdir(parents=True, exist_ok=True)
    _run([str(BIM_PYTHON), str(ROOT / "engine/ifc_inspector.py"),
          str(source), str(target)], timeout=120)
    if not target.is_file() or target.stat().st_size < 80:
        raise RuntimeError("IfcOpenShell did not produce a report")
    report = json.loads(target.read_text(encoding="utf-8"))
    if report.get("format") != "IFC" or not report.get("schema") or not report.get("total_entities"):
        raise RuntimeError("Incomplete IFC report")
    return str(BIM_PYTHON) + ":ifcopenshell", [target]


def _safe_name(name: str):
    if "\\" in name or name.startswith("/"):
        raise ValueError("Invalid ZIP path")
    path = PurePosixPath(name)
    if not path.parts or any(
        part in {".", ".."} or part.startswith(".") or
        not re.fullmatch(r"[a-zA-Z0-9_-][a-zA-Z0-9_.-]{0,79}", part)
        for part in path.parts
    ):
        raise ValueError("Unsafe ZIP member")
    if name != "index.html" and not (
        len(path.parts) >= 2 and path.parts[0] in {"src", "public"}
    ):
        raise ValueError("Only index.html, src/* and public/* are accepted")
    if path.suffix.lower() not in ALLOWED_EXT:
        raise ValueError("Unsupported web project file")
    return path


def _unpack_project(source: Path, work: Path):
    if source.suffix.lower() != ".zip" or source.is_symlink() or not source.is_file():
        raise ValueError("A regular ZIP web project is required")
    if source.stat().st_size > 2_000_000:
        raise ValueError("Project ZIP exceeds Ferrari Skill input limit")
    try:
        archive = zipfile.ZipFile(source)
    except zipfile.BadZipFile as exc:
        raise ValueError("Invalid ZIP archive") from exc
    with archive as z:
        files = [entry for entry in z.infolist() if not entry.is_dir()]
        if not files or len(files) > 120 or sum(i.file_size for i in files) > 6_000_000:
            raise ValueError("Project file count/size limit exceeded")
        names = set()
        for info in files:
            name = str(_safe_name(info.filename))
            if name in names or info.file_size > 2_000_000 or stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError("Duplicate, oversized or symbolic-link ZIP member")
            names.add(name)
            content = z.read(info, pwd=None)
            if len(content) != info.file_size:
                raise ValueError("Invalid ZIP member length")
            dst = work / name
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(content)
    if "index.html" not in names:
        raise ValueError("Web project requires index.html")
    return sorted(names)


def vite_build(source: Path, output_dir: Path):
    if not vite_available():
        raise RuntimeError("Ferrari isolated Node/Vite runtime is not installed")
    dist = output_dir / "dist"
    report = output_dir / "vite-build.json"
    if dist.exists() or dist.is_symlink() or report.exists() or report.is_symlink():
        raise FileExistsError("Refusing to overwrite Vite outputs")
    output_dir.mkdir(parents=True, exist_ok=True)
    with TemporaryDirectory(prefix="ferrari-vite-build-") as folder:
        work = Path(folder)
        inputs = _unpack_project(source, work)
        env = os.environ.copy()
        env.pop("NODE_OPTIONS", None)
        env["PATH"] = str(NODE.parent) + os.pathsep + env.get("PATH", "")
        env["CI"] = "true"
        _run([str(NODE), str(VITE), "build", str(work),
              "--outDir", str(dist), "--emptyOutDir"],
             timeout=150, cwd=work, env=env)
    files = sorted(p.relative_to(dist).as_posix() for p in dist.rglob("*") if p.is_file())
    if "index.html" not in files or not files:
        raise RuntimeError("Vite did not produce index.html")
    browser_status = "not_installed"
    browser_artifacts = []
    if browser_available():
        screenshot = output_dir / "browser-screenshot.png"
        mobile_screenshot = output_dir / "browser-mobile.png"
        browser_report = output_dir / "browser-check.json"
        if any(p.exists() or p.is_symlink() for p in (screenshot, mobile_screenshot, browser_report)):
            raise FileExistsError("Refusing overwrite of Ferrari browser artifacts")
        env["PLAYWRIGHT_BROWSERS_PATH"] = str(BROWSER_CACHE)
        _run([str(NODE), str(ROOT / "engine/browser_check.js"), str(dist),
              str(screenshot), str(browser_report)], timeout=100, env=env)
        result = json.loads(browser_report.read_text(encoding="utf-8"))
        mobile = result.get("mobile") or {}
        interactions = result.get("interactions") or {}
        if (result.get("status") != "passed"
                or interactions.get("status") not in {"clear", "findings"}
                or not isinstance(interactions.get("focusable_count"), int)
                or not isinstance(interactions.get("findings"), list)
                or not screenshot.is_file() or screenshot.stat().st_size < 100
                or not mobile_screenshot.is_file() or mobile_screenshot.stat().st_size < 100
                or mobile.get("viewport") != {"width": 390, "height": 844}
                or "horizontal_overflow_px" not in mobile
                or mobile.get("spotcheck_status") not in {"clear", "findings"}):
            raise RuntimeError("Ferrari browser/mobile evidence is missing or incomplete")
        browser_status = "passed"
        browser_artifacts = [screenshot, browser_report, mobile_screenshot]
    pkg = json.loads((VITE.parent.parent / "package.json").read_text(encoding="utf-8"))
    report.write_text(json.dumps({
        "builder": "Vite", "version": pkg.get("version"),
        "source_files": inputs, "built_files": files,
        "browser_test": {"status": browser_status,
                         "engine": "isolated Playwright Chromium headless shell" if browser_status == "passed" else None},
        "scope": "static frontend build of a restricted project ZIP; no npm scripts or user configs",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return str(NODE) + ":vite", [dist, report] + browser_artifacts
