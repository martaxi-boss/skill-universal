"""Ferrari: optional heavy-tool installers do not change other services."""
from pathlib import Path
import json
import tempfile
import unittest
from unittest.mock import patch
from engine import tool_runtime

ROOT=Path(__file__).resolve().parents[1]
HEAVY=ROOT/"install/vps-expand-heavy.sh"

class HeavyToolsTests(unittest.TestCase):
    def test_heavy_upstreams_are_versioned_and_locally_isolated(self):
        src=HEAVY.read_text()
        self.assertIn("Comfy-Org/ComfyUI.git",src)
        self.assertIn("v0.43.0",src)
        self.assertIn("download.pytorch.org/whl/cpu",src)
        self.assertIn("penpot/penpot/$PENPOT_VERSION/docker/images/docker-compose.yaml",src)
        self.assertIn("PENPOT_VERSION=2.18.5",src)
        self.assertIn('ROOT="/srv/projects/skill-universal"', (ROOT/"install/vps-bim-web.sh").read_text())
        self.assertIn('ROOT="/srv/projects/skill-universal"',src)

    def test_heavy_installation_never_starts_other_projects_or_network_services(self):
        src=HEAVY.read_text()
        for forbidden in ("systemctl start","systemctl enable","docker compose up",
                          "docker run","--listen 0.0.0.0","/root/rea","/opt/REA",
                          "pip install --break-system-packages"):
            self.assertNotIn(forbidden,src)
        self.assertIn("IMAGES_READY_NOT_RUNNING",src)
        self.assertIn("INSTALLED_CPU_NO_MODELS",src)
        self.assertIn("PREPARED_NEEDS_DOCKER",src)

    def test_heavy_report_is_read_back_into_skill_inventory(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            path=home/".runtime/expansion-33/heavy.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps({"project":"motor-ferrari","items":[
                {"id":"comfyui","status":"INSTALLED_CPU_NO_MODELS"},
                {"id":"penpot","status":"PREPARED_NEEDS_DOCKER"}]}))
            with patch.object(tool_runtime,"HOME",home):
                result=tool_runtime.inventory()
            self.assertEqual(len(result["expansion"]["heavy"]["items"]),2)
            self.assertEqual(result["expansion"]["heavy"]["items"][1]["status"],"PREPARED_NEEDS_DOCKER")

    def test_comfyui_source_is_detected_only_when_cpu_smoke_passed(self):
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            root=home/"tools/comfyui-v0.43.0"
            root.mkdir(parents=True)
            (root/"main.py").write_text("# Ferrari-owned ComfyUI source")
            venv=home/".runtime/venvs/extended/comfyui/bin"
            venv.mkdir(parents=True)
            (venv/"python").write_text("# venv")
            report=home/".runtime/expansion-33/heavy.json"
            report.parent.mkdir(parents=True)
            report.write_text(json.dumps({"project":"motor-ferrari","items":[
                {"id":"comfyui","status":"PENDING_CPU_TORCH"}]}))
            with patch.object(tool_runtime,"HOME",home):
                self.assertIsNone(tool_runtime.ferrari_source_presence("comfyui"))
                report.write_text(json.dumps({"project":"motor-ferrari","items":[
                    {"id":"comfyui","status":"INSTALLED_CPU_NO_MODELS"}]}))
                with patch("engine.tool_runtime.shutil.which",return_value="/old-rea/comfyui"):
                    self.assertIsNone(tool_runtime.executable("comfyui","comfyui"))
                result=tool_runtime.inventory()
                found=next(x for x in result["programs"] if x["id"]=="comfyui")
                self.assertTrue(found["installed"])
                self.assertEqual(found["status"],"installed_unintegrated")
                self.assertEqual(found["detection"],"ferrari_cpu_source")
                self.assertEqual(found["path"],str(root))
                self.assertFalse(found["ecosystem_evidence"]["model_inference_tested"])
            # The old REA must not count as a private ComfyUI runtime.
            (root/"main.py").unlink()
            with patch.object(tool_runtime,"HOME",home):
                self.assertIsNone(tool_runtime.ferrari_source_presence("comfyui"))

    def test_called_in_ferrari_installer_only(self):
        src=(ROOT/"install/vps-delivery.sh").read_text()
        self.assertIn("BLOCKED_LEGACY_GLOBAL_APT",src)
        self.assertNotIn("bash install/vps-expand-heavy.sh",src)
        self.assertIn('ROOT="/srv/projects/skill-universal"',HEAVY.read_text())

if __name__=="__main__":
    unittest.main()
