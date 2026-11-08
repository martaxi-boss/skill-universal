"""New Ferrari specialist routes must do actual work and reject unsafe inputs."""
from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from engine import catalog_registry, ferrari, program_adapters as a


def synthetic_geojson(epsg="EPSG:3857"):
    return {
        "type": "FeatureCollection",
        "crs": {"type": "name", "properties": {"name": epsg}},
        "features": [{"type": "Feature", "properties": {},
                      "geometry": {"type": "Polygon", "coordinates": [[
                          [0, 0], [100, 0], [100, 50], [0, 50], [0, 0]
                      ]]}}]
    }


class FerrariProgramAdaptersTests(unittest.TestCase):
    def test_single_universal_catalog_has_three_new_function_descriptors(self):
        doc = catalog_registry.read_catalog()
        expected = {
            "librecad-dxf-pdf": "librecad",
            "qgis-buffer-5m": "qgis",
            "godot-starter": "godot",
        }
        self.assertEqual(len(doc["tools"]), 173)
        self.assertEqual(len(doc["functions"]), 277)
        self.assertEqual(doc["counts"]["all_catalog_entries"], 455)
        for name, program in expected.items():
            with self.subTest(name=name):
                self.assertIn(name, ferrari.OPS)
                matching = [f for f in doc["functions"]
                            if f["id"] == "operation:" + name]
                self.assertEqual(len(matching), 1)
                self.assertEqual(matching[0]["program"], program)
                self.assertEqual(matching[0]["invocation"],
                                 {"kind": "operation", "operation": name})

    def test_qgis_rejects_degrees_and_unclosed_polygons(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "input.geojson"
            p.write_text(json.dumps(synthetic_geojson("EPSG:4326")),
                         encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "EPSG:3857"):
                a._validated_polygon(p)
            bad = synthetic_geojson()
            bad["features"][0]["geometry"]["coordinates"][0][-1] = [0, 1]
            p.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Closed"):
                a._validated_polygon(p)

    def test_qgis_validated_shape_is_metric_without_code_injection(self):
        with tempfile.TemporaryDirectory() as temp:
            p = Path(temp) / "input.geojson"
            p.write_text(json.dumps(synthetic_geojson()), encoding="utf-8")
            wkt, area = a._validated_polygon(p)
            self.assertEqual(area, 5000)
            self.assertEqual(wkt, "POLYGON((0 0,100 0,100 50,0 50,0 0))")

    def test_godot_generates_real_scene_and_checks_engine_exit(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".runtime").mkdir()
            exe = root / "tools/godot"
            exe.parent.mkdir()
            exe.write_bytes(b"#!/bin/sh\nexit 0\n")
            exe.chmod(0o700)
            folder = root / "job/artifacts"
            with (patch.object(a, "HOME", root),
                  patch.object(a, "GODOT", exe),
                  patch.object(a, "_run", return_value=subprocess.CompletedProcess(
                      args=["godot"], returncode=0, stdout="Godot", stderr=""))):
                identity, artifacts = a.godot_starter(folder)
                self.assertIn(str(exe), identity)
                self.assertEqual(len(artifacts), 3)
                self.assertTrue(all(x.is_file() for x in artifacts))
                record = json.loads((folder / "godot-starter-report.json").read_text())
                self.assertTrue(record["status"] == "completed")
                self.assertFalse(record["playable_game_certified"])

    def test_godot_refuses_false_success_when_engine_fails(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / ".runtime").mkdir()
            exe = root / "godot"
            exe.write_bytes(b"#!/bin/sh\nexit 2\n")
            exe.chmod(0o700)
            with (patch.object(a, "HOME", root),
                  patch.object(a, "GODOT", exe),
                  patch.object(a, "_run", return_value=subprocess.CompletedProcess(
                      args=["godot"], returncode=2, stdout="", stderr="failed"))):
                with self.assertRaisesRegex(RuntimeError, "Godot"):
                    a.godot_starter(root / "job/artifacts")

    def test_librecad_rejects_invalid_dxf_before_launch(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            file = root / "drawing.dxf"
            file.write_bytes(b"not a DXF")
            with patch.object(a, "HOME", root):
                with self.assertRaises(ValueError):
                    a.librecad_dxf_pdf(file, root / "artifacts")

    def test_guards_keep_execution_private_and_no_shell(self):
        source = Path(a.__file__).read_text(encoding="utf-8")
        self.assertIn("shell=False", source)
        self.assertIn("start_new_session=True", source)
        self.assertIn("os.killpg", source)
        self.assertIn('native:buffer', source)
        self.assertIn('"dxf2pdf"', source)
        self.assertIn('"--headless"', source)
        self.assertNotIn("shell=True", source)
        self.assertNotIn("subprocess.Popen([user", source)


if __name__ == "__main__":
    unittest.main()
