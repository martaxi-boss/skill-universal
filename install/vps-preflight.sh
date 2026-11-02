#!/usr/bin/env bash
# Read-only VPS Ubuntu inspection, no project files required.
set -euo pipefail
. /etc/os-release
printf 'OS=%s VERSION=%s ARCH=%s\n' "$ID" "$VERSION_ID" "$(uname -m)"
[ "$ID" = ubuntu ] || { echo "ERROR: Ubuntu required"; exit 2; }
dpkg --compare-versions "$VERSION_ID" ge 24.04 || { echo "ERROR: Ubuntu 24.04+ required"; exit 2; }
printf 'CPU_CORES=%s\n' "$(getconf _NPROCESSORS_ONLN)"
awk '/MemTotal:/{printf "RAM_TOTAL_KIB=%s\n",$2} /MemAvailable:/{printf "RAM_FREE_KIB=%s\n",$2}' /proc/meminfo
printf 'DISK_FREE_KIB=%s\n' "$(df -Pk "$HOME" | awk 'END{print $4}')"
for exe in python3 node npm java git ffmpeg pdftotext tesseract jadx r2 apktool sudo; do
  if command -v "$exe" >/dev/null 2>&1; then
    printf '%s=%s\n' "$exe" "$(command -v "$exe")"
  else
    printf '%s=NOT_INSTALLED\n' "$exe"
  fi
done
if command -v node >/dev/null 2>&1; then node --version; fi
if command -v java >/dev/null 2>&1; then java -version 2>&1 | head -n 3; fi
if command -v sudo >/dev/null 2>&1 && sudo -n true >/dev/null 2>&1; then echo 'PASSWORDLESS_SUDO=YES'; else echo 'PASSWORDLESS_SUDO=NO'; fi
if [ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]; then echo 'GUI_SESSION=YES'; else echo 'GUI_SESSION=NO'; fi
if command -v nvidia-smi >/dev/null 2>&1; then nvidia-smi --query-gpu=name,memory.total --format=csv,noheader || true; else echo 'NVIDIA_GPU=NOT_DETECTED'; fi
echo 'FERRARI_VPS_PREFLIGHT=PASS_READ_ONLY'
