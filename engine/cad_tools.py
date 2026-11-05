"""Real, typed Ubuntu CAD/3D and office adapters. No arbitrary shell execution."""
from __future__ import annotations
import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]

def _binary(name):
    target = shutil.which(name)
    if not target:
        raise RuntimeError("Missing Ubuntu program: " + name)
    return target

def _run(args, *, env=None, timeout=300):
    try:
        p = subprocess.run(args, shell=False, check=False,
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           timeout=timeout, env=env)
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("CAD/office executor timeout") from exc
    if p.returncode:
        detail = (p.stderr + b"\n" + p.stdout).decode("utf-8", "replace")[-1300:]
        raise RuntimeError("CAD/office executor failed: " + detail)
    return p

def _artifact(path, minimum_bytes=80):
    if not path.is_file() or path.stat().st_size < minimum_bytes:
        raise RuntimeError("Missing/empty output artifact: " + str(path))
    return path

def scad_to_stl(source: Path, output_dir: Path) -> tuple[str, list[Path]]:
    if source.suffix.lower() != ".scad":
        raise ValueError("OpenSCAD source (.scad) required")
    exe = _binary("openscad")
    dest = output_dir / "solid.stl"
    if dest.exists() or dest.is_symlink():
        raise FileExistsError("Refusing overwrite: " + str(dest))
    output_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["QT_QPA_PLATFORM"] = "offscreen"
    _run([exe, "-o", str(dest), str(source)], env=env, timeout=180)
    return exe, [_artifact(dest, 84)]

def blender_house(output_dir: Path, *, title: str = "Ferrari 3D") -> tuple[str, list[Path]]:
    exe = _binary("blender")
    source = ROOT / "engine" / "blender_house.py"
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [output_dir / "house.blend", output_dir / "house.glb", output_dir / "house.png"]
    if any(x.exists() or x.is_symlink() for x in paths):
        raise FileExistsError("Refusing overwrite for 3D artifacts")
    env = os.environ.copy()
    env["LIBGL_ALWAYS_SOFTWARE"] = "1"
    env["OMP_NUM_THREADS"] = "2"
    _run([exe, "--background", "--factory-startup", "--python-exit-code", "5",
          "--python", str(source), "--", str(output_dir), title[:100]],
         env=env, timeout=480)
    return exe, [_artifact(x, 200) for x in paths]

def office_pdf(source: Path, output_dir: Path) -> tuple[str, list[Path]]:
    if source.suffix.lower() not in {".docx", ".odt", ".pptx", ".xlsx", ".rtf"}:
        raise ValueError("DOCX/ODT/PPTX/XLSX/RTF input required")
    exe = _binary("libreoffice")
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / (source.stem + ".pdf")
    if target.exists() or target.is_symlink():
        raise FileExistsError("Refusing overwrite: " + str(target))
    with TemporaryDirectory(prefix=".ferrari-office-", dir=str(output_dir)) as profile:
        _run([exe, "--headless", "-env:UserInstallation=" + Path(profile).as_uri(),
              "--convert-to", "pdf", "--outdir", str(output_dir), str(source)],
             timeout=150)
    return exe, [_artifact(target, 100)]
