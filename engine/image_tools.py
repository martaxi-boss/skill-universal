"""Ferrari private OpenCV diagnostic for ordinary product photos and images.

This operation measures technical image properties and renders a small preview.
It NEVER certifies a photo's aesthetic/commercial suitability or invents content.
Only the Ferrari-owned Docling Python virtualenv with OpenCV is permitted;
there is no PATH, global Python, online API, installation or daemon fallback.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

HOME = Path("/srv/projects/skill-universal")
VENV = HOME / ".runtime/venvs/extended/docling"
PYTHON = VENV / "bin/python"
SITE = VENV / "lib/python3.12/site-packages"
ALLOWED = frozenset({".png", ".jpg", ".jpeg", ".webp"})
MAX_BYTES = 2_000_000
MAX_PIXELS = 24_000_000
PREVIEW_EDGE = 1280


def sha256(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def available() -> bool:
    """Read-only presence, not a functional import or success certificate."""
    try:
        home = HOME.resolve(strict=True)
        return bool(
            VENV.is_dir() and not VENV.is_symlink()
            and VENV.resolve(strict=True).is_relative_to(home)
            and PYTHON.is_file() and os.access(PYTHON, os.X_OK)
            and PYTHON.resolve(strict=True).is_relative_to(home)
            and SITE.is_dir() and not SITE.is_symlink()
            and SITE.resolve(strict=True).is_relative_to(home)
            and (SITE / "cv2").is_dir() and not (SITE / "cv2").is_symlink()
            and (SITE / "numpy").is_dir() and not (SITE / "numpy").is_symlink()
        )
    except (OSError, RuntimeError):
        return False


def _bounded_paths(source: Path, folder: Path) -> None:
    home = HOME.resolve(strict=True)
    if (source.is_symlink() or not source.is_file()
            or source.suffix.lower() not in ALLOWED
            or not source.resolve(strict=True).is_relative_to(home)
            or not 100 <= source.stat().st_size <= MAX_BYTES):
        raise ValueError("Ferrari image analysis requires a private PNG/JPEG/WebP of at most 2 MB")
    if folder.is_symlink() or not folder.resolve().is_relative_to(home):
        raise ValueError("Ferrari image analysis output must stay inside the project")


def analyze(source: Path, folder: Path):
    """Run one bounded, fixed worker in the Ferrari-owned OpenCV venv."""
    source, folder = Path(source), Path(folder)
    _bounded_paths(source, folder)
    if not available():
        raise RuntimeError("Ferrari private OpenCV/NumPy runtime is not available")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    report, preview = folder / "image-analysis.json", folder / "image-preview.png"
    if any(p.exists() or p.is_symlink() for p in (report, preview)):
        raise FileExistsError("Ferrari refuses to replace image analysis artifacts")
    env = os.environ.copy()
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_PRELOAD", "LD_LIBRARY_PATH"):
        env.pop(key, None)
    env.update({
        "PYTHONNOUSERSITE": "1", "CUDA_VISIBLE_DEVICES": "",
        "OMP_NUM_THREADS": "1", "OPENBLAS_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1", "OPENCV_OPENCL_RUNTIME": "disabled",
        "OPENCV_IO_MAX_IMAGE_PIXELS": str(MAX_PIXELS),
        "OPENCV_IO_MAX_IMAGE_WIDTH": "12000",
        "OPENCV_IO_MAX_IMAGE_HEIGHT": "12000",
        "HOME": str(folder), "TMPDIR": str(folder),
        "XDG_CACHE_HOME": str(folder), "XDG_CONFIG_HOME": str(folder),
        "XDG_DATA_HOME": str(folder),
    })
    try:
        process = subprocess.run(
            [str(PYTHON), "-I", str(Path(__file__).resolve(strict=True)),
             "--worker", str(source), str(folder)],
            shell=False, capture_output=True, text=True, errors="replace",
            timeout=90, cwd=str(folder), env=env, check=False)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("Ferrari private OpenCV timed out after 90 seconds") from exc
    if process.returncode:
        raise RuntimeError("Ferrari private OpenCV failed: " + process.stderr[-500:])
    if (not report.is_file() or report.is_symlink() or report.stat().st_size < 100
            or not preview.is_file() or preview.is_symlink() or preview.stat().st_size < 48):
        raise RuntimeError("Ferrari image analysis did not produce valid artifacts")
    with preview.open("rb") as f:
        header = f.read(24)
    if (header[:8] != b"\x89PNG\r\n\x1a\n"
            or int.from_bytes(header[16:20], "big") < 1
            or int.from_bytes(header[20:24], "big") < 1):
        raise RuntimeError("Ferrari OpenCV preview is not a valid PNG")
    payload = json.loads(report.read_text(encoding="utf-8"))
    if (payload.get("status") != "completed"
            or payload.get("program") != "opencv"
            or payload.get("input_sha256") != sha256(source)
            or payload.get("preview_sha256") != sha256(preview)
            or type(payload.get("width")) is not int or payload["width"] <= 0
            or type(payload.get("height")) is not int or payload["height"] <= 0
            or payload["width"] * payload["height"] > MAX_PIXELS
            or payload.get("commercial_quality_certified") is not False):
        raise RuntimeError("Ferrari OpenCV provenance or metadata failed verification")
    return str(PYTHON) + ":opencv-offline", [report, preview]


def _worker(source: Path, folder: Path) -> int:
    if Path(sys.prefix).resolve(strict=True) != VENV.resolve(strict=True):
        raise RuntimeError("Ferrari image worker must use the private Docling/OpenCV venv")
    _bounded_paths(source, folder)
    if not available():
        raise RuntimeError("Ferrari private OpenCV is missing")
    import cv2
    import numpy as np
    cv2.setNumThreads(1)
    raw = np.frombuffer(source.read_bytes(), dtype=np.uint8)
    image = cv2.imdecode(raw, cv2.IMREAD_COLOR)
    if image is None or len(image.shape) != 3:
        raise ValueError("Ferrari OpenCV could not decode a supported real image")
    height, width = (int(image.shape[0]), int(image.shape[1]))
    if width < 1 or height < 1 or width * height > MAX_PIXELS:
        raise ValueError("Ferrari OpenCV image dimensions exceed the 24MP ceiling")
    scale = min(1.0, PREVIEW_EDGE / max(width, height))
    if scale < 1.0:
        image = cv2.resize(image, (max(1, round(width * scale)),
                                   max(1, round(height * scale))),
                           interpolation=cv2.INTER_AREA)
    grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    brightness = float(np.mean(grey))
    contrast = float(np.std(grey))
    sharpness = float(np.var(cv2.Laplacian(grey, cv2.CV_64F)))
    encoded_ok, encoded = cv2.imencode(".png", image,
                                    [cv2.IMWRITE_PNG_COMPRESSION, 3])
    if not encoded_ok:
        raise RuntimeError("Ferrari OpenCV PNG preview encoding failed")
    folder.mkdir(parents=True, exist_ok=True, mode=0o700)
    preview = folder / "image-preview.png"
    with preview.open("xb") as f:
        f.write(encoded.tobytes())
    observations = []
    if width < 720 or height < 720:
        observations.append("Small image dimensions for many commercial placements")
    if brightness < 45:
        observations.append("Low average brightness measured")
    elif brightness > 220:
        observations.append("High average brightness measured")
    if contrast < 24:
        observations.append("Low greyscale contrast measured")
    payload = {
        "status": "completed",
        "program": "opencv",
        "opencv_version": cv2.__version__,
        "executor": "Ferrari private Docling virtualenv, CPU only",
        "input_sha256": sha256(source),
        "preview_sha256": sha256(preview),
        "width": width, "height": height,
        "preview_width": int(image.shape[1]),
        "preview_height": int(image.shape[0]),
        "brightness_mean_0_255": round(brightness, 2),
        "contrast_std_0_255": round(contrast, 2),
        "laplacian_variance": round(sharpness, 2),
        "measurements_on_preview": True,
        "observations": observations,
        "commercial_quality_certified": False,
        "semantic_accuracy_certified": False,
        "note": "Pixel statistics and preview only, not proof of focus, image rights, suitability for Meta or editorial approval"
    }
    with (folder / "image-analysis.json").open("x", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("FERRARI_OPENCV_IMAGE_ANALYZE=PASS", flush=True)
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 4 or sys.argv[1] != "--worker":
        raise SystemExit("Ferrari supports only a fixed --worker SRC OUTDIR invocation")
    try:
        raise SystemExit(_worker(Path(sys.argv[2]), Path(sys.argv[3])))
    except Exception as exc:
        print("FERRARI_OPENCV_FAILED=" + str(exc)[:450], file=sys.stderr)
        raise SystemExit(2)
