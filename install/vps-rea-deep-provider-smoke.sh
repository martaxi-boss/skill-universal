#!/usr/bin/env bash
# Real Ferrari-private REA Ghidra/JADX smoke. Never consult legacy REA or other projects.
set -Eeuo pipefail
ROOT="$HOME/.local/share/motor-ferrari"
REA="$ROOT/.runtime/npm/rea/node_modules/.bin/rea"
APKTOOL="$ROOT/tools/apktool-3.0.3/bin/apktool"
JDK="$ROOT/runtimes/jdk-25.0.5_8"
GHIDRA="$ROOT/tools/rea-providers/ghidra-12.1.4"
JAR="$ROOT/tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar"
NODE="$ROOT/runtimes/node-22.23.4"
test "$(id -u)" -ne 0
for p in "$REA" "$APKTOOL" "$JDK/bin/java" "$NODE/bin/node" "$GHIDRA/support/analyzeHeadless" "$JAR"; do
  test -f "$p" && test ! -L "$p" || {
    if [[ "$p" == "$REA" ]]; then
      test -f "$p" && test "$(realpath "$p")" == "$ROOT/.runtime/npm/rea/node_modules/rea-agents/bin/cli.js" || exit 2
    else
      echo 'FERRARI_REA_PRIVATE_EXECUTOR_MISSING' >&2; exit 2
    fi
  }
done
WORK="$(mktemp -d "$ROOT/.runtime/rea-functional.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT
export PATH="$NODE/bin:$JDK/bin:$PATH"
export JAVA_HOME="$JDK" GHIDRA_JAVA_HOME="$JDK"
export GHIDRA_INSTALL_DIR="$GHIDRA"
export REA_JADX_MCP_JAR="$JAR"
export REA_APKTOOL_COMMAND="$APKTOOL"
export XDG_CONFIG_HOME="$ROOT/.runtime/rea-config"
export XDG_CACHE_HOME="$ROOT/.runtime/rea-cache"
export XDG_DATA_HOME="$ROOT/.runtime/rea-data"
export TMPDIR="$WORK"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME"

# Only use a benign Ubuntu system ELF as the target.
if ! timeout 360 "$REA" analyze /usr/bin/true --provider ghidra --json \
  > "$WORK/ghidra.json" 2> "$WORK/ghidra.err"; then
  echo 'FERRARI_REA_GHIDRA_ANALYSIS_FAILED' >&2
  tail -n 12 "$WORK/ghidra.err" >&2
  exit 5
fi
python3 - "$WORK/ghidra.json" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
data=json.loads(p.read_text())
assert isinstance(data,(dict,list)) and p.stat().st_size>100
print('FERRARI_REA_GHIDRA_NATIVE_ANALYSIS=PASS;json_bytes='+str(p.stat().st_size))
PY

# Build a synthetic APK in the private Ferrari temp tree, not from any user app.
SRC="$WORK/apk-src"
mkdir -p "$SRC/res/values" "$SRC/smali/com/ferrari"
cat > "$SRC/AndroidManifest.xml" <<'APKM'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.ferrari.smoke" android:versionCode="1" android:versionName="1.0">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="28"/>
    <application android:label="@string/app_name"/>
</manifest>
APKM
cat > "$SRC/res/values/strings.xml" <<'APKR'
<?xml version="1.0" encoding="utf-8"?>
<resources><string name="app_name">Ferrari provider smoke</string></resources>
APKR
cat > "$SRC/smali/com/ferrari/Smoke.smali" <<'APKS'
.class public Lcom/ferrari/Smoke;
.super Ljava/lang/Object;
.source "Smoke.java"

.method public static status()Ljava/lang/String;
    .locals 1
    const-string v0, "Ferrari provider smoke"
    return-object v0
.end method
APKS
cat > "$SRC/apktool.yml" <<'APKY'
version: 3.0.3
apkFileName: ferrari-provider-smoke.apk
isFrameworkApk: false
usesFramework:
  ids:
  - 1
sdkInfo:
  minSdkVersion: 21
  targetSdkVersion: 28
packageInfo:
  forcedPackageId: 127
  renameManifestPackage: null
versionInfo:
  versionCode: 1
  versionName: '1.0'
resourcesAreCompressed: false
sharedLibrary: false
sparseResources: false
unknownFiles: {}
doNotCompress: []
APKY
"$APKTOOL" b "$SRC" -o "$WORK/ferrari-provider-smoke.apk" > "$WORK/apktool.log" 2>&1
test -s "$WORK/ferrari-provider-smoke.apk"
if ! timeout 300 "$REA" inspect-android-class "$WORK/ferrari-provider-smoke.apk" \
  com.ferrari.Smoke --json > "$WORK/jadx.json" 2> "$WORK/jadx.err"; then
  echo 'FERRARI_REA_JADX_CLASS_ANALYSIS_FAILED' >&2
  tail -n 15 "$WORK/jadx.err" >&2
  exit 6
fi
python3 - "$WORK/jadx.json" <<'PY'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
value=json.loads(p.read_text())
assert isinstance(value,(dict,list)) and p.stat().st_size>100
assert 'Smoke' in json.dumps(value), 'Expected synthetic class identity'
print('FERRARI_REA_JADX_CLASS_ANALYSIS=PASS;json_bytes='+str(p.stat().st_size))
PY
echo 'FERRARI_REA_DEEP_PROVIDERS=PASS'
