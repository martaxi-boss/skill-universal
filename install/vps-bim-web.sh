#!/usr/bin/env bash
# Install exactly two public, free professional tools in Ferrari-owned runtimes.
# Never change system Python/Node, unrelated apps, SSH or services.
set -Eeuo pipefail
umask 077
. /etc/os-release
[[ "${ID:-}" == ubuntu && "${VERSION_ID:-}" == 24.04 ]] || {
  echo 'FERRARI_PRO_TOOLS_UNSUPPORTED_OS' >&2; exit 2;
}
[[ "$(uname -m)" == x86_64 && "$(id -u)" != 0 ]] || {
  echo 'FERRARI_PRO_TOOLS_UNSUPPORTED_USER_OR_ARCH' >&2; exit 2;
}
ROOT="/srv/projects/skill-universal"
WORK="$ROOT/.runtime"
NODE_ROOT="$ROOT/runtimes/node-22.23.4"
PY_DIR="$WORK/venvs/bim"
VITE_ROOT="$WORK/npm/vite"
IFC_VERSION="0.9.0.post1"
VITE_VERSION="8.3.5"
test -x "$NODE_ROOT/bin/node" && test -x "$NODE_ROOT/bin/npm" || {
  echo 'FERRARI_ISOLATED_NODE_REQUIRED' >&2; exit 3;
}
test "$("$NODE_ROOT/bin/node" --version)" = "v22.23.4" || exit 3
python3 - <<'PY'
import sys
assert sys.version_info[:2] == (3, 12), 'Expected Ubuntu 24.04 Python 3.12'
PY
FREE_KIB="$(df -Pk "$HOME" | awk 'END{print $4}')"
(( FREE_KIB >= 3145728 )) || { echo 'FERRARI_PRO_TOOLS_NEED_3GIB' >&2; exit 4; }
mkdir -p "$WORK/venvs" "$WORK/npm" "$WORK/npm-cache"
if [[ ! -x "$PY_DIR/bin/python" ]]; then
  python3 -m venv "$PY_DIR"
fi
if ! "$PY_DIR/bin/python" -c 'import importlib.metadata as m,ifcopenshell; assert m.version("ifcopenshell")=="0.9.0.post1"' >/dev/null 2>&1; then
  "$PY_DIR/bin/python" -m pip install --only-binary=:all: --disable-pip-version-check --no-input "ifcopenshell==$IFC_VERSION"
fi
"$PY_DIR/bin/python" -c 'import importlib.metadata as m,ifcopenshell; assert m.version("ifcopenshell")=="0.9.0.post1"; print("FERRARI_ISOLATED_IFC="+m.version("ifcopenshell"))'

if [[ ! -f "$VITE_ROOT/node_modules/vite/package.json" ]] || ! python3 - "$VITE_ROOT/node_modules/vite/package.json" <<'PY'
import json,sys
assert json.load(open(sys.argv[1],encoding="utf-8"))["version"] == "8.3.5"
PY
then
  mkdir -p "$VITE_ROOT"
  PATH="$NODE_ROOT/bin:$PATH" \
    NPM_CONFIG_CACHE="$WORK/npm-cache" NPM_CONFIG_UPDATE_NOTIFIER=false \
    NPM_CONFIG_FUND=false \
    "$NODE_ROOT/bin/npm" install --prefix "$VITE_ROOT" --no-save \
      --ignore-scripts --no-audit --no-fund --no-progress \
      --loglevel=error "vite@$VITE_VERSION"
fi
test -f "$VITE_ROOT/node_modules/vite/bin/vite.js"
VITE_OUTPUT="$("$NODE_ROOT/bin/node" "$VITE_ROOT/node_modules/vite/bin/vite.js" --version)"
[[ "$VITE_OUTPUT" == *"$VITE_VERSION"* ]] || {
  echo "FERRARI_VITE_VERSION_MISMATCH=$VITE_OUTPUT" >&2; exit 5;
}
echo "FERRARI_ISOLATED_VITE=$VITE_VERSION"
echo 'FERRARI_PRO_TOOLS_INSTALL=PASS_NO_GLOBAL_CHANGES'
