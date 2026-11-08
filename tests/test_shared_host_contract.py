"""Guard the Ferrari's declared architecture: ONE shared host, no resident AI.

This is an acceptance-contract regression, NOT a claim to test every GUI
capability or all future tasks.
"""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]


class SharedHostContractTests(unittest.TestCase):
    def test_canonical_contract_uses_one_active_host(self):
        b=(ROOT/"BOOTSTRAP.md").read_text(encoding="utf-8")
        top=b.split("**FONTE DE VERDADE OBRIGATÓRIA",1)[0]
        for marker in ("UMA IA anfitriã", "Ruflo", "mesma IA anfitriã",
                       "42509439220", "não fazem parte", "não bloqueia"):
            # Canonical contract must keep the meaning explicit.
            if marker=="não fazem parte":
                self.assertTrue("NÃO FAZ PARTE" in top or "NÃO FAZEM PARTE" in top)
            else:
                self.assertIn(marker,top)

    def test_one_portable_skill_does_not_demand_autonomous_agents(self):
        s=(ROOT/"skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        lead=s.split("**Operação `prometheus-rule-check`",1)[0]
        self.assertIn("UMA IA ANFITRIÃ",lead)
        self.assertIn("não modelos que tenham de pensar",lead)
        self.assertIn("Não transformar",lead)
        self.assertIn("42509439220",lead)
        ref=(ROOT/"skill/motor-universal-linux/references/bootstrap.md").read_text(encoding="utf-8")
        self.assertIn("Nenhum subagente precisa de modelo",ref)
        self.assertIn("não são um objetivo nem uma pendência",
                      (ROOT/"skill/motor-universal-linux/references/orchestration.md").read_text(encoding="utf-8"))

    def test_agents_cannot_call_a_model_implicitly(self):
        src=(ROOT/"engine/agent_team.py").read_text(encoding="utf-8")
        self.assertIn("never calls an LLM",src)
        self.assertIn("Each turn is a separate Ferrari Skill job",src)
        self.assertIn("No automatic LLM agent actions in Ferrari VPS",src)
        self.assertIn("Only the assigned independent reviewer may review",src)
        self.assertIn("All agent tasks require distinct reviewer approval",src)

if __name__=="__main__":
    unittest.main()
