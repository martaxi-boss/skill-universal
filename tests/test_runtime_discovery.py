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

    def test_browser_probe_is_read_only_and_bounded_to_ferrari(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            owned=home/".runtime/browsers/chromium_headless_shell-999"
            (owned/"chrome-headless-shell-linux64").mkdir(parents=True)
            browser=owned/"chrome-headless-shell-linux64/chrome-headless-shell"
            browser.write_text("dummy browser marker")
            other=home/"other-project/chromium-222/chrome-linux"
            other.mkdir(parents=True)
            (other/"chrome").write_text("must be ignored")
            with patch("engine.runtime_discovery.shutil.which",
                       side_effect=lambda name: "/usr/bin/chromium" if name=="chromium" else None):
                result=runtime_discovery.browser_discovery(home=home)
            self.assertEqual(result["system_browser_executables"]["chromium"]["path"],
                             "/usr/bin/chromium")
            self.assertEqual(len(result["ferrari_browser_cache"]),1)
            self.assertEqual(result["ferrari_browser_cache"][0]["path"],str(browser))
            self.assertNotIn("other-project",str(result))

    def test_browser_probe_does_not_execute_or_install(self):
        with tempfile.TemporaryDirectory() as d:
            with patch("engine.runtime_discovery.shutil.which",return_value=None):
                with patch("engine.runtime_discovery.subprocess.run") as invoke:
                    result=runtime_discovery.browser_discovery(home=d)
            self.assertFalse(result["system_browser_executables"])
            self.assertEqual(result["ferrari_browser_cache"],[])
            invoke.assert_not_called()

    def test_browser_probe_is_reported_as_observation_not_action(self):
        result=runtime_discovery.discover(home=Path("/nonexistent/ferrari-browser-test"),
                                          system_npm_roots=())
        self.assertIn("browsers",result)
        self.assertIn("scope",result["browsers"])


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
                # A synthetic manifest-only test must not inherit the real
                # Ferrari Vite/IFC executors installed on the VPS.
                with patch("engine.professional_tools.vite_available",return_value=False):
                    with patch("engine.professional_tools.bim_available",return_value=False):
                        report=tool_runtime.inventory()
        vite=next(p for p in report["programs"] if p["id"]=="vite")
        self.assertTrue(vite["installed"])
        self.assertEqual(vite["detection"],"npm_package")
        self.assertEqual(vite["status"],"installed_unintegrated")
        self.assertEqual(vite["actions"],[])
        self.assertEqual(report["registered_actions"],22)


if __name__=="__main__":
    unittest.main()
