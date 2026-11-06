"""Ferrari F9 QGIS: official open-source micromamba, private env and fail-closed tests."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import json
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/"install/vps-phase9-private-qgis-conda.py"
SPEC=spec_from_file_location("ferrari_f9_qgis",SRC)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class QgisIsolatedTests(unittest.TestCase):
    def test_official_micromamba_and_pinned_oss_qgis(self):
        self.assertEqual(m.VERSION,"4.2.3")
        self.assertEqual(m.MAMBA_VERSION,"2.10.0-0")
        self.assertEqual(m.MAMBA_SIZE,19028608)
        self.assertEqual(m.MAMBA_SHA256,"701f39c06f8e6a670a0e186c8479b9e5c0502a2f0cda6cef65d83bdd2875e8bd")
        self.assertTrue(m.MAMBA_URL.startswith("https://github.com/mamba-org/micromamba-releases/"))
        self.assertEqual(str(m.TARGET),"/srv/projects/skill-universal/tools/qgis-4.2.3-condaforge")

    def test_rejects_root_global_installs_and_untrusted_channels(self):
        source=SRC.read_text(encoding="utf-8")
        for bad in ("sudo ","apt-get install","apt-get purge","pip install","shell=True",
                    "rm -rf","git reset","/usr/local/bin/qgis"):
            self.assertNotIn(bad,source)
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"NO_ROOT"):
                m.guard()
        spec=m.conda_args(False)
        self.assertIn("--override-channels",spec)
        self.assertIn("conda-forge",spec)
        self.assertIn("qgis=4.2.3",spec)
        self.assertIn("python=3.12",spec)
        # Single overridden channel is sufficient; 2.10 fails on --strict-channel-priority.
        self.assertNotIn("--strict-channel-priority",spec)
        self.assertNotIn("defaults",spec)

    def test_preview_conda_only_and_download_budget(self):
        data={"success":True,"actions":{"FETCH":[{"size":2500},{"size":1250}]}}
        with patch.object(m,"guard"),patch.object(m,"prepare_mamba"),\
             patch.object(m,"execute",return_value=SimpleNamespace(
                returncode=0,stdout=json.dumps(data),stderr="")) as run:
            result=m.preview()
        self.assertEqual(result["status"],"solved")
        self.assertEqual(result["estimated_download_bytes"],3750)
        self.assertTrue(result["no_ubuntu_packages_modified"])
        self.assertIn("--dry-run",run.call_args[0][0])
        too_large={"success":True,"actions":{"FETCH":[{"size":6*1024**3}]}}
        with patch.object(m,"guard"),patch.object(m,"prepare_mamba"),\
             patch.object(m,"execute",return_value=SimpleNamespace(
                returncode=0,stdout=json.dumps(too_large),stderr="")):
            with self.assertRaisesRegex(RuntimeError,"DOWNLOAD_BUDGET"):
                m.preview()

    def test_qgis_license_rejects_non_gpl(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            meta=p/"conda-meta"
            meta.mkdir()
            entry=meta/"qgis-4.2.3-py312_1.json"
            data={"name":"qgis","version":"4.2.3","license":"GPL-2.0-or-later","url":"https://conda.anaconda.org/conda-forge","build_string":"py312_1"}
            entry.write_text(json.dumps(data))
            with patch.object(m,"TARGET",p):
                self.assertEqual(m.qgis_package()["version"],"4.2.3")
                data["license"]="LicenseRef-proprietary"
                entry.write_text(json.dumps(data))
                with self.assertRaisesRegex(RuntimeError,"OPEN_SOURCE_LICENSE"):
                    m.qgis_package()

    def test_install_error_removes_only_its_own_prefix(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/"skill-universal"
            root_tools=p/"tools"
            runtime=p/".runtime"
            root_tools.mkdir(parents=True)
            runtime.mkdir()
            target=root_tools/"qgis-4.2.3-condaforge"
            unrelated=root_tools/"other-application"
            unrelated.mkdir()
            (unrelated/"keep.txt").write_text("preserve")
            def fake_execute(cmd,**kw):
                target.mkdir()
                (target/"partial.txt").write_text("partial")
                return SimpleNamespace(returncode=1,stdout="",stderr="no network")
            with patch.multiple(m,ROOT=p,TOOLS=root_tools,RUNTIME=runtime,TARGET=target),\
                 patch.object(m,"guard"),\
                 patch.object(m,"preview",return_value={"estimated_download_bytes":123}),\
                 patch.object(m,"execute",side_effect=fake_execute):
                with self.assertRaisesRegex(RuntimeError,"CONDA_INSTALL_FAILED"):
                    m.install()
            self.assertFalse(target.exists())
            self.assertEqual((unrelated/"keep.txt").read_text(),"preserve")

    def test_isolated_python_and_gui_smokes_have_separate_status(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            (p/"bin").mkdir()
            process=p/"bin/qgis_process"
            process.write_text("#!/bin/sh\n")
            process.chmod(0o700)
            (p/"bin/python").write_text("#!/bin/sh\n")
            def fake_execute(cmd,**kw):
                if cmd[0]==str(process):
                    return SimpleNamespace(returncode=0,stdout=(
                        "native:buffer\nnative:centroids\nnative:clip\nnative:dissolve\n"
                        "native:mergevectorlayers\nnative:reprojectlayer\n" if "list" in cmd
                        else "QGIS 4.2.3\n"),stderr="")
                if cmd[0]==str(p/"bin/python"):
                    return SimpleNamespace(returncode=0,stdout="F9_PRIVATE_QGIS_PYTHON_IMPORT=PASS\n",stderr="")
                return SimpleNamespace(returncode=0,stdout="libqgis_core.so => "+str(p)+"/lib/libqgis_core.so\n",stderr="")
            with patch.object(m,"TARGET",p),patch.object(m,"PREFIX_BIN",process),\
                 patch.object(m,"qgis_package",return_value={"license":"GPL-2.0"}),\
                 patch.object(m,"env",return_value={}),\
                 patch.object(m,"execute",side_effect=fake_execute):
                result=m.smoke()
            self.assertTrue(result["cli_version_certified"])
            self.assertFalse(result["gui_runtime_certified"])
            self.assertTrue(result["private_qgis_libraries_loaded"])

    def test_qgis_processing_remains_certified_if_optional_pyqgis_missing(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)
            (p/"bin").mkdir()
            process=p/"bin/qgis_process"
            process.write_text("#!/bin/sh\n")
            process.chmod(0o700)
            (p/"bin/python").write_text("#!/bin/sh\n")
            def fake_execute(cmd,**kwargs):
                if cmd[0]==str(p/"bin/python"):
                    return SimpleNamespace(returncode=1,stdout="",stderr="No module named qgis")
                if cmd[0]==str(process):
                    out=("native:buffer\nnative:centroids\nnative:clip\n"
                         "native:dissolve\nnative:merge\nnative:reproject\n") if "list" in cmd else "QGIS 4.2.3\n"
                    return SimpleNamespace(returncode=0,stdout=out,stderr="")
                return SimpleNamespace(returncode=0,
                    stdout="libqgis_core.so => "+str(p)+"/lib/libqgis_core.so\n",stderr="")
            with patch.object(m,"TARGET",p),patch.object(m,"PREFIX_BIN",process),\
                 patch.object(m,"qgis_package",return_value={"license":"GPL-2.0"}),\
                 patch.object(m,"env",return_value={}),\
                 patch.object(m,"execute",side_effect=fake_execute):
                result=m.smoke()
            self.assertTrue(result["cli_version_certified"])
            self.assertTrue(result["native_processing_catalog_certified"])
            self.assertFalse(result["python_qgis_import_certified"])
            self.assertFalse(result["gui_runtime_certified"])


if __name__=="__main__":
    unittest.main()
