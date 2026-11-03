#!/usr/bin/env bash
# Real Ferrari-only functional smoke: IFC semantic read and Vite static bundle.
set -Eeuo pipefail
umask 077
cd "$(dirname "$0")/.."
ROOT="$HOME/.local/share/motor-ferrari"
bash install/vps-bim-web.sh
bash install/vps-browser-headless.sh
mkdir -p "$ROOT/.runtime"
WORK="$(mktemp -d "$ROOT/.runtime/pro-smoke.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT

"$ROOT/.runtime/venvs/bim/bin/python" - "$WORK/model.ifc" <<'PY'
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import sys
model=ifcopenshell.api.project.create_file()
ifcopenshell.api.root.create_entity(model,ifc_class="IfcProject",name="Ferrari BIM smoke")
ifcopenshell.api.unit.assign_unit(model)
context=ifcopenshell.api.context.add_context(model,context_type="Model")
body=ifcopenshell.api.context.add_context(model,context_type="Model",context_identifier="Body",target_view="MODEL_VIEW",parent=context)
wall=ifcopenshell.api.root.create_entity(model,ifc_class="IfcWall",name="Ferrari wall")
ifcopenshell.api.geometry.edit_object_placement(model,product=wall)
representation=ifcopenshell.api.geometry.add_wall_representation(model,context=body,length=5,height=3,thickness=0.2)
ifcopenshell.api.geometry.assign_representation(model,product=wall,representation=representation)
model.write(sys.argv[1])
PY

python3 -m engine.ferrari run --operation ifc-summary --input "$WORK/model.ifc" --output "$WORK/ifc-result"

python3 - "$WORK/project.zip" <<'PY'
import sys
from zipfile import ZipFile,ZIP_DEFLATED
with ZipFile(sys.argv[1],"w",ZIP_DEFLATED) as z:
    z.writestr("index.html", '<!doctype html><html lang="pt"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body><h1 id="app">Ferrari Vite</h1><nav><a href="#ferrari-section" data-ferrari-test="link">Ir para secção</a></nav><button type="button" data-ferrari-test="button" data-ferrari-activations="0">Ativar pelo teclado</button><form data-ferrari-test="form"><label for="ferrari-message">Mensagem</label><input id="ferrari-message" name="message"><button type="submit">Enviar</button></form><section id="ferrari-section"><h2>Destino acessível</h2></section><script type="module" src="/src/main.js"></script></body></html>')
    z.writestr("src/main.js", 'import "./style.css"; document.querySelector("#app").dataset.ready="yes"; const b=document.querySelector(\'[data-ferrari-test="button"]\'); b.addEventListener("click",()=>{b.dataset.ferrariActivations=String(Number(b.dataset.ferrariActivations)+1)}); const form=document.querySelector(\'[data-ferrari-test="form"]\'); form.addEventListener("submit",e=>{e.preventDefault();form.dataset.ferrariSubmitted="yes"});')
    z.writestr("src/style.css", '#app { color: rebeccapurple; }')
PY
python3 -m engine.ferrari run --operation vite-build --input "$WORK/project.zip" --output "$WORK/web-result"
python3 -m engine.ferrari tools > "$WORK/inventory.json"

python3 - "$WORK" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
ifc=json.loads((p/"ifc-result/ifc-report.json").read_text())
assert ifc["schema"]=="IFC4",ifc
assert ifc["entities_by_type"]["IfcProject"]==1,ifc
assert ifc["entities_by_type"]["IfcWall"]==1,ifc
assert len(ifc["input_sha256"])==64,ifc
assert ifc["geometry"]["counts"]["mesh_measured"]==1,ifc
shape=next(x for x in ifc["geometry"]["elements"] if x["type"]=="IfcWall")
assert shape["status"]=="mesh_measured" and shape["triangle_count"]>0,shape
assert all(abs(actual-target)<0.005 for actual,target in zip(shape["world_bounds"]["size_m"],(5.0,0.2,3.0))),shape
assert ifc["geometry"]["units"]=="metres",ifc
print("FERRARI_IFC_SEMANTIC_REAL=PASS")
print("FERRARI_IFC_GEOMETRY_REAL=PASS")
build=json.loads((p/"web-result/vite-build.json").read_text())
assert build["builder"]=="Vite" and build["version"]=="8.3.5",build
assert (p/"web-result/dist/index.html").is_file(),build
assert any(x.endswith(".js") for x in build["built_files"]),build
assert any(x.endswith(".css") for x in build["built_files"]),build
print("FERRARI_VITE_BUILD_REAL=PASS")
browser=json.loads((p/"web-result/browser-check.json").read_text())
assert browser["status"]=="passed",browser
assert browser["demo_js_ready"]=="yes",browser
assert browser["dom_ready"]=="complete",browser
assert any(name.endswith(".js") for name in browser["served_assets"]),browser
assert any(name.endswith(".css") for name in browser["served_assets"]),browser
assert not browser["blocked_external"] and not browser["page_errors"] and not browser["console_errors"],browser
assert (p/"web-result/browser-screenshot.png").stat().st_size>200,browser
assert build["browser_test"]["status"]=="passed",build
print("FERRARI_VITE_BROWSER_REAL=PASS")
interactions=browser["interactions"]
assert interactions["status"]=="clear",interactions
assert interactions["findings"]==[],interactions
assert interactions["focusable_count"]>=4,interactions
assert interactions["tab_forward"]=="passed",interactions
assert interactions["shift_tab_back"]=="passed",interactions
print("FERRARI_BROWSER_KEYBOARD_REAL=PASS")
for action in ("button_enter","button_space","link_enter","form_enter"):
    assert interactions[action]=="passed",(action,interactions)
print("FERRARI_BROWSER_INTERACTIVE_CONTROLS_REAL=PASS")
mobile=browser["mobile"]
assert mobile["viewport"]=={"width":390,"height":844},mobile
assert mobile["horizontal_overflow_px"]==0,mobile
assert mobile["viewport_meta_present"] is True,mobile
assert mobile["html_lang"]=="pt",mobile
assert mobile["headings_found"]>=1,mobile
assert mobile["demo_js_ready"]=="yes",mobile
assert mobile["spotcheck_status"]=="clear",mobile
assert mobile["findings"]==[],mobile
assert (p/"web-result/browser-mobile.png").stat().st_size>200,mobile
print("FERRARI_VITE_RESPONSIVE_REAL=PASS")
print("FERRARI_BROWSER_A11Y_SPOTCHECK_REAL=PASS")
inv=json.loads((p/"inventory.json").read_text())
assert inv["registered_actions"]==21
for name,expected in (("ifcopenshell","ifc-summary"),("vite","vite-build")):
    entry=next(x for x in inv["programs"] if x["id"]==name)
    assert entry["installed"] and entry["status"]=="callable",entry
    assert expected in entry["base_operations"],entry
print("FERRARI_PROFESSIONAL_INVENTORY=PASS")
PY
