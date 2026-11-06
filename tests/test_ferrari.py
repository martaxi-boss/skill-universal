"""Regressions for the independent Ferrari engine."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import ferrari

class FerrariTests(unittest.TestCase):
    def test_registry(self):
        x=ferrari.registry()
        self.assertGreaterEqual(len(x),122)
        self.assertEqual(len(set(i["id"] for i in x)),len(x))
    def test_plan(self):
        x=ferrari.plan("Quero descompilar um APK")
        self.assertEqual(x["route"],"reverse")
        self.assertFalse(x["executed"])
        self.assertIn("jadx",[i["id"] for i in x["selected"]])
    def test_new_domains(self):
        cases = [
            ("desenha modelo CAD 3D para uma peça", "cad"),
            ("preciso de um fluxograma", "diagrams"),
            ("produzir musica e audio para podcast", "audio"),
            ("criar relatorio PDF com OCR", "docs"),
            ("analisar dados e SQL", "data"),
        ]
        for message, expected in cases:
            plan=ferrari.plan(message)
            self.assertEqual(plan["route"],expected)
            self.assertFalse(plan["executed"])
            self.assertGreaterEqual(plan["catalogued_total"],122)
    def test_penpot_retired_and_openpencil_kept(self):
        import json
        catalog = json.loads(
            (Path(__file__).resolve().parents[1] / "engine/catalog.json")
            .read_text(encoding="utf-8"))
        ids = {item["id"] for item in catalog["tools"]}
        self.assertNotIn("penpot", ids)
        self.assertIn("openpencil", ids)
        self.assertNotIn("penpot", {item["id"] for item in ferrari.registry()})
        self.assertNotIn("penpot", {item["id"] for item in ferrari.ubuntu_selection()})
        self.assertNotIn("penpot", {item["id"] for item in ferrari.plan(
            "desenhar um wireframe web")["selected"]})

    def test_quality_gate(self):
        approved=ferrari.ubuntu_selection()
        self.assertGreaterEqual(len(approved),50)
        self.assertEqual(len(approved),len(set(p["id"] for p in approved)))
        self.assertLess(len(approved),len(ferrari.registry()))
        self.assertNotIn("helix", [p["id"] for p in approved])
        self.assertTrue(all(p.get("ubuntu_evidence") for p in approved))
        self.assertTrue(all(p.get("ubuntu_certified") is False for p in approved))
    def test_only_ubuntu_repositories_are_suggested(self):
        ids=set(p["id"] for p in ferrari.ubuntu_selection())
        for query in ["site e loja profissional","CAD modelação","processar PDF","criar música e som","base de dados SQL"]:
            suggestion=ferrari.plan(query)
            self.assertTrue(all(p["id"] in ids for p in suggestion["selected"]))
    def test_no_unchecked_apt_candidates_in_install_plan(self):
        approved=ferrari.ubuntu_selection()
        allowed={p["package_candidate"] for p in approved if
                 p.get("package_candidate") and p["curated_status"] in {
                 "apt_candidate_found_on_ubuntu2404_runner","gui_apt_candidate_found_on_ubuntu2404_runner"}}
        packages=set(ferrari.packages("maximum"))
        packages_core=set(ferrari.packages("core"))
        self.assertTrue((packages-packages_core).issubset(allowed|{"openjdk-21-jdk-headless","binutils","gdb","strace","graphviz","poppler-utils","nodejs","npm","build-essential"}))
        self.assertNotIn("freecad",packages)
    def test_packages(self):
        x=ferrari.packages()
        self.assertIn("apktool",x)
        self.assertIn("tesseract-ocr",x)
        self.assertIn("ffmpeg",x)
        self.assertIn("krita",x)
        self.assertNotIn("krita",ferrari.packages(include_gui=False))
    def test_website(self):
        with tempfile.TemporaryDirectory() as d:
            x=ferrari.run("web-template",d,title="Ferrari")
            self.assertTrue(x["confirmed"])
            self.assertIn("Ferrari",Path(x["artifacts"][0]).read_text())
            with self.assertRaises(FileExistsError):
                ferrari.run("web-template",d)
    def test_layout_variants(self):
        for layout in ("store","portfolio","dashboard"):
            with tempfile.TemporaryDirectory() as d:
                result=ferrari.run("web-template",d,title="Marca Ferrari",layout=layout)
                self.assertTrue(result["confirmed"])
                self.assertIn("Marca Ferrari",Path(result["artifacts"][0]).read_text())
    def test_creative(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(ferrari.run("svg-poster",d)["confirmed"])
    def test_no_shell(self):
        with self.assertRaises(ValueError):
            ferrari.run("shell","/tmp/no-op")
    def test_invalid_apk(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"not-apk.txt";p.write_text("x")
            with self.assertRaises(ValueError):
                ferrari.run("apk-decompile",d+"/out",source=p)
    def test_missing_executable(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.pdf";p.write_bytes(b"%PDF")
            with patch("shutil.which",return_value=None):
                with self.assertRaises(RuntimeError):
                    ferrari.run("pdf-text",d+"/out",source=p)
    def test_legal_free_alternatives(self):
        x=ferrari.alternatives("Adobe Photoshop")
        self.assertEqual(x["match"],"Adobe Photoshop")
        self.assertIn("gimp",[p["id"] for p in x["alternatives"]])
        self.assertIn("not a cracked original",x["notice"])
    def test_discovery_filtered_without_network(self):
        import json
        from engine.github_discovery import discover
        payload={"items":[
            {"full_name":"good/repo","html_url":"https://github.com/good/repo","stargazers_count":3000,
             "archived":False,"fork":False,"license":{"spdx_id":"MIT"},"pushed_at":"2026-11-02T00:00:00Z"},
            {"full_name":"notfree/proprietary","html_url":"https://github.com/notfree/proprietary",
             "stargazers_count":9000,"archived":False,"fork":False,"license":{"spdx_id":"NOASSERTION"}},
            {"full_name":"old/archived","html_url":"https://github.com/old/archived",
             "stargazers_count":8000,"archived":True,"fork":False,"license":{"spdx_id":"MIT"}}]}
        class Response:
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def read(self,size): return json.dumps(payload).encode()
        with patch("urllib.request.urlopen",return_value=Response()) as mock:
            x=discover("image processing Ubuntu",minimum_stars=100,limit=5)
            self.assertEqual(len(x["results"]),1)
            self.assertEqual(x["results"][0]["repository"],"good/repo")
            self.assertFalse(x["results"][0]["automatic_install_allowed"])
            self.assertTrue(mock.call_args[0][0].full_url.startswith("https://api.github.com/search/repositories?"))
        with self.assertRaises(ValueError):
            discover("Adobe crack Photoshop")
    def test_doctor_no_false_cert(self):
        self.assertEqual(ferrari.doctor()["status"],"inventory_only_not_functional_certification")
if __name__=="__main__":unittest.main()
