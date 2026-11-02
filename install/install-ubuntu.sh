#!/usr/bin/env bash
# Ubuntu installer; dry-run unless --apply. Never touches unrelated projects.
set -euo pipefail
PROFILE="maximum"; APPLY=0
while (($#)); do
  case "$1" in
    --profile) PROFILE="${2:?missing profile}"; shift 2;;
    --apply) APPLY=1; shift;;
    *) echo "Unknown argument: $1" >&2; exit 2;;
  esac
done
case "$PROFILE" in core|web|reverse|creative|docs|mobile|maximum) ;; *) echo "Invalid profile" >&2; exit 2;; esac
if [[ ! -r /etc/os-release ]]; then echo "Requires Ubuntu" >&2; exit 2; fi
# shellcheck disable=SC1091
. /etc/os-release
if [[ "${ID:-}" != "ubuntu" ]]; then echo "Installer only targets Ubuntu" >&2; exit 2; fi
if ! command -v apt-cache >/dev/null; then echo "apt-cache is missing" >&2; exit 2; fi
CORE=(ca-certificates git curl wget python3 python3-pip python3-venv build-essential cmake clang jq ripgrep fd-find zip unzip sqlite3 golang-go rustc cargo podman)
WEB=(nodejs npm) # native Ubuntu runtime may NOT meet the REA required version; check after install
REVERSE=(file binutils gdb strace yara binwalk apktool openjdk-21-jdk-headless)
CREATIVE=(ffmpeg imagemagick inkscape gimp blender sox espeak-ng libimage-exiftool-perl)
DOCS=(pandoc poppler-utils libreoffice tesseract-ocr graphviz)
MOBILE=(adb aapt apksigner zipalign)
PACKAGES=()
case "$PROFILE" in
  core) PACKAGES=("${CORE[@]}");;
  web) PACKAGES=("${CORE[@]}" "${WEB[@]}");;
  reverse) PACKAGES=("${CORE[@]}" "${REVERSE[@]}");;
  creative) PACKAGES=("${CORE[@]}" "${CREATIVE[@]}");;
  docs) PACKAGES=("${CORE[@]}" "${DOCS[@]}");;
  mobile) PACKAGES=("${CORE[@]}" "${MOBILE[@]}");;
  maximum) PACKAGES=("${CORE[@]}" "${WEB[@]}" "${REVERSE[@]}" "${CREATIVE[@]}" "${DOCS[@]}" "${MOBILE[@]}");;
esac
# no uncontrolled `apt upgrade`, no adding outside repositories, no curl | bash
INSTALLABLE=(); MISSING=(); SEEN=" "
for name in "${PACKAGES[@]}"; do
  if [[ "$SEEN" == *" $name "* ]]; then continue; fi
  SEEN+="$name "
  candidate="$(apt-cache policy "$name" 2>/dev/null | sed -n 's/^  Candidate: //p' | head -1)"
  if [[ -n "$candidate" && "$candidate" != "(none)" ]]; then INSTALLABLE+=("$name"); else MISSING+=("$name"); fi
done
printf 'Target OS: %s %s / %s\n' "${ID:-unknown}" "${VERSION_ID:-unknown}" "$(uname -m)"
printf 'Profile: %s | installable: %s | unavailable APT: %s\n' "$PROFILE" "${#INSTALLABLE[@]}" "${#MISSING[@]}"
printf 'Installable packages:\n'; printf '  %s\n' "${INSTALLABLE[@]}"
if ((${#MISSING[@]})); then printf 'Unavailable in configured repositories:\n'; printf '  %s\n' "${MISSING[@]}"; fi
if ((APPLY)); then
  if ((EUID != 0)); then echo "Use sudo only for --apply" >&2; exit 2; fi
  if ((${#INSTALLABLE[@]})); then
    export DEBIAN_FRONTEND=noninteractive
    apt-get install --no-install-recommends -y "${INSTALLABLE[@]}"
  fi
  echo 'APT packages installed; verify binary status with: python3 -m engine.cli doctor'
  echo 'REA, Ruflo, JADX, Ghidra, ComfyUI and cloud-provider credentials require separate checks; NOT installed by this APT script.'
else
  echo 'DRY RUN: no changes made. Add --apply explicitly after reviewing hardware, disk and packages.'
fi
