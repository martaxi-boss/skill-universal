#!/usr/bin/env bash
# Extra tools only: OpenSCAD + Blender headless Ubuntu 24.04, no SSH bridge logic.
set -Eeuo pipefail
source /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || { echo 'FERRARI_CAD_OS_UNSUPPORTED'; exit 2; }
[[ "$(uname -m)" == x86_64 ]] || { echo 'FERRARI_CAD_ARCH_UNSUPPORTED'; exit 2; }
cd "$(dirname "$0")/.."
for pkg in blender openscad; do
  candidate="$(apt-cache policy "$pkg" 2>/dev/null | awk '/Candidate:/ && !found {print $2; found=1}')"
  if [[ -z "$candidate" || "$candidate" == "(none)" ]]; then
    echo "FERRARI_CAD_APT_CANDIDATE_MISSING=$pkg" >&2; exit 3
  fi
  echo "FERRARI_CAD_APT_CANDIDATE=$pkg:$candidate"
done
free="$(df -Pk "$HOME" | awk 'END{print $4}')"
if (( free < 8388608 )); then
  echo "FERRARI_CAD_INSUFFICIENT_DISK free_KiB=$free" >&2
  exit 4
fi
if ! command -v blender >/dev/null 2>&1 || ! command -v openscad >/dev/null 2>&1; then
  sudo -n apt-get -s install --no-install-recommends blender openscad >/dev/null
  sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends blender openscad
fi
command -v blender
command -v openscad
blender --background --factory-startup --version | sed -n '1p'
QT_QPA_PLATFORM=offscreen openscad --version
OUT="$HOME/.local/share/motor-ferrari/current/smoke/cad-3d"
mkdir -p "$OUT"
cat > "$OUT/ferrari-sample.scad" <<'SCAD'
difference() {
  cube([60,40,35],center=true);
  translate([0,-19,0]) cube([12,6,20],center=true);
}
SCAD
python3 -m engine.ferrari run --operation cad-stl --input "$OUT/ferrari-sample.scad" --output "$OUT/cad"
python3 -m engine.ferrari run --operation blender-house --title 'Casa conceptual Ferrari' --output "$OUT/blender"
test -s "$OUT/cad/solid.stl"
test -s "$OUT/blender/house.blend"
test -s "$OUT/blender/house.glb"
test -s "$OUT/blender/house.png"
echo 'FERRARI_CAD_STL_FUNCTIONAL=PASS'
echo 'FERRARI_BLENDER_HOUSE_3D_FUNCTIONAL=PASS'
echo 'FERRARI_CAD_3D_PROGRAMS_INSTALLED=YES'
