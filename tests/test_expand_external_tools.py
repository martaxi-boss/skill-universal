"""Inventory contracts for the 16 additional external Ferrari programs."""
from pathlib import Path
import unittest
from engine import ferrari

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"install/vps-expand-external.sh"

class ExternalProgramsTests(unittest.TestCase):
    def test_group_has_exactly_sixteen_selection_candidates(self):
        selected=[x for x in ferrari.ubuntu_selection() if x["curated_tier"]=="external_upstream" and x["id"] not in {"ghidra","jadx","rea","ruflo","vite","playwright"}]
        self.assertEqual(len(selected),16)
        self.assertEqual({x["id"] for x in selected},
            {"freecad","penpot","comfyui","nextjs","tailwind","bootstrap",
             "shadcn","docling","typst","duckdb","polars","streamlit",
             "gradio","godot","faster-whisper","prefect"})

    def test_installer_keeps_private_python_and_node_dependencies(self):
        src=SCRIPT.read_text()
        self.assertIn('ROOT="$HOME/.local/share/motor-ferrari"',src)
        self.assertIn('NODE="$ROOT/runtimes/node-22.23.4/bin/node"',src)
        self.assertIn('dir="$ROOT/.runtime/venvs/extended/$tool"',src)
        self.assertIn('root="$ROOT/.runtime/npm/$tool"',src)
        self.assertIn("PENDING_CONTAINER_DEPLOYMENT",src)
        self.assertIn("PENDING_CPU_RUNTIME",src)
        for forbidden in ("npm install -g","pip install --break-system-packages",
                          "systemctl start","docker run","rm -rf /root/rea"):
            self.assertNotIn(forbidden,src)

    def test_owned_extended_venv_is_discovered(self):
        import tempfile
        from unittest.mock import patch
        from engine import runtime_discovery
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            private=home/".runtime/venvs/extended/duckdb/lib/python3.12/site-packages/duckdb"
            private.mkdir(parents=True)
            (private/"__init__.py").write_text("own Ferrari duckdb")
            with patch("engine.runtime_discovery.importlib.util.find_spec",return_value=None):
                result=runtime_discovery.python_presence("duckdb",home=home)
            self.assertEqual(result["scope"],"ferrari_venv")
            self.assertIn("extended/duckdb",result["location"])

    def test_gui_and_godot_ubuntu_executables_are_identified(self):
        from engine import tool_runtime
        self.assertEqual(tool_runtime.BINARIES["openshot"],"openshot-qt")
        self.assertEqual(tool_runtime.BINARIES["synfig"],"synfigstudio")
        self.assertEqual(tool_runtime.BINARIES["godot"],"godot")

    def test_valkey_is_detected_only_inside_private_ferrari_tree(self):
        import tempfile
        from unittest.mock import patch
        from engine import tool_runtime
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            root=base/"tools/ferrari-services/valkey-server"
            (root/"usr/bin").mkdir(parents=True)
            private=root/"usr/bin/valkey-server"
            private.write_text("Ferrari service executable")
            with patch.object(tool_runtime,"HOME",base):
                with patch.dict(tool_runtime.ISOLATED,{"valkey":private}):
                    self.assertEqual(tool_runtime.executable("valkey","valkey-server"),str(private))
            other=base/"external-valkey"
            other.write_text("legacy tool")
            private.unlink()
            private.symlink_to(other)
            with patch.object(tool_runtime,"HOME",base):
                with patch.dict(tool_runtime.ISOLATED,{"valkey":private}):
                    self.assertIsNone(tool_runtime.executable("valkey","valkey-server"))

    def test_official_current_linux_binaries_are_pinned(self):
        source=SCRIPT.read_text()
        self.assertIn("typst-x86_64-unknown-linux-musl.tar.xz",source)
        self.assertIn("Godot_v4.7.2-stable_linux.x86_64.zip",source)
        self.assertIn("FreeCAD_1.1.4-Linux-x86_64-py311.AppImage",source)
        self.assertIn("sha256sum -c -",source)
        self.assertNotIn("godot3",source)
        self.assertNotIn("gradio typst",source)
        self.assertIn("GUI_UNTESTED",source)

    def test_each_candidate_has_individual_install_record(self):
        src=SCRIPT.read_text()
        for pkg in ("nextjs","tailwind","bootstrap","shadcn","duckdb","polars",
                    "streamlit","gradio","typst","faster-whisper","prefect",
                    "docling","freecad","godot","penpot","comfyui"):
            self.assertIn(pkg,src)
        self.assertIn("FERRARI_EXTERNAL_INSTALLED=",src)
        self.assertIn("FERRARI_EXTERNAL_PENDING=",src)

if __name__=="__main__":
    unittest.main()
