#!/usr/bin/env bash
# Motor Ferrari: Ubuntu APT installer, preview by default.
set -euo pipefail
cd "$(dirname "$0")/.."
PROFILE=maximum
APPLY=0
HEADLESS=0
while (($#)); do
  case "$1" in
    --profile) PROFILE="$2"; shift 2 ;;
    --apply) APPLY=1; shift ;;
    --headless) HEADLESS=1; shift ;;
    *) echo "Invalid option: $1" >&2; exit 2 ;;
  esac
done
test -r /etc/os-release || { echo "Missing os-release" >&2; exit 2; }
. /etc/os-release
test "$ID" = "ubuntu" || { echo "Ubuntu only" >&2; exit 2; }
command -v apt-cache >/dev/null
command -v dpkg >/dev/null
dpkg --compare-versions "$VERSION_ID" ge 24.04 || { echo "Ubuntu 24.04+ required" >&2; exit 2; }
ARGS=(python3 -m engine.ferrari packages --profile "$PROFILE" --plain)
if (( HEADLESS )); then ARGS+=(--headless); fi
mapfile -t REQUESTED < <("${ARGS[@]}")
AVAILABLE=()
MISSING=()
SKIPPED=()
for pkg in "${REQUESTED[@]}"; do
  [[ -n "$pkg" ]] || continue
  # Node 18 from Ubuntu APT can break REA's Node 22.23.4+ requirement.
  # Daemon packages may start/affect unrelated services on this VPS.
  case "$pkg" in
    nodejs|npm|prometheus|valkey-server)
      SKIPPED+=("$pkg")
      continue
      ;;
  esac
  candidate="$(apt-cache policy "$pkg" 2>/dev/null | awk '/Candidate:/ && !found {print $2; found=1}')"
  if [[ -n "$candidate" && "$candidate" != "(none)" ]]; then
    AVAILABLE+=("$pkg")
  else
    MISSING+=("$pkg")
  fi
done
printf 'Ferrari Ubuntu %s (%s) profile=%s headless=%s\n' "$VERSION_ID" "$(uname -m)" "$PROFILE" "$HEADLESS"
printf 'APT candidates: %s\n' "${#AVAILABLE[@]}"
if (( ${#SKIPPED[@]} )); then
  printf 'Isolated/excluded from APT install (not certified): %s\n' "${SKIPPED[*]}"
fi
printf '  %s\n' "${AVAILABLE[@]}"
if (( ${#MISSING[@]} )); then
  printf 'Unavailable APT names: %s\n' "${#MISSING[@]}"
  printf '  %s\n' "${MISSING[@]}"
fi
if (( ! APPLY )); then
  echo 'DRY RUN. No packages installed. Use --apply to install.'
  exit 0
fi
# APT candidates verified on the Ubuntu 24.04 runner, not arbitrary later releases.
if [[ "$VERSION_ID" != "24.04" ]]; then
  echo "APT install is validated for Ubuntu 24.04 only; stop for new platform review" >&2
  exit 2
fi
if (( ${#MISSING[@]} )); then
  echo 'Refusing partial install: required curated package candidates missing' >&2
  exit 3
fi
if (( EUID != 0 )); then
  echo 'sudo required for --apply' >&2
  exit 2
fi
FREE_KIB="$(df -Pk . | awk 'END {print $4}')"
if (( FREE_KIB < 3145728 )); then
  echo 'Less than 3 GiB free, cannot safely install.' >&2
  exit 2
fi
if (( ${#AVAILABLE[@]} )); then
  export DEBIAN_FRONTEND=noninteractive
  apt-get -s install --no-install-recommends "${AVAILABLE[@]}" >/dev/null
  apt-get install --no-install-recommends -y "${AVAILABLE[@]}"
fi
python3 -m engine.ferrari doctor
echo 'APT stage completed. REA, Ruflo, JADX and Ghidra need independent installations and tests.'
