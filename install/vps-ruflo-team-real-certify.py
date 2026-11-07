#!/usr/bin/env python3
"""Ferrari-only real Ruflo MCP + typed executor certificate (synthetic data).

Uses exactly one *external* host's pre-authored decisions, NEVER an LLM
call inside the VPS. This certifies round-trip control flow and real Ruflo MCP
agent/task registration; it does not certify autonomous intelligent workers.

Run only from a pinned Ferrari release on the authorized VPS. No installs.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import sys
import zipfile

from engine import agent_team, skill_job


ROOT = Path("/srv/projects/skill-universal")
ID = re.compile(r"[a-z][a-z0-9_-]{0,39}\Z")


def _call(out: Path, index: int, request: dict) -> dict:
    folder = out / ("round-" + str(index).zfill(2))
    report, code = skill_job.execute(request, folder)
    if code or report.get("status") != "completed":
        raise RuntimeError("Ferrari team real round failed: " + str(report.get("error", "code=" + str(code))))
    archive = folder / "response.zip"
    if not archive.is_file():
        raise RuntimeError("Ferrari did not package ZIP")
    with zipfile.ZipFile(archive) as z:
        names = set(z.namelist())
        if not {"report.json", "artifacts/ruflo-team-status.json"}.issubset(names):
            raise RuntimeError("Ferrari team ZIP is incomplete")
        packed_report = json.loads(z.read("report.json"))
        status = json.loads(z.read("artifacts/ruflo-team-status.json"))
    if packed_report.get("status") != "completed" or not isinstance(status.get("host_inbox"), list):
        raise RuntimeError("Ferrari team reply has invalid report/status")
    return status


def _request(tid, phase, rid, **kw):
    return {"version": 1, "id": rid, "kind": "ruflo-team",
            "team_id": tid, "phase": phase, **kw}


def _turn(tid, n, task, role, kind, message, **kw):
    return _request(tid, "turn", f"ruflo-team-qa-round-{n}",
                    revision=n, turn={"task": task, "role": role,
                                      "kind": kind, "message": message, **kw})


def _evidence(status, task, reviewer="reviewer"):
    items = [x for x in status["host_inbox"]
             if x.get("task") == task and x.get("role") == reviewer
             and x.get("kind") == "review"]
    if len(items) != 1 or not items[0].get("evidence"):
        raise RuntimeError("Host has no independently reviewable artifact")
    sha = [v["sha256"] for v in items[0]["evidence"]]
    if any(not re.fullmatch("[a-f0-9]{64}", x) for x in sha):
        raise RuntimeError("Unverifiable artifact digest")
    return sha


def verify(out: Path, team_id: str) -> dict:
    if not ID.fullmatch(team_id):
        raise ValueError("Unsafe team ID")
    if not ROOT.is_dir() or ROOT.is_symlink():
        raise RuntimeError("Ferrari root is not private")
    runtime = ROOT / ".runtime"
    if runtime.is_symlink() or not runtime.is_dir():
        raise RuntimeError("Ferrari runtime missing")
    if out.is_symlink() or out.exists() or not out.resolve().is_relative_to(runtime.resolve()):
        raise ValueError("Result folder must be new and belong to Ferrari runtime")
    out.mkdir(mode=0o700)
    state_folder = runtime / "ruflo-team-sessions" / team_id
    if state_folder.exists() or state_folder.is_symlink():
        raise ValueError("Test-only Ruflo team name already exists")
    report = {"certification": "ruflo-team-real-mcp-and-private-tools",
              "team_id": team_id, "mode": "synthetic_host_authored_decisions",
              "actual_chatgpt_llm_calls": 0,
              "scope": "Ferrari only", "result": "failed"}
    n = 0
    try:
        sample = b'{"status":"real-tool","items":[2,1]}\n'
        roles = [
            {"id": "architect", "type": "architect", "actions": []},
            {"id": "coder", "type": "coder", "actions": ["jq-format-json"]},
            {"id": "tester", "type": "tester", "actions": ["jq-format-json"]},
            {"id": "reviewer", "type": "reviewer", "actions": []}
        ]
        tasks = [
            {"id": "design", "role": "architect", "reviewer": "reviewer",
             "goal": "Design an objectively verifiable JSON conversion", "depends_on": []},
            {"id": "format", "role": "coder", "reviewer": "reviewer",
             "goal": "Format the JSON using private Ferrari jq", "depends_on": ["design"]},
            {"id": "verify", "role": "tester", "reviewer": "reviewer",
             "goal": "Run jq again against the approved formatted JSON", "depends_on": ["format"]}
        ]
        status = _call(out, n, _request(team_id, "start", "team-qa-start",
                          host="ChatGPT",
                          mission="Certify real Ruflo MCP four-role collaboration and Ferrari jq",
                          roles=roles, tasks=tasks,
                          input={"name": "sample.json",
                                 "content_base64": base64.b64encode(sample).decode("ascii")}))
        assert status["revision"] == 0 and status["host_inbox"][0]["role"] == "architect"
        n += 1
        status = _call(out, n, _turn(team_id, 0, "design", "architect", "submit",
                          "Acceptance criteria: valid JSON, a real .json artifact and independent review."))
        n += 1
        status = _call(out, n, _turn(team_id, 1, "design", "reviewer", "review",
                          "Plan reviewed against synthetic input and declared acceptance criteria.",
                          verdict="approved", evidence_sha256=_evidence(status, "design")))
        assert status["tasks"]["design"] == "approved"
        n += 1
        status = _call(out, n, _turn(team_id, 2, "format", "coder", "invoke",
                          "Run private Ferrari jq-format-json on the uploaded sample.",
                          action="jq-format-json", input_from="$input"))
        sha_format = _evidence(status, "format")
        n += 1
        status = _call(out, n, _turn(team_id, 3, "format", "reviewer", "review",
                          "Reviewed the real formatter artifact and verified the recorded SHA-256.",
                          verdict="approved", evidence_sha256=sha_format))
        assert status["tasks"]["format"] == "approved"
        n += 1
        status = _call(out, n, _turn(team_id, 4, "verify", "tester", "invoke",
                          "Re-run private Ferrari jq against the previously approved file.",
                          action="jq-format-json", input_from="format"))
        sha_test = _evidence(status, "verify")
        n += 1
        status = _call(out, n, _turn(team_id, 5, "verify", "reviewer", "review",
                          "Independently verified the tester output and the recorded SHA-256.",
                          verdict="approved", evidence_sha256=sha_test))
        assert all(v == "approved" for v in status["tasks"].values())
        n += 1
        status = _call(out, n, _request(team_id, "finish", "team-qa-finish",
                          revision=6,
                          approval="Host accepted two verified private Ferrari tool outputs with three distinct-role reviews."))
        if (status["status"] != "completed" or status["tool_calls_verified"] != 2
                or status["reviews_recorded"] != 3
                or status["autonomous_agent_model_calls"] != 0):
            raise RuntimeError("Ruflo team real acceptance conditions failed")
        record = state_folder / "state.json"
        state = json.loads(record.read_text(encoding="utf-8"))
        for task in state["tasks"].values():
            if task["status"] != "approved":
                raise RuntimeError("Unapproved private task")
            for file in task["evidence"]:
                p = Path(file["path"])
                if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(state_folder.resolve()):
                    raise RuntimeError("Unsafe private team evidence")
                if hashlib.sha256(p.read_bytes()).hexdigest() != file["sha256"]:
                    raise RuntimeError("Private team output checksum changed")
        shutil.copyfile(out / ("round-" + str(n).zfill(2)) / "response.zip",
                        out / "certified-response.zip")
        report.update({"result": "pass", "agents": 4, "tasks": 3,
                       "ruflo_mcp_swarm_rounds": 7,
                       "private_ferrari_tool_calls": 2,
                       "independent_role_reviews": 3,
                       "host_final_approval": True,
                       "input_extension_preserved": True,
                       "collaboration": "host-led rounds with real Ruflo MCP and Ferrari jq",
                       "artifacts_verified_sha256": True,
                       "autonomous_agent_model_calls": 0})
        print("FERRARI_RUFLO_TEAM_REAL_MCP=PASS")
        print("FERRARI_RUFLO_TEAM_REAL_TYPED_TOOLS=2/2_PASS")
        print("FERRARI_RUFLO_TEAM_ROLE_REVIEWS=3/3_PASS")
        print("FERRARI_RUFLO_TEAM_SHARED_HOST_ROUNDS=PASS_NO_REMOTE_LLM")
        return report
    finally:
        # Remove only the synthetic session named by this exact certificate.
        if state_folder.is_dir() and not state_folder.is_symlink():
            if not shutil.rmtree.avoids_symlink_attacks:
                raise RuntimeError("Safe Ferrari QA cleanup not supported")
            shutil.rmtree(state_folder)
        report_path = out / "ruflo-team-certification.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output", required=True)
    ap.add_argument("--team-id", required=True)
    args = ap.parse_args()
    report = verify(Path(args.output), args.team_id)
    return 0 if report["result"] == "pass" else 2


if __name__ == "__main__":
    try:
        sys.exit(main())
    except (ValueError, RuntimeError, OSError, AssertionError) as err:
        print("FERRARI_RUFLO_TEAM_CERT_FAILED=" + str(err), file=sys.stderr)
        sys.exit(2)
