"""F9 OBS Studio: official Ubuntu 24.04 private .deb, no system installation."""
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import hashlib
import io
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "install/vps-phase9-private-obs24.py"
SPEC = spec_from_file_location("ferrari_f9_obs24", SOURCE)
mod = module_from_spec(SPEC)
SPEC.loader.exec_module(mod)


class FerrariObsPrivateTests(unittest.TestCase):
    def test_official_ubuntu_2404_pinned_release(self):
        self.assertEqual(mod.VERSION, "32.2.2")
        self.assertEqual(mod.SIZE, 134324516)
        self.assertEqual(mod.SHA256,
                         "b6557ca2059287210332accc94c267094050489cffffc5c832e746e3a418dab0")
        self.assertTrue(mod.URL.startswith("https://github.com/obsproject/obs-studio/releases/"))
        self.assertTrue(mod.FILENAME.endswith("-Ubuntu-24.04-x86_64.deb"))
        self.assertIn("skill-universal/tools/obs-studio-32.2.2", str(mod.TARGET))

    def test_no_global_apts_root_or_services(self):
        code = SOURCE.read_text()
        for denied in ("apt-get ", "apt install", "sudo ", "pip install",
                       "rm -rf", "systemctl start", "obs --startstreaming",
                       "shell=True", "autoremove"):
            self.assertNotIn(denied, code)
        with patch.object(mod.os, "geteuid", return_value=0):
            with self.assertRaisesRegex(RuntimeError, "ROOT_NOT_ALLOWED"):
                mod.guard()

    def test_reject_untrusted_download(self):
        with tempfile.TemporaryDirectory() as td, \
             patch.object(mod.urllib.request, "urlopen",
                          return_value=io.BytesIO(b"not-the-official-deb")):
            with self.assertRaisesRegex(RuntimeError, "SHA_MISMATCH"):
                mod.retrieve(Path(td) / "asset.deb")

    def test_detect_private_binary_not_external_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "unpacked"
            (root / "usr/bin").mkdir(parents=True)
            (root / "usr/bin/obs").symlink_to("/usr/bin/obs")
            with self.assertRaisesRegex(RuntimeError, "NO_PRIVATE_EXECUTABLE"):
                mod.obs_binary(root)
            target = root / "opt/obs-studio/bin/obs"
            target.parent.mkdir(parents=True)
            target.write_text("#!/bin/sh\n")
            target.chmod(0o700)
            self.assertEqual(mod.obs_binary(root), "opt/obs-studio/bin/obs")

    def test_install_private_atomic_and_idempotent(self):
        payload = b"some-valid-deb-stub"
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            runtime, tools = root / ".runtime", root / "tools"
            runtime.mkdir(parents=True)
            tools.mkdir()
            target = tools / "obs-studio-32.2.2"
            def fake_retrieve(dst):
                dst.write_bytes(payload)
            def fake_run(cmd, **kwargs):
                if cmd[0] == "dpkg-deb" and "-x" in cmd:
                    unpacked = Path(cmd[-1])
                    binary = unpacked / "usr/bin/obs"
                    binary.parent.mkdir(parents=True)
                    binary.write_text("#!/bin/sh\n")
                    binary.chmod(0o700)
                    return SimpleNamespace(returncode=0, stdout="", stderr="")
                if cmd[0] == "dpkg-deb" and "-f" in cmd:
                    return SimpleNamespace(returncode=0,
                                           stdout="Package: obs-studio\nVersion: 32.2.2\nArchitecture: amd64\n",
                                           stderr="")
                return SimpleNamespace(returncode=0,
                                       stdout="OBS Studio 32.2.2\n", stderr="")
            with patch.multiple(mod, ROOT=root, RUNTIME=runtime, TOOLS=tools,
                                TARGET=target, SIZE=len(payload),
                                SHA256=hashlib.sha256(payload).hexdigest()), \
                 patch.object(mod, "guard"), patch.object(mod, "retrieve", side_effect=fake_retrieve), \
                 patch.object(mod.subprocess, "run", side_effect=fake_run) as process:
                result = mod.install()
                self.assertEqual(result["status"], "private_obs_package_verified")
                self.assertTrue(result["cli_version_tested"])
                self.assertFalse(result["websocket_studio_certified"])
                self.assertFalse(result["dependency_isolation_certified"])
                self.assertEqual(result, mod.install())
                self.assertEqual(process.call_count, 3)
                self.assertEqual(list(runtime.iterdir()), [])
                self.assertTrue((target / "payload/usr/bin/obs").is_file())

    def test_extract_failure_keeps_project_unmodified(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "skill-universal"
            runtime, tools = root / ".runtime", root / "tools"
            runtime.mkdir(parents=True)
            tools.mkdir()
            target = tools / "obs-studio-32.2.2"
            with patch.multiple(mod, ROOT=root, RUNTIME=runtime, TOOLS=tools, TARGET=target), \
                 patch.object(mod, "guard"), \
                 patch.object(mod, "retrieve",
                              side_effect=lambda dst: dst.write_bytes(b"stub")), \
                 patch.object(mod.subprocess, "run",
                              return_value=SimpleNamespace(returncode=1, stdout="", stderr="fail")):
                with self.assertRaisesRegex(RuntimeError, "DEB_EXTRACT_FAILED"):
                    mod.install()
                self.assertFalse(target.exists())
                self.assertEqual(list(runtime.iterdir()), [])

    def test_launcher_prioritizes_bundled_libobs_over_host(self):
        script=mod.launcher_source()
        self.assertIn('usr/local/lib/x86_64-linux-gnu',script)
        self.assertIn('env["LD_LIBRARY_PATH"] = ":".join(local)',script)
        self.assertLess(script.index("usr/local/lib/x86_64-linux-gnu"),
                        script.index("opt/obs-studio/lib"))

    def test_refuses_to_replace_unknown_private_launcher(self):
        payload=b"synthetic-package"
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)/"obs-studio-32.2.2"
            root.mkdir()
            (root/mod.FILENAME).write_bytes(payload)
            exe=root/"payload/usr/local/bin/obs"
            exe.parent.mkdir(parents=True)
            exe.write_text("#!/bin/sh\n")
            exe.chmod(0o700)
            libs=root/"payload/usr/local/lib/x86_64-linux-gnu"
            libs.mkdir(parents=True)
            (libs/"libobs.so.30").write_bytes(b"private")
            original="unsafe unrecognized launcher"
            (root/"run-obs").write_text(original)
            manifest={"source":mod.URL,"sha256":hashlib.sha256(payload).hexdigest(),
                      "version":mod.VERSION,"bytes":len(payload),
                      "obs_relative_exe":"usr/local/bin/obs"}
            (root/"manifest.json").write_text(json.dumps(manifest))
            with patch.multiple(mod,TARGET=root,SIZE=len(payload),
                                SHA256=hashlib.sha256(payload).hexdigest()),\
                 patch.object(mod,"guard"):
                with self.assertRaisesRegex(RuntimeError,"UNKNOWN_LAUNCHER"):
                    mod.repair_launcher()
            self.assertEqual((root/"run-obs").read_text(),original)


if __name__ == "__main__":
    unittest.main()
