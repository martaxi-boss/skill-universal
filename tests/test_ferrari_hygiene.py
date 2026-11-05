"""Scope constraints on Ferrari's own release pruning only."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
class HygieneScope(unittest.TestCase):
    def test_cleanup_is_release_scoped(self):
        s=(ROOT/"install/ferrari-hygiene.py").read_text()
        self.assertIn('release_root=root/"releases"',s)
        self.assertIn("40",s)
        self.assertIn('pointer=root/"current"',s)
        self.assertIn("active=pointer.resolve(strict=True)",s)
        self.assertIn("shutil.rmtree(p)",s)
        self.assertIn("outside_ferrari_touched",s)
        self.assertIn('fallback_sha="62f862cdf9727842546a244a3e4ec19dd8bc82f4"',s)
        self.assertNotIn("apt-get",s)
        self.assertNotIn("/root",s)
if __name__=="__main__":
    unittest.main()
