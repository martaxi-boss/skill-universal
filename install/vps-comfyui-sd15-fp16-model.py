#!/usr/bin/env python3
"""Ferrari-only locked SD 1.5 fp16 SafeTensors, ComfyUI v0.43.0 compatible.

Exactly three approved weight paths, pinned upstream commit and SHA256. No apt,
pip, symlinks, external scripts or changes outside the Ferrari project tree.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import urllib.request

ROOT=Path("/srv/projects/skill-universal")
COMFY=ROOT/"tools/comfyui-v0.43.0"
VENV=ROOT/".runtime/venvs/extended/comfyui"
PARENT=COMFY/"models/diffusers"
DEST=PARENT/"sd15-fp16-f03de327"
REV="f03de327dd89b501a01da37fc5240cf4fdba85a1"
SRC="https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/resolve/"+REV+"/"
WEIGHTS={
  "unet/diffusion_pytorch_model.fp16.safetensors":("c83908253f9a64d08c25fc90874c9c8aef9a329ce1ca5fb909d73b0c83d1ea21",1_800_000_000),
  "text_encoder/model.fp16.safetensors":("77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e",280_000_000),
  "vae/diffusion_pytorch_model.fp16.safetensors":("4fbcf0ebe55a0984f5a5e00d8c4521d52359af7229bb4d81890039d2aa16dd7c",190_000_000),
}
CONFIGS=("model_index.json","unet/config.json","vae/config.json","text_encoder/config.json")

def inside(path:Path,existing:bool=False):
    base=ROOT.resolve(strict=True)
    if not path.resolve(strict=existing).is_relative_to(base):
        raise RuntimeError("FERRARI_COMFY_SD15_PATH_ESCAPES_PROJECT")
    q=path
    while q!=ROOT:
        if q.is_symlink():
            raise RuntimeError("FERRARI_COMFY_SD15_LINK_REJECTED")
        q=q.parent

def preflight():
    if ROOT.is_symlink() or not ROOT.is_dir() or ROOT.stat().st_uid!=os.getuid():
        raise RuntimeError("FERRARI_COMFY_SD15_INVALID_OWNER")
    for p in (COMFY,COMFY/"main.py",VENV):
        inside(p,existing=True)
    if not (VENV/"bin/python").is_file() or not (VENV/"bin/python").resolve(strict=True).is_relative_to(ROOT.resolve()):
        raise RuntimeError("FERRARI_COMFY_SD15_PRIVATE_PYTHON_MISSING")
    if shutil.disk_usage(ROOT).free < 7*1024**3:
        raise RuntimeError("FERRARI_COMFY_SD15_DISK_HEADROOM_INSUFFICIENT")
    mem={}
    for s in Path("/proc/meminfo").read_text().splitlines():
        k,v=s.split(":",1)
        if k in ("MemTotal","MemAvailable"):mem[k]=int(v.split()[0])*1024
    if mem.get("MemTotal",0)<7*1024**3 or mem.get("MemAvailable",0)<3*1024**3:
        raise RuntimeError("FERRARI_COMFY_SD15_RAM_HEADROOM_INSUFFICIENT")
    inside(PARENT)
    print("FERRARI_COMFY_SD15_PRIVATE_PREFLIGHT=PASS",flush=True)

def digest(path:Path)->str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b""):
            h.update(chunk)
    return h.hexdigest()

def verify(dest:Path)->bool:
    if not dest.is_dir() or dest.is_symlink():return False
    try:
        for name,(sha,upper) in WEIGHTS.items():
            f=dest/name;inside(f,existing=True)
            if not f.is_file() or f.is_symlink() or not 1_000_000<f.stat().st_size<upper:return False
            if digest(f)!=sha:return False
        for name in CONFIGS:
            f=dest/name;inside(f,existing=True)
            if not f.is_file() or f.is_symlink() or not 10<f.stat().st_size<60_000:return False
            json.loads(f.read_text(encoding="utf-8"))
    except (OSError,ValueError,RuntimeError):
        return False
    return True

def fetch(name:str, dest:Path, expected:str|None, limit:int):
    if name not in WEIGHTS and name not in CONFIGS:
        raise ValueError("Unapproved model path")
    dest.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    inside(dest)
    req=urllib.request.Request(SRC+name,headers={"User-Agent":"Ferrari-Private-ComfyUI/1.0"})
    h=hashlib.sha256();size=0
    print("FERRARI_COMFY_SD15_DOWNLOAD_START="+name,flush=True)
    with urllib.request.urlopen(req,timeout=90) as response, dest.open("xb") as f:
        for b in iter(lambda:response.read(2*1024*1024),b""):
            size+=len(b)
            if size>limit:raise RuntimeError("FERRARI_COMFY_SD15_DOWNLOAD_LIMIT")
            h.update(b); f.write(b)
    if expected is not None:
        if h.hexdigest()!=expected or size<1_000_000:raise RuntimeError("FERRARI_COMFY_SD15_SHA256_MISMATCH="+name)
    else:json.loads(dest.read_text(encoding="utf-8"))
    print("FERRARI_COMFY_SD15_FILE_VERIFIED="+name+" bytes="+str(size),flush=True)

def main():
    ap=argparse.ArgumentParser()
    actions=ap.add_mutually_exclusive_group(required=True)
    actions.add_argument("--apply",action="store_true")
    actions.add_argument("--check",action="store_true")
    args=ap.parse_args()
    preflight()
    if args.check:
        if not verify(DEST):raise RuntimeError("FERRARI_COMFY_SD15_NOT_INSTALLED_OR_HASH_MISMATCH")
        print("FERRARI_COMFY_SD15=PASS_PRIVATE_SHA256",flush=True)
        return 0
    if verify(DEST):
        print("FERRARI_COMFY_SD15=PASS_REUSE",flush=True)
        return 0
    if DEST.exists() or DEST.is_symlink():
        raise RuntimeError("FERRARI_COMFY_SD15_EXISTING_PATH_CONFLICT")
    PARENT.mkdir(mode=0o700,parents=True,exist_ok=True)
    inside(PARENT,existing=True)
    stage=Path(tempfile.mkdtemp(prefix=".ferrari-sd15-stage-",dir=PARENT))
    inside(stage,existing=True)
    try:
        for name in CONFIGS:fetch(name,stage/name,None,60_000)
        for name,(sha,limit) in WEIGHTS.items():fetch(name,stage/name,sha,limit)
        if not verify(stage):raise RuntimeError("FERRARI_COMFY_SD15_STAGE_VALIDATION_FAILED")
        (stage/"FERRARI_PROVENANCE.json").write_text(json.dumps({
          "source":"stable-diffusion-v1-5/stable-diffusion-v1-5",
          "revision":REV,"license":"creativeml-openrail-m",
          "weights_sha256":{n:sha for n,(sha,_) in WEIGHTS.items()},
          "scope":"Ferrari ComfyUI only, fp16 SafeTensors, CPU",
          "reason":"canonical SD 1.5 UNet recognized by ComfyUI; Tiny-SD pruned variant was unsupported",
        },indent=2)+"\n")
        stage.rename(DEST)
        print("FERRARI_COMFY_SD15=PASS_INSTALLED_PRIVATE",flush=True)
        print("FERRARI_COMFY_SD15_GLOBAL_CHANGES=ZERO",flush=True)
    finally:
        if stage.exists() and not stage.is_symlink():shutil.rmtree(stage)
    return 0

if __name__=="__main__":
    try:sys.exit(main())
    except Exception as e:
        print("FERRARI_COMFY_SD15_BLOCKED="+str(e)[:500],file=sys.stderr)
        sys.exit(3)
