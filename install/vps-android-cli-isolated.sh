#!/usr/bin/env bash
# Install just four Android CLI tools in Ferrari; no system packages or shared SDK runtime.
set -Eeuo pipefail
ROOT="/srv/projects/skill-universal"
SDK="/srv/projects/android-sdk"
TARGET="$ROOT/tools/android-cli-36.0.0"
test "$(uname -s)" = Linux && test "$(uname -m)" = x86_64
grep -q '^ID=ubuntu$' /etc/os-release
test -d "$ROOT" && test ! -L "$ROOT"
test "$(realpath -e "$ROOT")" = "$ROOT"
test -d "$SDK" && test ! -L "$SDK"
test -f "$ROOT/runtimes/jdk-25.0.5_8/bin/java"
test -d "$ROOT/tools" && test ! -L "$ROOT/tools"
test ! -L "$TARGET"

FILES=(
  "build-tools/36.0.0/aapt2"
  "build-tools/36.0.0/zipalign"
  "build-tools/36.0.0/lib/apksigner.jar"
  "build-tools/36.0.0/lib64/libc++.so"
  "platform-tools/adb"
)
verify() {
  local dir="$1" rel
  test -d "$dir" && test ! -L "$dir"
  for rel in "${FILES[@]}"; do
    test -f "$dir/$rel" && test ! -L "$dir/$rel"
    test -f "$SDK/$rel" && test ! -L "$SDK/$rel"
    cmp -s "$SDK/$rel" "$dir/$rel"
  done
  test -f "$dir/build-tools/36.0.0/apksigner"
  test -x "$dir/build-tools/36.0.0/aapt2"
  test -x "$dir/build-tools/36.0.0/zipalign"
  test -x "$dir/build-tools/36.0.0/apksigner"
  test -x "$dir/platform-tools/adb"
}
if test -d "$TARGET"; then
  verify "$TARGET"
  echo "FERRARI_ANDROID_CLI_IDEMPOTENT=PASS"
  exit 0
fi
test ! -e "$TARGET"
STAGE="$(mktemp -d "$ROOT/tools/.android-cli-stage.XXXXXXXX")"
cleanup(){ if test -d "$STAGE"; then rm -rf -- "$STAGE"; fi; }
trap cleanup EXIT
for rel in "${FILES[@]}"; do
  source_file="$SDK/$rel"
  test -f "$source_file" && test ! -L "$source_file"
  mkdir -p "$STAGE/$(dirname "$rel")"
  cp -p -- "$source_file" "$STAGE/$rel"
  cmp -s "$source_file" "$STAGE/$rel"
done
cat > "$STAGE/build-tools/36.0.0/apksigner" <<'LAUNCH'
#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="/srv/projects/skill-universal"
TOOL="$ROOT/tools/android-cli-36.0.0"
STATE="$ROOT/.runtime/android-cli"
JAVA="$ROOT/runtimes/jdk-25.0.5_8/bin/java"
JAR="$TOOL/build-tools/36.0.0/lib/apksigner.jar"
test -x "$JAVA" && test -f "$JAR"
for part in home tmp cache config data; do mkdir -p "$STATE/$part"; done
export HOME="$STATE/home" TMPDIR="$STATE/tmp"
export XDG_CACHE_HOME="$STATE/cache" XDG_CONFIG_HOME="$STATE/config" XDG_DATA_HOME="$STATE/data"
exec "$JAVA" "-Duser.home=$STATE/home" -jar "$JAR" "$@"
LAUNCH
chmod 750 "$STAGE/build-tools/36.0.0/apksigner"
chmod 750 "$STAGE/build-tools/36.0.0/aapt2" "$STAGE/build-tools/36.0.0/zipalign" "$STAGE/platform-tools/adb"
chown -R --reference="$ROOT" "$STAGE"
verify "$STAGE"
for binary in "$STAGE/build-tools/36.0.0/aapt2" "$STAGE/build-tools/36.0.0/zipalign" "$STAGE/platform-tools/adb"; do
  if ldd "$binary" 2>&1 | grep -F 'not found'; then
    echo "FERRARI_ANDROID_LINUX_DEPENDENCY_MISSING=$binary" >&2
    exit 3
  fi
done
ldd "$STAGE/build-tools/36.0.0/zipalign" | grep -F "$STAGE/build-tools/36.0.0/lib64/libc++.so" >/dev/null
mv -- "$STAGE" "$TARGET"
trap - EXIT
test ! -L "$TARGET"
for rel in "${FILES[@]}"; do cmp -s "$SDK/$rel" "$TARGET/$rel"; done
"$TARGET/build-tools/36.0.0/aapt2" version
"$TARGET/platform-tools/adb" version
"$TARGET/build-tools/36.0.0/apksigner" --version
echo "FERRARI_ANDROID_LINUX_PRIVATE=PASS"
echo "FERRARI_ANDROID_NO_GLOBAL_INSTALL=PASS"
echo "FERRARI_ANDROID_FOUR_TOOLS_ONLY=PASS"
