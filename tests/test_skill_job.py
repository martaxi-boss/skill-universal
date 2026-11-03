"""Ferrari direct Skill-to-Ubuntu job contract: parsing, outputs and safety."""
import base64
import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from unittest.mock import patch
from engine import skill_job

def req(kind="operation",**kwargs):
    return {"version":1,"id":"skill-smoke-1","kind":kind,**kwargs}

class SkillJobTests(unittest.TestCase):
    def test_generate_real_svg_and_zip(self):
        with tempfile.TemporaryDirectory() as d:
            result,code=skill_job.execute(req(operation="svg-poster",title="Ferrari Skill"),Path(d)/"job")
            self.assertEqual(code,0)
            self.assertEqual(result["status"],"completed")
            with zipfile.ZipFile(Path(d)/"job/response.zip") as z:
                self.assertIn("report.json",z.namelist())
                self.assertTrue(any(x.endswith(".svg") for x in z.namelist()))
                self.assertIn("Ferrari Skill",z.read(next(x for x in z.namelist() if x.endswith(".svg"))).decode())
    def test_auto_real_file_mime_and_zip(self):
        with tempfile.TemporaryDirectory() as d:
            raw=base64.b64encode(b'{"hello":42}\n').decode("ascii")
            data=req("invoke",action="file-mime",input={"name":"test.json","content_base64":raw})
            result,code=skill_job.execute(data,Path(d)/"job")
            self.assertEqual(code,0)
            with zipfile.ZipFile(Path(d)/"job/response.zip") as z:
                self.assertEqual(z.read("report.json").startswith(b"{"),True)
                self.assertIn(b"json",z.read("artifacts/mime.txt"))
    def test_apktool_decoded_directory_is_returned_inside_existing_skill_zip(self):
        with tempfile.TemporaryDirectory() as d:
            raw=base64.b64encode(b"PK\\x03\\x04synthetic").decode("ascii")
            data=req("invoke",action="apktool-decode-resources",
                     input={"name":"test.apk","content_base64":raw})
            def decoder(action,source,folder,query=None):
                self.assertEqual(action,"apktool-decode-resources")
                decoded=Path(folder)/"apktool-decoded"
                decoded.mkdir(parents=True)
                (decoded/"apktool.yml").write_text("apkFileName: test.apk\\n")
                (decoded/"AndroidManifest.xml").write_text('<manifest package="com.ferrari.smoke"/>')
                return {"confirmed":True,"artifacts":[str(decoded)],"action":action}
            with patch.object(skill_job.tool_runtime,"invoke",side_effect=decoder):
                result,code=skill_job.execute(data,Path(d)/"job")
            self.assertEqual(code,0,result)
            self.assertEqual(result["status"],"completed")
            with zipfile.ZipFile(Path(d)/"job/response.zip") as archive:
                names=archive.namelist()
                self.assertIn("artifacts/apktool-decoded/AndroidManifest.xml",names)
                self.assertIn("artifacts/apktool-decoded/apktool.yml",names)
                self.assertIn(b"com.ferrari.smoke",archive.read("artifacts/apktool-decoded/AndroidManifest.xml"))

    def test_wrong_job_kind_generates_failure_report(self):
        with tempfile.TemporaryDirectory() as d:
            result,code=skill_job.execute(req("arbitrary"),Path(d)/"job")
            self.assertEqual(code,2)
            self.assertEqual(result["status"],"failed")
            self.assertTrue((Path(d)/"job/response.zip").is_file())
    def test_no_arbitrary_commands(self):
        for data in [
            req(kind="shell",operation="rm -rf /"),
            {**req(operation="svg-poster"),"command":"curl"},
            req("invoke",action="shell",input={"name":"a.txt","content_base64":"YQ=="}),
            req("operation",operation="unknown_tool"),
            req("auto",request="teste",input={"name":"../x.md","content_base64":"YQ=="}),
            req("operation",operation="svg-poster",input={"name":"a.md","content_base64":"nooo!"}),
        ]:
            with self.assertRaises(ValueError):
                skill_job.validate_job(data)
    def test_remote_query_action_validation(self):
        raw=base64.b64encode(b"Ferrari works\n").decode("ascii")
        data=req("invoke",action="ripgrep-find-text",query="Ferrari",
                 input={"name":"ferrari.txt","content_base64":raw})
        self.assertEqual(skill_job.validate_job(data),b"Ferrari works\n")
        with self.assertRaises(ValueError):
            skill_job.validate_job({**data,"query":None})
        with self.assertRaises(ValueError):
            skill_job.validate_job({**data,"query":"-"*300})

    def test_reject_reuse_output(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"job"
            skill_job.execute(req(operation="svg-poster"),path)
            with self.assertRaises(FileExistsError):
                skill_job.execute(req(operation="svg-poster"),path)
    def test_reject_unknown_actions_before_execution(self):
        bad=req("invoke",action="not-an-adapter",input={"name":"x.md","content_base64":"YQ=="})
        with self.assertRaises(ValueError):skill_job.validate_job(bad)
if __name__=="__main__":
    unittest.main()
