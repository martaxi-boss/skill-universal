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

from engine import ferrari, tool_runtime

MAX_REQUEST_BYTES = 2_800_000
MAX_INPUT_BYTES = 2_000_000
ID_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}$")
INPUT_PATTERN = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9._-]{0,79}\.[a-zA-Z0-9]{1,12}$")

def validate_job(data):
    if not isinstance(data,dict) or data.get("version") != 1:
        raise ValueError("Expected a version 1 Ferrari job object")
    if set(data) - {"version","id","kind","operation","request","action","title","layout","input"}:
        raise ValueError("Unknown Ferrari job fields")
    jid=data.get("id")
    if not isinstance(jid,str) or not ID_PATTERN.fullmatch(jid):
        raise ValueError("Invalid Ferrari job ID")
    kind=data.get("kind")
    if kind not in {"inventory","operation","auto","invoke"}:
        raise ValueError("Unsupported Ferrari job kind")
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
    if kind=="auto" and (not isinstance(data.get("request"),str) or not data["request"].strip() or len(data["request"])>500):
        raise ValueError("Invalid natural-language task")
    if kind=="operation" and data.get("title") is not None and (not isinstance(data["title"],str) or len(data["title"])>120):
        raise ValueError("Invalid title")
    if kind=="operation" and data.get("layout","landing") not in ferrari.LAYOUTS:
        raise ValueError("Invalid site layout")
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
            (dest/"inventory.json").write_text(json.dumps(tool_runtime.inventory(),ensure_ascii=False,indent=2),encoding="utf-8")
            response={"confirmed":True,"artifacts":[str(dest/"inventory.json")]}
        elif kind=="operation":
            response=ferrari.run(data["operation"],str(dest),source=str(src) if src else None,
                                 title=data.get("title","Ferrari Skill"),layout=data.get("layout","landing"))
        elif kind=="invoke":
            response=tool_runtime.invoke(data["action"],str(src),str(dest))
        else:
            response=tool_runtime.auto(data["request"],str(src),str(dest),execute=True)
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
        result["status"]="completed"
        result["artifacts"]=[str(p.relative_to(target)) for p in files]
        result["executor"]=response.get("executor")
        result["operation"]=response.get("operation",response.get("action",kind))
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
