"""F9 private creative suite: four official AppImages, no global APT."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import io
import gc
import warnings
import json
import os
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "install/vps-phase9-private-appimages.py"
SPEC = spec_from_file_location("ferrari_f9_private_appimages", SOURCE)
mod = module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FerrariPhase9AppimageTests(unittest.TestCase):
    def test_all_four_pinned_official_x64_assets(self):
        expected = {
            "librecad": (82846008, "f2d86e6a40ec684b758c821eff3496a7d36e69f17519cde0b508a66d72c5754c"),
            "audacity": (73726456, "a5f8787aa13cdb500a60fc013403b986776876b960cca962bc6e7fff066172f3"),
            "synfig": (115539968, "b85aabc26f690a0c150d2143c656c17f358b73abbedf8d01007f15a7a95740e9"),
            "openshot": (258921664, "662d0c3cec67ddc90df6a8b0c723c0aac0d3bddf0c3c467eff562e818bb8c72f"),
        }
        self.assertEqual(set(mod.ASSETS), set(expected))
        for key, (size, sha) in expected.items():
            self.assertEqual((mod.ASSETS[key]["size"], mod.ASSETS[key]["sha256"]), (size, sha))
            self.assertTrue(mod.url(key).startswith("https://github.com/"))
            self.assertTrue(mod.url(key).endswith(mod.ASSETS[key]["filename"]))

    def test_rejects_global_installs_and_root(self):
        source = SOURCE.read_text(encoding="utf-8")
        for bad in ("apt-get ", "sudo ", "pip install", "autoremove", "git reset",
                    "shell=True", "rm -rf", "/usr/local/bin/"):
            self.assertNotIn(bad, source)
        with patch.object(mod.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "ROOT_NOT_ALLOWED"):
                mod.guard()

    def test_private_root_and_runtime_required(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            root.mkdir()
            tools = root / "tools"
            runtime = root / ".runtime"
            tools.mkdir()
            runtime.mkdir()
            with patch.object(mod, "ROOT", root), patch.object(mod, "TOOLS", tools), \
                 patch.object(mod, "RUNTIME", runtime), \
                 patch.object(mod, "guard"):
                self.assertEqual(mod.directory("librecad"), tools / "librecad-2.2.1.6")
                with self.assertRaisesRegex(RuntimeError, "NOT_INSTALLED"):
                    mod.check("librecad")

    def test_fetch_rejects_mismatch(self):
        payload = b"synthetic"
        with tempfile.TemporaryDirectory() as td, \
             patch.object(mod.urllib.request, "urlopen",
                          side_effect=lambda *args, **kwargs: io.BytesIO(payload)):
            with self.assertRaisesRegex(RuntimeError, "DOWNLOAD_HASH_MISMATCH"):
                mod.fetch("librecad", Path(td) / "artifact")

    def test_install_is_atomic_and_check_is_idempotent(self):
        data = b"fake-stable-appimage"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            tools = root / "tools"
            runtime = root / ".runtime"
            tools.mkdir(parents=True)
            runtime.mkdir()
            a = {**mod.ASSETS["librecad"],
                 "size": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            def fake_fetch(key, dst):
                dst.write_bytes(data)
                dst.chmod(0o700)
            def fake_extract(cmd, cwd=None, **kwargs):
                extracted = Path(cwd) / "squashfs-root"
                extracted.mkdir()
                app = extracted / "AppRun"
                app.write_text("#!/bin/sh\nexit 0\n")
                app.chmod(0o755)
                return SimpleNamespace(returncode=0, stdout="", stderr="")
            with patch.object(mod, "ROOT", root), patch.object(mod, "TOOLS", tools), \
                 patch.object(mod, "RUNTIME", runtime), patch.object(mod, "guard"), \
                 patch.dict(mod.ASSETS, {"librecad": a}), \
                 patch.object(mod, "fetch", side_effect=fake_fetch), \
                 patch.object(mod.subprocess, "run", side_effect=fake_extract) as exe:
                result = mod.install("librecad")
                self.assertEqual(result["status"], "private_appimage_verified")
                self.assertFalse(result["gui_runtime_certified"])
                exe.assert_called_once()
                again = mod.install("librecad")
                self.assertEqual(again, result)
                self.assertEqual(exe.call_count, 1)
                self.assertEqual(list(runtime.iterdir()), [])
                self.assertEqual(
                    json.loads((mod.directory("librecad") / "manifest.json").read_text())["sha256"],
                    a["sha256"])

    def test_failed_extraction_leaves_no_installation(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            tools, runtime = root / "tools", root / ".runtime"
            tools.mkdir(parents=True)
            runtime.mkdir()
            with patch.object(mod, "ROOT", root), patch.object(mod, "TOOLS", tools), \
                 patch.object(mod, "RUNTIME", runtime), patch.object(mod, "guard"), \
                 patch.object(mod, "fetch", side_effect=lambda k, p: p.write_bytes(b"abcd")), \
                 patch.object(mod.subprocess, "run",
                              return_value=SimpleNamespace(returncode=1, stdout="", stderr="oops")):
                with self.assertRaisesRegex(RuntimeError, "EXTRACT_FAILED"):
                    mod.install("audacity")
                self.assertFalse(mod.directory("audacity").exists())
                self.assertEqual(list(runtime.iterdir()), [])

    def test_manifest_is_strictly_checked(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            tools, runtime = root / "tools", root / ".runtime"
            tools.mkdir(parents=True)
            runtime.mkdir()
            a = {**mod.ASSETS["librecad"], "size": 4,
                 "sha256": hashlib.sha256(b"good").hexdigest()}
            home = tools / "librecad-2.2.1.6"
            home.mkdir()
            (home / a["filename"]).write_bytes(b"good")
            run = home / "squashfs-root" / "AppRun"
            run.parent.mkdir()
            run.write_text("#!/bin/sh\n")
            run.chmod(0o700)
            (home / "manifest.json").write_text("{}")
            with patch.object(mod, "ROOT", root), patch.object(mod, "TOOLS", tools), \
                 patch.object(mod, "RUNTIME", runtime), patch.dict(mod.ASSETS, {"librecad": a}):
                with self.assertRaisesRegex(RuntimeError, "MANIFEST_MISMATCH"):
                    mod.check("librecad")

    def test_synfig_type1_records_hash_only_without_extraction_claim(self):
        payload = b"\x7fELFfake-type1-appimage"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            tools, runtime = root / "tools", root / ".runtime"
            tools.mkdir(parents=True)
            runtime.mkdir()
            a = {**mod.ASSETS["synfig"], "size": len(payload),
                 "sha256": hashlib.sha256(payload).hexdigest()}
            def fake_fetch(key, dst):
                dst.write_bytes(payload)
                dst.chmod(0o700)
            with patch.object(mod, "ROOT", root), patch.object(mod, "TOOLS", tools), \
                 patch.object(mod, "RUNTIME", runtime), patch.object(mod, "guard"), \
                 patch.dict(mod.ASSETS, {"synfig": a}), \
                 patch.object(mod, "fetch", side_effect=fake_fetch), \
                 patch.object(mod.subprocess, "run") as extraction:
                # Regression: the real VPS activation previously emitted a
                # ResourceWarning from an unclosed Synfig Type-1 header read.
                with warnings.catch_warnings(record=True) as captured:
                    warnings.simplefilter("always", ResourceWarning)
                    result = mod.install("synfig")
                    gc.collect()
                leaked = [w for w in captured
                          if issubclass(w.category, ResourceWarning)
                          and a["filename"] in str(w.message)]
                self.assertFalse(leaked, "Synfig archive descriptor must close")
                self.assertEqual(result["status"], "private_appimage_verified")
                self.assertFalse(result["extraction_verified"])
                self.assertFalse(result["gui_runtime_certified"])
                self.assertTrue(result["private_path"].endswith(a["filename"]))
                extraction.assert_not_called()
                self.assertEqual(mod.check("synfig"), result)
                self.assertEqual(list(runtime.iterdir()), [])



if __name__ == "__main__":
    unittest.main()
