"""Ferrari tool runtime tests, both catalogued and callable Ubuntu programs."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from engine import tool_runtime, orchestrator

class ToolRuntimeTests(unittest.TestCase):
    def test_56_selected_and_12_action_specs(self):
        x=tool_runtime.inventory()
        self.assertEqual(x["selected"],56)
        self.assertEqual(x["registered_actions"],12)
        self.assertEqual(len(x["programs"]),len(set(p["id"] for p in x["programs"])))
        self.assertTrue(any(p["id"]=="rea" for p in x["programs"]))
        self.assertTrue(any(p["id"]=="blender" for p in x["programs"]))
    def test_manifest_is_typed(self):
        x=tool_runtime.specs()
        self.assertEqual(len(x),12)
        self.assertTrue(all("{input}" in s["args"] for s in x.values()))
        self.assertTrue(all(s["mode"] in {"stdout","file"} for s in x.values()))
    def test_missing_binary_blocks_before_output_created(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.json";p.write_text("{}")
            with patch.object(tool_runtime,"executable",return_value=None):
                with self.assertRaises(RuntimeError):
                    tool_runtime.invoke("jq-format-json",str(p),str(Path(d)/"out"))
            self.assertFalse((Path(d)/"out").exists())
    def test_reject_symlink_and_existing_result(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"a.json";p.write_text("{}")
            link=Path(d)/"b.json";link.symlink_to(p)
            with self.assertRaises(ValueError):
                tool_runtime.invoke("jq-format-json",str(link),str(Path(d)/"out"))
            out=Path(d)/"out";out.mkdir()
            (out/"formatted.json").write_text("already")
            with self.assertRaises(FileExistsError):
                tool_runtime.invoke("jq-format-json",str(p),str(out))
    def test_route_selects_installed_tools_and_not_guesses(self):
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/fake"):
            r=tool_runtime.route("Converter markdown para docx","/tmp/demo.md")
            self.assertEqual(r["suggestions"][0]["action"],"pandoc-md-docx")
            self.assertFalse(r["executed"])
            unknown=tool_runtime.route("comando sem correspondencia nos adaptadores")
            self.assertEqual(unknown["suggestions"],[])
    def test_orchestrator_accepts_bound_tool_step(self):
        data={"version":1,"steps":[{"id":"convert","operation":"tool","tool":"pandoc",
              "action":"pandoc-md-docx","input":"/tmp/source.md"}]}
        valid=orchestrator.validate_workflow(data)
        self.assertEqual(valid[0]["tool"],"pandoc")
        self.assertEqual(valid[0]["action"],"pandoc-md-docx")
    def test_mismatched_or_arbitrary_tool_action_rejected(self):
        bad=[
          {"id":"test","operation":"tool","tool":"ffmpeg","action":"jq-format-json","input":"/tmp/source.json"},
          {"id":"test","operation":"tool","tool":"jq","action":"jq-format-json","input":"/tmp/source.json","shell":"echo"},
        ]
        for step in bad:
            with self.assertRaises(ValueError):
                orchestrator.validate_workflow({"version":1,"steps":[step]})
    def test_no_arbitrary_shell_execution(self):
        src=Path(tool_runtime.__file__).read_text()
        self.assertIn("shell=False",src)
        self.assertNotIn("shell=True",src)
if __name__=="__main__":
    unittest.main()
