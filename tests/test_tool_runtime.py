"""Ferrari tool runtime tests, both catalogued and callable Ubuntu programs."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from engine import tool_runtime, orchestrator

class ToolRuntimeTests(unittest.TestCase):
    def test_56_selected_and_25_action_specs(self):
        x=tool_runtime.inventory()
        self.assertEqual(x["selected"],56)
        self.assertEqual(x["registered_actions"],32)
        self.assertEqual(len(x["programs"]),len(set(p["id"] for p in x["programs"])))
        self.assertTrue(any(p["id"]=="rea" for p in x["programs"]))
        self.assertTrue(any(p["id"]=="blender" for p in x["programs"]))
    def test_manifest_is_typed(self):
        x=tool_runtime.specs()
        self.assertEqual(len(x),32)
        self.assertTrue(all("{input}" in s["args"] for s in x.values()))
        self.assertTrue(all(s["mode"] in {"stdout","file","directory"} for s in x.values()))
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
    def test_auto_preview_and_execute_exact_supported_action(self):
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/fake"):
            preview=tool_runtime.auto("Converter markdown para docx","/tmp/example.md")
            self.assertEqual(preview["selected"]["action"],"pandoc-md-docx")
            self.assertEqual(preview["status"],"preview")
            with patch.object(tool_runtime,"invoke",return_value={"confirmed":True}) as invoke:
                done=tool_runtime.auto("Converter markdown para docx","/tmp/example.md",
                                       "/tmp/output",execute=True)
                self.assertTrue(done["executed"])
                self.assertEqual(done["status"],"completed")
                invoke.assert_called_once_with("pandoc-md-docx","/tmp/example.md","/tmp/output")
    def test_auto_never_executes_without_match(self):
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/fake"):
            result=tool_runtime.auto("tarefa desconhecida xxx sem adaptador","/tmp/x.txt",
                                     "/tmp/output",execute=True)
            self.assertFalse(result["executed"])
            self.assertEqual(result["status"],"no_matching_installed_adapter")
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
    def test_read_only_python_module_detection(self):
        from importlib.machinery import ModuleSpec
        with patch("importlib.util.find_spec",return_value=ModuleSpec("cv2",loader=None,origin="/usr/lib/cv2.so")):
            self.assertEqual(tool_runtime.python_module_location("opencv"),"/usr/lib/cv2.so")
        self.assertIsNone(tool_runtime.python_module_location("not-a-python-package"))

    def test_existing_ocrmypdf_adapter_uses_pdf_and_no_shell(self):
        import subprocess
        spec=tool_runtime.specs()["ocrmypdf-searchable-pdf"]
        self.assertEqual(spec["tool"],"ocrmypdf")
        self.assertEqual(spec["extensions"],[".pdf"])
        self.assertEqual(spec["mode"],"file")
        self.assertEqual(spec["artifact"],"searchable.pdf")
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/"scan.pdf"
            source.write_bytes(b"%PDF-1.4\\n")
            output=Path(d)/"converted"
            def record(args,**kwargs):
                self.assertFalse(kwargs.get("shell",False))
                self.assertEqual(args[0],"/usr/bin/ocrmypdf")
                self.assertIn(str(source),args)
                self.assertIn(str(output/"searchable.pdf"),args)
                (output/"searchable.pdf").write_bytes(b"%PDF-1.4\\noutput")
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/ocrmypdf"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=record):
                    result=tool_runtime.invoke("ocrmypdf-searchable-pdf",str(source),str(output))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["tool"],"ocrmypdf")

    def test_ocrmypdf_route_filters_pdf_and_detects_missing_executable(self):
        with patch.object(tool_runtime,"executable",
                          side_effect=lambda tool,binary=None: "/usr/bin/ocrmypdf" if tool=="ocrmypdf" else None):
            found=tool_runtime.route("Criar pdf pesquisavel com ocrmypdf","/tmp/scan.pdf")
            self.assertEqual(found["suggestions"][0]["action"],"ocrmypdf-searchable-pdf")
            not_pdf=tool_runtime.route("Criar pdf pesquisavel com ocrmypdf","/tmp/scan.png")
            self.assertEqual(not_pdf["suggestions"],[])
        with patch.object(tool_runtime,"executable",return_value=None):
            self.assertEqual(tool_runtime.route("ocrmypdf","/tmp/scan.pdf")["suggestions"],[])

    def test_installed_apktool_decodes_to_directory_artifact(self):
        import subprocess
        action=tool_runtime.specs()["apktool-decode-resources"]
        self.assertEqual(action["tool"],"apktool")
        self.assertEqual(action["extensions"],[".apk"])
        self.assertEqual(action["mode"],"directory")
        with tempfile.TemporaryDirectory() as folder:
            inp=Path(folder)/"ferrari.apk"
            inp.write_bytes(b"PK\\x03\\x04mock")
            out=Path(folder)/"out"
            decoded=out/"apktool-decoded"
            def execute(args,**kwargs):
                self.assertEqual(args[0],"/usr/bin/apktool")
                self.assertEqual(args[1],"d")
                self.assertEqual(args[-1],str(inp))
                self.assertIn(str(decoded),args)
                self.assertFalse(kwargs.get("shell",False))
                decoded.mkdir()
                (decoded/"apktool.yml").write_text("apkFileName: ferrari.apk")
                (decoded/"AndroidManifest.xml").write_text("<manifest />")
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/apktool"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=execute):
                    result=tool_runtime.invoke("apktool-decode-resources",str(inp),str(out))
            self.assertTrue(result["confirmed"])
            self.assertEqual(result["artifacts"],[str(decoded)])
            self.assertTrue((decoded/"AndroidManifest.xml").is_file())

    def test_apktool_requires_nonempty_real_directory(self):
        import subprocess
        with tempfile.TemporaryDirectory() as folder:
            inp=Path(folder)/"ferrari.apk"
            inp.write_bytes(b"PK\\x03\\x04mock")
            def pretend(args,**kwargs):
                (Path(folder)/"out"/"apktool-decoded").mkdir()
                return subprocess.CompletedProcess(args,0,b"",b"")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/apktool"):
                with patch.object(tool_runtime.subprocess,"run",side_effect=pretend):
                    with self.assertRaisesRegex(RuntimeError,"Decoded directory empty"):
                        tool_runtime.invoke("apktool-decode-resources",str(inp),str(Path(folder)/"out"))
            wrong=Path(folder)/"other.txt"
            wrong.write_text("not an apk")
            with patch.object(tool_runtime,"executable",return_value="/usr/bin/apktool"):
                with self.assertRaisesRegex(ValueError,"Input format not supported"):
                    tool_runtime.invoke("apktool-decode-resources",str(wrong),str(Path(folder)/"other-out"))

    def test_apktool_action_routes_apk_only_and_requires_installation(self):
        with patch.object(tool_runtime,"executable",side_effect=lambda tool,binary=None: "/usr/bin/apktool" if tool=="apktool" else None):
            result=tool_runtime.route("descodificar apk com apktool","/tmp/sample.apk")
            self.assertEqual(result["suggestions"][0]["action"],"apktool-decode-resources")
            self.assertEqual(tool_runtime.route("descodificar apk com apktool","/tmp/sample.jar")["suggestions"],[])
        with patch.object(tool_runtime,"executable",return_value=None):
            self.assertEqual(tool_runtime.route("apktool","/tmp/sample.apk")["suggestions"],[])

    def test_base_operations_are_registered_separately(self):
        with patch.object(tool_runtime,"executable",return_value="/usr/bin/fake"):
            inv=tool_runtime.inventory()
        for tool,op in (("jadx","apk-decompile"),("blender","blender-house"),
                        ("openscad","cad-stl"),("libreoffice","office-pdf")):
            item=next(x for x in inv["programs"] if x["id"]==tool)
            self.assertIn(op,item["base_operations"])
            self.assertEqual(item["status"],"callable")

    def test_parameterized_ripgrep_action(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"ferrari.txt";p.write_text("Motor Ferrari integrado\nOutro programa\n")
            with patch.object(tool_runtime,"executable",return_value="rg"):
                with self.assertRaises(ValueError):
                    tool_runtime.invoke("ripgrep-find-text",str(p),str(Path(d)/"missing-query"))
            with patch.object(tool_runtime,"executable",return_value="rg"):
                with patch.object(tool_runtime.subprocess,"run") as execute:
                    execute.return_value.returncode=0
                    execute.return_value.stdout=b"1:Motor Ferrari integrado\n"
                    outcome=tool_runtime.invoke("ripgrep-find-text",str(p),str(Path(d)/"found"),query="Ferrari")
            self.assertEqual(Path(outcome["artifacts"][0]).read_text(),"1:Motor Ferrari integrado\n")
            self.assertIn("Ferrari",execute.call_args.args[0])

    def test_no_arbitrary_shell_execution(self):
        src=Path(tool_runtime.__file__).read_text()
        self.assertIn("shell=False",src)
        self.assertNotIn("shell=True",src)
if __name__=="__main__":
    unittest.main()
