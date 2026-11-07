#!/usr/bin/env python3
"""Final Ferrari-only acceptance: read-only installation check + bounded synthetic OBS QA."""
import json, os, signal, subprocess, sys, tempfile, time
from pathlib import Path

ROOT=Path("/srv/projects/skill-universal")
CURRENT="205c6f0e970259c79fa2111b6670c2fe1672fb27"
FALLBACK="7bf6dcecf15da26502c5969b5eee54d5e116fc32"
LEGACY="952b0a75ba798471b07053677d53791bd078ed56"
OLD=("tool_actions.json","ubuntu_selection.json","providers.json",
     "ferrari_registry.json","ferrari_expansion.json")
PACKAGES=("yt-dlp","librecad","qgis","audacity","obs-studio",
          "solvespace","synfigstudio","openshot-qt")
OBS=ROOT/"tools/obs-studio-32.2.2/run-obs"
FFPROBE=ROOT/"tools/ubuntu-cli/bin/ffprobe"

def require(ok, reason):
    if not ok: raise RuntimeError(reason)

def call(args, env=None, seconds=24):
    try:
        p=subprocess.run([str(x) for x in args],capture_output=True,
                         text=True,env=env,timeout=seconds,check=False)
        return p.returncode,(p.stdout+p.stderr)[-600:]
    except (subprocess.TimeoutExpired,OSError) as exc:
        return None,type(exc).__name__

def catalog_check():
    require(os.geteuid()!=0,"final_nonroot_only")
    for name in ("releases","tools",".runtime","runtimes"):
        p=ROOT/name
        require(p.is_dir() and not p.is_symlink(),"unsafe_project_path_"+name)
    require((ROOT/"current").is_symlink() and
            (ROOT/"current").resolve(strict=True)==ROOT/"releases"/CURRENT,
            "active_release_changed")
    require(not (ROOT/"releases"/LEGACY).exists(),"old_catalog_release_present")
    for r in (CURRENT,FALLBACK):
        folder=ROOT/"releases"/r/"engine"
        require((folder/"ferrari.py").is_file(),"engine_missing_"+r[:8])
        require(not any((folder/n).exists() for n in OLD),"old_manifest_present")
        c=json.loads((folder/"catalog.json").read_text())
        require((len(c["tools"]),len(c["functions"]),len(c["dependencies"]),
                 len(c["providers"]),c["counts"]["all_catalog_entries"])==
                (173,272,3,2,450),"catalog_not_universal")
    return {"active":CURRENT,"fallback":FALLBACK,"catalog_entries":450,
            "old_catalog_release_removed":True,"old_manifest_count":0}

def private_inventory():
    sys.path.insert(0,str(ROOT/"current"))
    from engine import tool_runtime
    d=tool_runtime.inventory()
    require(d["selected"]==55 and d["selected_detected"]==55,
            "selected_ubuntu_tools_missing")
    require(d["registered_actions"]==40 and d["callable_actions"]>=40,
            "private_actions_missing")
    return {"selected_detected":d["selected_detected"],
            "registered_actions":d["registered_actions"],
            "callable_actions":d["callable_actions"],
            "installed_detected":d["installed"]}

def apt_audit():
    seen=[]
    for name in PACKAGES:
        rc,out=call(("/usr/bin/dpkg-query","-W",name),seconds=8)
        # APT package existence is not equivalent to active dpkg installation.
        if rc==0:
            status_rc,status=call(("/usr/bin/dpkg-query","-s",name),seconds=8)
            if status_rc==0 and "Status: install ok installed" in status:
                seen.append(name)
    require(not seen,"legacy_global_apt_installed")
    return {"packages_checked":len(PACKAGES),"legacy_installed":seen}

def obs_qa():
    require(OBS.is_file() and os.access(OBS,os.X_OK) and
            OBS.resolve(strict=True).is_relative_to((ROOT/"tools").resolve(strict=True)),
            "obs_private_launcher_missing")
    with tempfile.TemporaryDirectory(prefix=".final-obs-",dir=ROOT/".runtime") as td:
        work=Path(td)
        for d in ("home","config","cache","data","run","recordings"):
            (work/d).mkdir(mode=0o700)
        env={k:v for k,v in os.environ.items()
             if k not in ("LD_LIBRARY_PATH","PYTHONPATH","QT_PLUGIN_PATH")}
        env.update({"HOME":str(work/"home"),"TMPDIR":str(work),
            "XDG_CONFIG_HOME":str(work/"config"),
            "XDG_CACHE_HOME":str(work/"cache"),
            "XDG_DATA_HOME":str(work/"data"),
            "XDG_RUNTIME_DIR":str(work/"run"),
            "QT_QPA_PLATFORM":"xcb","LIBGL_ALWAYS_SOFTWARE":"1",
            "PYTHONNOUSERSITE":"1","OMP_NUM_THREADS":"2",
            "HTTP_PROXY":"http://127.0.0.1:9",
            "HTTPS_PROXY":"http://127.0.0.1:9",
            "ALL_PROXY":"socks5://127.0.0.1:9",
            "NO_PROXY":"127.0.0.1,localhost"})
        rc,out=call((OBS,"--version"),env,30)
        version_ok=rc==0 and "32.2.2" in out
        result={"private_obs_version_ok":version_ok,
                "obs_local_recording_certified":False,
                "obs_interactive_gui_certified":False,
                "obs_streaming_attempted":False,
                "temp_files_deleted":True}
        if not version_ok:
            result["reason"]="obs_version_failed"
            return result
        xvfb=Path("/usr/bin/xvfb-run")
        if not (xvfb.is_file() and os.access(xvfb,os.X_OK)):
            result["reason"]="xvfb_qa_absent"
            return result
        profile=work/"config/obs-studio/basic/profiles/FerrariQA"
        profile.mkdir(parents=True,mode=0o700)
        (work/"config/obs-studio/global.ini").write_text(
            "[General]\nFirstRun=false\n[Basic]\nProfile=FerrariQA\nProfileDir=FerrariQA\n")
        (profile/"basic.ini").write_text(
            "[General]\nName=FerrariQA\n[Video]\nBaseCX=320\nBaseCY=180\n"
            "OutputCX=320\nOutputCY=180\nFPSType=0\nFPSCommon=10\n"
            "[Output]\nMode=Simple\n[SimpleOutput]\n"
            f"FilePath={work/'recordings'}\n"
            "RecFormat2=mkv\nRecQuality=Stream\nRecEncoder=x264\n"
            "VBitrate=500\nPreset=ultrafast\n"
            "[Audio]\nDesktopDevice1=disabled\nDesktopDevice2=disabled\n"
            "AuxDevice1=disabled\nAuxDevice2=disabled\n")
        cmd=[str(xvfb),"-a","--server-args=-screen 0 640x480x24 -nolisten tcp",
             str(OBS),"--multi","--safe-mode","--startrecording",
             "--disable-shutdown-check","--disable-missing-files-check"]
        p=subprocess.Popen(cmd,cwd=work,env=env,stdin=subprocess.DEVNULL,
                           stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,
                           start_new_session=True)
        try:
            start=time.monotonic()
            while time.monotonic()-start<16 and p.poll() is None:
                time.sleep(1)
        finally:
            for sig,seconds in ((signal.SIGINT,5),(signal.SIGTERM,3),
                                (signal.SIGKILL,3)):
                if p.poll() is not None: break
                try: os.killpg(p.pid,sig)
                except ProcessLookupError: pass
                try: p.wait(timeout=seconds)
                except subprocess.TimeoutExpired: pass
            if p.poll() is None: p.kill(); p.wait(timeout=3)
        files=[f for f in (work/"recordings").iterdir()
               if f.is_file() and f.suffix in (".mkv",".mp4")
               and 300<f.stat().st_size<24*1024*1024]
        result["recording_files_created"]=len(files)
        if files and FFPROBE.is_file():
            rc,info=call((FFPROBE,"-v","error","-select_streams","v:0",
                          "-show_entries","stream=codec_name,width,height",
                          "-of","json",files[0]),env,20)
            try:
                streams=json.loads(info).get("streams",[]) if rc==0 else []
                if streams and int(streams[0].get("width",0))>=160:
                    result["obs_local_recording_certified"]=True
                    result["recorded_codec"]=streams[0].get("codec_name")
                    result["recorded_bytes"]=files[0].stat().st_size
            except (ValueError,KeyError,TypeError): pass
        result["reason"]=("synthetic_blank_recording_verified" if
                          result["obs_local_recording_certified"] else
                          "headless_recording_not_confirmed")
        return result

def main():
    if sys.argv[1:]!=["--audit"]:
        raise SystemExit("final_audit_only")
    try:
        c=catalog_check()
        inv=private_inventory()
        a=apt_audit()
        obs=obs_qa()
        require((ROOT/"current").resolve(strict=True)==ROOT/"releases"/CURRENT,
                "active_release_changed_during_audit")
        print(json.dumps({"status":"PASS","installation_certified":True,
            "catalog":c,"inventory":inv,"global_legacy_packages":a,"obs":obs,
            "all_optional_formats_certified":False,
            "all_gui_editing_certified":False,
            "global_apt_modified":False,"other_projects_modified":False,
            "catalog_modified":False},sort_keys=True),flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status":"BLOCKED","reason":str(exc)[-300:],
                          "global_apt_modified":False,
                          "other_projects_modified":False}),flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
