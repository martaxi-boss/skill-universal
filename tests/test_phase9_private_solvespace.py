"""Ferrari F9: SolveSpace signed apt hash, private tree, no system install."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import json
import tempfile
import unittest

SOURCE=Path(__file__).resolve().parents[1] / "install/vps-phase9-private-solvespace.py"
SPEC=spec_from_file_location("ferrari_private_solvespace",SOURCE)
mod=module_from_spec(SPEC)
SPEC.loader.exec_module(mod)

class SolveSpaceIsolationTests(unittest.TestCase):
    def test_version_source_and_license(self):
        self.assertEqual(mod.VERSION,"3.1+ds1-3.1build2")
        self.assertEqual(mod.PACKAGE,"solvespace")
        self.assertEqual(str(mod.EXECUTABLE),
                         "/srv/projects/skill-universal/tools/solvespace-3.1-ubuntu24/usr/bin/solvespace")
        self.assertIn('"GPL-3.0"',SOURCE.read_text(encoding="utf-8"))

    def test_does_not_install_global_packages(self):
        text=SOURCE.read_text(encoding="utf-8")
        for forbidden in ("apt-get install","apt-get upgrade","apt-get remove","sudo ",
                          "pip install","autoremove","shell=True","git reset","os.system"):
            self.assertNotIn(forbidden,text)
        with patch.object(mod.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(RuntimeError,"MUST_BE_UNPRIVILEGED"):
                mod.guard()

    def test_signed_apt_metadata_accepted_only_exact_version(self):
        out="Package: solvespace\nVersion: 3.1+ds1-3.1build2\nArchitecture: amd64\nSize: 1234\nSHA256: "+"a"*64+"\nFilename: pool/universe/s/solvespace.deb\n"
        with patch.object(mod,"call",return_value=SimpleNamespace(stdout=out)):
            m=mod.apt_metadata()
        self.assertEqual(m["bytes"],1234)
        self.assertEqual(m["sha256"],"a"*64)
        for bad in ("Version: 3.2.0","Architecture: arm64","SHA256: xx"):
            wrong=out
            if bad.startswith("Version"):
                wrong=out.replace("Version: 3.1+ds1-3.1build2",bad)
            elif bad.startswith("Architecture"):
                wrong=out.replace("Architecture: amd64",bad)
            else:
                wrong=out.replace("SHA256: "+"a"*64,bad)
            with patch.object(mod,"call",return_value=SimpleNamespace(stdout=wrong)):
                with self.assertRaisesRegex(RuntimeError,"METADATA_MISSING"):
                    mod.apt_metadata()

    def test_private_install_checks_sha_and_idempotence(self):
        payload=b"fake_signed_ubuntu_deb"
        size=len(payload)
        digest=hashlib.sha256(payload).hexdigest()
        meta={"sha256":digest,"bytes":size,"source":"pool/test","version":mod.VERSION,"package":"solvespace"}
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"skill-universal"
            tools=root/"tools"
            runtime=root/".runtime"
            tools.mkdir(parents=True)
            runtime.mkdir()
            target=tools/"solvespace-3.1-ubuntu24"
            exe=target/"usr/bin/solvespace"
            commands=[]
            def fake_call(argv,**kw):
                commands.append(argv)
                if argv[:2]==["/usr/bin/apt-get","download"]:
                    (kw["cwd"]/"solvespace.deb").write_bytes(payload)
                if argv[:2]==["/usr/bin/dpkg-deb","-x"]:
                    binary=Path(argv[-1])/"usr/bin/solvespace"
                    binary.parent.mkdir(parents=True)
                    binary.write_text("#!/bin/sh\n")
                    binary.chmod(0o700)
                return SimpleNamespace(stdout="libGL.so.1 => /lib/libGL.so.1\n",stderr="")
            with patch.multiple(mod, ROOT=root,TOOLS=tools,RUNTIME=runtime,TARGET=target,
                                EXECUTABLE=exe,OS_PACKAGE=target/"package.deb"),\
                 patch.object(mod,"guard"),patch.object(mod,"apt_metadata",return_value=meta),\
                 patch.object(mod,"call",side_effect=fake_call):
                installed=mod.install()
                self.assertEqual(installed["status"],"private_ubuntu_package_verified")
                self.assertFalse(installed["gui_runtime_certified"])
                self.assertFalse(installed["dependency_isolation_certified"])
                self.assertEqual(mod.install(),installed)
                self.assertEqual(len([cmd for cmd in commands if cmd[1]=="download"]),1)
                self.assertEqual(list(runtime.iterdir()),[])
                self.assertEqual(json.loads((target/"manifest.json").read_text())["sha256"],digest)

    def test_check_rejects_corrupted_package(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"skill-universal"
            target=root/"tools/solvespace-3.1-ubuntu24"
            target.mkdir(parents=True)
            deb=target/"package.deb"
            deb.write_bytes(b"wrong")
            with patch.object(mod,"TARGET",target),patch.object(mod,"OS_PACKAGE",deb),\
                 patch.object(mod,"apt_metadata",return_value={"bytes":5,"sha256":"0"*64}):
                with self.assertRaisesRegex(RuntimeError,"DEB_SHA_MISMATCH"):
                    mod.check()

if __name__=="__main__":
    unittest.main()
