"""CSV profiles using installed Ferrari-owned DuckDB or Polars environments.

This is a typed adapter of the existing Ferrari runtime, not a new service.
Only the CSV input and the requested JSON artifact are read/written.
"""
from __future__ import annotations

import argparse
from datetime import date, datetime
import importlib
import json
from pathlib import Path
import sys


def _json_value(value):
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, (bytes, bytearray)):
        return value.hex()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(k): _json_value(v) for k, v in value.items()}
    return str(value)


def profile(library: str, source: Path) -> dict:
    """Produce an actual CSV sample and schema with the selected Python library."""
    if library not in {"duckdb", "polars"}:
        raise ValueError("Unsupported Ferrari CSV engine")
    if source.suffix.lower() != ".csv" or not source.is_file() or source.is_symlink():
        raise ValueError("CSV input must be a regular file")
    module = importlib.import_module(library)
    if library == "polars":
        table = module.read_csv(str(source))
        columns = [{"name": name, "type": str(dtype)}
                   for name, dtype in table.schema.items()]
        total_rows = table.height
        sample = table.head(5).to_dicts()
    else:
        connection = module.connect(database=":memory:")
        try:
            relation = connection.read_csv(str(source))
            columns = [{"name": name, "type": str(dtype)}
                       for name, dtype in zip(relation.columns, relation.types)]
            total_rows = int(relation.aggregate("count(*)").fetchone()[0])
            sample_rows = relation.limit(5).fetchall()
            sample = [dict(zip(relation.columns, row)) for row in sample_rows]
        finally:
            connection.close()
    return {
        "status": "completed",
        "executor": library,
        "library_version": str(module.__version__),
        "source": source.name,
        "rows": total_rows,
        "columns": columns,
        "sample": _json_value(sample),
        "sample_size": len(sample),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Ferrari isolated CSV data profiling")
    parser.add_argument("library", choices=("duckdb", "polars"))
    parser.add_argument("input_file", type=Path)
    parser.add_argument("output_file", type=Path)
    args = parser.parse_args(argv)
    out = args.output_file
    if out.exists() or out.is_symlink():
        raise FileExistsError("Existing Ferrari result cannot be overwritten")
    result = profile(args.library, args.input_file)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False,
                              allow_nan=False, default=str) + "\n",
                   encoding="utf-8")


if __name__ == "__main__":
    try:
        main()
    except (OSError, RuntimeError, ValueError, ImportError) as exc:
        print("FERRARI_DATA_PROFILE_FAILED=" + type(exc).__name__ + ": " + str(exc)[:200],
              file=sys.stderr)
        sys.exit(2)
