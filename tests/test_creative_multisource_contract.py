"""Protect the Ferrari universal creative intake, not URL-only advert prompts."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]

class CreativeMultisourceContract(unittest.TestCase):
    def test_skill_takes_any_authorized_media_not_just_website(self):
        skill=(ROOT/"skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        guide=(ROOT/"skill/motor-universal-linux/references/creative-multisource.md").read_text(encoding="utf-8")
        self.assertIn("references/creative-multisource.md",skill)
        self.assertIn("O URL não é obrigatório",skill)
        for name in ("fotografias", "vídeo", "Reels", "ideias", "misturas"):
            self.assertIn(name,skill)
        for term in ("input_kind","website","photos","video","reel","text_brief",
                     "mixed","intake_manifest.json","media_candidates.jpg",
                     "media_intake.py","voice_script","storyboard","rights_status"):
            self.assertIn(term,guide)
        self.assertIn("não preserva ainda excertos de vídeo em movimento",guide)
        self.assertIn("nunca enviar os bytes para um repositório GitHub público",guide)

if __name__=="__main__":
    unittest.main()
