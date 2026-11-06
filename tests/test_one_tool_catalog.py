"""Ferrari: exactly one authoritative catalog, no duplicate tool or dependency registry."""
import json
from pathlib import Path
import unittest

from engine import core, ferrari, tool_runtime

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "engine/catalog.json"
LEGACY = (
    "ubuntu_selection.json", "tool_actions.json", "providers.json",
    "ferrari_registry.json", "ferrari_expansion.json",
)

class OneToolCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(CATALOG.read_text(encoding="utf-8"))

    def test_single_source_of_truth_with_original_evidence_preserved(self):
        doc = self.data
        self.assertEqual(doc["schema"], 2)
        self.assertEqual(doc["counts"]["unique_tools"], 174)
        self.assertEqual(len(doc["tools"]), 174)
        self.assertEqual(len(doc["actions"]), 40)
        self.assertEqual(len(doc["providers"]), 12)
        self.assertEqual(len([t for t in doc["tools"] if "core" in t]), 71)
        self.assertEqual(len([t for t in doc["tools"] if "ubuntu" in t]), 56)
        self.assertEqual(len([t for t in doc["tools"] if "upstream" in t]), 125)
        self.assertEqual(len({t["id"] for t in doc["tools"]}), len(doc["tools"]))
        self.assertTrue(all(t["id"] == t["id"].lower() for t in doc["tools"]))
        self.assertTrue(all(t.get("ubuntu", {}).get("certified_on_vps") is not True
                            for t in doc["tools"] if "ubuntu" in t))

    def test_all_consumers_work_from_same_catalog(self):
        self.assertEqual(len(tool_runtime.specs()), 40)
        self.assertEqual(len(core.inventory()), 71)
        self.assertEqual(len(ferrari.registry()), 125)
        self.assertEqual(len(ferrari.ubuntu_selection()), 56)
        self.assertEqual(len(core.providers()), 12)
        inv = tool_runtime.inventory()
        self.assertEqual(inv["registered_actions"], 40)
        self.assertEqual(inv["selected"], 56)
        self.assertTrue(any(p["id"] == "rea" for p in inv["programs"]))

    def test_no_five_obsolete_metadata_sources(self):
        for name in LEGACY:
            with self.subTest(name=name):
                self.assertFalse((ROOT / "engine" / name).exists(),
                                 "Old catalog must not compete with engine/catalog.json")

    def test_actions_and_dependency_links_are_registered(self):
        doc = self.data
        programs = {t["id"]: t for t in doc["tools"]}
        action_ids = set()
        for action in doc["actions"]:
            self.assertNotIn(action["id"], action_ids)
            action_ids.add(action["id"])
            self.assertIn(action["tool"].lower(), programs)
        dependencies = {x["id"]: x for x in doc["dependencies"]}
        self.assertEqual(len(dependencies), len(doc["dependencies"]))
        self.assertEqual({x["reuse_key"] for x in dependencies.values()},
                         {x["reuse_key"] for x in doc["dependencies"]})
        for item in doc["dependencies"]:
            path = Path(item["relative_path"])
            self.assertFalse(path.is_absolute())
            self.assertNotIn("..", path.parts)
            self.assertNotIn("/srv/projects/", item["relative_path"])
            self.assertTrue(item["status"].startswith("requires_"))
        for program in doc["tools"]:
            for dep in program.get("requires", []):
                self.assertIn(dep, dependencies)
        self.assertEqual(programs["rea"]["requires"], programs["ruflo"]["requires"])
        self.assertEqual(programs["ghidra"]["requires"], programs["jadx"]["requires"])
        self.assertTrue(doc["dependency_policy"]["never_share_with_other_projects"])

    def test_original_rea_is_dynamic_and_no_second_engine(self):
        rea = next(t for t in self.data["tools"] if t["id"] == "rea")
        self.assertEqual(rea["mcp"]["discovery"], "tools/list")
        self.assertEqual(rea["mcp"]["invocation"], "tools/call")
        self.assertIsNone(rea["mcp"]["static_count"])
        self.assertEqual(rea["mcp"]["transport"], "engine/rea_mcp.py")
        self.assertEqual(self.data["ownership"]["project"], "skill-universal")

if __name__ == "__main__":
    unittest.main()
