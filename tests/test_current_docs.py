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
        self.assertIn("REA antigo", text)
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

    def test_portable_skill_does_not_reintroduce_old_runtime(self):
        sk = (ROOT / "skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        portable = (ROOT / "skill/motor-universal-linux/references/bootstrap.md").read_text(encoding="utf-8")
        for text in (sk, portable):
            self.assertIn("rea-agents@6.8.0", text)
            self.assertIn("3.0.3", text)
            self.assertIn("41716562469", text)
            self.assertIn("rea-mcp", text)
            self.assertIn("55/56", text)
            self.assertNotIn("REA antigo como fallback", text)
        self.assertIn("references/github-bridge.md", sk)
        self.assertIn("references/bootstrap.md", sk)

if __name__ == "__main__":
    unittest.main()
