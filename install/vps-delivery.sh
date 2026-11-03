#!/usr/bin/env bash
# Ferrari operational installation runs ON the Ubuntu VPS, never in the SSH bridge.
# Input: one source SHA. File source.tar.gz must have been copied by trusted GitHub Actions.
set -Eeuo pipefail
umask 077
if [[ $# -ne 1 || ! "$1" =~ ^[0-9a-f]{40}$ ]]; then
  echo 'FERRARI_INVALID_RELEASE_SHA' >&2; exit 2
fi
SHA="$1"
ROOT="$HOME/.local/share/motor-ferrari"
RELEASE="$ROOT/releases/$SHA"
test -d "$RELEASE" && test -f "$RELEASE/source.tar.gz" || {
  echo 'FERRARI_RELEASE_PACKAGE_MISSING' >&2; exit 2;
}
cd "$RELEASE"
test ! -e "engine/ferrari.py" || { echo 'FERRARI_RELEASE_NOT_FRESH' >&2; exit 2; }
tar -xzf source.tar.gz
rm source.tar.gz
test -f "engine/ferrari.py" && test -f "install/ferrari-ubuntu.sh" || {
  echo 'FERRARI_RELEASE_INCOMPLETE' >&2; exit 2;
}
echo "FERRARI_RELEASE_SHA=$SHA"
bash install/vps-preflight.sh
python3 -m compileall -q engine integrations
python3 -m engine.ferrari doctor
bash install/ferrari-ubuntu.sh --profile maximum --headless

# Protect existing apps: user-home project, no global Node, no daemon packages.
if [[ "$(id -u)" -eq 0 ]]; then
  echo 'FERRARI_DEPLOY_ROOT_USER_NOT_ALLOWED' >&2; exit 2
fi
if ! sudo -n true >/dev/null 2>&1; then
  echo 'FERRARI_APT_BLOCKED_NO_NONINTERACTIVE_SUDO' >&2; exit 3
fi
FREE_KIB="$(df -Pk "$HOME" | awk 'END{print $4}')"
if (( FREE_KIB < 6291456 )); then
  echo "FERRARI_APT_BLOCKED_DISK_BELOW_6GIB free_KiB=$FREE_KIB" >&2
  exit 3
fi
echo 'FERRARI_APT_STAGE=BEGIN'
sudo -n bash install/ferrari-ubuntu.sh --profile maximum --headless --apply
echo 'FERRARI_APT_STAGE=COMPLETED'

# Explicitly requested Ferrari expansion: 15 Ubuntu GUI applications and
# Ferrari-private Prometheus/Valkey binaries. No server is started here.
bash install/vps-expand-services-gui.sh

# Execute real local operations, not just binary --help probes.
python3 -m unittest discover -s tests -v
python3 -m engine.ferrari run --operation web-template --title "Ferrari Ubuntu VPS real" --output "$RELEASE/smoke/site"
python3 -m engine.ferrari run --operation svg-poster --title "Ferrari Ubuntu smoke" --output "$RELEASE/smoke/poster"
python3 -m engine.orchestrator --plan examples/ferrari-workflow.json --workspace "$RELEASE/smoke/orchestrator" --execute --max-parallel 2

for bin in git ffmpeg pdftotext tesseract strings; do
  command -v "$bin" >/dev/null || { echo "FERRARI_EXECUTOR_MISSING=$bin" >&2; exit 4; }
done
python3 -m engine.ferrari doctor

ln -sfn "$RELEASE" "$ROOT/current.next"
mv -Tf "$ROOT/current.next" "$ROOT/current"
echo "FERRARI_CURRENT_RELEASE=$SHA"
echo 'FERRARI_VPS_INSTALL=PASS_APT_HEADLESS_AND_REAL_WORKFLOW'
echo 'FERRARI_REA_RUFLO_GHIDRA_JADX=NOT_INSTALLED_OR_CERTIFIED_BY_THIS_STAGE'
