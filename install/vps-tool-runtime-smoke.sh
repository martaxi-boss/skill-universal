#!/usr/bin/env bash
# Run on Ferrari Ubuntu VPS after deployment. Real multi-domain work, not help-only.
set -Eeuo pipefail
umask 077
cd "$(dirname "$0")/.."
ROOT="$HOME/.local/share/motor-ferrari"
mkdir -p "$ROOT/.runtime"
WORK="$(mktemp -d "$ROOT/.runtime/tool-smoke.XXXXXXXX")"
trap 'rm -rf -- "$WORK"' EXIT

python3 -m engine.ferrari tools > "$WORK/catalogue.json"
python3 - "$WORK/catalogue.json" <<'PY'
import json,sys
x=json.load(open(sys.argv[1]))
assert x["selected"]==56
assert x["registered_actions"]==22
assert x["callable_actions"]>=22
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
printf '![Documento digitalizado](ocr-scan.png)\n' > "$WORK/ocr-scan.md"
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
