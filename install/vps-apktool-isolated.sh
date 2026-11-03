#!/usr/bin/env bash
# Install official Apktool 3.0.3 for Ferrari only; never use REA or system Java.
set -Eeuo pipefail
umask 077
. /etc/os-release
[[ "$ID" == ubuntu && "$VERSION_ID" == "24.04" && "$(uname -m)" == "x86_64" ]] || {
  echo 'FERRARI_APKTOOL_UNSUPPORTED_UBUNTU' >&2; exit 2;
}
ROOT="$HOME/.local/share/motor-ferrari"
JAVA="$ROOT/runtimes/jdk-25.0.5_8/bin/java"
TARGET="$ROOT/tools/apktool-3.0.3"
JAR="$TARGET/apktool_3.0.3.jar"
URL="https://github.com/iBotPeaches/Apktool/releases/download/v3.0.3/apktool_3.0.3.jar"
SHA256="dbf930b076c6b9be08d57c449cacefc3bdd6b71ebd59b3066fc0e1f5b14f9423"
test -x "$JAVA" || { echo 'FERRARI_OWN_JAVA_MISSING' >&2; exit 2; }
"$JAVA" -version 2>&1 | grep -q '25.0.5' || {
  echo 'FERRARI_OWN_JAVA_WRONG_VERSION' >&2; exit 2;
}
mkdir -p "$ROOT/tools" "$ROOT/.runtime/apktool-frameworks" "$ROOT/.runtime/apktool-home"
if [[ ! -f "$JAR" ]]; then
  # Preserve an unexpected preexisting target instead of overwriting it.
  if [[ -e "$TARGET" || -L "$TARGET" ]]; then
    echo 'FERRARI_APKTOOL_TARGET_CONFLICT' >&2; exit 2
  fi
  STAGE="$(mktemp -d "$ROOT/tools/.apktool-stage.XXXXXXXX")"
  trap 'rm -rf -- "$STAGE"' EXIT
  curl --fail --location --retry 3 --retry-delay 2 --max-time 900 \
    --silent --show-error --output "$STAGE/apktool_3.0.3.jar" "$URL"
  printf '%s  %s\n' "$SHA256" "$STAGE/apktool_3.0.3.jar" | sha256sum -c -
  mkdir -p "$STAGE/bin"
  cat > "$STAGE/bin/apktool" <<'LAUNCH'
#!/usr/bin/env bash
# Ferrari-owned Java and frameworks; no PATH Java, REA, or shared Apktool cache.
set -Eeuo pipefail
ROOT="$HOME/.local/share/motor-ferrari"
JAVA="$ROOT/runtimes/jdk-25.0.5_8/bin/java"
JAR="$ROOT/tools/apktool-3.0.3/apktool_3.0.3.jar"
FRAME="$ROOT/.runtime/apktool-frameworks"
test -x "$JAVA" && test -r "$JAR"
mkdir -p "$FRAME" "$ROOT/.runtime/apktool-home"
if [[ "${1:-}" == "d" || "${1:-}" == "decode" || "${1:-}" == "b" || "${1:-}" == "build" ]]; then
  cmd="$1"; shift
  exec "$JAVA" "-Duser.home=$ROOT/.runtime/apktool-home" -jar "$JAR" "$cmd" -p "$FRAME" "$@"
fi
exec "$JAVA" "-Duser.home=$ROOT/.runtime/apktool-home" -jar "$JAR" "$@"
LAUNCH
  chmod 750 "$STAGE/bin/apktool"
  mv "$STAGE" "$TARGET"
  trap - EXIT
fi
test -f "$JAR" && test ! -L "$JAR" && test -x "$TARGET/bin/apktool" || {
  echo 'FERRARI_APKTOOL_PRIVATE_INSTALL_INVALID' >&2; exit 2;
}
printf '%s  %s\n' "$SHA256" "$JAR" | sha256sum -c -
"$TARGET/bin/apktool" --version | grep -Fx '3.0.3'
echo 'FERRARI_APKTOOL_PRIVATE_VERSION=3.0.3'
echo 'FERRARI_APKTOOL_PRIVATE_JAVA=25.0.5'
echo 'FERRARI_APKTOOL_REA_DEPENDENCY=NONE'
