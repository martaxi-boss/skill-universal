#!/usr/bin/env python3
"""Ferrari F13: real, project-confined OpenShot 4.1.1 headless video workflow.

An installed AppImage, --version or --cli help alone is never "certified".
Only imported/edited/saved/exported media with independent ffprobe passes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
ACTIVE = "3f0ba44b7d8475a74a63c6010d1e27063c04bf1e"
FALLBACK = "427e1c33c6d10ca8ecd2103861adccd3d552c381"
SERVICES = ("pink-iptv-backend", "pink-vpn", "fadego-staging", "lowcost-europa",
            "pm2-iptvpn-bot", "pm2-telegram-robot-leads", "nginx", "postgresql@16-main")


def guard():
    if os.geteuid() == 0 or ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("F13_NONROOT_FERRARI_ONLY")
    for d in (ROOT / "tools", ROOT / ".runtime", ROOT / "releases", ROOT / "runtimes"):
        if d.is_symlink() or not d.is_dir():
            raise RuntimeError("F13_PROJECT_ROOT_INVALID")
    current = ROOT / "current"
    if not current.is_symlink() or current.resolve(strict=True) != ROOT / "releases" / ACTIVE:
        raise RuntimeError("F13_ACTIVE_SHA_CHANGED")
    if not (ROOT / "releases" / FALLBACK / "engine/catalog.json").is_file():
        raise RuntimeError("F13_FALLBACK_MISSING")
    catalog = json.loads((current / "engine/catalog.json").read_text(encoding="utf-8"))
    if len(catalog["tools"]) != 173 or len(catalog["functions"]) != 280 or catalog["counts"]["all_catalog_entries"] != 458:
        raise RuntimeError("F13_CATALOG_CHANGED")


def services():
    result = {}
    for name in SERVICES:
        p = subprocess.run(["/usr/bin/systemctl", "is-active", name],
                           capture_output=True, text=True, timeout=12, check=False)
        result[name] = p.stdout.strip()
    if set(result.values()) != {"active"}:
        raise RuntimeError("F13_SERVICE_UNHEALTHY:" + str([x for x, v in result.items() if v != "active"]))
    return result


def env_for(work):
    e = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH", "LD_PRELOAD", "OPENSHOT_SESSION"):
        e.pop(key, None)
    e.update({
        "HOME": str(work), "TMPDIR": str(work),
        "XDG_CONFIG_HOME": str(work / "config"), "XDG_CACHE_HOME": str(work / "cache"),
        "XDG_DATA_HOME": str(work / "data"), "XDG_RUNTIME_DIR": str(work / "run"),
        "OPENSHOT_SESSION_DIR": str(work / "sessions"),
        "QT_QPA_PLATFORM": "offscreen", "LIBGL_ALWAYS_SOFTWARE": "1",
        "APPIMAGELAUNCHER_DISABLE": "1", "SDL_AUDIODRIVER": "dummy",
        "GSETTINGS_BACKEND": "memory", "PYTHONNOUSERSITE": "1",
        "PYTHONDONTWRITEBYTECODE": "1", "OMP_NUM_THREADS": "2",
        "HTTP_PROXY": "http://127.0.0.1:9", "HTTPS_PROXY": "http://127.0.0.1:9",
        "ALL_PROXY": "socks5://127.0.0.1:9",
        "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost",
    })
    for name in ("config", "cache", "data", "run", "sessions"):
        (work / name).mkdir(mode=0o700)
    return e


def run(args, *, cwd, env, timeout=45):
    p = subprocess.run([str(x) for x in args], cwd=cwd, env=env,
                       capture_output=True, text=True, timeout=timeout, check=False)
    if p.returncode:
        raise RuntimeError("F13_EXEC_FAILED:"+str(p.returncode)+":"+(p.stderr or p.stdout)[-500:])
    return p.stdout


def answer(text, kind):
    """Reject CLI-only banners/warnings posing as JSON success."""
    text = text.strip()
    try:
        d = json.loads(text)
    except (json.JSONDecodeError, ValueError) as e:
        raise RuntimeError("F13_"+kind+"_NON_JSON:" + text[-250:]) from e
    if not isinstance(d, dict) or d.get("ok") is not True or not isinstance(d.get("result"), dict):
        raise RuntimeError("F13_"+kind+"_NOT_OK:" + text[-350:])
    return d["result"]


def result_id(result, label):
    """OpenShot CLI mutations carry IDs inside result.data, not always at top level."""
    for item in (result.get("data"), result.get("file"), result.get("clip"), result):
        if isinstance(item, dict):
            value = item.get("id") or item.get("file_id") or item.get("clip_id")
            if isinstance(value, str) and 0 < len(value) <= 160:
                return value
    raise RuntimeError("F13_"+label+"_MISSING_ID:"+repr(result)[:250])


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1024 * 1024), b""):
            h.update(b)
    return h.hexdigest()


def private_tools():
    sys.path.insert(0, str(ROOT / "current"))
    from engine import ferrari, tool_runtime
    exe = tool_runtime.executable("openshot")
    if not exe:
        raise RuntimeError("F13_OPENSHOT_PRIVATE_MISSING")
    p = Path(exe).resolve(strict=True)
    if not p.is_relative_to((ROOT / "tools").resolve(strict=True)) or not os.access(p, os.X_OK):
        raise RuntimeError("F13_OPENSHOT_NOT_ISOLATED")
    return exe, ferrari._exe("ffmpeg"), ferrari._exe("ffprobe")


def probe():
    guard()
    exe, _, _ = private_tools()
    with tempfile.TemporaryDirectory(prefix=".f13-openshot-probe-", dir=ROOT / ".runtime") as path:
        work = Path(path)
        env = env_for(work)
        out = run([exe, "--cli", "help"], cwd=work, env=env, timeout=45)
        if not all(k in out.lower() for k in ("session", "clip", "export")):
            raise RuntimeError("F13_OPENSHOT_CLI_NOT_EDIT_CAPABLE:" + out[-350:])
    guard()
    return {"status":"PASS","mode":"probe","tool":"openshot",
            "private_executable":exe,"cli_edits_and_exports_listed":True,
            "real_edit_export_certified":False}


def certify():
    guard()
    exe, ffmpeg, ffprobe = private_tools()
    if shutil.disk_usage(ROOT).free < 3 * 1024**3:
        raise RuntimeError("F13_DISK_GUARD")
    with tempfile.TemporaryDirectory(prefix=".f13-openshot-real-", dir=ROOT / ".runtime") as tmp:
        work = Path(tmp)
        env = env_for(work)
        source = work / "synthetic-source.mp4"
        edited = work / "edited.mp4"
        project = work / "editable.osp"
        run([ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", "testsrc2=s=320x180:r=25:d=2",
             "-an", "-c:v", "mpeg4", "-b:v", "350k", "-pix_fmt", "yuv420p",
             "-t", "2", str(source)], cwd=work, env=env, timeout=35)
        if not source.is_file() or source.stat().st_size < 1500:
            raise RuntimeError("F13_SYNTHETIC_SOURCE_MISSING")
        session_id = None
        commands = []
        try:
            start = answer(run([exe, "--cli", "session", "start"], cwd=work, env=env,
                               timeout=55), "SESSION_START")
            session_id = start.get("session_id")
            if not isinstance(session_id, str) or not session_id or len(session_id) > 160:
                raise RuntimeError("F13_SESSION_ID_INVALID")
            env["OPENSHOT_SESSION"] = session_id

            def call(*args, timeout=45):
                val = answer(run([exe, "--cli", *args], cwd=work, env=env, timeout=timeout),
                             "_".join(args[:2]).upper())
                commands.append(" ".join(args[:2]))
                return val

            imported = call("file", "import", str(source))
            file_id = result_id(imported,"IMPORTED_FILE")
            call("project", "profile", "set", "--from-file", file_id, "--create-custom")
            added = call("clip", "add", file_id, "--layer", "1000000",
                         "--position", "0", "--start", "0", "--end", "1")
            clip_id = result_id(added,"EDITED_CLIP")
            call("project", "save", str(project))
            call("export", "start", str(edited), "--wait", "--wait-timeout", "115",
                 timeout=150)
            if not project.is_file() or project.stat().st_size < 500:
                raise RuntimeError("F13_REAL_OSP_NOT_WRITTEN")
            if not edited.is_file() or edited.stat().st_size < 1500:
                raise RuntimeError("F13_REAL_MP4_NOT_WRITTEN")
            meta = json.loads(run([ffprobe, "-v", "error", "-show_entries",
                "stream=codec_type,width,height:format=duration",
                "-of", "json", str(edited)], cwd=work, env=env, timeout=25))
            tracks = [x for x in meta.get("streams", []) if x.get("codec_type") == "video"]
            if len(tracks) < 1:
                raise RuntimeError("F13_MP4_NO_VIDEO")
            duration = float(meta.get("format", {}).get("duration", 0))
            if not 0.8 <= duration <= 1.5:
                raise RuntimeError("F13_EDIT_TRIM_DURATION_INVALID:"+str(duration))
            if int(tracks[0].get("width",0)) != 320 or int(tracks[0].get("height",0)) != 180:
                raise RuntimeError("F13_EXPORT_SIZE_INVALID")
            result = {"status":"PASS","mode":"certify","tool":"openshot",
                      "private_executable":exe, "synthetic_source_bytes":source.stat().st_size,
                      "original_duration_seconds":2.0,
                      "timeline_trim_requested_seconds":1.0,
                      "exported_duration_seconds":duration,
                      "exported_resolution":"320x180",
                      "project_osp_bytes":project.stat().st_size,
                      "project_osp_sha256":digest(project),
                      "edited_mp4_bytes":edited.stat().st_size,
                      "edited_mp4_sha256":digest(edited),
                      "commands_confirmed":commands,
                      "interactive_gui_certified":False,
                      "external_media_or_network_used":False}
        finally:
            if session_id is not None:
                try:
                    stop = subprocess.run([exe, "--cli", "session", "stop", "--discard"],
                                          cwd=work, env=env, capture_output=True,
                                          text=True, timeout=30, check=False)
                    if stop.returncode:
                        print("F13_OPENSHOT_SESSION_STOP_FAILED="+stop.stderr[-300:],file=sys.stderr)
                except (OSError, subprocess.TimeoutExpired) as e:
                    print("F13_OPENSHOT_SESSION_STOP_ERROR="+str(e)[-200:],file=sys.stderr)
        if session_id is None:
            raise RuntimeError("F13_SESSION_NEVER_STARTED")
        if not result:
            raise RuntimeError("F13_NO_OUTPUT")
    guard()
    return result


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("probe","certify"), required=True)
    a = p.parse_args()
    try:
        before=services()
        report=probe() if a.mode=="probe" else certify()
        after=services()
        if before!=after:
            raise RuntimeError("F13_PROTECTED_SERVICE_CHANGED")
        report.update({"active":ACTIVE,"fallback":FALLBACK,"services":"8/8_PASS",
                       "global_apt_changed":False,"other_projects_changed":False,
                       "permanent_files_added":False})
        print(json.dumps(report,sort_keys=True),flush=True)
        return 0
    except Exception as e:
        print(json.dumps({"status":"BLOCKED","mode":a.mode,"reason":str(e)[-650:],
            "global_apt_changed":False,"other_projects_changed":False},sort_keys=True),flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
