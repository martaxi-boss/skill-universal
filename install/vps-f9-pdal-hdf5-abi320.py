#!/usr/bin/env python3
"""F9 Ferrari: private, reversible HDF5 2.x ABI-320 sidecar for optional PDAL.

The existing QGIS conda prefix is READ-ONLY. No global apt/pip installations,
no symlink alias between ABI 310 and 320, no other projects. Sidecar only
becomes certified after verifying both optional plugin ELF dependency chains.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT=Path("/srv/projects/skill-universal")
TOOLS=ROOT/"tools"
RUNTIME=ROOT/".runtime"
CURRENT=ROOT/"current"
EXPECTED="7bf6dcecf15da26502c5969b5eee54d5e116fc32"
FALLBACK="952b0a75ba798471b07053677d53791bd078ed56"
QGIS=TOOLS/"qgis-4.2.3-condaforge"
SIDECAR=TOOLS/"pdal-hdf5-2.2.0-abi320"
MAMBA=TOOLS/"micromamba-2.10.0-0"/"micromamba"
MAMBA_SIZE=19028608
MAMBA_SHA256="701f39c06f8e6a670a0e186c8479b9e5c0502a2f0cda6cef65d83bdd2875e8bd"
MAMBA_ROOT=RUNTIME/"mamba-qgis"
HDF5_VERSION="2.2.0"
MANIFEST=SIDECAR/"ferrari-hdf5-sidecar.json"
PLUGINS=("libpdal_plugin_reader_hdf.so","libpdal_plugin_reader_icebridge.so")
MAX_DOWNLOAD_BYTES=800_000_000

def require(value:bool,why:str)->None:
    if not value:
        raise RuntimeError(why)

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def guard()->None:
    require(os.geteuid()!=0,"F9_SIDECAR_NONROOT_ONLY")
    for p in (ROOT,TOOLS,RUNTIME,QGIS,MAMBA_ROOT):
        require(p.is_dir() and not p.is_symlink(),"F9_SIDECAR_UNSAFE_ROOT")
    require(CURRENT.is_symlink() and
            CURRENT.resolve(strict=True)==ROOT/"releases"/EXPECTED,
            "F9_SIDECAR_ACTIVE_RELEASE_DRIFT")
    require((ROOT/"releases"/FALLBACK/"engine/ferrari.py").is_file(),
            "F9_SIDECAR_FALLBACK_MISSING")
    d=json.loads((CURRENT/"engine/catalog.json").read_text(encoding="utf-8"))
    require(d["counts"]["all_catalog_entries"]==450
            and len(d["tools"])==173 and len(d["functions"])==272,
            "F9_SIDECAR_CATALOG_DRIFT")
    require(MAMBA.is_file() and not MAMBA.is_symlink()
            and MAMBA.stat().st_size==MAMBA_SIZE
            and digest(MAMBA)==MAMBA_SHA256,
            "F9_SIDECAR_PINNED_MICROMAMBA_MISMATCH")
    require(SIDECAR.parent.resolve(strict=True)==TOOLS.resolve(strict=True)
            and not SIDECAR.is_symlink(),"F9_SIDECAR_TARGET_UNSAFE")
    require((QGIS/"bin/python").is_file(),"F9_SIDECAR_QGIS_MISSING")

def private_env()->dict[str,str]:
    # Existing project-scoped micromamba cache; no second install of the tool.
    for name in ("home","tmp","cache","pkgs","xdg"):
        path=MAMBA_ROOT/name
        path.mkdir(parents=True,exist_ok=True,mode=0o700)
    d={k:v for k,v in os.environ.items()
       if k not in {"LD_LIBRARY_PATH","PYTHONPATH","QT_PLUGIN_PATH"}}
    d.update({
        "PATH":"/usr/bin:/bin","HOME":str(MAMBA_ROOT/"home"),
        "XDG_CACHE_HOME":str(MAMBA_ROOT/"cache"),
        "XDG_CONFIG_HOME":str(MAMBA_ROOT/"home"),
        "XDG_RUNTIME_DIR":str(MAMBA_ROOT/"xdg"),
        "MAMBA_ROOT_PREFIX":str(MAMBA_ROOT),
        "MAMBA_ROOT_ENVIRONMENT":str(MAMBA_ROOT),
        "CONDA_PKGS_DIRS":str(MAMBA_ROOT/"pkgs"),
        "MAMBA_NO_BANNER":"1",
        "TMPDIR":str(MAMBA_ROOT/"tmp"),
        "QT_QPA_PLATFORM":"offscreen",
        "PYTHONNOUSERSITE":"1",
        "LD_LIBRARY_PATH":str(QGIS/"lib"),
        "HTTP_PROXY":os.environ.get("HTTP_PROXY",""),
    })
    return d

def conda_command(dry_run:bool)->list[str]:
    cmd=[str(MAMBA),"--no-rc","create","--yes","--prefix",str(SIDECAR),
         "--override-channels","--channel","conda-forge",
         "hdf5="+HDF5_VERSION]
    if dry_run:
        cmd.extend(("--dry-run","--json"))
    return cmd

def execute(argv:list[str],environment:dict,timeout:int)->subprocess.CompletedProcess:
    return subprocess.run(argv,check=False,capture_output=True,text=True,
                          env=environment,timeout=timeout)

def preview()->dict:
    guard()
    require(not SIDECAR.exists(),"F9_SIDECAR_ALREADY_EXISTS")
    env=private_env()
    result=execute(conda_command(True),env,420)
    require(result.returncode==0,"F9_SIDECAR_SOLVE_FAILED:"+
            (result.stderr or result.stdout)[-400:])
    try:
        data=json.loads(result.stdout)
    except ValueError as exc:
        raise RuntimeError("F9_SIDECAR_SOLVE_NOT_JSON") from exc
    require(data.get("success") is not False,"F9_SIDECAR_SOLVE_REPORTED_FAILURE")
    actions=data.get("actions") or {}
    link=actions.get("LINK") or []
    fetch=actions.get("FETCH") or []
    require(any(isinstance(x,dict) and x.get("name")=="hdf5"
                and x.get("version")==HDF5_VERSION for x in link),
            "F9_SIDECAR_NO_PINNED_HDF5")
    count=len(link)
    bytes_=sum(int(x.get("size") or 0) for x in fetch if isinstance(x,dict))
    require(1<=count<=70 and bytes_<=MAX_DOWNLOAD_BYTES,
            "F9_SIDECAR_SOLVE_OVER_BUDGET")
    return {"status":"preview_pass","hdf5_version":HDF5_VERSION,
            "conda_link_packages":count,"download_bytes_estimate":bytes_,
            "sidecar_prefix":str(SIDECAR),"qgis_existing_prefix_untouched":True,
            "abi_310_not_aliased_to_320":True,
            "apt_modified":False,"other_projects_modified":False}

def hdf5_files()->dict[str,bool]:
    lib=SIDECAR/"lib"
    require(lib.is_dir() and not lib.is_symlink(),"F9_SIDECAR_LIB_DIR_MISSING")
    output={}
    for name in ("libhdf5_cpp.so.320","libhdf5.so.320"):
        p=lib/name
        output[name]=p.is_file() and p.resolve(strict=True).is_relative_to(SIDECAR)
    return output

def private_plugin_loader()->dict:
    lib=QGIS/"lib"
    environment=private_env()
    environment["LD_LIBRARY_PATH"]=str(SIDECAR/"lib")+":"+str(lib)
    details={}
    for name in PLUGINS:
        p=lib/name
        require(p.is_file() and p.resolve(strict=True).is_relative_to(QGIS),
                "F9_SIDECAR_QGIS_PLUGIN_MISSING:"+name)
        r=execute(["/usr/bin/ldd",str(p)],environment,35)
        unresolved=sorted(set(re.findall(r"([A-Za-z0-9_.+-]+)\s+=>\s+not found",
                                         r.stdout+"\n"+r.stderr)))
        details[name]={"linked":r.returncode==0 and not unresolved,
                       "unresolved_sonames":unresolved,
                       "direct_hdf5_cpp_320_resolved":(
                           "libhdf5_cpp.so.320 => "+str(SIDECAR/"lib")
                           in r.stdout),
                       "host_system_not_modified":True}
    return details

def verify_existing_qgis_core()->bool:
    e=private_env()
    e["LD_LIBRARY_PATH"]=str(QGIS/"lib")
    pythonpath=[QGIS/"share/qgis/python",QGIS/"share/qgis/python/plugins"]
    e["PYTHONPATH"]=":".join(str(p) for p in pythonpath if p.is_dir())
    code=("from qgis.core import QgsGeometry; "
          "x=QgsGeometry.fromWkt('POLYGON((0 0,100 0,100 50,0 50,0 0))'); "
          "assert x.isGeosValid() and abs(x.area()-5000)<0.1; "
          "print('FERRARI_ORIGINAL_QGIS_CORE=PASS')")
    r=execute([str(QGIS/"bin/python"),"-B","-c",code],e,40)
    return r.returncode==0 and "FERRARI_ORIGINAL_QGIS_CORE=PASS" in r.stdout

def check()->dict:
    guard()
    require(SIDECAR.is_dir() and not SIDECAR.is_symlink(),
            "F9_SIDECAR_NOT_INSTALLED")
    require(MANIFEST.is_file() and not MANIFEST.is_symlink(),
            "F9_SIDECAR_MANIFEST_MISSING")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("hdf5_version")==HDF5_VERSION and
            manifest.get("mamba_sha256")==MAMBA_SHA256,
            "F9_SIDECAR_PROVENANCE_MISMATCH")
    checked=hdf5_files()
    require(all(checked.values()),"F9_SIDECAR_REQUIRED_ABI_NOT_FOUND")
    plugins=private_plugin_loader()
    require(all(x["linked"] and x["direct_hdf5_cpp_320_resolved"]
                for x in plugins.values()),"F9_SIDECAR_OPTIONAL_PLUGINS_NOT_LINKED")
    require(verify_existing_qgis_core(),"F9_SIDECAR_QGIS_ORIGINAL_REGRESSION")
    return {"status":"private_sidecar_loader_pass",
            "hdf5_version":HDF5_VERSION,"required_files":checked,
            "pdal_plugin_linker":plugins,
            "original_qgis_core_pass":True,
            "full_pdal_formats_certified":False,"gui_certified":False,
            "qgis_existing_prefix_untouched":True,
            "global_apt_changed":False,"other_projects_changed":False}

def install()->dict:
    guard()
    require(not SIDECAR.exists() and not SIDECAR.is_symlink(),
            "F9_SIDECAR_EXISTS_OR_CONCURRENT")
    plan=preview()
    fs=os.statvfs(RUNTIME)
    require(fs.f_bavail*fs.f_frsize >= 3*1024**3,
            "F9_SIDECAR_INSUFFICIENT_PRIVATE_DISK")
    created=False
    try:
        env=private_env()
        result=execute(conda_command(False),env,900)
        created=SIDECAR.is_dir()
        require(result.returncode==0,
                "F9_SIDECAR_PRIVATE_INSTALL_FAILED:"+
                (result.stderr or result.stdout)[-320:])
        checked=hdf5_files()
        require(all(checked.values()),"F9_SIDECAR_ABI_320_MISSING")
        plugins=private_plugin_loader()
        require(all(x["linked"] and x["direct_hdf5_cpp_320_resolved"]
                    for x in plugins.values()),"F9_SIDECAR_PLUGIN_LINKER_FAIL")
        require(verify_existing_qgis_core(),"F9_SIDECAR_BASE_QGIS_REGRESSION")
        manifest={"hdf5_version":HDF5_VERSION,
                  "mamba_sha256":MAMBA_SHA256,
                  "channel":"conda-forge",
                  "requested_prefix":str(SIDECAR),
                  "qgis_original_prefix":str(QGIS),
                  "download_budget":plan["download_bytes_estimate"],
                  "binary_sonames_verified":True}
        MANIFEST.write_text(json.dumps(manifest,sort_keys=True)+"\n",
                            encoding="utf-8")
        return check()
    except BaseException:
        # Rollback ONLY this new uniquely named prefix, no package/global cleanups.
        if (created and SIDECAR.is_dir() and not SIDECAR.is_symlink()
                and SIDECAR.resolve(strict=True).is_relative_to(TOOLS.resolve(strict=True))):
            shutil.rmtree(SIDECAR)
        raise

def main()->int:
    parser=argparse.ArgumentParser()
    opts=parser.add_mutually_exclusive_group(required=True)
    opts.add_argument("--preview",action="store_true")
    opts.add_argument("--install",action="store_true")
    opts.add_argument("--check",action="store_true")
    args=parser.parse_args()
    try:
        d=preview() if args.preview else install() if args.install else check()
        print(json.dumps(d,sort_keys=True),flush=True)
        return 0
    except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)[-400:],
                          "global_apt_changed":False,
                          "other_projects_changed":False},sort_keys=True),
              flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
