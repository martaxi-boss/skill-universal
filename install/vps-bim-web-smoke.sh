#!/usr/bin/env bash
# Real Ferrari-only functional smoke: IFC semantic read and Vite static bundle.
set -Eeuo pipefail
umask 077
cd "$(dirname "$0")/.."
ROOT="$HOME/.local/share/motor-ferrari"
bash install/vps-bim-web.sh
mkdir -p "$ROOT/.runtime"
WORK="$(mktemp -d "$ROOT/.runtime/pro-smoke.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT

"$ROOT/.runtime/venvs/bim/bin/python" - "$WORK/model.ifc" <<'PY'
import ifcopenshell
import ifcopenshell.guid
import sys
model=ifcopenshell.file(schema="IFC4")
model.createIfcProject(GlobalId=ifcopenshell.guid.new(),Name="Ferrari BIM smoke")
model.createIfcWall(GlobalId=ifcopenshell.guid.new(),Name="Ferrari wall")
model.write(sys.argv[1])
PY

python3 -m engine.ferrari run --operation ifc-summary --input "$WORK/model.ifc" --output "$WORK/ifc-result"

python3 - "$WORK/project.zip" <<'PY'
import sys
from zipfile import ZipFile,ZIP_DEFLATED
with ZipFile(sys.argv[1],"w",ZIP_DEFLATED) as z:
    z.writestr("index.html", '<!doctype html><html><head><meta charset="utf-8"></head><body><h1 id="app">Ferrari Vite</h1><script type="module" src="/src/main.js"></script></body></html>')
    z.writestr("src/main.js", 'import "./style.css"; document.querySelector("#app").dataset.ready="yes";')
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
print("FERRARI_IFC_SEMANTIC_REAL=PASS")
build=json.loads((p/"web-result/vite-build.json").read_text())
assert build["builder"]=="Vite" and build["version"]=="8.3.5",build
assert (p/"web-result/dist/index.html").is_file(),build
assert any(x.endswith(".js") for x in build["built_files"]),build
assert any(x.endswith(".css") for x in build["built_files"]),build
print("FERRARI_VITE_BUILD_REAL=PASS")
inv=json.loads((p/"inventory.json").read_text())
assert inv["registered_actions"]==21
for name,expected in (("ifcopenshell","ifc-summary"),("vite","vite-build")):
    entry=next(x for x in inv["programs"] if x["id"]==name)
    assert entry["installed"] and entry["status"]=="callable",entry
    assert expected in entry["base_operations"],entry
print("FERRARI_PROFESSIONAL_INVENTORY=PASS")
PY
