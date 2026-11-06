"""Ferrari PDAL optional HDF5 ABI 320 must be private, pinned and reversible."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import ast
import json
import unittest

SCRIPT=Path(__file__).resolve().parents[1]/"install/vps-f9-pdal-hdf5-abi320.py"
SPEC=spec_from_file_location("f9_pdal_hdf5_abi320",SCRIPT)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class PrivateHDF5AbiTests(unittest.TestCase):
    def test_no_global_install_or_abi_alias(self):
        source=SCRIPT.read_text(encoding="utf-8")
        ast.parse(source)
        for forbidden in ("apt-get ","sudo ","subprocess.run(['pip'","git reset",
                          "shell=True","/srv/projects/fadego","/srv/projects/pink-iptv",
                          "ln -s","os.symlink(","ln -sf"):
            self.assertNotIn(forbidden,source)
        self.assertEqual(m.HDF5_VERSION,"2.2.0")
        self.assertTrue(str(m.SIDECAR).startswith("/srv/projects/skill-universal/tools/"))
        self.assertTrue(str(m.MAMBA_ROOT).startswith("/srv/projects/skill-universal/.runtime/"))
        self.assertIn("MAMBA_SHA256",source)
        self.assertIn("verify_existing_qgis_core()",source)
        self.assertIn("shutil.rmtree(SIDECAR)",source)

    def test_no_install_happens_on_preview(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            side=root/"sidecar"
            ok={"success":True,"actions":{"LINK":[{"name":"hdf5","version":"2.2.0"}],
                                           "FETCH":[{"size":2000000}]}}
            with patch.multiple(m,SIDECAR=side),\
                 patch.object(m,"guard"),\
                 patch.object(m,"private_env",return_value={}),\
                 patch.object(m,"execute",return_value=SimpleNamespace(
                     returncode=0,stdout=json.dumps(ok),stderr="")) as call:
                result=m.preview()
            self.assertEqual(result["status"],"preview_pass")
            self.assertEqual(result["download_bytes_estimate"],2000000)
            self.assertFalse(side.exists())
            self.assertIn("--dry-run",call.call_args[0][0])

    def test_solver_wrong_version_is_blocked(self):
        with TemporaryDirectory() as td:
            fake={"success":True,"actions":{"LINK":[{"name":"hdf5","version":"1.14.6"}],
                                            "FETCH":[]}}
            with patch.object(m,"SIDECAR",Path(td)/"nonexistent"),\
                 patch.object(m,"guard"),\
                 patch.object(m,"private_env",return_value={}),\
                 patch.object(m,"execute",return_value=SimpleNamespace(
                     returncode=0,stdout=json.dumps(fake),stderr="")):
                with self.assertRaisesRegex(RuntimeError,"NO_PINNED_HDF5"):
                    m.preview()

    def test_hdf5_soname_must_exist_inside_sidecar(self):
        with TemporaryDirectory() as td:
            base=Path(td)
            lib=base/"lib"
            lib.mkdir()
            for name in ("libhdf5_cpp.so.320","libhdf5.so.320"):
                (lib/name).write_text("synthetic")
            with patch.object(m,"SIDECAR",base):
                self.assertTrue(all(m.hdf5_files().values()))
            (lib/"libhdf5_cpp.so.320").unlink()
            outside=base.parent/"not-trusted.so"
            (lib/"libhdf5_cpp.so.320").symlink_to(outside)
            with patch.object(m,"SIDECAR",base):
                self.assertFalse(m.hdf5_files()["libhdf5_cpp.so.320"])

    def test_both_private_pdal_plugins_need_binary_link(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            qgis=root/"qgis"
            lib=qgis/"lib"
            lib.mkdir(parents=True)
            side=root/"sidecar"
            (side/"lib").mkdir(parents=True)
            for p in m.PLUGINS:
                (lib/p).write_text("fake")
            def fake(cmd,env,timeout):
                line=f"libhdf5_cpp.so.320 => {side}/lib/libhdf5_cpp.so.320 (0xabc)\n"
                return SimpleNamespace(returncode=0,stdout=line,stderr="")
            with patch.multiple(m,QGIS=qgis,SIDECAR=side),\
                 patch.object(m,"private_env",return_value={}),\
                 patch.object(m,"execute",side_effect=fake):
                result=m.private_plugin_loader()
            self.assertEqual(len(result),2)
            self.assertTrue(all(p["linked"] and p["direct_hdf5_cpp_320_resolved"]
                                for p in result.values()))

    def test_install_failure_cleans_only_its_new_folder(self):
        with TemporaryDirectory() as td:
            root=Path(td)
            tools=root/"tools"
            tools.mkdir()
            rt=root/".runtime"
            rt.mkdir()
            side=tools/"sidecar"
            protected=root/"other-project.txt"
            protected.write_text("preserve")
            def fail(argv,env,timeout):
                side.mkdir()
                (side/"partial-file").write_text("incomplete")
                return SimpleNamespace(returncode=1,stderr="synthetic fail",stdout="")
            with patch.multiple(m,TOOLS=tools,RUNTIME=rt,SIDECAR=side),\
                 patch.object(m,"guard"),\
                 patch.object(m,"preview",return_value={"download_bytes_estimate":0}),\
                 patch.object(m,"private_env",return_value={}),\
                 patch.object(m,"execute",side_effect=fail):
                with self.assertRaisesRegex(RuntimeError,"PRIVATE_INSTALL_FAILED"):
                    m.install()
            self.assertFalse(side.exists())
            self.assertEqual(protected.read_text(),"preserve")
            self.assertEqual(list(tools.iterdir()),[])

if __name__=="__main__":
    unittest.main()
