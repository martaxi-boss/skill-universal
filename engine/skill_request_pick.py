"""Ferrari-owned GitHub request selector; workflow merely transfers validated envelope."""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from engine.skill_job import validate_job, MAX_REQUEST_BYTES

REQUEST_PATTERN=re.compile(r"^ferrari-requests/job-[a-z0-9-]{8,70}\.json$")

def pick(repo,before,after,output):
    if not re.fullmatch("[a-f0-9]{40}",before) or not re.fullmatch("[a-f0-9]{40}",after):
        raise ValueError("Expected Git commit SHA identifiers")
    root=Path(repo).resolve()
    r=subprocess.run(["git","-C",str(root),"diff","--name-only","--diff-filter=A",
                      before,after,"--","ferrari-requests/"],capture_output=True,text=True,
                     check=True,timeout=20)
    files=[x for x in r.stdout.splitlines() if x.strip()]
    if len(files)!=1 or not REQUEST_PATTERN.fullmatch(files[0]):
        raise ValueError("Ferrari job push must add exactly one authorized request file")
    request=root/files[0]
    if request.is_symlink() or not request.is_file() or request.stat().st_size>MAX_REQUEST_BYTES:
        raise ValueError("Invalid Ferrari transport request file")
    doc=json.loads(request.read_text(encoding="utf-8"))
    validate_job(doc)
    dest=Path(output)
    dest.parent.mkdir(parents=True,exist_ok=True)
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("Ferrari request transport destination exists")
    dest.write_bytes(request.read_bytes())
    print("FERRARI_SKILL_TRANSPORT_REQUEST_VALID=PASS")
    print("FERRARI_SKILL_REQUEST_ID="+doc["id"])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",required=True)
    ap.add_argument("--before",required=True)
    ap.add_argument("--after",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    pick(a.repo,a.before,a.after,a.output)

if __name__=="__main__":
    try:main()
    except (ValueError,FileNotFoundError,FileExistsError,subprocess.CalledProcessError,subprocess.TimeoutExpired) as e:
        print("FERRARI_SKILL_TRANSPORT_REJECTED="+str(e),file=sys.stderr)
        sys.exit(2)
