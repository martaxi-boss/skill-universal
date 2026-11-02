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
RUNTIME="$PROJECT_ROOT/.runtime/npm"
VERSION_REA=6.8.0
VERSION_RUFLO=3.71.0
printf 'Independent runtime: %s\n' "$RUNTIME"
printf 'REA target: rea-agents@%s\nRuflo target: ruflo@%s\n' "$VERSION_REA" "$VERSION_RUFLO"
if ! command -v node >/dev/null 2>&1 || ! command -v npm >/dev/null 2>&1; then
  echo 'Node.js/npm absent; install compatible Node.js before proceeding.' >&2
  exit 2
fi
NODE_VER="$(node -p 'process.versions.node')"
printf 'Detected Node.js: %s\n' "$NODE_VER"
if ! node -e 'const [a,b]=process.versions.node.split(".").map(Number); process.exit(a===22&&b>=19||a===24&&b>=11||a>=26?0:1)'; then
  echo 'REA requires Node >=22.19 / >=24.11 / >=26. No packages will be installed.' >&2
  exit 2
fi
if ((APPLY==0)); then
  echo 'DRY RUN. Example to apply after reviewing: bash install/install-agent-engines.sh --profile all --apply'
  exit 0
fi
mkdir -p "$RUNTIME"
if [[ "$PROFILE" = rea || "$PROFILE" = all ]]; then
  npm install --prefix "$RUNTIME/rea" --no-audit --no-fund --save-exact "rea-agents@$VERSION_REA"
  "$RUNTIME/rea/node_modules/.bin/rea" --help >/dev/null
  echo 'REA CLI smoke: PASS (help only; analysis engine/provider NOT certified)'
fi
if [[ "$PROFILE" = ruflo || "$PROFILE" = all ]]; then
  npm install --prefix "$RUNTIME/ruflo" --no-audit --no-fund --save-exact "ruflo@$VERSION_RUFLO"
  "$RUNTIME/ruflo/node_modules/.bin/ruflo" --help >/dev/null
  echo 'Ruflo CLI smoke: PASS (help only; swarm/model provider NOT certified)'
fi
printf 'Now run: python3 -m engine.cli doctor\n'
