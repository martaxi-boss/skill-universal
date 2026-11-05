"""Ferrari professional workflow coordinator: independent of any AI harness.

The host AI submits structured steps. Ubuntu executes ONLY known Ferrari tools.
A dry run is the default. No arbitrary commands, URLs, or paid model calls.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile
import time
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


def _atomic_json(path: Path, value: dict):
    """Durable, local-only journal update; never create files outside the job."""
    fd, temporary = tempfile.mkstemp(prefix=".journal-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, sort_keys=True, indent=2)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temporary, 0o600)
        os.replace(temporary, path)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def _production_root() -> Path | None:
    """Recognize the live Ferrari release, not a runner's temporary CLI fixtures."""
    project = Path("/srv/projects/skill-universal")
    if project.is_symlink():
        raise ValueError("Ferrari physical project directory cannot be a symlink")
    current = project / "current"
    if not (project.is_dir() and current.is_symlink()
            and (current / "engine/ferrari.py").is_file()):
        return None
    release = current.resolve(strict=True)
    if not release.is_relative_to((project / "releases").resolve(strict=True)):
        raise ValueError("Ferrari active release escapes the project")
    return project.resolve(strict=True)


def _owned_workspace(path: str) -> Path:
    """Enforce same-repo project boundaries whenever the live VPS is present."""
    root = Path(path).expanduser()
    if root.is_symlink():
        raise ValueError("Ferrari workspace cannot be a symlink")
    resolved = root.resolve()
    project = _production_root()
    if project is not None:
        if not resolved.is_relative_to(project):
            raise ValueError("Ferrari workspace must remain inside the isolated project")
        for parent in (root, *root.parents):
            if parent.is_symlink() and not parent.resolve(strict=True).is_relative_to(project):
                raise ValueError("Ferrari workspace parent escapes its isolated project")
            if parent == project:
                break
    return resolved


def _checked_artifacts(job: Path, step_id: str, answer: dict, budget: int) -> int:
    """Validate persisted artifacts before reuse; missing/tampered files fail closed."""
    if not isinstance(answer, dict) or not answer.get("confirmed"):
        raise RuntimeError("Ferrari stage did not confirm its outputs")
    artifacts = answer.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        raise RuntimeError("Ferrari stage has no output artifacts")
    stage = job / step_id
    if stage.is_symlink() or not stage.is_dir():
        raise RuntimeError("Ferrari stage directory is missing or symbolic")
    safe_root = stage.resolve(strict=True)
    total = 0
    for raw in artifacts:
        if not isinstance(raw, str):
            raise RuntimeError("Non-file Ferrari stage artifact")
        path = Path(raw)
        if path.is_symlink() or not path.exists():
            raise RuntimeError("Ferrari stage artifact is missing or symbolic")
        resolved = path.resolve(strict=True)
        if not resolved.is_relative_to(safe_root):
            raise RuntimeError("Ferrari stage artifact escapes its private folder")
        if path.is_file():
            total += path.stat().st_size
        elif path.is_dir():
            for base, folders, files in os.walk(path, followlinks=False):
                for name in folders + files:
                    entry = Path(base) / name
                    if entry.is_symlink():
                        raise RuntimeError("Ferrari stage artifact contains an unsafe link")
                    if entry.is_file():
                        total += entry.stat().st_size
                        if total > budget:
                            raise RuntimeError("Ferrari workflow artifact quota exceeded")
        else:
            raise RuntimeError("Ferrari stage produced an unsupported artifact")
        if total > budget:
            raise RuntimeError("Ferrari workflow artifact quota exceeded")
    return total


def _remove_incomplete_stage(job: Path, name: str):
    """Remove only an unfinished step's disposable directory in this private job."""
    path = job / name
    if not path.exists() and not path.is_symlink():
        return
    if path.is_symlink() or not path.is_dir() or path.resolve(strict=True).parent != job.resolve(strict=True):
        raise RuntimeError("Unsafe incomplete Ferrari stage path")
    if not shutil.rmtree.avoids_symlink_attacks:
        raise RuntimeError("Safe Ferrari stage recovery is unavailable")
    shutil.rmtree(path)


def orchestrate(spec: dict, workspace: str, execute: bool = False, max_parallel: int = 2,
                *, job_key: str | None = None, resume: bool = False,
                retry_failed: bool = False, max_runtime_seconds: int = 3600,
                max_artifacts_bytes: int = 536870912) -> dict:
    """Persist a bounded Ferrari DAG and resume only verified completed stages.

    No new coordinator or daemon. The filesystem journal is inside this Ferrari
    job. Time budgets are *cooperative*, checked between waves; a running
    subprocess cannot be hard-killed by this threading-based coordinator.
    """
    steps = validate_workflow(spec)
    if type(max_parallel) is not int or not 1 <= max_parallel <= MAX_PARALLEL:
        raise ValueError("max_parallel must be between 1 and 4")
    if not isinstance(workspace, str) or not workspace.strip():
        raise ValueError("A Ferrari workspace directory is required")
    if job_key is not None and (not isinstance(job_key, str)
                                or not ID_PATTERN.fullmatch(job_key)):
        raise ValueError("Invalid Ferrari job key")
    if resume and (job_key is None or not execute):
        raise ValueError("Ferrari resume requires execution and a fixed job key")
    if retry_failed and not resume:
        raise ValueError("Retrying a failed stage requires explicit resume")
    if (type(max_runtime_seconds) is not int or not 1 <= max_runtime_seconds <= 86400
            or type(max_artifacts_bytes) is not int
            or not 1024 <= max_artifacts_bytes <= 2147483648):
        raise ValueError("Invalid Ferrari workflow resource quotas")
    plan_hash = hashlib.sha256(
        json.dumps(steps, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    result = {
        "engine": "ferrari-ubuntu", "mode": "execute" if execute else "preview",
        "steps": len(steps), "max_parallel": max_parallel,
        "workflow": steps, "requires_ubuntu": True,
        "job_key": job_key, "plan_sha256": plan_hash,
        "max_runtime_seconds": max_runtime_seconds,
        "max_artifacts_bytes": max_artifacts_bytes,
        "external_agents_invoked": False, "paid_providers_invoked": False,
        "notice": "Ferrari local typed operations only; timeout is cooperative between waves."
    }
    if not execute:
        return result
    if ferrari.system()["distro"] != "ubuntu":
        raise RuntimeError("Workflow execution requires Ubuntu")
    root = _owned_workspace(workspace)
    root.mkdir(mode=0o700, parents=True, exist_ok=True)
    job = root / ("ferrari-" + (job_key if job_key else uuid.uuid4().hex))
    if job.is_symlink():
        raise ValueError("Ferrari job directory cannot be a symlink")
    if resume:
        if not job.is_dir():
            raise FileNotFoundError("Ferrari resume job is absent")
    else:
        job.mkdir(mode=0o700, exist_ok=False)
    if not job.resolve(strict=True).is_relative_to(root):
        raise RuntimeError("Ferrari job escaped its workspace")
    lock_path = job / ".job.lock"
    if lock_path.is_symlink():
        raise RuntimeError("Ferrari job lock is a symlink")
    fd = os.open(lock_path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW, 0o600)
    try:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("Ferrari job is already being executed") from exc
        journal = job / "journal.json"
        report_file = job / "report.json"
        started = datetime.now(timezone.utc).isoformat()
        if resume:
            if journal.is_symlink() or not journal.is_file():
                raise RuntimeError("Ferrari job has no private journal")
            state = json.loads(journal.read_text(encoding="utf-8"))
            if (state.get("version") != 1 or state.get("plan_sha256") != plan_hash
                    or state.get("max_parallel") != max_parallel
                    or state.get("max_artifacts_bytes") != max_artifacts_bytes):
                raise ValueError("Ferrari resume plan or resource policy has changed")
            if state.get("status") == "completed":
                completed = state.get("completed", {})
                for sid, answer in completed.items():
                    _checked_artifacts(job, sid, answer, max_artifacts_bytes)
                if report_file.is_symlink() or not report_file.is_file():
                    raise RuntimeError("Ferrari completed report is missing")
                report = json.loads(report_file.read_text(encoding="utf-8"))
                return {**result, "resumed": True, "reused_steps": sorted(completed),
                        "result": report, "report_file": str(report_file)}
            if state.get("status") == "failed" and not retry_failed:
                raise RuntimeError("Ferrari failed job needs explicit retry_failed")
            if state.get("status") not in {"running", "failed", "cancelled", "timed_out"}:
                raise RuntimeError("Ferrari cannot resume an unknown journal status")
            completed = state.get("completed", {})
            if not isinstance(completed, dict) or not set(completed).issubset(
                    {s["id"] for s in steps}):
                raise RuntimeError("Ferrari journal includes unknown stages")
            for sid, answer in completed.items():
                _checked_artifacts(job, sid, answer, max_artifacts_bytes)
            for sid in (s["id"] for s in steps):
                if sid not in completed:
                    _remove_incomplete_stage(job, sid)
            started = state["started"]
            state["failed"] = {}
            state["status"] = "running"
            state["attempt"] = int(state.get("attempt", 1)) + 1
        else:
            completed = {}
            state = {"version": 1, "plan_sha256": plan_hash,
                     "max_parallel": max_parallel,
                     "max_artifacts_bytes": max_artifacts_bytes,
                     "started": started, "completed": {}, "failed": {},
                     "status": "running", "attempt": 1}
        _atomic_json(journal, state)
        waiting = {s["id"] for s in steps} - set(completed)
        by_id = {s["id"]: s for s in steps}
        failed = {}
        reason = None
        reused = sorted(completed)
        clock = time.monotonic()

        def call(step):
            source = step["input"]
            if step["input_from"]:
                previous = completed[step["input_from"]]
                source = previous["artifacts"][0]
                if not Path(source).is_file():
                    raise ValueError("Dependency has no regular-file artifact")
            if source:
                item = Path(source)
                if item.is_symlink() or not item.is_file():
                    raise ValueError("Ferrari input must be a regular file")
                project = _production_root()
                if project is not None and not item.resolve(strict=True).is_relative_to(project):
                    raise ValueError("Ferrari may not read inputs outside its project")
            if step["operation"] == "tool":
                return tool_runtime.invoke(step["action"], source,
                                           str(job / step["id"]), step["query"])
            return ferrari.run(step["operation"], str(job / step["id"]),
                               source=source, title=step["title"], layout=step["layout"])

        with ThreadPoolExecutor(max_workers=max_parallel) as pool:
            while waiting and not failed:
                flag = job / "cancel.request"
                if flag.is_symlink():
                    raise RuntimeError("Ferrari cancel marker cannot be a symlink")
                if flag.is_file():
                    reason = "cancelled"
                    break
                if time.monotonic() - clock > max_runtime_seconds:
                    reason = "timed_out"
                    break
                ready = [by_id[n] for n in sorted(waiting)
                         if all(dep in completed for dep in by_id[n]["depends_on"])]
                if not ready:
                    raise RuntimeError("Unresolved Ferrari workflow dependency")
                for i in range(0, len(ready), max_parallel):
                    batch = ready[i:i + max_parallel]
                    futures = {pool.submit(call, step): step["id"] for step in batch}
                    for future in as_completed(futures):
                        sid = futures[future]
                        try:
                            answer = future.result()
                            _checked_artifacts(job, sid, answer, max_artifacts_bytes)
                            completed[sid] = answer
                        except Exception as exc:
                            failed[sid] = {"error": str(exc)[:700],
                                           "error_type": type(exc).__name__}
                        waiting.remove(sid)
                        state.update({"completed": completed, "failed": failed,
                                      "status": "failed" if failed else "running"})
                        _atomic_json(journal, state)
                    if failed:
                        break
                if time.monotonic() - clock > max_runtime_seconds and waiting:
                    reason = "timed_out"
        status = ("failed" if failed else reason if reason else "completed")
        state["status"] = status
        state["completed"] = completed
        state["failed"] = failed
        _atomic_json(journal, state)
        report = {
            "job_id": job.name, "started": started,
            "finished": datetime.now(timezone.utc).isoformat(),
            "status": status, "completed": completed, "failed": failed,
            "blocked": sorted(waiting), "output_directory": str(job),
            "attempt": state["attempt"], "plan_sha256": plan_hash,
            "reused_steps": reused, "max_runtime_seconds": max_runtime_seconds,
            "timeout_enforcement": "cooperative_between_waves",
            "max_artifacts_bytes": max_artifacts_bytes,
            "external_agents_invoked": False, "paid_providers_invoked": False,
        }
        _atomic_json(report_file, report)
        return {**result, "resumed": resume, "reused_steps": reused,
                "result": report, "report_file": str(report_file)}
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)

def main(argv=None):
    parser = argparse.ArgumentParser(description="Independent Ferrari Ubuntu workflow orchestrator")
    parser.add_argument("--plan", required=True, help="Local JSON specification (not a shell script)")
    parser.add_argument("--workspace", required=True)
    parser.add_argument("--execute", action="store_true", help="Default is a read-only dry run")
    parser.add_argument("--max-parallel", type=int, default=2)
    parser.add_argument("--job-key", help="Stable private Ferrari job ID for idempotency")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--retry-failed", action="store_true")
    parser.add_argument("--max-runtime-seconds", type=int, default=3600)
    parser.add_argument("--max-artifacts-bytes", type=int, default=536870912)
    args = parser.parse_args(argv)
    plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    response = orchestrate(plan, args.workspace, args.execute, args.max_parallel,
                           job_key=args.job_key, resume=args.resume,
                           retry_failed=args.retry_failed,
                           max_runtime_seconds=args.max_runtime_seconds,
                           max_artifacts_bytes=args.max_artifacts_bytes)
    print(json.dumps(response, ensure_ascii=False, indent=2))
    if response.get("result", {}).get("status") != "completed" and args.execute:
        return 1
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, FileNotFoundError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        sys.exit(2)
