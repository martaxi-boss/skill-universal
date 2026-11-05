#!/usr/bin/env python3
"""Real Ferrari-only tests of the four Python-script typed actions."""
from pathlib import Path
import gzip
import json
import sys
import zipfile
from engine import tool_runtime

ROOT=Path("/srv/projects/skill-universal")


def sample_pdf():
    stream=b"BT /F1 18 Tf 50 700 Td (Ferrari private PDF) Tj ET\n"
    objects=[
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length "+str(len(stream)).encode()+b" >>\nstream\n"+stream+b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    buf=bytearray(b"%PDF-1.4\n")
    offsets=[0]
    for index,body in enumerate(objects,1):
        offsets.append(len(buf))
        buf.extend(f"{index} 0 obj\n".encode()+body+b"\nendobj\n")
    start=len(buf)
    buf.extend(f"xref\n0 {len(offsets)}\n".encode()+b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        buf.extend(f"{offset:010d} 00000 n \n".encode())
    buf.extend(f"trailer\n<< /Root 1 0 R /Size {len(offsets)} >>\nstartxref\n{start}\n%%EOF\n".encode())
    return bytes(buf)


def main():
    if len(sys.argv)!=2:
        raise SystemExit("Expected unique GitHub run ID")
    work=ROOT/".runtime/private-python-smoke"/sys.argv[1]
    if work.exists() or work.is_symlink():
        raise FileExistsError("Fresh Ferrari job directory required")
    work.mkdir(parents=True)
    inputs={
      "binwalk-scan":("sample.bin",b"Ferrari"+b"\\x00"*100+gzip.compress(b"Private Ferrari tool"*30)),
      "ansible-inventory-json":("inventory.ini",b"[all]\nlocalhost ansible_connection=local\n"),
      "ocrmypdf-searchable-pdf":("document.pdf",sample_pdf()),
      "calibre-md-epub":("chapter.md",b"# Ferrari\n\nIndependent Ubuntu skill.\n"),
    }
    results=[]
    for action,(filename,payload) in inputs.items():
        path=work/filename
        path.write_bytes(payload)
        spec=tool_runtime.specs()[action]
        exe=tool_runtime.executable(spec["tool"],spec["binary"])
        if not exe or not Path(exe).resolve(strict=True).is_relative_to(ROOT):
            raise RuntimeError("Executor outside Ferrari: "+action)
        print("FERRARI_PYTHON_CLI_START="+action,flush=True)
        response=tool_runtime.invoke(action,str(path),str(work/action))
        if not response["confirmed"]:
            raise RuntimeError("Real action failed: "+action)
        artifact=work/action/spec["artifact"]
        if not artifact.is_file() or artifact.stat().st_size<=20:
            raise RuntimeError("Missing real output: "+action)
        if action=="ansible-inventory-json" and "localhost" not in artifact.read_text():
            raise RuntimeError("Ansible inventory missing host")
        if action=="ocrmypdf-searchable-pdf" and not artifact.read_bytes().startswith(b"%PDF-"):
            raise RuntimeError("OCRmyPDF output is not PDF")
        if action=="calibre-md-epub":
            with zipfile.ZipFile(artifact) as result:
                if "mimetype" not in result.namelist():
                    raise RuntimeError("Calibre EPUB invalid")
        results.append({"action":action,"bytes":artifact.stat().st_size})
        print("FERRARI_PYTHON_CLI_PASS="+action,flush=True)
    count=sum(
        bool(exe:=tool_runtime.executable(spec["tool"],spec["binary"]))
        and Path(exe).resolve().is_relative_to(ROOT)
        for spec in tool_runtime.specs().values())
    print("FERRARI_PYTHON_PRIVATE_COUNT="+str(count))
    print("FERRARI_PYTHON_CLI_FOUR=PASS")
    print(json.dumps(results,sort_keys=True))


if __name__=="__main__":
    main()
