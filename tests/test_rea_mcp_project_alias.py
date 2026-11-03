"""REA MCP accepts only the physical isolated Ferrari project symlink, never a legacy alias."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import rea_mcp


def private_tree(root):
    targets=[
        ".runtime/npm/rea/node_modules/rea-agents/scripts/rea.mjs",
        "runtimes/node-22.23.4/bin/node",
        "runtimes/jdk-25.0.5_8/bin/java",
        "tools/rea-providers/ghidra-12.1.4/support/analyzeHeadless",
        "tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar",
        "tools/apktool-3.0.3/bin/apktool",
    ]
    for name in targets:
        p=root/name
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("Ferrari synthetic test")
    link=root/".runtime/npm/rea/node_modules/.bin/rea"
    link.parent.mkdir(parents=True,exist_ok=True)
    link.symlink_to("../rea-agents/scripts/rea.mjs")


class FerrariReaProjectAliasTests(unittest.TestCase):
    def test_exact_ferrari_symlink_to_independent_project_is_accepted(self):
        with TemporaryDirectory() as td:
            base=Path(td)
            home=base/"home/ubuntu"
            alias=home/".local/share/motor-ferrari"
            physical=base/"srv/projects/skill-universal"
            private_tree(physical)
            alias.parent.mkdir(parents=True)
            alias.symlink_to(physical,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(rea_mcp,"PROJECT_ROOT",physical):
                cli,env=rea_mcp._resources(alias)
            self.assertTrue(cli.is_file())
            self.assertTrue(cli.resolve().is_relative_to(physical))
            self.assertEqual(env["GHIDRA_INSTALL_DIR"],str(alias/"tools/rea-providers/ghidra-12.1.4"))
            self.assertEqual(env["REA_JADX_MCP_JAR"],str(alias/"tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar"))
            self.assertNotIn("rea-final-runtime",str(env))

    def test_alias_to_unapproved_project_is_rejected(self):
        with TemporaryDirectory() as td:
            base=Path(td)
            home=base/"home/ubuntu"
            alias=home/".local/share/motor-ferrari"
            physical=base/"srv/projects/skill-universal"
            other=base/"srv/projects/rea-final-runtime"
            private_tree(other)
            physical.mkdir(parents=True)
            alias.parent.mkdir(parents=True)
            alias.symlink_to(other,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(rea_mcp,"PROJECT_ROOT",physical):
                with self.assertRaisesRegex(RuntimeError,"alias is not trusted"):
                    rea_mcp._resources(alias)

    def test_different_symlink_name_does_not_grant_access(self):
        with TemporaryDirectory() as td:
            base=Path(td)
            home=base/"home/ubuntu"
            physical=base/"srv/projects/skill-universal"
            private_tree(physical)
            alias=home/"some-other-project"
            alias.parent.mkdir(parents=True)
            alias.symlink_to(physical,target_is_directory=True)
            with patch.object(Path,"home",return_value=home), \
                 patch.object(rea_mcp,"PROJECT_ROOT",physical):
                with self.assertRaisesRegex(RuntimeError,"alias is not trusted"):
                    rea_mcp._resources(alias)


if __name__=="__main__":
    unittest.main()
