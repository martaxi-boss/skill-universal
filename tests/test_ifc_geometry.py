"""Unit checks for IFC mesh metadata, with mocked API on the CI runner.

Real IfcOpenShell/OCCT geometry generation is tested separately on the VPS.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import patch
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class FakeElement:
    def __init__(self, index, represented=True, fails=False):
        self.index = index
        self.GlobalId = "ferrari-geom-" + str(index)
        self.Name = "Sample wall " + str(index)
        self.Representation = SimpleNamespace(Representations=[1]) if represented else None
        self.fails = fails

    def id(self):
        return self.index

    def is_a(self):
        return "IfcWall"


class FakeSettings:
    def __init__(self):
        self.options = {}

    def set(self, name, value):
        self.options[name] = value


class FakeModel:
    schema = "IFC4"

    def __init__(self, elements):
        self.elements = elements
        self.project = SimpleNamespace(GlobalId="ferrari-demo-project", Name="Ferrari")

    def by_type(self, typ):
        if typ == "IfcElement":
            return self.elements
        if typ == "IfcProject":
            return [self.project]
        return []

    def __iter__(self):
        return iter(self.elements)


class IfcGeometryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.settings = FakeSettings()
        fake = ModuleType("ifcopenshell")
        fake.version = "0.9.0.post1"
        fake.geom = ModuleType("ifcopenshell.geom")
        fake.geom.settings = lambda: cls.settings
        fake.geom.create_shape = lambda _settings, el: cls.create_shape(el)
        cls.fake = fake
        with patch.dict("sys.modules", {"ifcopenshell": fake, "ifcopenshell.geom": fake.geom}):
            spec = importlib.util.spec_from_file_location(
                "ferrari_geometry_worker_test", ROOT / "engine/ifc_inspector.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            cls.worker = module

    @staticmethod
    def create_shape(element):
        if element.fails:
            raise RuntimeError("Geometry failed")
        verts = (0, 0, 0, 5, 0, 0, 5, 0.2, 3, 0, 0.2, 3)
        return SimpleNamespace(geometry=SimpleNamespace(
            verts=verts, faces=(0, 1, 2, 0, 2, 3)
        ))

    def test_geometry_measured_bounding_box_in_metres(self):
        info = self.worker.geometry_inventory(FakeModel([FakeElement(1)]))
        self.assertEqual(info["counts"]["mesh_measured"], 1)
        mesh = info["elements"][0]
        self.assertEqual(mesh["world_bounds"]["size_m"], [5.0, 0.2, 3.0])
        self.assertEqual(mesh["triangle_count"], 2)
        self.assertEqual(self.settings.options["use-world-coords"], True)

    def test_explicit_missing_representation_never_looks_certified(self):
        info = self.worker.geometry_inventory(FakeModel([FakeElement(2, represented=False)]))
        self.assertEqual(info["counts"]["mesh_measured"], 0)
        self.assertEqual(info["counts"]["no_representation"], 1)
        self.assertNotIn("world_bounds", info["elements"][0])

    def test_geometry_failures_remain_visible_and_dont_hide_others(self):
        info = self.worker.geometry_inventory(FakeModel([
            FakeElement(1, fails=True), FakeElement(2)
        ]))
        self.assertEqual(info["counts"]["mesh_measured"], 1)
        self.assertEqual(info["counts"]["geometry_error"], 1)
        self.assertEqual(info["elements"][0]["error_type"], "RuntimeError")

    def test_geometry_reports_truncation(self):
        elements = [FakeElement(i, represented=False) for i in range(120)]
        info = self.worker.geometry_inventory(FakeModel(elements))
        self.assertTrue(info["truncated"])
        self.assertEqual(info["total_ifc_elements"], 120)
        self.assertEqual(info["inspected_elements"], 100)

    def test_reject_nan_and_invalid_vertex_buffer(self):
        with self.assertRaises(ValueError):
            self.worker._mesh_bounds((1, 2))
        with self.assertRaises(ValueError):
            self.worker._mesh_bounds((float("nan"), 1, 1))

    def test_existing_ifc_summary_also_contains_geometry(self):
        with tempfile.TemporaryDirectory() as folder:
            inp = Path(folder) / "sample.ifc"
            out = Path(folder) / "report.json"
            inp.write_text("FAKE IFC FILE")
            self.fake.open = lambda _name: FakeModel([FakeElement(1)])
            result = self.worker.inspect(str(inp), str(out))
            self.assertEqual(result["geometry"]["counts"]["mesh_measured"], 1)
            self.assertEqual(result["entities_by_type"]["IfcWall"], 1)
            self.assertTrue(out.is_file())


if __name__ == "__main__":
    unittest.main()
