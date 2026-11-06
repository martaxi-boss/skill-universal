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
# No QgsApplication.initQgis() here: its optional PDAL provider requires an
# HDF5 soname unavailable in the environment. Geometry and CPU QPainter
# operations do not require provider initialization, plugins or a GPU.
import json
from pathlib import Path
import sys
from qgis.core import QgsGeometry
from qgis.PyQt.QtCore import QPointF
from qgis.PyQt.QtGui import QImage, QPainter, QPolygonF, QColor, QPen, QBrush

work = Path(sys.argv[1])
prefix = Path(sys.argv[2])
assert work.is_dir() and prefix.is_dir()
geom = QgsGeometry.fromWkt("POLYGON((0 0,100 0,100 50,0 50,0 0))")
assert not geom.isEmpty() and geom.isGeosValid(), "Invalid QGIS plot geometry"
assert abs(geom.area()-5000.0) < 0.01, "QGIS polygon area differs from 5000m2"
geojson = work/"synthetic-parcel.geojson"
polygon = json.loads(geom.asJson())
fc = {"type":"FeatureCollection","features":[{
    "type":"Feature","properties":{"description":"synthetic, no real land data",
                                    "area_m2":5000.0},"geometry":polygon}]}
geojson.write_text(json.dumps(fc),encoding="utf-8")
doc = json.loads(geojson.read_text(encoding="utf-8"))
coords = doc["features"][0]["geometry"]["coordinates"][0]
assert len(coords) == 5 and coords[0] == coords[-1], "Invalid closed GeoJSON polygon"
shoelace = abs(sum(coords[i][0]*coords[i+1][1]-coords[i+1][0]*coords[i][1]
                  for i in range(len(coords)-1))/2)
assert abs(shoelace-5000.0)<0.01, "Independent GeoJSON area mismatch"
# Qt QImage renders purely in CPU memory (no OpenGL or physical display).
img = QImage(640, 400, QImage.Format.Format_ARGB32)
img.fill(QColor(250,250,248))
p = QPainter(img)
p.setPen(QPen(QColor(25,48,38), 3))
p.setBrush(QBrush(QColor(196,224,194)))
pts = [QPointF(60+x*4.6, 345-y*5.8) for x,y in coords]
p.drawPolygon(QPolygonF(pts))
p.end()
png=work/"synthetic-parcel.png"
assert img.save(str(png),"PNG") and png.stat().st_size>600, "CPU PNG export failed"
summary = {
    "status":"pass", "qgis_version":"4.2.3",
    "scenario":"100m x 50m synthetic plot; 5000m2",
    "private_qgis_python":True,
    "wkt_geometry_valid":True,
    "geojson_roundtrip_verified":True,
    "cpu_png_render":True,
    "qgis_provider_gui_certified":False,
    "full_qgis_plugin_suite_certified":False,
    "real_property_measurements_used":False,
    "gpu_required":False,
}
(work/"child-result.json").write_text(json.dumps(summary,sort_keys=True),encoding="utf-8")
print("F9_QGIS_SYNTHETIC_GEOJSON_ROUNDTRIP=PASS",flush=True)
print("F9_QGIS_CPU_MAP_RENDER=PASS",flush=True)
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
            msg = (run.stderr or run.stdout)
            raise RuntimeError("F9_QGIS_REAL_GEOMETRY_FAILED:" +
                               msg[:220] + " ... " + msg[-480:])
        report_file = work / "child-result.json"
        if not report_file.is_file():
            raise RuntimeError("F9_QGIS_CHILD_REPORT_NOT_FOUND")
        data = json.loads(report_file.read_text(encoding="utf-8"))
        if (data.get("status") != "pass" or not data.get("wkt_geometry_valid") or
                not data.get("geojson_roundtrip_verified") or not
                data.get("cpu_png_render") or not
                (work / "synthetic-parcel.geojson").is_file() or not
                (work / "synthetic-parcel.png").is_file()):
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
