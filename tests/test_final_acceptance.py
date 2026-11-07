import importlib.util
from pathlib import Path
import tempfile
from unittest import TestCase
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[1]/"install/vps-final-acceptance.py"
spec=importlib.util.spec_from_file_location("ferrari_acceptance",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class FinalAcceptanceTests(TestCase):
    def test_universal_catalog_guard(self):
        self.assertEqual(module.CURRENT,"205c6f0e970259c79fa2111b6670c2fe1672fb27")
        self.assertEqual(module.FALLBACK,"7bf6dcecf15da26502c5969b5eee54d5e116fc32")
        self.assertEqual(len(module.OLD),5)
    def test_no_unsafe_execution_paths(self):
        code=SOURCE.read_text()
        for forbidden in ("apt-get install","sudo ","pip install","shell=True",
                          "--startstreaming","systemctl stop","rm -rf"):
            self.assertNotIn(forbidden,code)
        self.assertIn("--startrecording",code)
    def test_obs_version_fail_is_not_recording_pass(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            exe=root/"run-obs"
            exe.write_text("test");exe.chmod(0o700)
            (root/".runtime").mkdir()
            with patch.object(module,"ROOT",root),patch.object(module,"OBS",exe),\
                 patch.object(module,"call",return_value=(1,"missing")):
                report=module.obs_qa()
            self.assertFalse(report["obs_local_recording_certified"])
            self.assertFalse(report["obs_interactive_gui_certified"])
            self.assertEqual(list((root/".runtime").iterdir()),[])
