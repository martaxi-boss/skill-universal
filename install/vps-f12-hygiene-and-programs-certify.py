#!/usr/bin/env python3
"""F12: project-confined hygiene and honest private-tool functional checks."""
import argparse
import hashlib
import http.server
import json
import os
from pathlib import Path
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
import threading
import zipfile

ROOT = Path("/srv/projects/skill-universal")
ACTIVE = "3f0ba44b7d8475a74a63c6010d1e27063c04bf1e"
FALLBACK = "427e1c33c6d10ca8ecd2103861adccd3d552c381"
SERVICES = ("pink-iptv-backend", "pink-vpn", "fadego-staging", "lowcost-europa",
            "pm2-iptvpn-bot", "pm2-telegram-robot-leads", "nginx", "postgresql@16-main")
SMOKE_MARKERS = ("image.png", "image.jpg", "publication.txt", "video.mlt", "song.mmp")


def guard():
    if os.geteuid() == 0 or ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("F12_NONROOT_PROJECT_ONLY")
    for name in ("releases", ".runtime", "tools", "runtimes"):
        p = ROOT / name
        if p.is_symlink() or not p.is_dir():
            raise RuntimeError("F12_MISSING_PRIVATE_ROOT:" + name)
    current = ROOT / "current"
    if not current.is_symlink() or current.resolve(strict=True) != ROOT / "releases" / ACTIVE:
        raise RuntimeError("F12_ACTIVE_RELEASE_MISMATCH")
    fallback = ROOT / "releases" / FALLBACK
    if fallback.is_symlink() or not (fallback / "engine/catalog.json").is_file():
        raise RuntimeError("F12_FALLBACK_MISSING")
    path = current / "engine/catalog.json"
    if path.is_symlink():
        raise RuntimeError("F12_CATALOG_SYMLINK")
    data = json.loads(path.read_text(encoding="utf-8"))
    if len(data["tools"]) != 173 or len(data["functions"]) != 280 or data["counts"]["all_catalog_entries"] != 458:
        raise RuntimeError("F12_CATALOG_COUNT_CHANGED")


def services():
    outcome = {}
    for name in SERVICES:
        p = subprocess.run(["/usr/bin/systemctl", "is-active", name],
                           capture_output=True, text=True, timeout=12, check=False)
        outcome[name] = p.stdout.strip()
    if set(outcome.values()) != {"active"}:
        raise RuntimeError("F12_PROTECTED_SERVICE_NOT_ACTIVE")
    return outcome


def busy(path):
    prefix = str(path) + "/"
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or proc.name == str(os.getpid()):
            continue
        refs = []
        for name in ("cwd", "exe"):
            try:
                refs.append(os.readlink(proc / name))
            except (OSError, PermissionError):
                pass
        try:
            refs.extend(x.decode("utf-8", "replace") for x in
                        (proc / "cmdline").read_bytes().split(b"\0")[:16])
        except (OSError, PermissionError):
            pass
        if any(r == str(path) or prefix in r for r in refs):
            return True
    return False


def eligible_scratch():
    root = ROOT / ".runtime/private-gui-test"
    if root.is_symlink():
        raise RuntimeError("F12_PRIVATE_SMOKE_ROOT_IS_SYMLINK")
    if not root.exists():
        return []
    if not root.is_dir() or root.resolve(strict=True).parent != (ROOT / ".runtime").resolve(strict=True):
        raise RuntimeError("F12_PRIVATE_SMOKE_ROOT_UNSAFE")
    result = []
    for child in root.iterdir():
        if not re.fullmatch("[0-9]{9,20}", child.name):
            continue
        if child.is_symlink() or not child.is_dir():
            continue
        if not all((child / x).is_file() and not (child / x).is_symlink() for x in SMOKE_MARKERS):
            continue
        if not busy(child):
            result.append(child)
    return sorted(result)


def clean(apply):
    guard()
    script = ROOT / "current/install/ferrari-cache-hygiene.py"
    if script.is_symlink() or not script.is_file():
        raise RuntimeError("F12_CACHE_CLEANER_NOT_TRUSTED")
    audited = runpy.run_path(str(script), run_name="f12_import")["audit"]
    cache = audited(ROOT, apply=False)
    targets = eligible_scratch()
    info = {"mode": "apply" if apply else "preview",
            "eligible_gui_smoke_run_ids": [p.name for p in targets],
            "removed_gui_smoke_run_ids": [],
            "npm_cache_present": cache["cache_present_before"],
            "npm_cache_bytes_before": cache["cache_allocated_bytes_before"],
            "npm_cache_removed": False, "removed_releases": 0,
            "removed_user_jobs": 0, "global_apt_modified": False,
            "other_projects_modified": False}
    if apply:
        if not shutil.rmtree.avoids_symlink_attacks:
            raise RuntimeError("F12_FD_SAFE_DELETE_REQUIRED")
        # Reuse the preexisting audited Ferrari algorithm: remove _cacache
        # only after checking ownership, symlinks and active npm processes.
        info["npm_cache_removed"] = audited(ROOT, apply=True)["cache_removed"]
        for child in targets:
            if child.is_symlink() or not child.is_dir() or busy(child):
                raise RuntimeError("F12_SMOKE_RUN_CHANGED")
            if not all((child / x).is_file() and not (child / x).is_symlink() for x in SMOKE_MARKERS):
                raise RuntimeError("F12_SMOKE_RUN_MARKERS_CHANGED")
            shutil.rmtree(child)
            info["removed_gui_smoke_run_ids"].append(child.name)
    guard()
    return info


def env(work):
    e = os.environ.copy()
    e.update({"HOME": str(work), "TMPDIR": str(work), "XDG_CACHE_HOME": str(work),
              "XDG_CONFIG_HOME": str(work), "XDG_DATA_HOME": str(work),
              "XDG_RUNTIME_DIR": str(work), "QT_QPA_PLATFORM": "offscreen",
              "LIBGL_ALWAYS_SOFTWARE": "1", "OMP_NUM_THREADS": "2",
              "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1",
              "HTTP_PROXY": "http://127.0.0.1:9",
              "HTTPS_PROXY": "http://127.0.0.1:9",
              "ALL_PROXY": "socks5://127.0.0.1:9",
              "NO_PROXY": "127.0.0.1,localhost", "no_proxy": "127.0.0.1,localhost"})
    for key in ("PYTHONPATH", "PYTHONHOME", "LD_LIBRARY_PATH", "LD_PRELOAD"):
        e.pop(key, None)
    return e


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def ytdlp_test(work):
    sys.path.insert(0, str(ROOT / "current"))
    from engine import ferrari, tool_runtime
    ytdlp = tool_runtime.executable("ytdlp", "yt-dlp")
    ffmpeg = ferrari._exe("ffmpeg")
    if not ytdlp or not Path(ytdlp).resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("F12_YTDLP_NOT_PRIVATE")
    source = work / "synthetic.mp4"
    p = subprocess.run([ffmpeg, "-hide_banner", "-nostdin", "-loglevel", "error", "-y",
                        "-f", "lavfi", "-i", "color=c=blue:s=160x90:r=2:d=1",
                        "-c:v", "mpeg4", "-an", "-t", "1", str(source)],
                       cwd=work, env=env(work), capture_output=True, text=True, timeout=35)
    if p.returncode or not source.is_file() or source.stat().st_size < 250:
        raise RuntimeError("F12_SYNTHETIC_MP4_FAILED:" + p.stderr[-200:])
    contents = source.read_bytes()
    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/synthetic.mp4":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "video/mp4")
            self.send_header("Content-Length", str(len(contents)))
            self.end_headers()
            self.wfile.write(contents)
        def log_message(self, fmt, *args):
            pass
    server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        target = work / "downloaded.mp4"
        url = "http://127.0.0.1:" + str(server.server_address[1]) + "/synthetic.mp4"
        p = subprocess.run([str(ytdlp), "--ignore-config", "--no-playlist",
                            "--no-progress", "--no-warnings", "--no-part",
                            "--socket-timeout", "8", "--retries", "1",
                            "--proxy", "", "-o", str(target), url],
                           cwd=work, env=env(work), capture_output=True, text=True, timeout=65)
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
    if p.returncode or not target.is_file():
        raise RuntimeError("F12_YTDLP_REAL_FAILED:" + (p.stderr or p.stdout)[-300:])
    if digest(source) != digest(target) or source.stat().st_size != target.stat().st_size:
        raise RuntimeError("F12_YTDLP_CONTENT_MISMATCH")
    return {"status": "pass", "private_executable": str(ytdlp),
            "mode": "real_mp4_download_localhost_only",
            "input_bytes": source.stat().st_size,
            "output_bytes": target.stat().st_size, "sha256_match": True,
            "external_network_used": False, "full_site_coverage_certified": False}


def freecad_test(work):
    sys.path.insert(0, str(ROOT / "current"))
    from engine import tool_runtime
    exe = tool_runtime.executable("freecad")
    if not exe or not Path(exe).resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("F12_FREECAD_NOT_PRIVATE")
    path = Path(exe)
    if not os.access(path, os.X_OK) or path.stat().st_size < 15_000_000:
        raise RuntimeError("F12_FREECAD_APPIMAGE_INVALID")
    if shutil.disk_usage(ROOT).free < 4 * 1024**3:
        raise RuntimeError("F12_FREECAD_DISK_GUARD")
    p = subprocess.run([str(path), "--appimage-extract"], cwd=work, env=env(work),
                       capture_output=True, text=True, timeout=200)
    if p.returncode:
        raise RuntimeError("F12_FREECAD_EXTRACT_FAILED:" + (p.stderr or p.stdout)[-350:])
    root = work / "squashfs-root"
    candidates = [root / "usr/bin/FreeCADCmd", root / "usr/local/bin/FreeCADCmd",
                  root / "bin/FreeCADCmd", root / "usr/bin/freecadcmd"]
    cli = next((c for c in candidates if c.is_file() and os.access(c, os.X_OK)
                and c.resolve(strict=True).is_relative_to(root.resolve(strict=True))), None)
    if cli is None:
        raise RuntimeError("F12_FREECAD_HEADLESS_CLI_MISSING")
    native = work / "box.FCStd"
    step = work / "box.step"
    macro = work / "box.py"
    macro.write_text("import FreeCAD as App\nimport Part\n"
                     "doc=App.newDocument('FerrariF12')\n"
                     "box=doc.addObject('Part::Box','Box')\n"
                     "box.Length=15.0\nbox.Width=20.0\nbox.Height=10.0\n"
                     "doc.recompute()\nassert abs(box.Shape.Volume-3000.0)<0.001\n"
                     "doc.saveAs(" + repr(str(native)) + ")\n"
                     "Part.export([box]," + repr(str(step)) + ")\n"
                     "print('F12_VOLUME=3000')\n", encoding="utf-8")
    p = subprocess.run([str(cli), str(macro)], cwd=work, env=env(work),
                       capture_output=True, text=True, timeout=100)
    if p.returncode or not native.is_file() or not step.is_file():
        raise RuntimeError("F12_FREECAD_REAL_EXPORT_FAILED:" + (p.stderr or p.stdout)[-450:])
    if native.stat().st_size < 500 or step.stat().st_size < 250:
        raise RuntimeError("F12_FREECAD_EMPTY_OUTPUT")
    with zipfile.ZipFile(native) as z:
        if z.testzip() is not None or "Document.xml" not in z.namelist():
            raise RuntimeError("F12_FREECAD_FCSTD_INVALID")
    if b"ISO-10303-21" not in step.read_bytes()[:120]:
        raise RuntimeError("F12_FREECAD_STEP_INVALID")
    return {"status": "pass", "mode": "parametric_box_to_fcstd_step",
            "private_executable": str(exe), "volume_mm3": 3000,
            "fcstd_bytes": native.stat().st_size, "step_bytes": step.stat().st_size,
            "interactive_gui_certified": False}


def certify():
    guard()
    results = {}
    for name, fn in (("yt-dlp", ytdlp_test), ("freecad", freecad_test)):
        try:
            with tempfile.TemporaryDirectory(prefix=".f12-" + name + "-", dir=ROOT / ".runtime") as t:
                results[name] = fn(Path(t))
        except Exception as e:
            results[name] = {"status": "not_certified", "reason": str(e)[-500:]}
    guard()
    return {"mode": "certify", "tools": results,
            "passed": sum(v["status"] == "pass" for v in results.values()),
            "tested": len(results), "permanent_files_added": False,
            "global_apt_modified": False, "other_projects_modified": False}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--mode", choices=("preview", "apply", "certify"), required=True)
    args = p.parse_args()
    try:
        before = services()
        data = certify() if args.mode == "certify" else clean(args.mode == "apply")
        after = services()
        if before != after:
            raise RuntimeError("F12_PROTECTED_SERVICES_CHANGED")
        data.update({"status": "PASS", "active": ACTIVE, "fallback": FALLBACK,
                     "protected_services": "8/8_PASS"})
        print(json.dumps(data, sort_keys=True), flush=True)
        return 0
    except Exception as e:
        print(json.dumps({"status": "BLOCKED", "mode": args.mode,
                          "error": str(e)[-600:]}, sort_keys=True), flush=True)
        return 3


if __name__ == "__main__":
    sys.exit(main())
