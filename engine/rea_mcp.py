"""Run the original REA MCP directly as a Ferrari-private executor.

The Ferrari job dispatcher owns tool selection and packages results.
No new coordinator, GitHub/SSH protocol or standalone REA Skill is created.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import selectors
import signal
import subprocess
import tempfile
import time

ROOT = Path.home() / ".local/share/motor-ferrari"
PROJECT_ROOT = Path("/srv/projects/skill-universal")
MAX_FRAME_BYTES = 64 * 1024 * 1024
METHODS = frozenset(("tools/list", "tools/call"))


def validate_requests(value):
    if not isinstance(value, list) or not value or len(value) > 30:
        raise ValueError("REA MCP requests must be a nonempty list of at most 30 entries")
    for item in value:
        if not isinstance(item, dict) or set(item) - {"method", "params"}:
            raise ValueError("Invalid REA MCP request fields")
        if item.get("method") not in METHODS:
            raise ValueError("REA MCP method must be tools/list or tools/call")
        params = item.get("params", {})
        if not isinstance(params, dict):
            raise ValueError("REA MCP params must be an object")
        if item["method"] == "tools/call":
            if set(params) != {"name", "arguments"}:
                raise ValueError("REA MCP tool call needs name and arguments")
            name = params["name"]
            if not isinstance(name, str) or not re.fullmatch(r"[A-Za-z0-9_.:-]{1,128}", name):
                raise ValueError("Invalid REA MCP tool name")
            if not isinstance(params["arguments"], dict):
                raise ValueError("REA MCP tool arguments must be JSON object")
        elif set(params) - {"cursor"}:
            raise ValueError("Invalid tools/list params")
        elif "cursor" in params and (not isinstance(params["cursor"], str)
                                     or len(params["cursor"]) > 1000):
            raise ValueError("Invalid tools/list pagination cursor")


def _resources(root: Path):
    node = root / "runtimes/node-22.23.4/bin/node"
    jdk = root / "runtimes/jdk-25.0.5_8"
    cli = root / ".runtime/npm/rea/node_modules/.bin/rea"
    ghidra = root / "tools/rea-providers/ghidra-12.1.4"
    jadx = root / "tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar"
    apktool = root / "tools/apktool-3.0.3/bin/apktool"
    modules = root / ".runtime/npm/rea/node_modules"
    # Ubuntu VPS project migration: a single historical Ferrari alias may
    # point to the physical, independent GitHub-repository directory.
    # Never accept arbitrary symlinks or pointers to another REA installation.
    if root.is_symlink():
        canonical = PROJECT_ROOT
        allowed_alias = Path.home() / ".local/share/motor-ferrari"
        if (root != allowed_alias or not canonical.is_dir() or
                canonical.is_symlink() or root.resolve(strict=True) != canonical):
            raise RuntimeError("Ferrari private project alias is not trusted")
    if not root.is_dir() or not modules.is_dir() or modules.is_symlink():
        raise RuntimeError("Ferrari private installation is missing")
    if (not cli.is_file() or not cli.resolve().is_relative_to(modules.resolve())):
        raise RuntimeError("Ferrari original REA CLI not private")
    for p in (node, jdk / "bin/java", ghidra / "support/analyzeHeadless", jadx, apktool):
        if not p.is_file() or p.is_symlink() or not p.resolve().is_relative_to(root.resolve()):
            raise RuntimeError("Ferrari private REA provider missing")
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("REA_", "GHIDRA_")) and key not in
           {"JAVA_HOME", "NODE_PATH", "NPM_CONFIG_PREFIX"}}
    env.update({
        "JAVA_HOME": str(jdk),
        "GHIDRA_JAVA_HOME": str(jdk),
        "GHIDRA_INSTALL_DIR": str(ghidra),
        "REA_JADX_MCP_JAR": str(jadx),
        "REA_APKTOOL_COMMAND": str(apktool),
        "PATH": ":".join((str(node.parent), str(jdk / "bin"), str(apktool.parent),
                          "/usr/local/bin", "/usr/bin", "/bin")),
        "XDG_CONFIG_HOME": str(root / ".runtime/rea-config"),
        "XDG_CACHE_HOME": str(root / ".runtime/rea-cache"),
        "XDG_DATA_HOME": str(root / ".runtime/rea-data"),
    })
    return cli, env


def _bind_input(data, source):
    if isinstance(data, str) and data == "$input":
        if source is None:
            raise ValueError("REA MCP $input requires an uploaded file")
        return str(source)
    if isinstance(data, list):
        return [_bind_input(x, source) for x in data]
    if isinstance(data, dict):
        return {k: _bind_input(v, source) for k, v in data.items()}
    return data


def _exchange(command, env, requests):
    with tempfile.TemporaryFile(mode="w+b") as err:
        p = subprocess.Popen(command, env=env, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=err,
                             start_new_session=True)
        pending = bytearray()
        try:
            with selectors.DefaultSelector() as sel:
                sel.register(p.stdout, selectors.EVENT_READ)

                def send(msg):
                    p.stdin.write(json.dumps(msg, ensure_ascii=True, separators=(",", ":")).encode("ascii") + b"\n")
                    p.stdin.flush()

                def recv(expected, seconds):
                    deadline = time.monotonic() + seconds
                    while time.monotonic() < deadline:
                        while b"\n" in pending:
                            frame, _, rest = pending.partition(b"\n")
                            pending[:] = rest
                            if not frame.strip():
                                continue
                            try:
                                value = json.loads(frame)
                            except (ValueError, UnicodeDecodeError) as exc:
                                raise RuntimeError("REA MCP returned invalid JSON") from exc
                            if isinstance(value, dict) and value.get("id") == expected:
                                return value
                        if p.poll() is not None:
                            raise RuntimeError("Ferrari private REA MCP closed before a response")
                        if sel.select(timeout=min(1.0, max(0.05, deadline - time.monotonic()))):
                            chunk = os.read(p.stdout.fileno(), 65536)
                            if not chunk:
                                raise RuntimeError("REA MCP pipe closed")
                            pending.extend(chunk)
                            if len(pending) > MAX_FRAME_BYTES:
                                raise RuntimeError("REA MCP response exceeds artifact limit")
                    raise RuntimeError("REA MCP request deadline exceeded")

                send({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                      "params": {"protocolVersion": "2025-03-26", "capabilities": {},
                                 "clientInfo": {"name": "motor-ferrari", "version": "1.0"}}})
                hello = recv(1, 90)
                if hello.get("error"):
                    raise RuntimeError("REA MCP initialization error")
                send({"jsonrpc": "2.0", "method": "notifications/initialized"})
                replies = []
                for index, entry in enumerate(requests, start=2):
                    send({"jsonrpc": "2.0", "id": index,
                          "method": entry["method"],
                          "params": entry.get("params", {})})
                    reply = recv(index, 720)
                    if reply.get("error"):
                        code = reply["error"].get("code") if isinstance(reply["error"], dict) else "unknown"
                        raise RuntimeError("REA MCP tool returned JSON-RPC error code " + str(code)[:50])
                    result = reply.get("result")
                    if isinstance(result, dict) and result.get("isError") is True:
                        raise RuntimeError("REA MCP tool reported isError=true")
                    replies.append({"method": entry["method"],
                                    "name": entry.get("params", {}).get("name"),
                                    "response": reply})
                return replies
        finally:
            if p.poll() is None:
                try:
                    os.killpg(p.pid, signal.SIGTERM)
                except ProcessLookupError:
                    pass
                try:
                    p.wait(timeout=4)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid, signal.SIGKILL)
                    p.wait(timeout=4)


def invoke(requests, dest: Path, source: Path | None = None, *, root: Path | None = None):
    validate_requests(requests)
    folder = Path(dest)
    if folder.is_symlink() or (folder.exists() and not folder.is_dir()):
        raise ValueError("Ferrari MCP output must be a normal directory")
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / "rea-mcp-result.json"
    if target.exists() or target.is_symlink():
        raise FileExistsError("REA MCP result already exists")
    home = ROOT if root is None else root
    cli, env = _resources(home)
    for rel in (".runtime/rea-config", ".runtime/rea-cache", ".runtime/rea-data"):
        path = home / rel
        if path.is_symlink():
            raise RuntimeError("Private REA XDG path is a symlink")
        path.mkdir(parents=True, exist_ok=True)
    if source is not None:
        if source.is_symlink() or not source.is_file():
            raise ValueError("REA MCP input is not a normal file")
        source = source.resolve()
    bound = _bind_input(requests, source)
    responses = _exchange([str(cli), "mcp"], env, bound)
    target.write_text(json.dumps({"engine": "motor-ferrari-ubuntu",
                                  "executor": "rea-original-private-mcp",
                                  "responses": responses},
                                 ensure_ascii=False, indent=2), encoding="utf-8")
    if target.stat().st_size == 0:
        raise RuntimeError("REA MCP produced empty result")
    return {"confirmed": True, "artifacts": [str(target)],
            "operation": "rea-mcp", "executor": str(cli)}
