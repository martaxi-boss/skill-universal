#!/usr/bin/env python3
"""Pinned SafeTensors Tiny-SD for the existing Ferrari ComfyUI on Ubuntu.

Do not install ComfyUI, PyTorch, a new system service or global packages.
All model bytes and staging remain inside /srv/projects/skill-universal.
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
import urllib.error
import urllib.request

ROOT = Path("/srv/projects/skill-universal")
COMFY = ROOT / "tools/comfyui-v0.43.0"
VENV = ROOT / ".runtime/venvs/extended/comfyui"
DEST_PARENT = COMFY / "models/diffusers"
DEST = DEST_PARENT / "segmind-tiny-sd-3d25de3"
REV = "3d25de3e8d5aacf94ce91176f204e6d11d120315"
HF = "https://huggingface.co/segmind/tiny-sd/resolve/" + REV + "/"
MAX_BYTES = 1_800_000_000
# Upstream verified SHA256 at pinned commit, from Hugging Face LFS pointers.
WEIGHTS = {
    "text_encoder/model.safetensors": ("cd56d54a36ac54c1de9a247a681059d19751e3706817a09e8b7a75c67ae93584", 246_144_152),
    "unet/diffusion_pytorch_model.safetensors": ("7a42d33f11664e625855aa437dd5aa5dabed711b54d55eb92d5e027db1c04196", 646_813_304),
    "vae/diffusion_pytorch_model.safetensors": ("249bd6adf5e03a78cfbc21c689b08f9e285fa49fa81f2cf9ff175c6272a2740a", 167_335_342),
}
CONFIGS = (
    "model_index.json", "unet/config.json", "vae/config.json", "text_encoder/config.json"
)

def confined(path: Path, *, require_exists: bool = False) -> None:
    base = ROOT.resolve(strict=True)
    resolved = path.resolve(strict=require_exists)
    if not resolved.is_relative_to(base):
        raise RuntimeError("FERRARI_COMFY_PATH_OUTSIDE_PROJECT")
    # Never allow symlinks in Ferrari owned source/target path.
    walk = path
    while walk != ROOT:
        if walk.is_symlink():
            raise RuntimeError("FERRARI_COMFY_SYMLINK_REJECTED")
        walk = walk.parent

def preflight() -> None:
    if not ROOT.is_dir() or ROOT.is_symlink() or ROOT.stat().st_uid != os.getuid():
        raise RuntimeError("FERRARI_COMFY_PROJECT_OWNER_OR_FOLDER_MISMATCH")
    for p in (COMFY, VENV, COMFY / "main.py"):
        confined(p, require_exists=True)
        if not p.exists():
            raise RuntimeError("FERRARI_COMFY_PRIVATE_ENV_MISSING")
    # Python venv bin/python can be an internal symlink to a Ferrari-owned runtime.
    py = VENV / "bin/python"
    if not py.is_file() or not py.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("FERRARI_COMFY_PRIVATE_PYTHON_MISSING")
    disk = shutil.disk_usage(ROOT).free
    mem = {}
    for line in Path("/proc/meminfo").read_text().splitlines():
        key,val = line.split(":",1)
        if key in ("MemTotal","MemAvailable","SwapTotal"):
            mem[key] = int(val.split()[0]) * 1024
    if disk < 9*1024**3 or mem.get("MemTotal",0)<7*1024**3 or mem.get("MemAvailable",0)<3*1024**3:
        raise RuntimeError("FERRARI_COMFY_RESOURCE_GUARD_FAILED")
    if (os.cpu_count() or 0)<2:
        raise RuntimeError("FERRARI_COMFY_CPU_GUARD_FAILED")
    if not COMFY.is_dir() or not VENV.is_dir():
        raise RuntimeError("FERRARI_COMFY_PRIVATE_INSTALLATION_MISSING")
    print("FERRARI_COMFY_PRIVATE_ENV=PASS",flush=True)
    print("FERRARI_COMFY_CPU_MODE=ONLY",flush=True)

def digest(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda:fh.read(4*1024*1024),b""):
            sha.update(chunk)
    return sha.hexdigest()

def verified(dest: Path) -> bool:
    if not dest.is_dir() or dest.is_symlink():
        return False
    try:
        for name,(sha,size) in WEIGHTS.items():
            p = dest/name
            confined(p, require_exists=True)
            if not p.is_file() or p.is_symlink() or p.stat().st_size != size or digest(p) != sha:
                return False
        for name in CONFIGS:
            p = dest/name
            confined(p, require_exists=True)
            if not p.is_file() or p.is_symlink() or not p.stat().st_size<60_000:
                return False
            json.loads(p.read_text(encoding="utf-8"))
    except (OSError,ValueError,RuntimeError,json.JSONDecodeError):
        return False
    return True

def download(name: str, file: Path, *, expected_sha: str | None, expected_size: int | None) -> None:
    if not name in WEIGHTS and not name in CONFIGS:
        raise ValueError("Only pinned Ferrari model files allowed")
    link = HF + name
    req = urllib.request.Request(link,headers={"User-Agent":"Ferrari-ComfyUI-PrivateModel/1.0"})
    print("FERRARI_COMFY_DOWNLOAD_START="+name,flush=True)
    total=0
    h=hashlib.sha256()
    file.parent.mkdir(mode=0o700,parents=True,exist_ok=True)
    with urllib.request.urlopen(req,timeout=90) as resp, file.open("xb") as out:
        for data in iter(lambda:resp.read(2*1024*1024),b""):
            total+=len(data)
            if total > (expected_size if expected_size else 60_000) or total > MAX_BYTES:
                raise RuntimeError("FERRARI_COMFY_DOWNLOAD_SIZE_LIMIT")
            h.update(data)
            out.write(data)
    if (expected_size is not None and total != expected_size) or (expected_sha and h.hexdigest()!=expected_sha):
        raise RuntimeError("FERRARI_COMFY_MODEL_SHA256_OR_SIZE_MISMATCH="+name)
    if expected_size is None:
        json.loads(file.read_text(encoding="utf-8"))
    print("FERRARI_COMFY_DOWNLOAD_VERIFIED="+name+" bytes="+str(total),flush=True)

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--check",action="store_true")
    parser.add_argument("--apply",action="store_true")
    args=parser.parse_args()
    if args.check == args.apply:
        parser.error("Choose --check or --apply")
    preflight()
    confined(DEST_PARENT)
    if args.check:
        if not verified(DEST):
            print("FERRARI_COMFY_TINY_SD=NOT_INSTALLED_OR_NOT_VERIFIED",file=sys.stderr)
            return 3
        print("FERRARI_COMFY_TINY_SD=PASS_PRIVATE_SHA256",flush=True)
        return 0
    if verified(DEST):
        print("FERRARI_COMFY_TINY_SD=PASS_REUSE",flush=True)
        return 0
    if DEST.exists() or DEST.is_symlink():
        raise RuntimeError("FERRARI_COMFY_EXISTING_MODEL_CONFLICT; no overwrite")
    DEST_PARENT.mkdir(mode=0o700,parents=True,exist_ok=True)
    confined(DEST_PARENT, require_exists=True)
    # A copy/mv within the same filesystem is atomic; exceptions scrub staging only.
    stage=Path(tempfile.mkdtemp(prefix=".ferrari-tiny-sd-staging-",dir=DEST_PARENT))
    confined(stage,require_exists=True)
    try:
        for name in CONFIGS:
            download(name,stage/name,expected_sha=None,expected_size=None)
        for name,(sha,size) in WEIGHTS.items():
            download(name,stage/name,expected_sha=sha,expected_size=size)
        if not verified(stage):
            raise RuntimeError("FERRARI_COMFY_STAGE_INTEGRITY_FAILED")
        (stage/"FERRARI_PROVENANCE.json").write_text(json.dumps({
            "repository":"segmind/tiny-sd","revision":REV,
            "license":"creativeml-openrail-m",
            "weights":{k:{"sha256":v[0],"bytes":v[1]} for k,v in WEIGHTS.items()},
            "source":"https://huggingface.co/segmind/tiny-sd",
            "scope":"Ferrari private ComfyUI CPU-only; no pickle weights",
        },indent=2)+"\n",encoding="utf-8")
        stage.rename(DEST)
        print("FERRARI_COMFY_TINY_SD=PASS_INSTALLED_PRIVATE",flush=True)
        print("FERRARI_COMFY_GLOBAL_INSTALLS=ZERO",flush=True)
    finally:
        if stage.exists() and not stage.is_symlink():
            shutil.rmtree(stage)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except (OSError,ValueError,RuntimeError,urllib.error.URLError) as exc:
        print("FERRARI_COMFY_MODEL_BLOCKED="+str(exc)[:600],file=sys.stderr)
        sys.exit(3)
