#!/usr/bin/env python3
"""Final F6 project-local residue cleanup: 4 copied Python launchers, 13 dead links.

Do not remove any real file, package, service, data or project directory.
Run as the Ferrari non-root owner via the existing pinned GitHub Actions/SSH.
--preview is read-only; --apply has a pre-written Ferrari-local rollback manifest.
"""
from __future__ import annotations
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
ACTIVE = "146145d5ada9c13e368df18727e4dbf4f5807664"
FALLBACK = "40c0e1cdf31b1fe9589ad8be90e5eac06eec2856"
PYTHON = ROOT / "runtimes/python3.12/bin/python3.12"
BACKUP = ROOT / ".runtime/phase6-launcher-and-deadlinks-20261105.json"

LAUNCHERS = (
    "tools/ubuntu-cli/bin/ansible-inventory",
    "tools/ubuntu-cli/bin/binwalk",
    "tools/ubuntu-cli/bin/ebook-convert",
    "tools/ubuntu-cli/bin/ocrmypdf",
)
DEADLINKS = (
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/d3",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/moment",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/jquery",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/jquery-hotkeys",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/moment-timezone",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/eonasdan-bootstrap-datetimepicker",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/mustache",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/popper.js",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/rickshaw",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/bootstrap4",
    "tools/ferrari-services/prometheus/usr/share/prometheus/web/static/vendor/bootstrap4-glyphicons/fonts/glyphicons",
    "tools/ferrari-services/valkey-server/usr/share/doc/valkey-server/00-RELEASENOTES.gz",
    "tools/ferrari-services/valkey-server/usr/share/doc/valkey-tools/00-RELEASENOTES.gz",
)


def inside(p: Path):
    try:
        return p.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
    except (OSError, RuntimeError):
        return False


def atomic_file(path: Path, data: bytes, mode: int):
    fd, name = tempfile.mkstemp(prefix=".phase6-last-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.lexists(name):
            os.unlink(name)


def boundaries():
    if ROOT.is_symlink() or not ROOT.is_dir() or os.geteuid()==0:
        raise RuntimeError("Unsafe Ferrari root/owner")
    if not (ROOT / "current").is_symlink() or (ROOT / "current").resolve(strict=True) != ROOT / "releases" / ACTIVE:
        raise RuntimeError("Active Ferrari release changed")
    if not (ROOT / "releases" / FALLBACK / "engine/ferrari.py").is_file():
        raise RuntimeError("Certified Ferrari rollback missing")
    if PYTHON.is_symlink() or not PYTHON.is_file() or not inside(PYTHON) or not os.access(PYTHON,os.X_OK):
        raise RuntimeError("Private Ferrari Python missing")


def check_candidates():
    boundaries()
    copied = {}
    for rel in LAUNCHERS:
        p = ROOT / rel
        if p.is_symlink() or not p.is_file() or not inside(p) or not os.access(p,os.X_OK):
            raise RuntimeError("Unexpected Ferrari launch binary: " + rel)
        blob = p.read_bytes()
        if not 0 < len(blob) < 65536:
            raise RuntimeError("Unexpected private script size: " + rel)
        shebang = blob.split(b"\n",1)[0]
        private_header = ("#!"+str(PYTHON)).encode()
        # Debian launchers legitimately include flags such as -Es or -s.
        # Only accept one short interpreter-option token; preserve it exactly.
        legacy = re.fullmatch(rb"#!/usr/bin/python3(?:\.12)?([ \t]+-[A-Za-z]{1,10})?", shebang)
        local = re.fullmatch(re.escape(private_header) + rb"([ \t]+-[A-Za-z]{1,10})?", shebang)
        if legacy:
            trailing = legacy.group(1) or b""
            needs_change = True
        elif local:
            trailing = local.group(1) or b""
            needs_change = False
        else:
            raise RuntimeError("Unexpected launcher interpreter: " + rel)
        copied[rel] = {"data":blob,"mode":stat.S_IMODE(p.stat().st_mode),
                       "trailing":trailing,"needs_change":needs_change}
    links = {}
    for rel in DEADLINKS:
        p = ROOT / rel
        if not inside(p.parent) or not p.is_symlink() or p.exists():
            raise RuntimeError("Expected Ferrari-owned broken symlink: " + rel)
        links[rel] = os.readlink(p)
    return copied,links


def no_service_consumers():
    prefix=str(ROOT / "tools/ferrari-services")+"/"
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal() or proc.name==str(os.getpid()):
            continue
        try:
            exe=os.readlink(proc/"exe")
            cwd=os.readlink(proc/"cwd")
        except (OSError,PermissionError):
            continue
        if exe.startswith(prefix) or cwd.startswith(prefix):
            raise RuntimeError("Ferrari vendored service is live; leave its links unchanged")


def check_actions():
    import importlib
    sys.path.insert(0,str(ROOT/"current"))
    runtime=importlib.import_module("engine.tool_runtime")
    specs=runtime.specs()
    if len(specs)!=40:
        raise RuntimeError("Ferrari action count changed")
    for action in specs.values():
        p=runtime.executable(action["tool"],action["binary"])
        if not p or not inside(Path(p)):
            raise RuntimeError("Ferrari action lost an isolated executor")
    return True


def run(mode: str):
    if mode not in ("--preview","--apply"):
        raise RuntimeError("Expected preview or apply")
    copied,links=check_candidates()
    proposed=sum(x["needs_change"] for x in copied.values())
    report={
        "schema":1,"phase":6,"mode":mode.removeprefix("--"),
        "release":ACTIVE,"fallback":FALLBACK,
        "private_launchers_checked":len(copied),
        "launchers_with_global_shebang":proposed,
        "broken_private_resource_links":len(links),
        "packages_removed":0,"service_changes":0,
        "other_projects_modified":False,
        "private_files_changed":0,
        "result":"preview_only",
    }
    if mode=="--preview":
        return report
    if BACKUP.exists() or BACKUP.is_symlink():
        raise RuntimeError("Previous phase-6 cleanup marker exists; no blind repeat")
    no_service_consumers()
    changes=[]
    # Store scope and original symlink/shebang data in Ferrari before edits.
    backup={"schema":1,"mode":"private-only","launcher_shebangs":{
        rel:entry["data"].split(b"\n",1)[0].decode("ascii")
        for rel,entry in copied.items()},
        "broken_link_targets":links}
    atomic_file(BACKUP,json.dumps(backup,sort_keys=True,indent=2).encode(),0o600)
    try:
        for rel,entry in copied.items():
            if entry["needs_change"]:
                old=entry["data"]
                first,rest=old.split(b"\n",1)
                modified=("#!"+str(PYTHON)).encode()+entry["trailing"]+b"\n"+rest
                changes.append(("file",ROOT/rel,old,entry["mode"]))
                atomic_file(ROOT/rel,modified,entry["mode"])
        for rel,target in links.items():
            p=ROOT/rel
            changes.append(("link",p,target,None))
            p.unlink()
        boundaries()
        for rel in LAUNCHERS:
            p=ROOT/rel
            if not p.read_bytes().startswith(("#!"+str(PYTHON)).encode()):
                raise RuntimeError("Launcher still resolves to global Python")
        if any(os.path.lexists(ROOT/rel) for rel in DEADLINKS):
            raise RuntimeError("Broken Ferrari vendor links remained")
        check_actions()
        report["private_files_changed"]=len(changes)
        report["result"]="private_launchers_and_dead_links_cleaned"
        return report
    except BaseException:
        for typ,p,old,mode in reversed(changes):
            if typ=="file":
                atomic_file(p,old,mode)
            elif not os.path.lexists(p):
                os.symlink(old,p)
        BACKUP.unlink(missing_ok=True)
        raise


if __name__ == "__main__":
    try:
        print(json.dumps(run(sys.argv[1] if len(sys.argv)==2 else ""),sort_keys=True))
    except (OSError,RuntimeError,ValueError,UnicodeDecodeError) as exc:
        print("FERRARI_PHASE6_FINAL_CLEANUP_BLOCKED="+type(exc).__name__+":"+str(exc)[:160],file=sys.stderr)
        sys.exit(2)
