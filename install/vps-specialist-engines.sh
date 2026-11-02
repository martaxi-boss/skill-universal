#!/usr/bin/env bash
# Ferrari isolated JADX + Ghidra + Temurin JDK 25, pinned official SHA256 releases.
set -Eeuo pipefail
umask 077
[[ "$(uname -s)" == Linux && "$(uname -m)" == x86_64 ]] || {
 echo 'FERRARI_SPECIALISTS_UNSUPPORTED_ARCH' >&2; exit 2;
}
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == 24.04 ]] || {
 echo 'FERRARI_SPECIALISTS_UNSUPPORTED_UBUNTU' >&2; exit 2;
}
SOURCE="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT="$HOME/.local/share/motor-ferrari"
TOOLS="$ROOT/tools"
JDK="$ROOT/runtimes/jdk-25.0.5_8"
JADX="$TOOLS/jadx-1.5.6"
GHIDRA="$TOOLS/ghidra-12.2"
mkdir -p "$ROOT/.runtime" "$ROOT/runtimes" "$TOOLS"
WORK="$(mktemp -d "$ROOT/.runtime/specialist.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT
download() {
  local url="$1" sha="$2" outfile="$3"
  curl --fail --location --retry 3 --retry-delay 2 --max-time 1200 \
       --silent --show-error -o "$outfile" "$url"
  printf '%s  %s\n' "$sha" "$outfile" | sha256sum -c -
}
if [[ ! -x "$JDK/bin/java" ]]; then
  download 'https://github.com/adoptium/temurin25-binaries/releases/download/jdk-25.0.5%2B8/OpenJDK25U-jdk_x64_linux_hotspot_25.0.5_8.tar.gz' \
    '68982529869257d0ee6b824ec5aa270ff8b118bb438670da0b97ebdab178d7fb' "$WORK/jdk.tar.gz"
  mkdir -p "$WORK/jdk"
  tar -xzf "$WORK/jdk.tar.gz" --strip-components=1 -C "$WORK/jdk"
  "$WORK/jdk/bin/java" -version 2>&1 | grep '25.0.5'
  mv "$WORK/jdk" "$JDK"
fi
export JAVA_HOME="$JDK"
export GHIDRA_JAVA_HOME="$JDK"
export PATH="$JDK/bin:$PATH"
export XDG_CONFIG_HOME="$ROOT/.runtime/xdg/config"
export XDG_CACHE_HOME="$ROOT/.runtime/xdg/cache"
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME"
java -version
if [[ ! -x "$JADX/bin/jadx" ]]; then
  download 'https://github.com/skylot/jadx/releases/download/v1.5.6/jadx-1.5.6.zip' \
    '545ea2be9c242511bc145755cf4bda2485ade42966e096f8b4d3da2a230e8974' "$WORK/jadx.zip"
  mkdir -p "$WORK/jadx"
  unzip -q "$WORK/jadx.zip" -d "$WORK/jadx"
  test -f "$WORK/jadx/bin/jadx"
  chmod +x "$WORK/jadx/bin/jadx"
  mv "$WORK/jadx" "$JADX"
fi
"$JADX/bin/jadx" --version
# Functional JADX smoke with a locally compiled harmless Java JAR.
mkdir -p "$WORK/source" "$WORK/jadx-out"
printf 'public class FerrariSmoke { public static int answer() { return 42; } }\n' \
  > "$WORK/source/FerrariSmoke.java"
"$JDK/bin/javac" --release 11 "$WORK/source/FerrariSmoke.java"
"$JDK/bin/jar" cf "$WORK/ferrari-smoke.jar" -C "$WORK/source" FerrariSmoke.class
"$JADX/bin/jadx" -d "$WORK/jadx-out" "$WORK/ferrari-smoke.jar"
test -f "$WORK/jadx-out/sources/FerrariSmoke.java"
grep -q 'FerrariSmoke' "$WORK/jadx-out/sources/FerrariSmoke.java"
echo 'FERRARI_JADX_FUNCTIONAL=PASS'
if [[ ! -x "$GHIDRA/support/analyzeHeadless" ]]; then
  download 'https://github.com/NationalSecurityAgency/ghidra/releases/download/Ghidra_12.2_build/ghidra_12.2_PUBLIC_20261016.zip' \
    '2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67' "$WORK/ghidra.zip"
  mkdir -p "$WORK/ghidra-extract"
  unzip -q "$WORK/ghidra.zip" -d "$WORK/ghidra-extract"
  found="$(find "$WORK/ghidra-extract" -mindepth 1 -maxdepth 1 -type d -name 'ghidra_*' -print -quit)"
  test -n "$found" && test -f "$found/support/analyzeHeadless"
  chmod +x "$found/support/analyzeHeadless"
  mv "$found" "$GHIDRA"
fi
mkdir -p "$WORK/ghidra-projects" "$SOURCE/smoke/specialists"
"$GHIDRA/support/analyzeHeadless" "$WORK/ghidra-projects" FerrariSmoke \
  -import /usr/bin/true -analysisTimeoutPerFile 60 -deleteProject \
  > "$SOURCE/smoke/specialists/ghidra-headless.log" 2>&1
grep -E 'Importing|Analysis|Finished|success|Successfully' \
  "$SOURCE/smoke/specialists/ghidra-headless.log" | tail -n 16 || true
echo 'FERRARI_GHIDRA_HEADLESS_FUNCTIONAL=PASS'
echo "FERRARI_SPECIALISTS_JDK=$("$JDK/bin/java" --version | sed -n '1p')"
echo 'FERRARI_JADX_GHIDRA_INSTALLED=YES'
