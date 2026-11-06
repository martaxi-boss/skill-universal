"""One Ferrari catalogue for Ubuntu programs, dependencies and live REA MCP tools."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch

from engine import rea_mcp, skill_job, tool_runtime

ROOT = Path(__file__).resolve().parents[1]


class UnifiedCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads((ROOT / "engine/catalog.json").read_text(encoding="utf-8"))

    def test_all_real_rea_names_appear_once_in_same_authoritative_file(self):
        names = self.doc["mcp_capabilities"]["names"]
        self.assertEqual(len(names), 225)
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(self.doc["counts"]["unique_tools"], 176)
        self.assertEqual(self.doc["counts"]["mcp_capabilities"], 225)
        self.assertEqual(self.doc["counts"]["all_catalog_entries"], 401)
        self.assertEqual(len(self.doc["tools"]) + len(names), 401)
        self.assertEqual(self.doc["mcp_capabilities"]["discovery"], "tools/list")
        self.assertEqual(self.doc["mcp_capabilities"]["invocation"], "tools/call")
        self.assertEqual(self.doc["mcp_capabilities"]["verified_vps_workflow_run"], 42269934831)
        self.assertFalse(any(name.startswith("rea:") for name in names))

    def test_free_only_ubuntu_admission_and_one_dependency_registry(self):
        self.assertEqual(len(self.doc["providers"]), 8)
        self.assertTrue(all(p["cost"] in {"free-tier", "open-source", "built-in"}
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

    def test_unified_runtime_real_name_reconciliation(self):
        names = self.doc["mcp_capabilities"]["names"]
        fake_live = [{"name": name, "title": name, "inputSchema": {"type": "object"},
                      "annotations": {"readOnlyHint": True}} for name in names]
        seed = {"programs": [], "ecosystems": {}}
        with patch.object(rea_mcp, "discover_tools", return_value=fake_live):
            result = tool_runtime.unified_catalog(inventory_now=seed)
        self.assertEqual(result["rea"]["status"], "rea_in_sync")
        self.assertEqual(result["counts"]["all_catalog_entries"], 401)
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 225)
        self.assertEqual(result["counts"]["no_cost_providers"], 8)
        self.assertEqual(sum(x["kind"] == "mcp_capability" for x in result["entries"]), 225)
        self.assertTrue(all(x["selectable"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))
        self.assertTrue(all(not x["installed_separately"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))

    def test_unexpected_live_rea_tools_are_not_silently_admitted(self):
        fake_live = [{"name": "inspect_analysis_settings"}, {"name": "unapproved_new_tool"}]
        with patch.object(rea_mcp, "discover_tools", return_value=fake_live):
            result = tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_catalog_drift")
        self.assertEqual(result["rea"]["unexpected_live_names"], ["unapproved_new_tool"])
        self.assertEqual(len(result["rea"]["missing_live_names"]), 224)
        self.assertNotIn("rea:unapproved_new_tool", [x["id"] for x in result["entries"]])

    def test_unavailable_rea_is_not_falsely_marked_operational(self):
        with patch.object(rea_mcp, "discover_tools", side_effect=RuntimeError("missing")):
            result = tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_unavailable")
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 0)
        self.assertTrue(all(not x["selectable"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))

    def test_commercial_jeb_bridge_excluded_even_when_rea_advertises_it(self):
        names = self.doc["mcp_capabilities"]["names"]
        commercial = [
            "inspect_jeb_client", "open_jeb_project",
            "list_jeb_units", "decompile_jeb_item",
        ]
        self.assertEqual(self.doc["mcp_capabilities"]["excluded_paid_provider_ids"], ["jeb"])
        self.assertTrue(all(name not in names for name in commercial))
        advertised = [{"name": name} for name in names + commercial]
        with patch.object(rea_mcp, "discover_tools", return_value=advertised):
            result = tool_runtime.unified_catalog(
                inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_in_sync")
        self.assertEqual(result["rea"]["excluded_paid_live_names"], sorted(commercial))
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 229)
        self.assertEqual(result["counts"]["rea_mcp_paid_excluded_now"], 4)
        self.assertEqual(result["counts"]["rea_mcp_capabilities"], 225)
        self.assertFalse(any("jeb" in item["id"].split("_")
                             for item in result["entries"]))
        for name in commercial:
            with self.assertRaisesRegex(ValueError, "Paid JEB"):
                rea_mcp.validate_requests([{"method": "tools/call",
                                            "params": {"name": name, "arguments": {}}}])

    def test_paid_provider_fails_closed_before_rea_discovery(self):
        modified = copy.deepcopy(self.doc)
        modified["providers"].append({"id": "new-paid", "kind": "cloud", "cost": "paid"})
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "catalog.json"
            path.write_text(json.dumps(modified), encoding="utf-8")
            with patch.object(tool_runtime, "CATALOG_PATH", path):
                with self.assertRaisesRegex(ValueError, "Paid or unverified-cost"):
                    tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})

    def test_existing_inventory_request_produces_unified_zip_no_new_bridge(self):
        self.assertIsNone(skill_job.validate_job(
            {"version": 1, "id": "catalog-read-001", "kind": "inventory"}))
        fake_inventory = {"selected": 56, "registered_actions": 40, "programs": [],
                          "ecosystems": {}, "shared_dependencies": []}
        fake_catalog = {"source": "engine/catalog.json",
                        "counts": {"all_catalog_entries": 401}}
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
                self.assertEqual(json.loads(archive.read("artifacts/catalog.json"))["counts"]["all_catalog_entries"], 401)

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
