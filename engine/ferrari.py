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
ROUTES.update({
 "cad": ("cad", "freecad", "openscad", "desenho tecnico", "modelo 3d", "modelacao", "pcb", "eletronica", "prototipagem"),
 "diagrams": ("diagrama", "fluxograma", "mapa mental", "wireframe", "whiteboard", "erd", "esquema"),
 "geo": ("mapas", "cartografia", "gis", "qgis", "geoespacial", "fotogrametria", "geografia"),
 "animation": ("animacao", "animar", "motion graphics", "efeitos especiais", "vfx", "composicao"),
 "audio": ("audio", "podcast", "musica", "som", "voz", "narracao", "transcricao", "sintese de voz"),
 "vision": ("visao computacional", "identificar imagem", "opencv", "reconhecimento de imagem", "remover fundo"),
 "data": ("dados", "estatistica", "analise de dados", "sql", "base de dados", "dashboard", "dashboards", "grafico"),
 "monitor": ("monitorizacao", "metricas", "observabilidade", "prometheus", "grafana"),
 "infra": ("servidor", "deploy", "implantacao", "infraestrutura", "containers", "vps", "git"),
 "game": ("jogo", "game", "godot", "videojogo"),
 "productivity": ("notas", "gestao de projeto", "produtividade", "documentacao"),
})
LAYOUTS = {"landing": "website.html", "store": "layouts/store.html", "portfolio": "layouts/portfolio.html", "dashboard": "layouts/dashboard.html"}
OPS = ("web-template","svg-poster","pdf-text","image-resize","video-thumbnail","apk-decompile","binary-strings")

def registry():
    """Merge checked GitHub repositories without claiming installation or license validation."""
    items = json.loads(REGISTRY.read_text(encoding="utf-8"))["projects"]
    expansion = ROOT / "engine" / "ferrari_expansion.json"
    if expansion.is_file():
        for source in json.loads(expansion.read_text(encoding="utf-8"))["projects"]:
            extra = dict(source)
            extra["binary"] = None
            extra["apt"] = None  # APT candidates are NOT certified Ubuntu package names.
            extra["gui"] = source.get("resources") == "gui"
            extra["requires_gpu"] = source.get("resources") == "gpu"
            extra["stars_snapshot"] = int(source["stars_snapshot"])
            extra["installation"] = source["install_method"] + "-candidate"
            extra["license"] = source.get("license_spdx") or "REVIEW_REQUIRED"
            items.append(extra)
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
    """Rank every supported domain, keeping separate installation and execution evidence."""
    if not request.strip():
        raise ValueError("Empty request")
    q = normalize(request)
    scores = {key: sum((4 if len(term) > 5 else 2) for term in terms if term in q)
              for key, terms in ROUTES.items()}
    ordered = sorted(scores, key=lambda key: (-scores[key], key != "reverse", key))
    best = ordered[0] if scores[ordered[0]] else "dev"
    active = [key for key in ordered if scores[key] > 0][:4] or ["dev"]
    cats = {
        "creative": {"creative", "design", "image-ai", "vision", "animation"},
        "media": {"media", "animation", "audio"},
        "automation": {"automation", "orchestration", "infra"},
        "dev": {"dev", "infra"},
        "docs": {"docs", "productivity"},
        "data": {"data", "diagrams"},
        "web": {"web", "design", "diagrams"},
        "cad": {"cad", "geo"},
        "audio": {"audio", "media"},
        "game": {"game", "animation", "creative"},
    }
    categories = set()
    for route in active:
        categories.update(cats.get(route, {route}))
    selected = [p for p in inventory() if p["category"] in categories]
    # Real executors first; otherwise prefer simpler/free-license-reviewed tools,
    # then GitHub popularity as one of several secondary signals.
    selected.sort(key=lambda p: (
        not p["binary_found"],
        p.get("license_status") == "review_required" or p.get("license") in {"REVIEW_REQUIRED", "verify-license-before-use"},
        p.get("resources") in {"gpu", "heavy"} or p.get("requires_gpu", False),
        -p["stars_snapshot"]
    ))
    results = [{
        "id": p["id"], "repository": p["repository"], "category": p["category"],
        "binary_found": p["binary_found"], "ubuntu_certified": False,
        "license_review_required": p.get("license_status") == "review_required" or
            p.get("license") in {"REVIEW_REQUIRED", "verify-license-before-use"},
        "installation": p.get("installation", "unknown"),
        "apt": p.get("apt"), "resources": p.get("resources", "unknown"),
        "capabilities": p.get("capabilities", []),
        "stars_snapshot": p["stars_snapshot"]
    } for p in selected[:30]]
    return {"request": request, "route": best, "routes": active,
            "selected": results, "executed": False,
            "catalogued_total": len(registry()),
            "notice": "Candidates only, not Ubuntu-installed or certified. No executor launched."}

def alternatives(product):
    """Locate independent, licensed Ubuntu alternatives to paid products.

    Reverse engineering can enable compatible formats/protocols, but does
    not grant the vendor's proprietary binaries, accounts or license rights.
    """
    if not product.strip():
        raise ValueError("Product name required")
    data=json.loads((ROOT/"engine"/"commercial_alternatives.json").read_text(encoding="utf-8"))
    query=normalize(product)
    matched=[]
    for entry in data["entries"]:
        for alias in entry.get("aliases",[]):
            needle=normalize(alias)
            if needle in query or query == needle:
                matched.append((len(needle),entry))
    if not matched:
        return {"product":product,"match":None,"alternatives":[],
                "notice":"No verified equivalent mapped; inspect free licensed upstreams."}
    entry=max(matched,key=lambda x:x[0])[1]
    known={p["id"]:p for p in inventory()}
    candidates=[]
    for name in entry["tools"]:
        p=known.get(name)
        candidates.append({"id":name,"repository":p["repository"] if p else None,
            "binary_found":p["binary_found"] if p else False,
            "license_review_required":p.get("license_status")=="review_required" if p else True,
            "ubuntu_certified":False})
    return {"product":product,"match":entry["product"],"domain":entry["domain"],
        "coverage":entry["coverage"],"alternatives":candidates,
        "notice":"Legal free alternatives, not a cracked original or guaranteed file compatibility."}

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
    al=sub.add_parser("alternatives");al.add_argument("product")
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
    elif a.cmd=="alternatives": result=alternatives(a.product)
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
