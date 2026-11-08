"""Ferrari shared runtime evidence: version checks do not pretend ABI certification."""
from pathlib import Path
import os
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

from engine import runtime_health, tool_runtime

RUNTIMES = {
    "python-3.12": ("Python 3.12", "FERRARI_PYTHON_READY:3.12.16"),
    "node-22": ("Node 22", "FERRARI_NODE_READY:22.23.4"),
    "java-25": ("Java 25", 'openjdk version "25.0.5" 2026-10-21'),
}
PATHS = {
    "python-3.12": "runtimes/python3.12/bin/python3.12",
    "node-22": "runtimes/node-22.23.4/bin/node",
    "java-25": "runtimes/jdk-25.0.5_8/bin/java",
}


class PrivateRuntimeHealthTests(unittest.TestCase):
    def _entry(self, name, root):
        path = root / PATHS[name]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("fixture runtime, never executed")
        path.chmod(0o755)
        return {"id": name, "version": name,
                "path": str(path)}

    def test_expected_probes_use_private_binary_without_shell_or_network(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)
            for name, (_label, output) in RUNTIMES.items():
                entry=self._entry(name,home)
                returned=SimpleNamespace(returncode=0,stdout=output,stderr="")
                with patch.object(runtime_health.subprocess, "run", return_value=returned) as run:
                    evidence=runtime_health.probe_dependency(entry,home)
                self.assertEqual(evidence["status"],"runtime_smoke_pass")
                self.assertTrue(evidence["runtime_smoke_pass"])
                self.assertFalse(evidence["compatibility_certified"])
                args,kw=run.call_args
                self.assertEqual(args[0][0],entry["path"])
                self.assertEqual(tuple(args[0][1:]),runtime_health.COMMANDS[name])
                self.assertFalse(kw["shell"])
                self.assertLessEqual(kw["timeout"],8)
                self.assertEqual(kw["cwd"],str(home))

    def test_wrong_version_fails_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)
            entry=self._entry("node-22",home)
            with patch.object(runtime_health.subprocess, "run",
                    return_value=SimpleNamespace(returncode=0,
                        stdout="FERRARI_NODE_READY:22.1.0",stderr="")):
                evidence=runtime_health.probe_dependency(entry,home)
            self.assertEqual(evidence["status"],"runtime_smoke_failed")
            self.assertFalse(evidence["runtime_smoke_pass"])

    def test_path_outside_project_and_missing_binary_do_not_execute(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)/"ferrari"
            home.mkdir()
            other=Path(folder)/"outside"
            other.write_bytes(b"dummy")
            other.chmod(0o755)
            with patch.object(runtime_health.subprocess,"run") as run:
                evidence=runtime_health.probe_dependency(
                    {"id":"python-3.12","path":str(other),"version":"3.12"},home)
                self.assertFalse(evidence["executed"])
                run.assert_not_called()
            broken=home/"runtimes/python3.12/bin/python3.12"
            broken.parent.mkdir(parents=True)
            broken.symlink_to(other)
            with patch.object(runtime_health.subprocess,"run") as run:
                evidence=runtime_health.probe_dependency(
                    {"id":"python-3.12","path":str(broken),"version":"3.12"},home)
                self.assertFalse(evidence["executed"])
                run.assert_not_called()

    def test_shared_dependency_status_follows_execution_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)
            for name in PATHS:
                self._entry(name,home)
            catalog={
                "tools":[{"id":"python","requires":["python-3.12"]},
                         {"id":"node","requires":["node-22"]},
                         {"id":"java","requires":["java-25"]}],
                "dependencies":[
                    {"id":name,"version":name,"relative_path":PATHS[name],
                     "reuse_key":name+"-x86_64"} for name in PATHS]}
            def probe(entry,_home):
                return {"status":"runtime_smoke_pass","runtime_smoke_pass":True,
                        "executed":True, "compatibility_certified":False}
            with patch.object(tool_runtime,"HOME",home), patch.object(
                runtime_health,"probe_dependency",side_effect=probe) as invoke:
                results=tool_runtime.shared_dependencies(catalog)
            self.assertEqual(invoke.call_count,3)
            self.assertTrue(all(x["status"]=="runtime_smoke_pass" for x in results))
            self.assertTrue(all(x["present"] for x in results))
            self.assertTrue(all(x["compatibility_certified"] is False for x in results))

    def test_all_173_catalogued_programs_are_reported_without_claiming_upstream_install(self):
        from engine import catalog_registry
        catalogue=catalog_registry.read_catalog()
        observed=tool_runtime.inventory()
        all_ids={x["id"] for x in catalogue["tools"]}
        records=observed["programs"]
        self.assertEqual(len(all_ids),173)
        self.assertEqual(len(records),173)
        self.assertEqual({x["id"] for x in records},all_ids)
        self.assertNotIn("REA",{x["id"] for x in records})
        self.assertIn("rea",{x["id"] for x in records})
        self.assertEqual(observed["programs_catalogued"],173)
        self.assertEqual(observed["programs_preflighted"],173)
        unadmitted=[x for x in catalogue["tools"] if
                    x.get("admission")=="upstream_candidate_unverified"]
        self.assertEqual(observed["upstream_candidates_not_admitted"],len(unadmitted))
        for item in records:
            if item["admission"]=="upstream_candidate_unverified":
                self.assertEqual(item["status"],"candidate_not_admitted")
                self.assertEqual(item["actions"],[])
                self.assertEqual(item["base_operations"],[])

    def test_catalogue_runtime_names_not_misclassified_missing(self):
        with tempfile.TemporaryDirectory() as folder:
            home=Path(folder)
            for name in PATHS:
                self._entry(name,home)
            ecosystems={"python":{"tools":{},"detected":0},
                        "npm":{"tools":{},"detected":0},
                        "containers":{"tools":{},"runtimes":{}},
                        "browsers":{"ferrari_browser_cache":[]}}
            def probe(entry,_home):
                return {"status":"runtime_smoke_pass","runtime_smoke_pass":True,
                        "executed":True,"compatibility_certified":False}
            with patch.object(tool_runtime,"HOME",home),patch.object(
                    tool_runtime.runtime_discovery,"discover",return_value=ecosystems),patch.object(
                    runtime_health,"probe_dependency",side_effect=probe), patch.object(
                    tool_runtime,"executable",return_value=None), patch(
                    "engine.professional_tools.vite_available",return_value=False),patch(
                    "engine.professional_tools.bim_available",return_value=False):
                record=tool_runtime.inventory()
            for name in ("python","node","java"):
                row=next(x for x in record["programs"] if x["id"]==name)
                self.assertTrue(row["installed"],name)
                self.assertEqual(row["status"],"runtime_dependency_verified",name)
                self.assertEqual(row["integration_role"],"shared_runtime",name)
                self.assertEqual(row["actions"],[],name)
            self.assertEqual(record["registered_actions"],40)


if __name__=="__main__":
    unittest.main()
