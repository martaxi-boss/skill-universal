#!/usr/bin/env python3
"""Ferrari F9: fully project-scoped QGIS 4.2.3 from conda-forge with micromamba.

No Ubuntu APT install or reuse of global qgis. Only publishes an executable if
the real offscreen QGIS CLI and Python library smoke succeed. Conda package
cache and settings stay under /srv/projects/skill-universal/.runtime.
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
import tempfile
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
TOOLS = ROOT / "tools"
RUNTIME = ROOT / ".runtime"
VERSION = "4.2.3"
MAMBA_VERSION = "2.10.0-0"
MAMBA_URL = ("https://github.com/mamba-org/micromamba-releases/"
             "releases/download/2.10.0-0/micromamba-linux-64")
MAMBA_SHA256 = "701f39c06f8e6a670a0e186c8479b9e5c0502a2f0cda6cef65d83bdd2875e8bd"
MAMBA_SIZE = 19028608
MAMBA = TOOLS / "micromamba-2.10.0-0" / "micromamba"
MAMBA_ROOT = RUNTIME / "mamba-qgis"
TARGET = TOOLS / "qgis-4.2.3-condaforge"
PREFIX_BIN = TARGET / "bin/qgis_process"
MANIFEST = TARGET / "ferrari-manifest.json"

def require(ok: bool, message: str) -> None:
    if not ok:
        raise RuntimeError(message)

def guard() -> None:
    require(os.geteuid() != 0, "F9_QGIS_NO_ROOT")
    require(os.uname().machine == "x86_64", "F9_QGIS_ARCH_NOT_X86_64")
    os_release = Path("/etc/os-release").read_text(encoding="utf-8")
    require("ID=ubuntu" in os_release and 'VERSION_ID="24.04"' in os_release,
            "F9_QGIS_REQUIRES_UBUNTU_2404")
    require(ROOT.resolve(strict=True) == Path("/srv/projects/skill-universal"),
            "F9_QGIS_WRONG_PROJECT_ROOT")
    for directory in (ROOT, TOOLS, RUNTIME):
        require(directory.is_dir() and not directory.is_symlink(),
                "F9_QGIS_ROOT_NOT_PRIVATE:" + str(directory))
    for directory in (TARGET, MAMBA_ROOT, MAMBA.parent):
        require(not directory.is_symlink(), "F9_QGIS_UNSAFE_SYMLINK:" + str(directory))
    require(TARGET.parent.resolve(strict=True) == TOOLS.resolve(strict=True),
            "F9_QGIS_TARGET_OUTSIDE_FERRARI")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def check_mamba() -> None:
    require(MAMBA.is_file() and not MAMBA.is_symlink()
            and MAMBA.stat().st_size == MAMBA_SIZE
            and sha256(MAMBA) == MAMBA_SHA256
            and os.access(MAMBA, os.X_OK),
            "F9_QGIS_MAMBA_BINARY_SHA_MISMATCH")

def prepare_mamba() -> None:
    if MAMBA.exists() or MAMBA.is_symlink():
        check_mamba()
        return
    with tempfile.TemporaryDirectory(prefix=".f9-mamba-", dir=RUNTIME) as td:
        stage=Path(td)
        binary=stage/"micromamba"
        req=urllib.request.Request(MAMBA_URL,headers={"User-Agent":"Ferrari-QGIS-F9-checked"})
        digest=hashlib.sha256()
        size=0
        with urllib.request.urlopen(req,timeout=120) as src,binary.open("xb") as dst:
            while block:=src.read(1024*1024):
                size+=len(block)
                require(size<=MAMBA_SIZE,"F9_QGIS_MAMBA_OVERSIZED")
                dst.write(block)
                digest.update(block)
        require(size==MAMBA_SIZE and digest.hexdigest()==MAMBA_SHA256,
                "F9_QGIS_MAMBA_DOWNLOAD_SHA_MISMATCH")
        binary.chmod(0o700)
        require(not MAMBA.parent.exists(),"F9_QGIS_MAMBA_CONCURRENT_INSTALL")
        MAMBA.parent.mkdir(mode=0o700)
        try:
            os.replace(binary,MAMBA)
        except BaseException:
            MAMBA.parent.rmdir()
            raise
    check_mamba()

def env() -> dict:
    MAMBA_ROOT.mkdir(mode=0o700,exist_ok=True)
    for d in ("home","cache","pkgs","tmp","xdg"):
        (MAMBA_ROOT/d).mkdir(mode=0o700,exist_ok=True)
    result=os.environ.copy()
    result.update({
       "PATH":"/usr/bin:/bin",
       "HOME":str(MAMBA_ROOT/"home"),
       "XDG_CONFIG_HOME":str(MAMBA_ROOT/"home"),
       "XDG_CACHE_HOME":str(MAMBA_ROOT/"cache"),
       "MAMBA_ROOT_PREFIX":str(MAMBA_ROOT),
       "CONDA_PKGS_DIRS":str(MAMBA_ROOT/"pkgs"),
       "MAMBA_NO_BANNER":"1",
       "MAMBA_CHANNEL_PRIORITY":"strict",
       "MAMBA_ROOT_ENVIRONMENT":str(MAMBA_ROOT),
       "TMPDIR":str(MAMBA_ROOT/"tmp"),
       "QT_QPA_PLATFORM":"offscreen",
       "XDG_RUNTIME_DIR":str(MAMBA_ROOT/"xdg"),
       "QGIS_PREFIX_PATH":str(TARGET),
       "QGIS_CUSTOM_CONFIG_PATH":str(MAMBA_ROOT/"home"),
       "PYTHONNOUSERSITE":"1",
    })
    lib=TARGET/"lib"
    result["LD_LIBRARY_PATH"]=str(lib) if lib.is_dir() else ""
    return result

def execute(cmd: list[str],timeout: int=90,environment: dict|None=None) -> subprocess.CompletedProcess:
    require(all(isinstance(x,str) for x in cmd), "F9_QGIS_BAD_CMD")
    return subprocess.run(cmd,env=environment or env(),capture_output=True,text=True,
                          timeout=timeout,check=False)

def conda_args(dry_run: bool) -> list[str]:
    cmd=[str(MAMBA),"--no-rc","create","--yes","--prefix",str(TARGET),
         "--override-channels","--channel","conda-forge",
         "--strict-channel-priority","qgis="+VERSION,"python=3.12"]
    if dry_run:
        cmd+=["--dry-run","--json"]
    return cmd

def preview() -> dict:
    guard()
    prepare_mamba()
    result=execute(conda_args(True),timeout=420)
    require(result.returncode==0,"F9_QGIS_CONDA_SOLVE_FAILED:"+
            (result.stderr or result.stdout)[-350:])
    data=json.loads(result.stdout)
    require(data.get("success") is not False,"F9_QGIS_SOLVE_REPORTED_FAILURE")
    actions=data.get("actions") or {}
    fetch=actions.get("FETCH") or []
    size=sum(int(item.get("size") or 0) for item in fetch if isinstance(item,dict))
    require(size<5*1024**3,"F9_QGIS_DOWNLOAD_BUDGET_OVER_5GB")
    return {"status":"solved","version":VERSION,"channel":"conda-forge",
            "packages_to_fetch":len(fetch),"estimated_download_bytes":size,
            "no_ubuntu_packages_modified":True}

def qgis_package() -> dict:
    meta=TARGET/"conda-meta"
    require(meta.is_dir() and not meta.is_symlink(),"F9_QGIS_CONDA_META_MISSING")
    choices=list(meta.glob("qgis-"+VERSION+"-*.json"))
    require(len(choices)==1,"F9_QGIS_VERSION_NOT_PINNED")
    info=json.loads(choices[0].read_text(encoding="utf-8"))
    require(info.get("name")=="qgis" and info.get("version")==VERSION and
            "gpl" in str(info.get("license","")).lower(),
            "F9_QGIS_OPEN_SOURCE_LICENSE_OR_VERSION_MISMATCH")
    return {"version":VERSION,"license":info.get("license"),
            "build":info.get("build_string"),"url":info.get("url","")}

def smoke() -> dict:
    require(PREFIX_BIN.is_file() and not PREFIX_BIN.is_symlink()
            and PREFIX_BIN.resolve(strict=True).is_relative_to(TARGET.resolve(strict=True)),
            "F9_QGIS_PRIVATE_PROCESS_BINARY_MISSING")
    require((TARGET/"bin/python").is_file(),"F9_QGIS_PRIVATE_PYTHON_MISSING")
    package=qgis_package()
    environment=env()
    cli=execute([str(PREFIX_BIN),"--no-python","--version"],timeout=120,environment=environment)
    detail=(cli.stdout+"\n"+cli.stderr)[-2400:]
    require(cli.returncode==0 and VERSION in detail,
            "F9_QGIS_PRIVATE_CLI_VERSION_SMOKE_FAILED:"+detail[-240:])
    py=execute([str(TARGET/"bin/python"),"-c",
                "from qgis.core import QgsApplication; print('F9_PRIVATE_QGIS_PYTHON_IMPORT=PASS')"],
               timeout=120,environment=environment)
    require(py.returncode==0 and "F9_PRIVATE_QGIS_PYTHON_IMPORT=PASS" in py.stdout,
            "F9_QGIS_PYTHON_IMPORT_FAILED:"+(py.stderr or py.stdout)[-350:])
    link=execute(["/usr/bin/ldd",str(PREFIX_BIN)],timeout=30,environment=environment)
    require(link.returncode==0 and "not found" not in link.stdout,
            "F9_QGIS_LDD_NOT_RESOLVED")
    qgis_libs=[x.strip() for x in link.stdout.splitlines() if "libqgis_" in x]
    require(qgis_libs and all(str(TARGET) in x for x in qgis_libs),
            "F9_QGIS_LINKED_TO_GLOBAL_QGIS_LIBRARY")
    return {"cli_version_certified":True,"python_qgis_import_certified":True,
            "private_qgis_libraries_loaded":True,"license":package["license"],
            "gui_runtime_certified":False}

def check() -> dict:
    guard()
    check_mamba()
    require(TARGET.is_dir() and not TARGET.is_symlink(),"F9_QGIS_INSTALL_MISSING")
    manifest=json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest.get("qgis_version")==VERSION and
            manifest.get("micromamba_version")==MAMBA_VERSION and
            manifest.get("mamba_sha256")==MAMBA_SHA256 and
            manifest.get("channel")=="conda-forge",
            "F9_QGIS_INSTALL_MANIFEST_MISMATCH")
    evidence=smoke()
    return {"status":"private_qgis_core_certified","root":str(TARGET),
            "version":VERSION,**evidence,"global_apt_changed":False}

def install() -> dict:
    guard()
    if TARGET.exists():
        return check()
    preview_info=preview()
    stat=os.statvfs(RUNTIME)
    require(stat.f_bavail*stat.f_frsize >= 9*1024**3,
            "F9_QGIS_NOT_ENOUGH_DISK")
    require(not TARGET.exists() and not TARGET.is_symlink(),
            "F9_QGIS_CONCURRENT_INSTALL")
    try:
        result=execute(conda_args(False),timeout=1800)
        require(result.returncode==0,
                "F9_QGIS_PRIVATE_CONDA_INSTALL_FAILED:"+
                (result.stderr or result.stdout)[-350:])
        evidence=smoke()
        manifest={"qgis_version":VERSION,"micromamba_version":MAMBA_VERSION,
                  "mamba_sha256":MAMBA_SHA256,"channel":"conda-forge",
                  "package_count":len(list((TARGET/"conda-meta").glob("*.json"))),
                  "estimated_download_bytes":preview_info["estimated_download_bytes"],
                  "runtime_check":evidence,"no_global_apt_install":True}
        MANIFEST.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
        return check()
    except BaseException:
        if TARGET.is_dir() and not TARGET.is_symlink() and
                TARGET.resolve(strict=True).is_relative_to(TOOLS.resolve(strict=True)):
            shutil.rmtree(TARGET)
        raise

def main() -> int:
    parser=argparse.ArgumentParser()
    options=parser.add_mutually_exclusive_group(required=True)
    options.add_argument("--preview",action="store_true")
    options.add_argument("--install",action="store_true")
    options.add_argument("--check",action="store_true")
    args=parser.parse_args()
    try:
        data=preview() if args.preview else install() if args.install else check()
        print(json.dumps(data,sort_keys=True),flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)[-500:],
                          "global_apt_changed":False},sort_keys=True),flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
