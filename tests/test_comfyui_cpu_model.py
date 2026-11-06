"""Ferrari ComfyUI model release guards (static + no-network fixtures)."""
import hashlib
import json
from pathlib import Path
import runpy
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
MODULE = ROOT / "install/vps-comfyui-cpu-model.py"
SMOKE = ROOT / "install/vps-comfyui-cpu-smoke.py"


class ComfyModelTests(unittest.TestCase):
    def test_predefined_origin_hashes_and_project_only(self):
        source=MODULE.read_text()
        self.assertIn("3d25de3e8d5aacf94ce91176f204e6d11d120315",source)
        self.assertIn("https://huggingface.co/segmind/tiny-sd/resolve/",source)
        self.assertIn("/srv/projects/skill-universal",source)
        self.assertIn("FERRARI_COMFY_GLOBAL_INSTALLS=ZERO",source)
        self.assertNotIn("pip install",source)
        self.assertNotIn("apt-get",source)
        self.assertNotIn("torch.load",source)
        self.assertNotIn("/tmp",source)
        code=compile(source,str(MODULE),"exec")
        self.assertIsNotNone(code)

    def test_weights_only_safetensors_and_hashes(self):
        state=runpy.run_path(str(MODULE))
        weights=state["WEIGHTS"]
        self.assertEqual(len(weights),3)
        self.assertEqual(sum(v[1] for v in weights.values()),1_060_292_798)
        self.assertTrue(all(x.endswith(".safetensors") and len(v[0])==64 for x,v in weights.items()))
        self.assertEqual(state["REV"],"3d25de3e8d5aacf94ce91176f204e6d11d120315")

    def test_model_verifier_is_hash_strict_no_network(self):
        state=runpy.run_path(str(MODULE))
        with tempfile.TemporaryDirectory() as d:
            home=Path(d)
            dest=home/"models"
            dest.mkdir()
            fake=b"synthetic image model bytes"
            fake_sha=hashlib.sha256(fake).hexdigest()
            weights={"unet/diffusion_pytorch_model.safetensors":(fake_sha,len(fake))}
            with patch.dict(state["verified"].__globals__,{"ROOT":home,"WEIGHTS":weights,
                      "CONFIGS":("model_index.json",)}):
                p=dest/"unet/diffusion_pytorch_model.safetensors"
                p.parent.mkdir()
                p.write_bytes(fake)
                (dest/"model_index.json").write_text('{"_class_name":"StableDiffusionPipeline"}')
                self.assertTrue(state["verified"](dest))
                p.write_bytes(b"tampered")
                self.assertFalse(state["verified"](dest))

    def test_rejects_any_nonallowlisted_download(self):
        state=runpy.run_path(str(MODULE))
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                state["download"]("../../secret",Path(d)/"evil",expected_sha=None,expected_size=None)

    def test_standard_sd15_unet_compatible_model_is_pinned(self):
        file=ROOT/"install/vps-comfyui-sd15-fp16-model.py"
        source=file.read_text()
        compile(source,str(file),"exec")
        self.assertIn("f03de327dd89b501a01da37fc5240cf4fdba85a1",source)
        self.assertIn("c83908253f9a64d08c25fc90874c9c8aef9a329ce1ca5fb909d73b0c83d1ea21",source)
        self.assertIn("77795e2023adcf39bc29a884661950380bd093cf0750a966d473d1718dc9ef4e",source)
        self.assertIn("4fbcf0ebe55a0984f5a5e00d8c4521d52359af7229bb4d81890039d2aa16dd7c",source)
        self.assertIn("models/diffusers",source)
        self.assertNotIn("apt-get",source)
        self.assertNotIn("pip install",source)
        self.assertNotIn("pickle",source.lower().replace("pickle weights",""))
        smoke=SMOKE.read_text()
        self.assertIn('sd15-fp16-f03de327',smoke)
        self.assertNotIn('segmind-tiny-sd-3d25de3',smoke)

    def test_cpu_smoke_requires_cgroup_and_real_model_png(self):
        code=SMOKE.read_text()
        self.assertIn("memory.max",code)
        self.assertIn("cpu",code)
        self.assertIn("DiffusersLoader",code)
        self.assertIn("KSampler",code)
        self.assertIn("VAEDecodeTiled",code)
        self.assertIn("unload_all_models()",code)
        self.assertIn("FERRARI_COMFY_SAMPLING_COMPLETE=PASS",code)
        self.assertIn('"image":"comfyui-sd15-proof.png"\',code)
        self.assertIn("comfy.options.enable_args_parsing()",code)
        self.assertLess(code.index("comfy.options.enable_args_parsing()"),code.index("    import nodes"))
        self.assertIn("VAEDecode",code)
        self.assertIn("OUTPUT.mkdir",code)
        self.assertIn("comfyui-sd15-proof.png",code)
        self.assertNotIn("pip install",code)
        compile(code,str(SMOKE),"exec")


if __name__=="__main__":
    unittest.main()
