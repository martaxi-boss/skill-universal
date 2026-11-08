"""Purpose-built Ferrari adapters for privately installed specialist programs.

These are real, bounded user-facing operations, not --version-only probes.
No global installations, no arbitrary command strings, no resident services.
Only synthetic/non-private files may enter through public GitHub transport.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import signal
import subprocess
import tempfile

HOME = Path("/srv/projects/skill-universal")
LIBRECAD = HOME / "tools/librecad-2.2.1.6/squashfs-root/AppRun"
PDFINFO = HOME / "tools/ubuntu-cli/bin/pdfinfo"
QGIS = HOME / "tools/qgis-4.2.3-condaforge"
GODOT = HOME / "tools/godot-4.7.2/extracted/Godot_v4.7.2-stable_linux.x86_64"

QGIS_WORKER = r"""
import json
from pathlib import Path
import sys
from qgis.core import QgsApplication, QgsFeature, QgsGeometry, QgsVectorLayer
work, prefix, output = map(Path, sys.argv[1:4])
data = json.loads((work / "validated-shape.json").read_text(encoding="utf-8"))
QgsApplication.setPrefixPath(str(prefix), True)
app = QgsApplication([], False)
app.initQgis()
import processing
from processing.core.Processing import Processing
Processing.initialize()
layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "ferrari-private-buffer", "memory")
assert layer.isValid()
feature = QgsFeature(layer.fields())
feature.setGeometry(QgsGeometry.fromWkt(data["wkt"]))
assert not feature.geometry().isEmpty() and feature.geometry().isGeosValid()
assert layer.dataProvider().addFeatures([feature])[0]
layer.updateExtents()
result = processing.run("native:buffer", {
    "INPUT": layer, "DISTANCE": 5.0, "SEGMENTS": 12,
    "END_CAP_STYLE": 0, "JOIN_STYLE": 0, "MITER_LIMIT": 2.0,
    "DISSOLVE": False, "OUTPUT": str(output)
})
assert output.is_file() and output.stat().st_size > 100
print("FERRARI_QGIS_BUFFER_5M=PASS", flush=True)
"""


def _private_file(path: Path, executable: bool = False) -> Path:
    root = HOME.resolve(strict=True)
    path = Path(path)
    real = path.resolve(strict=True)
    if (not path.is_file() or not real.is_relative_to(root)
            or (path.is_symlink() and not executable)
            or (executable and not os.access(path, os.X_OK))):
        raise RuntimeError("Ferrari private input or executable is unavailable")
    return real


def _private_folder(folder: Path) -> Path:
    root = HOME.resolve(strict=True)
    folder = Path(folder)
    if folder.is_symlink() or not folder.resolve().is_relative_to(root):
        raise ValueError("Ferrari output must stay in its own project")
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    return folder.resolve(strict=True)


def _new(folder: Path, name: str) -> Path:
    path = folder / name
    if path.exists() or path.is_symlink():
        raise FileExistsError("Ferrari refuses to overwrite " + name)
    return path


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _isolated_env(folder: Path, *, qt: str = "offscreen") -> dict:
    env = {k: v for k, v in os.environ.items()
           if k not in {"LD_PRELOAD", "LD_LIBRARY_PATH", "PYTHONPATH", "PYTHONHOME",
                        "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH",
                        "APPDIR", "APPIMAGE", "NODE_OPTIONS", "JAVA_TOOL_OPTIONS"}}
    env.update({
        "HOME": str(folder), "TMPDIR": str(folder),
        "XDG_CACHE_HOME": str(folder), "XDG_CONFIG_HOME": str(folder),
        "XDG_DATA_HOME": str(folder), "XDG_RUNTIME_DIR": str(folder),
        "QT_QPA_PLATFORM": qt, "LIBGL_ALWAYS_SOFTWARE": "1",
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
        "OMP_NUM_THREADS": "2", "OPENBLAS_NUM_THREADS": "1",
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "socks5://127.0.0.1:9",
        "NO_PROXY": "",
    })
    return env


def _run(args: list[str], folder: Path, timeout: int, *, env: dict) -> subprocess.CompletedProcess:
    process = subprocess.Popen(args, shell=False, cwd=str(folder), env=env,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               text=True, errors="replace", start_new_session=True)
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        try:
            os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        process.communicate(timeout=5)
        raise RuntimeError("Ferrari specialist adapter timed out") from exc
    return subprocess.CompletedProcess(args, process.returncode,
                                       stdout[-6000:], stderr[-6000:])


def librecad_dxf_pdf(source: Path, folder: Path):
    """Convert one authorized ASCII DXF to one real, independently checked PDF."""
    source = _private_file(source)
    if (source.suffix.lower() != ".dxf" or not 64 <= source.stat().st_size <= 2_000_000
            or b"EOF" not in source.read_bytes()[-256:]):
        raise ValueError("LibreCAD requires a valid bounded ASCII DXF")
    app = _private_file(LIBRECAD, executable=True)
    pdfinfo = _private_file(PDFINFO, executable=True)
    xvfb = Path("/usr/bin/xvfb-run")
    if not xvfb.is_file() or not os.access(xvfb, os.X_OK):
        raise RuntimeError("Pre-existing temporary Ubuntu Xvfb QA display unavailable")
    folder = _private_folder(folder)
    output = _new(folder, "librecad-drawing.pdf")
    report = _new(folder, "librecad-report.json")
    with tempfile.TemporaryDirectory(prefix=".librecad-", dir=HOME / ".runtime") as td:
        work = Path(td)
        env = _isolated_env(work, qt="xcb")
        env["GSETTINGS_BACKEND"] = "memory"
        env["PATH"] = str(HOME / "tools/ubuntu-cli/bin") + ":/usr/bin:/bin"
        converted = _run([str(xvfb), "-a",
                          "--server-args=-screen 0 1280x800x24 -nolisten tcp",
                          str(app), "dxf2pdf", "-a", "-o", str(output), str(source)],
                         work, 90, env=env)
        if converted.returncode:
            raise RuntimeError("LibreCAD DXF to PDF failed: " + converted.stderr[-400:])
        if not output.is_file() or output.is_symlink() or output.stat().st_size < 1200:
            raise RuntimeError("LibreCAD produced no real PDF")
        payload = output.read_bytes()
        if not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-2048:]:
            raise RuntimeError("LibreCAD PDF signature invalid")
        check_env = dict(env)
        check_env["LD_LIBRARY_PATH"] = str(HOME / "tools/ubuntu-cli/lib")
        info = _run([str(pdfinfo), str(output)], work, 35, env=check_env)
        pages = re.search(r"^Pages:\s+(\d+)\s*$", info.stdout, re.MULTILINE)
        if info.returncode or pages is None or int(pages.group(1)) < 1:
            raise RuntimeError("Private Poppler could not independently validate PDF")
    record = {"status": "completed", "program": "librecad",
              "workflow": "private_dxf_to_pdf", "pdf_pages": int(pages.group(1)),
              "input_sha256": _sha(source), "output_sha256": _sha(output),
              "private_pdfinfo_verified": True, "gui_editing_certified": False}
    report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return str(app), [output, report]


def _ring_area(ring: list) -> float:
    return abs(sum(ring[i][0] * ring[i + 1][1] - ring[i + 1][0] * ring[i][1]
                   for i in range(len(ring) - 1)) / 2.0)


def _validated_polygon(source: Path) -> tuple[str, float]:
    if source.suffix.lower() != ".geojson" or not 100 <= source.stat().st_size <= 2_000_000:
        raise ValueError("QGIS requires a bounded .geojson polygon")
    doc = json.loads(source.read_text(encoding="utf-8"))
    if not isinstance(doc, dict) or doc.get("type") != "FeatureCollection":
        raise ValueError("GeoJSON FeatureCollection required")
    crs = doc.get("crs", {})
    if not isinstance(crs, dict) or crs.get("properties", {}).get("name") not in {
            "EPSG:3857", "urn:ogc:def:crs:EPSG::3857"}:
        raise ValueError("Explicit metre-based EPSG:3857 required; no degree/meter confusion")
    features = doc.get("features")
    if not isinstance(features, list) or len(features) != 1:
        raise ValueError("One GeoJSON feature per operation")
    geom = features[0].get("geometry") if isinstance(features[0], dict) else None
    if not isinstance(geom, dict) or geom.get("type") != "Polygon":
        raise ValueError("QGIS buffer accepts a Polygon geometry")
    polygons = geom.get("coordinates")
    if not isinstance(polygons, list) or len(polygons) != 1:
        raise ValueError("Polygon must have one exterior ring and no holes")
    ring = polygons[0]
    if not isinstance(ring, list) or not 4 <= len(ring) <= 256 or ring[0] != ring[-1]:
        raise ValueError("Closed polygon of up to 255 edges required")
    for coordinate in ring:
        if (not isinstance(coordinate, list) or len(coordinate) != 2
                or any(type(n) not in {int, float} or not math.isfinite(n)
                       or abs(n) > 20_000_000 for n in coordinate)):
            raise ValueError("Non-finite or unsupported GeoJSON coordinates")
    area = _ring_area(ring)
    if not 1 <= area <= 1e11:
        raise ValueError("Unexpected EPSG:3857 polygon area")
    wkt = "POLYGON((" + ",".join(f"{p[0]} {p[1]}" for p in ring) + "))"
    return wkt, area


def qgis_buffer(source: Path, folder: Path):
    """Actually run QGIS native:buffer, with a fixed documented five-metre distance."""
    source = _private_file(source)
    wkt, area_in = _validated_polygon(source)
    python = _private_file(QGIS / "bin/python", executable=True)
    _private_file(QGIS / "bin/qgis_process", executable=True)
    if not (QGIS / "conda-meta").is_dir():
        raise RuntimeError("Ferrari private QGIS conda environment missing")
    folder = _private_folder(folder)
    output = _new(folder, "qgis-buffer-5m.geojson")
    report = _new(folder, "qgis-buffer-report.json")
    with tempfile.TemporaryDirectory(prefix=".qgis-", dir=HOME / ".runtime") as td:
        work = Path(td)
        (work / "validated-shape.json").write_text(
            json.dumps({"wkt": wkt}), encoding="utf-8")
        worker = work / "qgis-worker.py"
        worker.write_text(QGIS_WORKER, encoding="utf-8")
        env = _isolated_env(work)
        env.update({
            "QGIS_PREFIX_PATH": str(QGIS),
            "PYTHONPATH": os.pathsep.join([str(QGIS / "share/qgis/python"),
                                         str(QGIS / "share/qgis/python/plugins")]),
            "LD_LIBRARY_PATH": str(QGIS / "lib"),
            "PATH": str(QGIS / "bin") + ":/usr/bin:/bin",
        })
        result = _run([str(python), str(worker), str(work), str(QGIS), str(output)],
                      work, 100, env=env)
        if result.returncode:
            raise RuntimeError("QGIS private native:buffer failed: " + result.stderr[-400:])
    if not output.is_file() or output.is_symlink() or output.stat().st_size < 100:
        raise RuntimeError("QGIS generated no real GeoJSON")
    doc = json.loads(output.read_text(encoding="utf-8"))
    features = doc.get("features") if doc.get("type") == "FeatureCollection" else None
    if not isinstance(features, list) or len(features) != 1:
        raise RuntimeError("QGIS GeoJSON output has unexpected feature count")
    geom = features[0].get("geometry", {})
    if geom.get("type") != "Polygon":
        raise RuntimeError("QGIS buffer did not export a polygon")
    rings = geom.get("coordinates")
    if not isinstance(rings, list) or not rings or len(rings[0]) < 4:
        raise RuntimeError("QGIS polygon ring missing")
    if rings[0][0] != rings[0][-1]:
        raise RuntimeError("QGIS polygon ring not closed")
    area_out = _ring_area(rings[0]) - sum(_ring_area(hole) for hole in rings[1:])
    if not (math.isfinite(area_out) and area_out > area_in):
        raise RuntimeError("QGIS buffer geometry failed independent area check")
    record = {"status": "completed", "program": "qgis",
              "algorithm": "native:buffer", "crs": "EPSG:3857",
              "distance_m": 5.0, "area_before_m2": round(area_in, 3),
              "area_after_m2": round(area_out, 3),
              "features": 1, "output_sha256": _sha(output),
              "gui_certified": False, "ogr_readback_certified": False}
    report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return str(python) + ":QGIS-private-native-buffer", [output, report]


PROJECT = """config_version=5

[application]

config/name="Ferrari Godot Starter"
run/main_scene="res://main.tscn"

[rendering]

renderer/rendering_method="gl_compatibility"
renderer/rendering_method.mobile="gl_compatibility"
"""
SCENE = """[gd_scene load_steps=1 format=3]

[node name="FerrariStarter" type="Node2D"]

[node name="Label" type="Label" parent="."]
offset_right = 540.0
offset_bottom = 56.0
text = "Ferrari - projeto Godot de exemplo"
"""


def godot_starter(folder: Path):
    """Build an original tiny Godot project and validate it with the private engine."""
    executable = _private_file(GODOT, executable=True)
    folder = _private_folder(folder)
    project = _new(folder, "godot-starter")
    project.mkdir(mode=0o700)
    (project / "project.godot").write_text(PROJECT, encoding="utf-8")
    (project / "main.tscn").write_text(SCENE, encoding="utf-8")
    report = _new(folder, "godot-starter-report.json")
    with tempfile.TemporaryDirectory(prefix=".godot-", dir=HOME / ".runtime") as td:
        work = Path(td)
        result = _run([str(executable), "--headless", "--path", str(project),
                       "--editor", "--quit"], work, 65,
                      env=_isolated_env(work))
    if result.returncode or "ERROR:" in result.stderr:
        raise RuntimeError("Godot private project import failed: " + result.stderr[-400:])
    record = {"status": "completed", "program": "godot",
              "workflow": "private_headless_project_parse",
              "engine_exit_code": result.returncode,
              "project_sha256": _sha(project / "project.godot"),
              "scene_sha256": _sha(project / "main.tscn"),
              "playable_game_certified": False, "export_templates_certified": False}
    report.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return str(executable) + ":headless", [project / "project.godot", project / "main.tscn", report]
