"""Regression checks: authoritative Ferrari documentation must not regress to stale phases."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CurrentFerrariDocsTests(unittest.TestCase):
    def test_bootstrap_is_an_operational_snapshot_not_a_chronology(self):
        text = (ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")
        self.assertIn("Fotografia atual com provas", text)
        self.assertIn("41716562469", text)
        self.assertIn("41672372249", text)
        self.assertIn("41717389118", text)
        self.assertIn("41718385142", text)
        self.assertIn("Apktool", text)
        self.assertIn("3.0.3", text)
        self.assertIn("REA FINAL e Trial removidos", text)
        self.assertIn("NÃO autorizar", text)
        self.assertLess(len(text), 17000, "Keep old milestone narratives in Git history/docs")
        self.assertNotIn("Instalação na VPS: não iniciada", text)
        self.assertNotIn("0 ferramentas certificadas na VPS", text)

    def test_current_entrypoints_agree_on_scope(self):
        paths = (
            "README.md",
            "skill/motor-universal-linux/SKILL.md",
            "skill/motor-universal-linux/references/bootstrap.md",
            "skill/motor-universal-linux/references/github-bridge.md",
        )
        for path in paths:
            with self.subTest(path=path):
                doc = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("BOOTSTRAP", doc)
                self.assertIn("Ferrari", doc)
                self.assertNotIn("23/56", doc)
                self.assertNotIn("a VPS ativa ainda nao o recebe", doc)
                self.assertNotIn("ligação direta ainda não certificada", doc)
                self.assertNotIn("Apktool 2.7.0", doc)

    def test_20261105_state_and_legacy_alias_retirement(self):
        bootstrap = (ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sk = (ROOT / "skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        portable = (ROOT / "skill/motor-universal-linux/references/bootstrap.md").read_text(encoding="utf-8")
        for doc in (bootstrap, readme, sk, portable):
            self.assertNotIn("pinado em `292aeb7d10eecef8c3ca84760cd579e84e4b97f3`", doc)
            self.assertIn("Hopper", doc)
            self.assertNotIn("é um link exclusivo", doc)
            self.assertIn("450", doc)
            self.assertIn("42297678715", doc)
        # Historic SHA only needs to appear where historical releases are documented.
        for doc in (bootstrap, sk, portable):
            self.assertIn("f1f3b035", doc)
        # Historic code SHAs are not immutable requirements of the live snapshot.
        for doc in (readme, sk, portable):
            self.assertIn("b2869e33", doc)
        self.assertIn("87969badbde0a77c2c181bb9605357d51a4a30c0", bootstrap)
        self.assertIn("42030605124", bootstrap)
        self.assertIn("FERRARI_PRIVATE_EXECUTORS=40/40_PASS", bootstrap)
        self.assertIn("41981152670", bootstrap)
        self.assertIn("41840478411", bootstrap)

    def test_one_catalog_guides_skill_and_public_readme(self):
        """Do not send a Ferrari user to the deleted action registry."""
        paths = (
            "BOOTSTRAP.md", "README.md",
            "skill/motor-universal-linux/SKILL.md",
            "skill/motor-universal-linux/references/bootstrap.md",
            "skill/motor-universal-linux/references/github-bridge.md",
        )
        for path in paths:
            with self.subTest(path=path):
                doc = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("engine/catalog.json", doc)
                self.assertNotIn("engine/tool_actions.json", doc)
        bootstrap = (ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")
        self.assertIn("42263466893", bootstrap)
        self.assertIn("42265187873", bootstrap)
        bridge = (ROOT / "skill/motor-universal-linux/references/github-bridge.md").read_text(encoding="utf-8")
        self.assertIn("0b50e1d403deff8f3ccb421edd0b41c397d66b9b", bridge)

    def test_f9_nominal_global_apt_readback_is_current(self):
        report = (ROOT / "docs/FASE9_HIGIENE_APT_FINAL_20261106.md").read_text(encoding="utf-8")
        self.assertIn("42300665770", report)
        self.assertIn("42299686585", report)
        self.assertIn("Instalados: 0/8", report)
        self.assertIn("certificação funcional exaustiva", report)
        for path in ("BOOTSTRAP.md", "README.md",
                     "skill/motor-universal-linux/SKILL.md",
                     "skill/motor-universal-linux/references/bootstrap.md"):
            with self.subTest(path=path):
                doc = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("42300665770", doc)
                self.assertIn("QGIS", doc)

    def test_qgis_real_buffer_pass_does_not_claim_ogr_or_hdf5(self):
        report = (ROOT / "docs/FASE9_QGIS_BUFFER_GEOJSON_CERT_20261106.md").read_text(encoding="utf-8")
        for marker in ("42304131087", "6 578,316", "libhdf5_cpp.so.320",
                       "native:buffer", "std::bad_alloc"):
            self.assertIn(marker, report)
        for path in ("BOOTSTRAP.md", "README.md",
                     "skill/motor-universal-linux/SKILL.md",
                     "skill/motor-universal-linux/references/bootstrap.md"):
            with self.subTest(path=path):
                doc = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("42304131087", doc)
                self.assertIn("QGIS", doc)
        self.assertIn("OGR", report)
        self.assertIn("Não", report)

    def test_librecad_private_dxf_pdf_certificate_is_not_gui_certification(self):
        report = (ROOT / "docs/FASE9_LIBRECAD_DXF_PDF_CERT_20261106.md").read_text(encoding="utf-8")
        for value in ("42310428893", "42311158545", "1 614", "pdfinfo",
                      "Xvfb", "GUI", "25544619"):
            self.assertIn(value, report)
        for path in ("BOOTSTRAP.md", "README.md",
                     "skill/motor-universal-linux/SKILL.md",
                     "skill/motor-universal-linux/references/bootstrap.md"):
            with self.subTest(path=path):
                content = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("42311158545", content)
                self.assertIn("LibreCAD", content)
        script = (ROOT / "install/vps-f9-librecad-dxf2pdf-certify.py").read_text(encoding="utf-8")
        self.assertIn('"gui_editing_certified": False', script)
        self.assertIn('"preexisting_xvfb_qa_display": True', script)

    def test_f9_cad3d_blender_and_pdal_scopes_are_evidence_backed(self):
        report = (ROOT / "docs/FASE9_CAD3D_BLENDER_PDAL_SKILL_20261106.md").read_text(encoding="utf-8")
        for proof in ("42312047260", "42312161892", "42311620021",
                      "27 446,705", "208 faces", "6 geometrias",
                      "full_pdal_formats_certified=false", "não certifica"):
            self.assertIn(proof, report)
        for path in ("BOOTSTRAP.md", "README.md",
                     "skill/motor-universal-linux/SKILL.md",
                     "skill/motor-universal-linux/references/bootstrap.md"):
            with self.subTest(path=path):
                entry = (ROOT / path).read_text(encoding="utf-8")
                self.assertIn("42312047260", entry)
                self.assertIn("42312161892", entry)
                self.assertIn("42311620021", entry)
                self.assertIn("450", entry)
        self.assertLess(len((ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")), 17000)

    def test_f10_active_fallback_and_cleanup_evidence(self):
        paths = ("BOOTSTRAP.md", "README.md", "skill/motor-universal-linux/SKILL.md",
                 "skill/motor-universal-linux/references/bootstrap.md")
        for path in paths:
            text=(ROOT/path).read_text(encoding="utf-8")
            for marker in ("205c6f0e", "7bf6dcec", "450", "42314959728", "42315724016"):
                self.assertIn(marker,text)
        report=(ROOT/"docs/FASE10_CATALOGO_HIGIENE_FINAL_20261107.md").read_text()
        for marker in ("42314715020","42314959728","42315141299",
                       "42315365287","42315656543","42315724016","2 433 024"):
            self.assertIn(marker,report)

    def test_portable_skill_does_not_reintroduce_old_runtime(self):
        sk = (ROOT / "skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        portable = (ROOT / "skill/motor-universal-linux/references/bootstrap.md").read_text(encoding="utf-8")
        for text in (sk, portable):
            self.assertIn("rea-agents@6.8.0", text)
            self.assertIn("3.0.3", text)
            self.assertIn("41786521407", text)
            self.assertIn("rea-mcp", text)
            self.assertIn("55/55", text)
            self.assertIn("272/272", text)
            self.assertNotIn("REA antigo como fallback", text)
        self.assertIn("references/github-bridge.md", sk)
        self.assertIn("references/bootstrap.md", sk)

if __name__ == "__main__":
    unittest.main()
