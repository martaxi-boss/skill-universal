#!/usr/bin/env python3
"""Real, bounded ComfyUI CPU text-to-image proof, no persistent web service.

The administrator must launch this through a transient systemd scope limiting
memory and CPU. ComfyUI + weights are Ferrari-private and no global pip/apt.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import resource
import sys
import time

ROOT = Path("/srv/projects/skill-universal")
COMFY = ROOT / "tools/comfyui-v0.43.0"
VENV = ROOT / ".runtime/venvs/extended/comfyui"
MODEL = COMFY / "models/diffusers/sd15-fp16-f03de327"
OUTPUT = ROOT / ".runtime/comfyui-proof-20261106"

def main() -> int:
    # Scope must be established by the VPS runner, before importing torch.
    cg = Path("/sys/fs/cgroup")
    if not (cg/"cgroup.controllers").exists():
        raise RuntimeError("FERRARI_COMFY_CGROUP_V2_REQUIRED")
    mem_limit=(cg/"memory.max")
    # With a nested unit, /sys/fs/cgroup/.../memory.max can refer to the
    # delegated root, not the current process. Determine the actual cgroup.
    cp=Path("/proc/self/cgroup").read_text().strip().splitlines()
    process_cg=next((row.split("::",1)[1] for row in cp if "::" in row),None)
    if not process_cg or ".." in process_cg:
        raise RuntimeError("FERRARI_COMFY_CGROUP_NOT_FOUND")
    actual=(cg / process_cg.lstrip("/") / "memory.max")
    limit=actual.read_text().strip() if actual.is_file() else "max"
    if limit=="max" or int(limit)>5_500_000_000 or int(limit)<2_500_000_000:
        raise RuntimeError("FERRARI_COMFY_NO_SAFE_MEMORY_CGROUP="+limit)
    if not MODEL.is_dir() or MODEL.is_symlink() or not (MODEL/"model_index.json").is_file():
        raise RuntimeError("FERRARI_COMFY_MODEL_NOT_PRESENT")
    if OUTPUT.exists() or OUTPUT.is_symlink():
        raise FileExistsError("FERRARI_COMFY_PROOF_OUTPUT_ALREADY_EXISTS")
    if not (VENV/"bin/python").resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("FERRARI_COMFY_PYTHON_RUNTIME_NOT_PRIVATE")
    if Path(sys.prefix).resolve(strict=True) != VENV.resolve(strict=True):
        raise RuntimeError("FERRARI_COMFY_NOT_RUNNING_IN_PRIVATE_VENV")
    t0=time.monotonic()
    os.environ.update({
        "OMP_NUM_THREADS":"2",
        "MKL_NUM_THREADS":"2",
        "OPENBLAS_NUM_THREADS":"2",
        "HF_HUB_OFFLINE":"1",
        "TRANSFORMERS_OFFLINE":"1",
        "NO_PROXY":"*",
        "CUDA_VISIBLE_DEVICES":"",
        "COMFYUI_DISABLE_TELEMETRY":"1",
        "PYTHONNOUSERSITE":"1",
    })
    os.chdir(COMFY)
    sys.path.insert(0,str(COMFY))
    sys.argv=["main.py","--cpu","--disable-auto-launch"]
    import torch
    import numpy as np
    from PIL import Image
    torch.set_num_threads(2)
    # ComfyUI main.py enables CLI parsing before importing nodes; standalone
    # direct-node jobs must do the same or model_management assumes CUDA.
    import comfy.options
    comfy.options.enable_args_parsing()
    import comfy.cli_args
    if not comfy.cli_args.args.cpu:
        raise RuntimeError("FERRARI_COMFY_CPU_MODE_ARG_MISSING")
    import nodes
    print("FERRARI_COMFY_CPU_TORCH="+torch.__version__,flush=True)
    if torch.cuda.is_available():
        raise RuntimeError("FERRARI_COMFY_CUDA_NOT_EXPECTED")
    model,clip,vae=nodes.DiffusersLoader().load_checkpoint(MODEL.name)
    if not all(x is not None for x in (model,clip,vae)):
        raise RuntimeError("FERRARI_COMFY_MODEL_COMPONENTS_MISSING")
    print("FERRARI_COMFY_ACTUAL_MODEL_LOAD=PASS",flush=True)
    positive=nodes.CLIPTextEncode().encode(clip, "A small blue sailboat on a calm lake, daylight")[0]
    negative=nodes.CLIPTextEncode().encode(clip,"blurry, distorted, text")[0]
    latent=nodes.EmptyLatentImage().generate(256,256,1)[0]
    sample=nodes.KSampler().sample(model,1337,3,4.0,"euler","normal",
                                  positive,negative,latent,denoise=1.0)[0]
    pixels=nodes.VAEDecode().decode(vae,sample)[0]
    arr=np.clip(pixels[0].cpu().numpy()*255.0,0,255).astype(np.uint8)
    if arr.shape[:2]!=(256,256) or arr.std()<1.5:
        raise RuntimeError("FERRARI_COMFY_IMAGE_INVALID_OR_CONSTANT")
    OUTPUT.mkdir(mode=0o700,parents=True)
    png=OUTPUT/"comfyui-sd15-proof.png"
    Image.fromarray(arr).save(png)
    with Image.open(png) as img:
        img.verify()
    import hashlib
    sha=hashlib.sha256(png.read_bytes()).hexdigest()
    result={
        "status":"completed",
        "source":"stable-diffusion-v1-5/stable-diffusion-v1-5",
        "source_revision":"f03de327dd89b501a01da37fc5240cf4fdba85a1",
        "model_format":"safetensors",
        "engine":"ComfyUI-v0.43.0",
        "device":"cpu",
        "image":"comfyui-tiny-sd-proof.png",
        "size":[256,256],
        "seed":1337,
        "steps":3,
        "sha256":sha,
        "elapsed_seconds":round(time.monotonic()-t0,2),
        "peak_rss_mib":round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,1),
    }
    (OUTPUT/"report.json").write_text(json.dumps(result,indent=2)+"\n")
    print("FERRARI_COMFY_IMAGE_REAL=PASS width=256 height=256 sha256="+sha,flush=True)
    print("FERRARI_COMFY_ELAPSED_SECONDS="+str(result["elapsed_seconds"]),flush=True)
    print("FERRARI_COMFY_PEAK_RSS_MIB="+str(result["peak_rss_mib"]),flush=True)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:
        print("FERRARI_COMFY_REAL_INFERENCE_FAILED="+str(exc)[:600],file=sys.stderr)
        raise
