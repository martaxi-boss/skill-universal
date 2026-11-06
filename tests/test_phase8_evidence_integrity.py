"""F8 integrity guard: every claimed real test must have a private traceable ZIP proof."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MATRIX = ROOT / "docs/FASE8_MATRIZ_COBERTURA_20261105.md"
EVIDENCE = ROOT / "docs/FASE8_EVIDENCIAS_FUNCIONAIS_20261105.json"
MANIFEST = ROOT / "engine/tool_actions.json"
PRIVATE_ROOT = "/srv/projects/skill-universal/"


class FerrariF8EvidenceIntegrity(unittest.TestCase):
    def setUp(self):
        self.data = json.loads(EVIDENCE.read_text(encoding="utf-8"))
        self.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        self.matrix = MATRIX.read_text(encoding="utf-8")

    def test_exact_manifest_and_statuses(self):
        spec = {x["id"]: x for x in self.manifest["actions"]}
        rows = self.data["actions"]
        self.assertEqual(len(spec), 40)
        self.assertEqual(len(rows), 40)
        self.assertEqual({x["action"] for x in rows}, set(spec))
        self.assertEqual(len({x["action"] for x in rows}), 40)
        self.assertTrue(all(x["registered"] and x["private_executor_in_f7_inventory"] for x in rows))
        verified = [x for x in rows if x["phase8_individual_e2e_verified"]]
        self.assertEqual(len(verified), self.data["phase8_new_individual_e2e"])
        self.assertEqual(40 - len(verified), self.data["without_phase8_individual_e2e"])
        self.assertEqual(self.data["status"], "phase8_40_of_40_individual_real_evidence_verified")
        self.assertEqual(len(verified), 40)
        self.assertEqual(self.data["without_phase8_individual_e2e"], 0)
        self.assertIn(f"({len(verified)}/40)", self.matrix)

    def test_proofs_have_real_private_executors_and_source_run(self):
        section = self.matrix.split("## Provas funcionais individuais verificadas na Fase 8", 1)[1]
        section = section.split("## Nove candidatos ainda não privados", 1)[0]
        for x in self.data["actions"]:
            if x["phase8_individual_e2e_verified"]:
                with self.subTest(action=x["action"]):
                    ev = x["evidence"]
                    self.assertIsInstance(ev["vps_run_id"], int)
                    self.assertGreater(ev["vps_run_id"], 42000000000)
                    self.assertEqual(ev["url"], f"https://github.com/martaxi-boss/VPS/actions/runs/{ev['vps_run_id']}")
                    self.assertTrue(ev["executor"].startswith(PRIVATE_ROOT))
                    self.assertFalse("/../" in ev["executor"])
                    self.assertRegex(ev["artifact_basename"], r"^[a-zA-Z0-9._-]+$")
                    self.assertGreater(len(ev["verified_result"]), 5)
                    self.assertIn("`"+x["action"]+"`",section)
                    self.assertIn("#"+str(ev["vps_run_id"]),section)
            else:
                self.assertIsNone(x["evidence"])

    def test_real_android_physical_install_has_dedicated_evidence(self):
        row = next(x for x in self.data["actions"] if x["action"] == "android-adb-install-apk")
        self.assertTrue(row["phase8_individual_e2e_verified"])
        proof = row["evidence"]
        self.assertEqual(proof["vps_run_id"], 42128892714)
        self.assertIn("Success", proof["verified_result"])
        self.assertIn("com.example.empty9patch", proof["input"])
        self.assertIn("42128892714", self.matrix)
        self.assertIn("Fase 8 CERTIFICADA", self.matrix)

    def test_no_vps_global_install_or_total_certification_claim(self):
        self.assertEqual(self.data["vps_root"], PRIVATE_ROOT.rstrip("/"))
        for phrase in ("Fase 8 CERTIFICADA", "sem fallback aos binários globais",
                       "Não detetado privado"):
            self.assertIn(phrase, self.matrix.lower() if phrase.startswith("sem ") else self.matrix)
        self.assertNotIn("fase8_full_certified",self.data["status"])


if __name__ == "__main__":
    unittest.main()
