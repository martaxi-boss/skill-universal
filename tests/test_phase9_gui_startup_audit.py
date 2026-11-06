"""F9 GUI startup probe: only Ferrari executables; no GUI overclaims."""
from importlib.util import module_from_spec,spec_from_file_location
from pathlib import Path
from unittest.mock import patch
import tempfile
import unittest

SRC=Path(__file__).resolve().parents[1]/"install/vps-phase9-gui-startup-audit.py"
SPEC=spec_from_file_location("f9_gui_probe",SRC)
m=module_from_spec(SPEC)
SPEC.loader.exec_module(m)

class Phase9GuiProbeTests(unittest.TestCase):
    def test_six_app_roots_are_ferrari_only(self):
        self.assertEqual(set(m.PROBES),
                         {"librecad","audacity","openshot","synfig","solvespace","obs"})
        for path in m.PROBES.values():
            self.assertFalse(path.startswith("/"))
            self.assertNotIn("..",Path(path).parts)

    def test_never_certifies_gui_features_from_startup(self):
        text=SRC.read_text(encoding="utf-8")
        self.assertIn('"gui_functionality_certified":False',text)
        self.assertIn('"dependency_isolation_certified":False',text)
        self.assertIn('"gui_functions_certified":0',text)
        for denied in ("apt-get ","sudo ","pip install","shell=True",
                       "os.system","git reset","rm -rf","--startstreaming",
                       "--startrecording"):
            self.assertNotIn(denied,text)

    def test_reject_global_and_symlink_app(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"skill-universal"
            tools=root/"tools"
            tools.mkdir(parents=True)
            package=tools/"obs-studio-32.2.2"
            package.mkdir()
            binary=package/"run-obs"
            binary.symlink_to("/usr/bin/obs")
            with patch.object(m,"TOOLS",tools):
                with self.assertRaisesRegex(AssertionError,"ESCAPED"):
                    m.executable("obs")
        with patch.object(m.os,"geteuid",return_value=0):
            with self.assertRaisesRegex(AssertionError,"NO_ROOT"):
                m.guard()

    def test_internal_appimage_apprun_symlink_is_valid(self):
        with tempfile.TemporaryDirectory() as t:
            root=Path(t)/"skill-universal"
            tools=root/"tools"
            package=tools/"librecad-2.2.1.6/squashfs-root"
            (package/"bin").mkdir(parents=True)
            target=package/"bin/librecad"
            target.write_text("#!/bin/sh\n")
            target.chmod(0o700)
            (package/"AppRun").symlink_to("bin/librecad")
            with patch.object(m,"TOOLS",tools):
                resolved=m.executable("librecad")
            self.assertEqual(resolved,package/"AppRun")
            self.assertTrue(resolved.resolve().is_relative_to(tools))


if __name__=="__main__":
    unittest.main()
