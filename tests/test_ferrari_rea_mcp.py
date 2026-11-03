"""Single Ferrari Skill can call original REA MCP without the legacy REA bridge."""
import base64
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from engine import skill_job, rea_mcp


class FerrariReaMcpTests(unittest.TestCase):
    def _job(self, calls):
        return {"version":1,"id":"ferrari-original-rea-mcp-test","kind":"rea-mcp","mcp_requests":calls}

    def test_complete_live_tool_catalog_is_not_a_fixed_two_action_manifest(self):
        calls=[{"method":"tools/list"}]
        self.assertIsNone(skill_job.validate_job(self._job(calls)))
        self.assertEqual(rea_mcp.METHODS,{"tools/list","tools/call"})
        call=[{"method":"tools/call","params":{"name":"inspect_elf_notes","arguments":{"path":"$input"}}}]
        payload=self._job(call)
        payload["input"]={"name":"sample.elf","content_base64":base64.b64encode(b"\x7fELF").decode()}
        self.assertEqual(skill_job.validate_job(payload),b"\x7fELF")

    def test_reject_unknown_methods_and_invalid_tool_arguments(self):
        bad=(
            [{"method":"initialize"}],
            [{"method":"shell","params":{}}],
            [{"method":"tools/call","params":{"name":"x","arguments":[]}}],
            [{"method":"tools/call","params":{"name":"../../../secret","arguments":{}}}],
            [{"method":"tools/list","params":{"unexpected":1}}],
        )
        for items in bad:
            with self.subTest(items=items), self.assertRaises(ValueError):
                skill_job.validate_job(self._job(items))
        data={"version":1,"id":"ferrari-original-rea-mcp-test","kind":"inventory",
              "mcp_requests":[{"method":"tools/list"}]}
        with self.assertRaisesRegex(ValueError,"require kind=rea-mcp"):
            skill_job.validate_job(data)

    def test_original_mcp_is_invoked_and_zipped_inside_existing_skill(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)/"motor-ferrari"
            root.mkdir()
            calls=[{"method":"tools/list"},{"method":"tools/call",
                   "params":{"name":"inspect_elf_notes","arguments":{"path":"$input"}}}]
            envelope=self._job(calls)
            envelope["input"]={"name":"sample.elf","content_base64":base64.b64encode(b"\x7fELF").decode()}
            def fake_exchange(args,env,requests):
                self.assertEqual(args[1],"mcp")
                self.assertEqual(requests[1]["params"]["arguments"]["path"].rsplit("/",1)[-1],"sample.elf")
                return [
                    {"method":"tools/list","name":None,
                     "response":{"jsonrpc":"2.0","id":2,"result":{"tools":[{"name":"inspect_elf_notes"}]}}},
                    {"method":"tools/call","name":"inspect_elf_notes",
                     "response":{"jsonrpc":"2.0","id":3,"result":{"content":[{"type":"text","text":"PASS"}]}}}]
            with patch.object(rea_mcp,"ROOT",root),                  patch.object(rea_mcp,"_resources",return_value=(root/"rea",{"PATH":"/usr/bin"})),                  patch.object(rea_mcp,"_exchange",side_effect=fake_exchange):
                report,code=skill_job.execute(envelope,Path(tmp)/"job")
            self.assertEqual(code,0)
            self.assertEqual(report["status"],"completed")
            self.assertEqual(report["operation"],"rea-mcp")
            with zipfile.ZipFile(Path(tmp)/"job/response.zip") as z:
                self.assertIn("artifacts/rea-mcp-result.json",z.namelist())
                data=json.loads(z.read("artifacts/rea-mcp-result.json"))
                self.assertEqual(len(data["responses"]),2)
                self.assertEqual(data["executor"],"rea-original-private-mcp")

    def test_missing_private_providers_refuses_legacy_fallback(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch.object(rea_mcp,"ROOT",Path(tmp)/"motor-ferrari"):
                result,code=skill_job.execute(self._job([{"method":"tools/list"}]),Path(tmp)/"job")
            self.assertNotEqual(code,0)
            self.assertEqual(result["status"],"failed")
            self.assertNotIn("rea-final-runtime",str(result))


if __name__=="__main__":
    unittest.main()
