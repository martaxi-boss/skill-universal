"""Ferrari-private, fully offline Docling Word -> Markdown adapter.

Only a bounded, project-owned DOCX is accepted. This worker reuses the
existing Docling+OpenCV virtualenv, never downloads models or calls an API.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import zipfile

HOME = Path("/srv/projects/skill-universal")
VENV = HOME / ".runtime/venvs/extended/docling"
PYTHON = VENV / "bin/python"
MODULE = VENV / "lib/python3.12/site-packages/docling"
MAX_BYTES = 2_000_000
MAX_UNCOMPRESSED_BYTES = 12_000_000


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def available() -> bool:
    try:
        root = HOME.resolve(strict=True)
        return bool(
            VENV.is_dir() and not VENV.is_symlink()
            and VENV.resolve(strict=True).is_relative_to(root)
            and PYTHON.is_file() and os.access(PYTHON, os.X_OK)
            and PYTHON.resolve(strict=True).is_relative_to(root)
            and MODULE.is_dir() and not MODULE.is_symlink()
            and MODULE.resolve(strict=True).is_relative_to(root)
        )
    except (OSError, RuntimeError):
        return False


def _safe_docx(source: Path) -> None:
    root = HOME.resolve(strict=True)
    if (source.is_symlink() or not source.is_file()
            or not source.resolve(strict=True).is_relative_to(root)
            or source.suffix.lower() != ".docx"
            or not 100 <= source.stat().st_size <= MAX_BYTES):
        raise ValueError("Ferrari Docling needs a private DOCX up to 2 MB")
    try:
        with zipfile.ZipFile(source) as archive:
            entries = archive.infolist()
            if (not 2 <= len(entries) <= 300
                    or sum(e.file_size for e in entries) > MAX_UNCOMPRESSED_BYTES
                    or any(e.file_size > 8_000_000 or e.flag_bits & 0x1
                           or e.filename.startswith("/")
                           or any(v == ".." for v in e.filename.split("/"))
                           or (e.external_attr >> 16) & 0o170000 == 0o120000
                           for e in entries)):
                raise ValueError("Unsafe or oversized DOCX ZIP members")
            names = set(archive.namelist())
            if not {"[Content_Types].xml", "word/document.xml"} <= names:
                raise ValueError("DOCX missing Word document parts")
            if archive.testzip() is not None:
                raise ValueError("DOCX failed CRC integrity")
    except (zipfile.BadZipFile, OSError, RuntimeError) as exc:
        raise ValueError("Ferrari expected a valid DOCX package") from exc


def convert(source: Path, folder: Path):
    source, folder = Path(source), Path(folder)
    _safe_docx(source)
    if not available():
        raise RuntimeError("Ferrari private Docling interpreter is not available")
    if folder.is_symlink() or not folder.resolve().is_relative_to(HOME.resolve(strict=True)):
        raise ValueError("Ferrari Docling output must stay within the project")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    md, report = folder / "docling-extracted.md", folder / "docling-report.json"
    if any(p.exists() or p.is_symlink() for p in (md, report)):
        raise FileExistsError("Ferrari refuses to overwrite Docling outputs")
    env = {k: v for k, v in os.environ.items()
           if k not in {"PYTHONHOME","PYTHONPATH","LD_PRELOAD","LD_LIBRARY_PATH","HF_TOKEN"}}
    env.update({
        "PYTHONNOUSERSITE":"1", "PYTHONDONTWRITEBYTECODE":"1",
        "HF_HUB_OFFLINE":"1", "TRANSFORMERS_OFFLINE":"1",
        "HF_HUB_DISABLE_TELEMETRY":"1", "TOKENIZERS_PARALLELISM":"false",
        "CUDA_VISIBLE_DEVICES":"", "OMP_NUM_THREADS":"2",
        "HOME":str(folder), "TMPDIR":str(folder),
        "XDG_CACHE_HOME":str(folder), "XDG_CONFIG_HOME":str(folder),
        "HTTP_PROXY":"http://127.0.0.1:9",
        "HTTPS_PROXY":"http://127.0.0.1:9",
        "ALL_PROXY":"socks5://127.0.0.1:9", "NO_PROXY":"",
    })
    try:
        result = subprocess.run(
            [str(PYTHON), "-I", str(Path(__file__).resolve(strict=True)),
             "--worker", str(source), str(folder)],
            cwd=str(folder), env=env, shell=False,
            capture_output=True, text=True, errors="replace",
            timeout=110, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Ferrari private Docling timed out") from exc
    if result.returncode:
        raise RuntimeError("Ferrari Docling conversion failed: " + result.stderr[-450:])
    if (not md.is_file() or md.is_symlink() or not 15 <= md.stat().st_size <= MAX_BYTES
            or not report.is_file() or report.is_symlink()):
        raise RuntimeError("Ferrari Docling produced no valid Markdown/report")
    obj = json.loads(report.read_text(encoding="utf-8"))
    content = md.read_text(encoding="utf-8")
    if (obj.get("status") != "completed" or obj.get("program") != "docling"
            or obj.get("input_sha256") != sha(source)
            or obj.get("markdown_sha256") != sha(md)
            or obj.get("chars") != len(content)
            or obj.get("offline") is not True
            or obj.get("semantic_quality_certified") is not False):
        raise RuntimeError("Docling extraction proof failed independent verification")
    return str(PYTHON) + ":docling-private-word", [md, report]


def _worker(source: Path, folder: Path) -> int:
    if Path(sys.prefix).resolve(strict=True) != VENV.resolve(strict=True):
        raise RuntimeError("Ferrari Docling worker must use installed private Python")
    _safe_docx(source)
    from docling.datamodel.base_models import InputFormat
    from docling.document_converter import DocumentConverter, WordFormatOption
    converter = DocumentConverter(
        allowed_formats=[InputFormat.DOCX],
        format_options={InputFormat.DOCX: WordFormatOption()})
    result = converter.convert(str(source), max_file_size=MAX_BYTES)
    status = getattr(result.status, "value", str(result.status)).lower()
    if status != "success":
        raise RuntimeError("Docling Word conversion did not fully succeed: " + status)
    text = result.document.export_to_markdown()
    if not isinstance(text, str) or len(text.strip()) < 15:
        raise RuntimeError("Docling extracted no meaningful content")
    if len(text.encode("utf-8")) > MAX_BYTES:
        raise RuntimeError("Docling Markdown output exceeded size limit")
    md = folder / "docling-extracted.md"
    with md.open("x", encoding="utf-8") as output:
        output.write(text)
        if not text.endswith("\n"):
            output.write("\n")
    record = {
        "status":"completed", "program":"docling",
        "format":"docx", "offline":True,
        "input_sha256":sha(source), "markdown_sha256":sha(md),
        "chars":len(md.read_text(encoding="utf-8")),
        "semantic_quality_certified":False, "ocr_certified":False,
        "note":"Real Docling Word parser; text contents still require review."
    }
    with (folder/"docling-report.json").open("x", encoding="utf-8") as output:
        json.dump(record,output,ensure_ascii=False,indent=2)
        output.write("\n")
    try:
        result.input.release()
    except AttributeError:
        pass
    print("FERRARI_PRIVATE_DOCLING_WORD=PASS",flush=True)
    return 0


if __name__=="__main__":
    if len(sys.argv)!=4 or sys.argv[1]!="--worker":
        raise SystemExit("Ferrari Docling worker requires fixed --worker SRC OUTDIR")
    try:
        raise SystemExit(_worker(Path(sys.argv[2]),Path(sys.argv[3])))
    except Exception as exc:
        print("FERRARI_PRIVATE_DOCLING_WORD_FAILED="+str(exc)[:350],file=sys.stderr)
        raise SystemExit(2)
