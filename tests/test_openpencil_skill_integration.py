"""OpenPencil as a backward-compatible input mode of Ferrari's one Skill operation.

No real npm runtime is required on the CI runner: command boundaries are mocked.
The VPS end-to-end smoke must separately certify the actual installed CLI.
"""
import base64
import json
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch
import zipfile

from engine import ferrari, openpencil, skill_job


HTML = b'<!doctype html><html><head><title>Design</title></head><body><main style="color:#333"><h1>Ferrari</h1></main></body></html>'


class OpenPencilSkillTests(unittest.TestCase):
    def runtime(self, work: Path):
        root = work / "skill-universal"
        node = root / "runtimes/node-22.23.4/bin/node"
        cli = root / ".runtime/npm/openpencil/node_modules/@open-pencil/cli/bin/openpencil.js"
        manifest = cli.parent.parent / "package.json"
        for path in (node, cli, manifest):
            path.parent.mkdir(parents=True, exist_ok=True)
        node.write_text("#!/bin/sh\n")
        node.chmod(0o755)
        cli.write_text("console.log('stub')\n")
        manifest.write_text('{"version":"0.16.0"}\n')
        return root, node, cli, manifest

    def simulator(self, command, **kwargs):
        args = command[2:]
        if args[0] == "import":
            Path(args[args.index("-o")+1]).write_bytes(b'FIG-SMOKE-FERRARI')
        elif args[0] == "export":
            target=Path(args[args.index("-o")+1])
            target.write_text(
                '<svg xmlns="http://www.w3.org/2000/svg"><text>Ferrari</text></svg>'
                if args[args.index("-f")+1]=="svg"
                else '<!doctype html><html><body>Ferrari</body></html>')
        return SimpleNamespace(returncode=0,stdout='{"document":"Ferrari"}',stderr="")

    def test_single_skill_to_openpencil_to_real_zip_contract(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            root,node,cli,manifest=self.runtime(base)
            job={"version":1,"id":"openpencil-skill-test","kind":"operation",
                 "operation":"web-template","layout":"store",
                 "input":{"name":"design.html","content_base64":base64.b64encode(HTML).decode()}}
            self.assertEqual(skill_job.validate_job(job),HTML)
            with patch.object(openpencil,"FERRARI_HOME",root), \
                 patch.object(openpencil,"NODE",node), \
                 patch.object(openpencil,"CLI",cli), \
                 patch.object(openpencil,"MANIFEST",manifest), \
                 patch.object(openpencil.subprocess,"run",side_effect=self.simulator) as call:
                result,code=skill_job.execute(job,base/"job")
            self.assertEqual(code,0,result)
            self.assertEqual(result["status"],"completed")
            self.assertEqual(result["executor"],str(node))
            self.assertEqual(call.call_count,4)
            self.assertTrue(all(not c.kwargs["shell"] for c in call.call_args_list))
            with zipfile.ZipFile(base/"job/response.zip") as archive:
                files=set(archive.namelist())
                self.assertTrue({
                    "report.json","artifacts/design.fig","artifacts/design.svg",
                    "artifacts/design.html","artifacts/design-info.json"
                }.issubset(files),files)
                self.assertIn(b"Ferrari",archive.read("artifacts/design.svg"))
                self.assertIn(b'"status": "completed"',archive.read("report.json"))

    def test_legacy_web_template_unchanged(self):
        with tempfile.TemporaryDirectory() as d:
            result=ferrari.run("web-template",d,title="No input legacy")
            self.assertTrue(result["confirmed"])
            self.assertTrue((Path(d)/"site/index.html").is_file())

    def test_reject_untrusted_html_before_runtime(self):
        inputs=(
            "<html><script>window.x=1</script></html>",
            '<html><img src="https://example.com/x.png"></html>',
            '<html><style>@import "http://example.com/style.css"</style></html>',
            '<html><style>body{background:url(file:///etc/passwd)}</style></html>',
            '<html><iframe src="//external.example"></iframe></html>',
            '<html><img src="../../etc/passwd"></html>',
            '<html><a href="/etc/passwd">Do not read</a></html>',
            '<svg><text>incomplete html</text></svg>',
        )
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"input.html"
            for source in inputs:
                p.write_text(source)
                with self.subTest(source=source[:25]):
                    with self.assertRaises(ValueError):
                        openpencil._source_html(p)
            p.write_bytes(b'x'*(openpencil.MAX_HTML+1))
            with self.assertRaises(ValueError):
                openpencil._source_html(p)

    def test_no_fallback_to_global_executable(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            root,node,cli,manifest=self.runtime(base)
            manifest.write_text('{"version":"999.0.0"}')
            with patch.object(openpencil,"FERRARI_HOME",root), \
                 patch.object(openpencil,"NODE",node), \
                 patch.object(openpencil,"CLI",cli), \
                 patch.object(openpencil,"MANIFEST",manifest):
                with self.assertRaises(RuntimeError):
                    openpencil._private_runtime()

    def test_web_contract_and_action_count_intact(self):
        from engine import tool_runtime
        self.assertIn("web-template",ferrari.OPS)
        self.assertEqual(len(tool_runtime.specs()),40)
        self.assertEqual(openpencil.VERSION,"0.16.0")


if __name__ == "__main__":
    unittest.main()
