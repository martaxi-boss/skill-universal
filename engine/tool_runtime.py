"""Ferrari runtime: installed-program discovery and safe typed tool dispatch.

The 56 shortlist entries are candidates. Having a binary is not proof that
an executable adapter exists or that a full workflow has passed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
import unicodedata
import uuid

ROOT=Path(__file__).resolve().parents[1]
HOME=Path.home()/".local/share/motor-ferrari"
BINARIES={"imagemagick":"convert","libvips":"vips","opencv":None,
          "wireshark":"tshark","ytdlp":"yt-dlp","tesseract":"tesseract",
          "ocrmypdf":"ocrmypdf","radare2":"r2","ripgrep":"rg",
          "valkey":"valkey-server","ansible":"ansible"}
ISOLATED={"ghidra":HOME/"tools/ghidra-12.2/support/analyzeHeadless",
          "jadx":HOME/"tools/jadx-1.5.6/bin/jadx",
          "rea":HOME/".runtime/npm/rea/node_modules/.bin/rea",
          "ruflo":HOME/".runtime/npm/ruflo/node_modules/.bin/ruflo"}
def specs():
    doc=json.loads((ROOT/"engine/tool_actions.json").read_text(encoding="utf-8"))
    selected={x["id"] for x in json.loads((ROOT/"engine/ubuntu_selection.json").read_text())["tools"]}
    legacy={x["id"] for x in json.loads((ROOT/"engine/catalog.json").read_text())["tools"]}
    if doc.get("schema")!=1 or not isinstance(doc.get("actions"),list):
        raise ValueError("Invalid action manifest")
    result={}
    for x in doc["actions"]:
        if not isinstance(x,dict) or not re.fullmatch("[a-z0-9-]{3,60}",x.get("id","")):
            raise ValueError("Invalid action ID")
        if x["id"] in result or x["tool"] not in selected|legacy:
            raise ValueError("Duplicate action or unknown tool")
        if not re.fullmatch("[a-zA-Z0-9._-]{1,80}",x["binary"]):
            raise ValueError("Invalid binary")
        if x["mode"] not in {"stdout","file"} or not re.fullmatch("[a-zA-Z0-9._-]{1,90}",x["artifact"]):
            raise ValueError("Invalid artifact")
        if not isinstance(x["args"],list) or "{input}" not in x["args"]:
            raise ValueError("Missing bound input")
        if x["mode"]=="file" and "{output}" not in x["args"]:
            raise ValueError("Missing bound output")
        for arg in x["args"]:
            if not isinstance(arg,str) or len(arg)>160:
                raise ValueError("Invalid argument")
            if any(token not in {"{input}","{output}"} for token in re.findall(r"\{[^{}]*\}",arg)):
                raise ValueError("Unsupported argument placeholder")
        if not x.get("extensions") or not x.get("keywords") or not x.get("category"):
            raise ValueError("Incomplete action metadata")
        result[x["id"]]=x
    return result

def executable(tool,binary=None):
    pinned=ISOLATED.get(tool)
    if pinned and pinned.is_file():
        return str(pinned)
    return shutil.which(binary or BINARIES.get(tool) or tool) if (binary or BINARIES.get(tool,tool)) else None

def inventory():
    selected=json.loads((ROOT/"engine/ubuntu_selection.json").read_text())["tools"]
    helpers=json.loads((ROOT/"engine/catalog.json").read_text())["tools"]
    defined=specs()
    def inspect(entry,source):
        tool=entry["id"]
        base_bin=entry.get("bin") or BINARIES.get(tool,tool)
        path=executable(tool,base_bin)
        callable_ops=[x["id"] for x in defined.values() if x["tool"]==tool and executable(tool,x["binary"])]
        if not path and callable_ops:
            first=defined[callable_ops[0]]
            path=executable(tool,first["binary"])
        return {"id":tool,"category":entry["category"],"source":source,"installed":bool(path),
                "path":path,"actions":callable_ops,
                "status":"callable" if callable_ops else "installed_unintegrated" if path else "not_detected"}
    records=[inspect(x,"shortlist_56") for x in selected]
    used={x["id"] for x in selected}
    records.extend(inspect(x,"auxiliary_catalogue") for x in helpers if x["id"] not in used)
    return {"selected":len(selected),"registered_actions":len(defined),
            "installed":sum(x["installed"] for x in records),
            "callable_actions":sum(len(x["actions"]) for x in records),
            "programs":records,"note":"Detection is not a functional certification."}

def normalize(value):
    return "".join(x for x in unicodedata.normalize("NFKD",value.lower()) if not unicodedata.combining(x))

def route(request,source=None):
    if not isinstance(request,str) or not request.strip():raise ValueError("Request required")
    q=normalize(request)
    extension=Path(source).suffix.lower() if source else None
    candidates=[]
    for x in specs().values():
        exe=executable(x["tool"],x["binary"])
        if not exe:continue
        if extension and "*" not in x["extensions"] and extension not in x["extensions"]:continue
        matched=[k for k in x["keywords"] if normalize(k) in q]
        if not matched:continue
        candidates.append({"action":x["id"],"tool":x["tool"],"path":exe,
                           "score":10*len(matched)+(5 if extension and "*" not in x["extensions"] else 0),
                           "matched":matched})
    candidates.sort(key=lambda x:(-x["score"],x["action"]))
    return {"request":request,"input":source,"suggestions":candidates,"executed":False}

def auto(request,source,folder=None,execute=False):
    """Resolve a user request to a single installed adapter; run only if unambiguous."""
    proposal=route(request,source)
    options=proposal["suggestions"]
    if not options:
        return {**proposal,"selected":None,"status":"no_matching_installed_adapter"}
    best=options[0]
    if len(options)>1 and options[1]["score"]==best["score"]:
        return {**proposal,"selected":None,"status":"ambiguous","note":"No automatic execution when alternatives tie"}
    if not execute:
        return {**proposal,"selected":best,"status":"preview"}
    if not folder:
        raise ValueError("Output directory required to execute")
    outcome=invoke(best["action"],source,folder)
    return {**proposal,"selected":best,"status":"completed","executed":True,"result":outcome}

def invoke(action,source,folder):
    x=specs().get(action)
    if not x:raise ValueError("Unknown executable action")
    exe=executable(x["tool"],x["binary"])
    if not exe:raise RuntimeError("Executor not installed: "+x["binary"])
    if not source:raise ValueError("File input required")
    inp=Path(source)
    if inp.is_symlink() or not inp.is_file():
        raise ValueError("Input must be a non-symlink regular file")
    inp=inp.resolve(strict=True)
    if "*" not in x["extensions"] and inp.suffix.lower() not in x["extensions"]:
        raise ValueError("Input format not supported by "+action)
    outdir=Path(folder).resolve()
    target=outdir/x["artifact"]
    if target.exists() or target.is_symlink():
        raise FileExistsError("Refusing to overwrite "+str(target))
    outdir.mkdir(parents=True,exist_ok=True)
    replacements={"{input}":str(inp),"{output}":str(target)}
    args=[exe]+[replacements.get(v,v) for v in x["args"]]
    try:
        p=subprocess.run(args,shell=False,capture_output=True,timeout=240,check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Executor timeout: "+action) from exc
    if p.returncode:
        raise RuntimeError("Executor failed: "+p.stderr.decode("utf-8","replace")[-1000:])
    if x["mode"]=="stdout":
        if not p.stdout:raise RuntimeError("Empty executor output")
        target.write_bytes(p.stdout)
    if not target.is_file() or target.stat().st_size==0:
        raise RuntimeError("Expected artifact missing")
    return {"id":str(uuid.uuid4()),"at":datetime.now(timezone.utc).isoformat(),
            "operation":"tool","tool":x["tool"],"action":action,"executor":exe,
            "input":str(inp),"artifacts":[str(target)],"confirmed":True}

def main(argv=None):
    ap=argparse.ArgumentParser(description="Ferrari real-program runtime")
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("inventory")
    sub.add_parser("actions")
    r=sub.add_parser("route");r.add_argument("request");r.add_argument("--input")
    a=sub.add_parser("auto");a.add_argument("request");a.add_argument("--input",required=True)
    a.add_argument("--output");a.add_argument("--execute",action="store_true")
    i=sub.add_parser("invoke");i.add_argument("--action",required=True)
    i.add_argument("--input",required=True);i.add_argument("--output",required=True)
    args=ap.parse_args(argv)
    if args.cmd=="inventory":response=inventory()
    elif args.cmd=="actions":
        response=[{"action":x["id"],"tool":x["tool"],"available":bool(executable(x["tool"],x["binary"]))}
                  for x in specs().values()]
    elif args.cmd=="route":response=route(args.request,args.input)
    elif args.cmd=="auto":response=auto(args.request,args.input,args.output,args.execute)
    else:response=invoke(args.action,args.input,args.output)
    print(json.dumps(response,ensure_ascii=False,indent=2))
if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,FileNotFoundError,FileExistsError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}),file=sys.stderr)
        sys.exit(2)
