"""Ferrari-owned Valkey: ephemeral Unix-socket SET/GET/DEL proof.

No TCP listener, no persistent service, no user-supplied commands and no
global dependency. This proves only the bounded local key-value workflow.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import time

HOME = Path("/srv/projects/skill-universal")
EXECUTABLE = HOME / "tools/ferrari-services/valkey-server/bin/valkey-server"
VALUE = b"ferrari-ephemeral-kv-proof-v1"
KEY = b"ferrari:private:smoke:20261108"


def available() -> bool:
    try:
        root = HOME.resolve(strict=True)
        return bool(EXECUTABLE.is_file() and os.access(EXECUTABLE, os.X_OK)
                    and EXECUTABLE.resolve(strict=True).is_relative_to(root))
    except (OSError, RuntimeError):
        return False


def _command(sock: socket.socket, *parts: bytes):
    request = b"*" + str(len(parts)).encode() + b"\r\n"
    for part in parts:
        request += b"$" + str(len(part)).encode() + b"\r\n" + part + b"\r\n"
    sock.sendall(request)
    with sock.makefile("rb", buffering=0) as stream:
        line = stream.readline(2048)
        if not line.endswith(b"\r\n"):
            raise RuntimeError("Valkey did not send complete RESP frame")
        code, body = line[:1], line[1:-2]
        if code == b"+":
            return body
        if code == b":" and body.isdigit():
            return int(body)
        if code == b"$":
            size = int(body)
            if size == -1:
                return None
            if size < 0 or size > 2048:
                raise RuntimeError("Valkey bulk reply size exceeded")
            data = stream.read(size + 2)
            if len(data) != size + 2 or data[-2:] != b"\r\n":
                raise RuntimeError("Valkey bulk payload invalid")
            return data[:-2]
        raise RuntimeError("Unexpected Valkey RESP status")


def prove(folder: Path):
    if not available():
        raise RuntimeError("Ferrari private Valkey executable is not available")
    root = HOME.resolve(strict=True)
    folder = Path(folder)
    if folder.is_symlink() or not folder.resolve().is_relative_to(root):
        raise ValueError("Ferrari Valkey output must stay inside its project")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    report = folder / "valkey-kv-report.json"
    if report.exists() or report.is_symlink():
        raise FileExistsError("Ferrari refuses to replace Valkey evidence")
    runtime = HOME / ".runtime"
    if not runtime.is_dir() or runtime.is_symlink():
        raise RuntimeError("Ferrari private runtime directory unavailable")
    with tempfile.TemporaryDirectory(prefix=".valkey-probe-",dir=runtime) as name:
        work = Path(name)
        sockname = work / "kv.sock"
        log = work / "valkey.log"
        env = {k:v for k,v in os.environ.items()
               if k not in {"LD_PRELOAD","LD_LIBRARY_PATH","REDISCLI_AUTH"}}
        env.update({
            "HOME":str(work), "TMPDIR":str(work), "XDG_CACHE_HOME":str(work),
            "HTTP_PROXY":"http://127.0.0.1:9","HTTPS_PROXY":"http://127.0.0.1:9",
            "ALL_PROXY":"socks5://127.0.0.1:9","NO_PROXY":"",
        })
        with log.open("xb") as output:
            process = subprocess.Popen(
                [str(EXECUTABLE), "--port", "0", "--tls-port", "0",
                 "--unixsocket", str(sockname), "--unixsocketperm", "700",
                 "--daemonize", "no", "--save", "", "--appendonly", "no",
                 "--dir", str(work), "--maxmemory", "64mb",
                 "--protected-mode", "yes"],
                cwd=str(work), env=env, shell=False,
                stdin=subprocess.DEVNULL, stdout=output, stderr=subprocess.STDOUT,
                start_new_session=True)
        success = False
        try:
            end = time.monotonic() + 12
            conn = None
            while time.monotonic() < end:
                if process.poll() is not None:
                    raise RuntimeError("Ferrari Valkey exited early before ready")
                try:
                    conn = socket.socket(socket.AF_UNIX,socket.SOCK_STREAM)
                    conn.settimeout(2.0)
                    conn.connect(str(sockname))
                    break
                except (OSError,socket.timeout):
                    if conn:
                        conn.close()
                    time.sleep(0.15)
            else:
                raise RuntimeError("Ferrari Valkey private Unix socket did not start")
            try:
                if _command(conn,b"PING") != b"PONG":
                    raise RuntimeError("Valkey did not return PONG")
                if _command(conn,b"SET",KEY,VALUE)!=b"OK":
                    raise RuntimeError("Valkey private SET was rejected")
                if _command(conn,b"GET",KEY)!=VALUE:
                    raise RuntimeError("Valkey private GET did not preserve bytes")
                if _command(conn,b"DEL",KEY)!=1:
                    raise RuntimeError("Valkey private DEL did not erase the key")
                if _command(conn,b"GET",KEY) is not None:
                    raise RuntimeError("Valkey retained key after DEL")
                success=True
            finally:
                conn.close()
        finally:
            if process.poll() is None:
                try: os.killpg(process.pid,signal.SIGTERM)
                except ProcessLookupError: pass
            try:
                process.wait(timeout=8)
            except subprocess.TimeoutExpired:
                try: os.killpg(process.pid,signal.SIGKILL)
                except ProcessLookupError: pass
                process.wait(timeout=5)
            if process.poll() is None:
                raise RuntimeError("Ferrari ephemeral Valkey process survived cleanup")
        if not success:
            raise RuntimeError("Ferrari Valkey did not complete read/write/delete proof")
    record = {
        "status":"completed","program":"valkey",
        "operation":"private_unix_socket_set_get_del",
        "ping":"PONG", "set":True,"get_verified":True,
        "del_verified":True,"get_after_del":None,
        "input_fixture_sha256":hashlib.sha256(VALUE).hexdigest(),
        "tcp_listener":False,"persistent_daemon":False,
        "temporary_data_deleted":True,
        "production_cache_performance_certified":False,
        "external_network_certified":False
    }
    with report.open("x",encoding="utf-8") as output:
        json.dump(record,output,indent=2)
        output.write("\n")
    return str(EXECUTABLE)+":unixsocket-smoke",[report]
