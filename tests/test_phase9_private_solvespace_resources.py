"""Ferrari F9: close private SolveSpace resource links safely and idempotently."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
import hashlib
import json
import os
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/"install/vps-phase9-private-solvespace-resources.py"
SPEC=spec_from_file_location("f9_private_solvespace_res",SOURCE)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class SolveSpaceResourceTests(unittest.TestCase):
    def test_two_signed_debian_dependencies_pinned(self):
        self.assertEqual(set(m.PACKAGE_INFO),{"libjs-three","unifont"})
        self.assertEqual(m.PACKAGE_INFO["libjs-three"]["version"],"111+dfsg1-3")
        self.assertEqual(m.PACKAGE_INFO["libjs-three"]["sha256"],
            "ef7cc260f96bd469245f1f2405981e305f6bf001965cfd7a750e37dc5d87a963")
        self.assertEqual(m.PACKAGE_INFO["unifont"]["version"],"1:15.1.01-1build1")
        self.assertEqual(m.PACKAGE_INFO["unifont"]["sha256"],
            "f5d7516c5a430dc6ee8266fd333cc49339407865916462d608b8478b1e3a84a1")
        self.assertEqual(m.PACKAGE_INFO["unifont"]["bytes"],5908726)
        for item in m.PACKAGE_INFO.values():
            self.assertEqual(len(item["sha256"]),64)
            self.assertTrue(item["link"].startswith("usr/share/solvespace/"))
            self.assertTrue(item["relative"].startswith("usr/share/"))
            self.assertFalse(item["relative"].startswith("/"))

    def test_reject_global_modifications_or_root(self):
        src=SOURCE.read_text()
        for bad in ("sudo ","apt-get install","apt-get remove","apt-get purge",
                    "apt autoremove","rm -rf","os.system","shell=True"):
            self.assertNotIn(bad,src)
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"NO_ROOT"):
                m.guard()

    def test_signed_metadata_fail_closed_on_mismatch(self):
        info=m.PACKAGE_INFO["unifont"]
        fixture=("Package: unifont\nVersion: "+info["version"]+"\nArchitecture: all\n"
                 "Size: "+str(info["bytes"])+"\nSHA256: "+info["sha256"]+"\n")
        with patch.object(m.subprocess,"run",return_value=SimpleNamespace(returncode=0,stdout=fixture,stderr="")):
            self.assertEqual(m.apt_metadata("unifont")["SHA256"],info["sha256"])
        corrupt=fixture.replace("SHA256: "+info["sha256"],"SHA256: "+"0"*64)
        with patch.object(m.subprocess,"run",return_value=SimpleNamespace(returncode=0,stdout=corrupt,stderr="")):
            with self.assertRaisesRegex(RuntimeError,"METADATA_MISMATCH"):
                m.apt_metadata("unifont")

    def setup_tree(self,dir: Path):
        root=dir/"skill-universal"
        target=root/"tools/solvespace-3.1-ubuntu24"
        runtime=root/".runtime"
        target.mkdir(parents=True)
        runtime.mkdir()
        for item in m.PACKAGE_INFO.values():
            link=target/item["link"]
            link.parent.mkdir(parents=True,exist_ok=True)
            link.symlink_to(item["link_target"])
        return root,target,runtime

    def test_symlink_resolution_is_project_private(self):
        with tempfile.TemporaryDirectory() as td:
            root,target,runtime=self.setup_tree(Path(td))
            with patch.multiple(m,ROOT=root,TARGET=target,RUNTIME=runtime,MANIFEST=target/"ferrari-private-resources.json"):
                for name in m.PACKAGE_INFO:
                    self.assertEqual(m.source_link(name),target/m.PACKAGE_INFO[name]["link"])
                link=target/m.PACKAGE_INFO["libjs-three"]["link"]
                link.unlink()
                link.symlink_to("/usr/share/javascript/three/three.js")
                with self.assertRaisesRegex(RuntimeError,"EXPECTED_RELATIVE_LINK_MISSING"):
                    m.source_link("libjs-three")

    def test_verified_copy_idempotent_and_rollback(self):
        with tempfile.TemporaryDirectory() as td:
            root,target,runtime=self.setup_tree(Path(td))
            payloads={"libjs-three":b"synthetic3js", "unifont":b"synthetic-hex"}
            def fake_fetch(name,scratch):
                f=scratch/name/"data"
                f.parent.mkdir(parents=True,exist_ok=True)
                f.write_bytes(payloads[name])
                deb=f.parent/"package.deb"
                deb.write_bytes(b"deb")
                return f,deb
            with patch.multiple(m,ROOT=root,TARGET=target,RUNTIME=runtime,MANIFEST=target/"ferrari-private-resources.json"),\
                 patch.object(m,"guard"),patch.object(m,"fetch_and_extract",side_effect=fake_fetch) as download:
                first=m.repair()
                self.assertEqual(first["status"],"two_private_resource_links_verified")
                self.assertEqual(first,m.repair())
                self.assertEqual(download.call_count,2)
                self.assertEqual(list(runtime.iterdir()),[])
                for name in m.PACKAGE_INFO:
                    self.assertEqual((target/m.PACKAGE_INFO[name]["relative"]).read_bytes(),payloads[name])
                data=json.loads((target/"ferrari-private-resources.json").read_text())
                self.assertFalse(data["global_apt_changed"])
                self.assertFalse(data["gui_runtime_certified"])

    def test_interrupted_second_download_keeps_no_partial_data(self):
        with tempfile.TemporaryDirectory() as td:
            root,target,runtime=self.setup_tree(Path(td))
            def broken(name,scratch):
                if name=="unifont":
                    raise RuntimeError("fake download blocked")
                f=scratch/"pkg"/"three.js"
                f.parent.mkdir()
                f.write_bytes(b"only-first")
                return f,f
            with patch.multiple(m,ROOT=root,TARGET=target,RUNTIME=runtime,MANIFEST=target/"ferrari-private-resources.json"),\
                 patch.object(m,"guard"),patch.object(m,"fetch_and_extract",side_effect=broken):
                with self.assertRaisesRegex(RuntimeError,"fake download blocked"):
                    m.repair()
                self.assertFalse((target/"usr/share/javascript/three/three.js").exists())
                self.assertFalse((target/"usr/share/unifont/unifont.hex").exists())
                self.assertFalse((target/"ferrari-private-resources.json").exists())
                self.assertEqual(list(runtime.iterdir()),[])

if __name__=="__main__":
    unittest.main()
