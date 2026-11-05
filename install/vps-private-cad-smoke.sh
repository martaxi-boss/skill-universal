#!/usr/bin/env bash
# Real, private-only Ferrari OpenSCAD+Blender certification. No global writes,
# APT changes, service actions, external-project access or release switching.
set -Eeuo pipefail
umask 077
ROOT="/srv/projects/skill-universal"
[[ "$(id -u)" != 0 ]] || { echo 'FERRARI_SMOKE_ROOT_USER_FORBIDDEN' >&2; exit 2; }
[[ -d "$ROOT" && ! -L "$ROOT" && -d "$ROOT/.runtime" && ! -L "$ROOT/.runtime" ]] || {
  echo 'FERRARI_SMOKE_ROOT_INVALID' >&2; exit 2;
}
ACTIVE="$(realpath -e "$ROOT/current")"
[[ "$ACTIVE" == "$ROOT"/releases/* && -f "$ACTIVE/engine/blender_house.py" ]] || {
  echo 'FERRARI_SMOKE_RELEASE_INVALID' >&2; exit 2;
}
BLENDER="$ROOT/tools/blender/blender"
SCAD="$ROOT/tools/openscad/bin/openscad"
for exe in "$BLENDER" "$SCAD"; do
  [[ -x "$exe" && ! -L "$exe" ]] || { echo "FERRARI_PRIVATE_EXECUTOR_MISSING=${exe##*/}" >&2; exit 3; }
  resolved="$(realpath -e "$exe")"
  [[ "$resolved" == "$ROOT"/tools/* ]] || { echo "FERRARI_EXECUTOR_ESCAPES_PROJECT=${exe##*/}" >&2; exit 3; }
done
WORK="$(mktemp -d "$ROOT/.runtime/private-cad-smoke-XXXXXXXX")"
cleanup() {
  if [[ "$WORK" == "$ROOT"/.runtime/private-cad-smoke-* && -d "$WORK" && ! -L "$WORK" ]]; then
    rm -rf -- "$WORK"
  fi
}
trap cleanup EXIT
mkdir -p "$WORK/home" "$WORK/tmp" "$WORK/config" "$WORK/cache" "$WORK/data" "$WORK/run"
chmod 700 "$WORK/run"
export HOME="$WORK/home"
export TMPDIR="$WORK/tmp"
export XDG_CONFIG_HOME="$WORK/config"
export XDG_CACHE_HOME="$WORK/cache"
export XDG_DATA_HOME="$WORK/data"
export XDG_RUNTIME_DIR="$WORK/run"
export QT_QPA_PLATFORM=offscreen
export LIBGL_ALWAYS_SOFTWARE=1
export OMP_NUM_THREADS=2
printf 'cube([6,4,2]);\n' > "$WORK/private-test.scad"
timeout 180 "$SCAD" -o "$WORK/solid.stl" "$WORK/private-test.scad"
test -s "$WORK/solid.stl"
echo 'FERRARI_PRIVATE_OPENSCAD_STL=PASS'
timeout 600 "$BLENDER" --background --factory-startup --python-exit-code 5 \
  --python "$ACTIVE/engine/blender_house.py" -- "$WORK" "Ferrari privado"
for name in house.blend house.glb house.png; do
  test -s "$WORK/$name" || { echo "FERRARI_BLENDER_ARTIFACT_MISSING=$name" >&2; exit 4; }
done
PY="$ROOT/runtimes/python3.12/bin/python3.12"
[[ -x "$PY" ]] || { echo 'FERRARI_PRIVATE_PYTHON_MISSING' >&2; exit 4; }
"$PY" - "$WORK" <<'VERIFY'
from pathlib import Path
import sys
root=Path(sys.argv[1])
expected={"house.blend":b"BLENDER", "house.glb":b"glTF", "house.png":b"\x89PNG\r\n\x1a\n"}
for name,magic in expected.items():
    p=root/name
    assert p.is_file() and not p.is_symlink() and p.stat().st_size>=200,name
    with p.open("rb") as handle:
        assert handle.read(len(magic))==magic,name
    print("FERRARI_PRIVATE_ARTIFACT="+name+" SIZE="+str(p.stat().st_size))
stl=root/"solid.stl"
assert stl.is_file() and not stl.is_symlink() and stl.stat().st_size>=84
print("FERRARI_PRIVATE_ARTIFACT=solid.stl SIZE="+str(stl.stat().st_size))
VERIFY
echo 'FERRARI_PRIVATE_BLENDER_3D_FILES=PASS'
echo 'FERRARI_PRIVATE_CAD_REAL_SMOKE=PASS'
echo 'FERRARI_SMOKE_ONLY_PRIVATE_RUNTIME=PASS'
# All generated smoke data and the temporary GUI state are removed by trap.
