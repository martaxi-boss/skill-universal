"""Usage: python3 -m engine.cli <doctor|catalog|providers|plan|run>."""
import argparse
import json
from pathlib import Path
import sys
from .core import environment, execute, inventory, plan, providers


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="universal-motor", description="Motor Universal Linux (prototipo independente)")
    s = p.add_subparsers(dest="command", required=True)
    s.add_parser("doctor")
    cat = s.add_parser("catalog")
    cat.add_argument("--category", choices=["dev", "data", "reverse", "mobile", "media", "docs", "web"])
    s.add_parser("providers")
    pl = s.add_parser("plan")
    pl.add_argument("request")
    run = s.add_parser("run")
    run.add_argument("request")
    run.add_argument("--title", default="Projeto Criativo")
    run.add_argument("--output", type=Path, required=True)
    run.add_argument("--input", type=Path)
    a = p.parse_args(argv)
    try:
        data = {
            "doctor": lambda: environment(),
            "catalog": lambda: inventory(a.category),
            "providers": lambda: providers(),
            "plan": lambda: plan(a.request),
            "run": lambda: execute(a.request, a.output, a.title, a.input),
        }[a.command]()
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, NotImplementedError) as e:
        print(json.dumps({"status": "error", "reason": str(e)}, ensure_ascii=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
