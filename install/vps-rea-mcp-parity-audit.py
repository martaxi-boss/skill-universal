#!/usr/bin/env python3
"""Read-only tool-catalog parity of independent original-REA MCP installations.

Starts one short-lived MCP stdio client against each installation. It never
runs tools/call, edits an installation, or exposes target contents.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import selectors
import signal
import subprocess
import tempfile
import time

FERRARI = Path.home() / ".local/share/motor-ferrari"
LEGACY = Path.home() / "rea-final-runtime/bin/rea-mcp"
CLI = FERRARI / ".runtime/npm/rea/node_modules/.bin/rea"
MAX_MESSAGE = 32 * 1024 * 1024


def _error_kind(value) -> str:
    if isinstance(value, dict):
        code = value.get("code")
        return "jsonrpc_" + str(code)[:20]
    if isinstance(value, str):
        for word in ("timeout", "missing", "invalid", "permission", "unknown", "closed"):
            if word in value.lower():
                return word
        return "string_error"
    return "unknown_error"


def _catalog(executable: list[str], ferrari: bool) -> dict:
    if not Path(executable[0]).is_file():
        return {"status": "missing_executable"}
    with tempfile.TemporaryDirectory(prefix="ferrari-mcp-parity-") as home:
        env = dict(os.environ)
        env.update({
            "HOME": home, "TMPDIR": home,
            "XDG_CONFIG_HOME": home + "/.config",
            "XDG_CACHE_HOME": home + "/.cache",
            "XDG_DATA_HOME": home + "/.data",
        })
        if ferrari:
            node = FERRARI / "runtimes/node-22.23.4/bin"
            jdk = FERRARI / "runtimes/jdk-25.0.5_8"
            ghidra = FERRARI / "tools/rea-providers/ghidra-12.1.4"
            jar = FERRARI / "tools/rea-providers/jadx-headless-mcp-0.7.1-all.jar"
            apk = FERRARI / "tools/apktool-3.0.3/bin/apktool"
            for key, target in (("GHIDRA_INSTALL_DIR", ghidra),
                                ("REA_JADX_MCP_JAR", jar),
                                ("REA_APKTOOL_COMMAND", apk)):
                if not target.exists():
                    return {"status": "private_provider_missing", "component": key}
                env[key] = str(target)
            env["JAVA_HOME"] = str(jdk)
            env["GHIDRA_JAVA_HOME"] = str(jdk)
            env["PATH"] = str(node) + ":" + str(jdk / "bin") + ":" + env.get("PATH", "")
        with tempfile.TemporaryFile(mode="w+b") as stderr:
            p = subprocess.Popen(executable, env=env, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=stderr,
                                 start_new_session=True)
            pending = bytearray()
            try:
                with selectors.DefaultSelector() as sel:
                    sel.register(p.stdout, selectors.EVENT_READ)

                    def send(frame):
                        p.stdin.write(json.dumps(frame, separators=(",", ":")).encode() + b"\n")
                        p.stdin.flush()

                    def recv(wanted, timeout):
                        limit = time.monotonic() + timeout
                        while time.monotonic() < limit:
                            while b"\n" in pending:
                                line, _, remain = pending.partition(b"\n")
                                pending[:] = remain
                                if not line.strip():
                                    continue
                                try:
                                    msg = json.loads(line)
                                except (UnicodeDecodeError, ValueError):
                                    return {"error": "malformed_json"}
                                if isinstance(msg, dict) and msg.get("id") == wanted:
                                    return msg
                            if p.poll() is not None:
                                return {"error": "server_exited"}
                            if sel.select(timeout=min(1, max(0.05, limit - time.monotonic()))):
                                block = os.read(p.stdout.fileno(), 65536)
                                if not block:
                                    return {"error": "pipe_closed"}
                                pending.extend(block)
                                if len(pending) > MAX_MESSAGE:
                                    return {"error": "message_too_large"}
                        return {"error": "timeout"}

                    send({
                        "jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {
                            "protocolVersion": "2025-03-26",
                            "capabilities": {},
                            "clientInfo": {"name": "ferrari-rea-parity", "version": "1.0"},
                        },
                    })
                    initial = recv(1, 90)
                    if initial.get("error"):
                        return {"status": "initialize_error",
                                "reason": _error_kind(initial["error"])}
                    send({"jsonrpc": "2.0", "method": "notifications/initialized"})
                    names = set()
                    cursor = None
                    for index in range(12):
                        params = {"cursor": cursor} if cursor else {}
                        req = {"jsonrpc": "2.0", "id": index + 2, "method": "tools/list"}
                        if params:
                            req["params"] = params
                        send(req)
                        answer = recv(index + 2, 90)
                        if answer.get("error"):
                            return {"status": "tools_list_error", "reason": _error_kind(answer["error"])}
                        result = answer.get("result")
                        if not isinstance(result, dict) or not isinstance(result.get("tools"), list):
                            return {"status": "invalid_tool_list"}
                        for item in result["tools"]:
                            if isinstance(item, dict) and isinstance(item.get("name"), str):
                                names.add(item["name"])
                        cursor = result.get("nextCursor")
                        if not cursor:
                            return {"status": "ready", "count": len(names), "names": names}
                    return {"status": "pagination_limit"}
            except (OSError, BrokenPipeError, ValueError, TypeError):
                return {"status": "client_error"}
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


def main():
    old = _catalog([str(LEGACY)], ferrari=False)
    new = _catalog([str(CLI), "mcp"], ferrari=True)
    result = {
        "scope": "read_only_legacy_vs_ferrari_original_rea_mcp",
        "legacy_status": old["status"],
        "ferrari_status": new["status"],
        "legacy_tool_count": old.get("count"),
        "ferrari_tool_count": new.get("count"),
        "legacy_error": old.get("reason"),
        "ferrari_error": new.get("reason"),
    }
    if old["status"] == "ready" and new["status"] == "ready":
        missing = sorted(old["names"] - new["names"])
        extra = sorted(new["names"] - old["names"])
        result.update({
            "exact_name_parity": not missing and not extra,
            "missing_count": len(missing),
            "extra_count": len(extra),
            "missing_examples": missing[:20],
            "extra_examples": extra[:20],
        })
        result["status"] = "PARITY_PASS" if not missing and not extra else "PARITY_FAIL"
    else:
        result["status"] = "PARITY_NOT_PROVEN"
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))


if __name__ == "__main__":
    main()
