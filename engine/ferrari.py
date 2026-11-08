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
FERRARI_HOME = Path("/srv/projects/skill-universal")
REGISTRY = ROOT / "engine" / "catalog.json"
ROUTES = {
 "reverse": ("apk","dex","descompil","decompil","engenharia reversa","firmware","binario","executavel"),
 "web": ("website","web","site","landing","loja","frontend","html","layout","pagina"),
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
# Operation IDs are also read from the same canonical universal registry;
# never maintain a separate Ferrari operation allowlist in Python source.
OPS = tuple(item["name"] for item in json.loads(REGISTRY.read_text(encoding="utf-8"))["functions"]
            if item["kind"] == "operation")

def registry():
    """Discover upstream entries from the Ferrari's only tool catalog.

    An upstream candidate is NOT an installed or working program.  Preserve
    the original curated/source order, and never merge duplicate tool IDs.
    """
    from engine import catalog_registry
    catalog = catalog_registry.read_catalog(REGISTRY)
    if catalog.get("schema") != 2:
        raise ValueError("Unsupported Ferrari tool catalog")
    items = []
    for tool in sorted(
        (x for x in catalog["tools"] if "upstream" in x),
        key=lambda x: x["upstream_order"]
    ):
        source = dict(tool["upstream"])
        if tool.get("upstream_source") == "expansion":
            source["binary"] = None
            source["apt"] = (source.get("package_candidate")
                             if source.get("install_method") == "apt"
                             and source.get("license_status") == "github_declared"
                             else None)
            source["gui"] = source.get("resources") == "gui"
            source["requires_gpu"] = source.get("resources") == "gpu"
            source["stars_snapshot"] = int(source["stars_snapshot"])
            source["installation"] = source["install_method"] + "-candidate"
            source["license"] = source.get("license_spdx") or "REVIEW_REQUIRED"
        items.append(source)
    if len({p["id"] for p in items}) != len(items):
        raise ValueError("Duplicate upstream tools")
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
    """Report only Ferrari-owned executors, never Ubuntu PATH availability."""
    name=p.get("id")
    if name=="rea":
        private=FERRARI_HOME/".runtime/npm/rea"
        modules=private/"node_modules"
        cli=modules/".bin/rea"
        return (private.is_dir() and not private.is_symlink()
                and modules.is_dir() and not modules.is_symlink()
                and cli.is_file() and cli.resolve().is_relative_to(modules.resolve()))
    if name=="apktool":
        local=FERRARI_HOME/"tools/apktool-3.0.3/bin/apktool"
        return local.is_file() and not local.is_symlink()
    if name in {"blender","openscad","libreoffice"}:
        from engine import cad_tools
        try:
            cad_tools._binary(name)
            return True
        except RuntimeError:
            return False
    from engine import tool_runtime
    return tool_runtime.executable(name,p.get("binary")) is not None

def inventory(category=None):
    return [{**p,"binary_found":present(p),"certified":False}
            for p in registry() if category is None or p["category"]==category]

def doctor():
    found=[p["id"] for p in inventory() if p["binary_found"]]
    return {"time":datetime.now(timezone.utc).isoformat(),"system":system(),
            "catalogued":len(registry()),"ubuntu_shortlisted":len(ubuntu_selection()),
            "binary_found":found, "vps_certified_count":0,
            "status":"inventory_only_not_functional_certification"}


def ubuntu_selection():
    """Only curated Ubuntu evidence; unreviewed discovery stays out of planning."""
    from engine import catalog_registry
    catalog = catalog_registry.read_catalog(REGISTRY)
    manifest = dict(catalog["ubuntu_metadata"])
    manifest["tools"] = [x["ubuntu"] for x in sorted(
        (x for x in catalog["tools"] if "ubuntu" in x),
        key=lambda x:x["ubuntu_order"])]
    if manifest.get("platform") != "Ubuntu 24.04":
        raise ValueError("Curated platform must be Ubuntu 24.04")
    ids = [p["id"] for p in manifest["tools"]]
    if len(set(ids)) != len(ids):
        raise ValueError("Duplicated curated tools")
    valid = {"apt_candidate_found_on_ubuntu2404_runner", "upstream_linux_supported_not_host_certified",
             "awaiting_gui_apt_preflight", "gui_apt_candidate_found_on_ubuntu2404_runner"}
    known = {p["id"]: p for p in inventory()}
    result = []
    for item in manifest["tools"]:
        if item["selection_status"] not in valid:
            continue
        upstream = known.get(item["id"])
        if upstream is None:
            upstream = {"id": item["id"], "repository": item["repo"], "category": item["category"],
                        "stars_snapshot": 0, "binary_found": False}
        result.append({**upstream, "curated_status": item["selection_status"],
                       "curated_tier": item["installation_tier"],
                       "curated_priority": item["priority"],
                       "curated_license": item["license"],
                       "license_review_required": item.get("license_review_required", True),
                       "ubuntu_evidence": item["evidence"],
                       "package_candidate": item.get("installation_candidate"),
                       "runtime_note": item["runtime_note"],
                       "ubuntu_certified": False, "vps_installed": False})
    return result

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
        "diagrams": {"diagrams", "design"},
        "cad": {"cad", "geo"},
        "audio": {"audio", "media"},
        "game": {"game", "animation", "creative"},
    }
    categories = set()
    for route in active:
        categories.update(cats.get(route, {route}))
    selected = [p for p in ubuntu_selection() if p["category"] in categories]
    # Real executors first; otherwise prefer simpler/free-license-reviewed tools,
    # then GitHub popularity as one of several secondary signals.
    selected.sort(key=lambda p: (
        not p["binary_found"],
        p.get("license_review_required", False) or p.get("license_status") == "review_required" or p.get("license") in {"REVIEW_REQUIRED", "verify-license-before-use"},
        p.get("resources") in {"gpu", "heavy"} or p.get("requires_gpu", False),
        -p["stars_snapshot"]
    ))
    # Reserve places across every selected category. A niche design/CAD tool must
    # not disappear simply because broad web repositories have more stars.
    balanced = []
    seen_ids = set()
    for category in sorted(categories):
        for project in (p for p in selected if p["category"] == category):
            if project["id"] not in seen_ids:
                balanced.append(project)
                seen_ids.add(project["id"])
            if sum(1 for p in balanced if p["category"] == category) >= 3:
                break
    for project in selected:
        if project["id"] not in seen_ids:
            balanced.append(project)
            seen_ids.add(project["id"])
    selected = balanced
    results = [{
        "id": p["id"], "repository": p["repository"], "category": p["category"],
        "binary_found": p["binary_found"], "ubuntu_certified": False,
        "license_review_required": bool(p.get("license_review_required")) or p.get("license_status") == "review_required" or
            p.get("license") in {"REVIEW_REQUIRED", "verify-license-before-use"},
        "installation": p.get("installation", "unknown"),
        "apt": p.get("package_candidate"), "resources": p.get("resources", "unknown"),
        "ubuntu_selection_status": p["curated_status"], "ubuntu_evidence": p["ubuntu_evidence"],
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

def discover(query, minimum_stars=100, limit=15):
    from engine.github_discovery import discover as upstream_discover
    return upstream_discover(query, minimum_stars=minimum_stars, limit=limit)

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
    approved = ubuntu_selection()
    base.update(p["package_candidate"] for p in approved
                if p["category"] in cats[profile] and p.get("package_candidate")
                and (include_gui or p["curated_tier"] != "desktop_candidate")
                and not p["license_review_required"]
                and p["curated_status"] in {
                    "apt_candidate_found_on_ubuntu2404_runner",
                    "gui_apt_candidate_found_on_ubuntu2404_runner"})

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
    # Missing private binaries are unavailable, not replaced by the Ubuntu PATH.
    paths=[FERRARI_HOME/"tools/ubuntu-cli/bin"/name]
    if name=="jadx":
        paths.append(FERRARI_HOME/"tools/jadx-1.5.6/bin/jadx")
    for p in paths:
        if (p.is_file() and os.access(p,os.X_OK)
                and p.resolve().is_relative_to(FERRARI_HOME.resolve())):
            return str(p)
    raise RuntimeError("FERRARI_PRIVATE_EXECUTOR_MISSING="+name)

def _call(args,timeout=240,stdout=None):
    env=os.environ.copy()
    own=FERRARI_HOME/"tools/ubuntu-cli"
    if Path(args[0]).parent==own/"bin":
        env["LD_LIBRARY_PATH"]=str(own/"lib")
        env["HOME"]=str(FERRARI_HOME/".runtime")
        env["TMPDIR"]=str(FERRARI_HOME/".runtime")
        env["MAGICK_CONFIGURE_PATH"]=str(own/"etc/ImageMagick-6")
        env["MAGICK_CODER_MODULE_PATH"]=str(own/"lib/ImageMagick/coders")
    try:
        p=subprocess.run(args,shell=False,stdout=stdout if stdout is not None else subprocess.PIPE,
                         stderr=subprocess.PIPE,timeout=timeout,check=False,env=env)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Executor timeout") from exc
    if p.returncode:
        raise RuntimeError("Executor failed: "+p.stderr.decode("utf-8","replace")[:800])

def run(op,output,source=None,title="Novo Projeto",layout="landing"):
    if op not in OPS:
        raise ValueError("Unsupported operation: no arbitrary shell")
    if system()["distro"] != "ubuntu":
        raise RuntimeError("Ferrari execution is supported only on Ubuntu")
    p=_input(source) if op not in {"web-template","svg-poster","blender-house","godot-starter","valkey-kv-test"} else None
    if op=="web-template" and source is not None:
        # Optional HTML input uses the existing Skill operation and transport;
        # no new operation ID, validator pin, SSH or 40-action manifest changes.
        from engine import openpencil
        exe,artifacts=openpencil.convert_html(_input(source),output)
    elif op=="web-template":
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
    elif op=="image-analyze":
        # Reuse the Ferrari-owned Docling/OpenCV virtualenv for bounded
        # offline image diagnostics; installation alone never grants an action.
        from engine import image_tools
        exe,artifacts=image_tools.analyze(p,Path(output).resolve())
    elif op in {"librecad-dxf-pdf", "qgis-buffer-5m", "godot-starter"}:
        from engine import program_adapters
        folder = Path(output).resolve()
        if op == "librecad-dxf-pdf":
            exe, artifacts = program_adapters.librecad_dxf_pdf(p, folder)
        elif op == "qgis-buffer-5m":
            exe, artifacts = program_adapters.qgis_buffer(p, folder)
        else:
            exe, artifacts = program_adapters.godot_starter(folder)
    elif op=="prometheus-rule-check":
        from engine import monitor_tools
        exe,artifacts=monitor_tools.check_rules(p,Path(output).resolve())
    elif op=="docling-docx-markdown":
        from engine import document_tools
        exe,artifacts=document_tools.convert(p,Path(output).resolve())
    elif op=="valkey-kv-test":
        from engine import cache_tools
        exe,artifacts=cache_tools.prove(Path(output).resolve())
    elif op=="audio-transcribe":
        # One universal catalog entry, executed using the Ferrari-owned
        # faster-whisper venv and offline model. NOT a TTS or paid API route.
        from engine import audio_tools
        exe,artifacts=audio_tools.transcribe(p,Path(output).resolve())
    elif op in {"ifc-summary","vite-build"}:
        from engine import professional_tools
        folder=Path(output).resolve()
        if op=="ifc-summary":
            exe,artifacts=professional_tools.ifc_summary(p,folder)
        else:
            exe,artifacts=professional_tools.vite_build(p,folder)
    elif op in {"cad-stl","blender-house","office-pdf"}:
        from engine import cad_tools
        folder=Path(output).resolve()
        if op=="cad-stl":
            exe,artifacts=cad_tools.scad_to_stl(p,folder)
        elif op=="blender-house":
            exe,artifacts=cad_tools.blender_house(folder,title=title)
        else:
            exe,artifacts=cad_tools.office_pdf(p,folder)
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
    ls.add_argument("--include-discovery",action="store_true",help="Show unvetted sources too")
    pl=sub.add_parser("plan");pl.add_argument("request")
    sub.add_parser("tools")
    sub.add_parser("actions")
    rr=sub.add_parser("route");rr.add_argument("request");rr.add_argument("--input");rr.add_argument("--query")
    au=sub.add_parser("auto");au.add_argument("request");au.add_argument("--input",required=True)
    au.add_argument("--output");au.add_argument("--query");au.add_argument("--execute",action="store_true")
    iv=sub.add_parser("invoke");iv.add_argument("--action",required=True)
    iv.add_argument("--input",required=True);iv.add_argument("--output",required=True);iv.add_argument("--query")
    al=sub.add_parser("alternatives");al.add_argument("product")
    ds=sub.add_parser("discover");ds.add_argument("query");ds.add_argument("--min-stars",type=int,default=100);ds.add_argument("--limit",type=int,default=15)
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
    elif a.cmd=="list": result=inventory(a.category) if a.include_discovery else [p for p in ubuntu_selection() if not a.category or p["category"]==a.category]
    elif a.cmd=="plan": result=plan(a.request)
    elif a.cmd in {"tools","actions","route","auto","invoke"}:
        from engine import tool_runtime
        if a.cmd=="tools":result=tool_runtime.inventory()
        elif a.cmd=="actions":
            result=[{"action":x["id"],"tool":x["tool"],
                     "available":bool(tool_runtime.executable(x["tool"],x["binary"]))}
                    for x in tool_runtime.specs().values()]
        elif a.cmd=="route":result=tool_runtime.route(a.request,a.input,a.query)
        elif a.cmd=="auto":result=tool_runtime.auto(a.request,a.input,a.output,a.execute,a.query)
        else:result=tool_runtime.invoke(a.action,a.input,a.output,a.query)
    elif a.cmd=="alternatives": result=alternatives(a.product)
    elif a.cmd=="discover": result=discover(a.query,a.min_stars,a.limit)
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
