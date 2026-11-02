"""JADX/Ghidra/Java25 independent and digest-pinned installation contract."""
from pathlib import Path
import unittest
S=(Path(__file__).resolve().parents[1]/"install/vps-specialist-engines.sh").read_text()
class SpecialistRuntime(unittest.TestCase):
    def test_official_hashes_and_no_global_java(self):
        for marker in ("68982529869257d0ee6b824ec5aa270ff8b118bb438670da0b97ebdab178d7fb",
                       "545ea2be9c242511bc145755cf4bda2485ade42966e096f8b4d3da2a230e8974",
                       "2c2cd776db3c1f6a097ba418922378ac3649cadd5e844a6f5f088ae628a7be67",
                       "FERRARI_JADX_FUNCTIONAL=PASS","FERRARI_GHIDRA_HEADLESS_FUNCTIONAL=PASS",
                       "sha256sum -c -"):
            self.assertIn(marker,S)
        self.assertNotIn("sudo ",S)
        self.assertNotIn("update-alternatives",S)
if __name__=="__main__":
    unittest.main()
