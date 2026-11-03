"""Ferrari professional workflow coordinator: independent of any AI harness.

The host AI submits structured steps. Ubuntu executes ONLY known Ferrari tools.
A dry run is the default. No arbitrary commands, URLs, or paid model calls.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import uuid

from engine import ferrari, tool_runtime

ID_PATTERN = re.compile(r"^[a-z][a-z0-9_-]{0,39}$")
MAX_STEPS = 24
MAX_PARALLEL = 4


def validate_workflow(spec: dict) -> list[dict]:
    """Validate a small acyclic graph of typed operations without side effects."""
    if not isinstance(spec, dict) or spec.get("version") != 1:
        raise ValueError("Workflow must be an object with version=1")
    raw = spec.get("steps")
    if not isinstance(raw, list) or not 1 <= len(raw) <= MAX_STEPS:
        raise ValueError("Workflow requires 1 to 24 steps")
    ids = set()
    steps = []
    for item in raw:
        if not isinstance(item, dict):
            raise ValueError("Every step must be an object")
        allowed={"id", "operation", "depends_on", "input", "input_from", "title", "layout"}
        if item.get("operation")=="tool":
            allowed.update({"tool","action","query"})
        unknown = set(item) - allowed
        if unknown:
            raise ValueError("Unrecognized step fields: " + ", ".join(sorted(unknown)))
        name, op = item.get("id"), item.get("operation")
        if not isinstance(name, str) or not ID_PATTERN.fullmatch(name) or name in ids:
            raise ValueError("Invalid or duplicate step ID")
        if op not in ferrari.OPS and op!="tool":
            raise ValueError("Unsupported operation in " + name)
        tool=action=query=None
        if op=="tool":
            tool=item.get("tool")
            action=item.get("action")
            spec=tool_runtime.specs().get(action)
            if not spec or spec["tool"]!=tool:
                raise ValueError("Unknown or mismatched tool action")
            query=item.get("query")
            needs_query="{query}" in spec["args"]
            if needs_query and (not isinstance(query,str) or not 1<=len(query.strip())<=200):
                raise ValueError("Tool action requires a text query")
            if not needs_query and query is not None:
                raise ValueError("Tool action does not support query")
        deps = item.get("depends_on", [])
        if not isinstance(deps, list) or any(not isinstance(v, str) for v in deps):
            raise ValueError("depends_on must be a list of IDs")
        if name in deps or len(deps) != len(set(deps)):
            raise ValueError("Duplicate or self dependency in " + name)
        inp, source_step = item.get("input"), item.get("input_from")
        if inp is not None and (not isinstance(inp, str) or not inp):
            raise ValueError("input must be a nonempty file path")
        if source_step is not None and (not isinstance(source_step, str) or source_step not in deps):
            raise ValueError("input_from must be listed in depends_on")
        if inp and source_step:
            raise ValueError("Use either input or input_from, not both")
        if op not in {"web-template", "svg-poster", "blender-house"} and not (inp or source_step):
            raise ValueError("Operation " + op + " needs input or input_from")
        if op in {"web-template", "svg-poster"} and (inp or source_step):
            raise ValueError("Generator " + op + " does not accept input")
        title = item.get("title", "Novo Projeto")
        if not isinstance(title, str) or len(title) > 120:
            raise ValueError("Invalid title in " + name)
        layout = item.get("layout", "landing")
        if not isinstance(layout, str) or layout not in ferrari.LAYOUTS:
            raise ValueError("Unknown website layout")
        ids.add(name)
        steps.append({"id": name, "operation": op, "depends_on": list(deps),
                      "input": inp, "input_from": source_step, "title": title, "layout": layout,
                      "tool":tool,"action":action,"query":query})
    for step in steps:
        if not set(step["depends_on"]).issubset(ids):
            raise ValueError("Unknown dependencies in " + step["id"])
    remaining = {s["id"]: set(s["depends_on"]) for s in steps}
    completed = set()
    while remaining:
        ready = [n for n, deps in remaining.items() if deps.issubset(completed)]
        if not ready:
            raise ValueError("Cycle in workflow dependencies")
        for n in ready:
            completed.add(n)
            del remaining[n]
    return steps


def orchestrate(spec: dict, workspace: str, execute: bool = False, max_parallel: int = 2) -> dict:
    """Run independent tasks in bounded parallel waves and persist an evidence report."""
    steps = validate_workflow(spec)
    if type(max_parallel) is not int or not 1 <= max_parallel <= MAX_PARALLEL:
        raise ValueError("max_parallel must be between 1 and 4")
    if not isinstance(workspace, str) or not workspace.strip():
        raise ValueError("A workspace directory is required")
    result = {
        "engine": "ferrari-ubuntu", "mode": "execute" if execute else "preview",
        "steps": len(steps), "max_parallel": max_parallel,
        "workflow": steps, "requires_ubuntu": True,
        "external_agents_invoked": False, "paid_providers_invoked": False,
        "notice": "Only typed local Ferrari operations; uninstalled tools will fail, not be simulated."
    }
    if not execute:
        return result
    if not ferrari.system()["distro"] == "ubuntu":
        raise RuntimeError("Workflow execution requires Ubuntu")
    root = Path(workspace).expanduser()
    if root.is_symlink():
        raise ValueError("Workspace cannot be a symlink")
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    job = root / ("ferrari-" + uuid.uuid4().hex)
    job.mkdir(mode=0o700)
    by_id = {s["id"]: s for s in steps}
    waiting = set(by_id)
    completed = {}
    failed = {}
    started = datetime.now(timezone.utc).isoformat()

    def call(step):
        input_file = step["input"]
        if step["input_from"]:
            predecessor = completed[step["input_from"]]
            artifacts = predecessor.get("artifacts", [])
            if not artifacts or not Path(artifacts[0]).is_file():
                raise ValueError("Dependency has no regular-file artifact: " + step["input_from"])
            input_file = artifacts[0]
        if step["operation"]=="tool":
            return tool_runtime.invoke(step["action"],input_file,str(job/step["id"]),step["query"])
        return ferrari.run(step["operation"], str(job / step["id"]),
                           source=input_file, title=step["title"], layout=step["layout"])

    with ThreadPoolExecutor(max_workers=max_parallel) as pool:
        while waiting and not failed:
            ready = [by_id[n] for n in sorted(waiting)
                     if all(dep in completed for dep in by_id[n]["depends_on"])]
            if not ready:
                raise RuntimeError("Unresolved workflow dependency")
            # Each wave completes before dependent operations are launched.
            for i in range(0, len(ready), max_parallel):
                batch = ready[i:i + max_parallel]
                futures = {pool.submit(call, step): step["id"] for step in batch}
                for future in as_completed(futures):
                    name = futures[future]
                    try:
                        completed[name] = future.result()
                    except Exception as exc:
                        failed[name] = {"error": str(exc)[:700], "error_type": type(exc).__name__}
                    waiting.remove(name)
                if failed:
                    break
    report = {
        "job_id": job.name, "started": started,
        "finished": datetime.now(timezone.utc).isoformat(),
        "status": "failed" if failed else "completed",
        "completed": completed, "failed": failed,
        "blocked": sorted(waiting), "output_directory": str(job),
        "external_agents_invoked": False, "paid_providers_invoked": False
    }
    log = job / "report.json"
    log.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {**result, "result": report, "report_file": str(log)}


def main(argv=None):
    parser = argparse.ArgumentParser(description="Independent Ferrari Ubuntu workflow orchestrator")
    parser.add_argument("--plan", required=True, help="Local JSON specification (not a shell script)")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--execute", action="store_true", help="Default is a read-only dry run")
    parser.add_argument("--max-parallel", type=int, default=2)
    args = parser.parse_args(argv)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    response = orchestrate(plan, args.workspace, args.execute, args.max_parallel)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if response.get("result", {}).get("status") == "failed":
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        sys.exit(2)
