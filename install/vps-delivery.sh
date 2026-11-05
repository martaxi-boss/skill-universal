#!/usr/bin/env bash
# Historical global-APT installer is disabled. It must never touch the VPS.
# Deploy private packages only through a separately tested Ferrari-owned release.
set -Eeuo pipefail
echo FERRARI_VPS_INSTALL=BLOCKED_LEGACY_GLOBAL_APT >&2
echo 'Project programs and dependencies belong in /srv/projects/skill-universal/' >&2
exit 4
