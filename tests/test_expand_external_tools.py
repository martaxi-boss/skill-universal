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
