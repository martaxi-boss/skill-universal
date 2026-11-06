"""F9: private GIS synthetic test is CPU-only and never modifies external projects."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import os
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/"install/vps-phase9-functional-qgis.py"
SPEC=spec_from_file_location("f9_private_gis", SRC)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class PrivateGeospatialSmokeTests(unittest.TestCase):
    def test_source_contains_real_qgis_geometry_roundtrip_and_cpu_renderer(self):
        child=m.CHILD
        self.assertIn("QgsGeometry.fromWkt", child)
        self.assertIn("geom.area() - 5000.0", child)
        self.assertIn("QPainter(img)", child)
        self.assertIn("QImage(640, 400", child)
        self.assertNotIn("app.initQgis()",child)
        self.assertIn("LIBGL_ALWAYS_SOFTWARE", SRC.read_text())
        self.assertIn('"real_property_measurements_used": False', child)

    def test_no_global_install_or_other_project_mutation(self):
        source=SRC.read_text(encoding="utf-8")
        for denied in ("sudo ", "apt-get ", "apt install",
                       "subprocess.Popen", "shell=True", "os.system",
                       "git reset", "git pull", "rm -rf",
                       "/srv/projects/pink-iptv", "/srv/projects/fadego"):
            self.assertNotIn(denied,source)
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(AssertionError,"root"):
                m.guard()

    def test_qgis_private_environment_scope(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"skill-universal"
            target=root/"tools/qgis-4.2.3-condaforge"
            runtime=root/".runtime"
            (target/"share/qgis/python").mkdir(parents=True)
            runtime.mkdir()
            with patch.multiple(m,ROOT=root,TARGET=target,RUNTIME=runtime):
                env=m.env(runtime)
            self.assertEqual(env["QGIS_PREFIX_PATH"],str(target))
            self.assertEqual(env["LD_LIBRARY_PATH"],str(target/"lib"))
            self.assertIn(str(target),env["PYTHONPATH"])
            self.assertEqual(env["QT_QPA_PLATFORM"],"offscreen")
            self.assertEqual(env["LIBGL_ALWAYS_SOFTWARE"],"1")

    def test_fake_completed_synthetic_gis_keeps_temp_clean(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"skill-universal"
            runtime=root/".runtime"
            runtime.mkdir(parents=True)
            target=root/"tools/qgis-4.2.3-condaforge"
            target.mkdir(parents=True)
            def fake_subprocess(cmd,**kwargs):
                work=Path(cmd[2])
                (work/"synthetic-parcel.geojson").write_text(
                    '{"type":"FeatureCollection","features":[]}')
                (work/"synthetic-parcel.png").write_bytes(b"\\x89PNG\\r\\n\\x1a\\n")
                (work/"child-result.json").write_text(json.dumps({
                    "status":"pass", "wkt_geometry_valid":True,
                    "geojson_roundtrip_verified":True,
                    "real_property_measurements_used":False,
                    "cpu_png_render":True}))
                return SimpleNamespace(returncode=0,stdout="PASS",stderr="")
            with patch.multiple(m,ROOT=root,RUNTIME=runtime,TARGET=target),\
                 patch.object(m,"guard"),\
                 patch.object(m.subprocess,"run",side_effect=fake_subprocess):
                result=m.certify()
            self.assertEqual(result["status"],"pass")
            self.assertTrue(result["cpu_png_render"])
            self.assertTrue(result["temp_files_cleaned_after_test"])
            self.assertEqual(list(runtime.iterdir()),[])

    def test_real_failure_never_claims_gis_certification(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"skill-universal"
            runtime=root/".runtime"
            runtime.mkdir(parents=True)
            target=root/"tools/qgis-4.2.3-condaforge"
            target.mkdir(parents=True)
            with patch.multiple(m,ROOT=root,RUNTIME=runtime,TARGET=target),\
                 patch.object(m,"guard"),\
                 patch.object(m.subprocess,"run",return_value=SimpleNamespace(
                     returncode=2,stdout="",stderr="import failed")):
                with self.assertRaisesRegex(RuntimeError,"REAL_GEOMETRY_FAILED"):
                    m.certify()
            self.assertEqual(list(runtime.iterdir()),[])


if __name__=="__main__":
    unittest.main()
