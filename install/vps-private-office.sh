#!/usr/bin/env bash
# Ferrari-only OFFLINE LibreOffice relocation from the already-installed
# Ubuntu package. Read-only system source; all written files stay in Ferrari.
# No APT install, network, sudo, shared app files or edits to other projects.
set -Eeuo pipefail
umask 077

ROOT="/srv/projects/skill-universal"
DEST="$ROOT/tools/libreoffice"
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
for exe in timeout; do command -v "$exe" >/dev/null || exit 4; done
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


# The Ubuntu package source is read-only. The program AND application assets
# are copied, and hardcoded FHS references are changed in the private copy.
SOURCE="/usr/lib/libreoffice"
[[ -x "$SOURCE/program/soffice" && -f "$SOURCE/program/soffice.bin" ]] || {
  echo FERRARI_PRIVATE_OFFICE_LOCAL_SOURCE_MISSING >&2; exit 5;
}
mkdir -p "$WORK/test" "$WORK/test/profile" "$WORK/test/out" "$WORK/test/run"
chmod 700 "$WORK/test/run"

"$PRIVATE_PYTHON" - "$WORK/office" <<'PYCOPY'
from pathlib import Path
import hashlib
import shutil
import sys

target=Path(sys.argv[1])
sources=(
    (Path('/usr/lib/libreoffice'), target),
    (Path('/usr/share/libreoffice'), target/'share'),
    (Path('/etc/libreoffice'), target/'etc'),
)
for src,dst in sources:
    if src.is_dir() and not src.is_symlink():
        shutil.copytree(src,dst,symlinks=False,
                        ignore_dangling_symlinks=True,dirs_exist_ok=True)

def patch(name,old,new):
    path=target/'program'/name
    content=path.read_text(encoding='utf-8')
    if old not in content:
        raise RuntimeError("FERRARI_PRIVATE_OFFICE_RELOCATION_PATTERN_MISSING="+name)
    path.write_text(content.replace(old,new,1),encoding='utf-8')

patch('fundamentalrc',
      'BRAND_BASE_DIR=file:///usr/lib/libreoffice',
      'BRAND_BASE_DIR=${ORIGIN}/..')
patch('sofficerc',
      'FHS_CONFIG_FILE=file:///etc/libreoffice/sofficerc',
      'FHS_CONFIG_FILE=${ORIGIN}/../etc/sofficerc')
for path in target.rglob('*'):
    if path.is_symlink():
        raise RuntimeError("FERRARI_PRIVATE_OFFICE_EXTERNAL_SYMLINK="+str(path))
program=target/'program/soffice.bin'
original=Path('/usr/lib/libreoffice/program/soffice.bin')
if not program.is_file() or program.stat().st_size<1024:
    raise RuntimeError("FERRARI_PRIVATE_OFFICE_CORE_MISSING")
digest=hashlib.sha256(program.read_bytes()).hexdigest()
if digest != hashlib.sha256(original.read_bytes()).hexdigest():
    raise RuntimeError("FERRARI_PRIVATE_OFFICE_SOURCE_MISMATCH")
(target/'source.txt').write_text(
    'Origin: existing Ubuntu LibreOffice package (read-only, local copy)\\n'
    'System app files modified: NO\\n'
    'Project destination: /srv/projects/skill-universal/tools/libreoffice\\n'
    'SHA256 copied soffice.bin: '+digest+'\\n'
    'Bootstrap: project-relative (no /usr/lib/libreoffice or /etc/libreoffice)\\n'
    'Vendor signature: not verified by this local-copy script\\n',
    encoding='utf-8')
print("FERRARI_PRIVATE_OFFICE_LOCAL_COPY=PASS")
PYCOPY

export HOME="$WORK/test"
export XDG_CONFIG_HOME="$WORK/test/config"
export XDG_CACHE_HOME="$WORK/test/cache"
export XDG_DATA_HOME="$WORK/test/data"
export TMPDIR="$WORK/test"
export SAL_USE_VCLPLUGIN=svp
export QT_QPA_PLATFORM=offscreen
export XDG_RUNTIME_DIR="$WORK/test/run"

VERSION="$(timeout 90 "$WORK/office/program/soffice" --version)"
printf 'FERRARI_PRIVATE_OFFICE_VERSION=%s\n' "$VERSION"
[[ "$VERSION" == LibreOffice\ * ]] || {
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
# The staged local copy is activated inside Ferrari after its PDF test.
[[ ! -e "$DEST" && ! -L "$DEST" ]] || { echo FERRARI_OFFICE_DEST_RACE >&2; exit 8; }
mv -- "$WORK/office" "$DEST"
[[ -x "$DEST/program/soffice" ]] || exit 8
echo FERRARI_PRIVATE_OFFICE_INSTALL=PASS
