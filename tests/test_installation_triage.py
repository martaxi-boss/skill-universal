"""Conservative Ferrari installation triage: no extra programs or fake action IDs."""
import unittest
from unittest.mock import patch

from engine import catalog_registry, tool_runtime


EXPECTED = {
    "reuse_existing_indirect": {"ruflo", "playwright"},
    "backend_needs_execution_proof": {"ghidra"},
    "development_dependency": {
        "nextjs", "tailwind", "bootstrap", "shadcn",
        "streamlit", "gradio", "prefect",
    },
    "optional_desktop_gui": {
        "freecad", "audacity", "obs", "solvespace", "synfig", "openshot",
    },
    "optional_model_runtime": {"comfyui"},
    "standalone_cli_candidate": {"ytdlp", "prometheus"},
}


class FerrariInstallationTriageTests(unittest.TestCase):
    def test_all_nineteen_have_one_class_and_no_fabricated_function(self):
        catalog = catalog_registry.read_catalog()
        reviewed = {t["id"]: t["integration_review"] for t in catalog["tools"]
                    if "integration_review" in t}
        self.assertEqual(len(reviewed), 19)
        self.assertEqual(set(reviewed), set().union(*EXPECTED.values()))
        for group, ids in EXPECTED.items():
            for name in ids:
                with self.subTest(program=name):
                    self.assertEqual(reviewed[name]["group"], group)
                    self.assertEqual(reviewed[name]["scope"],
                                     "triage_only_not_executable_certification")
                    self.assertTrue(reviewed[name]["route_policy"])
                    self.assertFalse(any(f["program"] == name
                                         for f in catalog["functions"]))
        self.assertEqual(catalog["counts"]["unique_tools"], 173)
        self.assertEqual(catalog["counts"]["functions"], 279)
        self.assertEqual(catalog["counts"]["all_catalog_entries"], 457)

    def test_inventory_distinguishes_present_reuse_from_missing(self):
        # Simulate two Ferrari-owned executable paths. This is NOT a VPS
        # runtime test. All other 17 remain "not detected" in this fixture.
        def private_cli(tool, binary=None):
            if tool in {"ytdlp", "prometheus"}:
                return "/srv/projects/skill-universal/tools/test-only-private"
            return None

        ecosystems = {
            "python": {"tools": {}}, "npm": {"tools": {}},
            "containers": {"tools": {}},
        }
        with patch.object(tool_runtime, "specs", return_value={}), \
             patch.object(tool_runtime, "executable", side_effect=private_cli), \
             patch.object(tool_runtime, "shared_dependencies", return_value=[]), \
             patch.object(tool_runtime, "ferrari_source_presence", return_value=None), \
             patch.object(tool_runtime.runtime_discovery, "discover",
                          return_value=ecosystems):
            inventory = tool_runtime.inventory()

        triage = inventory["installation_triage"]
        self.assertEqual(triage["classified"], 19)
        self.assertEqual(triage["detected_reuse"], 2)
        self.assertEqual(triage["not_detected_on_this_host"], 17)
        self.assertFalse(triage["reinstallation_performed"])
        self.assertEqual(triage["groups"],
                         {group: len(ids) for group, ids in sorted(EXPECTED.items())})
        programs = {p["id"]: p for p in inventory["programs"]}
        for name in set().union(*EXPECTED.values()):
            with self.subTest(program=name):
                record = programs[name]
                review = record["installation_review"]
                self.assertEqual(review["observed_installed"], name in {"ytdlp", "prometheus"})
                self.assertEqual(review["direct_operation_confirmed"], False)
                self.assertEqual(
                    review["next_install_action"],
                    "reuse_private_installation" if name in {"ytdlp", "prometheus"}
                    else "evaluate_only_for_requested_workflow",
                )
                if name in {"ytdlp", "prometheus"}:
                    self.assertEqual(record["status"], "installed_unintegrated")
                else:
                    self.assertNotEqual(record["status"], "callable")


if __name__ == "__main__":
    unittest.main()
