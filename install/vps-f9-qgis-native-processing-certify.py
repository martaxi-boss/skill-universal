#!/usr/bin/env python3
"""Ferrari-only: actual QGIS native:buffer processing and loader preflight.

Uses the already installed private QGIS runtime. A synthetic polygon, input
GeoJSON, output GeoJSON and all transient settings live in a TemporaryDirectory
under Ferrari/.runtime. No APT, no network, no GUI, no project-crossing writes.
A startup smoke or a previous QgsGeometry test is NOT sufficient to pass here.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
TARGET = ROOT / "tools/qgis-4.2.3-condaforge"
RUNTIME = ROOT / ".runtime"
EXPECTED = "7bf6dcecf15da26502c5969b5eee54d5e116fc32"
FALLBACK = "952b0a75ba798471b07053677d53791bd078ed56"

CHILD = r"""
import json
from pathlib import Path
import sys
from qgis.core import (QgsApplication, QgsVectorLayer, QgsGeometry, QgsFeature)

work = Path(sys.argv[1])
prefix = Path(sys.argv[2])
assert work.is_dir() and prefix.is_dir()
QgsApplication.setPrefixPath(str(prefix), True)
app = QgsApplication([], False)
app.initQgis()

import processing
from processing.core.Processing import Processing
Processing.initialize()
layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "ferrari-synthetic-plot", "memory")
assert layer.isValid(), "Synthetic QGIS memory vector layer invalid"
feature = QgsFeature(layer.fields())
feature.setGeometry(QgsGeometry.fromWkt(
    "POLYGON((0 0,100 0,100 50,0 50,0 0))"))
assert feature.geometry().isGeosValid()
assert layer.dataProvider().addFeatures([feature])[0]
layer.updateExtents()
output = work / "buffer-5m.geojson"
result = processing.run("native:buffer", {
    "INPUT": layer, "DISTANCE": 5.0, "SEGMENTS": 12,
    "END_CAP_STYLE": 0, "JOIN_STYLE": 0, "MITER_LIMIT": 2.0,
    "DISSOLVE": False, "OUTPUT": str(output)
})
assert output.is_file(), "native:buffer did not create a real GeoJSON"
doc = json.loads(output.read_text(encoding="utf-8"))
assert doc.get("type") == "FeatureCollection", "GeoJSON export not a FeatureCollection"
features = doc.get("features", [])
assert len(features) == 1, "Buffer did not generate one feature"
# Independent GeoJSON validation intentionally does NOT initialize OGR:
# on this host the optional provider aborts in C++ (VPS #42303505063).
# The native QGIS buffer executed and wrote a real GeoJSON; independently
# verify the polygon's structure, ring closure and area with pure Python.
geometry = features[0]["geometry"]
assert isinstance(geometry, dict)
typ = geometry.get("type")
coordinates = geometry.get("coordinates")
assert typ in ("Polygon", "MultiPolygon"), "Buffer did not export polygon geometry"
polygons = [coordinates] if typ == "Polygon" else coordinates
assert isinstance(polygons, list) and len(polygons) == 1
def ring_area(ring):
    assert isinstance(ring, list) and len(ring) >= 4, "GeoJSON ring too short"
    assert ring[0] == ring[-1], "GeoJSON polygon ring not closed"
    assert all(isinstance(p, list) and len(p) >= 2
               and all(isinstance(v, (int, float)) for v in p[:2])
               for p in ring), "Invalid coordinate values"
    return abs(sum(ring[i][0] * ring[i+1][1] -
                   ring[i+1][0] * ring[i][1]
                   for i in range(len(ring)-1)) / 2.0)
poly = polygons[0]
assert isinstance(poly, list) and poly, "GeoJSON polygon has no rings"
area = ring_area(poly[0]) - sum(ring_area(h) for h in poly[1:])
assert 6500.0 < area < 7500.0, ("Unexpected 5m buffer area", area)
report = {
    "native_buffer_algorithm_executed": True,
    "synthetic_input_area_m2": 5000.0,
    "buffer_distance_m": 5.0,
    "buffer_area_m2": round(area, 3),
    "geojson_export_and_reparse": True,
    "independent_geojson_area_verified": True,
    "ogr_provider_geojson_readback": False,
    "feature_count": 1,
    "gui_certified": False,
    "all_qgis_providers_certified": False,
    "real_property_data_used": False
}
(work / "native-processing-result.json").write_text(
    json.dumps(report, sort_keys=True), encoding="utf-8")
print("FERRARI_QGIS_NATIVE_BUFFER_REAL=PASS", flush=True)
"""

def guard() -> None:
    if os.geteuid() == 0:
        raise RuntimeError("F9_QGIS_TEST_NO_ROOT")
    for p in (ROOT, TARGET, RUNTIME):
        if not p.is_dir() or p.is_symlink():
            raise RuntimeError("F9_QGIS_PRIVATE_DIR_UNSAFE")
    cur = ROOT / "current"
    if not cur.is_symlink() or cur.resolve(strict=True) != ROOT / "releases" / EXPECTED:
        raise RuntimeError("F9_QGIS_ACTIVE_RELEASE_CHANGED")
    if not (ROOT / "releases" / FALLBACK / "engine/ferrari.py").is_file():
        raise RuntimeError("F9_QGIS_FALLBACK_MISSING")
    doc = json.loads((cur / "engine/catalog.json").read_text(encoding="utf-8"))
    if not (len(doc["tools"]) == 173 and len(doc["functions"]) == 272
            and doc["counts"]["all_catalog_entries"] == 450):
        raise RuntimeError("F9_QGIS_UNIVERSAL_CATALOG_DRIFT")
    for name in ("bin/python", "bin/qgis_process"):
        exe = TARGET / name
        if not exe.is_file() or not os.access(exe, os.X_OK) or not exe.resolve().is_relative_to(TARGET):
            raise RuntimeError("F9_QGIS_PRIVATE_EXECUTOR_MISSING:" + name)
    if not (TARGET / "conda-meta").is_dir():
        raise RuntimeError("F9_QGIS_CONDA_PROVENANCE_MISSING")

def private_env(work: Path) -> dict[str, str]:
    environment = {k: v for k, v in os.environ.items()
                   if k not in {"LD_LIBRARY_PATH", "PYTHONPATH",
                                "QT_PLUGIN_PATH", "QT_QPA_PLATFORM_PLUGIN_PATH"}}
    qgis_python = [TARGET / "share/qgis/python",
                   TARGET / "share/qgis/python/plugins"]
    environment.update({
        "HOME": str(work), "TMPDIR": str(work),
        "XDG_CONFIG_HOME": str(work),
        "XDG_CACHE_HOME": str(work), "XDG_DATA_HOME": str(work),
        "XDG_RUNTIME_DIR": str(work),
        "QT_QPA_PLATFORM": "offscreen",
        "LIBGL_ALWAYS_SOFTWARE": "1",
        "OMP_NUM_THREADS": "2",
        "PYTHONNOUSERSITE": "1",
        "QGIS_PREFIX_PATH": str(TARGET),
        "PYTHONPATH": os.pathsep.join(str(p) for p in qgis_python if p.is_dir()),
        "LD_LIBRARY_PATH": str(TARGET / "lib"),
        "PATH": str(TARGET / "bin") + ":/usr/bin:/bin",
        "HTTP_PROXY": "http://127.0.0.1:9",
        "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "socks5://127.0.0.1:9",
    })
    return environment

def loader_inspection(environment: dict[str, str]) -> dict:
    # ldd is informational and runs only on the fixed, trusted private QGIS CLI.
    target = TARGET / "bin/qgis_process"
    p = subprocess.run(["/usr/bin/ldd", str(target)], env=environment,
                       capture_output=True, text=True, timeout=35, check=False)
    lines = (p.stdout + "\n" + p.stderr).splitlines()
    missing = []
    private = system = 0
    for line in lines:
        item = line.strip()
        match = re.match(r"^([a-zA-Z0-9_.+-]+)\s+=>\s+not found\b", item)
        if match:
            missing.append(match.group(1))
        elif " => " in item:
            if str(TARGET) in item:
                private += 1
            elif "/usr/" in item or "/lib/" in item:
                system += 1
    return {
        "ldd_exit_code": p.returncode,
        "linked_private_libraries": private,
        "linked_ubuntu_base_libraries": system,
        "unresolved_sonames": sorted(set(missing)),
        "transitive_dependency_isolation_certified": False,
        "host_libraries_not_removed": True,
    }

def certify() -> dict:
    guard()
    with tempfile.TemporaryDirectory(prefix=".f9-qgis-native-", dir=RUNTIME) as td:
        work = Path(td)
        env = private_env(work)
        deps = loader_inspection(env)
        child = work / "native-buffer-child.py"
        child.write_text(CHILD, encoding="utf-8")
        try:
            result = subprocess.run(
                [str(TARGET / "bin/python"), str(child), str(work), str(TARGET)],
                cwd=work, env=env, capture_output=True, text=True,
                timeout=90, check=False)
        except subprocess.TimeoutExpired:
            result = None
        payload = None
        output = work / "native-processing-result.json"
        if result and result.returncode == 0 and output.is_file():
            try:
                payload = json.loads(output.read_text(encoding="utf-8"))
                if (payload.get("native_buffer_algorithm_executed") is not True
                        or payload.get("geojson_export_and_reparse") is not True
                        or payload.get("independent_geojson_area_verified") is not True
                        or payload.get("feature_count") != 1
                        or not (work / "buffer-5m.geojson").is_file()):
                    payload = None
            except (ValueError, OSError):
                payload = None
        report = {
            "status": "pass" if payload is not None else "partial_blocked",
            "active_release": EXPECTED,
            "fallback_preserved": FALLBACK,
            "catalog_entries": 450,
            "qgis_version": "4.2.3",
            "native_processing_certified": payload is not None,
            "native_processing": payload,
            "child_exit_code": result.returncode if result else None,
            # Retain only a short error suffix; redact potential private root paths.
            "diagnostic": re.sub(re.escape(str(ROOT)), "<FERRARI>",
                                  ((result.stderr or result.stdout)[-500:]
                                   if result is not None else "processing timeout")),
            "ldd": deps,
            "gui_certified": False,
            "all_providers_certified": False,
            "other_projects_modified": False,
            "ubuntu_apt_modified": False,
            "test_artifacts_removed": True,
        }
        return report

def main() -> int:
    if sys.argv[1:] != ["--certify"]:
        raise SystemExit("F9_QGIS_CERTIFY_MODE_REQUIRED")
    try:
        report = certify()
        print(json.dumps(report, sort_keys=True), flush=True)
        print("FERRARI_QGIS_REAL_CERTIFICATE=" + report["status"].upper(), file=sys.stderr)
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)[-350:],
                          "ubuntu_apt_modified": False,
                          "other_projects_modified": False}), flush=True)
        return 3

if __name__ == "__main__":
    sys.exit(main())
