#!/usr/bin/env python3
"""Ferrari F14 OBS r2: synthetic-only recording, graceful stop, independently verified video."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time

ROOT = Path("/srv/projects/skill-universal")
ACTIVE = "3f0ba44b7d8475a74a63c6010d1e27063c04bf1e"
FALLBACK = "427e1c33c6d10ca8ecd2103861adccd3d552c381"
SERVICES = ("pink-iptv-backend","pink-vpn","fadego-staging","lowcost-europa",
            "pm2-iptvpn-bot","pm2-telegram-robot-leads","nginx","postgresql@16-main")

def guard():
    if os.geteuid()==0 or ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("F14_OBS_NOT_PRIVATE_UNPRIVILEGED")
    for name in ("tools",".runtime","releases","runtimes"):
        path=ROOT/name
        if path.is_symlink() or not path.is_dir():
            raise RuntimeError("F14_OBS_PROJECT_ROOT_INVALID:"+name)
    current=ROOT/"current"
    if not current.is_symlink() or current.resolve(strict=True)!=ROOT/"releases"/ACTIVE:
        raise RuntimeError("F14_OBS_ACTIVE_CHANGED")
    if not (ROOT/"releases"/FALLBACK/"engine/catalog.json").is_file():
        raise RuntimeError("F14_OBS_FALLBACK_MISSING")
    catalog=json.loads((current/"engine/catalog.json").read_text(encoding="utf-8"))
    if len(catalog["tools"])!=173 or len(catalog["functions"])!=280 or catalog["counts"]["all_catalog_entries"]!=458:
        raise RuntimeError("F14_OBS_CATALOG_MISMATCH")

def services():
    states={}
    for name in SERVICES:
        p=subprocess.run(["/usr/bin/systemctl","is-active",name],capture_output=True,
                         text=True,timeout=12,check=False)
        states[name]=p.stdout.strip()
    if set(states.values())!={"active"}:
        raise RuntimeError("F14_OBS_PROTECTED_SERVICE_DOWN:"+str(states))
    return states

def private_exe(name):
    sys.path.insert(0,str(ROOT/"current"))
    from engine import tool_runtime
    exe=tool_runtime.executable(name)
    if not exe or not os.access(exe,os.X_OK) or not Path(exe).resolve(strict=True).is_relative_to(ROOT/"tools"):
        raise RuntimeError("F14_OBS_PRIVATE_EXECUTABLE_MISSING:"+name)
    return str(exe)

def digest(path):
    h=hashlib.sha256()
    with Path(path).open("rb") as f:
        for b in iter(lambda:f.read(65536),b""):
            h.update(b)
    return h.hexdigest()

def read_log(work):
    logs=(work/"config/obs-studio/logs")
    if not logs.is_dir() or logs.is_symlink():
        return ""
    entries=[p for p in logs.glob("*.txt") if p.is_file() and not p.is_symlink()]
    if not entries:
        return ""
    latest=max(entries,key=lambda p:p.stat().st_mtime)
    # Only synthetic config and local QA logs; avoid propagating arbitrary environment.
    lines=latest.read_text(encoding="utf-8",errors="replace").splitlines()
    selected=[l for l in lines if any(t in l.lower() for t in
      ("record","encoder","video","fail","error","output","x264","mkv"))]
    return "\n".join(selected[-18:])[-2200:]

def obs_process_in_group(pgid):
    root=(ROOT/"tools/obs-studio-32.2.2").resolve(strict=True)
    matches=[]
    for entry in Path("/proc").iterdir():
        if not entry.name.isdecimal():
            continue
        pid=int(entry.name)
        try:
            if os.getpgid(pid)!=pgid:
                continue
            exe=(entry/"exe").resolve(strict=True)
            if exe.is_relative_to(root) and ("obs" in exe.name.lower()):
                matches.append((pid,str(exe)))
        except (PermissionError,ProcessLookupError,OSError):
            continue
    return sorted(matches)

def environment(work):
    for x in ("config","cache","data","run"):
        (work/x).mkdir(mode=0o700)
    env=os.environ.copy()
    for key in ("PYTHONPATH","PYTHONHOME","LD_PRELOAD","LD_LIBRARY_PATH"):
        env.pop(key,None)
    env.update({
       "HOME":str(work),"TMPDIR":str(work),
       "XDG_CONFIG_HOME":str(work/"config"),"XDG_DATA_HOME":str(work/"data"),
       "XDG_CACHE_HOME":str(work/"cache"),"XDG_RUNTIME_DIR":str(work/"run"),
       "QT_QPA_PLATFORM":"xcb","GDK_BACKEND":"x11",
       "LIBGL_ALWAYS_SOFTWARE":"1","OMP_NUM_THREADS":"2","PYTHONNOUSERSITE":"1",
       "GSETTINGS_BACKEND":"memory","SDL_AUDIODRIVER":"dummy",
       "PULSE_SERVER":"unix:/dev/null","PIPEWIRE_REMOTE":"ferrari-qa-no-audio",
       "ALSA_CONFIG_PATH":"/dev/null","DBUS_SESSION_BUS_ADDRESS":"unix:path=/dev/null",
       "HTTP_PROXY":"http://127.0.0.1:9","HTTPS_PROXY":"http://127.0.0.1:9",
       "ALL_PROXY":"socks5://127.0.0.1:9",
       "NO_PROXY":"localhost,127.0.0.1","no_proxy":"localhost,127.0.0.1"})
    return env

def probe_video(path,env,work):
    """Require decodable OBS frames AND a fully finalized playable private MP4."""
    ffmpeg=private_exe("ffmpeg")
    probe=ROOT/"tools/ubuntu-cli/bin/ffprobe"
    if not probe.is_file() or not os.access(probe,os.X_OK) or not probe.resolve(strict=True).is_relative_to(ROOT/"tools"):
        raise RuntimeError("F14_OBS_PRIVATE_FFPROBE_MISSING")

    def metadata(filename,timeout=45):
        proc=subprocess.run([str(probe),"-v","error","-count_frames","-show_entries",
            "format=duration,size:stream=codec_type,codec_name,width,height,nb_read_frames",
            "-of","json",str(filename)],capture_output=True,text=True,cwd=work,env=env,
            timeout=timeout,check=False)
        try:obj=json.loads(proc.stdout)
        except (ValueError,TypeError):obj={}
        tracks=[x for x in obj.get("streams",[]) if x.get("codec_type")=="video"]
        frames=0
        for t in tracks:
            try:frames+=int(t.get("nb_read_frames",0))
            except (ValueError,TypeError):pass
        try:seconds=float(obj.get("format",{}).get("duration"))
        except (TypeError,ValueError):seconds=0.0
        return {"exit":proc.returncode,"error":proc.stderr[-220:],
                "video_streams":len(tracks),"video_frames_decoded":frames,
                "duration_seconds":seconds,
                "width":int(tracks[0].get("width") or 0) if tracks else 0,
                "height":int(tracks[0].get("height") or 0) if tracks else 0,
                "bytes":filename.stat().st_size}

    source=metadata(path)
    report={"source_MKV":source,"source_mkv_sha256":digest(path),
            "native_obs_mkv_fully_finalized":source["duration_seconds"]>0 and not source["error"],
            "private_ffmpeg_postprocess":False}
    if source["exit"] or source["video_streams"]<1 or source["video_frames_decoded"]<8:
        report.update({"status":"not_certified","reason":"OBS_MKV_has_no_verified_decodable_video"})
        return report

    # The F14 r2 recording contained 398 actual frames but lost its
    # Matroska end metadata. Explicitly finalize a NEW video with
    # Ferrari's already-installed private FFmpeg (no fake OBS-native PASS).
    target=work/"ferrari-obs-finalized.mp4"
    proc=subprocess.run([ffmpeg,"-hide_banner","-nostdin","-loglevel","error",
         "-threads","2","-y","-fflags","+genpts","-i",str(path),
         "-map","0:v:0","-an","-t","30","-c:v","mpeg4","-q:v","5",
         "-pix_fmt","yuv420p","-movflags","+faststart",str(target)],
         cwd=work,env=env,capture_output=True,text=True,timeout=150,check=False)
    report["ffmpeg_exit"]=proc.returncode
    report["ffmpeg_diagnostic"]=proc.stderr[-280:]
    if proc.returncode or not target.is_file() or target.stat().st_size<3000:
        report.update({"status":"not_certified","reason":"private_ffmpeg_could_not_finalize_OBS_video"})
        return report
    final=metadata(target,timeout=55)
    report["final_MP4"]=final
    b=target.read_bytes()
    if (b[4:8]!=b"ftyp" or final["exit"] or final["error"] or
            final["video_streams"]!=1 or final["video_frames_decoded"]<8 or
            not (0.5<=final["duration_seconds"]<=30) or
            final["width"]<160 or final["height"]<90):
        report.update({"status":"not_certified","reason":"finalized_MP4_not_independently_validated"})
        return report
    report.update({"status":"pass","mode":"real_OBS_synthetic_video_followed_by_private_FFmpeg_MP4_finalization",
          "private_ffmpeg_postprocess":True,
          "final_mp4_sha256":digest(target),
          "final_mp4_bytes":target.stat().st_size,
          "final_duration_seconds":final["duration_seconds"],
          "final_decoded_video_frames":final["video_frames_decoded"],
          "camera_mic_desktop_streaming_disabled":True,
          "OBS_native_recording_completeness_not_claimed":True,
          "full_GUI_certified":False})
    return report

def attempt():
    guard()
    exe=private_exe("obs")
    private_exe("ffmpeg")
    xvfb=Path("/usr/bin/xvfb-run")
    if not xvfb.is_file() or not os.access(xvfb,os.X_OK):
        raise RuntimeError("F14_OBS_XVFB_ABSENT")
    with tempfile.TemporaryDirectory(prefix=".f14-obs-r2-",dir=ROOT/".runtime") as tmp:
        work=Path(tmp)
        env=environment(work)
        profile=work/"config/obs-studio/basic/profiles/FerrariSynthetic"
        scenes=work/"config/obs-studio/basic/scenes"
        profile.mkdir(parents=True)
        scenes.mkdir(parents=True)
        recorded=work/"recordings"
        recorded.mkdir(mode=0o700)
        (profile/"basic.ini").write_text(
            "[General]\nName=FerrariSynthetic\n"
            "[Video]\nBaseCX=320\nBaseCY=180\nOutputCX=320\nOutputCY=180\nFPSCommon=25\n"
            "[Output]\nMode=Simple\n"
            "[SimpleOutput]\nFilePath="+str(recorded)+"\nRecFormat2=mkv\n"
            "RecEncoder=obs_x264\nRecQuality=Small\n"
            "[Audio]\nSampleRate=48000\nChannelSetup=Stereo\n"
            "DesktopAudioDevice1=disabled\nDesktopAudioDevice2=disabled\n"
            "AuxAudioDevice1=disabled\nAuxAudioDevice2=disabled\n"
            "AuxAudioDevice3=disabled\nAuxAudioDevice4=disabled\n",
            encoding="utf-8")
        scene={"name":"FerrariSynthetic","current_scene":"FerrariSynthetic",
               "current_program_scene":"FerrariSynthetic",
               "sources":[{"name":"FerrariSynthetic","id":"scene",
                           "settings":{"items":[]}}],
               "groups":[],"scene_order":[{"name":"FerrariSynthetic"}],
               "transitions":[],"transition_duration":300,
               "quick_transitions":[],"modules":{}}
        (scenes/"FerrariSynthetic.json").write_text(json.dumps(scene),encoding="utf-8")
        # Synthetic blank scene, no device/network media. OBS only writes inside private temp HOME.
        p=subprocess.Popen([str(xvfb),"-a",
            "--server-args=-screen 0 640x480x24 -nolisten tcp",
            exe,"--profile","FerrariSynthetic","--collection","FerrariSynthetic",
            "--scene","FerrariSynthetic","--startrecording","--multi",
            "--disable-updater"],cwd=work,env=env,stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,start_new_session=True)
        signalled=None
        try:
            time.sleep(16)
            candidates=obs_process_in_group(p.pid)
            if candidates:
                # IMPORTANT: keep Xvfb alive while OBS flushes its own recording.
                obs_pid=candidates[-1][0]
                os.kill(obs_pid,signal.SIGINT)
                signalled="private_OBS_child_only_SIGINT"
            else:
                signalled="OBS_private_child_not_identified"
            try:
                out,err=p.communicate(timeout=13)
            except subprocess.TimeoutExpired:
                os.killpg(p.pid,signal.SIGTERM)
                try:out,err=p.communicate(timeout=4)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGKILL)
                    out,err=p.communicate(timeout=3)
        finally:
            if p.poll() is None:
                os.killpg(p.pid,signal.SIGKILL)
                p.wait(timeout=5)
        output_files=[x for x in recorded.rglob("*") if x.is_file() and not x.is_symlink()
                      and x.suffix.lower() in {".mkv",".mp4"}]
        if len(output_files)==1:
            result=probe_video(output_files[0],env,work)
        else:
            result={"status":"not_certified","reason":"expected_one_recording_file",
                    "recording_files_created":len(output_files)}
        result.update({"tool":"obs","signal_method":signalled,
                       "private_executable":exe,
                       "upstream_OBS_quit_log_excerpt":read_log(work),
                       "startup_exit":p.returncode,
                       "process_diagnostic":(err or out or b"").decode("utf-8","replace")[-350:],
                       "synthetic_blank_canvas_only":True,
                       "external_capture_or_stream_used":False})
    guard()
    return result

def main():
    try:
        before=services()
        result=attempt()
        after=services()
        if before!=after:
            raise RuntimeError("F14_OBS_PROTECTED_SERVICES_CHANGED")
        doc={"status":"audit_complete","tool":"obs",
            "observation":result,"protected_services":"8/8_PASS",
            "release":ACTIVE,"fallback":FALLBACK,"catalog_entries":458,
            "global_apt_modified":False,"other_projects_modified":False,
            "permanent_files_added":False,
            "recording_certified":result["status"]=="pass"}
        print(json.dumps(doc,sort_keys=True),flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc)[-650:],
                         "global_apt_modified":False,"other_projects_modified":False},sort_keys=True),flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
