#!/usr/bin/env bash
# Ferrari Phase B: external Ubuntu-compatible tools with own Node/Python roots.
# Keep all dependencies inside Ferrari; do not install into legacy REA projects.
set -Eeuo pipefail
umask 077
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04 && test "$(uname -m)" = x86_64
test "$(id -u)" -ne 0
ROOT="$HOME/.local/share/motor-ferrari"
OUT="$ROOT/.runtime/expansion-33"
mkdir -p "$OUT" "$ROOT/.runtime/venvs/extended" "$ROOT/.runtime/npm"
TSV="$OUT/external.tsv"
printf 'group\tid\tstatus\tdetail\n' > "$TSV"
record() {
  printf 'external\t%s\t%s\t%s\n' "$1" "$2" "${3:-}" >> "$TSV"
  printf 'FERRARI_EXTERNAL_%s=%s\n' "${1//-/_}" "$2"
}
enough_disk() { test "$(df -Pk "$HOME" | awk 'END{print $4}')" -ge 5242880; }

NODE="$ROOT/runtimes/node-22.23.4/bin/node"
NPM="$ROOT/runtimes/node-22.23.4/bin/npm"
if [[ -x "$NODE" && -x "$NPM" ]]; then
  export PATH="$(dirname "$NODE"):$PATH"
  export NPM_CONFIG_CACHE="$ROOT/.runtime/npm-cache"
  export NPM_CONFIG_UPDATE_NOTIFIER=false NPM_CONFIG_FUND=false
  for tool in nextjs tailwind bootstrap shadcn; do
    case "$tool" in
      nextjs) packages=(next) ; testpkg=next ;;
      tailwind) packages=(tailwindcss @tailwindcss/cli); testpkg=tailwindcss ;;
      bootstrap) packages=(bootstrap); testpkg=bootstrap ;;
      shadcn) packages=(shadcn); testpkg=shadcn ;;
    esac
    root="$ROOT/.runtime/npm/$tool"
    mkdir -p "$root"
    if ! enough_disk; then record "$tool" PENDING_DISK; continue; fi
    if "$NPM" install --prefix "$root" --no-save --ignore-scripts --no-audit --no-fund \
          --no-progress --loglevel=error "${packages[@]}" > "$OUT/$tool-install.log" 2>&1 &&
       test -f "$root/node_modules/$testpkg/package.json"; then
      ver="$("$NODE" -p "require('$root/node_modules/$testpkg/package.json').version" 2>/dev/null)"
      record "$tool" INSTALLED_FERRARI_NPM "$ver"
    else
      record "$tool" FAILED_NPM
    fi
  done
else
  for x in nextjs tailwind bootstrap shadcn; do record "$x" PENDING_OWN_NODE; done
fi

# A separate Python environment per package means installing Docling/Prefect
# does not alter Streamlit, Gradio, other users or the legacy REA.
for tool in duckdb polars streamlit gradio typst faster-whisper prefect docling; do
  case "$tool" in
    faster-whisper) package=faster-whisper; module=faster_whisper ;;
    *) package="$tool"; module="$tool" ;;
  esac
  dir="$ROOT/.runtime/venvs/extended/$tool"
  if ! enough_disk; then record "$tool" PENDING_DISK; continue; fi
  if [[ ! -x "$dir/bin/python" ]]; then
    if ! python3 -m venv "$dir" > "$OUT/$tool-venv.log" 2>&1; then
      record "$tool" FAILED_VENV; continue
    fi
  fi
  if "$dir/bin/python" -m pip install --only-binary=:all: --no-cache-dir \
       --disable-pip-version-check --no-input --prefer-binary \
       --timeout 45 --retries 1 "$package" > "$OUT/$tool-install.log" 2>&1 &&
     "$dir/bin/python" -c "import importlib.metadata as m; import $module; print(m.version('$package'))" \
        > "$OUT/$tool-version.txt" 2>&1; then
    record "$tool" INSTALLED_FERRARI_VENV "$(tail -n 1 "$OUT/$tool-version.txt")"
  else
    record "$tool" FAILED_PYTHON_INSTALL
  fi
done

# FreeCAD and Godot are GUI programs. Install official Ubuntu candidates if
# available; record installed package state, not a made-up headless GUI test.
for tool in freecad godot; do
  if [[ "$tool" == freecad ]]; then pkg=freecad; else pkg=godot3; fi
  candidate="$(apt-cache policy "$pkg" 2>/dev/null | awk '$1=="Candidate:" {v=$2} END{print v}')"
  if [[ -z "$candidate" || "$candidate" == "(none)" ]]; then
    record "$tool" PENDING_NO_UBUNTU_APT
  elif ! enough_disk; then
    record "$tool" PENDING_DISK
  else
    if sudo -n apt-get -s install --no-install-recommends "$pkg" >/dev/null 2>&1 &&
       sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends \
           -y "$pkg" > "$OUT/$tool-install.log" 2>&1 &&
       [[ "$(dpkg-query -W -f='${Status}' "$pkg" 2>/dev/null)" == "install ok installed" ]]; then
      record "$tool" INSTALLED_APT "$(dpkg-query -W -f='${Version}' "$pkg")"
    else
      record "$tool" FAILED_APT
    fi
  fi
done

# Two server/heavy upstreams require their own verified packaging and runtime.
# Never treat a source checkout as an installed Penpot service or a GPU
# candidate as a working ComfyUI on this 4-CPU Ubuntu VPS.
record penpot PENDING_CONTAINER_DEPLOYMENT
record comfyui PENDING_CPU_RUNTIME

python3 - "$TSV" "$OUT/external.json" <<'PY'
import csv,json,sys
from pathlib import Path
rows=list(csv.DictReader(Path(sys.argv[1]).open(),delimiter="\t"))
installed=[x for x in rows if x["status"].startswith("INSTALLED_")]
report={"schema":1,"project":"motor-ferrari","group":"external","items":rows,
        "installed":len(installed),
        "pending":[x for x in rows if not x["status"].startswith("INSTALLED_")],
        "note":"Installed packages are Ferrari-owned; GUI/API functionality not implied."}
Path(sys.argv[2]).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("FERRARI_EXTERNAL_INSTALLED="+str(report["installed"]))
print("FERRARI_EXTERNAL_PENDING="+str(len(report["pending"])))
PY
