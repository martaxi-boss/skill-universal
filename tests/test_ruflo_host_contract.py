"""One-host Ruflo v3 coordination contract and bounded tool handoff tests."""
import base64
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from engine import ruflo_host, skill_job


def example():
    return {
        "version":1,"id":"ferrari-ruflo-host-qa","kind":"ruflo-host",
        "host":"ChatGPT",
        "roles":[{"id":"coder","type":"coder"},{"id":"reviewer","type":"reviewer"}],
        "max_parallel":2,
        "input":{"name":"demo.json","content_base64":base64.b64encode(b'{"safe":true}\n').decode()},
        "steps":[
            {"id":"format","role":"coder","kind":"invoke","action":"jq-format-json"},
            {"id":"review","role":"reviewer","kind":"rea-mcp","mcp_requests":[
                {"method":"tools/call","params":{"name":"inspect_analysis_settings","arguments":{}}}
            ]},
        ],
    }


class StubMCP:
    def __init__(self,_space):
        self.agent=0
        self.task=0
        self.calls=[]
    def start(self):self.calls.append("initialize")
    def close(self):self.calls.append("close")
    def tool(self,name,_args):
        self.calls.append(name)
        if name=="swarm_init":return {"success":True,"swarmId":"swarm-demo"}
        if name=="agent_spawn":
            self.agent+=1
            return {"success":True,"agentId":"agent-"+str(self.agent)}
        if name=="task_create":
            self.task+=1
            return {"success":True,"taskId":"task-"+str(self.task)}
        return {"success":True,"status":"completed"}


class RufloHostTests(unittest.TestCase):
    def test_one_host_valid(self):
        self.assertTrue(ruflo_host.validate_job(example()))
        raw=skill_job.validate_job(example())
        self.assertEqual(raw,b'{"safe":true}\n')

    def test_roles_are_not_separate_models(self):
        d=example()
        d["roles"][1]["id"]="coder"
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)
        d=example()
        d["roles"][1]["type"]="new-paid-provider"
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)
        d=example()
        d["host"]="2-OpenAI-and-Claude"
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)

    def test_no_arbitrary_commands_or_future_inputs(self):
        d=example()
        d["steps"][0]["action"]="shell"
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)
        d=example()
        d["steps"][0]["input_from"]="review"
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)
        d=example()
        d["steps"][0]["query"]="bad"
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)

    def test_bounds(self):
        d=example();d["max_parallel"]=4
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)
        d=example();d["steps"] *= 5
        with self.assertRaises(ValueError):ruflo_host.validate_job(d)

    def test_real_work_handoff_with_stub_coordination_and_private_outputs(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp);(home/".runtime").mkdir()
            upload=home/"source.json";upload.write_text('{"safe":true}\n')
            def synthetic_tool(_action,_src,dest,_query=None):
                p=Path(dest);p.mkdir()
                out=p/"from-private-tool.txt";out.write_text("Ferrari private jq")
                return {"confirmed":True,"executor":str(home/"tools/jq"),"artifacts":[str(out)]}
            def synthetic_rea(_requests,dest,_source):
                p=Path(dest);p.mkdir()
                out=p/"from-rea.txt";out.write_text("Ferrari REA MCP")
                return {"confirmed":True,"executor":str(home/"rea"),"artifacts":[str(out)]}
            with (patch.object(ruflo_host,"HOME",home),
                  patch.object(ruflo_host,"RufloMCP",StubMCP),
                  patch.object(ruflo_host.tool_runtime,"invoke",side_effect=synthetic_tool),
                  patch.object(ruflo_host.rea_mcp,"invoke",side_effect=synthetic_rea)):
                result=ruflo_host.run(example(),home/"result",upload)
            self.assertTrue(result["confirmed"])
            report=json.loads((home/"result/ruflo-host-report.json").read_text())
            self.assertEqual(report["status"],"completed")
            self.assertEqual(len(report["roles"]),2)
            self.assertEqual(len(report["steps"]),2)
            self.assertEqual(report["independent_agent_model_calls"],0)
            self.assertTrue(report["swarm_shutdown"])
            self.assertTrue(report["cleanup_verified"])


if __name__=="__main__":
    unittest.main()
