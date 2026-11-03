#!/usr/bin/env bash
# Ferrari Phase A: 15 missing GUI programs and two private service executables.
# Services are never enabled or started. The old REA project is untouched.
set -Eeuo pipefail
umask 077
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04 && test "$(uname -m)" = x86_64
test "$(id -u)" -ne 0
cd "$(dirname "$0")/.."
ROOT="$HOME/.local/share/motor-ferrari"
REPORT="$ROOT/.runtime/expansion-33"
mkdir -p "$REPORT" "$ROOT/tools"
TSV="$REPORT/services-gui.tsv"
printf 'group\tid\tstatus\tdetail\n' > "$TSV"
GUI=(gimp krita kdenlive scribus darktable librecad qgis audacity obs-studio
     lmms solvespace synfigstudio openshot-qt calibre inkscape)
SERVICES=(prometheus valkey-server)
candidate() {
  apt-cache policy "$1" 2>/dev/null | awk '$1=="Candidate:" {v=$2} END {print v}'
}
record() {
  printf '%s\t%s\t%s\t%s\n' "$1" "$2" "$3" "${4:-}" >> "$TSV"
  printf 'FERRARI_EXPANSION_%s_%s=%s\n' "$1" "${2//-/_}" "$3"
}
available=()
for pkg in "${GUI[@]}"; do
  ver="$(candidate "$pkg")"
  if [[ "$ver" == "(none)" || -z "$ver" ]]; then
    record gui "$pkg" NO_APT_CANDIDATE
  else
    available+=("$pkg")
  fi
done
if (("${#available[@]}")); then
  # Install official Ubuntu APT packages with explicit ownership in the
  # package manager; none is taken from the other REA's private directories.
  test "$(df -Pk "$HOME" | awk 'END{print $4}')" -ge 8388608 || {
    echo 'FERRARI_EXPANSION_GUI_INSUFFICIENT_DISK_8GIB' >&2; exit 3;
  }
  sudo -n true
  sudo -n apt-get -s install --no-install-recommends "${available[@]}" > "$REPORT/gui-apt-simulation.log"
  if sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends "${available[@]}" > "$REPORT/gui-install.log" 2>&1; then
    :
  else
    echo 'FERRARI_EXPANSION_GUI_APT_FAILED' >&2
    tail -n 35 "$REPORT/gui-install.log" >&2
  fi
  for pkg in "${available[@]}"; do
    if [[ "$(dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null)" == "install ok installed" ]]; then
      record gui "$pkg" INSTALLED_APT "$(dpkg-query -W -f='${Version}' "$pkg" 2>/dev/null)"
    else
      record gui "$pkg" INSTALL_FAILED
    fi
  done
fi
# Download signed Ubuntu binary packages into Ferrari's own tree, without
# activating Prometheus or Valkey services and without touching system ports.
for pkg in "${SERVICES[@]}"; do
  ver="$(candidate "$pkg")"
  if [[ -z "$ver" || "$ver" == "(none)" ]]; then
    record service "$pkg" NO_APT_CANDIDATE
    continue
  fi
  out="$ROOT/tools/ferrari-services/$pkg"
  if [[ ! -d "$out/usr" ]]; then
    work="$(mktemp -d "$REPORT/.service-$pkg.XXXXXXXX")"
    if (cd "$work" && apt-get download "$pkg" > download.log 2>&1); then
      deb="$(find "$work" -maxdepth 1 -name '*.deb' -type f -print -quit)"
      if [[ -n "$deb" ]]; then
        mkdir -p "$work/unpacked"
        dpkg-deb -x "$deb" "$work/unpacked"
        mkdir -p "$(dirname "$out")"
        if [[ ! -e "$out" ]]; then mv "$work/unpacked" "$out"; fi
      fi
    fi
    rm -rf -- "$work"
  fi
  # Ubuntu 24.04 Valkey server package depends on valkey-tools for its
  # executable; unpack the matching dependency into the same private tree.
  if [[ "$pkg" == valkey-server && ! -f "$out/usr/bin/valkey-server" ]]; then
    work="$(mktemp -d "$REPORT/.valkey-tools.XXXXXXXX")"
    if (cd "$work" && apt-get download valkey-tools > download.log 2>&1); then
      deb="$(find "$work" -maxdepth 1 -name '*.deb' -type f -print -quit)"
      if [[ -n "$deb" ]]; then dpkg-deb -x "$deb" "$out"; fi
    fi
    rm -rf -- "$work"
  fi
  exe="$out/usr/bin/$pkg"
  if [[ ! -f "$exe" ]]; then
    case "$pkg" in
      prometheus) exe="$out/usr/bin/prometheus" ;;
      valkey-server) exe="$out/usr/bin/valkey-server" ;;
    esac
  fi
  if [[ -f "$exe" ]] && timeout 15 "$exe" --version > "$REPORT/$pkg-version.txt" 2>&1; then
    record service "$pkg" INSTALLED_PRIVATE "$ver"
  elif [[ -f "$exe" ]]; then
    record service "$pkg" EXTRACTED_NOT_FUNCTIONAL "$ver"
  else
    record service "$pkg" DOWNLOAD_OR_LAYOUT_FAILED "$ver"
  fi
done
python3 - "$TSV" "$REPORT/services-gui.json" <<'PY'
import csv,json,sys
from pathlib import Path
rows=list(csv.DictReader(Path(sys.argv[1]).open(),delimiter="\t"))
out={"schema":1,"project":"motor-ferrari","groups":["gui","service"],"items":rows,
     "installed":sum(x["status"] in ("INSTALLED_APT","INSTALLED_PRIVATE") for x in rows),
     "pending":[x for x in rows if x["status"] not in ("INSTALLED_APT","INSTALLED_PRIVATE")],
     "note":"GUI installed without a desktop session; service binaries are never started."}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2,ensure_ascii=False)+"\n")
print("FERRARI_EXPANSION_GUI_SERVICE_INSTALLED="+str(out["installed"]))
print("FERRARI_EXPANSION_GUI_SERVICE_PENDING="+str(len(out["pending"])))
PY
