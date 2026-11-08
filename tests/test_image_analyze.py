"""Ferrari's real private OpenCV operation, isolation and output verification."""
import base64
import binascii
import json
from pathlib import Path
import struct
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch
import zlib
from zipfile import ZipFile

from engine import ferrari, image_tools, skill_job, tool_runtime


def fixture_png(width=64, height=64):
    """Portable public/synthetic RGB input with valid PNG CRC, no PIL dependency."""
    def chunk(name, data):
        return (struct.pack(">I", len(data)) + name + data +
                struct.pack(">I", binascii.crc32(name + data) & 0xffffffff))
    raw = bytearray()
    for row in range(height):
        raw.append(0)
        for col in range(width):
            raw.extend(((col * 4) % 256, (row * 4) % 256,
                        ((col + row) * 2) % 256))
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress(raw)) +
            chunk(b"IEND", b""))


class PrivateOpenCVTests(unittest.TestCase):
    def test_single_catalog_and_no_global_runtime(self):
        self.assertIn("image-analyze", ferrari.OPS)
        self.assertIn("image-analyze", tool_runtime.BASE_OPERATIONS["opencv"])
        self.assertEqual(len(ferrari.OPS), 14)
        self.assertEqual(len(tool_runtime.BASE_OPERATIONS), 14)
        source = Path(image_tools.__file__).read_text()
        for forbidden in ("apt-get", "sudo ", "pip install", "shell=True", "shutil.which"):
            self.assertNotIn(forbidden, source)
        self.assertIsNone(skill_job.validate_job({
            "version":1, "id":"opencv-image-test", "kind":"operation",
            "operation":"image-analyze"}))

    def test_private_source_rules_and_no_symlinks(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)
            sample=home/"photo.png"
            sample.write_bytes(fixture_png())
            external=home.parent/"no-private-image.png"
            with patch.object(image_tools,"HOME",home):
                image_tools._bounded_paths(sample,home/"artifacts")
                link=home/"symlink.png"
                link.symlink_to(sample)
                with self.assertRaises(ValueError):
                    image_tools._bounded_paths(link,home/"artifacts")
                outside=home.parent/"external-private-test-output"
                with self.assertRaises(ValueError):
                    image_tools._bounded_paths(sample,outside)
                bad=home/"image.txt"
                bad.write_bytes(sample.read_bytes())
                with self.assertRaises(ValueError):
                    image_tools._bounded_paths(bad,home/"artifacts")
                too_large=home/"huge.png"
                too_large.write_bytes(b"x"*(image_tools.MAX_BYTES+1))
                with self.assertRaises(ValueError):
                    image_tools._bounded_paths(too_large,home/"artifacts")

    def test_fixed_private_worker_generates_provenance_checked_files(self):
        with TemporaryDirectory() as tmp:
            home=Path(tmp)
            src=home/"photo.png"
            src.write_bytes(fixture_png())
            dest=home/"artifacts"
            def mock_worker(args,**kw):
                self.assertEqual(args[1],"-I")
                self.assertEqual(args[3],"--worker")
                self.assertFalse(kw["shell"])
                self.assertLessEqual(kw["timeout"],90)
                self.assertNotIn("PYTHONPATH",kw["env"])
                self.assertEqual(kw["env"]["HOME"],str(dest))
                self.assertEqual(kw["env"]["PYTHONNOUSERSITE"],"1")
                preview=dest/"image-preview.png"
                preview.write_bytes(fixture_png(16,16))
                (dest/"image-analysis.json").write_text(json.dumps({
                    "status":"completed","program":"opencv",
                    "input_sha256": image_tools.sha256(src),
                    "preview_sha256": image_tools.sha256(preview),
                    "width":64,"height":64,
                    "commercial_quality_certified":False}))
                return SimpleNamespace(returncode=0,stderr="",stdout="PASS")
            with patch.object(image_tools,"HOME",home), patch.object(
                    image_tools,"available",return_value=True), patch.object(
                    image_tools.subprocess,"run",side_effect=mock_worker) as runner:
                exe,files=image_tools.analyze(src,dest)
                self.assertTrue(exe.endswith(":opencv-offline"))
                self.assertEqual([p.name for p in files],
                                 ["image-analysis.json","image-preview.png"])
                runner.assert_called_once()
            # Provenance must be checked, never trust subprocess success alone.
            src.write_bytes(fixture_png(32,32))
            with patch.object(image_tools,"HOME",home), patch.object(
                    image_tools,"available",return_value=True):
                with self.assertRaises(FileExistsError):
                    image_tools.analyze(src,dest)

    def test_real_vps_opencv_through_skill_and_zip(self):
        # Run an actual imported cv2 decode/measure/PNG encode when deployed;
        # CI on the GitHub runner does not masquerade as Ferrari VPS evidence.
        if not (image_tools.HOME/"current").is_symlink():
            self.skipTest("Only the real activated Ferrari VPS runs this integration")
        self.assertTrue(image_tools.available(),
                        "OpenCV installed in Ferrari must have a private usable venv")
        home=image_tools.HOME
        with TemporaryDirectory(prefix=".opencv-functional-",dir=home/".runtime") as folder:
            root=Path(folder)
            content=fixture_png(64,64)
            request={"version":1,"id":"ferrari-opencv-visual-real",
                "kind":"operation","operation":"image-analyze",
                "input":{"name":"synthetic-product.png",
                         "content_base64":base64.b64encode(content).decode()},
                "acceptance":{"required_extensions":[".json",".png"]}}
            report,code=skill_job.execute(request,root/"result")
            self.assertEqual(code,0,report)
            self.assertEqual(report["status"],"completed")
            self.assertEqual(report["quality_gate"]["status"],"passed")
            self.assertTrue(report["executor"].endswith(":opencv-offline"))
            zip_path=root/"result"/"response.zip"
            with ZipFile(zip_path) as bundle:
                self.assertIsNone(bundle.testzip())
                self.assertTrue({"artifacts/image-analysis.json",
                                 "artifacts/image-preview.png","report.json"}.issubset(bundle.namelist()))
                meta=json.loads(bundle.read("artifacts/image-analysis.json"))
                png=bundle.read("artifacts/image-preview.png")
            self.assertEqual((meta["width"],meta["height"]),(64,64))
            self.assertEqual(meta["program"],"opencv")
            self.assertFalse(meta["commercial_quality_certified"])
            self.assertEqual(png[:8],b"\x89PNG\r\n\x1a\n")
            print("FERRARI_REAL_OPENCV_SKILL_TO_ZIP=PASS")


if __name__=="__main__":
    unittest.main()
