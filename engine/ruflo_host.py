"""Ruflo 3.71 host-mediated multiagent coordination for the one Ferrari Skill.

One active host AI (ChatGPT, Codex, Claude or another caller) authors roles and
tool decisions. Ruflo creates swarm, agents and task ledger; Ferrari executes
only its vetted private actions/REA MCP. This does not spawn model-backed LLM
workers, does not use provider keys and does not create a resident daemon.
"""
from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import tempfile
import time

from engine import rea_mcp, tool_runtime

HOME=Path("/srv/projects/skill-universal")
NODE=HOME/"runtimes/node-22.23.4/bin/node"
CLI=HOME/".runtime/npm/ruflo/node_modules/ruflo/bin/ruflo.js"
ROLE_TYPES=frozenset({"coder","reviewer","tester","researcher","architect","debugger","optimizer","documenter"})
IDENTITY=re.compile(r"[a-z][a-z0-9_-]{0,39}\Z")


def validate_job(doc):
    if not isinstance(doc,dict) or doc.get("kind")!="ruflo-host":
        raise ValueError("Expected Ferrari Ruflo host job")
    if set(doc)-{"version","id","kind","input","host","roles","steps","max_parallel"}:
        raise ValueError("Unknown Ruflo job property")
    if doc.get("host") not in {"ChatGPT","Codex","Claude","other"}:
        raise ValueError("One selected host AI is required")
    roles=doc.get("roles")
    steps=doc.get("steps")
    if not isinstance(roles,list) or not 2<=len(roles)<=4 or not isinstance(steps,list) or not 2<=len(steps)<=8:
        raise ValueError("Expected 2-4 roles and 2-8 tasks")
    ids=set()
    for item in roles:
        if not isinstance(item,dict) or set(item)!={"id","type"}:
            raise ValueError("Invalid Ruflo role")
        rid,kind=item["id"],item["type"]
        if not isinstance(rid,str) or not IDENTITY.fullmatch(rid) or rid in ids or kind not in ROLE_TYPES:
            raise ValueError("Unknown or duplicate Ruflo agent role")
        ids.add(rid)
    if type(doc.get("max_parallel",2)) is not int or not 1<=doc.get("max_parallel",2)<=2:
        raise ValueError("Ferrari Ruflo max_parallel must be 1 or 2")
    names=set()
    for item in steps:
        if not isinstance(item,dict) or set(item)-{"id","role","kind","action","query","input_from","mcp_requests"}:
            raise ValueError("Unknown Ruflo task field")
        sid,role,kind=item.get("id"),item.get("role"),item.get("kind")
        if not isinstance(sid,str) or not IDENTITY.fullmatch(sid) or sid in names or role not in ids:
            raise ValueError("Invalid task identity/agent assignment")
        if kind=="invoke":
            if set(item)-{"id","role","kind","action","query","input_from"}:
                raise ValueError("Invalid Ferrari action task")
            spec=tool_runtime.specs().get(item.get("action"))
            if not spec:
                raise ValueError("Unregistered private action")
            need="{query}" in spec["args"]
            query=item.get("query")
            if need != (isinstance(query,str) and 1<=len(query.strip())<=200):
                raise ValueError("Invalid required query for tool action")
            if not need and query is not None:
                raise ValueError("Unexpected tool query")
            source=item.get("input_from","$input")
            if source=="$input" and not isinstance(doc.get("input"),dict):
                raise ValueError("Tool step requires uploaded input")
            if source!="$input" and source not in names:
                raise ValueError("Use an earlier task output only")
        elif kind=="rea-mcp":
            if set(item)-{"id","role","kind","mcp_requests"}:
                raise ValueError("Unexpected REA task parameters")
            rea_mcp.validate_requests(item.get("mcp_requests"))
        else:
            raise ValueError("Unsupported Ruflo worker kind")
        names.add(sid)
    return True


class RufloMCP:
    """Ephemeral stdio MCP client with bounded frames and process cleanup."""

    def __init__(self,workspace):
        root=HOME.resolve(strict=True)
        for p in (NODE,CLI):
            if not p.is_file() or not p.resolve(strict=True).is_relative_to(root):
                raise RuntimeError("Ferrari private Ruflo or Node unavailable")
        if not Path(workspace).resolve(strict=True).is_relative_to((HOME/".runtime").resolve(strict=True)):
            raise ValueError("Ruflo home escaped Ferrari")
        env={"PATH":str(NODE.parent)+":/usr/bin:/bin","HOME":str(workspace),"TMPDIR":str(workspace),
             "XDG_CACHE_HOME":str(workspace),"XDG_CONFIG_HOME":str(workspace),
             "XDG_DATA_HOME":str(workspace),"CI":"true","LANG":"C",
             "NODE_OPTIONS":"--max-old-space-size=512","CLAUDE_FLOW_NO_COW_MEMORY":"1"}
        self.proc=subprocess.Popen([str(NODE),str(CLI),"mcp","start"],
             cwd=str(workspace),env=env,stdin=subprocess.PIPE,
             stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,bufsize=0,start_new_session=True)
        self.selector=selectors.DefaultSelector()
        self.selector.register(self.proc.stdout,selectors.EVENT_READ)
        self.buf=bytearray()
        self.sequence=0

    def request(self,method,params=None,deadline_seconds=18):
        self.sequence+=1
        xid=self.sequence
        msg={"jsonrpc":"2.0","id":xid,"method":method}
        if params is not None: msg["params"]=params
        self.proc.stdin.write((json.dumps(msg,separators=(",",":"))+"\n").encode())
        self.proc.stdin.flush()
        deadline=time.monotonic()+deadline_seconds
        while time.monotonic()<deadline:
            while b"\n" in self.buf:
                line,_,rest=self.buf.partition(b"\n")
                self.buf=bytearray(rest)
                try: obj=json.loads(line)
                except (ValueError,UnicodeDecodeError):continue
                if obj.get("id")==xid:return obj
            if self.proc.poll() is not None:raise RuntimeError("Ruflo MCP terminated")
            for _,_ in self.selector.select(timeout=min(0.6,max(0.01,deadline-time.monotonic()))):
                data=os.read(self.proc.stdout.fileno(),65536)
                if not data:raise RuntimeError("Ruflo MCP output closed")
                self.buf.extend(data)
                if len(self.buf)>1048576:raise RuntimeError("Ruflo MCP oversized frame")
        raise TimeoutError("Ruflo MCP response deadline")

    def notify(self,method):
        self.proc.stdin.write((json.dumps({"jsonrpc":"2.0","method":method})+"\n").encode())
        self.proc.stdin.flush()

    def tool(self,name,args):
        if name not in {"swarm_init","agent_spawn","task_create","task_complete",
                        "swarm_shutdown","agent_list","task_list"}:
            raise ValueError("Ruflo tool not authorized")
        resp=self.request("tools/call",{"name":name,"arguments":args},deadline_seconds=25)
        if "error" in resp:raise RuntimeError("Ruflo "+name+" MCP error")
        obj=resp.get("result",{})
        if not isinstance(obj,dict) or obj.get("isError"):
            raise RuntimeError("Ruflo "+name+" rejected task")
        val=obj.get("structuredContent")
        if val is None:
            for item in obj.get("content",[]):
                if isinstance(item,dict) and item.get("type")=="text":
                    try:val=json.loads(item.get("text",""))
                    except (ValueError,TypeError):val={"text":str(item.get("text",""))[:400]}
                    break
        if val is None:val={}
        if isinstance(val,dict) and val.get("success") is False:
            raise RuntimeError("Ruflo "+name+" returned unsuccessful state")
        return val

    def start(self):
        x=self.request("initialize",{"protocolVersion":"2025-03-26",
               "capabilities":{},"clientInfo":{"name":"Ferrari single host","version":"1.0"}},24)
        if "result" not in x:raise RuntimeError("Ruflo MCP handshake failed")
        self.notify("notifications/initialized")

    def close(self):
        self.selector.close()
        if self.proc.poll() is None:
            try:os.killpg(self.proc.pid,signal.SIGTERM)
            except ProcessLookupError:pass
            try:self.proc.wait(timeout=3)
            except subprocess.TimeoutExpired:
                os.killpg(self.proc.pid,signal.SIGKILL)
                self.proc.wait(timeout=3)


def lookup(obj,keys):
    if isinstance(obj,dict):
        for k in keys:
            if isinstance(obj.get(k),str) and obj[k]:return obj[k]
        for v in obj.values():
            found=lookup(v,keys)
            if found:return found
    if isinstance(obj,list):
        for v in obj:
            found=lookup(v,keys)
            if found:return found
    return None


def run(doc,folder,uploaded=None):
    """Run an explicit single-host authored role plan, with Ruflo accounting."""
    validate_job(doc)
    dest=Path(folder)
    if dest.is_symlink() or dest.exists():
        raise FileExistsError("Ruflo work output must be new")
    if not dest.resolve().is_relative_to(HOME.resolve(strict=True)):
        raise ValueError("Ruflo job cannot leave the project")
    dest.mkdir(parents=True,mode=0o700)
    report={"kind":"ruflo-host","host":doc["host"],
            "execution_mode":"one_host_ai_prepared_role_decisions",
            "independent_agent_model_calls":0,"ruflo_version":"3.71.0",
            "roles":[],"steps":[],"status":"failed","cleanup_verified":False}
    state=HOME/".runtime"
    if state.is_symlink() or not state.is_dir():
        raise RuntimeError("Ferrari local runtime unavailable")
    with tempfile.TemporaryDirectory(dir=state,prefix="ruflo-host-job-") as tmp:
        client=RufloMCP(tmp)
        swarm_id=None
        try:
            client.start()
            swarm=client.tool("swarm_init",{"topology":"hierarchical",
                   "maxAgents":len(doc["roles"]),"strategy":"specialized"})
            swarm_id=lookup(swarm,("swarmId","swarm_id"))
            if not swarm_id:raise RuntimeError("Ruflo swarm ID missing")
            report["swarm_created"]=True
            agentids={}
            for role in doc["roles"]:
                item=client.tool("agent_spawn",{"agentType":role["type"],
                         "name":"ferrari-"+role["id"],
                         "model":"inherit","swarmId":swarm_id})
                aid=lookup(item,("agentId","agent_id"))
                if not aid:raise RuntimeError("Ruflo did not register agent")
                agentids[role["id"]]=aid
                report["roles"].append({"id":role["id"],"type":role["type"],
                                        "agent_id":aid,"model":"shared_host"})
            taskids={}
            for step in doc["steps"]:
                item=client.tool("task_create",{"type":"research",
                    "description":"Ferrari private "+step["kind"]+" task "+step["id"],
                    "priority":"normal","assignTo":[agentids[step["role"]]]})
                tid=lookup(item,("taskId","task_id"))
                if not tid:raise RuntimeError("Ruflo did not register task")
                taskids[step["id"]]=tid
            def execute(step):
                source=uploaded
                if step.get("input_from") not in (None,"$input"):
                    previous=results[step["input_from"]]["artifacts"][0]
                    source=previous
                out=dest/step["id"]
                if step["kind"]=="invoke":
                    return tool_runtime.invoke(step["action"],str(source),str(out),step.get("query"))
                return rea_mcp.invoke(step["mcp_requests"],out,None)
            results={}
            waiting=list(doc["steps"])
            with ThreadPoolExecutor(max_workers=doc.get("max_parallel",2)) as pool:
                while waiting:
                    runnable=[s for s in waiting if s.get("input_from") in (None,"$input",*results)]
                    if not runnable:raise RuntimeError("Ruflo task dependency cycle")
                    batch=runnable[:doc.get("max_parallel",2)]
                    futures={pool.submit(execute,s):s for s in batch}
                    for future in as_completed(futures):
                        step=futures[future]
                        item=future.result()
                        if not item.get("confirmed") or not item.get("artifacts"):
                            raise RuntimeError("Ferrari role task did not produce artifacts")
                        for path in item["artifacts"]:
                            p=Path(path)
                            if not p.resolve(strict=True).is_relative_to(dest.resolve()):
                                raise RuntimeError("Ruflo task artifact escapes private job")
                        results[step["id"]]=item
                        record={"id":step["id"],"role":step["role"],"kind":step["kind"],
                                "task_id":taskids[step["id"]],"artifacts":len(item["artifacts"]),
                                "executor":str(item.get("executor",""))}
                        client.tool("task_complete",{"taskId":taskids[step["id"]],
                           "result":{"verified":True,"host":doc["host"],
                                     "executor":record["executor"]}})
                        report["steps"].append(record)
                    waiting=[s for s in waiting if s not in batch]
            artifacts=[p for result in results.values() for p in result["artifacts"]]
            report["status"]="completed"
        finally:
            if swarm_id:
                try:
                    client.tool("swarm_shutdown",{"swarmId":swarm_id,"graceful":True})
                    report["swarm_shutdown"]=True
                except Exception:report["swarm_shutdown"]=False
            client.close()
    report["cleanup_verified"]=not Path(tmp).exists()
    if report["status"]!="completed" or not report.get("swarm_shutdown") or not report["cleanup_verified"]:
        raise RuntimeError("Ferrari Ruflo team did not finish and clean up")
    result=dest/"ruflo-host-report.json"
    result.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"confirmed":True,"artifacts":[str(result),*artifacts],
            "executor":str(CLI),"operation":"ruflo-host"}
