"""F8: guard the published functional matrix against fictitious actions or counts."""
import json
from pathlib import Path
import re
import unittest

from engine import ferrari

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"docs/FASE8_MATRIZ_COBERTURA_20261105.md"
MANIFEST=ROOT/"engine/tool_actions.json"

class FerrariPhase8Coverage(unittest.TestCase):
    def test_every_typed_action_appears_once_in_the_domain_matrix(self):
        text=DOC.read_text(encoding="utf-8")
        section=text.split("## Matriz de ações tipadas (40) e evidências por domínio",1)[1]
        section=section.split("## Nove candidatos ainda não privados",1)[0]
        found=[]
        for row in section.splitlines():
            if row.startswith("| **"):
                cells=row.split("|")
                self.assertGreaterEqual(len(cells),4)
                found+=re.findall(r"`([a-z0-9-]+)`",cells[2])
        expected={a["id"] for a in json.loads(MANIFEST.read_text())["actions"]}
        self.assertEqual(len(found),40)
        self.assertEqual(set(found),expected)
        self.assertEqual(len(set(found)),len(found))

    def test_all_base_operations_are_listed_and_not_misrepresented(self):
        text=DOC.read_text(encoding="utf-8")
        base=text.split("## Operações base (12)",1)[1].split("## Matriz de ações",1)[0]
        found=re.findall(r"`([a-z0-9-]+)`",base.splitlines()[2])
        self.assertEqual(len(found),len(ferrari.OPS))
        self.assertEqual(set(found),set(ferrari.OPS))

    def test_private_counts_and_missing_tools_are_explicit(self):
        s=DOC.read_text(encoding="utf-8")
        for marker in ("47/56","29","18","9/56","108 registos",
                       "Não detetado privado","não declara a Fase 8 concluída",
                       "/srv/projects/skill-universal/"):
            self.assertIn(marker,s)
        for name in ("ytdlp","librecad","qgis","audacity","obs","solvespace",
                     "synfig","openshot","penpot"):
            self.assertIn("`"+name+"`",s)

    def test_proof_separated_from_presence(self):
        s=DOC.read_text(encoding="utf-8")
        self.assertIn("não confirma que *todas* as ações",s)
        self.assertIn("sem fallback aos binários globais",s)
        self.assertIn("FERRARI_SKILL_END_TO_END=PASS",s)

if __name__=="__main__":
    unittest.main()
