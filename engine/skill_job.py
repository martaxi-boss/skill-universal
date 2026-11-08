"""Ferrari-owned Skill job envelope: validate, execute on Ubuntu and package evidence.

GitHub/SSH carry the JSON and ZIP. Task selection and actual execution happen here.
Public GitHub requests must never contain credentials or confidential source files.
"""
from __future__ import annotations

import argparse
import base64
import binascii
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import sys
import traceback
import uuid
import zipfile

from engine import ferrari, tool_runtime, orchestrator, rea_mcp, ruflo_host, agent_team, quality_gate, runtime_health

MAX_REQUEST_BYTES = 2_800_000
MAX_INPUT_BYTES = 2_000_000
ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
INPUT_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}\.[a-zA-Z0-9]{1,12}$")

def validate_job(data):
    if not isinstance(data,dict) or data.get("version") != 1:
        raise ValueError("Expected a version 1 Ferrari job object")
    if set(data) - {"version","id","kind","operation","request","action","title","layout","input","query","plan","max_parallel","mcp_requests","roles","steps","host","phase","team_id","mission","tasks","turn","revision","approval","task","reason","acknowledge_risk","acceptance","targets"}:
        raise ValueError("Unknown Ferrari job fields")
    jid=data.get("id")
    if not isinstance(jid,str) or not ID_PATTERN.fullmatch(jid):
        raise ValueError("Invalid Ferrari job ID")
    kind=data.get("kind")
    if "acceptance" in data:
        if kind not in {"operation", "invoke", "auto", "plan", "ruflo-host"}:
            raise ValueError("Acceptance policy is unsupported for this job kind")
        quality_gate.validate(data["acceptance"])
    if kind not in {"inventory","runtime-check","operation","auto","invoke","plan","rea-mcp","ruflo-host","ruflo-team"}:
        raise ValueError("Unsupported Ferrari job kind")
    if kind=="runtime-check":
        if set(data)-{"version","id","kind","targets"}:
            raise ValueError("Unexpected Ferrari runtime-check fields")
        targets=data.get("targets")
        if (not isinstance(targets,list) or not 1<=len(targets)<=len(runtime_health.PROGRAM_COMMANDS)
                or any(not isinstance(t,str) or t not in runtime_health.PROGRAM_COMMANDS for t in targets)
                or len(set(targets))!=len(targets)):
            raise ValueError("Expected unique, whitelisted Ferrari support-program targets")
    elif "targets" in data:
        raise ValueError("Ferrari targets require runtime-check")
    inp=data.get("input")
    if kind in {"auto","invoke"} and not isinstance(inp,dict):
        raise ValueError("This operation requires an input file")
    if inp is not None:
        if not isinstance(inp,dict) or set(inp)!={"name","content_base64"}:
            raise ValueError("Invalid input envelope")
        name,encoded=inp["name"],inp["content_base64"]
        if not isinstance(name,str) or not INPUT_PATTERN.fullmatch(name):
            raise ValueError("Invalid input filename")
        if not isinstance(encoded,str) or len(encoded)>MAX_INPUT_BYTES*4//3+8:
            raise ValueError("Invalid input content size")
        try:
            raw=base64.b64decode(encoded,validate=True)
        except (ValueError,binascii.Error) as exc:
            raise ValueError("Invalid base64 file data") from exc
        if len(raw)>MAX_INPUT_BYTES:
            raise ValueError("Input content too large")
    else:
        raw=None
    if kind=="operation":
        if data.get("operation") not in ferrari.OPS:
            raise ValueError("Ferrari operation is not implemented")
    if kind=="invoke" and data.get("action") not in tool_runtime.specs():
        raise ValueError("Ferrari tool action is not integrated")
    if kind=="ruflo-host":
        ruflo_host.validate_job(data)
    elif kind=="ruflo-team":
        agent_team.validate_job(data)
    elif any(key in data for key in
             ("roles","steps","host","phase","team_id","mission","tasks","turn",
              "revision","approval","task","reason","acknowledge_risk")):
        raise ValueError("Ruflo fields require a Ruflo request kind")
    if kind=="rea-mcp":
        if set(data)-{"version","id","kind","input","mcp_requests"}:
            raise ValueError("Unexpected original REA MCP job fields")
        rea_mcp.validate_requests(data.get("mcp_requests"))
    elif "mcp_requests" in data:
        raise ValueError("REA MCP calls require kind=rea-mcp")
    query=data.get("query")
    if query is not None:
        if kind not in {"invoke","auto"} or not isinstance(query,str) or not 1<=len(query.strip())<=200 or "\x00" in query:
            raise ValueError("Invalid query for Ferrari tool")
    if kind=="invoke":
        spec=tool_runtime.specs()[data["action"]]
        if ("{query}" in spec["args"]) != (query is not None):
            raise ValueError("Action query required or not supported")
    if kind=="auto" and (not isinstance(data.get("request"),str) or not data["request"].strip() or len(data["request"])>500):
        raise ValueError("Invalid natural-language task")
    if kind=="operation" and data.get("title") is not None and (not isinstance(data["title"],str) or len(data["title"])>120):
        raise ValueError("Invalid title")
    if kind=="operation" and data.get("layout","landing") not in ferrari.LAYOUTS:
        raise ValueError("Invalid site layout")
    if kind=="plan":
        # The existing Ferrari orchestrator owns the DAG; the Skill only carries it.
        if set(data)-{"version","id","kind","input","plan","max_parallel","acceptance"}:
            raise ValueError("Unrecognized Ferrari plan envelope fields")
        plan=data.get("plan")
        if not isinstance(plan,dict) or set(plan)!={"version","steps"}:
            raise ValueError("Expected a versioned Ferrari orchestrator plan")
        parallel=data.get("max_parallel",2)
        if type(parallel) is not int or not 1<=parallel<=orchestrator.MAX_PARALLEL:
            raise ValueError("Invalid Ferrari parallelism")
        # Never interpret paths supplied in public GitHub JSON as VPS file paths.
        if not isinstance(plan.get("steps"),list):
            raise ValueError("Plan steps must be a list")
        for step in plan["steps"]:
            if isinstance(step,dict) and step.get("input") not in (None,"$input"):
                raise ValueError("Plan input must be the uploaded file alias $input")
            if isinstance(step,dict) and step.get("input")=="$input" and raw is None:
                raise ValueError("The plan requests an uploaded input file")
        orchestrator.validate_workflow(plan)
    elif "plan" in data or ("max_parallel" in data and kind!="ruflo-host"):
        raise ValueError("Plan fields require kind=plan")
    return raw

def execute(data, outdir):
    """Own output tree; return a response.zip including report and produced files."""
    target=Path(outdir).expanduser()
    if target.exists() or target.is_symlink():
        raise FileExistsError("Job output directory must be new")
    target.mkdir(parents=True,mode=0o700)
    result={"id":data.get("id"),"kind":data.get("kind"),"status":"failed",
            "at":datetime.now(timezone.utc).isoformat(),
            "engine":"motor-ferrari-ubuntu","artifacts":[]}
    code=0
    try:
        encoded=validate_job(data)
        src=None
        if encoded is not None:
            inp=target/"input"
            inp.mkdir(mode=0o700)
            src=inp/data["input"]["name"]
            src.write_bytes(encoded)
            src.chmod(0o600)
        kind=data["kind"]
        dest=target/"artifacts"
        if kind=="inventory":
            dest.mkdir(mode=0o700)
            existing=tool_runtime.inventory()
            inventory_file=dest/"inventory.json"
            inventory_file.write_text(json.dumps(existing,ensure_ascii=False,indent=2),encoding="utf-8")
            # Same authorized transport and one Ferrari source catalog. REA
            # tools/list is read-only; no extra GitHub request type or bridge.
            catalog_file=dest/"catalog.json"
            catalog_file.write_text(json.dumps(tool_runtime.unified_catalog(inventory_now=existing),ensure_ascii=False,indent=2),encoding="utf-8")
            response={"confirmed":True,"artifacts":[str(inventory_file),str(catalog_file)]}
        elif kind=="runtime-check":
            dest.mkdir(mode=0o700)
            items=[]
            for program in data["targets"]:
                exe=tool_runtime.executable(program)
                items.append(runtime_health.probe_support_program(program,exe,tool_runtime.HOME))
            check={"status":"complete_with_failures" if any(not x["startup_smoke_pass"] for x in items) else "passed",
                   "scope":"Private non-network startup checks only, NOT integrated functionality",
                   "results":items,
                   "pass_count":sum(x["startup_smoke_pass"] for x in items),
                   "requested_count":len(items)}
            output=dest/"runtime-check.json"
            output.write_text(json.dumps(check,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
            response={"confirmed":True,"artifacts":[str(output)],
                      "executor":"ferrari-private-version-smoke","operation":"runtime-check"}
        elif kind=="operation":
            response=ferrari.run(data["operation"],str(dest),source=str(src) if src else None,
                                 title=data.get("title","Ferrari Skill"),layout=data.get("layout","landing"))
        elif kind=="invoke":
            response=tool_runtime.invoke(data["action"],str(src),str(dest),query=data.get("query"))
        elif kind=="rea-mcp":
            response=rea_mcp.invoke(data["mcp_requests"],dest,src)
        elif kind=="ruflo-host":
            response=ruflo_host.run(data,dest,src)
        elif kind=="ruflo-team":
            response=agent_team.run(data,dest,src)
        elif kind=="plan":
            # Use the existing DAG runner; no changes to GitHub Actions or SSH.
            steps=[]
            for step in data["plan"]["steps"]:
                prepared=dict(step)
                if prepared.get("input")=="$input":
                    prepared["input"]=str(src)
                steps.append(prepared)
            execution=orchestrator.orchestrate(
                {"version":1,"steps":steps},str(dest),execute=True,
                max_parallel=data.get("max_parallel",2))
            report=execution["result"]
            if report["status"]!="completed":
                raise RuntimeError("Ferrari plan failed: "+json.dumps(report["failed"],ensure_ascii=False)[:700])
            artifacts=[execution["report_file"]]
            for stage in report["completed"].values():
                artifacts.extend(stage.get("artifacts",[]))
            response={"confirmed":True,"artifacts":artifacts,
                      "executor":"ferrari-orchestrator","operation":"plan"}
        else:
            response=tool_runtime.auto(data["request"],str(src),str(dest),execute=True,query=data.get("query"))
            if response["status"]!="completed":
                raise RuntimeError("Ferrari could not select an executable action: "+response["status"])
            response=response["result"]
        if not response.get("confirmed"):
            raise RuntimeError("Ferrari did not confirm generated artifacts")
        files=[]
        for item in response.get("artifacts",[]):
            candidate=Path(item)
            if candidate.is_symlink() or not candidate.exists():
                raise RuntimeError("Missing or symbolic-link output")
            if not candidate.resolve().is_relative_to(dest.resolve()):
                raise RuntimeError("Artifact outside this Ferrari job")
            if candidate.is_dir():
                files.extend(p for p in candidate.rglob("*") if p.is_file() and not p.is_symlink())
            elif candidate.is_file():
                files.append(candidate)
        files=sorted(set(files))
        if not files or any(not p.is_file() or p.is_symlink() for p in files):
            raise RuntimeError("No regular-file artifacts produced")
        # Files returned by the parallel DAG runner can use the physical
        # /srv/projects/skill-universal path while this job is entered via
        # the Ferrari-only historical symlink. Compare canonical paths,
        # retaining the original ZIP-relative archive layout.
        canonical_target=target.resolve(strict=True)
        canonical_artifacts=dest.resolve(strict=True)
        relative_files=[]
        for path in files:
            resolved=path.resolve(strict=True)
            if (not resolved.is_relative_to(canonical_target) or
                    not resolved.is_relative_to(canonical_artifacts)):
                raise RuntimeError("Ferrari artifact escapes this isolated job")
            relative_files.append(str(resolved.relative_to(canonical_target)))
        result["artifacts"]=relative_files
        result["quality_gate"]=quality_gate.inspect(files,data.get("acceptance"))
        if result["quality_gate"]["status"] == "failed":
            raise RuntimeError("Ferrari acceptance failed: " + "; ".join(result["quality_gate"]["failures"])[:700])
        result["executor"]=response.get("executor")
        result["operation"]=response.get("operation",response.get("action",kind))
        result["status"]="completed"
    except Exception as exc:
        code=2
        result["error"]=str(exc)[:1200]
    (target/"report.json").write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding="utf-8")
    archive=target/"response.zip"
    with zipfile.ZipFile(archive,"w",zipfile.ZIP_DEFLATED) as z:
        z.write(target/"report.json","report.json")
        for rel in result["artifacts"]:
            z.write(target/rel,rel)
    return result,code

def main():
    ap=argparse.ArgumentParser(description="Motor Ferrari Skill request job")
    ap.add_argument("--request",required=True)
    ap.add_argument("--output",required=True)
    args=ap.parse_args()
    req=Path(args.request)
    if req.is_symlink() or not req.is_file() or req.stat().st_size>MAX_REQUEST_BYTES:
        raise ValueError("Ferrari request must be a regular JSON file under size limit")
    job=json.loads(req.read_text(encoding="utf-8"))
    report,code=execute(job,args.output)
    print("FERRARI_SKILL_JOB_STATUS="+report["status"])
    print(json.dumps(report,ensure_ascii=False))
    return code

if __name__=="__main__":
    try:sys.exit(main())
    except (OSError,ValueError,RuntimeError,json.JSONDecodeError) as exc:
        print("FERRARI_SKILL_JOB_INVALID="+str(exc),file=sys.stderr)
        sys.exit(2)
