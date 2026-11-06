"""Phase 10: reversible-uninstall boundaries exercised on disposable project copies only.

This is NOT a claim that the production Ferrari was uninstalled; no VPS access.
"""
from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest


def fingerprint(tree: Path) -> dict[str, str]:
    """Hash independent-project canaries without exposing content."""
    return {
        p.relative_to(tree).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in tree.rglob("*") if p.is_file() and not p.is_symlink()
    }


def remove_disposable_ferrari_only(projects: Path) -> None:
    """Test-only operation: must have a strictly isolated, ephemeral parent."""
    root = projects / "skill-universal"
    if projects.name != "projects" or not projects.parent.name.startswith("f10-simulation-"):
        raise RuntimeError("not a test-only isolated project root")
    if projects.is_symlink() or root.is_symlink() or not root.is_dir():
        raise RuntimeError("ambiguous target")
    if root.resolve(strict=True).parent != projects.resolve(strict=True):
        raise RuntimeError("escaped project parent")
    for child in root.rglob("*"):
        if child.is_symlink():
            # Symlinks pointing to any other project are not Ferrari-owned dependencies.
            if not child.resolve(strict=False).is_relative_to(root.resolve(strict=True)):
                raise RuntimeError("external application dependency")
    shutil.rmtree(root)


class Phase10IsolatedUninstallSimulation(unittest.TestCase):
    def test_removal_of_ferrari_copy_preserves_every_other_project(self):
        with TemporaryDirectory(prefix="f10-simulation-") as d:
            projects = Path(d) / "projects"
            for name in ("skill-universal", "pink-iptv", "fadego", "lowcost-europa",
                         "telegram-robot-leads", "iptvpn-bot", "Codex", "VPS"):
                p = projects / name
                (p / "private").mkdir(parents=True)
                (p / "private" / "artifact.dat").write_bytes(("private-canary:" + name).encode())
            ferrari = projects / "skill-universal"
            (ferrari / "releases").mkdir()
            (ferrari / "releases" / "active").mkdir()
            (ferrari / "current").symlink_to(ferrari / "releases" / "active")
            others = {p.name: fingerprint(p) for p in projects.iterdir() if p.name != "skill-universal"}
            remove_disposable_ferrari_only(projects)
            self.assertFalse(ferrari.exists())
            self.assertEqual({p.name: fingerprint(p) for p in projects.iterdir()}, others)

    def test_external_dependency_symlink_blocks_removal_without_writes(self):
        with TemporaryDirectory(prefix="f10-simulation-") as d:
            projects = Path(d) / "projects"
            ferrari, other = projects / "skill-universal", projects / "pink-iptv"
            ferrari.mkdir(parents=True)
            other.mkdir(parents=True)
            (other / "sentinel").write_text("unchanged")
            (ferrari / "shared").symlink_to(other, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "external application dependency"):
                remove_disposable_ferrari_only(projects)
            self.assertTrue(ferrari.is_dir())
            self.assertEqual((other / "sentinel").read_text(), "unchanged")

    def test_symlinked_ferrari_root_blocks_removal(self):
        with TemporaryDirectory(prefix="f10-simulation-") as d:
            projects = Path(d) / "projects"
            projects.mkdir()
            other = projects / "fadego"
            other.mkdir()
            (other / "sentinel").write_text("unchanged")
            (projects / "skill-universal").symlink_to(other, target_is_directory=True)
            with self.assertRaisesRegex(RuntimeError, "ambiguous target"):
                remove_disposable_ferrari_only(projects)
            self.assertTrue((other / "sentinel").is_file())


if __name__ == "__main__":
    unittest.main()
