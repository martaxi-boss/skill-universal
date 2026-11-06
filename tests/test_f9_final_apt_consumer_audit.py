"""F9 cross-project APT consumer scanner is read-only and fail-closed."""
import ast
from importlib.util import module_from_spec, spec_from_file_location
import os
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest
import time

SOURCE=Path(__file__).resolve().parents[1]/"install/vps-f9-final-apt-consumer-audit.py"
spec=spec_from_file_location("f9_apt_readonly",SOURCE)
m=module_from_spec(spec)
spec.loader.exec_module(m)

class F9FinalAptAuditTests(unittest.TestCase):
    def test_fixed_eight_targets_and_no_mutation_commands(self):
        self.assertEqual(len(m.PACKAGES),8)
        self.assertEqual(set(m.PACKAGES),{"yt-dlp","librecad","qgis",
           "audacity","obs-studio","solvespace","synfigstudio","openshot-qt"})
        self.assertEqual(len(m.SERVICES),8)
        code=SOURCE.read_text(encoding="utf-8")
        ast.parse(code)
        for forbidden in ('"apply"', '"purge", *PACKAGES', '"apt-get", "-y"',
                          '"apt-get", "install"', 'shutil.rmtree(', 'os.unlink(',
                          'os.remove(', 'rm -rf', 'git reset'):
            self.assertNotIn(forbidden,code)
        self.assertIn('"apt-get", "-s", "purge", *PACKAGES',code)
        self.assertIn('"package_purge_authorized": False',code)

    def test_cross_project_scan_detects_real_binary_references_without_leaking_source(self):
        with TemporaryDirectory() as td:
            root=Path(td)/"fadego"
            root.mkdir()
            (root/"startup.sh").write_text("#!/bin/sh\nexec /usr/bin/yt-dlp --version\n")
            (root/"options.json").write_text('{"tool":"librecad"}')
            outside=Path(td)/"private"
            outside.mkdir()
            (outside/"secret.sh").write_text("obs-studio")
            (root/"alias.sh").symlink_to(outside/"secret.sh")
            r=m.consumer_scan(root,time.monotonic()+12,{"/usr/bin/other"})
            self.assertTrue(r["complete_for_selected_source_types"])
            self.assertGreater(r["mentions_of_global_program_names"].get("yt-dlp",0),0)
            self.assertGreater(r["mentions_of_global_program_names"].get("librecad",0),0)
            self.assertNotIn(str(outside),str(r))
            self.assertNotIn("secret.sh",str(r))

    def test_large_executable_config_blocks_complete_scan(self):
        with TemporaryDirectory() as td:
            root=Path(td)/"pink-iptv"
            root.mkdir()
            (root/"large.sh").write_bytes(b"x"*20)
            with patch.object(m,"MAX_FILE",10):
                r=m.consumer_scan(root,time.monotonic()+12,set())
            self.assertEqual(r["large_code_files_unchecked"],1)
            self.assertFalse(r["complete_for_selected_source_types"])

    def test_simulated_apt_cannot_hide_extra_removal(self):
        def fake(args,timeout=40):
            if args[0]=="dpkg-query" and "-W" in args:
                return SimpleNamespace(returncode=0,stdout="install ok installed|1.0")
            if args[:2]==["dpkg-query","-L"]:
                return SimpleNamespace(returncode=0,stdout="/usr/bin/yt-dlp\n")
            if args[:3]==["apt-get","-s","purge"]:
                return SimpleNamespace(returncode=0,stdout=
                    "".join("Purg "+p+" [1]\n" for p in m.PACKAGES)+"Purg nginx [1]\n")
            raise AssertionError(args)
        with patch.object(m,"command",side_effect=fake):
            states,owned,exact=m.package_state()
        self.assertEqual(len(states),8)
        self.assertIn("/usr/bin/yt-dlp",owned)
        self.assertFalse(exact)

    def test_guard_does_not_accept_other_projects_as_ferrari_root(self):
        with TemporaryDirectory() as td:
            bad=Path(td)/"skill-universal"
            bad.mkdir()
            with patch.object(m,"ROOT",bad):
                with self.assertRaisesRegex(RuntimeError,"POINTER"):
                    m.verify_release()

if __name__=="__main__":
    unittest.main()
