"""Safety, provenance and catalog checks for the next Ferrari direct adapters."""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from engine import document_tools as doc, cache_tools as kv, ferrari, tool_runtime, catalog_registry


def make_docx(path: Path, text="Ferrari document synthetic laboratory proof"):
    xml = ('<?xml version="1.0" encoding="UTF-8"?>'
           '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
           '<w:body><w:p><w:r><w:t>' + text + '</w:t></w:r></w:p></w:body></w:document>')
    with zipfile.ZipFile(path,"w",zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml",
                         '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/><Default Extension="xml" ContentType="application/xml"/><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr("_rels/.rels",
                         '<?xml version="1.0"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml",xml)


class FerrariNewProgramAdapters(unittest.TestCase):
    def test_one_catalog_exact_two_more_direct_operations(self):
        d=catalog_registry.read_catalog()
        self.assertEqual(d["counts"]["all_catalog_entries"],458)
        self.assertEqual(d["counts"]["functions"],280)
        self.assertEqual(d["counts"]["functions_base_operations"],19)
        self.assertEqual(len(d["tools"]),173)
        for op,tool in (("docling-docx-markdown","docling"),("valkey-kv-test","valkey")):
            with self.subTest(op=op):
                self.assertIn(op,ferrari.OPS)
                self.assertIn(op,tool_runtime.BASE_OPERATIONS[tool])
                entries=[x for x in d["functions"] if x["id"]=="operation:"+op]
                self.assertEqual(len(entries),1)
                self.assertEqual(entries[0]["program"],tool)

    def test_docling_module_inventory_promotes_only_verified_private_worker(self):
        # A module does not have a CLI binary. The worker presence needs its
        # own private executable probe, exactly as faster-whisper/OpenCV.
        evidence={"scope":"ferrari_venv",
                  "location":"/srv/projects/skill-universal/.runtime/venvs/extended/docling/lib/python3.12/site-packages/docling"}
        worlds={
            "python":{"tools":{"docling":evidence}},
            "npm":{"tools":{}},
            "containers":{"tools":{}}
        }
        with patch.object(tool_runtime.runtime_discovery,"discover",return_value=worlds):
            with patch.object(doc,"available",return_value=True):
                available=tool_runtime.inventory()
            with patch.object(doc,"available",return_value=False):
                missing=tool_runtime.inventory()
        yes=next(x for x in available["programs"] if x["id"]=="docling")
        no=next(x for x in missing["programs"] if x["id"]=="docling")
        self.assertEqual(yes["status"],"callable")
        self.assertEqual(yes["integration_role"],"direct_action")
        self.assertEqual(yes["base_operations"],["docling-docx-markdown"])
        self.assertEqual(no["status"],"installed_unintegrated")
        self.assertEqual(no["base_operations"],[])

    def test_docx_package_accepts_only_bounded_private_word_parts(self):
        with tempfile.TemporaryDirectory() as tmp:
            home=Path(tmp)
            source=home/"synthetic.docx"
            make_docx(source)
            with patch.object(doc,"HOME",home):
                doc._safe_docx(source)
                with self.assertRaises(ValueError):
                    doc._safe_docx(home/"missing.docx")
                duplicate=home/"malicious.docx"
                with zipfile.ZipFile(duplicate,"w") as z:
                    z.writestr("../escape","SECRET")
                    z.writestr("[Content_Types].xml","types")
                    z.writestr("word/document.xml","content")
                with self.assertRaisesRegex(ValueError,"Unsafe"):
                    doc._safe_docx(duplicate)
                link=home/"symlink.docx"
                link.symlink_to(source)
                with self.assertRaises(ValueError):
                    doc._safe_docx(link)

    def test_docling_real_result_must_have_matching_hash_and_nonempty_md(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            (root/".runtime").mkdir()
            source=root/"doc.docx"
            make_docx(source)
            target=root/"outputs"
            def execute(args,**kwargs):
                target.mkdir(exist_ok=True)
                md=target/"docling-extracted.md"
                md.write_text("## Ferrari\n\nSynthetic document converted from Word.\n")
                report={
                    "status":"completed","program":"docling",
                    "input_sha256":doc.sha(source),"markdown_sha256":doc.sha(md),
                    "chars":len(md.read_text()),"offline":True,
                    "semantic_quality_certified":False
                }
                (target/"docling-report.json").write_text(json.dumps(report))
                return subprocess.CompletedProcess(args,0,"FERRARI_PRIVATE_DOCLING_WORD=PASS","")
            with patch.object(doc,"HOME",root),patch.object(doc,"available",return_value=True),\
                 patch.object(doc.subprocess,"run",side_effect=execute):
                exe,files=doc.convert(source,target)
                self.assertEqual(len(files),2)
                self.assertTrue(all(f.is_file() for f in files))
                self.assertIn("docling-private-word",exe)
                self.assertIn("Ferrari",files[0].read_text())
                with self.assertRaises(FileExistsError):
                    doc.convert(source,target)

    def test_valkey_RESP_protocol_is_whitelisted_and_bounded(self):
        class FakeConn:
            def __init__(self,replies):
                self.replies=iter(replies)
                self.sent=[]
            def sendall(self,data):
                self.sent.append(data)
            def makefile(self,*args,**kwargs):
                return io.BytesIO(next(self.replies))
        conn=FakeConn([b"+PONG\r\n",b"+OK\r\n",
                       b"$4\r\nDATA\r\n",b":1\r\n",b"$-1\r\n"])
        self.assertEqual(kv._command(conn,b"PING"),b"PONG")
        self.assertEqual(kv._command(conn,b"SET",b"K",b"DATA"),b"OK")
        self.assertEqual(kv._command(conn,b"GET",b"K"),b"DATA")
        self.assertEqual(kv._command(conn,b"DEL",b"K"),1)
        self.assertIsNone(kv._command(conn,b"GET",b"K"))
        self.assertTrue(all(line.startswith(b"*") for line in conn.sent))
        self.assertEqual(len(conn.sent),5)

    def test_valkey_rejects_output_paths_outside_ferrari(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"home"
            root.mkdir()
            exe=root/"valkey"
            exe.write_bytes(b"#!/bin/sh\nexit 0\n")
            exe.chmod(0o700)
            with patch.object(kv,"HOME",root),patch.object(kv,"EXECUTABLE",exe):
                with self.assertRaises(ValueError):
                    kv.prove(Path(tmp)/"outside")
                self.assertTrue(kv.available())

    def test_no_network_daemon_global_python_or_shell_fallback(self):
        dsource=Path(doc.__file__).read_text(encoding="utf-8")
        csource=Path(kv.__file__).read_text(encoding="utf-8")
        self.assertIn('allowed_formats=[InputFormat.DOCX]',dsource)
        self.assertIn('HF_HUB_OFFLINE',dsource)
        self.assertIn('shell=False',dsource)
        self.assertIn('shell=False',csource)
        self.assertIn('--port", "0"',csource)
        self.assertIn('start_new_session=True',csource)
        self.assertIn('os.killpg',csource)
        self.assertNotIn('shell=True',dsource+csource)
        self.assertNotIn('https://api.',dsource+csource)


if __name__=="__main__":
    unittest.main()
