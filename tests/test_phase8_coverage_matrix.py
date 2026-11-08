"""F8: guard the published functional matrix against fictitious actions or counts."""
import json
from pathlib import Path
import re
import unittest

from engine import catalog_registry, ferrari

ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/"docs/FASE8_MATRIZ_COBERTURA_20261105.md"
MANIFEST=ROOT/"engine/catalog.json"

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
        expected={a["id"] for a in catalog_registry.read_catalog(MANIFEST)["actions"]}
        self.assertEqual(len(found),40)
        self.assertEqual(set(found),expected)
        self.assertEqual(len(set(found)),len(found))

    def test_all_base_operations_are_listed_and_not_misrepresented(self):
        text=DOC.read_text(encoding="utf-8")
        base=text.split("## Operações base (12)",1)[1].split("## Matriz de ações",1)[0]
        found=re.findall(r"`([a-z0-9-]+)`",base.splitlines()[2])
        # The Fase 8 matrix is a historical certificate for its 12 base
        # operations, not a mutable count of newer certified functions.
        self.assertEqual(len(found),12)
        self.assertEqual(set(found),set(ferrari.OPS)-{"audio-transcribe","image-analyze","librecad-dxf-pdf","qgis-buffer-5m","godot-starter","docling-docx-markdown","valkey-kv-test"})
        self.assertIn("audio-transcribe",ferrari.OPS)

    def test_private_counts_and_missing_tools_are_explicit(self):
        s=DOC.read_text(encoding="utf-8")
        for marker in ("47/56","29","18","9/56","108 registos",
                       "Não detetado privado","Fase 8 CERTIFICADA",
                       "/srv/projects/skill-universal/"):
            self.assertIn(marker,s)
        for name in ("ytdlp","librecad","qgis","audacity","obs","solvespace",
                     "synfig","openshot","penpot"):
            self.assertIn("`"+name+"`",s)

    def test_proof_separated_from_presence(self):
        s=DOC.read_text(encoding="utf-8")
        self.assertIn("não confirma que *todas* as ações",s)
        self.assertIn("sem fallback aos binários globais",s.lower())
        self.assertIn("FERRARI_SKILL_END_TO_END=PASS",s)

if __name__=="__main__":
    unittest.main()
