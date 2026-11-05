#!/usr/bin/env bash
# Ferrari-only LibreOffice Standard AppImage, from the LibreOffice-endorsed
# LibreItalia distribution. No apt install, snap, sudo, global writes, or
# dependency sharing with another project.
set -Eeuo pipefail
umask 077

ROOT="/srv/projects/skill-universal"
DEST="$ROOT/tools/libreoffice"
URL="https://appimages.libreitalia.org/LibreOffice-previous.standard-x86_64.AppImage"
. /etc/os-release
[[ "${ID:-}" == ubuntu && "${VERSION_ID:-}" == 24.04 && "$(uname -m)" == x86_64 ]] || {
  echo FERRARI_PRIVATE_OFFICE_UNSUPPORTED_PLATFORM >&2; exit 2;
}
[[ $(id -u) -ne 0 && -d "$ROOT" && ! -L "$ROOT" && -d "$ROOT/tools" && ! -L "$ROOT/tools" ]] || {
  echo FERRARI_PRIVATE_OFFICE_PROJECT_INVALID >&2; exit 2;
}
[[ "$(stat -c %u "$ROOT")" == "$(id -u)" ]] || {
  echo FERRARI_PRIVATE_OFFICE_OWNER_INVALID >&2; exit 2;
}
[[ -d "$ROOT/.runtime" && ! -L "$ROOT/.runtime" ]] || {
  echo FERRARI_PRIVATE_OFFICE_RUNTIME_INVALID >&2; exit 2;
}
if [[ -e "$DEST" || -L "$DEST" ]]; then
  if [[ ! -L "$DEST" && -x "$DEST/program/soffice" ]]; then
    echo FERRARI_PRIVATE_OFFICE_ALREADY_PRESENT
    "$DEST/program/soffice" --version
    exit 0
  fi
  echo FERRARI_PRIVATE_OFFICE_EXISTING_CONFLICT >&2
  exit 3
fi
[[ "$(df -Pk "$ROOT" | awk 'END{print $4}')" -ge 3145728 ]] || {
  echo FERRARI_PRIVATE_OFFICE_DISK_BELOW_3GIB >&2; exit 3;
}
for exe in curl sha256sum timeout; do command -v "$exe" >/dev/null || exit 4; done
PRIVATE_PYTHON="$ROOT/runtimes/python3.12/bin/python3.12"
[[ -x "$PRIVATE_PYTHON" ]] || { echo FERRARI_PRIVATE_OFFICE_PYTHON_MISSING >&2; exit 4; }

WORK="$(mktemp -d "$ROOT/.runtime/.private-office-20261105.XXXXXXXX")"
cleanup() {
  case "$WORK" in "$ROOT"/.runtime/.private-office-20261105.*)
    if [[ -d "$WORK" && ! -L "$WORK" ]]; then rm -rf -- "$WORK"; fi
    ;;
  esac
}
trap cleanup EXIT

mkdir -p "$WORK/office/program" "$WORK/test" "$WORK/test/profile" "$WORK/test/out"
APPIMAGE="$WORK/office/LibreOffice-previous.standard-x86_64.AppImage"
curl --fail --silent --show-error --location --proto '=https' --proto-redir '=https' \
  --retry 2 --connect-timeout 20 --max-time 1500 "$URL" -o "$APPIMAGE"
[[ -s "$APPIMAGE" ]] || { echo FERRARI_PRIVATE_OFFICE_DOWNLOAD_EMPTY >&2; exit 5; }
HASH="$(sha256sum "$APPIMAGE" | awk '{print $1}')"
[[ "$HASH" =~ ^[a-f0-9]{64}$ ]] || exit 5
chmod 700 "$APPIMAGE"
(
  cd "$WORK/office"
  timeout 180 "$APPIMAGE" --appimage-extract > "$WORK/extract.log"
)
[[ -x "$WORK/office/squashfs-root/AppRun" ]] || {
  echo FERRARI_PRIVATE_OFFICE_EXTRACTION_FAILED >&2; exit 6;
}
"$PRIVATE_PYTHON" - "$WORK/office/squashfs-root" <<'PYLINKS'
from pathlib import Path
import sys
root=Path(sys.argv[1]).resolve(strict=True)
for candidate in root.rglob('*'):
    if candidate.is_symlink() and not candidate.resolve(strict=False).is_relative_to(root):
        raise RuntimeError("FERRARI_PRIVATE_OFFICE_EXTERNAL_SYMLINK")
PYLINKS

cat > "$WORK/office/program/soffice" <<'WRAPPER'
#!/usr/bin/env bash
set -Eeuo pipefail
PREFIX="$(cd "$(dirname "$0")/.." && pwd -P)"
[[ "$PREFIX" == "/srv/projects/skill-universal/tools/libreoffice" ]] || {
  # During installation, this wrapper is tested inside Ferrari .runtime.
  [[ "$PREFIX" == /srv/projects/skill-universal/.runtime/.private-office-20261105.*/office ]] || exit 3
}
exec "$PREFIX/squashfs-root/AppRun" "$@"
WRAPPER
chmod 700 "$WORK/office/program/soffice"
export HOME="$WORK/test"
export XDG_CONFIG_HOME="$WORK/test/config"
export XDG_CACHE_HOME="$WORK/test/cache"
export XDG_DATA_HOME="$WORK/test/data"
export TMPDIR="$WORK/test"
export SAL_USE_VCLPLUGIN=gen
export QT_QPA_PLATFORM=offscreen

VERSION="$(timeout 90 "$WORK/office/program/soffice" --version)"
printf 'FERRARI_PRIVATE_OFFICE_VERSION=%s\n' "$VERSION"
[[ "$VERSION" == *"LibreOffice 26.2."* ]] || {
  echo FERRARI_PRIVATE_OFFICE_UNEXPECTED_VERSION >&2; exit 7;
}
"$PRIVATE_PYTHON" - "$WORK/test/demo.docx" <<'PYDOCX'
import sys,zipfile
p=sys.argv[1]
content='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''
rels='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>'''
doc='''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body><w:p><w:r><w:t>Ferrari LibreOffice privado</w:t></w:r></w:p></w:body></w:document>'''
with zipfile.ZipFile(p,'w',compression=zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml',content)
    z.writestr('_rels/.rels',rels)
    z.writestr('word/document.xml',doc)
PYDOCX
timeout 240 "$WORK/office/program/soffice" --headless \
  "-env:UserInstallation=file://$WORK/test/profile" \
  --convert-to pdf --outdir "$WORK/test/out" "$WORK/test/demo.docx"
"$PRIVATE_PYTHON" - "$WORK/test/out/demo.pdf" <<'PYPDF'
from pathlib import Path
import sys
p=Path(sys.argv[1])
assert p.is_file() and not p.is_symlink() and p.stat().st_size>1000, "FERRARI_OFFICE_PDF_MISSING"
with p.open("rb") as f:
    assert f.read(5)==b"%PDF-", "FERRARI_OFFICE_PDF_INVALID"
print("FERRARI_PRIVATE_OFFICE_PDF_TEST=PASS")
PYPDF
cat > "$WORK/office/source.txt" <<EOF
Origin: The Document Foundation endorsed LibreItalia AppImage (Standard)
Source URL: $URL
Retrieved UTC: $(date -u +%FT%TZ)
SHA256: $HASH
Verification scope: HTTPS source plus local SHA256 inventory; vendor signature not verified
Test: headless DOCX to PDF performed successfully before activation
EOF
# Drop the downloaded archive; keep only the extracted application and its
# launcher inside the project. No temporary files or profiles outside Ferrari.
rm -f -- "$APPIMAGE"
[[ ! -e "$DEST" && ! -L "$DEST" ]] || { echo FERRARI_OFFICE_DEST_RACE >&2; exit 8; }
mv -- "$WORK/office" "$DEST"
[[ -x "$DEST/program/soffice" ]] || exit 8
echo FERRARI_PRIVATE_OFFICE_INSTALL=PASS
