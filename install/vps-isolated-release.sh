#!/usr/bin/env bash
# Ferrari versioned private-only release. Fail closed before modifying current.
# Uses the existing project, its own runtime, and the already installed private tools.
# No service/SSH/Ubuntu-package changes or deletions outside Ferrari.
set -Eeuo pipefail
umask 077

ROOT="/srv/projects/skill-universal"
SHA="${1:-}"
MODE="${2:---check}"
[[ "$SHA" =~ ^[a-f0-9]{40}$ ]] || { echo FERRARI_RELEASE_SHA_REQUIRED >&2; exit 2; }
[[ "$MODE" == "--check" || "$MODE" == "--activate" ]] || {
  echo 'Expected --check or --activate' >&2; exit 2;
}
[[ $(id -u) -ne 0 && -d "$ROOT" && ! -L "$ROOT" ]] || {
  echo FERRARI_RELEASE_OWNER_INVALID >&2; exit 2;
}
[[ -d "$ROOT/releases" && ! -L "$ROOT/releases"
   && -d "$ROOT/.runtime" && ! -L "$ROOT/.runtime"
   && -d "$ROOT/tools" && ! -L "$ROOT/tools"
   && "$(stat -c %u "$ROOT")" == "$(id -u)" ]] || {
  echo FERRARI_RELEASE_STRUCTURE_INVALID >&2; exit 2;
}
PRIVATE_PYTHON="$ROOT/runtimes/python3.12/bin/python3.12"
[[ -x "$PRIVATE_PYTHON" ]] || { echo FERRARI_RELEASE_PYTHON_MISSING >&2; exit 2; }
for rel in tools/blender/blender tools/openscad/bin/openscad tools/libreoffice/program/soffice; do
  path="$ROOT/$rel"
  [[ -f "$path" && -x "$path" && ! -L "$path" ]] || {
    echo "FERRARI_RELEASE_PRIVATE_TOOL_MISSING=$rel" >&2; exit 3;
  }
  real="$(realpath -e "$path")"
  [[ "$real" == "$ROOT"/tools/* ]] || { echo FERRARI_RELEASE_TOOL_ESCAPE >&2; exit 3; }
done
PREVIOUS="$(realpath -e "$ROOT/current")"
[[ -L "$ROOT/current" && "$PREVIOUS" == "$ROOT"/releases/*
   && -f "$PREVIOUS/engine/ferrari.py" ]] || {
  echo FERRARI_CURRENT_RELEASE_UNSAFE >&2; exit 3;
}
[[ "$PREVIOUS" != "$ROOT/releases/$SHA" ]] || {
  echo FERRARI_RELEASE_ALREADY_ACTIVE; exit 0;
}
WORK="$(mktemp -d "$ROOT/.runtime/.release-verify-XXXXXXXX")"
STAGED=""
SWITCHED=0
PASSED=0
cleanup() {
  code=$?
  if [[ "$SWITCHED" == 1 && "$PASSED" != 1 ]]; then
    back="$ROOT/.current.rollback.$$"
    if [[ ! -e "$back" && ! -L "$back" ]]; then
      ln -s "$PREVIOUS" "$back"
      mv -Tf "$back" "$ROOT/current"
      echo FERRARI_RELEASE_ROLLBACK=PASS >&2
    fi
  fi
  if [[ -n "$STAGED" && "$STAGED" == "$ROOT"/releases/.staging-* && -d "$STAGED" && ! -L "$STAGED" ]]; then
    rm -rf -- "$STAGED"
  fi
  if [[ "$WORK" == "$ROOT"/.runtime/.release-verify-* && -d "$WORK" && ! -L "$WORK" ]]; then
    rm -rf -- "$WORK"
  fi
  exit "$code"
}
trap cleanup EXIT

mkdir -p "$WORK/home" "$WORK/tmp" "$WORK/cache" "$WORK/config" "$WORK/data" "$WORK/run"
chmod 700 "$WORK/run"
export HOME="$WORK/home"
export TMPDIR="$WORK/tmp"
export XDG_CACHE_HOME="$WORK/cache"
export XDG_CONFIG_HOME="$WORK/config"
export XDG_DATA_HOME="$WORK/data"
export XDG_RUNTIME_DIR="$WORK/run"
export QT_QPA_PLATFORM=offscreen
export LIBGL_ALWAYS_SOFTWARE=1
export OMP_NUM_THREADS=2
export PYTHONDONTWRITEBYTECODE=1
JDK="$ROOT/runtimes/jdk-25.0.5_8"
if [[ -x "$JDK/bin/java" ]]; then
  export JAVA_HOME="$JDK"
  export JRE_HOME="$JDK"
  export PATH="$JDK/bin:$ROOT/tools/ubuntu-cli/bin:$PATH"
fi

RELEASE="$ROOT/releases/$SHA"
if [[ -e "$RELEASE" || -L "$RELEASE" ]]; then
  [[ ! -L "$RELEASE" && -d "$RELEASE" && -f "$RELEASE/engine/ferrari.py" ]] || {
    echo FERRARI_RELEASE_EXISTING_DIR_CONFLICT >&2; exit 4;
  }
  echo FERRARI_RELEASE_REUSING_EXISTING=YES
else
  STAGED="$(mktemp -d "$ROOT/releases/.staging-XXXXXXXX")"
  echo FERRARI_RELEASE_SOURCE_DOWNLOADING
  curl --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
       --connect-timeout 20 --retry 2 --max-time 240 \
       "https://github.com/martaxi-boss/skill-universal/archive/$SHA.tar.gz" \
       -o "$WORK/release.tar.gz"
  "$PRIVATE_PYTHON" - "$WORK/release.tar.gz" <<'VERIFY_ARCHIVE'
from pathlib import PurePosixPath
import sys, tarfile
with tarfile.open(sys.argv[1], 'r:gz') as archive:
    entries=archive.getmembers()
    assert entries and len(entries)<5000, "FERRARI_ARCHIVE_ENTRIES_INVALID"
    parents=set()
    total=0
    for member in entries:
        p=PurePosixPath(member.name)
        assert not p.is_absolute() and '..' not in p.parts and len(p.parts)>=1
        parents.add(p.parts[0])
        assert member.isfile() or member.isdir(), "FERRARI_ARCHIVE_LINK_FORBIDDEN"
        total+=member.size
    assert len(parents)==1 and total<200_000_000,"FERRARI_ARCHIVE_LAYOUT_OR_SIZE_INVALID"
    print("FERRARI_RELEASE_ARCHIVE_VALID=PASS")
VERIFY_ARCHIVE
  tar --no-same-owner --no-same-permissions --strip-components=1 \
      -xzf "$WORK/release.tar.gz" -C "$STAGED"
  [[ -f "$STAGED/engine/ferrari.py" && -f "$STAGED/engine/skill_job.py"
     && -f "$STAGED/engine/catalog.json" ]] || {
    echo FERRARI_RELEASE_SOURCE_INVALID >&2; exit 5;
  }
  RELEASE="$STAGED"
fi

cd "$RELEASE"
"$PRIVATE_PYTHON" -m unittest discover -s tests -p 'test_*.py' -q
echo FERRARI_RELEASE_REGRESSION_TESTS=PASS
"$PRIVATE_PYTHON" - "$ROOT" "$WORK" <<'VERIFY_REAL'
import base64
import json
import os
from pathlib import Path
import sys
import zipfile
from engine import cad_tools, ferrari, skill_job, tool_runtime

root=Path(sys.argv[1])
work=Path(sys.argv[2])
expected=root.resolve()
for name in ("blender","openscad","libreoffice"):
    path=Path(cad_tools._binary(name)).resolve(strict=True)
    assert path.is_relative_to(expected),name
    print("FERRARI_PRIVATE_CAD_EXECUTOR="+name+"="+str(path))
for name in ("strings","pdftotext","convert","ffmpeg","jadx"):
    path=Path(ferrari._exe(name)).resolve(strict=True)
    assert path.is_relative_to(expected),name
specs=tool_runtime.specs()
assert len(specs)==40, "FERRARI_REGISTERED_ACTION_COUNT_CHANGED"
missing=[]
external=[]
for item in specs.values():
    exe=tool_runtime.executable(item["tool"],item["binary"])
    if not exe:
        missing.append(item["id"])
    elif not Path(exe).resolve(strict=True).is_relative_to(expected):
        external.append(item["id"])
assert not missing and not external, "PRIVATE_ACTION_FAILURE missing="+repr(missing)+" external="+repr(external)
print("FERRARI_PRIVATE_ACTIONS=40/40_PASS")

scad=work/"demo.scad"
scad.write_text("cube([6,4,2]);\n")
cad=ferrari.run("cad-stl",str(work/"cad"),source=str(scad))
assert cad["confirmed"] and cad["executor"].startswith(str(root)+"/")
blend=ferrari.run("blender-house",str(work/"blender"),title="Ferrari privado")
assert blend["confirmed"] and blend["executor"].startswith(str(root)+"/")
for filename,magic in (("house.blend",b"BLENDER"),("house.glb",b"glTF"),("house.png",b"\x89PNG\r\n\x1a\n")):
    with (work/"blender"/filename).open("rb") as stream:
        assert stream.read(len(magic))==magic,filename
print("FERRARI_CAD_3D_RELEASE_SMOKE=PASS")

input_file=work/"demo.docx"
content_types='''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
rels='''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
doc='''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body><w:p><w:r><w:t>Ferrari release privada</w:t></w:r></w:p></w:body></w:document>'''
with zipfile.ZipFile(input_file,"w",compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr("[Content_Types].xml",content_types)
    z.writestr("_rels/.rels",rels)
    z.writestr("word/document.xml",doc)
office=ferrari.run("office-pdf",str(work/"office"),source=str(input_file))
assert office["confirmed"] and office["executor"].startswith(str(root)+"/")
assert (work/"office"/"demo.pdf").read_bytes().startswith(b"%PDF-")
print("FERRARI_OFFICE_RELEASE_SMOKE=PASS")

job={"version":1,"id":"ferrari-private-release-smoke","kind":"operation",
     "operation":"office-pdf",
     "input":{"name":"demo.docx","content_base64":base64.b64encode(input_file.read_bytes()).decode("ascii")}}
report,code=skill_job.execute(job,work/"skill-smoke")
assert code==0 and report["status"]=="completed" and report["artifacts"],repr(report)
with zipfile.ZipFile(work/"skill-smoke"/"response.zip") as z:
    assert "report.json" in z.namelist()
    pdfs=[p for p in z.namelist() if p.endswith(".pdf")]
    assert pdfs and z.read(pdfs[0]).startswith(b"%PDF-")
print("FERRARI_PRIVATE_SKILL_JOB_RESPONSE_ZIP=PASS")
VERIFY_REAL
echo FERRARI_RELEASE_PRIVATE_PREACTIVATION=PASS

# Never switch 'current' until the three new specialist adapters have
# actually produced output on this VPS, not merely returned --version.
# This is bounded to the dedicated Ferrari release that introduces them.
if "$PRIVATE_PYTHON" - <<'ADAPTERS_RELEASE_CHECK'
from engine import ferrari
required = {"librecad-dxf-pdf", "qgis-buffer-5m", "godot-starter"}
assert required <= set(ferrari.OPS)
ADAPTERS_RELEASE_CHECK
then
  "$PRIVATE_PYTHON" - "$WORK" <<'ADAPTERS_REAL_PREACTIVATION'
import json
from pathlib import Path
import runpy
import sys

from engine import ferrari

work = Path(sys.argv[1])
drawing = runpy.run_path("install/vps-f9-librecad-dxf2pdf-certify.py")["DRAWING"]
dxf = work / "specialist-test.dxf"
dxf.write_bytes(drawing.replace("\n", "\r\n").encode("ascii"))
result = ferrari.run("librecad-dxf-pdf", str(work / "specialist-librecad"),
                     source=str(dxf))
assert result["confirmed"] and len(result["artifacts"]) == 2
pdf = work / "specialist-librecad" / "librecad-drawing.pdf"
meta = json.loads((work / "specialist-librecad" / "librecad-report.json").read_text())
assert pdf.read_bytes().startswith(b"%PDF-") and meta["private_pdfinfo_verified"]
print("FERRARI_PRIVATE_LIBRECAD_REAL=PASS")

geo = work / "specialist-test.geojson"
geo.write_text(json.dumps({
    "type":"FeatureCollection",
    "crs":{"type":"name","properties":{"name":"EPSG:3857"}},
    "features":[{"type":"Feature","properties":{},
        "geometry":{"type":"Polygon","coordinates":[[
            [0,0],[100,0],[100,50],[0,50],[0,0]]]}}]}),
    encoding="utf-8")
result = ferrari.run("qgis-buffer-5m", str(work / "specialist-qgis"),
                     source=str(geo))
assert result["confirmed"] and len(result["artifacts"]) == 2
shape = json.loads((work / "specialist-qgis" / "qgis-buffer-5m.geojson").read_text())
meta = json.loads((work / "specialist-qgis" / "qgis-buffer-report.json").read_text())
assert len(shape["features"]) == 1
assert meta["area_after_m2"] > meta["area_before_m2"] == 5000
print("FERRARI_PRIVATE_QGIS_REAL=PASS")

result = ferrari.run("godot-starter", str(work / "specialist-godot"))
assert result["confirmed"] and len(result["artifacts"]) == 3
meta = json.loads((work / "specialist-godot" / "godot-starter-report.json").read_text())
assert meta["engine_exit_code"] == 0
assert (work / "specialist-godot" / "godot-starter/main.tscn").is_file()
print("FERRARI_PRIVATE_GODOT_REAL=PASS")
print("FERRARI_PRIVATE_SPECIALIST_SMOKE=PASS")
ADAPTERS_REAL_PREACTIVATION
fi

if [[ "$MODE" == "--check" ]]; then
  echo FERRARI_RELEASE_NOT_ACTIVATED_CHECK_ONLY
  exit 0
fi

if [[ "$RELEASE" == "$STAGED" && -n "$STAGED" ]]; then
  [[ ! -e "$ROOT/releases/$SHA" && ! -L "$ROOT/releases/$SHA" ]] || {
    echo FERRARI_RELEASE_RACE_DETECTED >&2; exit 8;
  }
  mv -T -- "$STAGED" "$ROOT/releases/$SHA"
  STAGED=""
  RELEASE="$ROOT/releases/$SHA"
fi
NEXT="$ROOT/.current.next.$$"
[[ ! -e "$NEXT" && ! -L "$NEXT" ]] || { echo FERRARI_CURRENT_NEXT_CONFLICT >&2; exit 9; }
ln -s "$RELEASE" "$NEXT"
mv -Tf "$NEXT" "$ROOT/current"
SWITCHED=1
cd "$ROOT/current"
"$PRIVATE_PYTHON" - "$SHA" "$ROOT" <<'VERIFY_ACTIVE'
from pathlib import Path
import sys
from engine import ferrari, tool_runtime, cad_tools
sha,root=sys.argv[1],Path(sys.argv[2])
assert (root/"current").resolve(strict=True)==root/"releases"/sha
assert len(tool_runtime.specs())==40
assert all(tool_runtime.executable(a["tool"],a["binary"])
           for a in tool_runtime.specs().values())
for name in ("blender","openscad","libreoffice"):
    assert Path(cad_tools._binary(name)).resolve().is_relative_to(root.resolve())
print("FERRARI_PRIVATE_ACTIVE_RELEASE=PASS "+sha)
VERIFY_ACTIVE
PASSED=1
echo FERRARI_RELEASE_SWITCH=PASS
echo "FERRARI_PREVIOUS_RELEASE_PRESERVED=$PREVIOUS"
echo "FERRARI_PRIVATE_RELEASE_ACTIVE=$SHA"
# Hygiene is intentionally confined to the script's own transient work.
# Existing releases, system packages and other project services are untouched.
