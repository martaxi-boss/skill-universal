#!/usr/bin/env python3
"""Ferrari F11: one synthetic PDAL TXT->LAS->TXT round-trip in the private QGIS prefix.

No package installations, catalog writes, external files or background services.
Output is JSON evidence only; all generated point clouds are removed on exit.
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path
import resource
import struct
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
RUNTIME = ROOT / ".runtime"
QGIS = ROOT / "tools/qgis-4.2.3-condaforge"
SIDECAR = ROOT / "tools/pdal-hdf5-2.2.0-abi320"
CURRENT_SHA = "205c6f0e970259c79fa2111b6670c2fe1672fb27"
FALLBACK_SHA = "7bf6dcecf15da26502c5969b5eee54d5e116fc32"
POINTS = ((10.,20.,5.), (11.,21.,6.), (12.,22.,7.), (13.,23.,8.), (14.,24.,9.))


def require(ok: bool, code: str) -> None:
    if not ok:
        raise RuntimeError(code)


def guard() -> Path:
    require(os.geteuid() != 0, "F11_PDAL_NONROOT_REQUIRED")
    for p in (ROOT, RUNTIME, QGIS, SIDECAR):
        require(p.is_dir() and not p.is_symlink(), "F11_PDAL_UNSAFE_PROJECT_DIR")
    current = ROOT / "current"
    require(current.is_symlink() and current.resolve(strict=True) ==
            ROOT / "releases" / CURRENT_SHA, "F11_PDAL_ACTIVE_RELEASE_DRIFT")
    fallback = ROOT / "releases" / FALLBACK_SHA
    require((fallback / "engine/ferrari.py").is_file() and
            (fallback / "engine/catalog.json").is_file(),
            "F11_PDAL_MODERN_FALLBACK_MISSING")
    d = json.loads((current / "engine/catalog.json").read_text())
    require(len(d["tools"]) == 173 and len(d["functions"]) == 272 and
            d["counts"]["all_catalog_entries"] == 450,
            "F11_PDAL_UNIVERSAL_CATALOG_DRIFT")
    for filename in ("libhdf5_cpp.so.320", "libhdf5.so.320"):
        path = SIDECAR / "lib" / filename
        require(path.is_file() and path.resolve(strict=True).is_relative_to(SIDECAR),
                "F11_PDAL_ABI320_SIDECAR_MISSING")
    binary = QGIS / "bin/pdal"
    require(binary.is_file() and os.access(binary, os.X_OK) and
            binary.resolve(strict=True).is_relative_to(QGIS),
            "F11_PDAL_PRIVATE_EXECUTABLE_MISSING")
    return binary


def environment(tmp: Path) -> dict[str, str]:
    for name in ("home", "cache", "config", "run"):
        (tmp / name).mkdir(mode=0o700)
    return {
        "HOME": str(tmp/"home"), "TMPDIR": str(tmp),
        "XDG_CACHE_HOME": str(tmp/"cache"),
        "XDG_CONFIG_HOME": str(tmp/"config"),
        "XDG_RUNTIME_DIR": str(tmp/"run"),
        "PATH": str(QGIS/"bin") + ":/usr/bin:/bin",
        "LD_LIBRARY_PATH": str(SIDECAR/"lib") + ":" + str(QGIS/"lib"),
        "PDAL_DRIVER_PATH": str(QGIS/"lib"),
        "QGIS_PREFIX_PATH": str(QGIS),
        "LANG": "C.UTF-8", "LC_ALL": "C.UTF-8", "OMP_NUM_THREADS": "2",
        "QT_QPA_PLATFORM": "offscreen", "LIBGL_ALWAYS_SOFTWARE": "1",
        "PYTHONDONTWRITEBYTECODE": "1",
    }


def child_limits() -> None:
    resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    resource.setrlimit(resource.RLIMIT_FSIZE, (24*1024*1024, 24*1024*1024))
    resource.setrlimit(resource.RLIMIT_CPU, (50, 55))


def run(binary: Path, argv: list[str], env: dict[str,str],
        cwd: Path) -> dict:
    try:
        p = subprocess.run([str(binary), *argv], cwd=cwd, env=env,
                           capture_output=True, text=True, check=False,
                           timeout=85, preexec_fn=child_limits)
        return {"exit_code": p.returncode, "timed_out": False,
                "stdout_tail": p.stdout[-900:], "stderr_tail": p.stderr[-900:]}
    except subprocess.TimeoutExpired as exc:
        return {"exit_code": None, "timed_out": True,
                "stdout_tail": "", "stderr_tail": str(exc)[-200:]}


def pipeline(path: Path, stages: list[dict]) -> None:
    path.write_text(json.dumps({"pipeline": stages}), encoding="utf-8")


def las_header(path: Path) -> dict:
    data = path.read_bytes()
    require(len(data) >= 227 and data[:4] == b"LASF", "F11_PDAL_LAS_MAGIC_FAIL")
    count = struct.unpack_from("<I", data, 107)[0]
    header_bytes = struct.unpack_from("<H", data, 94)[0]
    offset = struct.unpack_from("<I", data, 96)[0]
    require(227 <= header_bytes <= offset <= len(data), "F11_PDAL_LAS_HEADER_INVALID")
    require(count == len(POINTS), "F11_PDAL_LAS_POINT_COUNT")
    return {"las_signature": "LASF", "bytes": len(data), "point_count": count,
            "header_bytes": header_bytes, "point_data_offset": offset}


def verify_csv(path: Path) -> int:
    require(path.is_file() and path.stat().st_size <= 256*1024,
            "F11_PDAL_ROUNDTRIP_MISSING_OR_LARGE")
    with path.open(newline="", encoding="utf-8") as fh:
        r = csv.DictReader(fh)
        require(r.fieldnames is not None and
                all(name in r.fieldnames for name in ("X","Y","Z")),
                "F11_PDAL_ROUNDTRIP_DIMENSIONS")
        points = [(float(x["X"]),float(x["Y"]),float(x["Z"])) for x in r]
    require(len(points) == len(POINTS), "F11_PDAL_ROUNDTRIP_COUNT")
    require(all(all(abs(a-b) <= 0.02 for a,b in zip(actual, expected))
                for actual,expected in zip(points, POINTS)),
            "F11_PDAL_ROUNDTRIP_COORDINATES")
    return len(points)


def certify() -> dict:
    binary = guard()
    with tempfile.TemporaryDirectory(prefix=".f11-pdal-las-", dir=RUNTIME) as td:
        tmp = Path(td)
        env = environment(tmp)
        report = {"status": "partial_blocked", "scope": "TXT_LAS_TXT_synthetic",
                  "project": "skill-universal", "catalog_entries": 450,
                  "active_release": CURRENT_SHA, "fallback_release": FALLBACK_SHA,
                  "global_apt_modified": False, "other_projects_modified": False,
                  "catalog_modified": False, "full_pdal_formats_certified": False,
                  "optional_hdf_icebridge_formats_certified": False,
                  "test_artifacts_removed": True}
        drivers = run(binary, ["--drivers"], env, tmp)
        needed = ("readers.text", "writers.text", "readers.las", "writers.las")
        available = (drivers["exit_code"] == 0 and not drivers["timed_out"] and
                     all(name in drivers["stdout_tail"] or name in drivers["stderr_tail"]
                         for name in needed))
        # Driver output can exceed the bounded stdout tail; verify again with
        # the real pipeline if the loader succeeded.
        report["driver_registry_started"] = drivers["exit_code"] == 0 and not drivers["timed_out"]
        report["driver_names_in_tail"] = available
        if not report["driver_registry_started"]:
            report["reason"] = "private_pdal_driver_registry_failed"
            report["diagnostic_tail"] = drivers["stderr_tail"][-300:]
            return report
        source = tmp / "synthetic-points.txt"
        source.write_text("X,Y,Z\n" + "".join(
            f"{a:g},{b:g},{c:g}\n" for a,b,c in POINTS), encoding="utf-8")
        las = tmp / "synthetic-points.las"
        conversion = tmp / "to-las.json"
        pipeline(conversion, [
            {"type": "readers.text", "filename": str(source)},
            {"type": "writers.las", "filename": str(las),
             "minor_version": 2, "dataformat_id": 0,
             "scale_x": 0.01, "scale_y": 0.01, "scale_z": 0.01}])
        writing = run(binary, ["pipeline", str(conversion)], env, tmp)
        report["txt_to_las_exit_code"] = writing["exit_code"]
        if writing["exit_code"] != 0 or not las.is_file():
            report["reason"] = "private_pdal_txt_to_las_failed"
            report["diagnostic_tail"] = writing["stderr_tail"][-300:]
            return report
        header = las_header(las)
        output = tmp / "roundtrip.csv"
        inverse = tmp / "from-las.json"
        pipeline(inverse, [
            {"type": "readers.las", "filename": str(las)},
            {"type": "writers.text", "filename": str(output),
             "format": "csv", "order": "X,Y,Z",
             "keep_unspecified": False, "precision": 3}])
        reading = run(binary, ["pipeline", str(inverse)], env, tmp)
        report["las_to_txt_exit_code"] = reading["exit_code"]
        if reading["exit_code"] != 0 or not output.is_file():
            report["reason"] = "private_pdal_las_to_txt_failed"
            report["diagnostic_tail"] = reading["stderr_tail"][-300:]
            return report
        rows = verify_csv(output)
        report.update({"status": "pass", "synthetic_point_count": rows,
                       "las_header": header, "txt_las_txt_roundtrip_pass": True,
                       "no_global_install": True})
        return report


def main() -> int:
    if sys.argv[1:] != ["--certify"]:
        raise SystemExit("F11_PDAL_CERTIFY_ONLY")
    try:
        result = certify()
        print(json.dumps(result, sort_keys=True), flush=True)
        return 0 if result["status"] == "pass" else 2
    except (OSError,RuntimeError,ValueError,KeyError,subprocess.SubprocessError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)[-300:],
                          "global_apt_modified":False,"other_projects_modified":False},
                         sort_keys=True),flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
