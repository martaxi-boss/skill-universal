#!/usr/bin/env bash
# Isolated official Node + REA/Ruflo for Ferrari only. Does not modify system runtimes.
set -Eeuo pipefail
umask 077
if [[ "$(uname -s)" != "Linux" || "$(uname -m)" != "x86_64" ]]; then
  echo 'FERRARI_AGENTS_BLOCKED_UNSUPPORTED_ARCH' >&2; exit 2
fi
SCRIPT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
test -f "$SCRIPT_ROOT/engine/ferrari.py" || exit 2
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || {
  echo 'FERRARI_AGENTS_BLOCKED_NOT_UBUNTU_2404' >&2; exit 2;
}
ROOT="$HOME/.local/share/motor-ferrari"
NODE_VER="22.23.4"
NODE_DIR="$ROOT/runtimes/node-$NODE_VER"
NODE_ARCHIVE="node-v$NODE_VER-linux-x64.tar.xz"
NODE_SHA256="1805bcd35e6815559bd2eb97db438d3fdb0eb3a5e6a977b7c1badca76337e9ce"
NODE_URL="https://nodejs.org/dist/v$NODE_VER/$NODE_ARCHIVE"
mkdir -p "$ROOT/runtimes"
if [[ ! -x "$NODE_DIR/bin/node" ]]; then
  STAGING="$(mktemp -d "$ROOT/runtimes/.node-stage.XXXXXXXX")"
  trap 'rm -rf -- "$STAGING"' EXIT
  curl --fail --location --retry 2 --max-time 180 --silent --show-error \
    --output "$STAGING/$NODE_ARCHIVE" "$NODE_URL"
  printf '%s  %s\n' "$NODE_SHA256" "$STAGING/$NODE_ARCHIVE" | sha256sum -c -
  mkdir -p "$STAGING/node"
  tar -xJf "$STAGING/$NODE_ARCHIVE" --strip-components=1 -C "$STAGING/node"
  test "$("$STAGING/node/bin/node" --version)" = "v$NODE_VER"
  mv "$STAGING/node" "$NODE_DIR"
  rm -f "$STAGING/$NODE_ARCHIVE"
  rmdir "$STAGING"
  trap - EXIT
fi
export PATH="$NODE_DIR/bin:$PATH"
export NPM_CONFIG_CACHE="$ROOT/.runtime/npm-cache"
export NPM_CONFIG_UPDATE_NOTIFIER=false
export NPM_CONFIG_FUND=false
test "$(node --version)" = "v$NODE_VER" || exit 3
printf 'FERRARI_ISOLATED_NODE=%s\n' "$(node --version)"
mkdir -p "$NPM_CONFIG_CACHE"
cd "$SCRIPT_ROOT"
bash install/install-agent-engines.sh --profile all --apply
REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"
RUFLO="$ROOT/.runtime/npm/ruflo/node_modules/.bin/ruflo"
test -x "$REA" && test -x "$RUFLO"
"$REA" --help >/dev/null
"$RUFLO" --help >/dev/null
echo "FERRARI_REA_CLI=PASS_HELP_ONLY"
echo "FERRARI_RUFLO_CLI=PASS_HELP_ONLY"
echo "FERRARI_AGENT_ENGINES_INSTALLED=YES_UNCERTIFIED_FUNCTIONAL"
echo "FERRARI_EXTERNAL_REA_DEPENDENCY=NONE"
python3 -m engine.ferrari doctor
