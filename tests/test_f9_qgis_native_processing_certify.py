"""Tests for Ferrari project-isolated QGIS native:buffer + loader audit."""
import ast
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "install/vps-f9-qgis-native-processing-certify.py"
SPEC = spec_from_file_location("ferrari_qgis_native", SOURCE)
m = module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class QGISNativeProcessingCertificateTests(unittest.TestCase):
    def test_synthetic_real_native_processing_not_geometry_only(self):
        ast.parse(SOURCE.read_text(encoding="utf-8"))
        self.assertIn('processing.run("native:buffer"', m.CHILD)
        self.assertIn('QgsApplication([], False)', m.CHILD)
        self.assertIn('initQgis()', m.CHILD)
        self.assertIn('geojson_export_and_reparse', m.CHILD)
        self.assertIn('6500.0 < area < 7500.0', m.CHILD)
        self.assertNotIn("real land", m.CHILD)

    def test_no_global_apt_install_crossproject_write_or_gui_false_pass(self):
        source = SOURCE.read_text(encoding="utf-8")
        for forbidden in ('apt-get ', 'sudo ', 'git reset', 'git pull', 'shell=True',
                          'rm -rf', '/srv/projects/fadego', '/srv/projects/pink-iptv'):
            self.assertNotIn(forbidden, source)
        self.assertIn('"all_providers_certified": False', source)
        self.assertIn('"transitive_dependency_isolation_certified": False', source)
        with patch.object(m.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "NO_ROOT"):
                m.guard()

    def test_env_never_uses_public_qgis_or_user_settings(self):
        with TemporaryDirectory() as td:
            root=Path(td)/"skill-universal"
            target=root/"tools/qgis-4.2.3-condaforge"
            runtime=root/".runtime"
            runtime.mkdir(parents=True)
            (target/"share/qgis/python").mkdir(parents=True)
            with patch.multiple(m, ROOT=root, TARGET=target, RUNTIME=runtime):
                env=m.private_env(runtime)
            self.assertEqual(env["QGIS_PREFIX_PATH"],str(target))
            self.assertEqual(env["LD_LIBRARY_PATH"],str(target/"lib"))
            self.assertEqual(env["QT_QPA_PLATFORM"],"offscreen")
            self.assertEqual(env["HOME"],str(runtime))
            self.assertIn("/usr/bin:/bin",env["PATH"])
            self.assertNotIn("/usr/local/lib",env["LD_LIBRARY_PATH"])

    def test_loader_only_reports_sonames_not_private_paths(self):
        out = ('libqgis_core.so => /srv/projects/skill-universal/tools/qgis-4.2.3-condaforge/lib/libqgis_core.so (0x1)\n'
               'libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x2)\n'
               'liboptional.so.320 => not found\n')
        with patch.object(m.subprocess,"run",return_value=SimpleNamespace(
            returncode=0,stdout=out,stderr="")):
            x=m.loader_inspection({})
        self.assertEqual(x["linked_private_libraries"],1)
        self.assertEqual(x["linked_ubuntu_base_libraries"],1)
        self.assertEqual(x["unresolved_sonames"],["liboptional.so.320"])
        self.assertFalse(x["transitive_dependency_isolation_certified"])
        self.assertNotIn("/lib/x86_64",str(x))

    def test_real_child_success_verifies_output_then_cleans(self):
        with TemporaryDirectory() as td:
            root=Path(td)/"skill-universal"
            runtime=root/".runtime"
            runtime.mkdir()
            target=root/"tools/qgis-4.2.3-condaforge"
            target.mkdir(parents=True)
            def make_result(args, **kwargs):
                work=Path(args[2])
                (work/"buffer-5m.geojson").write_text(
                    json.dumps({"type":"FeatureCollection","features":[{}]}))
                (work/"native-processing-result.json").write_text(json.dumps({
                    "native_buffer_algorithm_executed":True,
                    "geojson_export_and_reparse":True,"feature_count":1}))
                return SimpleNamespace(returncode=0,stdout="PASS",stderr="")
            with patch.multiple(m,ROOT=root,RUNTIME=runtime,TARGET=target), \
                 patch.object(m,"guard"), \
                 patch.object(m,"loader_inspection",return_value={}), \
                 patch.object(m.subprocess,"run",side_effect=make_result):
                result=m.certify()
            self.assertEqual(result["status"],"pass")
            self.assertTrue(result["native_processing_certified"])
            self.assertTrue(result["test_artifacts_removed"])
            self.assertEqual(list(runtime.iterdir()),[])

    def test_nonzero_qgis_exit_never_certifies_processing(self):
        with TemporaryDirectory() as td:
            root=Path(td)/"skill-universal"
            runtime=root/".runtime"
            runtime.mkdir()
            target=root/"tools/qgis-4.2.3-condaforge"
            target.mkdir(parents=True)
            with patch.multiple(m,ROOT=root,RUNTIME=runtime,TARGET=target), \
                 patch.object(m,"guard"), \
                 patch.object(m,"loader_inspection",return_value={}), \
                 patch.object(m.subprocess,"run",return_value=SimpleNamespace(
                    returncode=2,stdout="",stderr="missing optional provider")):
                result=m.certify()
            self.assertEqual(result["status"],"partial_blocked")
            self.assertFalse(result["native_processing_certified"])
            self.assertEqual(list(runtime.iterdir()),[])

if __name__=="__main__":
    unittest.main()
