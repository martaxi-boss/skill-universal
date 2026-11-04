#!/usr/bin/env bash
# Ferrari expansion phase C: ComfyUI CPU and official Penpot Docker images.
# This does not open ports, start processes or modify any legacy REA project.
set -Eeuo pipefail
umask 077
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04 && test "$(uname -m)" = x86_64
test "$(id -u)" -ne 0
ROOT="/srv/projects/skill-universal"
OUT="$ROOT/.runtime/expansion-33"
mkdir -p "$OUT" "$ROOT/tools" "$ROOT/.runtime/venvs/extended"
TSV="$OUT/heavy.tsv"
printf 'id\tstatus\tdetail\n' > "$TSV"
record() {
  printf '%s\t%s\t%s\n' "$1" "$2" "${3:-}" >> "$TSV"
  printf 'FERRARI_HEAVY_%s=%s\n' "$1" "$2"
}
free_kib() { df -Pk "$HOME" | awk 'END {print $4}'; }
COMFY_VERSION=v0.43.0
COMFY_DIR="$ROOT/tools/comfyui-$COMFY_VERSION"
COMFY_PY="$ROOT/.runtime/venvs/extended/comfyui/bin/python"
if (( $(free_kib) < 7340032 )); then
  record comfyui PENDING_DISK_NEED_7GIB
else
  if [[ ! -d "$COMFY_DIR/.git" ]]; then
    if [[ -e "$COMFY_DIR" ]]; then
      record comfyui SOURCE_CONFLICT
    else
      if ! GIT_TERMINAL_PROMPT=0 timeout 420 git clone --depth 1 \
        --branch "$COMFY_VERSION" https://github.com/Comfy-Org/ComfyUI.git \
        "$COMFY_DIR" > "$OUT/comfyui-source.log" 2>&1; then
        record comfyui SOURCE_FETCH_FAILED
      fi
    fi
  fi
  if [[ -d "$COMFY_DIR/.git" ]]; then
    if [[ ! -x "$COMFY_PY" ]]; then
      python3 -m venv "$(dirname "$(dirname "$COMFY_PY")")" \
        > "$OUT/comfyui-venv.log" 2>&1 || true
    fi
    if [[ -x "$COMFY_PY" ]]; then
      if ! "$COMFY_PY" -c 'import torch,torchvision,torchaudio; assert not torch.cuda.is_available()' >/dev/null 2>&1; then
        timeout 850 "$COMFY_PY" -m pip install --only-binary=:all: --no-cache-dir \
          --disable-pip-version-check --no-input --timeout 60 --retries 1 \
          --index-url https://download.pytorch.org/whl/cpu \
          torch torchvision torchaudio > "$OUT/comfyui-torch-cpu.log" 2>&1 || true
      fi
      if "$COMFY_PY" -c 'import torch; assert not torch.cuda.is_available()' >/dev/null 2>&1; then
        if timeout 950 "$COMFY_PY" -m pip install --only-binary=:all: --no-cache-dir \
          --disable-pip-version-check --no-input --timeout 60 --retries 1 \
          -r "$COMFY_DIR/requirements.txt" > "$OUT/comfyui-requirements.log" 2>&1 &&
          (cd "$COMFY_DIR" && CUDA_VISIBLE_DEVICES=-1 timeout 65 "$COMFY_PY" main.py \
            --cpu --help > "$OUT/comfyui-help.log" 2>&1); then
          record comfyui INSTALLED_CPU_NO_MODELS "$COMFY_VERSION;models_not_downloaded"
        else
          record comfyui PENDING_REQUIREMENTS_OR_CLI "$COMFY_VERSION"
        fi
      else
        record comfyui PENDING_CPU_TORCH "$COMFY_VERSION"
      fi
    else
      record comfyui PENDING_VENV "$COMFY_VERSION"
    fi
  fi
fi
# Penpot is a multi-container service. Fetch the official versioned Compose
# definition and, if an already usable Docker engine exists, pull images under
# a dedicated Ferrari project. Never perform "up", expose :9001 or start DBs.
PENPOT_VERSION=2.18.5
PENPOT_DIR="$ROOT/tools/penpot-$PENPOT_VERSION"
mkdir -p "$PENPOT_DIR"
COMPOSE="$PENPOT_DIR/docker-compose.yaml"
if [[ ! -s "$COMPOSE" ]]; then
  curl --fail --location --retry 3 --retry-delay 2 --max-time 180 \
    --silent --show-error \
    "https://raw.githubusercontent.com/penpot/penpot/$PENPOT_VERSION/docker/images/docker-compose.yaml" \
    -o "$COMPOSE.part" > "$OUT/penpot-compose-fetch.log" 2>&1 &&
    mv "$COMPOSE.part" "$COMPOSE" || true
fi
if [[ ! -s "$COMPOSE" ]] ||
   ! grep -q 'penpot-frontend:' "$COMPOSE" ||
   ! grep -q 'penpot-backend:' "$COMPOSE"; then
  record penpot COMPOSE_FETCH_FAILED "$PENPOT_VERSION"
elif ! command -v docker >/dev/null 2>&1 || ! docker compose version >/dev/null 2>&1; then
  record penpot PREPARED_NEEDS_DOCKER "$PENPOT_VERSION;no_containers_started"
elif ! docker info >/dev/null 2>&1; then
  record penpot PREPARED_DOCKER_UNAVAILABLE "$PENPOT_VERSION"
elif (( $(free_kib) < 10485760 )); then
  record penpot PREPARED_NEEDS_10GIB_FOR_IMAGES "$PENPOT_VERSION"
elif ! PENPOT_VERSION="$PENPOT_VERSION" docker compose -p ferrari-penpot \
  -f "$COMPOSE" config --quiet > "$OUT/penpot-validate.log" 2>&1; then
  record penpot COMPOSE_INVALID "$PENPOT_VERSION"
elif PENPOT_VERSION="$PENPOT_VERSION" timeout 900 docker compose -p ferrari-penpot \
  -f "$COMPOSE" pull > "$OUT/penpot-images.log" 2>&1; then
  record penpot IMAGES_READY_NOT_RUNNING "$PENPOT_VERSION;configuration_required"
else
  record penpot IMAGE_DOWNLOAD_FAILED "$PENPOT_VERSION"
fi
python3 - "$TSV" "$OUT/heavy.json" <<'PY'
import csv,json,sys
from pathlib import Path
items=list(csv.DictReader(Path(sys.argv[1]).open(),delimiter="\t"))
report={"schema":1,"project":"motor-ferrari","group":"heavy-external","items":items,
        "note":"CPU ComfyUI has no model weights. Penpot is never started or exposed by this installer."}
Path(sys.argv[2]).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
print("FERRARI_HEAVY_REPORT=PASS")
PY
