"""F14 final closure must preserve truthful scope and one Ferrari catalog."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"docs/FERRARI_F14_GUI_CERTIFICACOES_FINAL_20261108.md"
SKILL=ROOT/"skill/motor-universal-linux/SKILL.md"
BOOT=ROOT/"BOOTSTRAP.md"

class FerrariF14ClosureDocs(unittest.TestCase):
    def test_real_evidence_and_limits(self):
        report=REPORT.read_text(encoding="utf-8")
        skill=SKILL.read_text(encoding="utf-8")
        bootstrap=BOOT.read_text(encoding="utf-8")
        for doc in (report,skill,bootstrap):
            self.assertIn("42515392261",doc)
            self.assertIn("42516534292",doc)
            self.assertIn("Audacity",doc)
            self.assertIn("SolveSpace",doc)
            self.assertIn("Synfig",doc)
            self.assertIn("OBS",doc)
            self.assertIn("FFmpeg",doc)
        for marker in ("400", "13,333333","46 185", "0c170035a8ca4e98ca2ef7d5b9e9269f17d717e78416bbfad8aa15258e0bb50e", "MKV", "GUI", "não"):
            self.assertIn(marker,report)
        self.assertIn("v1.0.19",skill)
        self.assertIn("v1.0.19",bootstrap)
        self.assertLess(len(bootstrap),24000)
    def test_no_new_fictitious_catalog_operations(self):
        report=REPORT.read_text(encoding="utf-8")
        for marker in ("173 programas","280 funções","458 entradas"):
            self.assertIn(marker,report)
        self.assertIn("não",report.lower())
    def test_same_plugin_identity_version(self):
        import json
        manifest=json.loads((ROOT/"packaging/motor-ferrari/plugin.json").read_text())
        self.assertEqual(manifest["version"],"1.0.19")
        self.assertEqual(manifest["name"],"motor-universal-linux")

if __name__=="__main__":
    unittest.main()
