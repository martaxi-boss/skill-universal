"""F9 yt-dlp: Ferrari-only, pinned-release and fail-closed unit tests."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock
import hashlib
import io
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "install/vps-phase9-private-ytdlp.py"
SPEC = spec_from_file_location("phase9_private_ytdlp", SOURCE)
mod = module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class Phase9YtDlpPrivateTests(unittest.TestCase):
    def test_release_is_pinned_to_official_linux_amd64_asset(self):
        self.assertEqual(mod.VERSION, "2026.10.26")
        self.assertEqual(mod.SIZE, 41166968)
        self.assertEqual(mod.SHA256,
                         "767ba9dce7052aa196f8b12652f433d76de128ba168966fa84b6394d5e6c6795")
        self.assertEqual(mod.URL,
                         "https://github.com/yt-dlp/yt-dlp/releases/download/2026.10.26/yt-dlp_linux")
        self.assertEqual(str(mod.TARGET),
                         "/srv/projects/skill-universal/tools/yt-dlp-2026.10.26/yt-dlp")

    def test_script_does_not_modify_global_os_or_other_projects(self):
        code = SOURCE.read_text(encoding="utf-8")
        for prohibited in ("apt-get", "dpkg ", "sudo ", "pip install", "git reset",
                           "autoremove", "subprocess.Popen", "shell=True"):
            self.assertNotIn(prohibited, code)
        self.assertIn("F9_YTDLP_MUST_RUN_AS_PROJECT_USER", code)
        self.assertIn("F9_YTDLP_BINARY_DIGEST_MISMATCH", code)
        self.assertIn("real_media_download_tested", code)

    def test_refuses_root_before_installation(self):
        with patch.object(mod.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "MUST_RUN_AS_PROJECT_USER"):
                mod.root_guard()

    def test_smoke_requires_matching_version_and_generic_extractor(self):
        version = SimpleNamespace(returncode=0, stdout="2026.10.26\n")
        inventory = SimpleNamespace(returncode=0,
                                    stdout="\n".join(["generic"] + ["extractor"] * 520))
        with patch.object(mod.subprocess, "run", side_effect=[version, inventory]) as runner:
            outcome = mod.smoke(Path("/ferrari/yt-dlp"), Path("/ferrari/scratch"))
        self.assertEqual(outcome["version"], mod.VERSION)
        self.assertEqual(outcome["extractors_discovered"], 521)
        self.assertFalse(outcome["real_media_download_tested"])
        self.assertEqual(runner.call_count, 2)

    def test_smoke_fails_on_missing_generic(self):
        version = SimpleNamespace(returncode=0, stdout="2026.10.26\n")
        inventory = SimpleNamespace(returncode=0, stdout="extractor\n" * 520)
        with patch.object(mod.subprocess, "run", side_effect=[version, inventory]):
            with self.assertRaisesRegex(RuntimeError, "EXTRACTOR_SMOKE_FAILED"):
                mod.smoke(Path("/ferrari/yt-dlp"), Path("/ferrari/scratch"))

    def fake_paths(self, tmp):
        root = Path(tmp) / "skill-universal"
        runtime = root / ".runtime"
        tools = root / "tools"
        runtime.mkdir(parents=True)
        tools.mkdir()
        return {"ROOT": root, "RUNTIME": runtime, "TOOLS": tools,
                "TARGET": tools / ("yt-dlp-" + mod.VERSION) / "yt-dlp"}

    def test_downloads_only_into_private_tree_and_rechecks(self):
        payload = b"known-good-official-asset-for-unit-test"
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.fake_paths(tmp)
            with patch.multiple(mod, **paths), \
                    patch.object(mod, "root_guard"), \
                    patch.object(mod, "SIZE", len(payload)), \
                    patch.object(mod, "SHA256", hashlib.sha256(payload).hexdigest()), \
                    patch.object(mod.urllib.request, "urlopen",
                                 side_effect=lambda *_, **__: io.BytesIO(payload)) as fetch, \
                    patch.object(mod, "smoke", return_value={
                        "version": mod.VERSION, "extractors_discovered": 1200,
                        "real_media_download_tested": False}) as smoke:
                outcome = mod.run(install=True)
                self.assertEqual(outcome["status"], "private_installed_verified")
                self.assertEqual(paths["TARGET"].read_bytes(), payload)
                self.assertTrue(paths["TARGET"].is_relative_to(paths["ROOT"]))
                self.assertEqual(fetch.call_count, 1)
                self.assertEqual(smoke.call_count, 1)
                self.assertEqual(list(paths["RUNTIME"].iterdir()), [])
                second = mod.run(install=False)
                self.assertEqual(second["status"], "private_existing_verified")
                self.assertEqual(fetch.call_count, 1)

    def test_checksum_failure_never_publishes_an_executable(self):
        payload = b"tampered-package"
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.fake_paths(tmp)
            with patch.multiple(mod, **paths), \
                    patch.object(mod, "root_guard"), \
                    patch.object(mod, "SIZE", len(payload)), \
                    patch.object(mod, "SHA256", "0" * 64), \
                    patch.object(mod.urllib.request, "urlopen",
                                 side_effect=lambda *_, **__: io.BytesIO(payload)), \
                    patch.object(mod, "smoke") as smoke:
                with self.assertRaisesRegex(RuntimeError, "DOWNLOAD_DIGEST_MISMATCH"):
                    mod.run(install=True)
                self.assertFalse(paths["TARGET"].exists())
                self.assertFalse(paths["TARGET"].parent.exists())
                self.assertEqual(list(paths["RUNTIME"].iterdir()), [])
                smoke.assert_not_called()

    def test_check_on_missing_binary_does_not_download(self):
        with tempfile.TemporaryDirectory() as tmp:
            paths = self.fake_paths(tmp)
            with patch.multiple(mod, **paths), patch.object(mod, "root_guard"), \
                    patch.object(mod.urllib.request, "urlopen") as fetch:
                out = mod.run(install=False)
                self.assertEqual(out["status"], "private_missing")
                self.assertFalse(paths["TARGET"].parent.exists())
                fetch.assert_not_called()


if __name__ == "__main__":
    unittest.main()
