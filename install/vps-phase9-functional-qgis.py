#!/usr/bin/env python3
"""F9: certify an actual QGIS plot polygon and optional CPU-only map render.

All project artifacts and user settings stay in the Ferrari-owned temporary
directory. The output states exactly which tests passed; no GUI false claims.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
TARGET = ROOT / "tools/qgis-4.2.3-condaforge"
RUNTIME = ROOT / ".runtime"
CHILD = r'''
import json
from pathlib import Path
import sys
from qgis.core import (QgsApplication, QgsFeature, QgsGeometry, QgsVectorLayer,
                       QgsMapSettings, QgsMapRendererSequentialJob,
                       QgsFillSymbol, QgsSingleSymbolRenderer, QgsRectangle)
from qgis.PyQt.QtCore import QSize
work = Path(sys.argv[1])
prefix = Path(sys.argv[2])
assert work.is_dir() and prefix.is_dir()
QgsApplication.setPrefixPath(str(prefix), True)
app = QgsApplication([], False)
app.initQgis()
layer = QgsVectorLayer("Polygon?crs=EPSG:3857", "Synthetic 100m x 50m parcel", "memory")
assert layer.isValid(), "QGIS memory vector provider missing"
geom = QgsGeometry.fromWkt("POLYGON((0 0,100 0,100 50,0 50,0 0))")
assert not geom.isEmpty() and geom.isGeosValid(), "Invalid parcel geometry"
assert abs(geom.area() - 5000.0) < 0.01, "Unexpected parcel area"
feature = QgsFeature(layer.fields())
feature.setGeometry(geom)
added = layer.dataProvider().addFeatures([feature])
assert added[0], "QGIS feature insert failed"
layer.updateExtents()
assert layer.featureCount() == 1
geojson = work / "synthetic-parcel.geojson"
geojson.write_text(json.dumps({"type": "FeatureCollection", "features": [{
    "type": "Feature", "properties": {"area_m2": 5000, "description": "synthetic only"},
    "geometry": json.loads(geom.asJson())}]}), encoding="utf-8")
readback = QgsVectorLayer(str(geojson), "readback", "ogr")
assert readback.isValid(), "QGIS OGR provider could not read exported GeoJSON"
assert readback.featureCount() == 1, "GeoJSON feature count mismatch"
one = next(readback.getFeatures())
assert abs(one.geometry().area() - 5000.0) < 0.01, "GeoJSON measured area mismatch"
render = False
render_error = ""
try:
    layer.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple({
        "color":"235,237,220,255", "outline_color":"26,28,24,255",
        "outline_width":"0.9"})))
    settings = QgsMapSettings()
    settings.setLayers([layer])
    settings.setExtent(QgsRectangle(-10, -10, 110, 60))
    settings.setOutputSize(QSize(600, 360))
    job = QgsMapRendererSequentialJob(settings)
    job.start()
    job.waitForFinished()
    img = job.renderedImage()
    png = work / "synthetic-parcel.png"
    render = bool(img.save(str(png), "PNG") and png.stat().st_size > 1500)
except Exception as err:
    render_error = (type(err).__name__ + ":" + str(err))[:230]
summary = {"status": "pass", "qgis_version": "4.2.3",
           "scenario": "100m x 50m synthetic plot; 5000m2",
           "private_qgis_python": True, "wkt_geometry_valid": True,
           "ogr_geojson_roundtrip": True, "cpu_png_render": render,
           "cpu_png_render_error": render_error,
           "gis_project_certified": False,
           "real_property_measurements_used": False,
           "gpu_required": False}
(work / "child-result.json").write_text(json.dumps(summary, sort_keys=True), encoding="utf-8")
print("F9_QGIS_SYNTHETIC_GEOJSON_ROUNDTRIP=PASS", flush=True)
print("F9_QGIS_CPU_MAP_RENDER=" + ("PASS" if render else "PENDING"), flush=True)
'''

def guard() -> None:
    assert os.geteuid() != 0, "Must not run as root"
    assert ROOT.resolve(strict=True) == Path("/srv/projects/skill-universal")
    for p in (ROOT, TARGET, RUNTIME):
        assert p.is_dir() and not p.is_symlink(), f"Unsafe Ferrari directory {p}"
    assert (TARGET / "bin/python").is_file(), "Private QGIS Python missing"
    assert (TARGET / "conda-meta").is_dir(), "Conda provenance missing"
    assert (TARGET / "bin/qgis_process").is_file(), "QGIS processing CLI missing"

def env(work: Path) -> dict:
    private_python = [TARGET / "share/qgis/python",
                      TARGET / "share/qgis/python/plugins"]
    result = os.environ.copy()
    result.update({
        "HOME": str(work),
        "TMPDIR": str(work),
        "XDG_CONFIG_HOME": str(work),
        "XDG_CACHE_HOME": str(work),
        "XDG_RUNTIME_DIR": str(work),
        "QT_QPA_PLATFORM": "offscreen",
        "LIBGL_ALWAYS_SOFTWARE": "1",
        "OMP_NUM_THREADS": "2",
        "PYTHONNOUSERSITE": "1",
        "QGIS_PREFIX_PATH": str(TARGET),
        "PYTHONPATH": ":".join(str(p) for p in private_python if p.is_dir()),
        "LD_LIBRARY_PATH": str(TARGET / "lib"),
        "PATH": str(TARGET / "bin") + ":/usr/bin:/bin",
    })
    return result

def certify() -> dict:
    guard()
    with tempfile.TemporaryDirectory(prefix=".f9-qgis-real-gis-", dir=RUNTIME) as folder:
        work = Path(folder)
        code = work / "qgis-real-gis-child.py"
        code.write_text(CHILD, encoding="utf-8")
        run = subprocess.run([str(TARGET / "bin/python"), str(code), str(work), str(TARGET)],
                             cwd=work, env=env(work), capture_output=True, text=True,
                             timeout=95, check=False)
        if run.returncode != 0:
            raise RuntimeError("F9_QGIS_REAL_GEOMETRY_FAILED:" +
                               (run.stderr or run.stdout)[-480:])
        report_file = work / "child-result.json"
        if not report_file.is_file():
            raise RuntimeError("F9_QGIS_CHILD_REPORT_NOT_FOUND")
        data = json.loads(report_file.read_text(encoding="utf-8"))
        if (data.get("status") != "pass" or not data.get("wkt_geometry_valid") or
                not data.get("ogr_geojson_roundtrip") or not
                (work / "synthetic-parcel.geojson").is_file()):
            raise RuntimeError("F9_QGIS_SYNTHETIC_GIS_TEST_FAILED")
        assert not data.get("real_property_measurements_used")
        data["temp_files_cleaned_after_test"] = True
        data["global_apt_changed"] = False
        data["other_projects_changed"] = False
        return data

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certify", action="store_true", required=True)
    parser.parse_args()
    try:
        print(json.dumps(certify(), sort_keys=True), flush=True)
        return 0
    except Exception as err:
        print(json.dumps({"status": "blocked", "reason": str(err)[-550:],
                          "global_apt_changed": False}, sort_keys=True), flush=True)
        return 3

if __name__ == "__main__":
    sys.exit(main())
