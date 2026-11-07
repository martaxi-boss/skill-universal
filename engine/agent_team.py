"""Ferrari/Ruflo shared-host team: explicit, auditable human/AI host turns.

The *only* model reasoning happens in the authorized external host (ChatGPT,
Codex, etc.). This module never calls an LLM, provider or network endpoint.
Each turn is a separate Ferrari Skill job. The private journal allows real
role-to-role handoffs and verifiable evidence between those jobs.

The Ruflo MCP swarm is ephemeral per turn; the Ferrari-owned journal preserves
task continuity. This is not autonomous LLM inference in the VPS.
"""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import tempfile

from engine import ruflo_host, tool_runtime, rea_mcp

HOME = Path("/srv/projects/skill-universal")
SESSION_PARENT = HOME / ".runtime" / "ruflo-team-sessions"
IDENTIFIER = re.compile(r"[a-z][a-z0-9_-]{0,39}\Z")
HOSTS = frozenset({"ChatGPT", "Codex", "Claude", "other"})
MAX_ROLES = 8  # simultaneous team size, not the Ruflo specialization catalog
MAX_TASKS = 24
MAX_EVIDENCE = 12_000_000

# Instruction contracts, not another tool catalog. Additional upstream Ruflo
# types may be used if Ruflo accepts them; unknown types get generic policy.
BRIEFS = {
    "architect": ("Design the solution and acceptance criteria.",
                  "Return explicit dependencies, risks and a verifiable plan."),
    "coder": ("Implement the assigned change with approved Ferrari tools.",
              "Produce working outputs; never approve your own changes."),
    "tester": ("Test against stated acceptance criteria and real outputs.",
               "Show actual test evidence and report failures."),
    "reviewer": ("Independently compare evidence against acceptance criteria.",
                 "Reject missing proof; never approve your own work."),
    "researcher": ("Investigate supported, verifiable alternatives.",
                   "State uncertainty and distinguish research from execution."),
    "debugger": ("Localize and reproduce failures before changing code.",
                 "Record errors, inputs and correction rationale."),
    "optimizer": ("Measure before optimizing; preserve original behavior.",
                  "Supply before/after evidence rather than claims."),
    "documenter": ("Describe implementation and reproducible operation.",
                    "Keep claims in agreement with verified artifacts."),
}


def _id(value):
    return isinstance(value, str) and bool(IDENTIFIER.fullmatch(value))


def _text(value, maximum=1200, minimum=1):
    return isinstance(value, str) and minimum <= len(value.strip()) <= maximum and "\x00" not in value


def validate_job(doc):
    """Reject unsafe, unrecognized operations before touching the VPS."""
    if not isinstance(doc, dict) or doc.get("version") != 1 or doc.get("kind") != "ruflo-team":
        raise ValueError("Expected versioned Ruflo team job")
    if not _id(doc.get("team_id")):
        raise ValueError("Invalid private team ID")
    phase = doc.get("phase")
    common = {"version", "id", "kind", "team_id", "phase"}
    if phase == "start":
        if set(doc) - (common | {"host", "mission", "roles", "tasks", "input"}):
            raise ValueError("Unknown Ruflo team start fields")
        if doc.get("host") not in HOSTS or not _text(doc.get("mission"), 1000):
            raise ValueError("One authorized host and a mission are required")
        roles = doc.get("roles")
        tasks = doc.get("tasks")
        if not isinstance(roles, list) or not 2 <= len(roles) <= MAX_ROLES:
            raise ValueError("Ruflo team requires 2-8 active roles")
        if not isinstance(tasks, list) or not 1 <= len(tasks) <= MAX_TASKS:
            raise ValueError("Ruflo team requires 1-24 tasks")
        seen_roles = set()
        for role in roles:
            if not isinstance(role, dict) or set(role) != {"id", "type", "actions"}:
                raise ValueError("Role needs id, upstream Ruflo type and action allowlist")
            rid, kind, actions = role["id"], role["type"], role["actions"]
            if not _id(rid) or rid in seen_roles or not _id(kind):
                raise ValueError("Invalid or duplicated Ruflo role")
            if (not isinstance(actions, list) or len(actions) > 30 or
                    any(not isinstance(a, str) for a in actions) or len(actions) != len(set(actions))):
                raise ValueError("Invalid role action allowlist")
            available = tool_runtime.specs()
            if any(a not in available and a != "rea-mcp" for a in actions):
                raise ValueError("Role can only use Ferrari catalog actions")
            seen_roles.add(rid)
        seen_tasks = set()
        for task in tasks:
            if not isinstance(task, dict) or set(task) != {"id", "role", "reviewer", "goal", "depends_on"}:
                raise ValueError("Task needs owner, distinct reviewer, goal and dependencies")
            tid, owner, reviewer = task["id"], task["role"], task["reviewer"]
            deps = task["depends_on"]
            if not _id(tid) or tid in seen_tasks or owner not in seen_roles or reviewer not in seen_roles or owner == reviewer:
                raise ValueError("Invalid task identity or lack of independent review")
            if not _text(task["goal"], 700) or not isinstance(deps, list):
                raise ValueError("Invalid task goal or dependencies")
            if len(deps) != len(set(deps)) or any(not _id(d) or d == tid for d in deps):
                raise ValueError("Invalid task dependency IDs")
            seen_tasks.add(tid)
        if any(not set(t["depends_on"]).issubset(seen_tasks) for t in tasks):
            raise ValueError("Unknown task dependency")
        visiting, visited = set(), set()
        by_id = {t["id"]: t for t in tasks}
        def visit(tid):
            if tid in visiting:
                raise ValueError("Cyclic Ruflo team dependencies")
            if tid in visited:
                return
            visiting.add(tid)
            for dep in by_id[tid]["depends_on"]:
                visit(dep)
            visiting.remove(tid)
            visited.add(tid)
        for tid in seen_tasks:
            visit(tid)
    elif phase in {"turn", "recover", "finish", "status"}:
        extra = {"revision"} if phase != "status" else set()
        if phase == "turn":
            extra.add("turn")
        if phase == "recover":
            extra |= {"task", "reason", "acknowledge_risk"}
        if phase == "finish":
            extra.add("approval")
        if set(doc) - (common | extra):
            raise ValueError("Unknown Ruflo team turn fields")
        if phase != "status" and (type(doc.get("revision")) is not int or doc["revision"] < 0):
            raise ValueError("Explicit revision required to reject stale turns")
        if phase == "finish" and not _text(doc.get("approval"), 700, 20):
            raise ValueError("Explicit final host approval required")
        if phase == "recover" and (not _id(doc.get("task")) or not _text(doc.get("reason"), 500, 20)
                                   or doc.get("acknowledge_risk") is not True):
            raise ValueError("Recovery needs explicit idempotency-risk acknowledgement")
        if phase == "turn":
            turn = doc.get("turn")
            if not isinstance(turn, dict) or not _id(turn.get("task")) or not _id(turn.get("role")):
                raise ValueError("Invalid host-authorized agent turn")
            kind = turn.get("kind")
            base = {"task", "role", "kind", "message"}
            if kind == "invoke":
                allowed = base | {"action", "input_from", "query"}
            elif kind == "rea-mcp":
                allowed = base | {"mcp_requests"}
            elif kind == "submit":
                allowed = base
            elif kind == "review":
                allowed = base | {"verdict"}
                if turn.get("verdict") not in {"approved", "changes_requested"}:
                    raise ValueError("Review needs an explicit verdict")
            else:
                raise ValueError("No automatic LLM agent actions in Ferrari VPS")
            if set(turn) - allowed or not _text(turn.get("message"), 1500, 12):
                raise ValueError("Invalid host turn content")
            if kind == "rea-mcp":
                rea_mcp.validate_requests(turn.get("mcp_requests"))
            if kind == "invoke" and (not isinstance(turn.get("action"), str)
                                      or turn["action"] not in tool_runtime.specs()):
                raise ValueError("Unknown Ferrari action")
    else:
        raise ValueError("Unknown Ruflo team phase")
    return True


def _now():
    return datetime.now(timezone.utc).isoformat()


def _atomic(path, obj):
    fd, tmp = tempfile.mkstemp(prefix=".team-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as out:
            json.dump(obj, out, ensure_ascii=False, indent=2, sort_keys=True)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
        os.chmod(tmp, 0o600)
        os.replace(tmp, path)
    finally:
        if os.path.lexists(tmp):
            os.unlink(tmp)


def _load(teamdir):
    file = teamdir / "state.json"
    if file.is_symlink() or not file.is_file():
        raise RuntimeError("Private team journal missing or unsafe")
    value = json.loads(file.read_text(encoding="utf-8"))
    if value.get("version") != 1 or not isinstance(value.get("revision"), int):
        raise RuntimeError("Unrecognized Ferrari team journal")
    return value


@contextmanager
def _locked(team_id, new=False):
    if not HOME.is_dir() or HOME.is_symlink():
        raise RuntimeError("Ferrari private project root unavailable")
    runtime = HOME / ".runtime"
    if runtime.is_symlink() or not runtime.is_dir():
        raise RuntimeError("Ferrari private runtime unavailable")
    if SESSION_PARENT.is_symlink():
        raise RuntimeError("Unsafe Ferrari team storage")
    SESSION_PARENT.mkdir(mode=0o700, exist_ok=True)
    if not SESSION_PARENT.resolve(strict=True).is_relative_to(HOME.resolve(strict=True)):
        raise RuntimeError("Ferrari team storage escaped project")
    teamdir = SESSION_PARENT / team_id
    if teamdir.is_symlink():
        raise RuntimeError("Symbolic Ferrari team sessions forbidden")
    if new:
        teamdir.mkdir(mode=0o700, exist_ok=False)
    if not teamdir.is_dir():
        raise FileNotFoundError("Unknown Ferrari team session")
    lock = teamdir / ".team.lock"
    if lock.is_symlink():
        raise RuntimeError("Unsafe team lock")
    fd = os.open(lock, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        yield teamdir
    finally:
        fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)


def _verified_artifacts(answer, output):
    if not isinstance(answer, dict) or not answer.get("confirmed"):
        raise RuntimeError("Tool did not confirm any result")
    files = answer.get("artifacts")
    if not isinstance(files, list) or not files:
        raise RuntimeError("Tool did not produce evidence")
    if len(files) > 30:
        raise RuntimeError("Too many Ferrari evidence files")
    root = output.resolve(strict=True)
    evidence = []
    total = 0
    for raw in files:
        path = Path(raw)
        if path.is_symlink() or not path.is_file() or not path.resolve(strict=True).is_relative_to(root):
            raise RuntimeError("Unsafe or missing Ferrari evidence")
        size = path.stat().st_size
        total += size
        if total > MAX_EVIDENCE:
            raise RuntimeError("Ferrari evidence quota exceeded")
        evidence.append({"path": str(path), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                         "bytes": size})
    return evidence


def _check_recorded_evidence(state, folder):
    """Review and final acceptance fail if previously produced evidence changed."""
    root = folder.resolve(strict=True)
    for task in state["tasks"].values():
        if task["status"] not in {"awaiting_review", "approved"}:
            continue
        items = task.get("evidence")
        if not isinstance(items, list) or not items:
            raise ValueError("Team task has no reviewable evidence")
        for item in items:
            path = Path(item["path"])
            if (path.is_symlink() or not path.is_file()
                    or not path.resolve(strict=True).is_relative_to(root)
                    or path.stat().st_size != item["bytes"]
                    or hashlib.sha256(path.read_bytes()).hexdigest() != item["sha256"]):
                raise ValueError("Private team evidence was modified or removed")


def _stage_input(state, task, from_id, teamdir):
    if from_id == "$input":
        path = state.get("input_path")
        if not path:
            raise ValueError("This team has no uploaded input")
    else:
        if from_id not in task["depends_on"]:
            raise ValueError("Tool inputs must come from an approved dependency")
        previous = state["tasks"][from_id]
        if previous["status"] != "approved" or not previous.get("evidence"):
            raise ValueError("Dependency is not approved with evidence")
        path = previous["evidence"][0]["path"]
    p = Path(path)
    if p.is_symlink() or not p.is_file() or not p.resolve(strict=True).is_relative_to(teamdir.resolve(strict=True)):
        raise ValueError("Ferrari input escaped private team")
    return str(p)


@contextmanager
def _ruflo_ledger(state, task_id=None):
    """Real Ruflo MCP, ephemeral for each host-led round; no LLM API or daemon."""
    with tempfile.TemporaryDirectory(dir=HOME / ".runtime", prefix="ruflo-team-round-") as tmp:
        client = ruflo_host.RufloMCP(tmp)
        swarm_id = None
        try:
            client.start()
            swarm = client.tool("swarm_init", {"topology": "hierarchical",
                 "maxAgents": len(state["roles"]), "strategy": "specialized"})
            swarm_id = ruflo_host.lookup(swarm, ("swarmId", "swarm_id"))
            if not swarm_id:
                raise RuntimeError("Ruflo did not create swarm")
            agentids = {}
            for role in state["roles"].values():
                response = client.tool("agent_spawn", {"agentType": role["type"],
                     "name": "ferrari-" + role["id"], "model": "inherit", "swarmId": swarm_id})
                aid = ruflo_host.lookup(response, ("agentId", "agent_id"))
                if not aid:
                    raise RuntimeError("Ruflo did not create specialized agent")
                agentids[role["id"]] = aid
            task_key = None
            if task_id is not None:
                task = state["tasks"][task_id]
                reply = client.tool("task_create", {"type": "research",
                     "description": "Ferrari host-led " + task["goal"][:160],
                     "priority": "normal", "assignTo": [agentids[task["role"]]]})
                task_key = ruflo_host.lookup(reply, ("taskId", "task_id"))
                if not task_key:
                    raise RuntimeError("Ruflo did not assign task")
            yield client, task_key
        finally:
            if swarm_id:
                try:
                    client.tool("swarm_shutdown", {"swarmId": swarm_id, "graceful": True})
                except Exception as exc:
                    client.close()
                    raise RuntimeError("Ruflo swarm shutdown failed") from exc
            client.close()


def _inbox(state):
    tasks = state["tasks"]
    ready = []
    for task in tasks.values():
        if task["status"] == "pending" and all(tasks[d]["status"] == "approved" for d in task["depends_on"]):
            role = state["roles"][task["role"]]
            goal, proof = BRIEFS.get(role["type"], ("Complete only the assigned mission.",
                            "Produce evidence and request independent review."))
            ready.append({"task": task["id"], "role": role["id"], "type": role["type"],
                "mission": task["goal"], "brief": goal, "quality_rule": proof,
                "allowed_actions": role["actions"], "dependency_evidence":
                {d: [e["sha256"] for e in tasks[d].get("evidence", [])] for d in task["depends_on"]}})
        if task["status"] == "awaiting_review":
            role = state["roles"][task["reviewer"]]
            ready.append({"task": task["id"], "role": role["id"], "type": role["type"],
                "mission": "Review independently: " + task["goal"],
                "brief": "Verify actual evidence; request corrections when unsupported.",
                "evidence": [{k: e[k] for k in ("sha256", "bytes")} for e in task.get("evidence", [])],
                "submission": task.get("summary", ""), "kind": "review"})
    return ready


def _status(state):
    statuses = {tid: task["status"] for tid, task in state["tasks"].items()}
    return {"team_id": state["team_id"], "host": state["host"],
            "mission": state["mission"], "revision": state["revision"],
            "status": state["status"], "tasks": statuses,
            "host_inbox": _inbox(state), "tool_calls_verified": state["tool_calls_verified"],
            "reviews_recorded": state["reviews_recorded"],
            "autonomous_agent_model_calls": 0,
            "host_reasoning_mode": "external_host_rounds_only",
            "ruflo_session_mode": "ephemeral_per_round"}


def _export(state, dest, extra=()):
    dest = Path(dest)
    if dest.is_symlink() or dest.exists():
        raise FileExistsError("Ferrari team output must be a new directory")
    dest.mkdir(parents=True, mode=0o700)
    item = dest / "ruflo-team-status.json"
    item.write_text(json.dumps(_status(state), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = [str(item)]
    # Only files produced by the current turn enter this response, bounded
    # and reverified; never upload the whole private journal or prior inputs.
    for file in extra:
        p = Path(file)
        if p.is_symlink() or not p.is_file() or p.stat().st_size > MAX_EVIDENCE:
            raise RuntimeError("Unsafe response evidence")
        target = dest / ("evidence-" + str(len(outputs)) + p.suffix[:12])
        shutil.copyfile(p, target)
        outputs.append(str(target))
    return {"confirmed": True, "artifacts": outputs,
            "operation": "ruflo-team", "executor": "ferrari-ruflo-mcp-shared-host"}


def run(doc, dest, uploaded=None):
    validate_job(doc)
    phase = doc["phase"]
    if phase == "start":
        with _locked(doc["team_id"], new=True) as folder:
            state = {"version": 1, "team_id": doc["team_id"], "host": doc["host"],
                 "mission": doc["mission"], "revision": 0, "status": "awaiting_host",
                 "roles": {r["id"]: dict(r) for r in doc["roles"]},
                 "tasks": {t["id"]: {**t, "status": "pending", "evidence": []} for t in doc["tasks"]},
                 "input_path": None, "tool_calls_verified": 0, "reviews_recorded": 0,
                 "history": [{"at": _now(), "event": "created", "host": doc["host"]}]}
            if uploaded is not None:
                source = Path(uploaded)
                if source.is_symlink() or not source.is_file() or source.stat().st_size > 2_000_000:
                    raise ValueError("Unsafe Ferrari uploaded team input")
                input_dir = folder / "input"
                input_dir.mkdir(mode=0o700)
                private = input_dir / "source"
                shutil.copyfile(source, private)
                private.chmod(0o600)
                state["input_path"] = str(private)
            with _ruflo_ledger(state):
                pass
            _atomic(folder / "state.json", state)
            return _export(state, dest)
    with _locked(doc["team_id"]) as folder:
        state = _load(folder)
        if phase == "status":
            return _export(state, dest)
        if doc["revision"] != state["revision"]:
            raise ValueError("Stale or replayed Ferrari host turn")
        if state["status"] == "completed":
            raise ValueError("Ferrari team is already completed")
        if phase == "finish":
            if any(t["status"] != "approved" for t in state["tasks"].values()):
                raise ValueError("All agent tasks require distinct reviewer approval")
            _check_recorded_evidence(state, folder)
            if (not any(t["status"] == "approved" and t.get("evidence_kind") == "tool"
                        for t in state["tasks"].values())
                    or state["reviews_recorded"] == 0):
                raise ValueError("No approved real Ferrari tool evidence; cannot certify")
            state["status"] = "completed"
            state["revision"] += 1
            state["history"].append({"at": _now(), "event": "final_host_approval",
                                      "approval": doc["approval"]})
            _atomic(folder / "state.json", state)
            return _export(state, dest)
        if phase == "recover":
            task = state["tasks"].get(doc["task"])
            if not task or task["status"] != "failed":
                raise ValueError("Only failed tasks can be explicitly recovered")
            task["status"] = "pending"
            state["revision"] += 1
            state["history"].append({"at": _now(), "event": "explicit_recovery",
                 "task": doc["task"], "reason": doc["reason"]})
            _atomic(folder / "state.json", state)
            return _export(state, dest)
        turn = doc["turn"]
        task = state["tasks"].get(turn["task"])
        if task is None:
            raise ValueError("Unknown Ruflo team task")
        if turn["kind"] == "review":
            if task["status"] != "awaiting_review" or turn["role"] != task["reviewer"]:
                raise ValueError("Only the assigned independent reviewer may review submitted work")
            _check_recorded_evidence(state, folder)
        else:
            if task["status"] != "pending" or turn["role"] != task["role"]:
                raise ValueError("Turn does not belong to ready agent")
            if any(state["tasks"][d]["status"] != "approved" for d in task["depends_on"]):
                raise ValueError("Task dependencies are not independently approved")
        if turn["kind"] == "invoke":
            role = state["roles"][turn["role"]]
            action = turn["action"]
            if action not in role["actions"]:
                raise ValueError("Ferrari tool not authorized for this agent")
            spec = tool_runtime.specs()[action]
            query = turn.get("query")
            if ("{query}" in spec["args"]) != (isinstance(query, str) and _text(query, 200)):
                raise ValueError("Ferrari tool query requirements not met")
            source = _stage_input(state, task, turn.get("input_from", "$input"), folder)
        else:
            source = None
        if turn["kind"] == "rea-mcp" and "rea-mcp" not in state["roles"][turn["role"]]["actions"]:
            raise ValueError("REA MCP must be explicitly authorized for this agent")
        # Journal the running stage before side effects. An interrupted tool may
        # NOT be replayed until explicit recovery acknowledges duplicate risk.
        stage = folder / "work" / (task["id"] + "-" + str(state["revision"]))
        if turn["kind"] in {"invoke", "rea-mcp"}:
            stage.parent.mkdir(mode=0o700, exist_ok=True)
            task["status"] = "failed"
            _atomic(folder / "state.json", state)
        extra = []
        try:
            with _ruflo_ledger(state, task["id"]) as (client, ruflo_task):
                if turn["kind"] == "invoke":
                    answer = tool_runtime.invoke(turn["action"], source, str(stage), query)
                    evidence = _verified_artifacts(answer, stage)
                    extra = [e["path"] for e in evidence]
                elif turn["kind"] == "rea-mcp":
                    answer = rea_mcp.invoke(turn["mcp_requests"], stage, None)
                    evidence = _verified_artifacts(answer, stage)
                    extra = [e["path"] for e in evidence]
                elif turn["kind"] == "submit":
                    stage.parent.mkdir(mode=0o700, exist_ok=True)
                    stage.mkdir(mode=0o700)
                    note = stage / "host-submission.json"
                    note.write_text(json.dumps({"role": turn["role"], "task": task["id"],
                              "text": turn["message"], "source": "host_assertion_not_tool"},
                              ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                    evidence = _verified_artifacts({"confirmed": True, "artifacts": [str(note)]}, stage)
                    extra = [str(note)]
                else:
                    evidence = task["evidence"]
                if turn["kind"] in {"invoke", "rea-mcp", "submit"}:
                    task["status"] = "awaiting_review"
                    task["evidence"] = evidence
                    task["evidence_kind"] = "tool" if turn["kind"] in {"invoke", "rea-mcp"} else "host_note"
                    task["summary"] = turn["message"]
                    if turn["kind"] in {"invoke", "rea-mcp"}:
                        state["tool_calls_verified"] += 1
                        client.tool("task_complete", {"taskId": ruflo_task,
                            "result": {"verified_tool_artifacts": [e["sha256"] for e in evidence],
                                       "host": state["host"]}})
                else:
                    if turn["verdict"] == "approved":
                        task["status"] = "approved"
                        client.tool("task_complete", {"taskId": ruflo_task,
                            "result": {"reviewed": True, "host": state["host"]}})
                    else:
                        task["status"] = "pending"
                    task["review"] = {"role": turn["role"], "verdict": turn["verdict"],
                                      "feedback": turn["message"]}
                    state["reviews_recorded"] += 1
            state["revision"] += 1
            state["history"].append({"at": _now(), "event": turn["kind"],
                   "task": task["id"], "role": turn["role"], "message": turn["message"][:240]})
            _atomic(folder / "state.json", state)
            return _export(state, dest, extra)
        except Exception:
            if turn["kind"] in {"invoke", "rea-mcp"}:
                task["status"] = "failed"
                state["revision"] += 1
                state["history"].append({"at": _now(), "event": "execution_failed",
                     "task": task["id"], "role": turn["role"]})
                _atomic(folder / "state.json", state)
            raise
