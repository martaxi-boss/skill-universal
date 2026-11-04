#!/usr/bin/env bash
# Ferrari Phase B: external Ubuntu-compatible tools with own Node/Python roots.
# Keep all dependencies inside Ferrari; do not install into legacy REA projects.
set -Eeuo pipefail
umask 077
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04 && test "$(uname -m)" = x86_64
test "$(id -u)" -ne 0
ROOT="/srv/projects/skill-universal"
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
for tool in duckdb polars streamlit gradio faster-whisper prefect docling; do
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
  # Docling's PyTorch is forced to the CPU wheel distribution: there is no
  # NVIDIA GPU, and default CUDA packages would waste VPS storage.
  if [[ "$tool" == docling ]]; then
    if ! "$dir/bin/python" -c 'import torch; assert "+cpu" in torch.__version__' >/dev/null 2>&1; then
      if ! "$dir/bin/python" -m pip install --only-binary=:all: --no-cache-dir \
         --disable-pip-version-check --no-input --timeout 60 --retries 1 \
         --index-url https://download.pytorch.org/whl/cpu torch > "$OUT/docling-cpu-torch.log" 2>&1; then
        record "$tool" PENDING_CPU_TORCH
        continue
      fi
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

# Install exact verified official Ubuntu-compatible Linux x86_64 releases,
# not a different Python "typst" package or the obsolete Godot 3 APT.
# SHA-256 values are from each upstream GitHub release asset.
install_binary() {
  local id="$1" version="$2" url="$3" expected="$4" suffix="$5" verify="$6"
  local dest="$ROOT/tools/$id-$version"
  local file="$dest/archive.$suffix"
  if ! enough_disk; then record "$id" PENDING_DISK; return; fi
  mkdir -p "$dest"
  if [[ ! -s "$file" ]]; then
    if ! curl --fail --location --retry 3 --retry-delay 3 --max-time 1500 \
           --silent --show-error "$url" -o "$file.part" > "$OUT/$id-fetch.log" 2>&1; then
      rm -f "$file.part"
      record "$id" DOWNLOAD_FAILED
      return
    fi
    mv "$file.part" "$file"
  fi
  if ! printf '%s  %s\n' "$expected" "$file" | sha256sum -c - > "$OUT/$id-sha256.log" 2>&1; then
    rm -f "$file"
    record "$id" CHECKSUM_FAILED
    return
  fi
  if [[ "$id" == typst ]]; then
    mkdir -p "$dest/extracted"
    if ! tar -xf "$file" -C "$dest/extracted" > "$OUT/$id-extract.log" 2>&1; then
      record "$id" EXTRACT_FAILED; return
    fi
    exe="$(find "$dest/extracted" -type f -name typst -print -quit)"
    if [[ -n "$exe" ]]; then
      chmod 750 "$exe"
      if "$exe" --version > "$OUT/$id-version.txt" 2>&1; then
        record "$id" INSTALLED_FERRARI_BINARY "$("$exe" --version)"
        return
      fi
    fi
    record "$id" BINARY_NOT_FUNCTIONAL
  elif [[ "$id" == godot ]]; then
    mkdir -p "$dest/extracted"
    if ! unzip -oq "$file" -d "$dest/extracted" > "$OUT/$id-extract.log" 2>&1; then
      record "$id" EXTRACT_FAILED; return
    fi
    exe="$(find "$dest/extracted" -type f -name 'Godot_v*-linux.x86_64' -print -quit)"
    if [[ -z "$exe" ]]; then exe="$(find "$dest/extracted" -type f -name 'Godot_v*linux.x86_64' -print -quit)"; fi
    if [[ -n "$exe" ]]; then
      chmod 750 "$exe"
      if timeout 45 "$exe" --headless --version > "$OUT/$id-version.txt" 2>&1; then
        record "$id" INSTALLED_FERRARI_BINARY "$(head -n 1 "$OUT/$id-version.txt")"
        return
      fi
    fi
    record "$id" BINARY_NOT_FUNCTIONAL
  else
    # FreeCAD's official AppImage can exist on a headless machine with no
    # FUSE/display. A verified AppImage is installed, GUI execution untested.
    chmod 750 "$file"
    record "$id" INSTALLED_VERIFIED_APPIMAGE "$version;GUI_UNTESTED"
  fi
}
install_binary typst 0.15.1 \
  "https://github.com/typst/typst/releases/download/v0.15.1/typst-x86_64-unknown-linux-musl.tar.xz" \
  "a6d077d0a95eed5a2eba715b2dae06be954f624ccbf85758a03f389ded33118c" tar.xz typst
install_binary godot 4.7.2 \
  "https://github.com/godotengine/godot/releases/download/4.7.2-stable/Godot_v4.7.2-stable_linux.x86_64.zip" \
  "cadd3204e728a35d3f13adb7fd0d7902636b79f6b95c40c265eb73b6c35329e4" zip godot
install_binary freecad 1.1.4 \
  "https://github.com/FreeCAD/FreeCAD/releases/download/1.1.4/FreeCAD_1.1.4-Linux-x86_64-py311.AppImage" \
  "f6dc6ba676e5ac96a565ebc8d657232f94c6158e85b4352141bd1a46f6b43434" AppImage freecad

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
