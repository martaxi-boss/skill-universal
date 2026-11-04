"""Ferrari legacy path retirement never changes unrelated source or runtime data."""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "install/ferrari_alias_retirement.py"
spec = importlib.util.spec_from_file_location("ferrari_alias_retirement", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class FerrariAliasRetirementTests(unittest.TestCase):
    def test_exact_owned_launcher_assignments_only(self):
        for path, old, new in module.PATCHES:
            original = b"#!/usr/bin/env bash\n" + old + b"\nexec echo safe\n"
            migrated, changed = module.rewrite_exact(original, old, new)
            self.assertTrue(changed, str(path))
            self.assertEqual(migrated, original.replace(old, new))
            self.assertNotIn(old, migrated)
            unchanged, changed_again = module.rewrite_exact(migrated, old, new)
            self.assertFalse(changed_again)
            self.assertEqual(unchanged, migrated)

    def test_ambiguous_and_duplicate_old_paths_block(self):
        old = b"ROOT=legacy"
        new = b"ROOT=canonical"
        for content in (old + b"\n" + old, old + b"\n" + new, b"OTHER=unknown"):
            with self.subTest(content=content):
                with self.assertRaises(RuntimeError):
                    module.rewrite_exact(content, old, new)

    def test_exact_ferrari_locations_and_fallback(self):
        self.assertEqual(str(module.ROOT), "/srv/projects/skill-universal")
        self.assertEqual(str(module.ALIAS), "/home/ubuntu/.local/share/motor-ferrari")
        self.assertEqual(module.CURRENT, module.ROOT / "current")
        self.assertEqual(module.FALLBACK.parent, module.ROOT / "releases")
        self.assertEqual(len(module.PATCHES), 2)
        self.assertEqual({p.name for p, _, _ in module.PATCHES}, {"apktool", "valkey-server"})
        self.assertEqual(len(module.SERVICES), 9)

    def test_no_deployment_or_cross_project_writes(self):
        contents = SCRIPT.read_text()
        self.assertIn("if args.apply:", contents)
        self.assertIn("real_rea_mcp_probe()", contents)
        self.assertIn("ALIAS.unlink()", contents)
        self.assertIn("ALIAS.symlink_to(ROOT)", contents)
        self.assertIn("for path, original, mode in reversed(edited):", contents)
        self.assertNotIn("shutil.rmtree", contents)
        self.assertNotIn("systemctl restart", contents)
        self.assertNotIn("git reset", contents)


if __name__ == "__main__":
    unittest.main()
