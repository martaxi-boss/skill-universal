"""Guardrails for the canonical Ferrari bootstrap and Skill package."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]

class BootstrapTests(unittest.TestCase):
    def test_bootstrap_must_survive(self):
        bootstrap = (ROOT / "BOOTSTRAP.md").read_text(encoding="utf-8")
        for marker in (
            "UMA ÚNICA SKILL", "CONSTRUÇÃO", "CAD", "BIM",
            "INSTALADO_VPS", "DISPONIVEL_PELA_SKILL",
            "PRECHECK", "DEPLOY", "INSTALL_HEADLESS",
            "NÃO IMPLEMENTADA", "sem", "Ubuntu",
        ):
            self.assertIn(marker.lower(), bootstrap.lower(), marker)

    def test_skill_is_self_describing_and_links_bootstrap(self):
        text = (ROOT / "skill/motor-universal-linux/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("BOOTSTRAP.md", text)
        self.assertIn("references/bootstrap.md", text)
        ref = ROOT / "skill/motor-universal-linux/references/bootstrap.md"
        self.assertTrue(ref.is_file())
        self.assertIn("CAD", ref.read_text(encoding="utf-8"))
        self.assertIn("uma skill universal", ref.read_text(encoding="utf-8").lower())

    def test_selection_is_not_installed_state(self):
        data = json.loads((ROOT / "engine/ubuntu_selection.json").read_text(encoding="utf-8"))
        self.assertEqual(data["count"], len(data["tools"]))
        self.assertTrue(all(not tool["certified_on_vps"] for tool in data["tools"]))
        self.assertTrue(all(not tool["installed_on_vps"] for tool in data["tools"]))

if __name__ == "__main__":
    unittest.main()
