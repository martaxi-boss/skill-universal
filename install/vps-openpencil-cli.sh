#!/usr/bin/env bash
# OpenPencil CLI 0.16.0, Ferrari-only, Ubuntu 24.04 x86_64.
# Runs with the existing Ferrari-owned Node runtime; never uses apt/npm -g.
set -Eeuo pipefail
umask 077

ROOT="/srv/projects/skill-universal"
NODE="$ROOT/runtimes/node-22.23.4/bin/node"
NPM_CLI="$ROOT/runtimes/node-22.23.4/lib/node_modules/npm/bin/npm-cli.js"
PARENT="$ROOT/.runtime/npm"
DEST="$PARENT/openpencil"
VERSION="0.16.0"
PACKAGE="@open-pencil/cli"
BIN_REL="node_modules/@open-pencil/cli/bin/openpencil.js"
MODE="${1:---check}"

[[ "$#" -le 1 && ( "$MODE" == --check || "$MODE" == --apply ) ]] || {
  echo "Usage: $0 [--check|--apply]" >&2; exit 2;
}
[[ -d "$ROOT" && ! -L "$ROOT" && -d "$ROOT/.runtime" && ! -L "$ROOT/.runtime" ]] || {
  echo FERRARI_OPENPENCIL_PROJECT_INVALID >&2; exit 2;
}
[[ "$(stat -c '%u' "$ROOT")" == "$(id -u)" ]] || {
  echo FERRARI_OPENPENCIL_OWNER_MISMATCH >&2; exit 2;
}
[[ -x "$NODE" && -f "$NPM_CLI" && ! -L "$NODE" && ! -L "$NPM_CLI" ]] || {
  echo FERRARI_OPENPENCIL_PRIVATE_NODE_OR_NPM_MISSING >&2; exit 2;
}
[[ "$("$NODE" -p 'process.version')" == "v22.23.4" ]] || {
  echo FERRARI_OPENPENCIL_NODE_VERSION_MISMATCH >&2; exit 2;
}
[[ ! -L "$PARENT" && ! -L "$DEST" ]] || {
  echo FERRARI_OPENPENCIL_LINK_FORBIDDEN >&2; exit 2;
}

version_at() {
  local dir="$1" pkg="$1/node_modules/@open-pencil/cli/package.json"
  [[ -f "$pkg" && ! -L "$pkg" ]] || return 1
  "$NODE" -p "JSON.parse(require('fs').readFileSync(process.argv[1], 'utf8')).version" "$pkg"
}

verify_install() {
  local dir="$1" version binary
  [[ -d "$dir" && ! -L "$dir" && -f "$dir/$BIN_REL" ]] || return 1
  [[ "$(realpath -e "$dir/$BIN_REL")" == "$dir/"* ]] || return 1
  version="$(version_at "$dir")" || return 1
  [[ "$version" == "$VERSION" ]] || return 1
  binary="$dir/$BIN_REL"
  "$NODE" "$binary" --help >/dev/null
}

smoke_file_exports() {
  local dir="$1" work="$2" binary="$1/$BIN_REL"
  cat > "$work/design.html" <<'HTML'
<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Ferrari OpenPencil smoke</title></head>
<body><main style="width:480px;padding:24px;background-color:#f3f4f6">
<h1 style="font-size:30px;color:#20252b">Ferrari design</h1>
<p style="font-size:16px;color:#364152">Private OpenPencil test</p>
</main></body></html>
HTML
  "$NODE" "$binary" import "$work/design.html" -o "$work/design.fig" --json > "$work/import.json"
  [[ -s "$work/design.fig" ]]
  "$NODE" "$binary" info "$work/design.fig" --json > "$work/info.json"
  [[ -s "$work/info.json" ]]
  "$NODE" "$binary" export "$work/design.fig" -f svg -o "$work/design.svg" > "$work/export-svg.log"
  "$NODE" "$binary" export "$work/design.fig" -f html --html standalone -o "$work/design-export.html" > "$work/export-html.log"
  [[ -s "$work/design.svg" && -s "$work/design-export.html" ]]
  grep -qi '<svg' "$work/design.svg"
  grep -qi '<html' "$work/design-export.html"
  printf 'FERRARI_OPENPENCIL_REAL_IMPORT=PASS\n'
  printf 'FERRARI_OPENPENCIL_REAL_SVG=PASS sha256=%s\n' "$(sha256sum "$work/design.svg" | cut -d' ' -f1)"
  printf 'FERRARI_OPENPENCIL_REAL_HTML=PASS sha256=%s\n' "$(sha256sum "$work/design-export.html" | cut -d' ' -f1)"
}

if [[ "$MODE" == --check ]]; then
  if verify_install "$DEST"; then
    printf 'FERRARI_OPENPENCIL_CLI=PASS version=%s scope=private\n' "$VERSION"
    exit 0
  fi
  echo FERRARI_OPENPENCIL_CLI=NOT_CERTIFIED_OR_NOT_INSTALLED >&2
  exit 3
fi

[[ -d "$PARENT" && ! -L "$PARENT" && "$(stat -c '%u' "$PARENT")" == "$(id -u)" ]] || {
  echo FERRARI_OPENPENCIL_NPM_PARENT_INVALID >&2; exit 3;
}
[[ ! -e "$DEST" ]] || {
  # Never overwrite an existing installation; verify and reuse exact version.
  verify_install "$DEST" && { echo FERRARI_OPENPENCIL_CLI=PASS_REUSE; exit 0; }
  echo FERRARI_OPENPENCIL_EXISTING_CONFLICT >&2; exit 3;
}
WORK="$(mktemp -d "$PARENT/.openpencil-work-XXXXXXXX")"
cleanup() {
  if [[ -n "${WORK:-}" && -d "$WORK" && ! -L "$WORK" ]]; then rm -rf -- "$WORK"; fi
}
trap cleanup EXIT
mkdir -p "$WORK"/{install,tmp,cache,config,data,home}
export HOME="$WORK/home" TMPDIR="$WORK/tmp" TMP="$WORK/tmp"
export XDG_CACHE_HOME="$WORK/cache" XDG_CONFIG_HOME="$WORK/config" XDG_DATA_HOME="$WORK/data"
export npm_config_cache="$WORK/cache/npm" npm_config_update_notifier=false
export npm_config_userconfig="$WORK/npmrc"
export PATH="$ROOT/runtimes/node-22.23.4/bin:/usr/bin:/bin"

# Package scripts are disabled: all dependencies stay within WORK until smoke PASS.
"$NODE" "$NPM_CLI" install --prefix "$WORK/install" --ignore-scripts \
  --no-audit --no-fund --no-progress --save-exact "$PACKAGE@$VERSION"
verify_install "$WORK/install"
smoke_file_exports "$WORK/install" "$WORK"
mv -T -- "$WORK/install" "$DEST"
verify_install "$DEST"
echo FERRARI_OPENPENCIL_CLI=PASS_INSTALLED_PRIVATE
echo FERRARI_OPENPENCIL_GLOBAL_APT_NPM_CHANGES=ZERO
