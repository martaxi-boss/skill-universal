"""Motor Ferrari: curated Ubuntu tool discovery and typed execution. No AI host tools."""
import argparse
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import unicodedata
import uuid
from datetime import datetime, timezone
from engine import core

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "engine" / "ferrari_registry.json"
ROUTES = {
 "reverse": ("apk","dex","descompil","decompil","engenharia reversa","firmware","binario","executavel"),
 "web": ("website","site","landing","loja","frontend","html","layout","pagina"),
 "creative": ("criativo","imagem","foto","fotografia","logo","banner","poster","cartaz","design"),
 "docs": ("pdf","documento","docx","excel","ocr","relatorio"),
 "media": ("video","audio","transcri","legend","filme"),
 "automation": ("autom","agente","orquestr","workflow"),
 "dev": ("codigo","program","api","backend","teste","debug")
}
LAYOUTS = {"landing": "website.html", "store": "layouts/store.html", "portfolio": "layouts/portfolio.html", "dashboard": "layouts/dashboard.html"}
OPS = ("web-template","svg-poster","pdf-text","image-resize","video-thumbnail","apk-decompile","binary-strings")

def registry():
    items = json.loads(REGISTRY.read_text(encoding="utf-8"))["projects"]
    if len({p["id"] for p in items}) != len(items):
        raise ValueError("Duplicate tools")
    return items

def system():
    vals = {}
    try:
        for line in Path("/etc/os-release").read_text().splitlines():
            if "=" in line:
                k,v = line.split("=",1)
                vals[k]=v.strip('"')
    except OSError:
        pass
    return {"platform":platform.system(),"distro":vals.get("ID","unknown"),
            "release":vals.get("VERSION_ID","unknown"),
            "architecture":platform.machine(),"cpu":os.cpu_count(),
            "free_disk_gib":round(shutil.disk_usage(ROOT).free/1024**3,2),
            "gui":bool(os.getenv("DISPLAY") or os.getenv("WAYLAND_DISPLAY"))}

def present(p):
    exe=p.get("binary")
    if not exe:
        return False
    if p["id"]=="ghidra":
        home=os.getenv("GHIDRA_INSTALL_DIR")
        return bool(shutil.which(exe) or (home and (Path(home)/"support/analyzeHeadless").is_file()))
    if p["id"] in {"rea","ruflo"}:
        local=ROOT/".runtime"/"npm"/p["id"]/"node_modules"/".bin"/p["id"]
        return bool(shutil.which(p["id"]) or local.is_file())
    return shutil.which(exe) is not None

def inventory(category=None):
    return [{**p,"binary_found":present(p),"certified":False}
            for p in registry() if category is None or p["category"]==category]

def doctor():
    found=[p["id"] for p in inventory() if p["binary_found"]]
    return {"time":datetime.now(timezone.utc).isoformat(),"system":system(),
            "catalogued":len(registry()),"binary_found":found,
            "status":"inventory_only_not_functional_certification"}

def normalize(s):
    return "".join(c for c in unicodedata.normalize("NFKD",s.lower()) if not unicodedata.combining(c))

def plan(request):
    if not request.strip():
        raise ValueError("Empty request")
    q=normalize(request)
    rank={k:sum(3 if len(t)>5 else 1 for t in terms if t in q) for k,terms in ROUTES.items()}
    best=max(rank,key=lambda k:(rank[k],k=="reverse"))
    if rank[best]==0:
        best="dev"
    cats={"creative":{"creative","image-ai"},"media":{"media","image-ai"},
          "automation":{"automation","orchestration"},"dev":{"dev","local-ai"}}.get(best,{best})
    selected=[p for p in inventory() if p["category"] in cats]
    selected.sort(key=lambda p:(not p["binary_found"],p.get("requires_gpu",False),-p["stars_snapshot"]))
    return {"request":request,"route":best,"selected":[{"id":p["id"],"repository":p["repository"],
            "binary_found":p["binary_found"],"apt":p.get("apt")} for p in selected[:15]],
            "executed":False,"notice":"Candidates only; no tool launched"}

def packages(profile="maximum",include_gui=True):
    cats={"core":{"dev","automation"},"web":{"dev","web"},"reverse":{"dev","reverse"},
          "creative":{"creative","media"},"docs":{"docs"},"media":{"media","creative"},
          "maximum":set(p["category"] for p in registry())}
    if profile not in cats:
        raise ValueError("Unknown profile")
    base={"ca-certificates","git","python3","python3-venv","curl","file","jq","zip","unzip"}
    if profile in {"web","maximum"}:
        base.update({"nodejs","npm","build-essential"})
    if profile in {"reverse","maximum"}:
        base.update({"binutils","gdb","strace","openjdk-21-jdk-headless"})
    if profile in {"docs","maximum"}:
        base.update({"poppler-utils","graphviz"})
    base.update(p["apt"] for p in registry() if p["category"] in cats[profile] and
                p.get("apt") and (include_gui or not p.get("gui")))
    return sorted(base)

def _input(path):
    if not path:
        raise ValueError("Missing input")
    p=Path(path)
    if p.is_symlink() or not p.is_file():
        raise ValueError("Input must be a non-symlink regular file")
    return p.resolve(strict=True)

def _output(folder,name):
    p=Path(folder).resolve()/name
    if p.exists() or p.is_symlink():
        raise FileExistsError("Refusing overwrite: "+str(p))
    p.parent.mkdir(parents=True,exist_ok=True)
    return p

def _exe(name):
    p=shutil.which(name)
    if not p:
        raise RuntimeError("Missing Ubuntu executor: "+name)
    return p

def _call(args,timeout=240,stdout=None):
    try:
        p=subprocess.run(args,shell=False,stdout=stdout if stdout is not None else subprocess.PIPE,
                         stderr=subprocess.PIPE,timeout=timeout,check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Executor timeout") from exc
    if p.returncode:
        raise RuntimeError("Executor failed: "+p.stderr.decode("utf-8","replace")[:800])

def run(op,output,source=None,title="Novo Projeto",layout="landing"):
    if op not in OPS:
        raise ValueError("Unsupported operation: no arbitrary shell")
    if platform.system()!="Linux":
        raise RuntimeError("Linux required")
    p=_input(source) if op not in {"web-template","svg-poster"} else None
    if op=="web-template":
        dest=_output(output,"site/index.html")
        if layout not in LAYOUTS:
            raise ValueError("Unknown layout")
        if layout=="landing":
            artifacts=core.create_website(dest.parent.parent,title)
        else:
            import html
            base=ROOT/"templates"/LAYOUTS[layout]
            dest.write_text(base.read_text(encoding="utf-8").replace("{{TITLE}}",html.escape(title[:90],quote=True)),encoding="utf-8")
            artifacts=[dest]
        exe="built-in:website:"+layout
    elif op=="svg-poster":
        dest=_output(output,"creative/poster.svg")
        artifacts=core.create_creative(dest.parent.parent,title)
        exe="built-in:creative"
    elif op=="pdf-text":
        if p.suffix.lower()!=".pdf": raise ValueError("PDF expected")
        dest=_output(output,"extracted.txt")
        exe=_exe("pdftotext")
        _call([exe,"-layout",str(p),str(dest)])
        artifacts=[dest]
    elif op=="image-resize":
        if p.suffix.lower() not in {".png",".jpg",".jpeg",".webp",".tif",".tiff"}:
            raise ValueError("Unsupported image")
        dest=_output(output,"image-1600.png")
        exe=_exe("convert")
        _call([exe,str(p),"-auto-orient","-resize","1600x1600>",str(dest)])
        artifacts=[dest]
    elif op=="video-thumbnail":
        dest=_output(output,"thumbnail.png")
        exe=_exe("ffmpeg")
        _call([exe,"-nostdin","-hide_banner","-loglevel","error","-i",str(p),"-frames:v","1",str(dest)])
        artifacts=[dest]
    elif op=="apk-decompile":
        if p.suffix.lower() not in {".apk",".dex",".jar"}:
            raise ValueError("APK/DEX/JAR expected")
        dest=_output(output,"jadx-decompiled")
        exe=_exe("jadx")
        _call([exe,"-d",str(dest),str(p)],timeout=600)
        artifacts=[dest]
    else:
        dest=_output(output,"strings.txt")
        exe=_exe("strings")
        with dest.open("wb") as f: _call([exe,"-a","-n","6",str(p)],stdout=f)
        artifacts=[dest]
    return {"id":str(uuid.uuid4()),"at":datetime.now(timezone.utc).isoformat(),
            "operation":op,"executor":exe,"input":str(p) if p else None,
            "artifacts":[str(x) for x in artifacts],"confirmed":all(x.exists() for x in artifacts)}

def main(argv=None):
    ap=argparse.ArgumentParser(description="Motor Ferrari Ubuntu")
    sub=ap.add_subparsers(dest="cmd",required=True)
    sub.add_parser("doctor")
    ls=sub.add_parser("list");ls.add_argument("--category")
    pl=sub.add_parser("plan");pl.add_argument("request")
    pk=sub.add_parser("packages")
    pk.add_argument("--profile",default="maximum");pk.add_argument("--headless",action="store_true")
    pk.add_argument("--plain",action="store_true")
    ru=sub.add_parser("run")
    ru.add_argument("--operation",required=True,choices=OPS)
    ru.add_argument("--input",dest="source")
    ru.add_argument("--output",required=True)
    ru.add_argument("--title",default="Novo Projeto")
    ru.add_argument("--layout",choices=sorted(LAYOUTS),default="landing")
    a=ap.parse_args(argv)
    if a.cmd=="doctor": result=doctor()
    elif a.cmd=="list": result=inventory(a.category)
    elif a.cmd=="plan": result=plan(a.request)
    elif a.cmd=="packages":
        result=packages(a.profile,not a.headless)
        if a.plain:
            print("\n".join(result));return
    else: result=run(a.operation,a.output,a.source,a.title,a.layout)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
    try: main()
    except (ValueError,RuntimeError,FileNotFoundError,FileExistsError) as exc:
        print(json.dumps({"ok":False,"error":str(exc)}),file=sys.stderr)
        sys.exit(2)
