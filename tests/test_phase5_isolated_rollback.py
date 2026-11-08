"""Exercise the production Ferrari release's real rollback/switch shell code.

An isolated fake project tree is created under this project's .runtime.
No service, production symlink, global package or other project is modified.
When FERRARI_PHASE5_LIVE_ROOT is set, read the active VPS script directly.
"""
from __future__ import annotations

import os
import hashlib
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest

EXPECTED_ACTIVE_SHA = "40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
# Historical VPS phase-5 fixture preserves the original immutable bytes.
EXPECTED_LEGACY_SCRIPT_BLOB = "2b1f7703b96a963af01af02bc9617e7554b85a98"
# The source-tree test uses the newer adapter-gated preactivation script.
EXPECTED_SCRIPT_BLOB = "1ebfa84c05fe1e35d3eec8cf874ea83edc72c9fe"
LIVE_ROOT = os.environ.get("FERRARI_PHASE5_LIVE_ROOT")
ROOT = (Path(LIVE_ROOT) if LIVE_ROOT else Path(__file__).resolve().parents[1]).resolve()
SCRIPT = (ROOT / "current/install/vps-isolated-release.sh"
          if LIVE_ROOT else ROOT / "install/vps-isolated-release.sh")


def release_shell_blocks():
    """Extract UNCHANGED rollback and atomic switch statements from real source."""
    data = SCRIPT.read_bytes()
    # Git blob hash confirms that the tested bytes are the deployed source.
    blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
    expected = EXPECTED_LEGACY_SCRIPT_BLOB if LIVE_ROOT else EXPECTED_SCRIPT_BLOB
    assert blob == expected, "FERRARI_PHASE5_ACTIVE_SCRIPT_BLOB_MISMATCH"
    source = data.decode("utf-8")
    begin = source.index("cleanup() {\n")
    end = source.index("\ntrap cleanup EXIT", begin) + len("\ntrap cleanup EXIT")
    cleanup = source[begin:end]
    switch_begin = source.index('NEXT="$ROOT/.current.next.$$"', end)
    switch_end = source.index('\ncd "$ROOT/current"', switch_begin)
    switch = source[switch_begin:switch_end]
    assert 'if [[ "$SWITCHED" == 1 && "$PASSED" != 1 ]]' in cleanup
    assert 'mv -Tf "$back" "$ROOT/current"' in cleanup
    assert 'mv -Tf "$NEXT" "$ROOT/current"' in switch
    assert 'ln -s "$RELEASE" "$NEXT"' in switch
    assert "FERRARI_RELEASE_ROLLBACK=PASS" in cleanup
    return cleanup, switch


class FerrariPhase5IsolatedRollback(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.live_before = None
        if LIVE_ROOT:
            expected = ROOT / "releases" / EXPECTED_ACTIVE_SHA
            current = ROOT / "current"
            assert current.is_symlink(), "FERRARI_PHASE5_LIVE_CURRENT_NOT_SYMLINK"
            assert current.resolve(strict=True) == expected, "FERRARI_PHASE5_LIVE_SHA_CHANGED"
            cls.live_before = current.resolve(strict=True)
            assert SCRIPT.is_file(), "FERRARI_PHASE5_LIVE_SCRIPT_MISSING"
        cls.cleanup, cls.switch = release_shell_blocks()

    @classmethod
    def tearDownClass(cls):
        if LIVE_ROOT:
            assert (ROOT / "current").resolve(strict=True) == cls.live_before, (
                "FERRARI_PHASE5_PRODUCTION_CURRENT_CHANGED"
            )
            print("FERRARI_PHASE5_PRODUCTION_UNCHANGED=PASS", flush=True)

    def exercise(self, name: str, *, inject_failure: bool, before_switch: bool = False):
        scratch = ROOT / ".runtime"
        scratch.mkdir(exist_ok=True)
        self.assertTrue(scratch.is_dir() and not scratch.is_symlink())
        with tempfile.TemporaryDirectory(prefix=".phase5-rollback-", dir=scratch) as base:
            fake = Path(base) / "fake-project"
            releases = fake / "releases"
            runtime = fake / ".runtime"
            releases.mkdir(parents=True)
            runtime.mkdir()
            previous = releases / "previous"
            candidate = releases / "candidate"
            for item in (previous, candidate):
                (item / "engine").mkdir(parents=True)
                (item / "engine/ferrari.py").write_text("# test fixture only\n")
            (fake / "current").symlink_to(previous, target_is_directory=True)
            (fake / "do-not-touch").write_text("KEEP")
            work = runtime / ".release-verify-cert"
            work.mkdir()
            stage = releases / ".staging-cert"
            stage.mkdir()
            (stage / "transient").write_text("DELETE")
            setup = "\n".join((
                "set -Eeuo pipefail",
                "umask 077",
                "ROOT=" + shlex.quote(str(fake)),
                "PREVIOUS=" + shlex.quote(str(previous)),
                "RELEASE=" + shlex.quote(str(candidate)),
                "WORK=" + shlex.quote(str(work)),
                "STAGED=" + shlex.quote(str(stage)),
                "SWITCHED=0",
                "PASSED=0",
                self.cleanup,
                "",
            ))
            if before_switch:
                script = setup + "exit 19\n"
                expected_exit = 19
                expected_target = previous
            else:
                script = setup + self.switch + '\nSWITCHED=1\ncd "$ROOT/current"\n'
                if inject_failure:
                    script += 'echo "FERRARI_PHASE5_INJECTED_POST_SWITCH_FAILURE" >&2\nexit 37\n'
                    expected_exit = 37
                    expected_target = previous
                else:
                    script += 'PASSED=1\nexit 0\n'
                    expected_exit = 0
                    expected_target = candidate
            # Source executed only by bash with explicit paths in a copy.
            proc = subprocess.run(["bash", "-c", script], capture_output=True, text=True,
                                  timeout=12, check=False)
            self.assertEqual(proc.returncode, expected_exit, proc.stderr)
            self.assertEqual((fake / "current").resolve(strict=True), expected_target)
            self.assertEqual((fake / "do-not-touch").read_text(), "KEEP")
            self.assertFalse(stage.exists(), "staging was not removed")
            self.assertFalse(work.exists(), "work was not removed")
            self.assertFalse(list(fake.glob(".current.next.*")))
            self.assertFalse(list(fake.glob(".current.rollback.*")))
            self.assertTrue(previous.is_dir() and candidate.is_dir())
            if inject_failure and not before_switch:
                self.assertIn("FERRARI_RELEASE_ROLLBACK=PASS", proc.stderr)
                print("FERRARI_PHASE5_ROLLBACK_INJECTED_FAILURE=PASS", flush=True)
            else:
                self.assertNotIn("FERRARI_RELEASE_ROLLBACK=PASS", proc.stderr)
            return proc

    def test_post_switch_failure_restores_previous(self):
        self.exercise("failure", inject_failure=True)

    def test_pre_switch_failure_keeps_current(self):
        self.exercise("before-switch", inject_failure=True, before_switch=True)

    def test_successful_switch_preserves_candidate(self):
        self.exercise("success", inject_failure=False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
