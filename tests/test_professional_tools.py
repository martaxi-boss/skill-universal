"""Ferrari professional adapters: bounded input, isolated runtimes, artifact checks."""
from pathlib import Path
import base64
import json
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED

from engine import ferrari, professional_tools, skill_job, tool_runtime


def _zip(path, members):
    with ZipFile(path, "w", ZIP_DEFLATED) as z:
        for name, payload in members.items():
            z.writestr(name, payload)


class FerrariProfessionalTests(unittest.TestCase):
    def test_operations_exposed_to_existing_skill_contract(self):
        self.assertIn("ifc-summary", ferrari.OPS)
        self.assertIn("vite-build", ferrari.OPS)
        raw=base64.b64encode(b"test").decode()
        for op,ext in (("ifc-summary","ifc"),("vite-build","zip")):
            job={"version":1,"id":"ferrari-pro-test","kind":"operation","operation":op,
                 "input":{"name":"demo."+ext,"content_base64":raw}}
            self.assertEqual(skill_job.validate_job(job),b"test")

    def test_ifc_extension_is_required(self):
        with self.assertRaises(ValueError):
            professional_tools.ifc_summary(Path("example.txt"),Path("/tmp/ferrari-no-create"))

    def test_ifc_bound_worker_generates_json(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"demo.ifc"
            source.write_text("IFC sample")
            def write_report(args, **kwargs):
                target=Path(args[-1])
                target.write_text(json.dumps({"format":"IFC","schema":"IFC4","total_entities":2,"entities_by_type":{"IfcProject":1,"IfcWall":1}}))
            with patch.object(professional_tools,"bim_available",return_value=True):
                with patch.object(professional_tools,"_run",side_effect=write_report) as run:
                    result=professional_tools.ifc_summary(source,root/"out")
            self.assertTrue(result[1][0].exists())
            self.assertEqual(run.call_args.args[0][1],str(professional_tools.ROOT/"engine/ifc_inspector.py"))

    def test_reject_zip_traversal_and_scripts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            for name in ("../bad.js","vite.config.js","package.json","src/.env","src/../../../pwn.js"):
                source=root/"input.zip"
                _zip(source,{"index.html":"<h1>Ok</h1>",name:"bad"})
                with self.assertRaises(ValueError, msg=name):
                    professional_tools._unpack_project(source,root/"project")

    def test_reject_missing_index_and_unbounded_files(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"missing.zip"
            _zip(source,{"src/main.js":"console.log('x')"})
            with self.assertRaises(ValueError):
                professional_tools._unpack_project(source,root/"project")
            source=root/"large.zip"
            _zip(source,{"index.html":"hello","src/file.js":"x" * 2_000_001})
            with self.assertRaises(ValueError):
                professional_tools._unpack_project(source,root/"project")

    def test_vite_build_with_bound_artifacts(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"project.zip"
            _zip(source,{"index.html":"<h1>Ferrari</h1>","src/main.js":"console.log('ok')"})
            vite_dir=root/"fake-vite"
            (vite_dir/"bin").mkdir(parents=True)
            (vite_dir/"package.json").write_text('{"version":"8.3.5"}')
            def build(args, **kwargs):
                out=Path(args[args.index("--outDir")+1])
                (out/"assets").mkdir(parents=True)
                (out/"index.html").write_text("<h1>Ferrari</h1>")
                (out/"assets/app.js").write_text("console.log(1)")
            with patch.object(professional_tools,"vite_available",return_value=True):
                with patch.object(professional_tools,"VITE",vite_dir/"bin/vite.js"):
                    with patch.object(professional_tools,"browser_available",return_value=False):
                        with patch.object(professional_tools,"_run",side_effect=build):
                            _, outputs=professional_tools.vite_build(source,root/"out")
            self.assertEqual(len(outputs),2)
            report=json.loads((root/"out/vite-build.json").read_text())
            self.assertIn("assets/app.js",report["built_files"])

    def test_browser_isolated_runtime_detection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            cache=root/"browsers"
            binary=cache/"chromium_headless_shell-1567/chrome-headless-shell-linux64/chrome-headless-shell"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"own Ferrari binary marker")
            package=root/"node_modules/playwright/cli.js"
            package.parent.mkdir(parents=True)
            package.write_text("// Playwright Ferrari marker")
            node=root/"node"
            node.write_text("# Ferrari node")
            with patch.object(professional_tools,"NODE",node):
                with patch.object(professional_tools,"PLAYWRIGHT",package.parent):
                    with patch.object(professional_tools,"BROWSER_CACHE",cache):
                        self.assertTrue(professional_tools.browser_available())
                        binary.unlink()
                        self.assertFalse(professional_tools.browser_available())

    def test_vite_build_browser_evidence_without_new_operation(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            source=root/"site.zip"
            _zip(source,{"index.html":"<h1 id='app'>Ferrari</h1>","src/main.js":"console.log('ferrari')"})
            fake=root/"vite"
            (fake/"bin").mkdir(parents=True)
            (fake/"package.json").write_text('{"version":"8.3.5"}')
            def execute(args, **kwargs):
                if "--outDir" in args:
                    dist=Path(args[args.index("--outDir")+1])
                    dist.mkdir(parents=True)
                    (dist/"index.html").write_text("<h1>Ferrari</h1>")
                else:
                    self.assertTrue(str(args[1]).endswith("engine/browser_check.js"))
                    Path(args[-2]).write_bytes(b"PNG" * 70)
                    Path(args[-2]).with_name("browser-mobile.png").write_bytes(b"PNG" * 80)
                    Path(args[-1]).write_text(json.dumps({
                        "status":"passed","browser_version":"test",
                        "interactions":{"status":"clear","focusable_count":4,"findings":[],
                                        "tab_forward":"passed","shift_tab_back":"passed",
                                        "button_enter":"passed","button_space":"passed",
                                        "link_enter":"passed","form_enter":"passed"},
                        "mobile":{"viewport":{"width":390,"height":844},
                                  "horizontal_overflow_px":0,
                                  "spotcheck_status":"clear","findings":[]}
                    }))
            with patch.object(professional_tools,"vite_available",return_value=True):
                with patch.object(professional_tools,"browser_available",return_value=True):
                    with patch.object(professional_tools,"VITE",fake/"bin/vite.js"):
                        with patch.object(professional_tools,"_run",side_effect=execute) as run:
                            _, result=professional_tools.vite_build(source,root/"out")
            self.assertEqual(run.call_count,2)
            self.assertEqual(len(result),5)
            self.assertGreater((root/"out/browser-mobile.png").stat().st_size,100)
            result_json=json.loads((root/"out/browser-check.json").read_text())
            self.assertEqual(result_json["interactions"]["button_space"],"passed")
            self.assertEqual(result_json["interactions"]["form_enter"],"passed")
            self.assertEqual(result_json["mobile"]["viewport"]["width"],390)
            self.assertEqual(json.loads((root/"out/vite-build.json").read_text())["browser_test"]["status"],"passed")

    def test_browser_script_blocks_external_network_without_http_server(self):
        source=(professional_tools.ROOT/"engine/browser_check.js").read_text()
        self.assertIn('context.route("**/*"',source)
        self.assertIn('ferrari.invalid',source)
        self.assertIn('data.blocked_external.push',source)
        self.assertIn('page.setViewportSize({width: 390, height: 844})',source)
        self.assertIn('"browser-mobile.png"',source)
        self.assertIn('horizontal_overflow_px',source)
        self.assertIn('images_missing_alt',source)
        self.assertIn('fields_missing_label',source)
        self.assertIn('page.keyboard.press("Tab")',source)
        self.assertIn('page.keyboard.press("Shift+Tab")',source)
        self.assertIn('page.keyboard.press("Enter")',source)
        self.assertIn('await button.focus();\n      await page.keyboard.press("Space")',source)
        self.assertIn('page.keyboard.press("Space")',source)
        self.assertIn('data-ferrari-test="button"',source)
        self.assertIn('data-ferrari-test="form"',source)
        self.assertIn('data-ferrari-test="link"',source)
        self.assertIn('opt-in data-ferrari-test controls only',source)
        self.assertIn('not actual mobile-device emulation',source)
        self.assertNotIn('spawn(',source)
        installer=(professional_tools.ROOT/"install/vps-browser-headless.sh").read_text()
        self.assertIn("--only-shell",installer)
        self.assertIn("chromium_headless_shell-1248/chrome-headless-shell-linux64/chrome-headless-shell",installer)
        self.assertNotIn("chromium.executablePath()",installer.split("BROWSER_BIN=")[1])
        self.assertIn("--ignore-scripts",installer)
        self.assertNotIn("sudo ",installer)
        self.assertNotIn("apt-get",installer)

    def test_inventory_tracks_base_capabilities_not_fake_manifest_actions(self):
        bim={"scope":"ferrari_venv","location":"/tmp/ifcopenshell","verification":"files_present_not_import_tested"}
        npm={"scope":"ferrari_npm","location":"/tmp/vite","package":"vite"}
        ecosystems={"python":{"tools":{"ifcopenshell":bim}},"npm":{"tools":{"vite":npm}},"containers":{"tools":{}}}
        with patch.object(tool_runtime.runtime_discovery,"discover",return_value=ecosystems):
            with patch.object(tool_runtime,"executable",return_value=None):
                with patch.object(professional_tools,"bim_available",return_value=True):
                    with patch.object(professional_tools,"vite_available",return_value=True):
                        inv=tool_runtime.inventory()
        for name,op in (("ifcopenshell","ifc-summary"),("vite","vite-build")):
            item=next(x for x in inv["programs"] if x["id"]==name)
            self.assertEqual(item["base_operations"],[op])
            self.assertEqual(item["status"],"callable")
            self.assertTrue(item["installed"])
        self.assertEqual(inv["registered_actions"],22)

    def test_no_arbitrary_shell_or_project_config(self):
        src=(professional_tools.ROOT/"engine/professional_tools.py").read_text()
        self.assertIn("shell=False",src)
        self.assertNotIn("shell=True",src)
        installer=(professional_tools.ROOT/"install/vps-bim-web.sh").read_text()
        self.assertIn("--ignore-scripts",installer)
        self.assertIn("ifcopenshell==",installer)
        self.assertIn("vite@",installer)


if __name__=="__main__":
    unittest.main()
