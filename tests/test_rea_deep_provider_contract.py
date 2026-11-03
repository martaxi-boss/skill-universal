"""Ferrari deep REA provider smoke only accesses private installations and synthetic fixture."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=(ROOT/"install/vps-rea-deep-provider-smoke.sh").read_text(encoding="utf-8")

class ReaDeepFunctionalContract(unittest.TestCase):
    def test_only_private_rea_and_pinned_provider_paths(self):
        for word in (".runtime/npm/rea/node_modules/.bin/rea",
                     "tools/rea-providers/ghidra-12.1.4",
                     "tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar",
                     "tools/apktool-3.0.3/bin/apktool",
                     "realpath -e", "rea-final-runtime"):
            if word=="rea-final-runtime":
                self.assertNotIn(word,SCRIPT)
            else:
                self.assertIn(word,SCRIPT)
    def test_real_elf_and_synthetic_apk_calls(self):
        for marker in ("analyze /usr/bin/true --provider ghidra --json",
                       "inspect-android-class",
                       "FERRARI_REA_GHIDRA_NATIVE_ANALYSIS=PASS",
                       "FERRARI_REA_JADX_CLASS_ANALYSIS=PASS",
                       "FERRARI_REA_DEEP_PROVIDERS=PASS"):
            self.assertIn(marker,SCRIPT)
        self.assertNotIn("sudo ",SCRIPT)
        self.assertNotIn("rm -rf /home/ubuntu",SCRIPT)

if __name__=="__main__":
    unittest.main()
