"""Ferrari F6: only 4 owned launcher headers and 13 dead symlinks may change."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


def load():
    src=Path(__file__).resolve().parents[1]/"install/vps-phase6-final-hygiene.py"
    spec=importlib.util.spec_from_file_location("ferrari_phase6_final_hygiene",src)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class F6FinalHygiene(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/"skill-universal"
        self.root.mkdir()
        self.module=load()
        self.python=self.root/"runtimes/python3.12/bin/python3.12"
        self.python.parent.mkdir(parents=True)
        self.python.write_bytes(b"fake private Python")
        self.python.chmod(0o755)
        self.backup=self.root/".runtime/phase6-launcher-and-deadlinks-20261105.json"
        self.backup.parent.mkdir(parents=True)
        for name in (self.module.ACTIVE,self.module.FALLBACK):
            p=self.root/"releases"/name/"engine/ferrari.py"
            p.parent.mkdir(parents=True)
            p.write_text("true")
        (self.root/"current").symlink_to(self.root/"releases"/self.module.ACTIVE)
        self.patches=[
            patch.object(self.module,"ROOT",self.root),
            patch.object(self.module,"PYTHON",self.python),
            patch.object(self.module,"BACKUP",self.backup),
            patch.object(self.module,"no_service_consumers",return_value=None),
            patch.object(self.module,"check_actions",return_value=True),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        for i,rel in enumerate(self.module.LAUNCHERS):
            p=self.root/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            first=(b"#!/usr/bin/python3.12 -s\n" if i==2 else b"#!/usr/bin/python3 -Es\n" if i==0 else b"#!/usr/bin/python3\n")
            p.write_bytes(first+b"print('ok')\n")
            p.chmod(0o755)
        for rel in self.module.DEADLINKS:
            p=self.root/rel
            p.parent.mkdir(parents=True,exist_ok=True)
            p.symlink_to("absent-ferrari-resource")

    def test_preview_never_writes(self):
        x=self.module.run("--preview")
        self.assertEqual((x["launchers_with_global_shebang"],x["broken_private_resource_links"]),(4,13))
        self.assertEqual(x["private_files_changed"],0)
        self.assertFalse(self.backup.exists())
        self.assertTrue((self.root/self.module.DEADLINKS[0]).is_symlink())

    def test_apply_changes_exactly_17_ferrari_items(self):
        r=self.module.run("--apply")
        self.assertEqual(r["private_files_changed"],17)
        self.assertEqual(r["packages_removed"],0)
        self.assertEqual(r["service_changes"],0)
        self.assertTrue(self.backup.is_file())
        for rel in self.module.LAUNCHERS:
            self.assertTrue((self.root/rel).read_bytes().startswith(("#!"+str(self.python)).encode()))
        self.assertTrue((self.root/self.module.LAUNCHERS[0]).read_bytes().startswith(("#!"+str(self.python)+" -Es\n").encode()))
        self.assertTrue((self.root/self.module.LAUNCHERS[2]).read_bytes().startswith(("#!"+str(self.python)+" -s\n").encode()))
        for rel in self.module.DEADLINKS:
            self.assertFalse((self.root/rel).is_symlink())

    def test_runtime_failure_restores_all_source_artifacts(self):
        originals={rel:(self.root/rel).read_bytes() for rel in self.module.LAUNCHERS}
        with patch.object(self.module,"check_actions",side_effect=RuntimeError("deliberate failure")):
            with self.assertRaisesRegex(RuntimeError,"deliberate failure"):
                self.module.run("--apply")
        self.assertFalse(self.backup.exists())
        for rel,old in originals.items():
            self.assertEqual((self.root/rel).read_bytes(),old)
        for rel in self.module.DEADLINKS:
            self.assertTrue((self.root/rel).is_symlink())

    def test_live_resource_or_unexpected_link_blocks(self):
        bad=self.root/self.module.DEADLINKS[0]
        bad.unlink()
        bad.write_text("important data")
        with self.assertRaisesRegex(RuntimeError,"Expected Ferrari-owned broken symlink"):
            self.module.run("--preview")
        self.assertTrue(bad.exists())

    def test_script_does_not_operate_on_other_projects(self):
        source=(Path(__file__).resolve().parents[1]/"install/vps-phase6-final-hygiene.py").read_text()
        self.assertNotIn("apt-get remove",source)
        self.assertNotIn("shutil.rmtree(",source)
        self.assertIn("other_projects_modified",source)


if __name__=="__main__":
    unittest.main()
