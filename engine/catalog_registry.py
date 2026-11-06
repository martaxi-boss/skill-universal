"""The ONE persisted Ferrari catalog and its backwards-compatible in-memory views.

Only engine/catalog.json stores programs, functions, dependencies and providers.
No separate REA catalog, typed-action manifest or operation registry is persisted.
The old dispatcher interfaces read projections built from functions[] at runtime.
"""
from __future__ import annotations

import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"


def read_catalog(path: Path | str | None = None) -> dict:
    """Return the single catalog plus *ephemeral* legacy dispatcher projections."""
    source = Path(path) if path is not None else CATALOG_PATH
    doc = json.loads(source.read_text(encoding="utf-8"))
    if doc.get("schema") != 2 or doc.get("functions_schema") != 1:
        raise ValueError("Unsupported Ferrari universal catalog schema")
    functions = doc.get("functions")
    if not isinstance(functions, list):
        raise ValueError("Ferrari universal functions must be a single list")

    programs = {item["id"]: item for item in doc["tools"]}
    seen = set()
    actions = []
    approved_mcp = []
    for item in functions:
        name = item.get("name")
        kind = item.get("kind")
        program = item.get("program")
        identity = item.get("id")
        expected_prefix = {
            "operation": "operation:", "invoke": "invoke:",
            "mcp_capability": "rea:",
        }.get(kind)
        if (not isinstance(name, str) or not name
                or not isinstance(identity, str)
                or not expected_prefix or identity != expected_prefix + name
                or identity in seen or program not in programs
                or item.get("category") is None):
            raise ValueError("Invalid or duplicate Ferrari universal function")
        seen.add(identity)
        invocation = item.get("invocation")
        if not isinstance(invocation, dict):
            raise ValueError("Missing Ferrari function invocation descriptor")
        if kind == "operation":
            if invocation != {"kind": "operation", "operation": name}:
                raise ValueError("Invalid Ferrari base operation route")
            programs[program].setdefault("base_operations", []).append(name)
        elif kind == "invoke":
            if invocation != {"kind": "invoke", "action": name}:
                raise ValueError("Invalid Ferrari typed-action route")
            action = {
                "id": name, "tool": program, "category": item["category"],
                **{k: v for k, v in item.items() if k not in {
                    "id", "name", "kind", "program", "category", "invocation"}},
            }
            actions.append(action)
        else:
            if program != "rea" or invocation != {
                    "kind": "rea-mcp", "method": "tools/call", "name": name}:
                raise ValueError("Invalid Ferrari MCP function route")
            approved_mcp.append(name)

    # These are *computed* compatibility views, NEVER extra catalog files.
    doc["actions"] = actions
    doc["mcp_capabilities"]["names"] = approved_mcp
    if doc["counts"].get("functions") != len(functions):
        raise ValueError("Ferrari function count mismatch")
    if doc["counts"].get("all_catalog_entries") != (
            len(doc["tools"]) + len(functions) + len(doc["dependencies"])
            + len(doc["providers"])):
        raise ValueError("Ferrari universal catalog count mismatch")
    return doc
