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
        self.assertEqual(len(names), 220)
        self.assertEqual(len(set(names)), len(names))
        self.assertEqual(self.doc["counts"]["unique_tools"], 176)
        self.assertEqual(self.doc["counts"]["mcp_capabilities"], 220)
        self.assertEqual(self.doc["counts"]["mcp_source_advertised"], 229)
        self.assertEqual(self.doc["counts"]["excluded_paid_or_demo_mcp_capabilities"], 9)
        self.assertEqual(self.doc["counts"]["all_catalog_entries"], 396)
        self.assertEqual(len(self.doc["tools"]) + len(names), 396)
        excluded = self.doc["mcp_capabilities"]["excluded_paid_or_demo_names"]
        self.assertEqual(len(excluded), 9)
        self.assertFalse(set(names) & set(excluded))
        self.assertIn("inspect_jeb_client", excluded)
        self.assertIn("current_document", excluded)
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
        # The upstream REA advertises all 229, but the Ferrari must silently
        # exclude the nine commercial-only/demo-dependent MCP endpoints.
        fake_live.extend({"name": name} for name in self.doc["mcp_capabilities"]["excluded_paid_or_demo_names"])
        with patch.object(rea_mcp, "discover_tools", return_value=fake_live):
            result = tool_runtime.unified_catalog(inventory_now=seed)
        self.assertEqual(result["rea"]["status"], "rea_in_sync")
        self.assertEqual(result["counts"]["all_catalog_entries"], 396)
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 220)
        self.assertEqual(result["counts"]["rea_mcp_advertised_raw"], 229)
        self.assertEqual(result["counts"]["rea_excluded_paid_observed"], 9)
        self.assertEqual(result["counts"]["no_cost_providers"], 8)
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
        self.assertEqual(result["rea"]["unexpected_live_names"], ["unapproved_new_tool"])
        self.assertEqual(len(result["rea"]["missing_live_names"]), 219)
        self.assertNotIn("rea:unapproved_new_tool", [x["id"] for x in result["entries"]])

    def test_commercial_rea_calls_denied_by_the_single_catalog(self):
        for name in self.doc["mcp_capabilities"]["excluded_paid_or_demo_names"]:
            with self.subTest(name=name):
                with self.assertRaisesRegex(ValueError, "not admitted"):
                    rea_mcp.validate_requests([{
                        "method": "tools/call",
                        "params": {"name": name, "arguments": {}}
                    }])
        rea_mcp.validate_requests([{
            "method": "tools/call",
            "params": {"name": "inspect_elf_notes", "arguments": {}}
        }])

    def test_unavailable_rea_is_not_falsely_marked_operational(self):
        with patch.object(rea_mcp, "discover_tools", side_effect=RuntimeError("missing")):
            result = tool_runtime.unified_catalog(inventory_now={"programs": [], "ecosystems": {}})
        self.assertEqual(result["rea"]["status"], "rea_unavailable")
        self.assertEqual(result["counts"]["rea_mcp_discovered_now"], 0)
        self.assertTrue(all(not x["selectable"] for x in result["entries"]
                            if x["kind"] == "mcp_capability"))

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
                        "counts": {"all_catalog_entries": 405}}
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
                self.assertEqual(json.loads(archive.read("artifacts/catalog.json"))["counts"]["all_catalog_entries"], 405)

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
