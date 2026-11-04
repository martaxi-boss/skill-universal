#!/usr/bin/env bash
# Chromium headless shell + Playwright 1.64.1, strictly inside Ferrari runtime.
# No sudo, Snap, apt, daemon, global Node or SSH changes.
set -Eeuo pipefail
umask 077
. /etc/os-release
[[ "${ID:-}" == ubuntu && "${VERSION_ID:-}" == 24.04 && "$(uname -m)" == x86_64 ]] || {
  echo 'FERRARI_BROWSER_OS_UNSUPPORTED' >&2; exit 2;
}
(( EUID != 0 )) || { echo 'FERRARI_BROWSER_ROOT_DISALLOWED' >&2; exit 2; }

ROOT="/srv/projects/skill-universal"
NODE_ROOT="$ROOT/runtimes/node-22.23.4"
NODE="$NODE_ROOT/bin/node"
NPM="$NODE_ROOT/bin/npm"
PKG_ROOT="$ROOT/.runtime/npm/playwright"
PKG="$PKG_ROOT/node_modules/playwright"
export PLAYWRIGHT_BROWSERS_PATH="$ROOT/.runtime/browsers"
export NPM_CONFIG_CACHE="$ROOT/.runtime/npm-cache"
export NPM_CONFIG_UPDATE_NOTIFIER=false NPM_CONFIG_FUND=false NPM_CONFIG_AUDIT=false
export PLAYWRIGHT_DOWNLOAD_CONNECTION_TIMEOUT=120000
VERSION="1.64.1"
test -x "$NODE" && test -x "$NPM" || { echo 'FERRARI_ISOLATED_NODE_MISSING' >&2; exit 3; }
test "$("$NODE" --version)" = "v22.23.4" || { echo 'FERRARI_NODE_VERSION_MISMATCH' >&2; exit 3; }
FREE_KIB="$(df -Pk "$HOME" | awk 'END{print $4}')"
(( FREE_KIB >= 5242880 )) || { echo 'FERRARI_BROWSER_REQUIRES_5GIB_FREE' >&2; exit 4; }
mkdir -p "$PKG_ROOT" "$PLAYWRIGHT_BROWSERS_PATH" "$NPM_CONFIG_CACHE"
if ! "$NODE" -e 'const p=require(process.argv[1]);process.exit(p.version===process.argv[2]?0:1)' "$PKG/package.json" "$VERSION" >/dev/null 2>&1; then
  PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1 PATH="$NODE_ROOT/bin:$PATH" "$NPM" install \
    --prefix "$PKG_ROOT" --no-save --ignore-scripts --no-audit --no-fund \
    --no-progress --loglevel=error "playwright@$VERSION"
fi
"$NODE" -e 'const p=require(process.argv[1]);if(p.version!==process.argv[2])process.exit(2)' "$PKG/package.json" "$VERSION"
# Playwright 1.64.1 pins Chromium headless-shell revision 1248.
# chromium.executablePath() points to the *full* browser and is not valid
# after --only-shell; verify the downloaded headless shell itself.
BROWSER_BIN="$PLAYWRIGHT_BROWSERS_PATH/chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell"
if [[ ! -x "$BROWSER_BIN" ]]; then
  PATH="$NODE_ROOT/bin:$PATH" "$NODE" "$PKG/cli.js" install chromium --only-shell
fi
test -x "$BROWSER_BIN" || { echo 'FERRARI_HEADLESS_SHELL_NOT_INSTALLED' >&2; exit 6; }
"$BROWSER_BIN" --version
echo "FERRARI_PLAYWRIGHT_ISOLATED_VERSION=$VERSION"
echo "FERRARI_BROWSER_BIN=$BROWSER_BIN"
echo 'FERRARI_BROWSER_INSTALL=PASS_FERRARI_ONLY_NO_SYSTEM_PACKAGES'
