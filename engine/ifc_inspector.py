"""Semantic and bounded geometric IFC inspection by Ferrari's existing IfcOpenShell.

Reports triangulated mesh bounds where an IFC element actually has geometry.
Does NOT certify structural safety, IFC validity, net quantities, clash detection,
building regulations or model completeness. No extra executor or install.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import sys

import ifcopenshell
import ifcopenshell.geom

MAX_GEOMETRY_ELEMENTS = 100


def _mesh_bounds(vertices):
    """Bounds of IfcOpenShell world-coordinate triangles (metres)."""
    if not vertices or len(vertices) % 3:
        raise ValueError("Invalid or empty geometry vertex buffer")
    if not all(math.isfinite(float(v)) for v in vertices):
        raise ValueError("Non-finite geometry coordinates")
    axes = [vertices[offset::3] for offset in range(3)]
    low = [min(v) for v in axes]
    high = [max(v) for v in axes]
    return {
        "min_m": [round(float(v), 5) for v in low],
        "max_m": [round(float(v), 5) for v in high],
        "size_m": [round(float(b - a), 5) for a, b in zip(low, high)],
    }


def geometry_inventory(model):
    """Measure represented IFC elements only; distinguish absence from failures."""
    elements = sorted(model.by_type("IfcElement"), key=lambda element: element.id())
    settings = ifcopenshell.geom.settings()
    settings.set("use-world-coords", True)
    results = []
    counts = Counter()
    for element in elements[:MAX_GEOMETRY_ELEMENTS]:
        record = {
            "guid": str(element.GlobalId),
            "type": element.is_a(),
            "name": str(element.Name or "")[:160],
        }
        if not element.Representation or not element.Representation.Representations:
            record["status"] = "no_representation"
        else:
            try:
                shape = ifcopenshell.geom.create_shape(settings, element)
                vertices = tuple(shape.geometry.verts)
                faces = tuple(shape.geometry.faces)
                if not faces or len(faces) % 3:
                    raise ValueError("Empty/invalid triangulation")
                record.update({
                    "status": "mesh_measured",
                    "vertex_count": len(vertices) // 3,
                    "triangle_count": len(faces) // 3,
                    "world_bounds": _mesh_bounds(vertices),
                })
            except (RuntimeError, ValueError, TypeError, AttributeError, OverflowError) as exc:
                record["status"] = "geometry_error"
                record["error_type"] = type(exc).__name__
        counts[record["status"]] += 1
        results.append(record)
    total = len(elements)
    return {
        "kind": "triangulated_world_coordinate_bounds",
        "units": "metres",
        "total_ifc_elements": total,
        "inspected_elements": len(results),
        "sample_limit": MAX_GEOMETRY_ELEMENTS,
        "truncated": total > len(results),
        "counts": {
            "mesh_measured": counts["mesh_measured"],
            "no_representation": counts["no_representation"],
            "geometry_error": counts["geometry_error"],
        },
        "elements": results,
        "notice": (
            "Bounding boxes from triangulated geometry, not exact net areas, "
            "volumes, clash/structural tests or comprehensive IFC validation."
        ),
    }


def inspect(input_path: str, output_path: str) -> dict:
    source = Path(input_path)
    if source.suffix.lower() != ".ifc" or not source.is_file() or source.is_symlink():
        raise ValueError("A regular .ifc input file is required")
    if source.stat().st_size > 2_000_000 or source.stat().st_size == 0:
        raise ValueError("Invalid IFC file size")
    model = ifcopenshell.open(str(source))
    if model is None:
        raise ValueError("IfcOpenShell did not parse a model")

    types = Counter(entity.is_a() for entity in model)
    projects = [
        {"guid": str(x.GlobalId), "name": str(x.Name or "")[:160]}
        for x in model.by_type("IfcProject")[:20]
    ]
    warning = []
    if len(projects) != 1:
        warning.append("Expected one IfcProject for a typical standalone IFC model")
    geometry = geometry_inventory(model)
    if geometry["truncated"]:
        warning.append("Geometry scan includes only the first 100 IFC elements")
    report = {
        "format": "IFC",
        "schema": model.schema,
        "engine": "IfcOpenShell",
        "ifcopenshell_version": str(ifcopenshell.version),
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "total_entities": sum(types.values()),
        "entities_by_type": dict(sorted(types.items())),
        "projects": projects,
        "geometry": geometry,
        "warnings": warning,
        "scope": "semantic entity inventory and bounded geometric mesh bounds only",
    }
    target = Path(output_path)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: ifc_inspector.py INPUT.ifc OUTPUT.json")
    inspect(sys.argv[1], sys.argv[2])
