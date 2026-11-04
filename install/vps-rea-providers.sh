#!/usr/bin/env bash
# Ferrari-owned providers for the unmodified original rea-agents 6.8.0.
# No installation or config is shared with any separate REA project.
set -Eeuo pipefail
. /etc/os-release
test "$ID" = ubuntu && test "$VERSION_ID" = 24.04 && test "$(uname -m)" = x86_64
ROOT="/srv/projects/skill-universal"
LEGACY_ALIAS="$HOME/.local/share/motor-ferrari"
# Historical Ferrari path may be a symlink after physical project migration.
# Accept only the exact independent Ferrari repository directory.
if [[ -L "$LEGACY_ALIAS" ]]; then
  [[ "$(realpath -e "$LEGACY_ALIAS")" == "/srv/projects/skill-universal" ]] &&
    [[ -d "/srv/projects/skill-universal" ]] &&
    [[ ! -L "/srv/projects/skill-universal" ]] || {
      echo 'FERRARI_PROJECT_ALIAS_INVALID' >&2; exit 6;
    }
  ROOT="/srv/projects/skill-universal"
fi
TOOLS="$ROOT/tools"
REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"
NODE="$ROOT/runtimes/node-22.23.4/bin/node"
JDK="$ROOT/runtimes/jdk-25.0.5_8"
GHIDRA="$TOOLS/rea-providers/ghidra-12.1.4"
JAR="$TOOLS/rea-providers/jadx-headless-mcp-0.7.1-all.jar"
JAR_SHA="6e5eacf500b64292bfb73c49797c1958f6ee44646e43e868039ae7feb573ff75"
GHIDRA_SHA="ddac49f903da9d5bac833e5cc79395098b9c33cfd3279be5f31bd00387d2d4db"
GHIDRA_URL="https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.1.4_build/ghidra_12.1.4_PUBLIC_20260921.zip"
JAR_URL="https://github.com/1013503897/jadx-headless-mcp/releases/download/v0.7.1/jadx-headless-mcp-0.7.1-all.jar"

test -d "$ROOT" && test ! -L "$ROOT"
test -x "$REA" && test -x "$NODE" && test -x "$JDK/bin/java"
test -f "$ROOT/tools/apktool-3.0.3/bin/apktool"
mkdir -p "$TOOLS/rea-providers" "$ROOT/.runtime"
test ! -L "$TOOLS/rea-providers"
WORK="$(mktemp -d "$ROOT/.runtime/rea-provider-install.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT
export PATH="$ROOT/runtimes/node-22.23.4/bin:$JDK/bin:$PATH"
export JAVA_HOME="$JDK" GHIDRA_JAVA_HOME="$JDK"
export XDG_CACHE_HOME="$ROOT/.runtime/rea-cache"
export XDG_CONFIG_HOME="$ROOT/.runtime/rea-config"
export XDG_DATA_HOME="$ROOT/.runtime/rea-data"
export REA_APKTOOL_COMMAND="$ROOT/tools/apktool-3.0.3/bin/apktool"

if [[ ! -f "$JAR" ]]; then
  curl --fail --location --retry 3 --retry-delay 3 --connect-timeout 25 --max-time 600 \
    "$JAR_URL" -o "$WORK/jadx-headless.jar"
  echo "$JAR_SHA  $WORK/jadx-headless.jar" | sha256sum -c -
  mv "$WORK/jadx-headless.jar" "$JAR"
fi
test ! -L "$JAR"
echo "$JAR_SHA  $JAR" | sha256sum -c -
"$JDK/bin/jar" tf "$JAR" > "$WORK/jadx-contents.txt"
grep -qE "[.]class$" "$WORK/jadx-contents.txt"
echo 'FERRARI_REA_JADX_BRIDGE_PIN=PASS'

if [[ ! -x "$GHIDRA/support/analyzeHeadless" ]]; then
  test ! -e "$GHIDRA" && test ! -L "$GHIDRA"
  curl --fail --location --retry 3 --retry-delay 3 --connect-timeout 30 --max-time 1200 \
    "$GHIDRA_URL" -o "$WORK/ghidra-12.1.4.zip"
  echo "$GHIDRA_SHA  $WORK/ghidra-12.1.4.zip" | sha256sum -c -
  mkdir "$WORK/ghidra-unpack"
  unzip -q "$WORK/ghidra-12.1.4.zip" -d "$WORK/ghidra-unpack"
  SOURCE="$WORK/ghidra-unpack/ghidra_12.1.4_PUBLIC"
  test -x "$SOURCE/support/analyzeHeadless"
  test -f "$SOURCE/Ghidra/application.properties"
  grep -Eq '^application[.]version=12[.]1[.]4$' "$SOURCE/Ghidra/application.properties"
  mv "$SOURCE" "$GHIDRA"
fi
test ! -L "$GHIDRA"
test -x "$GHIDRA/support/analyzeHeadless"
grep -Eq '^application[.]version=12[.]1[.]4$' "$GHIDRA/Ghidra/application.properties"
echo 'FERRARI_REA_GHIDRA_COMPATIBLE_PIN=PASS'

export GHIDRA_INSTALL_DIR="$GHIDRA"
export REA_JADX_MCP_JAR="$JAR"
# The upstream doctor may report unrelated optional providers absent. Validate
# the two specifically installed providers rather than a misleading global bool.
set +e
"$REA" doctor --provider ghidra --json > "$WORK/doctor.json"
doctor_exit=$?
set -e
python3 - "$WORK/doctor.json" "$doctor_exit" <<'PY'
import json,sys
from pathlib import Path
d=json.loads(Path(sys.argv[1]).read_text())
by_id={x.get('id'):x for x in d.get('providerInspections',[]) if isinstance(x,dict)}
for name in ('ghidra','jadx'):
    info=by_id.get(name)
    if info is None or info.get('available') is not True:
        checks=[x for x in d.get('checks',[]) if isinstance(x,dict) and
                x.get('name') in ('ghidra-version','jadx')]
        print('FERRARI_REA_PROVIDER_BLOCKED='+name+';checks='+json.dumps(
            [{'name':x.get('name'),'ok':x.get('ok'),'detail':str(x.get('detail'))[:180]} for x in checks]))
        sys.exit(4)
    print('FERRARI_REA_PROVIDER_'+name.upper()+'=PASS')
print('FERRARI_REA_PRIVATE_PROVIDERS=PASS')
PY
