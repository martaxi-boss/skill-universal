"""F9: pinned Ubuntu Three.js + Unifont SolveSpace private resource closure."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import json
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1]/"install/vps-phase9-private-solvespace.py"
SPEC=spec_from_file_location("ferrari_f9_private_solvespace_support",SOURCE)
mod=module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class SolveSpacePrivateResourceTests(unittest.TestCase):
    def test_license_source_pins_and_no_global_mutations(self):
        self.assertEqual(set(mod.RESOURCES),{"libjs-three","unifont"})
        self.assertEqual(mod.RESOURCES["libjs-three"]["sha256"],
                         "ef7cc260f96bd469245f1f2405981e305f6bf001965cfd7a750e37dc5d87a963")
        self.assertEqual(mod.RESOURCES["unifont"]["sha256"],
                         "f5d7516c5a430dc6ee8266fd333cc49339407865916462d608b8478b1e3a84a1")
        content=SOURCE.read_text(encoding="utf-8")
        for denied in ("apt-get install","apt-get purge","sudo ","autoremove",
                       "shell=True","os.system","/usr/share/solvespace/threejs"):
            self.assertNotIn(denied,content)
        self.assertIn("GPL-2.0-or-later",content)
        self.assertIn('"MIT"',content)

    def test_signed_apt_resource_index_is_pinned(self):
        for name,pinned in mod.RESOURCES.items():
            metadata=("Package: "+name+"\nVersion: "+pinned["version"]+
                      "\nArchitecture: all\nSize: "+str(pinned["size"])+
                      "\nSHA256: "+pinned["sha256"]+
                      "\nFilename: pool/universe/resource/path.deb\n")
            with patch.object(mod,"call",return_value=SimpleNamespace(stdout=metadata)):
                self.assertEqual(mod.apt_resource_metadata(name)["Package"],name)
            wrong=metadata.replace("SHA256: "+pinned["sha256"],"SHA256: "+"0"*64)
            with patch.object(mod,"call",return_value=SimpleNamespace(stdout=wrong)):
                with self.assertRaisesRegex(RuntimeError,"REPOSITORY_HASH_UNEXPECTED"):
                    mod.apt_resource_metadata(name)
        with self.assertRaisesRegex(RuntimeError,"UNEXPECTED_RESOURCE"):
            mod.apt_resource_metadata("outside-package")

    def test_download_extract_and_validate_only_project_files(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"skill-universal"
            runtime=root/".runtime"
            target=root/"tools/solvespace-3.1-ubuntu24"
            runtime.mkdir(parents=True)
            target.mkdir(parents=True)
            for name,pinned in mod.RESOURCES.items():
                link=target/pinned["link"]
                link.parent.mkdir(parents=True,exist_ok=True)
                relative="../../javascript/three/three.js" if name=="libjs-three" else "../../unifont/unifont.hex"
                link.symlink_to(relative)
            sample={name:("official-resource-"+name).encode()
                    for name in mod.RESOURCES}
            support={name:{**pinned,"size":len(sample[name]),
                           "sha256":hashlib.sha256(sample[name]).hexdigest()}
                     for name,pinned in mod.RESOURCES.items()}
            def fake_call(args,**kwargs):
                if args[:2]==["/usr/bin/apt-get","download"]:
                    name=args[2].split("=",1)[0]
                    (kwargs["cwd"]/(name+".deb")).write_bytes(sample[name])
                elif args[:2]==["/usr/bin/dpkg-deb","-x"]:
                    deb=Path(args[2])
                    name=deb.stem
                    dest=Path(args[3])/support[name]["relative"]
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes(b"unifont-file" if name=="unifont" else b"threejs-file")
                return SimpleNamespace(returncode=0,stdout="",stderr="")
            with patch.multiple(mod,ROOT=root,RUNTIME=runtime,TOOLS=root/"tools",
                                TARGET=target,RESOURCE_MANIFEST=target/"private-resources.json",
                                RESOURCES=support), \
                 patch.object(mod,"guard"),patch.object(mod,"check"), \
                 patch.object(mod,"apt_resource_metadata",return_value={}), \
                 patch.object(mod,"call",side_effect=fake_call):
                result=mod.repair_resources()
                self.assertEqual(result["status"],"private_solvespace_resources_verified")
                self.assertEqual(result,mod.check_resources())
                self.assertEqual(result,mod.repair_resources())
                for name in support:
                    dest=target/support[name]["relative"]
                    self.assertTrue(dest.is_file())
                    self.assertTrue((target/support[name]["link"]).resolve().is_relative_to(target))
                self.assertEqual(list(runtime.iterdir()),[])
                dest=target/support["libjs-three"]["relative"]
                dest.write_bytes(b"modified")
                with self.assertRaisesRegex(RuntimeError,"CONTENT_HASH_MISMATCH"):
                    mod.check_resources()

    def test_original_resource_link_must_remain_private(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"skill-universal"
            target=root/"tools/solvespace-3.1-ubuntu24"
            target.mkdir(parents=True)
            p=target/mod.RESOURCES["libjs-three"]["link"]
            p.parent.mkdir(parents=True)
            p.symlink_to("/usr/share/javascript/three/three.js")
            with patch.object(mod,"TARGET",target):
                with self.assertRaisesRegex(RuntimeError,"DESTINATION_ESCAPED|RESOURCE_LINK_CHANGED"):
                    mod.resource_paths("libjs-three")

if __name__=="__main__":
    unittest.main()
