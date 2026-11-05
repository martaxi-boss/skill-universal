#!/usr/bin/env bash
# CAD/3D private-only Ferrari smoke; does not install Ubuntu packages.
set -Eeuo pipefail
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || exit 2
[[ "$(uname -m)" == x86_64 ]] || exit 2
ROOT="/srv/projects/skill-universal"
cd "$ROOT/current"
PY="$ROOT/runtimes/python3.12/bin/python3.12"
PANDOC="$ROOT/tools/ubuntu-cli/bin/pandoc"
test -x "$PY" && test -x "$PANDOC" || { echo FERRARI_PRIVATE_RUNTIME_MISSING; exit 3; }
"$PY" - <<'PYCODE'
from engine.cad_tools import _binary
for name in ("blender", "openscad", "libreoffice"):
    print("FERRARI_PRIVATE_CAD_EXECUTOR=" + _binary(name))
PYCODE
OUT="$ROOT/.runtime/smoke/cad-3d"
mkdir -p "$OUT"
test ! -e "$OUT/ferrari-sample.scad" || { echo FERRARI_SMOKE_ALREADY_EXISTS; exit 4; }
cat > "$OUT/ferrari-sample.scad" <<'SCAD'
difference() {
  cube([60,40,35],center=true);
  translate([0,-19,0]) cube([12,6,20],center=true);
}
SCAD
"$PY" -m engine.ferrari run --operation cad-stl --input "$OUT/ferrari-sample.scad" --output "$OUT/cad"
"$PY" -m engine.ferrari run --operation blender-house --title 'Casa conceptual Ferrari' --output "$OUT/blender"
printf '# Ferrari document smoke\n\nUbuntu private office export test.\n' > "$OUT/document.md"
"$PANDOC" "$OUT/document.md" -o "$OUT/document.docx"
"$PY" -m engine.ferrari run --operation office-pdf --input "$OUT/document.docx" --output "$OUT/office"
test -s "$OUT/office/document.pdf"
test -s "$OUT/cad/solid.stl"
test -s "$OUT/blender/house.blend"
test -s "$OUT/blender/house.glb"
test -s "$OUT/blender/house.png"
echo FERRARI_PRIVATE_CAD_3D_OFFICE=PASS
