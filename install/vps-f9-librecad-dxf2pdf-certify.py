#!/usr/bin/env python3
"""Ferrari F9: certify real LibreCAD DXF -> PDF via private binaries.

Create a synthetic R12 rectangle/circle drawing, run the private LibreCAD
converter, validate the generated PDF with Ferrari-private Poppler pdfinfo,
and remove every transient file from the Ferrari project. No global installs,
no other-project writes, no GUI claims, no external input or network access.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
TOOLS = ROOT / "tools"
RUNTIME = ROOT / ".runtime"
APPHOME = TOOLS / "librecad-2.2.1.6"
EXECUTABLE = APPHOME / "squashfs-root/AppRun"
PDFINFO = TOOLS / "ubuntu-cli/bin/pdfinfo"
EXPECTED = "7bf6dcecf15da26502c5969b5eee54d5e116fc32"
FALLBACK = "952b0a75ba798471b07053677d53791bd078ed56"
APPIMAGE = APPHOME / "LibreCAD-v2.2.1.6-x86_64.AppImage"
APPIMAGE_SIZE = 82846008
APPIMAGE_SHA256 = "f2d86e6a40ec684b758c821eff3496a7d36e69f17519cde0b508a66d72c5754c"

# R12 ASCII DXF: 4 edges of a 100x50 rectangle plus a circle in its interior.
# The DXF is original synthetic geometry: no user or private project files.
DRAWING = """0
SECTION
2
HEADER
9
$ACADVER
1
AC1009
0
ENDSEC
0
SECTION
2
TABLES
0
TABLE
2
LAYER
70
1
0
LAYER
2
0
70
0
62
7
6
CONTINUOUS
0
ENDTAB
0
ENDSEC
0
SECTION
2
ENTITIES
0
LINE
8
0
10
0
20
0
30
0
11
100
21
0
31
0
0
LINE
8
0
10
100
20
0
30
0
11
100
21
50
31
0
0
LINE
8
0
10
100
20
50
30
0
11
0
21
50
31
0
0
LINE
8
0
10
0
20
50
30
0
11
0
21
0
31
0
0
CIRCLE
8
0
10
50
20
25
30
0
40
10
0
ENDSEC
0
EOF
"""

def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()

def guard() -> dict:
    require(os.geteuid() != 0, "F9_LIBRECAD_NO_ROOT")
    for parent in (ROOT, TOOLS, RUNTIME, APPHOME):
        require(parent.is_dir() and not parent.is_symlink(),
                "F9_LIBRECAD_UNSAFE_PRIVATE_ROOT:" + parent.name)
    current = ROOT / "current"
    require(current.is_symlink() and current.resolve(strict=True)
            == ROOT / "releases" / EXPECTED, "F9_LIBRECAD_ACTIVE_RELEASE_DRIFT")
    require((ROOT / "releases" / FALLBACK / "engine/ferrari.py").is_file(),
            "F9_LIBRECAD_FALLBACK_MISSING")
    doc = json.loads((current / "engine/catalog.json").read_text(encoding="utf-8"))
    require(len(doc["tools"]) == 173 and len(doc["functions"]) == 272
            and doc["counts"]["all_catalog_entries"] == 450,
            "F9_LIBRECAD_CATALOG_NOT_UNIVERSAL")
    for binary in (EXECUTABLE, PDFINFO):
        require(binary.is_file() and os.access(binary, os.X_OK),
                "F9_LIBRECAD_PRIVATE_TOOL_MISSING:" + binary.name)
        require(binary.resolve(strict=True).is_relative_to(TOOLS.resolve(strict=True)),
                "F9_LIBRECAD_EXECUTOR_ESCAPE")
    require(APPIMAGE.is_file() and not APPIMAGE.is_symlink()
            and APPIMAGE.stat().st_size == APPIMAGE_SIZE
            and sha256(APPIMAGE) == APPIMAGE_SHA256,
            "F9_LIBRECAD_OFFICIAL_APPIMAGE_DIGEST_MISMATCH")
    return {"active_release": EXPECTED, "fallback_release": FALLBACK,
            "catalog_entries": 450, "appimage_sha256_verified": True}

def env(work: Path, pdfinfo: bool = False) -> dict:
    child = {k: v for k, v in os.environ.items() if k not in {
        "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH", "LD_LIBRARY_PATH",
        "PYTHONPATH", "QT_QPA_FONTDIR", "APPDIR", "APPIMAGE"}}
    child.update({
        "HOME": str(work), "TMPDIR": str(work),
        "XDG_CONFIG_HOME": str(work), "XDG_CACHE_HOME": str(work),
        "XDG_DATA_HOME": str(work), "XDG_RUNTIME_DIR": str(work),
        "QT_QPA_PLATFORM": "offscreen",
        "LIBGL_ALWAYS_SOFTWARE": "1",
        "GSETTINGS_BACKEND": "memory",
        "PYTHONNOUSERSITE": "1",
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "socks5://127.0.0.1:9",
        "PATH": str(TOOLS / "ubuntu-cli/bin") + ":/usr/bin:/bin"
    })
    if pdfinfo:
        child["LD_LIBRARY_PATH"] = str(TOOLS / "ubuntu-cli/lib")
    return child

def run(args: list[str], work: Path, timeout: int, pdfinfo: bool = False):
    return subprocess.run(args, env=env(work, pdfinfo=pdfinfo), cwd=work,
                          text=True, capture_output=True, check=False,
                          timeout=timeout)

def validate_pdf(path: Path, work: Path) -> dict:
    require(path.is_file() and not path.is_symlink() and path.stat().st_size > 1200,
            "F9_LIBRECAD_NO_REAL_PDF")
    with path.open("rb") as handle:
        signature = handle.read(8)
        handle.seek(max(0, path.stat().st_size - 2048))
        tail = handle.read()
    require(signature.startswith(b"%PDF-") and b"%%EOF" in tail,
            "F9_LIBRECAD_PDF_STRUCTURE_INVALID")
    probe = run([str(PDFINFO), str(path)], work, timeout=35, pdfinfo=True)
    require(probe.returncode == 0, "F9_LIBRECAD_PRIVATE_PDFINFO_FAILED:" +
            (probe.stderr or probe.stdout)[-200:])
    pages = re.search(r"^Pages:\s+(\d+)\s*$", probe.stdout, flags=re.M)
    require(pages is not None and int(pages.group(1)) == 1,
            "F9_LIBRECAD_PDF_NOT_SINGLE_PAGE")
    return {"real_pdf_created": True, "independent_poppler_pdfinfo": True,
            "pdf_pages": 1, "pdf_bytes": path.stat().st_size,
            "pdf_sha256": sha256(path)}

def certify() -> dict:
    identity = guard()
    with tempfile.TemporaryDirectory(prefix=".f9-librecad-real-", dir=RUNTIME) as name:
        work = Path(name)
        drawing = work / "synthetic-100x50-rectangle.dxf"
        output = work / "librecad-converted.pdf"
        drawing.write_bytes(DRAWING.replace("\n", "\r\n").encode("ascii"))
        require(drawing.stat().st_size > 160 and DRAWING.count("\nLINE\n") == 4
                and DRAWING.count("\nCIRCLE\n") == 1,
                "F9_LIBRECAD_SYNTHETIC_DXF_BAD")
        trial = run([str(EXECUTABLE), "dxf2pdf", "-a", "-o",
                     str(output), str(drawing)], work, timeout=90)
        # A PDF can exist even when a converter returns an error; both are required.
        converted = trial.returncode == 0
        evidence = {}
        diagnostic = ""
        if converted:
            try:
                evidence = validate_pdf(output, work)
            except (OSError, RuntimeError, subprocess.TimeoutExpired) as exc:
                converted = False
                diagnostic = str(exc)[-250:]
        else:
            diagnostic = (trial.stderr or trial.stdout or "converter failed")[-300:]
        diagnostic = diagnostic.replace(str(ROOT), "<FERRARI>")
        return {
            **identity,
            "status": "pass" if converted else "partial_blocked",
            "tool": "librecad",
            "version": "2.2.1.6",
            "synthetic_dxf_rectangle_mm": [100, 50],
            "synthetic_lines": 4,
            "synthetic_circles": 1,
            "private_dxf2pdf_certified": converted,
            "converter_exit_code": trial.returncode,
            "pdf_evidence": evidence,
            "diagnostic": diagnostic,
            "gui_editing_certified": False,
            "other_dxf_formats_certified": False,
            "cad_3d_certified": False,
            "global_apt_modified": False,
            "other_projects_modified": False,
            "active_release_changed": False,
            "test_files_removed_after_run": True,
        }

def main() -> int:
    require(sys.argv[1:] == ["--certify"], "F9_LIBRECAD_CERTIFY_REQUIRED")
    try:
        record = certify()
        print(json.dumps(record, sort_keys=True), flush=True)
        print("FERRARI_F9_LIBRECAD_DXF2PDF=" + record["status"].upper(),
              file=sys.stderr)
        return 0
    except (OSError, RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[-300:],
                          "global_apt_modified": False,
                          "other_projects_modified": False}), flush=True)
        return 3

if __name__ == "__main__":
    sys.exit(main())
