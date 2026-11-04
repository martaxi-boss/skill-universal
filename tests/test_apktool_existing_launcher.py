"""Verify that existing Apktool launchers migrate without changing unrelated content."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "install/vps-apktool-isolated.sh"
OLD = 'ROOT="$HOME/.local/share/motor-ferrari"'
NEW = 'ROOT="/srv/projects/skill-universal"'


class ExistingApktoolLauncherMigrationTests(unittest.TestCase):
    def _migration_python(self):
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertIn("FERRARI_APKTOOL_LAUNCHER_ROLLBACK=PASS", text)
        self.assertIn("FERRARI_APKTOOL_LAUNCHER_CANONICALIZED=PASS", text)
        self.assertIn('bash -n "$MIGRATION/new"', text)
        return text.split("<<'PY_MIGRATE'\n", 1)[1].split("\nPY_MIGRATE\n", 1)[0]

    def test_one_known_legacy_assignment_changes_and_other_content_stays(self):
        with TemporaryDirectory() as temp:
            old_file = Path(temp) / "before"
            migrated = Path(temp) / "after"
            original = "#!/usr/bin/env bash\n" + OLD + "\nexec \"$ROOT/bin/java\" --version\n"
            old_file.write_text(original)
            subprocess.run([sys.executable, "-c", self._migration_python(),
                            str(old_file), str(migrated)], check=True)
            self.assertEqual(old_file.read_text(), original)
            self.assertEqual(migrated.read_text(), original.replace(OLD, NEW))

    def test_multiple_legacy_assignments_are_rejected_without_new_file(self):
        with TemporaryDirectory() as temp:
            old_file = Path(temp) / "before"
            migrated = Path(temp) / "after"
            old_file.write_text(OLD + "\n" + OLD + "\n")
            proc = subprocess.run([sys.executable, "-c", self._migration_python(),
                                   str(old_file), str(migrated)],
                                  capture_output=True, text=True)
            self.assertNotEqual(proc.returncode, 0)
            self.assertFalse(migrated.exists())


if __name__ == "__main__":
    unittest.main()
