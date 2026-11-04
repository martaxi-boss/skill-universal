#!/usr/bin/env bash
# Run on Ferrari Ubuntu VPS after deployment. Real multi-domain work, not help-only.
set -Eeuo pipefail
umask 077
cd "$(dirname "$0")/.."
ROOT="/srv/projects/skill-universal"
mkdir -p "$ROOT/.runtime"
WORK="$(mktemp -d "$ROOT/.runtime/tool-smoke.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT

python3 -m engine.ferrari tools > "$WORK/catalogue.json"
python3 - "$WORK/catalogue.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
assert x["selected"]==56
assert x["registered_actions"]==36
assert x["callable_actions"]>=36
for name in ("pandoc","graphviz","jq","ffmpeg","imagemagick","tesseract","libvips","ripgrep","ansible","wireshark","objdump","strings","pdftotext"):
    p=next(z for z in x["programs"] if z["id"]==name)
    assert p["installed"] and p["actions"],name
print("FERRARI_UNIVERSAL_INVENTORY=PASS")
print("FERRARI_UNIVERSAL_ACTIONS_AVAILABLE="+str(x["callable_actions"]))
print("FERRARI_UNIVERSAL_PROGRAMS_DETECTED="+str(x["installed"]))
print("FERRARI_SELECTION_DETECTED="+str(x["selected_detected"]))
print("FERRARI_SELECTION_NOT_DETECTED="+str(x["selected_not_detected"]))
print("FERRARI_SELECTION_MISSING_BY_TIER="+json.dumps(x["missing_by_tier"],sort_keys=True))
assert next(z for z in x["programs"] if z["id"]=="blender")["base_operations"]==["blender-house"]
PY

APKTOOL="$ROOT/tools/apktool-3.0.3/bin/apktool"
test -x "$APKTOOL"
test "$("$APKTOOL" --version)" = "3.0.3"
test -d "$ROOT/.runtime/apktool-frameworks"
test ! -L "$APKTOOL"
echo 'FERRARI_APKTOOL_PRIVATE_RUNTIME=PASS'
# Build a minimal, synthetic APK with the Ferrari-private Apktool 3.0.3, then
# decode it through Ferrari's existing typed tool dispatcher. No external app
# or Android device and no access to other project repositories.
mkdir -p "$WORK/ferrari-apk-src/res/values" "$WORK/ferrari-apk-src/smali/com/ferrari"
cat > "$WORK/ferrari-apk-src/AndroidManifest.xml" <<'APKM'
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.ferrari.smoke" android:versionCode="1" android:versionName="1.0">
    <uses-sdk android:minSdkVersion="21" android:targetSdkVersion="28"/>
    <application android:label="@string/app_name"/>
</manifest>
APKM
cat > "$WORK/ferrari-apk-src/res/values/strings.xml" <<'APKR'
<?xml version="1.0" encoding="utf-8"?>
<resources><string name="app_name">Ferrari APK Smoke</string></resources>
APKR
cat > "$WORK/ferrari-apk-src/smali/com/ferrari/Smoke.smali" <<'APKS'
.class public Lcom/ferrari/Smoke;
.super Ljava/lang/Object;
.source "Smoke.java"

.method public static status()Ljava/lang/String;
    .locals 1
    const-string v0, "Ferrari APK Smoke"
    return-object v0
.end method
APKS
cat > "$WORK/ferrari-apk-src/apktool.yml" <<'APKY'
version: 3.0.3
apkFileName: ferrari-sample.apk
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
if ! "$APKTOOL" b "$WORK/ferrari-apk-src" -o "$WORK/ferrari-sample.apk" > "$WORK/apktool-build.log" 2>&1; then
  echo 'FERRARI_APKTOOL_FIXTURE_BUILD_FAILED' >&2
  tail -n 60 "$WORK/apktool-build.log" >&2
  exit 5
fi
test -s "$WORK/ferrari-sample.apk"
python3 -m engine.ferrari invoke --action apktool-decode-resources \
  --input "$WORK/ferrari-sample.apk" --output "$WORK/apktool-decode" > "$WORK/apktool-result.json"
test -s "$WORK/apktool-decode/apktool-decoded/AndroidManifest.xml"
test -s "$WORK/apktool-decode/apktool-decoded/apktool.yml"
grep -q 'com.ferrari.smoke' "$WORK/apktool-decode/apktool-decoded/AndroidManifest.xml"
grep -q 'Ferrari APK Smoke' "$WORK/apktool-decode/apktool-decoded/res/values/strings.xml"
grep -q 'Ferrari APK Smoke' "$WORK/apktool-decode/apktool-decoded/smali/com/ferrari/Smoke.smali"
echo 'FERRARI_APKTOOL_REAL=PASS'

# Exercise REA 6.8.0 from Ferrari's private npm tree, never from global PATH
# or the legacy Engineering Reversa project. These are real REA analyses.
python3 -m engine.ferrari invoke --action rea-elf-notes \
  --input /usr/bin/true --output "$WORK/rea-elf" > "$WORK/rea-elf-run.json"
python3 -m engine.ferrari invoke --action rea-android-resources \
  --input "$WORK/ferrari-sample.apk" --output "$WORK/rea-apk" > "$WORK/rea-apk-run.json"
python3 - "$WORK" <<'REA_CHECK'
import json,sys
from pathlib import Path
p=Path(sys.argv[1])
elf=json.loads((p/"rea-elf/rea-elf-notes.json").read_text())
apk=json.loads((p/"rea-apk/rea-android-resources.json").read_text())
assert isinstance(elf,dict) and isinstance(apk,dict)
assert elf.get("ok") is not False and apk.get("ok") is not False
elf_text=json.dumps(elf,ensure_ascii=False)
apk_text=json.dumps(apk,ensure_ascii=False)
assert "sha256" in elf_text.lower() and ("table" in elf_text.lower() or "notes" in elf_text.lower())
assert "com.ferrari.smoke" in apk_text or "Ferrari APK Smoke" in apk_text, apk_text[:1000]
for fn in ("rea-elf-run.json","rea-apk-run.json"):
    outcome=json.loads((p/fn).read_text())
    assert outcome["confirmed"] and "/srv/projects/skill-universal/" in outcome["executor"]
print("FERRARI_PRIVATE_REA_ELF_REAL=PASS")
print("FERRARI_PRIVATE_REA_ANDROID_REAL=PASS")
REA_CHECK


printf 'digraph Ferrari { Chat -> Motor -> Ubuntu; }\n' > "$WORK/demo.dot"
printf '# Ferrari\n\nOperacao Ubuntu com ferramenta externa real.\n' > "$WORK/demo.md"
printf '{"ferrari":"ubuntu","routed":true}\n' > "$WORK/demo.json"

python3 -m engine.ferrari route "Converter markdown para docx" --input "$WORK/demo.md" > "$WORK/route.json"
python3 -m engine.ferrari auto "Converter markdown para docx" --input "$WORK/demo.md" --output "$WORK/auto-office" --execute > "$WORK/auto-result.json"
python3 -m engine.ferrari invoke --action graphviz-dot-svg --input "$WORK/demo.dot" --output "$WORK/diagram"
python3 -m engine.ferrari invoke --action pandoc-md-docx --input "$WORK/demo.md" --output "$WORK/office"
python3 -m engine.ferrari invoke --action jq-format-json --input "$WORK/demo.json" --output "$WORK/data"
python3 -m engine.ferrari invoke --action file-mime --input "$WORK/demo.json" --output "$WORK/file"

# Real, local multi-domain tests for newly linked executors.
printf 'Ferrari capaz de pesquisar texto numa amostra.\nFerrari Ubuntu.\n' > "$WORK/ferrari.txt"
python3 -m engine.ferrari invoke --action ripgrep-find-text --input "$WORK/ferrari.txt" --query Ferrari --output "$WORK/search"
python3 -m engine.ferrari invoke --action strings-file-extract --input "$WORK/ferrari.txt" --output "$WORK/strings"
python3 -m engine.ferrari invoke --action objdump-file-header --input /usr/bin/true --output "$WORK/objdump"
printf '[ferrari]\nlocalhost ansible_connection=local\n' > "$WORK/hosts.ini"
python3 -m engine.ferrari invoke --action ansible-inventory-json --input "$WORK/hosts.ini" --output "$WORK/ansible"

convert -size 80x50 xc:blue "$WORK/image.png"
python3 -m engine.ferrari invoke --action vips-image-thumbnail --input "$WORK/image.png" --output "$WORK/vips-thumb"
python3 -m engine.ferrari invoke --action vips-image-inspect --input "$WORK/image.png" --output "$WORK/vips-inspect"
python3 -m engine.ferrari invoke --action imagemagick-webp --input "$WORK/image.png" --output "$WORK/webp"
python3 -m engine.ferrari run --operation office-pdf --input "$WORK/office/document.docx" --output "$WORK/pdf"
python3 -m engine.ferrari invoke --action pdftotext-layout --input "$WORK/pdf/document.pdf" --output "$WORK/pdftext"

# Existing local OCRmyPDF becomes a callable Ferrari action. The source is a
# deliberately IMAGE-ONLY PDF; Tesseract must create real searchable text.
convert -size 950x150 xc:white -font DejaVu-Sans -fill black -pointsize 58 \
  -gravity center -annotate +0+0 'FERRARI OCR 2026' "$WORK/ocr-scan.png"
printf '![](ocr-scan.png)\n' > "$WORK/ocr-scan.md"
pandoc --resource-path="$WORK" -f markdown -t docx \
  "$WORK/ocr-scan.md" -o "$WORK/ocr-scan.docx"
python3 -m engine.ferrari run --operation office-pdf \
  --input "$WORK/ocr-scan.docx" --output "$WORK/ocr-source-pdf"
scan_pdf="$(find "$WORK/ocr-source-pdf" -type f -name '*.pdf' -print -quit)"
test -n "$scan_pdf" && test -s "$scan_pdf"
pdftotext "$scan_pdf" "$WORK/before-ocr.txt"
if grep -qi 'FERRARI' "$WORK/before-ocr.txt"; then
  echo 'FERRARI_OCR_INPUT_NOT_IMAGE_ONLY' >&2; exit 5
fi
python3 -m engine.ferrari invoke --action ocrmypdf-searchable-pdf \
  --input "$scan_pdf" --output "$WORK/ocr-result"
test -s "$WORK/ocr-result/searchable.pdf"
pdftotext "$WORK/ocr-result/searchable.pdf" "$WORK/after-ocr.txt"
grep -qi 'FERRARI' "$WORK/after-ocr.txt"
grep -q '2026' "$WORK/after-ocr.txt"
echo 'FERRARI_OCRMYPDF_REAL=PASS'


python3 - "$WORK/capture.pcap" <<'PY'
import struct,sys
eth=bytes.fromhex("ffffffffffff0011223344550800")
ip=bytes.fromhex("4500001e00010000401100007f0000017f000001")
udp=struct.pack("!HHHH",2222,3333,10,0)
packet=eth+ip+udp+b"OK"
with open(sys.argv[1],"wb") as f:
    f.write(struct.pack("<IHHIIII",0xa1b2c3d4,2,4,0,0,65535,1))
    f.write(struct.pack("<IIII",1,0,len(packet),len(packet)))
    f.write(packet)
PY
python3 -m engine.ferrari invoke --action tshark-pcap-summary --input "$WORK/capture.pcap" --output "$WORK/tshark"

cat > "$WORK/workflow.json" <<EOF
{"version":1,"steps":[
{"id":"diagram","operation":"tool","tool":"graphviz","action":"graphviz-dot-svg","input":"$WORK/demo.dot"},
{"id":"office","operation":"tool","tool":"pandoc","action":"pandoc-md-docx","input":"$WORK/demo.md"},
{"id":"json","operation":"tool","tool":"jq","action":"jq-format-json","input":"$WORK/demo.json"}
]}
EOF
python3 -m engine.orchestrator --plan "$WORK/workflow.json" --workspace "$WORK/workflow" --execute --max-parallel 2 > "$WORK/flow-result.json"

python3 - "$WORK" <<'PY'
import json,sys,zipfile
from pathlib import Path
p=Path(sys.argv[1])
assert "<svg" in (p/"diagram/diagram.svg").read_text()
assert zipfile.is_zipfile(p/"auto-office/document.docx")
assert json.loads((p/"auto-result.json").read_text())["status"]=="completed"
assert zipfile.is_zipfile(p/"office/document.docx")
assert json.loads((p/"data/formatted.json").read_text())["routed"]
assert "json" in (p/"file/mime.txt").read_text()
assert "Ferrari" in (p/"search/matches.txt").read_text()
assert "Ferrari" in (p/"strings/strings.txt").read_text()
assert "file format" in (p/"objdump/object-header.txt").read_text()
assert "ferrari" in (p/"ansible/hosts.json").read_text()
assert (p/"vips-thumb/thumbnail.png").stat().st_size>40
assert "80x50" in (p/"vips-inspect/image-header.txt").read_text() or "80 x 50" in (p/"vips-inspect/image-header.txt").read_text()
assert (p/"webp/converted.webp").stat().st_size>30
assert "Ferrari" in (p/"pdftext/extracted.txt").read_text()
assert (p/"tshark/traffic-summary.txt").stat().st_size>20
print("FERRARI_EXTENDED_PROGRAMS_REAL=PASS")
assert json.loads((p/"route.json").read_text())["suggestions"][0]["action"]=="pandoc-md-docx"
result=json.loads((p/"flow-result.json").read_text())["result"]
assert result["status"]=="completed"
assert len(result["completed"])==3
print("FERRARI_UNIVERSAL_AUTO_EXECUTION=PASS")
print("FERRARI_UNIVERSAL_ROUTING=PASS")
print("FERRARI_UNIVERSAL_REAL_MULTI_PROGRAM_EXECUTION=PASS")
print("FERRARI_UNIVERSAL_ORCHESTRATOR=PASS")
PY

# CAD/BIM and development web: isolated packages and real sample outputs.
bash install/vps-bim-web-smoke.sh

# Phase 1: real, synthetic data/typography/vector work through the
# existing typed Ferrari dispatcher, never through a global Python library.
cat > "$WORK/phase1.csv" <<'CSV'
country,orders,revenue
Portugal,7,142.50
Espanha,3,75.25
Franca,5,110.00
CSV
cat > "$WORK/phase1.svg" <<'SVG'
<svg xmlns="http://www.w3.org/2000/svg" width="320" height="160">
 <rect width="320" height="160" fill="#ebf8ff"/>
 <circle cx="60" cy="80" r="40" fill="#1877ab"/>
 <text x="128" y="92" font-size="27" fill="#16324c">Ferrari</text>
</svg>
SVG
cat > "$WORK/phase1.typ" <<'TYPST'
#set page(width: 12cm, height: 8cm)
#set text(size: 16pt)
= Motor Ferrari
Fase 1: Typst para PDF.
TYPST
python3 -m engine.ferrari invoke --action duckdb-csv-profile \
  --input "$WORK/phase1.csv" --output "$WORK/duckdb-csv" \
  > "$WORK/phase1-duckdb-action.json"
python3 -m engine.ferrari invoke --action polars-csv-profile \
  --input "$WORK/phase1.csv" --output "$WORK/polars-csv" \
  > "$WORK/phase1-polars-action.json"
python3 -m engine.ferrari invoke --action inkscape-svg-png \
  --input "$WORK/phase1.svg" --output "$WORK/inkscape-png" \
  > "$WORK/phase1-inkscape-action.json"
python3 -m engine.ferrari invoke --action typst-compile-pdf \
  --input "$WORK/phase1.typ" --output "$WORK/typst-pdf" \
  > "$WORK/phase1-typst-action.json"
python3 - "$WORK" <<'PY_PHASE1'
import json,sys
from pathlib import Path
root=Path(sys.argv[1])
for tool in ("duckdb","polars"):
    path=root/(tool+"-csv")/(tool+"-profile.json")
    doc=json.loads(path.read_text())
    assert doc["status"]=="completed",doc
    assert doc["executor"]==tool,doc
    assert doc["rows"]==3,doc
    assert [c["name"] for c in doc["columns"]]==["country","orders","revenue"],doc
    assert len(doc["sample"])==3 and doc["sample"][0]["country"]=="Portugal",doc
    assert doc.get("library_version"),doc
    if tool=="duckdb":
        print("FERRARI_DUCKDB_CSV_REAL=PASS")
    else:
        print("FERRARI_POLARS_CSV_REAL=PASS")
png=root/"inkscape-png/inkscape.png"
assert png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n") and png.stat().st_size>100,png
print("FERRARI_INKSCAPE_SVG_PNG_REAL=PASS")
pdf=root/"typst-pdf/typst-document.pdf"
assert pdf.read_bytes().startswith(b"%PDF-") and pdf.stat().st_size>100,pdf
print("FERRARI_TYPST_PDF_REAL=PASS")
print("FERRARI_DATA_DESIGN_FOUR_PROGRAMS_REAL=PASS")
PY_PHASE1

# Phase 2 - three distinct CLI paths provided by installed publishing apps.
# Synthetic assets only, no user projects, no external network or GUI session.
printf '# Ferrari\n\nPublicacao de teste independente.\n' > "$WORK/phase2-book.md"
convert -size 160x100 xc:lightblue -fill navy -draw 'rectangle 16,16 110,80' \
  "$WORK/phase2-photo.jpg"

# Diagnose all three real applications even if one is unavailable.
# Fail the deployment after collecting errors; never claim a partial PASS.
phase2_failed=0
if ! python3 -m engine.ferrari invoke --action calibre-md-epub \
  --input "$WORK/phase2-book.md" --output "$WORK/calibre-epub" \
  > "$WORK/phase2-calibre-action.json"; then
  echo 'FERRARI_PHASE2_CALIBRE_EXECUTION=FAIL' >&2
  phase2_failed=1
fi
if ! python3 -m engine.ferrari invoke --action darktable-jpeg-tiff \
  --input "$WORK/phase2-photo.jpg" --output "$WORK/darktable-tiff" \
  > "$WORK/phase2-darktable-action.json"; then
  echo 'FERRARI_PHASE2_DARKTABLE_EXECUTION=FAIL' >&2
  phase2_failed=1
fi
if ! python3 -m engine.ferrari invoke --action krita-image-png \
  --input "$WORK/phase2-photo.jpg" --output "$WORK/krita-png" \
  > "$WORK/phase2-krita-action.json"; then
  echo 'FERRARI_PHASE2_KRITA_EXECUTION=FAIL' >&2
  phase2_failed=1
fi
if ((phase2_failed)); then
  # Preserve trustworthy evidence from successful commands even when the
  # remaining GUI-based application fails on an Ubuntu server without X.
  python3 - "$WORK" <<'PY_PHASE2_PARTIAL'
import sys,zipfile
from pathlib import Path
root=Path(sys.argv[1])
epub=root/"calibre-epub/calibre-book.epub"
try:
    with zipfile.ZipFile(epub) as z:
        assert z.read("mimetype")==b"application/epub+zip"
    print("FERRARI_CALIBRE_MD_EPUB_REAL=PASS")
except (OSError,KeyError,AssertionError,zipfile.BadZipFile):
    print("FERRARI_CALIBRE_MD_EPUB_REAL=NOT_CERTIFIED")
tiff=root/"darktable-tiff/darktable-export.tif"
try:
    assert tiff.stat().st_size>100
    with tiff.open("rb") as f: assert f.read(4) in (b"II*\x00",b"MM\x00*")
    print("FERRARI_DARKTABLE_JPEG_TIFF_REAL=PASS")
except (OSError,AssertionError):
    print("FERRARI_DARKTABLE_JPEG_TIFF_REAL=NOT_CERTIFIED")
PY_PHASE2_PARTIAL
  echo 'FERRARI_PHASE2_APPLICATIONS_NOT_CERTIFIED' >&2
  exit 7
fi

python3 - "$WORK" <<'PY_PHASE2'
import json,sys,zipfile
from pathlib import Path
root=Path(sys.argv[1])
epub=root/"calibre-epub/calibre-book.epub"
assert zipfile.is_zipfile(epub) and epub.stat().st_size>200,epub
with zipfile.ZipFile(epub) as z:
    assert "mimetype" in z.namelist() and z.read("mimetype")==b"application/epub+zip"
print("FERRARI_CALIBRE_MD_EPUB_REAL=PASS")
tiff=root/"darktable-tiff/darktable-export.tif"
assert tiff.stat().st_size>100 and tiff.read_bytes()[:4] in (b"II*\x00",b"MM\x00*"),tiff
print("FERRARI_DARKTABLE_JPEG_TIFF_REAL=PASS")
png=root/"krita-png/krita-export.png"
assert png.stat().st_size>100 and png.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"),png
print("FERRARI_KRITA_JPEG_PNG_REAL=PASS")
for tool in ("calibre","darktable","krita"):
    report=json.loads((root/("phase2-"+tool+"-action.json")).read_text())
    assert report.get("confirmed") is True and report["tool"]==tool,report
print("FERRARI_PHASE2_PUBLISHING_THREE_REAL=PASS")
PY_PHASE2

# Phase 2 GIMP: independent, noninteractive editable output via the Ferrari
# dispatcher; no changes to system settings or other project workspaces.
convert -size 140x90 xc:'#c2deed' -fill '#2f5870' \
  -draw 'rectangle 18,20 98,71' "$WORK/phase2-gimp.png"
python3 -m engine.ferrari invoke --action gimp-png-xcf \
  --input "$WORK/phase2-gimp.png" --output "$WORK/gimp-xcf" \
  > "$WORK/phase2-gimp-action.json"
python3 - "$WORK" <<'PY_GIMP'
from pathlib import Path
import json,sys
root=Path(sys.argv[1])
xcf=root/"gimp-xcf/gimp-editable.xcf"
assert xcf.is_file() and xcf.stat().st_size>256,xcf
assert xcf.read_bytes().startswith(b"gimp xcf "),xcf
report=json.loads((root/"phase2-gimp-action.json").read_text())
assert report["confirmed"] and report["tool"]=="gimp",report
print("FERRARI_GIMP_XCF_REAL=PASS")
PY_GIMP


# Phase 2 Scribus: same installed Xvfb as Krita, no desktop service.
# Create a true PDF and editable SLA, both inside the Ferrari job only.
printf 'Ferrari - Publicacao de teste\n\nScribus gera PDF e projeto editavel.\n' > "$WORK/phase2-scribus.txt"
python3 -m engine.ferrari invoke --action scribus-text-publication \
  --input "$WORK/phase2-scribus.txt" --output "$WORK/scribus-publication" \
  > "$WORK/phase2-scribus-action.json"
python3 - "$WORK" <<'PY_SCRIBUS'
from pathlib import Path
import json,sys
root=Path(sys.argv[1])
pub=root/"scribus-publication/scribus-publication"
pdf=pub/"publication.pdf"
sla=pub/"publication.sla"
assert pdf.is_file() and pdf.stat().st_size>500,pdf
assert pdf.read_bytes()[:5]==b"%PDF-",pdf
assert sla.is_file() and sla.stat().st_size>500,sla
assert b"SCRIBUS" in sla.read_bytes()[:400],sla
report=json.loads((root/"phase2-scribus-action.json").read_text())
assert report["confirmed"] and report["tool"]=="scribus",report
print("FERRARI_SCRIBUS_PDF_SLA_REAL=PASS")
PY_SCRIBUS


# Phase 3: render two original oscillator notes with already installed LMMS.
# The reference is LMMS's installed factory template, not another project.
# Create the fixture and output only under Ferrari's private test workspace.
python3 - "$WORK" <<'PY_LMMS_SOURCE'
from pathlib import Path
import xml.etree.ElementTree as ET
import sys
root=Path(sys.argv[1])
template=Path("/usr/share/lmms/projects/templates/default.mpt")
assert template.is_file(),template
document=ET.parse(template)
track=document.getroot().find(".//song/trackcontainer/track[@type='0']")
assert track is not None,"LMMS default oscillator track missing"
pattern=ET.SubElement(track,"pattern",{
    "name":"Ferrari Original Two Notes","type":"1","pos":"0",
    "len":"192","steps":"16","muted":"0"})
for pitch,at,duration in ((57,0,96),(64,96,96)):
    ET.SubElement(pattern,"note",{
        "key":str(pitch),"pos":str(at),"len":str(duration),
        "vol":"85","pan":"0"})
document.write(root/"phase3-original.mmp",encoding="utf-8",xml_declaration=True)
PY_LMMS_SOURCE
python3 -m engine.ferrari invoke --action lmms-project-wav \
  --input "$WORK/phase3-original.mmp" --output "$WORK/lmms-audio" \
  > "$WORK/phase3-lmms-action.json"
python3 - "$WORK" <<'PY_LMMS_AUDIO'
from pathlib import Path
import wave,json,sys
root=Path(sys.argv[1])
path=root/"lmms-audio/lmms-render.wav"
assert path.is_file() and path.stat().st_size>1000,path
with wave.open(str(path),"rb") as audio:
    frames=audio.getnframes()
    rate=audio.getframerate()
    channels=audio.getnchannels()
    samples=audio.readframes(min(frames,65536))
    assert frames>1000 and 8000<=rate<=192000 and channels in (1,2)
    assert samples and any(samples),"LMMS WAV is silent"
report=json.loads((root/"phase3-lmms-action.json").read_text())
assert report["confirmed"] and report["tool"]=="lmms",report
print("FERRARI_LMMS_WAV_REAL=PASS")
PY_LMMS_AUDIO

# Phase 3: the existing Kdenlive/MLT 'melt' headless renderer.
# All fixtures and outputs are confined to this Ferrari job.
cat > "$WORK/phase3-colour.mlt" <<'MLT_INPUT'
<?xml version="1.0" encoding="utf-8"?>
<mlt LC_NUMERIC="C" version="7.0.0" producer="playlist0">
  <profile description="Ferrari" width="320" height="180" progressive="1" sample_aspect_num="1" sample_aspect_den="1" display_aspect_num="16" display_aspect_den="9" frame_rate_num="25" frame_rate_den="1" colorspace="709"/>
  <producer id="colour0" in="0" out="49">
    <property name="mlt_service">color</property>
    <property name="resource">#176fae</property>
  </producer>
  <playlist id="playlist0">
    <entry producer="colour0" in="0" out="49"/>
  </playlist>
</mlt>
MLT_INPUT
python3 -m engine.ferrari invoke --action kdenlive-mlt-mp4 \
  --input "$WORK/phase3-colour.mlt" --output "$WORK/mlt-video" \
  > "$WORK/phase3-mlt-action.json"
python3 - "$WORK" <<'PY_PHASE3_MLT'
import json,sys,subprocess
from pathlib import Path
root=Path(sys.argv[1])
mp4=root/"mlt-video/mlt-video.mp4"
assert mp4.is_file() and mp4.stat().st_size>1024,mp4
p=subprocess.run(["ffprobe","-v","error","-show_entries",
  "stream=codec_type,width,height:format=duration","-of","json",str(mp4)],
  capture_output=True,text=True,check=True,timeout=30)
data=json.loads(p.stdout)
streams=[v for v in data.get("streams",[]) if v.get("codec_type")=="video"]
assert streams and streams[0]["width"]==320 and streams[0]["height"]==180,streams
assert 1.5<float(data["format"]["duration"])<3.0,data
report=json.loads((root/"phase3-mlt-action.json").read_text())
assert report.get("confirmed") is True and report.get("tool")=="kdenlive",report
print("FERRARI_KDENLIVE_MLT_MP4_REAL=PASS")
PY_PHASE3_MLT
