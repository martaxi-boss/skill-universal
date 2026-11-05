#!/usr/bin/env bash
# Ferrari-owned, vendor-verified Linux CAD binaries. No APT, sudo, Snap or global writes.
# This script NEVER switches current, removes other programs or edits another project.
set -Eeuo pipefail
umask 077
ROOT="/srv/projects/skill-universal"
VERSION_BLENDER="4.5.15"
VERSION_SCAD="2021.01"
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 && "$(uname -m)" == x86_64 ]] || {
  echo 'FERRARI_PRIVATE_CAD_UNSUPPORTED_OS'; exit 2;
}
[[ -d "$ROOT" && ! -L "$ROOT" && -d "$ROOT/tools" && ! -L "$ROOT/tools" ]] || {
  echo 'FERRARI_PRIVATE_CAD_ROOT_INVALID'; exit 2;
}
[[ "$(id -u)" -ne 0 && "$(stat -c %u "$ROOT")" == "$(id -u)" ]] || {
  echo 'FERRARI_PRIVATE_CAD_OWNER_MISMATCH'; exit 2;
}
[[ -d "$ROOT/.runtime" && ! -L "$ROOT/.runtime" ]] || {
  echo 'FERRARI_PRIVATE_CAD_RUNTIME_INVALID'; exit 2;
}
command -v curl >/dev/null
command -v sha256sum >/dev/null
command -v tar >/dev/null
[[ "$(df -Pk "$ROOT" | awk 'END {print $4}')" -ge 4194304 ]] || {
  echo 'FERRARI_PRIVATE_CAD_DISK_BELOW_4GIB'; exit 3;
}
WORK="$(mktemp -d "$ROOT/.runtime/.private-cad-20261105.XXXXXXXX")"
cleanup() {
  case "$WORK" in "$ROOT/.runtime/.private-cad-20261105."*) rm -rf -- "$WORK" ;; esac
}
trap cleanup EXIT
download_verified() {
  local url="$1" filename="$2" sum_url="$3" destination="$4" sumfile="$WORK/checksums.txt"
  [[ "$url" == https://* && "$sum_url" == https://* ]] || exit 4
  curl --fail --silent --show-error --location --retry 2 --connect-timeout 15 --max-time 120 "$sum_url" -o "$sumfile"
  local hash
  hash="$(grep -F "$filename" "$sumfile" | grep -Eo '[A-Fa-f0-9]{64}' | head -n 1 || :)"
  [[ "$hash" =~ ^[A-Fa-f0-9]{64}$ ]] || {
    echo 'FERRARI_PRIVATE_CAD_CHECKSUM_MISSING'; exit 5;
  }
  curl --fail --silent --show-error --location --retry 2 --connect-timeout 20 --max-time 1200 "$url" -o "$destination"
  printf '%s  %s\n' "$hash" "$destination" | sha256sum -c - >/dev/null
  echo "FERRARI_PRIVATE_SOURCE_SHA256_PASS=$filename"
}
scad="$ROOT/tools/openscad"
if [[ -e "$scad" || -L "$scad" ]]; then
  test -x "$scad/bin/openscad" && test ! -L "$scad" || { echo 'FERRARI_OPENSCAD_EXISTING_CONFLICT'; exit 6; }
  echo 'FERRARI_PRIVATE_OPENSCAD_EXISTING=YES'
else
  file="OpenSCAD-$VERSION_SCAD-x86_64.AppImage"
  mkdir -p "$WORK/openscad/bin"
  download_verified "https://files.openscad.org/$file" "$file" \
    "https://files.openscad.org/$file.sha256" "$WORK/openscad/$file"
  chmod 700 "$WORK/openscad/$file"
  (cd "$WORK/openscad" && "./$file" --appimage-extract > /dev/null)
  test -x "$WORK/openscad/squashfs-root/AppRun" || { echo 'FERRARI_OPENSCAD_APPIMAGE_EXTRACT_FAILED'; exit 7; }
  cat > "$WORK/openscad/bin/openscad" <<'WRAPPER'
#!/usr/bin/env bash
set -Eeuo pipefail
SELF="$(cd "$(dirname "$0")" && pwd -P)"
export QT_QPA_PLATFORM="${QT_QPA_PLATFORM:-offscreen}"
exec "$SELF/../squashfs-root/AppRun" "$@"
WRAPPER
  chmod 700 "$WORK/openscad/bin/openscad"
  test "$(realpath "$WORK/openscad/squashfs-root/AppRun" | cut -c1-${#WORK})" = "$WORK" || {
    echo 'FERRARI_OPENSCAD_EXTERNAL_APPRUN'; exit 7;
  }
  QT_QPA_PLATFORM=offscreen "$WORK/openscad/bin/openscad" --version
  printf 'cube([3,5,7]);\n' > "$WORK/demo.scad"
  QT_QPA_PLATFORM=offscreen timeout 150 "$WORK/openscad/bin/openscad" \
    -o "$WORK/solid.stl" "$WORK/demo.scad"
  test -s "$WORK/solid.stl" || { echo 'FERRARI_OPENSCAD_STL_SMOKE_FAIL'; exit 7; }
  mv -- "$WORK/openscad" "$scad"
  echo 'FERRARI_PRIVATE_OPENSCAD_INSTALLED=YES'
fi
blender="$ROOT/tools/blender"
if [[ -e "$blender" || -L "$blender" ]]; then
  test -x "$blender/blender" && test ! -L "$blender" || { echo 'FERRARI_BLENDER_EXISTING_CONFLICT'; exit 6; }
  echo 'FERRARI_PRIVATE_BLENDER_EXISTING=YES'
else
  file="blender-$VERSION_BLENDER-linux-x64.tar.xz"
  download_verified "https://download.blender.org/release/Blender4.5/$file" "$file" \
    "https://download.blender.org/release/Blender4.5/blender-$VERSION_BLENDER.sha256" "$WORK/$file"
  mkdir -p "$WORK/blender"
  tar --no-same-owner --no-same-permissions -xJf "$WORK/$file" -C "$WORK/blender" --strip-components=1
  test -x "$WORK/blender/blender" || { echo 'FERRARI_BLENDER_ARCHIVE_LAYOUT_FAIL'; exit 8; }
  # A verified vendor archive must not point symlinks outside its own extracted tree.
  python3 - "$WORK/blender" <<'PYCHECK'
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve(strict=True)
for path in root.rglob("*"):
    if path.is_symlink() and not path.resolve(strict=False).is_relative_to(root):
        raise RuntimeError("Vendor Blender archive has external symlink")
PYCHECK
  LIBGL_ALWAYS_SOFTWARE=1 timeout 75 "$WORK/blender/blender" --background --factory-startup --version
  mv -- "$WORK/blender" "$blender"
  echo 'FERRARI_PRIVATE_BLENDER_INSTALLED=YES'
fi
QT_QPA_PLATFORM=offscreen "$scad/bin/openscad" --version
LIBGL_ALWAYS_SOFTWARE=1 timeout 80 "$blender/blender" --background --factory-startup --version
echo 'FERRARI_PRIVATE_CAD_INSTALL=PASS'
