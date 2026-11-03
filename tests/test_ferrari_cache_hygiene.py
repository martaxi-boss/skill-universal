"""Ferrari cache hygiene: tests that private runtimes and other projects survive."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from tempfile import TemporaryDirectory
import os
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = spec_from_file_location("ferrari_cache_hygiene", ROOT / "install/ferrari-cache-hygiene.py")
hygiene = module_from_spec(spec)
spec.loader.exec_module(hygiene)


def fixture(base: Path):
    ferrari = base / "motor-ferrari"
    release = ferrari / "releases" / ("a" * 40)
    (release / "engine").mkdir(parents=True)
    (release / "engine/ferrari.py").write_text("engine")
    (ferrari / "current").symlink_to(release, target_is_directory=True)
    modules = ferrari / ".runtime/npm/rea/node_modules"
    cli = modules / "rea-agents/bin/cli.js"
    cli.parent.mkdir(parents=True)
    cli.write_text("official private rea")
    (modules / ".bin").mkdir()
    (modules / ".bin/rea").symlink_to("../rea-agents/bin/cli.js")
    for rel in ("runtimes/node-22.23.4/bin/node",
                "runtimes/jdk-25.0.5_8/bin/java",
                "tools/apktool-3.0.3/bin/apktool",
                ".runtime/npm/ruflo/node_modules/.bin/ruflo"):
        p = ferrari / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("preserve")
    cache = ferrari / ".runtime/npm-cache/_cacache"
    cache.mkdir(parents=True)
    (cache / "download-blob").write_bytes(b"X" * 8192)
    return ferrari, cache


class FerrariCacheHygieneTests(unittest.TestCase):
    def test_audit_does_not_touch_private_rea_or_cache(self):
        with TemporaryDirectory() as tmp:
            ferrari, cache = fixture(Path(tmp))
            a = hygiene.audit(ferrari)
            self.assertEqual(a["status"], "PASS")
            self.assertEqual(a["mode"], "audit")
            self.assertFalse(a["cache_removed"])
            self.assertTrue((cache / "download-blob").exists())
            self.assertTrue((ferrari / ".runtime/npm/rea/node_modules/.bin/rea").is_file())

    def test_apply_only_removes_cached_downloads(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            ferrari, cache = fixture(base)
            outside = base / "another-project"
            outside.mkdir()
            (outside / "sensitive-data").write_text("untouched")
            a = hygiene.audit(ferrari, apply=True)
            self.assertEqual(a["status"], "PASS")
            self.assertTrue(a["cache_removed"])
            self.assertFalse(cache.exists())
            self.assertTrue((ferrari / ".runtime/npm/rea/node_modules/.bin/rea").is_file())
            self.assertTrue((ferrari / "tools/apktool-3.0.3/bin/apktool").is_file())
            self.assertEqual((outside / "sensitive-data").read_text(), "untouched")

    def test_refuse_symlinked_cache_without_touching_target(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            ferrari, cache = fixture(base)
            outside = base / "outside"
            outside.mkdir()
            (outside / "file").write_text("preserve")
            (cache / "link").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "Symlink"):
                hygiene.audit(ferrari, apply=True)
            self.assertTrue((cache / "download-blob").exists())
            self.assertEqual((outside / "file").read_text(), "preserve")

    def test_project_migration_alias_is_safe_for_private_cache_audit(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            physical,cache=fixture(base)
            home=base/"home/ubuntu"
            alias=home/".local/share/motor-ferrari"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(physical,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(hygiene,"PROJECT_ROOT",physical):
                result=hygiene.audit(alias)
            self.assertEqual(result["status"],"PASS")
            self.assertFalse(result["cache_removed"])
            self.assertTrue(cache.is_dir())

    def test_project_migration_rejects_foreign_alias(self):
        with TemporaryDirectory() as tmp:
            base=Path(tmp)
            foreign,cache=fixture(base)
            expected=base/"srv/projects/skill-universal"
            expected.mkdir(parents=True)
            home=base/"home/ubuntu"
            alias=home/".local/share/motor-ferrari"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(foreign,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(hygiene,"PROJECT_ROOT",expected):
                with self.assertRaisesRegex(RuntimeError,"outside isolated project"):
                    hygiene.audit(alias,apply=True)
            self.assertTrue(cache.is_dir())

    def test_refuse_external_rea_cli(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            ferrari, cache = fixture(base)
            external = base / "external-rea"
            external.write_text("never use")
            cli = ferrari / ".runtime/npm/rea/node_modules/.bin/rea"
            cli.unlink()
            cli.symlink_to(external)
            with self.assertRaisesRegex(RuntimeError, "external"):
                hygiene.audit(ferrari, apply=True)
            self.assertTrue(cache.is_dir())
            self.assertEqual(external.read_text(), "never use")


if __name__ == "__main__":
    unittest.main()
