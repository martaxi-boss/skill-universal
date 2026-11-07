"""Regression checks for Ferrari professional ad QA, brand fidelity and speech."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
class CreativeContractTests(unittest.TestCase):
    def test_brand_and_voice_gate(self):
        skill=(ROOT/"skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        ref=(ROOT/"skill/motor-universal-linux/references/professional-creatives.md").read_text(encoding="utf-8")
        for phrase in ("references/professional-creatives.md", "FINAL PROFISSIONAL", "PRÉ-VISUALIZAÇÃO", "voz humana", "Piper", "Kokoro", "eSpeak"):
            self.assertIn(phrase,skill)
        for phrase in ("martaxi-boss/lowcost-europa", "#164f42", "#103c32", "VER EQUIPAMENTOS E PREÇOS", "human_recording", "synthetic_pt_pt", "audition_approved_by_owner", "editorial_pending", "approved_for_ads", "Criativos-anuncios"):
            self.assertIn(phrase,ref)
    def test_tts_catalog_not_false_certified(self):
        import json
        catalog=json.loads((ROOT/"engine/catalog.json").read_text(encoding="utf-8"))
        self.assertTrue(any(x.get("id")=="piper" for x in catalog["tools"]))
        self.assertFalse(any("piper" in x.get("id","").lower() for x in catalog["functions"]))
        doc=(ROOT/"skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("Nunca afirmar que Piper ou Kokoro estão instalados/certificados",doc)
if __name__=="__main__":
    unittest.main()
