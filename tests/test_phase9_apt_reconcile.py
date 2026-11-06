"""F9 APT migration: fail-closed contract tests; never execute real apt."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import ast
import unittest

SRC=Path(__file__).resolve().parents[1]/"install/vps-phase9-apt-reconcile.py"
spec=spec_from_file_location("vps_phase9_apt_reconcile",SRC)
mod=module_from_spec(spec)
spec.loader.exec_module(mod)


class Phase9AptSafetyTests(unittest.TestCase):
    def test_source_compiles(self):
        ast.parse(SRC.read_text(encoding="utf-8"))

    def test_only_eight_authorized_with_private_executors(self):
        self.assertEqual(set(mod.NAMES),set(mod.BINARIES))
        self.assertEqual(len(mod.NAMES),8)
        self.assertEqual(len(mod.STAY),8)
        self.assertFalse(set(mod.NAMES)&set(mod.STAY))
        self.assertEqual(len(mod.SERVICES),8)
        self.assertEqual(mod.EXPECTED_SHA,"f1f3b03525adec7018d7d629243e7b0fbb7f5087")

    def test_apt_simulation_only_exact_eight(self):
        fake=SimpleNamespace(returncode=0,stdout="\n".join("Purg "+p+" [1.0]" for p in mod.NAMES),stderr="")
        with patch.object(mod,"command",return_value=fake):
            self.assertEqual(set(mod.simulation()),set(mod.NAMES))

    def test_apt_simulation_rejects_extra_removal(self):
        fake=SimpleNamespace(returncode=0,stdout="\n".join("Purg "+p+" [1.0]" for p in mod.NAMES)+"\nRemv nginx [1.0]",stderr="")
        with patch.object(mod,"command",return_value=fake):
            with self.assertRaisesRegex(RuntimeError,"F9_APT_SIMULATION_WOULD_CHANGE_OTHER_PACKAGES"):
                mod.simulation()

    def test_apt_simulation_rejects_extra_install(self):
        fake=SimpleNamespace(returncode=0,stdout="\n".join("Purg "+p+" [1.0]" for p in mod.NAMES)+"\nInst openssl [1.0]",stderr="")
        with patch.object(mod,"command",return_value=fake):
            with self.assertRaisesRegex(RuntimeError,"F9_APT_SIMULATION_WOULD_CHANGE_OTHER_PACKAGES"):
                mod.simulation()

    def test_debian_archive_fields_are_verified_independently(self):
        from types import SimpleNamespace
        def probe(args, **_):
            self.assertEqual(args[:3], ["dpkg-deb","-f","/tmp/test.deb"])
            self.assertEqual(len(args),4,"Each dpkg-deb query must ask for one field")
            values={"Package":"gimp","Version":"2.10.36-3ubuntu0.24.04.1"}
            return SimpleNamespace(returncode=0,stdout=values[args[3]]+"\\n")
        with patch.object(mod,"command",side_effect=probe):
            self.assertTrue(mod.matches_deb_identity(Path("/tmp/test.deb"),
                              "gimp","2.10.36-3ubuntu0.24.04.1"))
            self.assertFalse(mod.matches_deb_identity(Path("/tmp/test.deb"),
                              "ansible","2.10.36-3ubuntu0.24.04.1"))

    def test_no_uncontrolled_autoremove(self):
        tree=ast.parse(SRC.read_text(encoding="utf-8"))
        code=SRC.read_text(encoding="utf-8")
        self.assertNotIn('["apt-get","autoremove"',code)
        self.assertNotIn('["apt-get","-y","autoremove"',code)
        self.assertIn('"--no-install-recommends","purge",*NAMES',code)
        self.assertIn('apt_autoremove_executed":False',code)

    def test_guard_prevents_running_as_nonroot(self):
        with patch.object(mod.os,"geteuid",return_value=1000):
            with self.assertRaisesRegex(RuntimeError,"F9_NEEDS_ROOT_FOR_OS_APT"):
                mod.guard()

if __name__=="__main__":
    unittest.main()
