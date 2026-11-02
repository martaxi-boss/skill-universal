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
assert x["registered_actions"]==12
assert x["callable_actions"]>=7
for name in ("pandoc","graphviz","jq","ffmpeg","imagemagick","tesseract"):
    p=next(z for z in x["programs"] if z["id"]==name)
    assert p["installed"] and p["actions"],name
print("FERRARI_UNIVERSAL_INVENTORY=PASS")
print("FERRARI_UNIVERSAL_ACTIONS_AVAILABLE="+str(x["callable_actions"]))
print("FERRARI_UNIVERSAL_PROGRAMS_DETECTED="+str(x["installed"]))
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
assert json.loads((p/"route.json").read_text())["suggestions"][0]["action"]=="pandoc-md-docx"
result=json.loads((p/"flow-result.json").read_text())["result"]
assert result["status"]=="completed"
assert len(result["completed"])==3
print("FERRARI_UNIVERSAL_AUTO_EXECUTION=PASS")
print("FERRARI_UNIVERSAL_ROUTING=PASS")
print("FERRARI_UNIVERSAL_REAL_MULTI_PROGRAM_EXECUTION=PASS")
print("FERRARI_UNIVERSAL_ORCHESTRATOR=PASS")
PY
