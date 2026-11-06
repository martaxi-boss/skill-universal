"""Ferrari F9: provider diagnostic must isolate crashes and never alter host APT."""
import ast
from importlib.util import module_from_spec,spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

SRC=Path(__file__).resolve().parents[1]/"install/vps-f9-qgis-providers-diagnose.py"
SPEC=spec_from_file_location("f9_qgis_providers",SRC)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class FerrariQGISProvidersTests(unittest.TestCase):
    def test_immutable_read_only_and_ferrari_scope(self):
        code=SRC.read_text(encoding="utf-8")
        ast.parse(code)
        for forbidden in ("apt-get ", "apt install", "sudo ",
                          "rm -rf", "shell=True", "/srv/projects/fadego",
                          "git reset", "git pull", "global_apt_changed\":True"):
            self.assertNotIn(forbidden,code)
        self.assertIn("TemporaryDirectory(",code)
        self.assertIn("start_new_session=True",code)
        self.assertIn("os.killpg(",code)
        self.assertIn('"full_qgis_certified":False',code)
        self.assertIn('"all_transitive_dependencies_certified":False',code)

    def test_sample_is_one_synthetic_polygon(self):
        with TemporaryDirectory() as d:
            path=Path(d)/"synthetic.json"
            m.sample(path)
            doc=json.loads(path.read_text())
            self.assertEqual(doc["type"],"FeatureCollection")
            self.assertEqual(len(doc["features"]),1)
            ring=doc["features"][0]["geometry"]["coordinates"][0]
            self.assertEqual(ring[0],ring[-1])
            self.assertTrue(doc["features"][0]["properties"]["synthetic"])

    def test_process_bad_cpp_abortion_is_not_a_pass(self):
        proc=SimpleNamespace(pid=12345,returncode=-6,
                             communicate=lambda timeout=40:("","std::bad_alloc"))
        with TemporaryDirectory() as td, patch.object(m.subprocess,"Popen",return_value=proc):
            with patch.object(m,"TARGET",Path(td)),patch.object(m,"ROOT",Path(td)):
                doc=m.check_process("qgis_ogr",m.QGIS_OGR_PROBE,
                                    Path(td)/"sample.json",{})
        self.assertFalse(doc["success"])
        self.assertEqual(doc["exit_code"],-6)
        self.assertIn("bad_alloc",doc["stderr_tail"])
        self.assertFalse(doc["host_persisted"])

    def test_process_gdal_success_needs_valid_json_not_just_zero_exit(self):
        with TemporaryDirectory() as td:
            with patch.object(m,"TARGET",Path(td)),patch.object(m,"ROOT",Path(td)):
                p=SimpleNamespace(pid=5,returncode=0,
                                  communicate=lambda timeout=40:
                                  ('{"driver":"GeoJSON","count":1}',""))
                with patch.object(m.subprocess,"Popen",return_value=p):
                    outcome=m.check_process("gdal_ogr",m.GDAL_PROBE,
                                            Path(td)/"fake.json",{})
                self.assertTrue(outcome["success"])
                self.assertEqual(outcome["result"]["count"],1)
                p=SimpleNamespace(pid=6,returncode=0,
                                  communicate=lambda timeout=40:("not-json",""))
                with patch.object(m.subprocess,"Popen",return_value=p):
                    other=m.check_process("gdal_ogr",m.GDAL_PROBE,
                                          Path(td)/"fake.json",{})
                self.assertFalse(other["success"])

    def test_optional_hdf5_loader_reports_only_names_not_library_paths(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            lib=root/"lib"
            lib.mkdir()
            (lib/"libhdf5_cpp.so.310").write_text("test")
            plugin=lib/m.OPTIONAL_PLUGINS[0]
            plugin.write_text("test")
            meta=root/"conda-meta"
            meta.mkdir()
            (meta/"libhdf5-1.14.json").write_text(json.dumps({
                "name":"libhdf5","version":"1.14.1","build":"h123_0"}))
            stdout="libhdf5_cpp.so.320 => not found\nlibstdc++.so => /usr/lib/libstdc++.so\n"
            with patch.object(m,"TARGET",root),\
                 patch.object(m.subprocess,"run",return_value=SimpleNamespace(
                     returncode=0,stdout=stdout,stderr="")):
                evidence=m.optional_linker_audit({})
            self.assertEqual(evidence["private_hdf5_cpp_sonames"],
                             ["libhdf5_cpp.so.310"])
            self.assertEqual(evidence["optional_plugins"][m.OPTIONAL_PLUGINS[0]]
                             ["unresolved_sonames"],["libhdf5_cpp.so.320"])
            self.assertFalse(evidence["all_transitive_dependencies_certified"])
            self.assertNotIn(str(root),str(evidence))

    def test_diagnostic_cleans_synthetic_file_and_never_certifies_gui(self):
        with TemporaryDirectory() as d:
            root=Path(d)/"skill-universal"
            active=root/"releases"/m.ACTIVE
            active.mkdir(parents=True)
            (root/"current").symlink_to(active)
            runtime=root/".runtime"
            runtime.mkdir()
            with patch.multiple(m,ROOT=root,RUNTIME=runtime),\
                 patch.object(m,"guard"),\
                 patch.object(m.resource,"setrlimit"),\
                 patch.object(m,"optional_linker_audit",return_value={
                     "optional_plugins":{},"all_transitive_dependencies_certified":False}),\
                 patch.object(m,"check_process",side_effect=[
                     {"success":True}, {"success":False}]):
                result=m.diagnose()
            self.assertEqual(result["status"],"diagnostic_complete")
            self.assertFalse(result["full_qgis_certified"])
            self.assertFalse(result["provider_issue_resolved"])
            self.assertFalse(result["global_apt_changed"])
            self.assertFalse(result["other_projects_changed"])
            self.assertEqual(list(runtime.iterdir()),[])

if __name__=="__main__":
    unittest.main()
