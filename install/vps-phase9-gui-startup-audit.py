#!/usr/bin/env python3
"""F9: guarded, non-interactive GUI startup audit of Ferrari-private Linux apps.

Uses the VPS's existing Xvfb as a temporary QA display (not a project runtime).
A process staying alive briefly is NOT certification of editing, CAD, recording
or supplier-independent dependencies. No app is allowed to stream or persist.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT=Path("/srv/projects/skill-universal")
RUNTIME=ROOT/".runtime"
TOOLS=ROOT/"tools"
PROBES={
    "librecad":"librecad-2.2.1.6/squashfs-root/AppRun",
    "audacity":"audacity-4.0.2/squashfs-root/AppRun",
    "openshot":"openshot-4.1.1/squashfs-root/AppRun",
    "synfig":"synfig-1.5.5/SynfigStudio-1.5.5-2026.03.15-linux64-79bf7.appimage",
    "solvespace":"solvespace-3.1-ubuntu24/usr/bin/solvespace",
    "obs":"obs-studio-32.2.2/run-obs",
}
LIMIT_SECONDS=7.0

def guard() -> None:
    assert os.geteuid()!=0, "F9_GUI_NO_ROOT"
    assert ROOT.resolve(strict=True)==Path("/srv/projects/skill-universal")
    for p in (ROOT,RUNTIME,TOOLS):
        assert p.is_dir() and not p.is_symlink(), "F9_GUI_UNSAFE_PROJECT_ROOT"
    tester=Path("/usr/bin/xvfb-run")
    assert tester.is_file() and os.access(tester,os.X_OK), "F9_GUI_XVFB_EXISTING_QA_REQUIRED"
    assert Path("/usr/bin/Xvfb").is_file(), "F9_GUI_XVFB_SERVER_REQUIRED"

def executable(name: str) -> Path:
    path=TOOLS/PROBES[name]
    assert path.is_file() and os.access(path,os.X_OK), "F9_GUI_PRIVATE_APP_MISSING:"+name
    assert path.resolve(strict=True).is_relative_to(TOOLS.resolve(strict=True)), \
        "F9_GUI_PRIVATE_APP_ESCAPED:"+name
    return path

def run_one(name: str) -> dict:
    app=executable(name)
    with tempfile.TemporaryDirectory(prefix=".f9-gui-"+name+"-",dir=RUNTIME) as td:
        work=Path(td)
        env=os.environ.copy()
        env.update({
            "HOME":str(work),"TMPDIR":str(work),
            "XDG_CONFIG_HOME":str(work),"XDG_CACHE_HOME":str(work),
            "XDG_DATA_HOME":str(work),"XDG_RUNTIME_DIR":str(work),
            "QT_QPA_PLATFORM":"xcb","GDK_BACKEND":"x11",
            "LIBGL_ALWAYS_SOFTWARE":"1","GSETTINGS_BACKEND":"memory",
            "PYTHONNOUSERSITE":"1","DBUS_SESSION_BUS_ADDRESS":"unix:path=/dev/null",
            "HTTP_PROXY":"http://127.0.0.1:9",
            "HTTPS_PROXY":"http://127.0.0.1:9",
            "ALL_PROXY":"socks5://127.0.0.1:9",
        })
        env.pop("LD_LIBRARY_PATH",None)
        env.pop("PYTHONPATH",None)
        cmd=["/usr/bin/xvfb-run","-a",
             "--server-args=-screen 0 1280x800x24 -nolisten tcp",
             str(app)]
        p=subprocess.Popen(cmd,cwd=work,env=env,stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE,start_new_session=True)
        alive=False
        try:
            out,err=p.communicate(timeout=LIMIT_SECONDS)
            result="exited_early"
        except subprocess.TimeoutExpired:
            alive=True
            result="survived_seven_seconds"
            os.killpg(p.pid,signal.SIGTERM)
            try:
                out,err=p.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGKILL)
                out,err=p.communicate(timeout=3)
        return {
            "tool":name,"status":result,
            "startup_survived_seven_seconds":alive,
            "gui_functionality_certified":False,
            "dependency_isolation_certified":False,
            "test_display":"preexisting Ubuntu Xvfb, transient QA only",
            "diagnostic":(err or out or b"").decode("utf-8","replace")[-340:],
        }

def certify() -> dict:
    guard()
    original=ROOT/"current"
    current=original.resolve(strict=True)
    assert original.is_symlink() and current.parent==(ROOT/"releases").resolve(strict=True), \
        "F9_GUI_ACTIVE_RELEASE_UNSAFE"
    results=[]
    for name in PROBES:
        result=run_one(name)
        results.append(result)
        print("F9_GUI_STARTUP_PROBE="+json.dumps(result,sort_keys=True),flush=True)
    assert original.resolve(strict=True)==current, "F9_GUI_ACTIVE_RELEASE_MOVED"
    return {
        "status":"audit_complete",
        "applications_checked":len(results),
        "startups_survived":sum(bool(x["startup_survived_seven_seconds"]) for x in results),
        "gui_functions_certified":0,
        "app_private_runtime_certified":False,
        "global_apt_changed":False,
        "other_projects_changed":False,
        "root":str(ROOT),
        "results":results,
    }

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--audit",action="store_true",required=True)
    p.parse_args()
    try:
        result=certify()
        print("F9_GUI_AUDIT="+json.dumps(result,sort_keys=True),flush=True)
        return 0
    except Exception as err:
        print("F9_GUI_AUDIT="+json.dumps({"status":"blocked",
              "reason":str(err)[-300:],"global_apt_changed":False},sort_keys=True),flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
