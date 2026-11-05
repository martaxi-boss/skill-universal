"""Ferrari must not execute application programs owned by Ubuntu or other projects."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from engine import cad_tools, ferrari, tool_runtime

class ProjectIsolationTests(unittest.TestCase):
    def test_cad_ignores_global_and_external_symlink(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            with patch.object(cad_tools,"FERRARI_HOME",root):
                with patch.object(cad_tools.shutil,"which",return_value="/usr/bin/blender"):
                    with self.assertRaisesRegex(RuntimeError,"FERRARI_PRIVATE_EXECUTOR_MISSING"):
                        cad_tools._binary("blender")
                private=root/"tools/blender/blender"
                private.parent.mkdir(parents=True)
                private.symlink_to("/bin/true")
                with self.assertRaisesRegex(RuntimeError,"FERRARI_PRIVATE_EXECUTOR_MISSING"):
                    cad_tools._binary("blender")
                private.unlink()
                private.write_text("#!/bin/sh\nexit 0\n")
                private.chmod(0o755)
                self.assertEqual(cad_tools._binary("blender"),str(private))
    def test_base_operation_does_not_fallback_to_path(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(ferrari,"FERRARI_HOME",Path(folder)):
                with patch.object(ferrari.shutil,"which",return_value="/usr/bin/ffmpeg"):
                    with self.assertRaisesRegex(RuntimeError,"FERRARI_PRIVATE_EXECUTOR_MISSING"):
                        ferrari._exe("ffmpeg")
    def test_typed_adapter_has_no_global_fallback(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(tool_runtime,"PRIVATE_CLI_ROOT",Path(folder)):
                with patch.object(tool_runtime.shutil,"which",return_value="/usr/bin/jq"):
                    self.assertIsNone(tool_runtime.executable("jq","jq"))
    def test_inventory_never_counts_an_external_path(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(cad_tools,"FERRARI_HOME",Path(folder)):
                with patch.object(ferrari.shutil,"which",return_value="/usr/bin/blender"):
                    self.assertFalse(ferrari.present({"id":"blender","binary":"blender"}))

    def test_no_global_installs_in_entrypoints(self):
        from pathlib import Path
        root=Path(__file__).resolve().parents[1]
        for p in ("install/ferrari-ubuntu.sh","install/vps-cad-3d.sh",
                  "install/vps-delivery.sh","install/vps-expand-services-gui.sh"):
            s=(root/p).read_text()
            self.assertNotIn("apt-get install -y",s,p)
            self.assertNotIn("sudo -n apt-get install",s,p)
        self.assertIn("GLOBAL_APT_INSTALL_FORBIDDEN",(root/"install/ferrari-ubuntu.sh").read_text())
if __name__=="__main__":
    unittest.main()
