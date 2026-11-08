#!/usr/bin/env python3
"""Ferrari F14: close out four optional GUI programs with honest REAL tests.

Each GUI tool receives an independent verdict. A CLI help/startup/version
never counts as editing, rendering or recording. No global writes or installs.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import tempfile
import time

ROOT=Path("/srv/projects/skill-universal")
ACTIVE="3f0ba44b7d8475a74a63c6010d1e27063c04bf1e"
FALLBACK="427e1c33c6d10ca8ecd2103861adccd3d552c381"
SERVICES=("pink-iptv-backend","pink-vpn","fadego-staging","lowcost-europa",
          "pm2-iptvpn-bot","pm2-telegram-robot-leads","nginx","postgresql@16-main")
# Provenance: solvespace/solvespace, test/request/line_segment/normal.slvs,
# original public GPL-3.0 test fixture. It has no user-supplied data.
SOLVESPACE_FIXTURE="±²³SolveSpaceREVa\n\n\nGroup.h.v=00000001\nGroup.type=5000\nGroup.name=#references\nGroup.color=ff000000\nGroup.skipFirst=0\nGroup.predef.swapUV=0\nGroup.predef.negateU=0\nGroup.predef.negateV=0\nGroup.visible=1\nGroup.suppress=0\nGroup.relaxConstraints=0\nGroup.allowRedundant=0\nGroup.allDimsReference=0\nGroup.scale=1.00000000000000000000\nGroup.remap={\n}\nAddGroup\n\nGroup.h.v=00000002\nGroup.type=5001\nGroup.order=1\nGroup.name=sketch-in-plane\nGroup.activeWorkplane.v=80020000\nGroup.color=ff000000\nGroup.subtype=6000\nGroup.skipFirst=0\nGroup.predef.q.w=1.00000000000000000000\nGroup.predef.origin.v=00010001\nGroup.predef.swapUV=0\nGroup.predef.negateU=0\nGroup.predef.negateV=0\nGroup.visible=1\nGroup.suppress=0\nGroup.relaxConstraints=0\nGroup.allowRedundant=0\nGroup.allDimsReference=0\nGroup.scale=1.00000000000000000000\nGroup.remap={\n}\nAddGroup\n\nParam.h.v.=00010010\nAddParam\n\nParam.h.v.=00010011\nAddParam\n\nParam.h.v.=00010012\nAddParam\n\nParam.h.v.=00010020\nParam.val=1.00000000000000000000\nAddParam\n\nParam.h.v.=00010021\nAddParam\n\nParam.h.v.=00010022\nAddParam\n\nParam.h.v.=00010023\nAddParam\n\nParam.h.v.=00020010\nAddParam\n\nParam.h.v.=00020011\nAddParam\n\nParam.h.v.=00020012\nAddParam\n\nParam.h.v.=00020020\nParam.val=0.50000000000000000000\nAddParam\n\nParam.h.v.=00020021\nParam.val=0.50000000000000000000\nAddParam\n\nParam.h.v.=00020022\nParam.val=0.50000000000000000000\nAddParam\n\nParam.h.v.=00020023\nParam.val=0.50000000000000000000\nAddParam\n\nParam.h.v.=00030010\nAddParam\n\nParam.h.v.=00030011\nAddParam\n\nParam.h.v.=00030012\nAddParam\n\nParam.h.v.=00030020\nParam.val=0.50000000000000000000\nAddParam\n\nParam.h.v.=00030021\nParam.val=-0.50000000000000000000\nAddParam\n\nParam.h.v.=00030022\nParam.val=-0.50000000000000000000\nAddParam\n\nParam.h.v.=00030023\nParam.val=-0.50000000000000000000\nAddParam\n\nParam.h.v.=00040010\nParam.val=-5.00000000000000000000\nAddParam\n\nParam.h.v.=00040011\nParam.val=5.00000000000000000000\nAddParam\n\nParam.h.v.=00040013\nParam.val=5.00000000000000000000\nAddParam\n\nParam.h.v.=00040014\nParam.val=5.00000000000000000000\nAddParam\n\nRequest.h.v=00000001\nRequest.type=100\nRequest.group.v=00000001\nRequest.construction=0\nAddRequest\n\nRequest.h.v=00000002\nRequest.type=100\nRequest.group.v=00000001\nRequest.construction=0\nAddRequest\n\nRequest.h.v=00000003\nRequest.type=100\nRequest.group.v=00000001\nRequest.construction=0\nAddRequest\n\nRequest.h.v=00000004\nRequest.type=200\nRequest.workplane.v=80020000\nRequest.group.v=00000002\nRequest.construction=0\nAddRequest\n\nEntity.h.v=00010000\nEntity.type=10000\nEntity.construction=0\nEntity.point[0].v=00010001\nEntity.normal.v=00010020\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00010001\nEntity.type=2000\nEntity.construction=1\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00010020\nEntity.type=3000\nEntity.construction=0\nEntity.point[0].v=00010001\nEntity.actNormal.w=1.00000000000000000000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00020000\nEntity.type=10000\nEntity.construction=0\nEntity.point[0].v=00020001\nEntity.normal.v=00020020\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00020001\nEntity.type=2000\nEntity.construction=1\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00020020\nEntity.type=3000\nEntity.construction=0\nEntity.point[0].v=00020001\nEntity.actNormal.w=0.50000000000000000000\nEntity.actNormal.vx=0.50000000000000000000\nEntity.actNormal.vy=0.50000000000000000000\nEntity.actNormal.vz=0.50000000000000000000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00030000\nEntity.type=10000\nEntity.construction=0\nEntity.point[0].v=00030001\nEntity.normal.v=00030020\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00030001\nEntity.type=2000\nEntity.construction=1\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00030020\nEntity.type=3000\nEntity.construction=0\nEntity.point[0].v=00030001\nEntity.actNormal.w=0.50000000000000000000\nEntity.actNormal.vx=-0.50000000000000000000\nEntity.actNormal.vy=-0.50000000000000000000\nEntity.actNormal.vz=-0.50000000000000000000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00040000\nEntity.type=11000\nEntity.construction=0\nEntity.point[0].v=00040001\nEntity.point[1].v=00040002\nEntity.workplane.v=80020000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00040001\nEntity.type=2001\nEntity.construction=0\nEntity.workplane.v=80020000\nEntity.actPoint.x=-5.00000000000000000000\nEntity.actPoint.y=5.00000000000000000000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=00040002\nEntity.type=2001\nEntity.construction=0\nEntity.workplane.v=80020000\nEntity.actPoint.x=5.00000000000000000000\nEntity.actPoint.y=5.00000000000000000000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=80020000\nEntity.type=10000\nEntity.construction=0\nEntity.point[0].v=80020002\nEntity.normal.v=80020001\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=80020001\nEntity.type=3010\nEntity.construction=0\nEntity.point[0].v=80020002\nEntity.actNormal.w=1.00000000000000000000\nEntity.actVisible=1\nAddEntity\n\nEntity.h.v=80020002\nEntity.type=2012\nEntity.construction=1\nEntity.actVisible=1\nAddEntity\n\n"

def guard():
    if os.geteuid()==0 or ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("F14_MUST_RUN_UNPRIVILEGED_IN_FERRARI")
    for name in ("tools",".runtime","releases","runtimes"):
        p=ROOT/name
        if p.is_symlink() or not p.is_dir():
            raise RuntimeError("F14_PRIVATE_DIRECTORY_INVALID:"+name)
    current=ROOT/"current"
    if not current.is_symlink() or current.resolve(strict=True)!=ROOT/"releases"/ACTIVE:
        raise RuntimeError("F14_RELEASE_CHANGED")
    if not (ROOT/"releases"/FALLBACK/"engine/catalog.json").is_file():
        raise RuntimeError("F14_FALLBACK_MISSING")
    catalog=json.loads((current/"engine/catalog.json").read_text(encoding="utf-8"))
    if (len(catalog["tools"]),len(catalog["functions"]),catalog["counts"]["all_catalog_entries"])!=(173,280,458):
        raise RuntimeError("F14_UNIVERSAL_CATALOG_CHANGED")

def services():
    result={}
    for service in SERVICES:
        p=subprocess.run(["/usr/bin/systemctl","is-active",service],capture_output=True,
                         text=True,timeout=12,check=False)
        result[service]=p.stdout.strip()
    if set(result.values())!={"active"}:
        raise RuntimeError("F14_PROTECTED_SERVICES_UNHEALTHY:"+repr(result))
    return result

def private_exe(name):
    sys.path.insert(0,str(ROOT/"current"))
    from engine import tool_runtime
    executable=tool_runtime.executable(name)
    if not executable:
        raise RuntimeError("F14_PRIVATE_BINARY_ABSENT:"+name)
    path=Path(executable)
    if not path.is_file() or not os.access(path,os.X_OK):
        raise RuntimeError("F14_PRIVATE_BINARY_NOT_EXECUTABLE:"+name)
    if not path.resolve(strict=True).is_relative_to((ROOT/"tools").resolve(strict=True)):
        raise RuntimeError("F14_EXECUTABLE_ESCAPED_PROJECT:"+name)
    return str(path)

def runtime_env(work,graphical=False):
    for dir_name in ("config","data","cache","run","sessions"):
        (work/dir_name).mkdir(mode=0o700,exist_ok=True)
    result=os.environ.copy()
    for key in ("PYTHONPATH","PYTHONHOME","LD_LIBRARY_PATH","LD_PRELOAD"):
        result.pop(key,None)
    result.update({"HOME":str(work),"TMPDIR":str(work),
          "XDG_CONFIG_HOME":str(work/"config"),
          "XDG_CACHE_HOME":str(work/"cache"),
          "XDG_DATA_HOME":str(work/"data"),
          "XDG_RUNTIME_DIR":str(work/"run"),
          "QT_QPA_PLATFORM":"xcb" if graphical else "offscreen",
          "LIBGL_ALWAYS_SOFTWARE":"1","OMP_NUM_THREADS":"2",
          "PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1",
          "HTTP_PROXY":"http://127.0.0.1:9",
          "HTTPS_PROXY":"http://127.0.0.1:9",
          "ALL_PROXY":"socks5://127.0.0.1:9",
          "NO_PROXY":"localhost,127.0.0.1","no_proxy":"localhost,127.0.0.1"})
    return result

def run(cmd,work,env,timeout=35):
    r=subprocess.run([str(x) for x in cmd],cwd=work,env=env,timeout=timeout,
                     capture_output=True,text=True,check=False)
    if r.returncode:
        raise RuntimeError("command_exit_"+str(r.returncode)+":"+(r.stderr or r.stdout)[-450:])
    return r.stdout

def sha(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for block in iter(lambda:f.read(65536),b""):
            h.update(block)
    return h.hexdigest()

def audacity_check(work):
    # Official Audacity 4.0.x notes explicitly remove script pipe and macros.
    # Do not install an older build or claim that unrelated FFmpeg is Audacity.
    private_exe("audacity")
    return {"status":"not_certified","reason":"Audacity_4.0.2_no_macro_manager_or_script_pipe",
      "upstream":"https://www.audacityteam.org/changelog/4.0.0/",
      "private_installed":True,"headless_editing_demonstrated":False,
      "gui_manual_editing_not_tested":True}

def solvespace_check(work):
    gui=Path(private_exe("solvespace"))
    cli=gui.with_name("solvespace-cli")
    if not cli.is_file() or not os.access(cli,os.X_OK) or not cli.resolve(strict=True).is_relative_to(ROOT/"tools"):
        return {"status":"not_certified",
          "reason":"private_ubuntu_3.1_install_has_no_export_capable_solvespace_cli",
          "gui_private_installed":True,"cli_present":False,
          "real_cad_export_demonstrated":False}
    model=work/"official-public-line.slvs"
    model.write_bytes(SOLVESPACE_FIXTURE.encode("latin-1"))
    if model.stat().st_size<4000 or not model.read_bytes().startswith(b"\xb1\xb2\xb3SolveSpaceREV"):
        raise RuntimeError("F14_SOLVESPACE_PUBLIC_FIXTURE_INVALID")
    result=work/"line.svg"
    run([cli,"export-view","--output",result,"--view","top",model],work,runtime_env(work),timeout=55)
    if not result.is_file() or result.stat().st_size<250 or b"<svg" not in result.read_bytes()[:1600]:
        raise RuntimeError("F14_SOLVESPACE_SVG_NOT_REAL")
    return {"status":"pass","mode":"public_slvs_to_svg_real","source_bytes":model.stat().st_size,
      "svg_bytes":result.stat().st_size,"svg_sha256":sha(result),
      "private_cli":str(cli),"full_gui_certified":False}

SIF='''<?xml version="1.0" encoding="UTF-8"?>
<canvas version="1.2" width="160" height="120" view-box="-2.0 1.5 2.0 -1.5"
 fps="24" begin-time="0f" end-time="1s" bgcolor="1.0 1.0 1.0 1.0">
 <layer type="rectangle" active="true" version="0.2" desc="synthetic">
 <param name="color"><color><r>1</r><g>0</g><b>0</b><a>1</a></color></param>
 <param name="point1"><vector><x>-1</x><y>0.75</y></vector></param>
 <param name="point2"><animated type="vector">
 <waypoint time="0s" before="linear" after="linear"><vector><x>0</x><y>-0.75</y></vector></waypoint>
 <waypoint time="1s" before="linear" after="linear"><vector><x>1</x><y>-0.75</y></vector></waypoint>
 </animated></param>
 </layer>
</canvas>
'''
def synfig_check(work):
    exe=private_exe("synfig")
    source=work/"moving-red-rectangle.sif"
    source.write_text(SIF,encoding="utf-8")
    env=runtime_env(work)
    frames=[]
    for t in ("0s","1s"):
        out=work/("frame"+t+".png")
        run([exe,"--appimage-exec","synfig",str(source),
             "-t","png","--time",t,"-o",str(out)],work,env,timeout=75)
        if not out.is_file() or out.stat().st_size<500 or out.read_bytes()[:8]!=b"\x89PNG\r\n\x1a\n":
            raise RuntimeError("F14_SYNFIG_REAL_FRAME_MISSING:"+t)
        frames.append({"frame":t,"bytes":out.stat().st_size,"sha256":sha(out)})
    if frames[0]["sha256"]==frames[1]["sha256"]:
        raise RuntimeError("F14_SYNFIG_ANIMATED_FRAME_IDENTICAL")
    return {"status":"pass","mode":"synthetic_animated_SIF_to_two_PNG_frames",
            "frames":frames,"frame_changed":True,"full_gui_certified":False}

def obs_check(work):
    exe=private_exe("obs")
    xvfb=Path("/usr/bin/xvfb-run")
    if not xvfb.is_file() or not os.access(xvfb,os.X_OK):
        raise RuntimeError("F14_EXISTING_XVFB_NOT_PRESENT")
    ffprobe=ROOT/"tools/ubuntu-cli/bin/ffprobe"
    if not ffprobe.is_file() or not os.access(ffprobe,os.X_OK):
        raise RuntimeError("F14_PRIVATE_FFPROBE_MISSING")
    env=runtime_env(work,graphical=True)
    env.update({"PULSE_SERVER":"unix:/dev/null",
                "PIPEWIRE_REMOTE":"ferrari-no-audio-devices",
                "ALSA_CONFIG_PATH":"/dev/null",
                "DBUS_SESSION_BUS_ADDRESS":"unix:path=/dev/null"})
    base=work/"config/obs-studio/basic"
    profile=base/"profiles/FerrariBlank"
    scenes=base/"scenes"
    profile.mkdir(parents=True,exist_ok=True)
    scenes.mkdir(parents=True,exist_ok=True)
    recordings=work/"recordings"
    recordings.mkdir(mode=0o700)
    (profile/"basic.ini").write_text(
        "[General]\nName=FerrariBlank\n"
        "[Video]\nBaseCX=320\nBaseCY=180\nOutputCX=320\nOutputCY=180\nFPSCommon=25\n"
        "[Output]\nMode=Simple\n"
        "[SimpleOutput]\nFilePath="+str(recordings)+"\nRecFormat2=mkv\n"
        "RecEncoder=obs_x264\nRecQuality=Small\n"
        "[Audio]\nSampleRate=48000\nChannelSetup=Stereo\n"
        "DesktopAudioDevice1=disabled\nDesktopAudioDevice2=disabled\n"
        "AuxAudioDevice1=disabled\nAuxAudioDevice2=disabled\n"
        "AuxAudioDevice3=disabled\nAuxAudioDevice4=disabled\n",encoding="utf-8")
    scene={"name":"FerrariBlank","current_scene":"FerrariBlank",
           "current_program_scene":"FerrariBlank","sources":[{
             "name":"FerrariBlank","id":"scene","settings":{"items":[]}}],
           "groups":[],"scene_order":[{"name":"FerrariBlank"}],
           "transitions":[],"transition_duration":300,
           "quick_transitions":[],"modules":{}}
    (scenes/"FerrariBlank.json").write_text(json.dumps(scene),encoding="utf-8")
    if len(scene["sources"])!=1 or scene["sources"][0]["settings"]["items"]:
        raise RuntimeError("F14_OBS_NONBLANK_SCENE_REFUSED")
    p=subprocess.Popen([str(xvfb),"-a",
            "--server-args=-screen 0 640x480x24 -nolisten tcp",
            exe,"--profile","FerrariBlank","--collection","FerrariBlank",
            "--scene","FerrariBlank","--startrecording","--multi","--disable-updater"],
            cwd=work,env=env,capture_output if False else subprocess.PIPE,
            stderr=subprocess.PIPE,start_new_session=True)
    try:
        time.sleep(12)
        try:
            os.killpg(p.pid,signal.SIGINT)
        except ProcessLookupError:
            pass
        try:
            out,err=p.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGKILL)
            out,err=p.communicate(timeout=5)
    finally:
        if p.poll() is None:
            os.killpg(p.pid,signal.SIGKILL)
            p.wait(timeout=5)
    files=[x for x in recordings.rglob("*") if x.is_file() and x.suffix.lower() in {".mkv",".mp4"}]
    if len(files)!=1 or files[0].stat().st_size<1800:
        return {"status":"not_certified","reason":"blank_recording_not_produced",
           "recordings_created":len(files),"diagnostic":(err or out or b"").decode("utf-8","replace")[-400:],
           "microphone_camera_desktop_capture_disabled":True}
    data=json.loads(run([ffprobe,"-v","error","-show_entries","format=duration:stream=codec_type",
       "-of","json",files[0]],work,env,timeout=20))
    duration=float(data.get("format",{}).get("duration",0))
    tracks=[s for s in data.get("streams",[]) if s.get("codec_type")=="video"]
    if not 0.5<duration<25 or not tracks:
        raise RuntimeError("F14_OBS_RECORDING_EMPTY_OR_INVALID")
    return {"status":"pass","mode":"blank_only_local_video_capture",
       "output_bytes":files[0].stat().st_size,"duration_seconds":duration,
       "sha256":sha(files[0]),"camera_mic_screen_and_stream_disabled":True,
       "full_OBS_GUI_certified":False}

def main():
    argparse.ArgumentParser(description="Ferrari final bound-to-project QA").parse_args()
    try:
        guard()
        before=services()
        reports={}
        for name,func in (("audacity",audacity_check),("solvespace",solvespace_check),
                          ("synfig",synfig_check),("obs",obs_check)):
            try:
                with tempfile.TemporaryDirectory(prefix=".f14-"+name+"-",dir=ROOT/".runtime") as td:
                    reports[name]=func(Path(td))
            except (Exception,) as exc:
                reports[name]={"status":"not_certified","reason":str(exc)[-500:]}
            print("F14_TOOL="+name+" "+reports[name]["status"],file=sys.stderr,flush=True)
        guard()
        after=services()
        if before!=after:
            raise RuntimeError("F14_PROTECTED_SERVICES_CHANGED")
        report={"status":"audit_complete","tested":list(reports),
            "real_passed":sum(x["status"]=="pass" for x in reports.values()),
            "not_certified":sum(x["status"]!="pass" for x in reports.values()),
            "tools":reports,"protected_services":"8/8_PASS",
            "release":ACTIVE,"fallback":FALLBACK,"catalog_entries":458,
            "global_apt_modified":False,"other_projects_modified":False,
            "permanent_files_added":False,"unverified_apps_not_counted_as_pass":True}
        print(json.dumps(report,sort_keys=True),flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","error":str(exc)[-600:],
            "global_apt_modified":False,"other_projects_modified":False},sort_keys=True),flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
