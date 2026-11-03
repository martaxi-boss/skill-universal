"""IFC semantic inventory using the *isolated* IfcOpenShell interpreter.

This is not geometric validation, structural certification, IDS testing or
construction compliance. Execute only from the Ferrari worker with a bound
input/output path. No dependency installation happens in this module.
"""
from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys

import ifcopenshell


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
    report = {
        "format": "IFC",
        "schema": model.schema,
        "engine": "IfcOpenShell",
        "ifcopenshell_version": str(ifcopenshell.version),
        "input_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "total_entities": sum(types.values()),
        "entities_by_type": dict(sorted(types.items())),
        "projects": projects,
        "warnings": warning,
        "scope": "semantic entity inventory only; no geometry/structural/IDS validation",
    }
    target = Path(output_path)
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


if __name__ == "__main__":
    if len(sys.argv) != 3:
        raise SystemExit("Usage: ifc_inspector.py INPUT.ifc OUTPUT.json")
    inspect(sys.argv[1], sys.argv[2])
