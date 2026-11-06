#!/usr/bin/env python3
"""A bounded, synthetic, host-led Ruflo MCP + Ferrari/REA integration smoke.

The *one host AI* authors the two task decisions. Ruflo registers/assigns the
roles; the Ferrari host executor runs vetted private tools. No per-role LLM,
no network provider, no global install, and no resident Ruflo coordinator.
This does NOT certify autonomous Ruflo agent_execute with an LLM.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import sys
import tempfile
import time
import resource

ROOT = Path("/srv/projects/skill-universal")
CLI = ROOT / ".runtime/npm/ruflo/node_modules/ruflo/bin/ruflo.js"
NODE = ROOT / "runtimes/node-22.23.4/bin/node"
SOURCE = ROOT / "current"
MAX_FRAME = 1024 * 1024
SELECTED_TOOLS = {"swarm_init", "swarm_status", "swarm_shutdown", "agent_spawn",
                  "agent_list", "agent_status", "agent_terminate",
                  "task_create", "task_assign", "task_complete", "task_list"}


class MCP:
    def __init__(self, sandbox: Path):
        env = {
            "PATH": f"{NODE.parent}:/usr/bin:/bin",
            "HOME": str(sandbox),
            "TMPDIR": str(sandbox),
            "XDG_CACHE_HOME": str(sandbox),
            "XDG_CONFIG_HOME": str(sandbox),
            "XDG_DATA_HOME": str(sandbox),
            "CI": "true",
            "LANG": "C",
            "NODE_OPTIONS": "--max-old-space-size=512",
            "CLAUDE_FLOW_NO_COW_MEMORY": "1",
        }
        self.process = subprocess.Popen(
            [str(NODE), str(CLI), "mcp", "start"],
            cwd=str(sandbox), env=env,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, start_new_session=True, bufsize=0,
        )
        self.sel = selectors.DefaultSelector()
        self.sel.register(self.process.stdout, selectors.EVENT_READ)
        self.buffer = bytearray()
        self.counter = 0

    def request(self, method: str, params: dict | None = None, timeout: float = 18):
        self.counter += 1
        rid = self.counter
        obj = {"jsonrpc": "2.0", "id": rid, "method": method}
        if params is not None:
            obj["params"] = params
        self.process.stdin.write((json.dumps(obj, separators=(",", ":")) + "\n").encode())
        self.process.stdin.flush()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            while b"\n" in self.buffer:
                line, _, rest = self.buffer.partition(b"\n")
                self.buffer = bytearray(rest)
                try:
                    data = json.loads(line)
                except (ValueError, UnicodeDecodeError):
                    continue
                if data.get("id") == rid:
                    return data
            if self.process.poll() is not None:
                return {"error": {"message": "ruflo_process_exited"}}
            for _, _ in self.sel.select(timeout=min(0.8, max(0.01, deadline - time.monotonic()))):
                data = os.read(self.process.stdout.fileno(), 65536)
                if not data:
                    return {"error": {"message": "ruflo_mcp_closed"}}
                self.buffer.extend(data)
                if len(self.buffer) > MAX_FRAME:
                    return {"error": {"message": "ruflo_mcp_oversize"}}
        return {"error": {"message": "ruflo_mcp_timeout"}}

    def notify(self, method: str):
        self.process.stdin.write((json.dumps({"jsonrpc":"2.0", "method":method})+"\n").encode())
        self.process.stdin.flush()

    def tool(self, name: str, args: dict, timeout=15):
        if name not in SELECTED_TOOLS:
            raise ValueError("Unexpected tool")
        response = self.request("tools/call", {"name":name,"arguments":args},timeout=timeout)
        result = response.get("result",{})
        contents = result.get("content",[]) if isinstance(result,dict) else []
        parsed = result.get("structuredContent") if isinstance(result,dict) else None
        if parsed is None:
            for item in contents:
                if item.get("type") == "text":
                    try:
                        parsed=json.loads(item.get("text",""))
                        break
                    except ValueError:
                        parsed=item.get("text","")[:1000]
                        break
        return {"ok": not response.get("error") and not result.get("isError",False),
                "parsed": parsed, "error": response.get("error")}

    def close(self):
        try: self.sel.close()
        except OSError: pass
        p=self.process
        if p.poll() is None:
            try: os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError: pass
            try: p.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL)
                p.wait(timeout=3)


def find_id(x, keys):
    """Extract IDs from Ruflo's version-specific structured/text wrappers."""
    if isinstance(x,dict):
        for k in keys:
            if isinstance(x.get(k),str) and x[k]:
                return x[k]
        for y in x.values():
            z=find_id(y,keys)
            if z:
                return z
    elif isinstance(x,list):
        for y in x:
            z=find_id(y,keys)
            if z:
                return z
    elif isinstance(x,str) and x.startswith("{"):
        try:
            return find_id(json.loads(x),keys)
        except ValueError: pass
    return None


def concise(obj):
    if isinstance(obj,dict):
        v={k:val for k,val in obj.items() if k in ("success","status","swarmId","agentId","taskId","id","agentType","name","error","message","assignedTo")}
        if v:
            return v
    return str(obj)[:400]


def main():
    assert ROOT.is_dir() and not ROOT.is_symlink() and SOURCE.is_symlink()
    assert SOURCE.resolve().is_relative_to((ROOT/"releases").resolve())
    for p in (NODE,CLI):
        assert p.is_file() and p.resolve().is_relative_to(ROOT.resolve())
    out={"scope":"ruflo_v3.71_single_host_role_coordination_synthetic",
         "active_release":SOURCE.resolve().name,
         "host_intelligence":"ChatGPT produces all agent-role instructions",
         "agent_models_launched":0,
         "autonomous_agent_execution_certified":False,
         "ruflo_mcp":{},"host_tool_executions":{},"status":"incomplete"}
    with tempfile.TemporaryDirectory(prefix="ruflo-host-certificate-",dir=ROOT/".runtime") as temp:
        space=Path(temp)
        m=MCP(space)
        try:
            init=m.request("initialize",{
                "protocolVersion":"2025-03-26","capabilities":{},
                "clientInfo":{"name":"ferrari-single-host-proof","version":"1.0"}},timeout=24)
            out["ruflo_mcp"]["initialized"]="result" in init
            if "result" not in init:
                out["ruflo_mcp"]["failure"]=str(init.get("error"))[:200]
                print(json.dumps(out,ensure_ascii=False))
                return 2
            m.notify("notifications/initialized")
            catalog=m.request("tools/list",timeout=20)
            names={x.get("name") for x in catalog.get("result",{}).get("tools",[])}
            out["ruflo_mcp"]["available_coordination_tools"]=sorted(names & SELECTED_TOOLS)
            if not {"swarm_init","agent_spawn","task_create"}.issubset(names):
                print(json.dumps(out,ensure_ascii=False))
                return 3
            swarm=m.tool("swarm_init",{"topology":"hierarchical","maxAgents":2,"strategy":"specialized"})
            out["ruflo_mcp"]["swarm_init"]=concise(swarm["parsed"])
            if not swarm["ok"]:
                out["ruflo_mcp"]["failure"]="swarm_init_error"
                print(json.dumps(out,ensure_ascii=False));return 4
            swarm_id=find_id(swarm["parsed"],("swarmId","swarm_id","id"))
            out["ruflo_mcp"]["swarm_id_present"]=bool(swarm_id)
            if "swarm_status" in names:
                status=m.tool("swarm_status",{"swarmId":swarm_id} if swarm_id else {})
                out["ruflo_mcp"]["swarm_status"]=concise(status["parsed"])
            agent_ids={}
            for role in ("coder","reviewer"):
                args={"agentType":role,"name":"ferrari-"+role,"model":"inherit"}
                if swarm_id: args["swarmId"]=swarm_id
                spawned=m.tool("agent_spawn",args,timeout=25)
                out["ruflo_mcp"]["agent_"+role]=concise(spawned["parsed"])
                if spawned["ok"]:
                    agent_id=find_id(spawned["parsed"],("agentId","agent_id","id"))
                    if agent_id: agent_ids[role]=agent_id
            out["ruflo_mcp"]["agent_roles_registered"]=sorted(agent_ids)
            assigned={}
            for role,description in (
                 ("coder","Format a synthetic JSON fixture with Ferrari private jq"),
                 ("reviewer","Review REA private settings using a read-only original MCP call")):
                # With one shared host AI, these role tasks have distinct context,
                # but do NOT pretend that Ruflo called a language model.
                args={"type":"research","description":description,"priority":"normal"}
                if role in agent_ids: args["assignTo"]=[agent_ids[role]]
                created=m.tool("task_create",args)
                out["ruflo_mcp"]["task_"+role]=concise(created["parsed"])
                if created["ok"]:
                    tid=find_id(created["parsed"],("taskId","task_id","id"))
                    if tid:assigned[role]=tid
            out["ruflo_mcp"]["task_roles_registered"]=sorted(assigned)
            # Perform the real work using Ferrari-owned executors under the
            # same single ChatGPT-authored plan; Ruflo handles task allocation.
            sys.path.insert(0,str(SOURCE))
            from engine import tool_runtime, rea_mcp
            inp=space/"synthetic.json"
            inp.write_text('{"single_host":"ChatGPT","roles":["coder","reviewer"]}\n',encoding="utf-8")
            dest=space/"tools-output"
            dest.mkdir()
            jq=tool_runtime.invoke("jq-format-json",str(inp),str(dest/"coder"))
            out["host_tool_executions"]["coder_private_jq"]={
                "confirmed":jq.get("confirmed",False),
                "executor":str(jq.get("executor",""))[:160],
                "private":str(jq.get("executor","")).startswith(str(ROOT)),
                "artifacts":len(jq.get("artifacts",[]))}
            rea=rea_mcp.invoke([
                {"method":"tools/call","params":{"name":"inspect_analysis_settings","arguments":{}}}
            ],dest/"reviewer",None)
            out["host_tool_executions"]["reviewer_private_rea"]={
                "confirmed":rea.get("confirmed",False),
                "executor":str(rea.get("executor",""))[:160],
                "private":str(rea.get("executor","")).startswith(str(ROOT)),
                "artifacts":len(rea.get("artifacts",[]))}
            for role in ("coder","reviewer"):
                if role in assigned and "task_complete" in names:
                    completed=m.tool("task_complete",{"taskId":assigned[role],
                       "result":{"verified":True,"executor":"Ferrari private "+("jq" if role=="coder" else "REA MCP"),"host":"single shared ChatGPT"}})
                    out["ruflo_mcp"]["completed_"+role]=concise(completed["parsed"])
            if "task_list" in names:
                listed=m.tool("task_list",{"limit":8})
                out["ruflo_mcp"]["task_list_ok"]=listed["ok"]
            if "agent_list" in names:
                listed=m.tool("agent_list",{})
                out["ruflo_mcp"]["agent_list_ok"]=listed["ok"]
            if "swarm_shutdown" in names:
                stopped=m.tool("swarm_shutdown",{"swarmId":swarm_id,"graceful":True} if swarm_id else {"graceful":True})
                out["ruflo_mcp"]["swarm_shutdown_ok"]=stopped["ok"]
            # Real model-backed agent_execute is intentionally not attempted:
            # there is no ChatGPT/Claude model API delegated to this process.
            out["status"]="host_mediated_work_verified" if all(
                x["confirmed"] and x["private"] for x in out["host_tool_executions"].values()
            ) and len(agent_ids)==2 and len(assigned)==2 else "partial"
        finally:
            m.close()
    # The test's temporary home and every synthetic tool output are removed.
    out["disposable_test_state_removed"]=not Path(temp).exists()
    print(json.dumps(out,ensure_ascii=False,sort_keys=True))
    return 0 if out["status"]=="host_mediated_work_verified" else 5

if __name__=="__main__":
    try: raise SystemExit(main())
    except Exception as exc:
        print(json.dumps({"status":"failed","error_type":type(exc).__name__,"error":str(exc)[:300]}))
        raise SystemExit(7)
