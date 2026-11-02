"""Real Git commit request transport selection tests."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from engine.skill_request_pick import pick

def git(path,*args):
    return subprocess.run(["git","-C",str(path),*args],check=True,capture_output=True,text=True).stdout.strip()

class RequestPickTests(unittest.TestCase):
    def setup_git(self,path):
        git(path,"init","-q")
        git(path,"config","user.email","ferrari@invalid.example")
        git(path,"config","user.name","Ferrari Test")
        (path/"README.md").write_text("base")
        git(path,"add",".")
        git(path,"commit","-qm","base")
        return git(path,"rev-parse","HEAD")
    def test_one_new_request_selected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            before=self.setup_git(root)
            directory=root/"ferrari-requests";directory.mkdir()
            payload={"version":1,"id":"skill-transport-test","kind":"operation","operation":"svg-poster","title":"Ferrari"}
            source=directory/"job-test1234.json"
            source.write_text(json.dumps(payload))
            git(root,"add",".");git(root,"commit","-qm","request")
            after=git(root,"rev-parse","HEAD")
            dest=root/"output/job.json"
            pick(root,before,after,dest)
            self.assertEqual(json.loads(dest.read_text())["operation"],"svg-poster")
    def test_two_requests_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);before=self.setup_git(root)
            directory=root/"ferrari-requests";directory.mkdir()
            for name in ("job-abcdefgh.json","job-ijklmnop.json"):
                (directory/name).write_text(json.dumps({"version":1,"id":"sample","kind":"inventory"}))
            git(root,"add",".");git(root,"commit","-qm","too-many")
            after=git(root,"rev-parse","HEAD")
            with self.assertRaises(ValueError):
                pick(root,before,after,root/"output.json")
    def test_reject_invalid_git_shas(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                pick(d,"not-a-sha","0"*40,Path(d)/"output")
if __name__=="__main__":
    unittest.main()
