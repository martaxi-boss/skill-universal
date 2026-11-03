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
                target.write_text(json.dumps({"format":"IFC","schema":"IFC4","total_entities":2}))
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
                    with patch.object(professional_tools,"_run",side_effect=build):
                        _, outputs=professional_tools.vite_build(source,root/"out")
            self.assertEqual(len(outputs),2)
            report=json.loads((root/"out/vite-build.json").read_text())
            self.assertIn("assets/app.js",report["built_files"])

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
        self.assertEqual(inv["registered_actions"],21)

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
