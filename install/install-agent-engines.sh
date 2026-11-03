#!/usr/bin/env bash
# Optional isolated npm engines for Ubuntu/Linux. Preview first; --apply is explicit.
set -euo pipefail
PROFILE=all; APPLY=0
while (($#)); do
  case "$1" in
    --profile) PROFILE="${2:?missing value}"; shift 2;;
    --apply) APPLY=1; shift;;
    *) echo "Unknown option: $1" >&2; exit 2;;
  esac
done
case "$PROFILE" in rea|ruflo|all) ;; *) echo "Expected rea, ruflo, all" >&2; exit 2;; esac
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
RUNTIME="$HOME/.local/share/motor-ferrari/.runtime/npm"
VERSION_REA=6.8.0
VERSION_RUFLO=3.71.0
printf 'Ferrari-private runtime: %s\n' "$RUNTIME"
printf 'REA target: rea-agents@%s\nRuflo target: ruflo@%s\n' "$VERSION_REA" "$VERSION_RUFLO"
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo 'Node.js/npm absent; install compatible Node.js before proceeding.' >&2
  exit 2
fi
NODE_VER="$(node -p 'process.versions.node')"
printf 'Detected Node.js: %s\n' "$NODE_VER"
if ! node -e 'const [a,b,c]=process.versions.node.split(".").map(Number);const ok=(a===22&&(b>23||(b===23&&c>=4)))||(a===24&&(b>22||(b===22&&c>=1)))||(a===26&&(b>12||(b===12&&c>=1)))||a>26;process.exit(ok?0:1)'; then
  echo 'REA upstream package requires Node ^22.23.4 || ^24.22.1 || >=26.12.1. No packages will be installed.' >&2
  exit 2
fi
if ((APPLY==0)); then
  echo 'DRY RUN. Example to apply after reviewing: bash install/install-agent-engines.sh --profile all --apply'
  exit 0
fi
mkdir -p "$RUNTIME"
if [[ "$PROFILE" = rea || "$PROFILE" = all ]]; then
  if [[ -x "$RUNTIME/rea/node_modules/.bin/rea" ]] && \
     [[ "$(node -p "try { require('$RUNTIME/rea/node_modules/rea-agents/package.json').version } catch(e) { 'missing' }")" == "$VERSION_REA" ]]; then
    echo "FERRARI_REA_REUSE=EXACT_PINNED_VERSION"
  else
  npm install --prefix "$RUNTIME/rea" --no-audit --no-fund --save-exact "rea-agents@$VERSION_REA"
  fi
  "$RUNTIME/rea/node_modules/.bin/rea" --help >/dev/null
  echo 'REA CLI smoke: PASS (help only; analysis engine/provider NOT certified)'
fi
if [[ "$PROFILE" = ruflo || "$PROFILE" = all ]]; then
  if [[ -x "$RUNTIME/ruflo/node_modules/.bin/ruflo" ]] && \
     [[ "$(node -p "try { require('$RUNTIME/ruflo/node_modules/ruflo/package.json').version } catch(e) { 'missing' }")" == "$VERSION_RUFLO" ]]; then
    echo "FERRARI_RUFLO_REUSE=EXACT_PINNED_VERSION"
  else
  npm install --prefix "$RUNTIME/ruflo" --no-audit --no-fund --save-exact "ruflo@$VERSION_RUFLO"
  fi
  "$RUNTIME/ruflo/node_modules/.bin/ruflo" --help >/dev/null
  echo 'Ruflo CLI smoke: PASS (help only; swarm/model provider NOT certified)'
fi
printf 'Now run: python3 -m engine.cli doctor\n'
