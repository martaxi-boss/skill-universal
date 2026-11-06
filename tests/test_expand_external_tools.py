"""Inventory contracts for the remaining 15 selected external Ferrari programs."""
from pathlib import Path
import unittest
from engine import ferrari

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"install/vps-expand-external.sh"

class ExternalProgramsTests(unittest.TestCase):
    def test_group_has_exactly_fifteen_selection_candidates(self):
        selected=[x for x in ferrari.ubuntu_selection() if x["curated_tier"]=="external_upstream" and x["id"] not in {"ghidra","jadx","rea","ruflo","vite","playwright"}]
        self.assertEqual(len(selected),15)
        self.assertEqual({x["id"] for x in selected},
            {"freecad","comfyui","nextjs","tailwind","bootstrap",
             "shadcn","docling","typst","duckdb","polars","streamlit",
             "gradio","godot","faster-whisper","prefect"})

    def test_installer_keeps_private_python_and_node_dependencies(self):
        src=SCRIPT.read_text()
        self.assertIn('ROOT="/srv/projects/skill-universal"',src)
        self.assertIn('NODE="$ROOT/runtimes/node-22.23.4/bin/node"',src)
        self.assertIn('dir="$ROOT/.runtime/venvs/extended/$tool"',src)
        self.assertIn('root="$ROOT/.runtime/npm/$tool"',src)
        self.assertNotIn("record penpot",src)
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
            (root/"bin").mkdir(parents=True)
            private=root/"bin/valkey-server"
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

    def test_valkey_dependencies_are_ferrari_private(self):
        script=(ROOT/"install/vps-expand-services-gui.sh").read_text()
        self.assertIn("apt-get download liblzf1",script)
        self.assertIn('liblzf.so.1',script)
        self.assertIn('cat > "$out/bin/valkey-server"',script)
        self.assertIn('export LD_LIBRARY_PATH=',script)
        self.assertIn("FERRARI_VALKEY_EXTERNAL_BINARY_FORBIDDEN",script)
        self.assertIn("FERRARI_PROJECT_ALIAS_INVALID",script)
        self.assertIn('ROOT="/srv/projects/skill-universal"',script)
        self.assertIn('[[ ! -L "/srv/projects/skill-universal" ]]',script)
        self.assertLess(script.index('ROOT="/srv/projects/skill-universal"'),
                        script.index('REPORT="$ROOT/.runtime/expansion-33"'))
        self.assertNotIn("sudo -n apt-get install -y liblzf1",script)

    def test_binary_archive_path_is_initialized_after_directory(self):
        source=SCRIPT.read_text()
        self.assertIn('local dest="$ROOT/tools/$id-$version"',source)
        self.assertIn('local file="$dest/archive.$suffix"',source)
        self.assertNotIn('local dest="$ROOT/tools/$id-$version" file=',source)

    def test_official_current_linux_binaries_are_pinned(self):
        source=SCRIPT.read_text()
        self.assertIn("typst-x86_64-unknown-linux-musl.tar.xz",source)
        self.assertIn("Godot_v4.7.2-stable_linux.x86_64.zip",source)
        self.assertIn("FreeCAD_1.1.4-Linux-x86_64-py311.AppImage",source)
        self.assertIn("sha256sum -c -",source)
        self.assertNotIn("godot3",source)
        self.assertNotIn("gradio typst",source)
        self.assertIn("GUI_UNTESTED",source)

    def test_skill_inventory_includes_owned_expansion_report(self):
        import json,tempfile
        from unittest.mock import patch
        from engine import tool_runtime
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            report=home/".runtime/expansion-33/services-gui.json"
            report.parent.mkdir(parents=True)
            report.write_text(json.dumps({"project":"motor-ferrari","items":[
                {"group":"service","id":"prometheus","status":"INSTALLED_PRIVATE"}
            ],"installed":1,"pending":[]}))
            with patch.object(tool_runtime,"HOME",home):
                result=tool_runtime.inventory()
        self.assertEqual(result["expansion"]["services_gui"]["installed"],1)
        self.assertEqual(result["expansion"]["services_gui"]["items"][0]["id"],"prometheus")

    def test_each_candidate_has_individual_install_record(self):
        src=SCRIPT.read_text()
        for pkg in ("nextjs","tailwind","bootstrap","shadcn","duckdb","polars",
                    "streamlit","gradio","typst","faster-whisper","prefect",
                    "docling","freecad","godot","comfyui"):
            self.assertIn(pkg,src)
        self.assertNotIn("record penpot",src)
        self.assertIn("FERRARI_EXTERNAL_INSTALLED=",src)
        self.assertIn("FERRARI_EXTERNAL_PENDING=",src)

if __name__=="__main__":
    unittest.main()
