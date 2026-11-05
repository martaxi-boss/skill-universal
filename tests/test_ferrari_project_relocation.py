"""Ferrari project relocation keeps installers and hygiene inside physical project."""
import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1]


class FerrariPrivateProjectMigrationTests(unittest.TestCase):
    def test_installers_only_accept_expected_alias(self):
        for name in ("vps-external-agents.sh","vps-rea-providers.sh"):
            script=(BASE/"install"/name).read_text()
            self.assertIn("FERRARI_PROJECT_ALIAS_INVALID",script)
            self.assertIn('ROOT="/srv/projects/skill-universal"',script)
            self.assertIn('[[ ! -L "/srv/projects/skill-universal" ]]',script)
            self.assertNotIn("rea-final-runtime",script)

    def _load_hygiene(self):
        spec=importlib.util.spec_from_file_location(
            "ferrari_hygiene_alias",BASE/"install/ferrari-hygiene.py")
        module=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_release_preview_works_with_exact_isolated_symlink(self):
        h=self._load_hygiene()
        with TemporaryDirectory() as td:
            base=Path(td)
            home=base/"home/ubuntu"
            physical=base/"srv/projects/skill-universal"
            release=physical/"releases"/"146145d5ada9c13e368df18727e4dbf4f5807664"
            fallback=physical/"releases"/"40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
            for installed in (release,fallback):
                (installed/"engine").mkdir(parents=True)
                (installed/"engine/ferrari.py").write_text("Ferrari")
            (physical/"runtimes").mkdir()
            (physical/"current").symlink_to(release,target_is_directory=True)
            alias=home/".local/share/motor-ferrari"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(physical,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(h,"PROJECT_ROOT",physical):
                result=h.clean(apply=False)
            self.assertEqual(result["status"],"PASS")
            self.assertEqual(result["active"],release.name)
            self.assertIn(fallback.name,result["preserved_releases"])
            self.assertEqual(result["removed_releases"],[])
            self.assertEqual(result["outside_ferrari_touched"],False)

    def test_wrong_project_alias_is_refused_before_cleanup(self):
        h=self._load_hygiene()
        with TemporaryDirectory() as td:
            base=Path(td)
            home=base/"home/ubuntu"
            physical=base/"srv/projects/skill-universal"
            foreign=base/"srv/projects/rea-final-runtime"
            physical.mkdir(parents=True)
            foreign.mkdir(parents=True)
            alias=home/".local/share/motor-ferrari"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(foreign,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(h,"PROJECT_ROOT",physical):
                with self.assertRaisesRegex(RuntimeError,"outside its isolated directory"):
                    h.clean(apply=True)


if __name__=="__main__":
    unittest.main()
