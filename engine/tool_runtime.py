"""Ferrari runtime: installed-program discovery and safe typed tool dispatch.

The 56 shortlist entries are candidates. Having a binary is not proof that
an executable adapter exists or that a full workflow has passed.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import importlib.util
import os
from pathlib import Path
from engine import runtime_discovery
import re
import shutil
import subprocess
import sys
import unicodedata
import uuid
import wave

ROOT=Path(__file__).resolve().parents[1]
HOME=Path.home()/".local/share/motor-ferrari"
BINARIES={"imagemagick":"convert","libvips":"vips","opencv":None,
          "wireshark":"tshark","ytdlp":"yt-dlp","tesseract":"tesseract",
          "ocrmypdf":"ocrmypdf","radare2":"r2","ripgrep":"rg",
          "valkey":"valkey-server","ansible":"ansible","godot":"godot",
          "openshot":"openshot-qt","synfig":"synfigstudio"}
ISOLATED={"apktool":HOME/"tools/apktool-3.0.3/bin/apktool",
          "prometheus":HOME/"tools/ferrari-services/prometheus/usr/bin/prometheus",
          "typst":HOME/"tools/typst-0.15.1/extracted/typst-x86_64-unknown-linux-musl/typst",
          "godot":HOME/"tools/godot-4.7.2/extracted/Godot_v4.7.2-stable_linux.x86_64",
          "freecad":HOME/"tools/freecad-1.1.4/archive.AppImage",
          "valkey":HOME/"tools/ferrari-services/valkey-server/bin/valkey-server",
          "ghidra":HOME/"tools/ghidra-12.2/support/analyzeHeadless",
          "jadx":HOME/"tools/jadx-1.5.6/bin/jadx",
          "rea":HOME/".runtime/npm/rea/node_modules/.bin/rea",
          "ruflo":HOME/".runtime/npm/ruflo/node_modules/.bin/ruflo"}
# Python libraries have no command-line executable; detect them as modules instead.
PYTHON_MODULES=runtime_discovery.PYTHON_MODULES
# Base Ferrari operations are independently implemented and tested, not manifest adapters.
BASE_OPERATIONS={"jadx":["apk-decompile"],"blender":["blender-house"],
                 "openscad":["cad-stl"],"libreoffice":["office-pdf"],
                 "imagemagick":["image-resize"],"ffmpeg":["video-thumbnail"],
                 "ifcopenshell":["ifc-summary"],"vite":["vite-build"],
                 "pdftotext":["pdf-text"],"strings":["binary-strings"]}

def python_module_location(tool):
    """Compatible location helper, now including Ferrari-owned virtual environments."""
    name=PYTHON_MODULES.get(tool)
    evidence=runtime_discovery.python_presence(name) if name else None
    return evidence["location"] if evidence else None

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
        if x["mode"] not in {"stdout","file","directory"} or not re.fullmatch("[a-zA-Z0-9._-]{1,90}",x["artifact"]):
            raise ValueError("Invalid artifact")
        if not isinstance(x["args"],list) or "{input}" not in x["args"]:
            raise ValueError("Missing bound input")
        if x["mode"] in {"file","directory"} and "{output}" not in x["args"]:
            raise ValueError("Missing bound output")
        for arg in x["args"]:
            if not isinstance(arg,str) or len(arg)>160:
                raise ValueError("Invalid argument")
            if any(token not in {"{input}","{output}","{query}"} for token in re.findall(r"\{[^{}]*\}",arg)):
                raise ValueError("Unsupported argument placeholder")
        if not x.get("extensions") or not x.get("keywords") or not x.get("category"):
            raise ValueError("Incomplete action metadata")
        result[x["id"]]=x
    return result

def executable(tool,binary=None):
    # Ferraris REA is a Ferrari-owned npm installation, never a PATH/system REA.
    pinned=ISOLATED.get(tool)
    if tool=="rea":
        # npm creates a .bin symlink; accept only one resolving inside Ferrari.
        private=HOME/".runtime/npm/rea"
        node_modules=private/"node_modules"
        if not private.is_dir() or private.is_symlink() or not node_modules.is_dir() or node_modules.is_symlink():
            return None
        return str(pinned) if pinned.is_file() and pinned.resolve().is_relative_to(node_modules.resolve()) else None
    if tool in {"duckdb","polars"}:
        # Only use the Ferrari venv belonging to this exact tool.
        # venv/bin/python may be a normal interpreter symlink created by venv.
        venv=HOME/".runtime/venvs/extended"/tool
        py=venv/"bin/python"
        site=venv/"lib/python3.12/site-packages"/tool
        if (venv.is_dir() and not venv.is_symlink() and
                venv.resolve().is_relative_to(HOME.resolve()) and
                (venv/"pyvenv.cfg").is_file() and py.is_file() and
                site.is_dir() and not site.is_symlink()):
            return str(py)
        return None
    if tool=="comfyui":
        # No executable from PATH: only Ferrari-owned CPU source is valid.
        return None
    if tool=="valkey":
        # Ubuntu provides valkey-server via symlinks in its tools package.
        # Resolve only links staying within the Ferrari-owned service tree.
        private=HOME/"tools/ferrari-services/valkey-server"
        return str(pinned) if pinned.is_file() and pinned.resolve().is_relative_to(private.resolve()) else None
    if tool in {"apktool","prometheus","typst","godot","freecad"}:
        return str(pinned) if pinned.is_file() and not pinned.is_symlink() else None
    if pinned and pinned.is_file():
        return str(pinned)
    return shutil.which(binary or BINARIES.get(tool) or tool) if (binary or BINARIES.get(tool,tool)) else None

def ferrari_source_presence(tool):
    """Recognize a Ferrari-owned CPU source installation, not a PATH copy."""
    if tool!="comfyui":
        return None
    src=HOME/"tools/comfyui-v0.43.0"
    venv=HOME/".runtime/venvs/extended/comfyui"
    py=venv/"bin/python"
    report=HOME/".runtime/expansion-33/heavy.json"
    if not (src.is_dir() and not src.is_symlink() and
            venv.is_dir() and not venv.is_symlink() and
            (src/"main.py").is_file() and py.is_file() and
            report.is_file() and not report.is_symlink() and report.stat().st_size<=32768):
        return None
    if not src.resolve().is_relative_to(HOME.resolve()) or not venv.resolve().is_relative_to(HOME.resolve()):
        return None
    try:
        data=json.loads(report.read_text(encoding="utf-8"))
    except (OSError,ValueError,UnicodeError):
        return None
    if data.get("project")!="motor-ferrari" or not any(
        isinstance(x,dict) and x.get("id")=="comfyui" and
        x.get("status")=="INSTALLED_CPU_NO_MODELS"
        for x in data.get("items",[]) if isinstance(x,dict)
    ):
        return None
    return {"scope":"ferrari_cpu_source","location":str(src),
            "version":"v0.43.0","model_inference_tested":False}

def inventory():
    selected=json.loads((ROOT/"engine/ubuntu_selection.json").read_text())["tools"]
    helpers=json.loads((ROOT/"engine/catalog.json").read_text())["tools"]
    defined=specs()
    ecosystems=runtime_discovery.discover()
    python=ecosystems["python"]["tools"]
    npm=ecosystems["npm"]["tools"]
    containers=ecosystems["containers"]["tools"]
    def inspect(entry,source):
        tool=entry["id"]
        base_bin=entry.get("bin") or BINARIES.get(tool,tool)
        path=executable(tool,base_bin)
        module_evidence=python.get(tool) if not path else None
        npm_evidence=npm.get(tool) if not path and not module_evidence else None
        container_evidence=containers.get(tool) if not path and not module_evidence and not npm_evidence else None
        source_evidence=ferrari_source_presence(tool) if not path else None
        callable_ops=[x["id"] for x in defined.values() if x["tool"]==tool and executable(tool,x["binary"])]
        if not path and callable_ops:
            first=defined[callable_ops[0]]
            path=executable(tool,first["binary"])
        from engine import professional_tools
        available=(professional_tools.bim_available() if tool=="ifcopenshell" else
                   professional_tools.vite_available() if tool=="vite" else bool(path))
        base_ops=BASE_OPERATIONS.get(tool,[]) if available else []
        evidence=module_evidence or npm_evidence or (container_evidence[0] if container_evidence else None) or source_evidence
        present=bool(path or evidence)
        state=("callable" if callable_ops or base_ops else
               "installed_unintegrated" if present else "not_detected")
        detection=("executable" if path else "python_module" if module_evidence else
                   "npm_package" if npm_evidence else "ferrari_container" if container_evidence else
                   "ferrari_cpu_source" if source_evidence else None)
        return {"id":tool,"category":entry["category"],"source":source,"installed":present,
                "path":path or (evidence or {}).get("location"),"detection":detection,
                "ecosystem_evidence":evidence,
                "actions":callable_ops,"base_operations":base_ops,
                "installation_tier":entry.get("installation_tier"),
                "apt_candidate":entry.get("installation_candidate"),
                "status":state}
    records=[inspect(x,"shortlist_56") for x in selected]
    used={x["id"] for x in selected}
    records.extend(inspect(x,"auxiliary_catalogue") for x in helpers if x["id"] not in used)
    picked=records[:len(selected)]
    absent=[p for p in picked if not p["installed"]]
    missing_by_tier={}
    for item in absent:
        tier=item.get("installation_tier") or "unknown"
        missing_by_tier[tier]=missing_by_tier.get(tier,0)+1
    # Include Ferrari-owned installation outcomes in the read-only Skill
    # inventory. These are verified package states, not execution certificates.
    expansion={}
    reports_dir=HOME/".runtime/expansion-33"
    for group,filename in (("services_gui","services-gui.json"),("external","external.json"),("heavy","heavy.json")):
        report=reports_dir/filename
        if report.is_file() and not report.is_symlink() and report.stat().st_size<=131072:
            try:
                content=json.loads(report.read_text(encoding="utf-8"))
                if content.get("project")=="motor-ferrari" and isinstance(content.get("items"),list):
                    expansion[group]=content
            except (OSError,ValueError,UnicodeError):
                pass
    return {"selected":len(selected),"registered_actions":len(defined),
            "installed":sum(x["installed"] for x in records),
            "selected_detected":len(picked)-len(absent),
            "selected_not_detected":len(absent),
            "missing_by_tier":missing_by_tier,
            "callable_actions":sum(len(x["actions"]) for x in records),
            "programs":records,"ecosystems":ecosystems,"expansion":expansion,
            "note":"Read-only binaries, Python specs/venvs, npm manifests and Ferrari-labelled containers; discovery is not a functional test. Base operations and typed adapters remain separate."}

def normalize(value):
    return "".join(x for x in unicodedata.normalize("NFKD",value.lower()) if not unicodedata.combining(x))

def route(request,source=None,query=None):
    if not isinstance(request,str) or not request.strip():raise ValueError("Request required")
    q=normalize(request)
    extension=Path(source).suffix.lower() if source else None
    candidates=[]
    for x in specs().values():
        exe=executable(x["tool"],x["binary"])
        if not exe:continue
        if "{query}" in x["args"] and (not isinstance(query,str) or not query.strip()):
            continue
        if extension and "*" not in x["extensions"] and extension not in x["extensions"]:continue
        matched=[k for k in x["keywords"] if normalize(k) in q]
        if not matched:continue
        candidates.append({"action":x["id"],"tool":x["tool"],"path":exe,
                           "score":10*len(matched)+(5 if extension and "*" not in x["extensions"] else 0),
                           "matched":matched})
    candidates.sort(key=lambda x:(-x["score"],x["action"]))
    return {"request":request,"input":source,"suggestions":candidates,"executed":False}

def auto(request,source,folder=None,execute=False,query=None):
    """Resolve a user request to a single installed adapter; run only if unambiguous."""
    proposal=route(request,source,query)
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
    outcome=(invoke(best["action"],source,folder,query=query)
             if query is not None else invoke(best["action"],source,folder))
    return {**proposal,"selected":best,"status":"completed","executed":True,"result":outcome}

def invoke(action,source,folder,query=None):
    x=specs().get(action)
    if not x:raise ValueError("Unknown executable action")
    exe=executable(x["tool"],x["binary"])
    if not exe:raise RuntimeError("Executor not installed: "+x["binary"])
    requires_query="{query}" in x["args"]
    if requires_query and (not isinstance(query,str) or not 1<=len(query.strip())<=200 or "\x00" in query):
        raise ValueError("This action requires a non-empty query of up to 200 characters")
    if not requires_query and query is not None:
        raise ValueError("This action does not accept a query")
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
    replacements={"{input}":str(inp),"{output}":str(target),"{query}":query}
    args=[exe]+[replacements.get(v,v) for v in x["args"]]
    run_options={}
    if x["tool"]=="rea":
        # The REA CLI, Node, Apktool and REA state belong to Ferrari alone.
        # No global REA command, package root or legacy project's providers.
        node=HOME/"runtimes/node-22.23.4/bin/node"
        apktool=ISOLATED["apktool"]
        if not node.is_file() or node.is_symlink():
            raise RuntimeError("Ferrari private Node 22.23.4 missing")
        if not apktool.is_file() or apktool.is_symlink():
            raise RuntimeError("Ferrari private Apktool missing")
        env=os.environ.copy()
        jdk=HOME/"runtimes/jdk-25.0.5_8"
        env["PATH"]=os.pathsep.join((str(node.parent),str(jdk/"bin"),
                                     str(apktool.parent),env.get("PATH","")))
        env["REA_APKTOOL_COMMAND"]=str(apktool)
        env["JAVA_HOME"]=str(jdk)
        env["GHIDRA_JAVA_HOME"]=str(jdk)
        # The unmodified original REA 6.8.0 requires its verified 12.1.x
        # Ghidra provider, independently from Ferrari's Ghidra 12.2.
        ghidra_provider=HOME/"tools/rea-providers/ghidra-12.1.4"
        if (ghidra_provider.is_dir() and not ghidra_provider.is_symlink() and
                (ghidra_provider/"support/analyzeHeadless").is_file()):
            env["GHIDRA_INSTALL_DIR"]=str(ghidra_provider)
        else:
            env.pop("GHIDRA_INSTALL_DIR",None)
        # The REA JADX provider is the separate audited headless MCP JAR,
        # not the standalone JADX command-line decompiler.
        jadx_bridge=HOME/"tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar"
        if jadx_bridge.is_file() and not jadx_bridge.is_symlink():
            env["REA_JADX_MCP_JAR"]=str(jadx_bridge)
        else:
            env.pop("REA_JADX_MCP_JAR",None)
        env["XDG_CACHE_HOME"]=str(HOME/".runtime/rea-cache")
        env["XDG_CONFIG_HOME"]=str(HOME/".runtime/rea-config")
        env["XDG_DATA_HOME"]=str(HOME/".runtime/rea-data")
        run_options["env"]=env
    if x["tool"] in {"duckdb","polars"}:
        # -m engine.data_profiles is an existing Ferrari module run inside
        # its own Python environment, never another project's packages.
        env=os.environ.copy()
        env.pop("PYTHONPATH",None)
        env.pop("PYTHONHOME",None)
        env["PYTHONNOUSERSITE"]="1"
        run_options["env"]=env
        run_options["cwd"]=str(ROOT)
    if x["tool"] in {"calibre","darktable","krita","gimp","scribus","lmms"}:
        # Installed GUI applications provide dedicated command-line export.
        # Keep per-run caches/preferences inside this Ferrari job, never
        # in Ubuntu's shared user profile or another project's directory.
        env=os.environ.copy()
        home=outdir/".ferrari-application-state"
        for field,part in (("XDG_CACHE_HOME","cache"),
                           ("XDG_CONFIG_HOME","config"),
                           ("XDG_DATA_HOME","data")):
            directory=home/part
            directory.mkdir(parents=True,exist_ok=True)
            env[field]=str(directory)
        if x["tool"]=="calibre":
            env["CALIBRE_CONFIG_DIRECTORY"]=env["XDG_CONFIG_HOME"]
        if x["tool"]=="calibre":
            env["QT_QPA_PLATFORM"]="offscreen"
        if x["tool"]=="krita":
            # Krita ignores Qt offscreen and requires a display. The Ubuntu
            # VPS already has Xvfb; run an ephemeral display for this job.
            xvfb=shutil.which("xvfb-run")
            server=shutil.which("Xvfb")
            if not xvfb or not server:
                raise RuntimeError("Krita requires an existing Xvfb virtual display")
            tmp=home/"tmp"
            tmp.mkdir(parents=True,exist_ok=True)
            env["TMPDIR"]=str(tmp)
            env["QT_QPA_PLATFORM"]="xcb"
            args=[xvfb,"-a",exe]+args[1:]
        if x["tool"]=="lmms":
            # Render only local LMMS project files; never use system user
            # preferences or an interactive audio/desktop service.
            env["HOME"]=str(home)
            env["QT_QPA_PLATFORM"]="offscreen"
            runtime=home/"runtime"
            runtime.mkdir(mode=0o700,exist_ok=True)
            env["XDG_RUNTIME_DIR"]=str(runtime)
        if x["tool"]=="scribus":
            # The Scribus Scripter is executed once per job, with no GUI,
            # ephemeral Xvfb and every writable path inside the Ferrari job.
            xvfb=shutil.which("xvfb-run")
            server=shutil.which("Xvfb")
            if not xvfb or not server:
                raise RuntimeError("Scribus requires an existing Xvfb virtual display")
            target.mkdir(mode=0o700)
            tmp=home/"tmp"
            runtime=home/"runtime"
            tmp.mkdir(parents=True,exist_ok=True)
            runtime.mkdir(mode=0o700)
            env["TMPDIR"]=str(tmp)
            env["XDG_RUNTIME_DIR"]=str(runtime)
            env["QT_QPA_PLATFORM"]="xcb"
            env["HOME"]=str(home)
            env["FERRARI_SCRIBUS_INPUT"]=str(inp)
            env["FERRARI_SCRIBUS_OUTPUT"]=str(target)
            args=[xvfb,"-a",exe,"-g","-ns","-py",str(ROOT/"engine/scribus_job.py")]
        run_options["env"]=env
    if x["tool"]=="gimp":
        # Ferrari already verified GIMP 2.10 console's headless Script-Fu.
        # Only the trusted file paths from this invocation enter Scheme.
        def _scheme_path(path):
            return '"' + str(path).replace("\\","\\\\").replace('"','\\"').replace("\n","\\n") + '"'
        source=_scheme_path(inp)
        output=_scheme_path(target)
        expression=(
            '(let* ((image (car (gimp-file-load RUN-NONINTERACTIVE '
            + source + ' ' + source + '))) '
            '(drawable (car (gimp-image-get-active-drawable image)))) '
            '(gimp-xcf-save RUN-NONINTERACTIVE image drawable '
            + output + ' ' + output + ') '
            '(gimp-image-delete image))'
        )
        args=[exe,"-i","-n","-s","-b",expression,"-b","(gimp-quit 0)"]
    try:
        p=subprocess.run(args,shell=False,capture_output=True,timeout=240,check=False,**run_options)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Executor timeout: "+action) from exc
    if p.returncode:
        raise RuntimeError("Executor failed: "+p.stderr.decode("utf-8","replace")[-1000:])
    if x["tool"]=="lmms":
        # Test a real PCM WAV, never treat a zero-byte or silent export as
        # success just because LMMS exited with code zero.
        if target.is_symlink() or not target.is_file() or target.stat().st_size<128:
            raise RuntimeError("LMMS did not produce a real WAV")
        try:
            with wave.open(str(target),"rb") as audio:
                frames=audio.getnframes()
                if (audio.getnchannels() not in (1,2) or
                        not 8000<=audio.getframerate()<=192000 or
                        not 1<=audio.getsampwidth()<=4 or frames<100):
                    raise RuntimeError("LMMS produced invalid PCM WAV metadata")
                sample=audio.readframes(min(frames,65536))
                if not sample or not any(sample):
                    raise RuntimeError("LMMS produced empty or silent audio")
        except (wave.Error,EOFError,OSError) as exc:
            raise RuntimeError("LMMS did not produce valid PCM WAV") from exc
    if x["tool"]=="scribus":
        pdf=target/"publication.pdf"
        sla=target/"publication.sla"
        if (not pdf.is_file() or pdf.is_symlink() or pdf.stat().st_size<100 or
                pdf.read_bytes()[:5]!=b"%PDF-"):
            raise RuntimeError("Scribus did not produce a valid PDF")
        if (not sla.is_file() or sla.is_symlink() or sla.stat().st_size<100 or
                b"SCRIBUS" not in sla.read_bytes()[:400]):
            raise RuntimeError("Scribus did not produce an editable SLA")
    if x["mode"]=="stdout":
        if not p.stdout:raise RuntimeError("Empty executor output")
        target.write_bytes(p.stdout)
    if x["mode"]=="directory":
        if not target.is_dir() or target.is_symlink():
            raise RuntimeError("Expected decoded directory missing")
        produced=list(target.rglob("*"))
        if not produced or any(p.is_symlink() for p in produced) or not any(p.is_file() for p in produced):
            raise RuntimeError("Decoded directory empty or contains symlinks")
    elif not target.is_file() or target.stat().st_size==0:
        raise RuntimeError("Expected artifact missing")
    return {"id":str(uuid.uuid4()),"at":datetime.now(timezone.utc).isoformat(),
            "operation":"tool","tool":x["tool"],"action":action,"executor":exe,
            "input":str(inp),"artifacts":[str(target)],"confirmed":True}

def main(argv=None):
    ap=argparse.ArgumentParser(description="Ferrari real-program runtime")
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("inventory")
    sub.add_parser("actions")
    r=sub.add_parser("route");r.add_argument("request");r.add_argument("--input");r.add_argument("--query")
    a=sub.add_parser("auto");a.add_argument("request");a.add_argument("--input",required=True)
    a.add_argument("--output");a.add_argument("--query");a.add_argument("--execute",action="store_true")
    i=sub.add_parser("invoke");i.add_argument("--action",required=True)
    i.add_argument("--input",required=True);i.add_argument("--output",required=True);i.add_argument("--query")
    args=ap.parse_args(argv)
    if args.cmd=="inventory":response=inventory()
    elif args.cmd=="actions":
        response=[{"action":x["id"],"tool":x["tool"],"available":bool(executable(x["tool"],x["binary"]))}
                  for x in specs().values()]
    elif args.cmd=="route":response=route(args.request,args.input,args.query)
    elif args.cmd=="auto":response=auto(args.request,args.input,args.output,args.execute,args.query)
    else:response=invoke(args.action,args.input,args.output,args.query)
    print(json.dumps(response,ensure_ascii=False,indent=2))
if __name__=="__main__":
    try:main()
    except (RuntimeError,ValueError,FileNotFoundError,FileExistsError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}),file=sys.stderr)
        sys.exit(2)
