"""One Ferrari catalogue for Ubuntu programs, dependencies and live REA MCP tools."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from engine import catalog_registry, rea_mcp, skill_job, tool_runtime

ROOT = Path(__file__).resolve().parents[1]


class UnifiedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = catalog_registry.read_catalog()

    def test_all_real_rea_names_appear_once_in_same_authoritative_file(self):
        names = self.doc["mcp_capabilities"]["names"]
        self.assertEqual(len(names), 220)
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(self.doc["counts"]["unique_tools"], 173)
        self.assertEqual(self.doc["counts"]["mcp_capabilities"], 220)
        self.assertEqual(self.doc["counts"]["all_catalog_entries"], 450)
        self.assertEqual(len(self.doc["tools"]) + len(self.doc["functions"]) +
                         len(self.doc["providers"]) + len(self.doc["dependencies"]), 450)
        self.assertEqual(self.doc["mcp_capabilities"]["discovery"], "tools/list")
        self.assertEqual(self.doc["mcp_capabilities"]["invocation"], "tools/call")
        self.assertEqual(self.doc["mcp_capabilities"]["verified_vps_workflow_run"], 42269934831)
        self.assertFalse(any(name.startswith("rea:") for name in names))

    def test_one_persisted_universal_function_registry_without_rea_partition(self):
        """All programs use exactly one root functions list in one JSON file."""
        raw = json.loads((ROOT / "engine/catalog.json").read_text(encoding="utf-8"))
        self.assertEqual(raw["functions_schema"], 1)
        self.assertNotIn("actions", raw)
        self.assertNotIn("names", raw["mcp_capabilities"])
        self.assertTrue(all("base_operations" not in tool for tool in raw["tools"]))
        self.assertEqual(len(raw["functions"]), 272)
        self.assertEqual(len({f["id"] for f in raw["functions"]}), 272)
        self.assertEqual(len(raw["tools"]) + len(raw["functions"]) +
                         len(raw["dependencies"]) + len(raw["providers"]), 450)
        self.assertEqual({f["kind"] for f in raw["functions"]},
                         {"operation", "invoke", "mcp_capability"})
        self.assertEqual({f["program"] for f in raw["functions"]
                          if f["kind"] == "mcp_capability"}, {"rea"})
        self.assertEqual(len(self.doc["actions"]), 40)
        self.assertEqual(len(self.doc["mcp_capabilities"]["names"]), 220)

    def test_free_only_ubuntu_admission_and_one_dependency_registry(self):
        self.assertEqual(len(self.doc["providers"]), 2)
        self.assertTrue(all(p["cost"] in {"open-source", "built-in"}
                            and p["admission"] == "free_only_no_paid_fallback"
                            for p in self.doc["providers"]))
        names = {p["id"] for p in self.doc["providers"]}
        self.assertFalse(names.intersection({
            "host-model", "huggingface-inference", "nvidia-nim-dev", "pollinations"}))
        self.assertEqual(len({x["id"] for x in self.doc["dependencies"]}),
                         len(self.doc["dependencies"]))
        self.assertTrue(all(t["admission"] in {
            "ubuntu_reviewed_or_core", "upstream_candidate_unverified"}
                            for t in self.doc["tools"]))

    def test_non_equivalent_closed_entries_stay_out(self):
        program_ids = {t["id"] for t in self.doc["tools"]}
        provider_ids = {p["id"] for p in self.doc["providers"]}
        self.assertFalse({"nmap", "vscode"} & program_ids)
        self.assertEqual(provider_ids, {"imagemagick-local", "svg-local"})
        self.assertEqual(self.doc["counts"]["upstream_registry"], 122)
        self.assertEqual(self.doc["expansion_metadata"]["count"], 72)
        self.assertEqual(self.doc["admission_policy"]["cost"],
                         "local_open_source_or_builtin_only_no_cloud_providers")
        self.assertEqual(self.doc["counts"]["all_catalog_entries"], 450)

    def test_closed_cloud_provider_fails_closed_even_with_free_tier(self):
        modified = copy.deepcopy(self.doc)
        modified["providers"].append({
            "id": "closed-cloud", "kind": "cloud", "cost": "free-tier",
        })
        modified["counts"]["all_catalog_entries"] += 1
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "catalog.json"
            path.write_text(json.dumps(modified), encoding="utf-8")
            with patch.object(tool_runtime, "CATALOG_PATH", path):
                with self.assertRaisesRegex(ValueError, "cloud or closed-source"):
                    tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})

    def test_unified_runtime_real_name_reconciliation(self):
        names = self.doc["mcp_capabilities"]["names"]
        fake_live = [{"name": name, "title": name, "inputSchema": {"type": "object"},
                      "annotations": {"readOnlyHint": True}} for name in names]
        seed = {"programs": [], "ecosystems": {}}
        with patch.object(rea_mcp, "discover_tools", return_value=fake_live):
            result = tool_runtime.unified_catalog(inventory_now=seed)
        self.assertEqual(result["rea"]["status"], "rea_in_sync")
        self.assertEqual(result["counts"]["all_catalog_entries"], 450)
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 220)
        self.assertEqual(result["counts"]["no_cost_providers"], 2)
        self.assertEqual(sum(x["kind"] == "mcp_capability" for x in result["entries"]), 220)
        self.assertTrue(all(x["selectable"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))
        self.assertTrue(all(not x["installed_separately"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))

    def test_unexpected_live_rea_tools_are_not_silently_admitted(self):
        fake_live = [{"name": "inspect_analysis_settings"}, {"name": "unapproved_new_tool"}]
        with patch.object(rea_mcp, "discover_tools", return_value=fake_live):
            result = tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_catalog_drift")
        self.assertEqual(result["rea"]["unlisted_source_count"], 1)
        self.assertNotIn("rea:unapproved_new_tool", [x["id"] for x in result["entries"]])
        self.assertEqual(len(result["rea"]["missing_live_names"]), 219)
        self.assertNotIn("rea:unapproved_new_tool", [x["id"] for x in result["entries"]])

    def test_unavailable_rea_is_not_falsely_marked_operational(self):
        with patch.object(rea_mcp, "discover_tools", side_effect=RuntimeError("missing")):
            result = tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_unavailable")
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 0)
        self.assertTrue(all(not x["selectable"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))

    def test_deleted_upstream_names_are_never_in_ferrari_catalog_or_dispatch(self):
        names = self.doc["mcp_capabilities"]["names"]
        parent = self.doc["mcp_capabilities"]
        self.assertEqual(len(names), 220)
        self.assertNotIn("excluded_paid_or_demo_names", parent)
        self.assertNotIn("excluded_paid_provider_ids", parent)
        self.assertNotIn("exclusion_reason", parent)
        self.assertNotIn("excluded_paid_or_demo_mcp_capabilities", self.doc["counts"])
        self.assertEqual(self.doc["counts"]["mcp_source_advertised"], 229)
        unlisted = ["unlisted_tool_%d" % i for i in range(9)]
        advertised = [{"name": name} for name in names + unlisted]
        with patch.object(rea_mcp, "discover_tools", return_value=advertised):
            result = tool_runtime.unified_catalog(
                inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_in_sync")
        self.assertEqual(result["rea"]["unlisted_source_count"], 9)
        self.assertNotIn("excluded_paid_live_names", result["rea"])
        self.assertNotIn("excluded_paid_or_demo_names", result["rea"])
        self.assertNotIn("unexpected_live_names", result["rea"])
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 220)
        self.assertEqual(result["counts"]["rea_mcp_advertised_raw"], 229)
        self.assertEqual(result["counts"]["rea_mcp_unlisted_source_now"], 9)
        self.assertEqual(result["counts"]["rea_mcp_capabilities"], 220)
        self.assertFalse(any(item["id"] in {"rea:" + n for n in unlisted}
                             for item in result["entries"]))
        for name in unlisted:
            with self.assertRaisesRegex(ValueError, "not admitted"):
                rea_mcp.validate_requests([{"method": "tools/call",
                                            "params": {"name": name, "arguments": {}}}])
        rea_mcp.validate_requests([{"method": "tools/call",
                                    "params": {"name": "inspect_elf_notes", "arguments": {}}}])

    def test_paid_provider_fails_closed_before_rea_discovery(self):
        modified = copy.deepcopy(self.doc)
        modified["providers"].append({"id": "new-paid", "kind": "cloud", "cost": "paid"})
        modified["counts"]["all_catalog_entries"] += 1
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "catalog.json"
            path.write_text(json.dumps(modified), encoding="utf-8")
            with patch.object(tool_runtime, "CATALOG_PATH", path):
                with self.assertRaisesRegex(ValueError, "Paid, cloud or closed-source"):
                    tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})

    def test_one_function_index_covers_every_integrated_ferrari_executor(self):
        """REA is not a privileged category: everything is one typed index."""
        fake_live = [{"name": name, "inputSchema": {"type": "object"}}
                     for name in self.doc["mcp_capabilities"]["names"]]
        with patch.object(rea_mcp, "discover_tools", return_value=fake_live):
            result = tool_runtime.unified_catalog(
                inventory_now={"programs": [], "ecosystems": {}})
        functions = result["functions"]
        self.assertEqual(len(functions), 272)
        self.assertEqual(result["counts"]["functions_registered"], 272)
        self.assertEqual(result["counts"]["functions_from_base_operations"], 12)
        self.assertEqual(result["counts"]["functions_from_typed_actions"], 40)
        self.assertEqual(result["counts"]["functions_from_rea_mcp"], 220)
        self.assertEqual(len({item["id"] for item in functions}), len(functions))
        self.assertEqual(functions, sorted(functions,
                          key=lambda item: (item["category"], item["id"])))
        index = {item["id"]: item for item in functions}
        self.assertEqual(index["operation:web-template"]["program"], "html-templates")
        self.assertEqual(index["operation:svg-poster"]["program"], "svg")
        self.assertEqual(index["invoke:ffmpeg-audio-wav"]["program"], "ffmpeg")
        self.assertEqual(index["invoke:pandoc-md-docx"]["program"], "pandoc")
        self.assertEqual(index["rea:inspect_elf_notes"]["program"], "rea")
        self.assertTrue(index["operation:svg-poster"]["selectable"])
        self.assertEqual({item["invocation"]["kind"] for item in functions},
                         {"operation", "invoke", "rea-mcp"})
        self.assertNotIn("certified", index["rea:inspect_elf_notes"])
        self.assertEqual(result["source"], "engine/catalog.json")

    def test_base_operations_require_an_owner_in_same_catalog(self):
        modified = copy.deepcopy(self.doc)
        modified["functions"] = [
            item for item in modified["functions"] if item["id"] != "operation:svg-poster"
        ]
        modified["counts"]["functions"] -= 1
        modified["counts"]["all_catalog_entries"] -= 1
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "catalog.json"
            path.write_text(json.dumps(modified), encoding="utf-8")
            with patch.object(tool_runtime, "CATALOG_PATH", path):
                with patch.object(rea_mcp, "discover_tools", return_value=[]):
                    with self.assertRaisesRegex(ValueError,
                                                "base operations missing"):
                        tool_runtime.unified_catalog(
                            inventory_now={"programs": [], "ecosystems": {}})

    def test_existing_inventory_request_produces_unified_zip_no_new_bridge(self):
        self.assertIsNone(skill_job.validate_job(
            {"version": 1, "id": "catalog-read-001", "kind": "inventory"}))
        fake_inventory = {"selected": 55, "registered_actions": 40, "programs": [],
                          "ecosystems": {}, "shared_dependencies": []}
        fake_catalog = {"source": "engine/catalog.json",
                        "counts": {"all_catalog_entries": 393}}
        with tempfile.TemporaryDirectory() as td:
            output = Path(td) / "job"
            with patch.object(tool_runtime, "inventory", return_value=fake_inventory):
                with patch.object(tool_runtime, "unified_catalog", return_value=fake_catalog):
                    report, code = skill_job.execute(
                        {"version": 1, "id": "catalog-read-001", "kind": "inventory"}, output)
            self.assertEqual(code, 0, report)
            self.assertEqual(report["status"], "completed")
            with zipfile.ZipFile(output / "response.zip") as archive:
                self.assertIn("artifacts/inventory.json", archive.namelist())
                self.assertIn("artifacts/catalog.json", archive.namelist())
                self.assertEqual(json.loads(archive.read("artifacts/catalog.json"))["counts"]["all_catalog_entries"], 450)

    def test_rea_live_discovery_requires_private_paths_and_no_duplicates(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td)
            good = [{"response": {"result": {"tools": [{"name": "inspect_analysis_settings"}]}}}]
            with patch.object(rea_mcp, "_resources", return_value=("rea", {})):
                with patch.object(rea_mcp, "_exchange", return_value=good):
                    result = rea_mcp.discover_tools(root=home)
                    self.assertEqual([x["name"] for x in result], ["inspect_analysis_settings"])
                bad = [{"response": {"result": {"tools": [
                    {"name": "inspect_analysis_settings"},
                    {"name": "inspect_analysis_settings"}]}}}]
                with patch.object(rea_mcp, "_exchange", return_value=bad):
                    with self.assertRaisesRegex(RuntimeError, "duplicate"):
                        rea_mcp.discover_tools(root=home)


if __name__ == "__main__":
    unittest.main()
