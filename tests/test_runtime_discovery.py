"""Read-only Ferrari ecosystem discovery tests: no installed apps are altered."""
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from engine import runtime_discovery, tool_runtime


class RuntimeDiscoveryTests(unittest.TestCase):
    def test_python_venv_module_detected_without_import(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            mod=root/".runtime/venvs/bim/lib/python3.12/site-packages/ifcopenshell"
            mod.mkdir(parents=True)
            (mod/"__init__.py").write_text("# marker only\n")
            with patch("engine.runtime_discovery.importlib.util.find_spec", return_value=None):
                result=runtime_discovery.python_presence("ifcopenshell",home=root)
            self.assertEqual(result["scope"],"ferrari_venv")
            self.assertEqual(result["verification"],"files_present_not_import_tested")

    def test_python_spec_keeps_current_interpreter_support(self):
        with patch("engine.runtime_discovery.importlib.util.find_spec",
                   return_value=SimpleNamespace(origin="/usr/lib/python3/dist-packages/cv2.so")):
            result=runtime_discovery.python_presence("cv2")
        self.assertEqual(result["scope"],"current_python")
        self.assertTrue(result["location"].endswith("cv2.so"))

    def test_npm_detects_ferrari_isolated_package(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            path=home/".runtime/npm/web/node_modules/vite/package.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"name":"vite"}\n')
            result=runtime_discovery.npm_presence("vite",home=home,system_roots=())
            self.assertEqual(result["scope"],"ferrari_npm")
            self.assertEqual(result["package"],"vite")
            self.assertEqual(result["verification"],"manifest_present_not_executed")

    def test_npm_does_not_scan_unrelated_project(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            other=home/"other-project/node_modules/next/package.json"
            other.parent.mkdir(parents=True)
            other.write_text("{}")
            self.assertIsNone(runtime_discovery.npm_presence("nextjs",home=home,system_roots=()))
            self.assertIsNone(runtime_discovery.npm_presence("unknown",home=home,system_roots=()))

    def test_container_probe_only_ferrari_label_and_no_shell(self):
        payload=('{"Labels":"org.motor-ferrari.managed=true,org.motor-ferrari.tool=penpot",'
                 '"Image":"penpot/app:latest","State":"running"}\n')
        with patch("engine.runtime_discovery.shutil.which",side_effect=lambda x: "/usr/bin/docker" if x=="docker" else None):
            with patch("engine.runtime_discovery.subprocess.run",
                       return_value=SimpleNamespace(returncode=0,stdout=payload,stderr="")) as execute:
                result=runtime_discovery.container_discovery()
        self.assertEqual(result["tools"]["penpot"][0]["state"],"running")
        self.assertEqual(result["runtimes"]["docker"]["ferrari_managed_containers"],1)
        args=execute.call_args.args[0]
        self.assertIn("label=org.motor-ferrari.managed=true",args)
        self.assertFalse(execute.call_args.kwargs["shell"])
        self.assertNotIn("exec",args)

    def test_container_probe_failure_is_diagnostic_only(self):
        with patch("engine.runtime_discovery.shutil.which",side_effect=lambda x: "/usr/bin/"+x):
            with patch("engine.runtime_discovery.subprocess.run",
                       return_value=SimpleNamespace(returncode=1,stdout="",stderr="permission denied")):
                result=runtime_discovery.container_discovery()
        self.assertEqual(result["runtimes"]["docker"]["probe"],"unavailable")
        self.assertEqual(result["tools"],{})

    def test_inventory_distinguishes_detected_package_from_adapter(self):
        evidence={"scope":"ferrari_npm","package":"vite","location":"/tmp/ferrari/vite/package.json",
                  "verification":"manifest_present_not_executed"}
        ecosystems={
            "python":{"tools":{},"detected":0},
            "npm":{"tools":{"vite":evidence},"detected":1},
            "containers":{"tools":{},"runtimes":{}},
        }
        with patch.object(tool_runtime.runtime_discovery,"discover",return_value=ecosystems):
            with patch.object(tool_runtime,"executable",return_value=None):
                report=tool_runtime.inventory()
        vite=next(p for p in report["programs"] if p["id"]=="vite")
        self.assertTrue(vite["installed"])
        self.assertEqual(vite["detection"],"npm_package")
        self.assertEqual(vite["status"],"installed_unintegrated")
        self.assertEqual(vite["actions"],[])
        self.assertEqual(report["registered_actions"],21)


if __name__=="__main__":
    unittest.main()
