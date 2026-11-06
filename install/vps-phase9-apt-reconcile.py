#!/usr/bin/env python3
"""Phase-9 guarded de-globalization of eight packages with Ferrari-private executors.

Modes:
  backup: read-only on APT (downloads signed distribution packages into the
          Ferrari-owned rollback folder, no uninstall).
  apply: re-verify everything, purge *only* eight allowlisted APT packages,
         check Ferrari action catalog + eight protected services, attempt
         version-locked local rollback on postflight failure.

No autoremove, no Git reset, no edits to other projects, no global installs.
The separate eight packages without Ferrari-private alternatives are untouched.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time

ROOT = Path("/srv/projects/skill-universal")
EXPECTED_SHA = "f1f3b03525adec7018d7d629243e7b0fbb7f5087"
BACKUP = ROOT / ".runtime" / "phase9-apt-eight-rollback-20261106"
NAMES = ("ansible", "blender", "calibre", "darktable", "gimp", "kdenlive", "libreoffice", "openscad")
STAY = ("yt-dlp", "librecad", "qgis", "audacity", "obs-studio", "solvespace", "synfigstudio", "openshot-qt")
SERVICES = ("pink-iptv-backend", "pink-vpn", "fadego-staging", "lowcost-europa",
            "pm2-iptvpn-bot", "pm2-telegram-robot-leads", "nginx", "postgresql@16-main")
BINARIES = {
    "ansible": ("ansible", "ansible-inventory"),
    "blender": ("blender", "blender"),
    "calibre": ("calibre", "ebook-convert"),
    "darktable": ("darktable", "darktable-cli"),
    "gimp": ("gimp", "gimp-console-2.10"),
    "kdenlive": ("kdenlive", "melt"),
    "libreoffice": ("libreoffice", "soffice"),
    "openscad": ("openscad", "openscad"),
}


def command(argv, *, cwd=None, timeout=120):
    env = os.environ.copy()
    env.update(LC_ALL="C", LANG="C", DEBIAN_FRONTEND="noninteractive",
               DEBIAN_PRIORITY="critical", NEEDRESTART_MODE="l")
    return subprocess.run(argv, cwd=cwd, capture_output=True, text=True,
                          timeout=timeout, env=env, check=False)


def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def guard():
    require(os.geteuid()==0, "F9_NEEDS_ROOT_FOR_OS_APT")
    require(ROOT.is_dir() and not ROOT.is_symlink() and (ROOT / ".runtime").is_dir()
            and not (ROOT / ".runtime").is_symlink(), "F9_ROOT_NOT_PRIVATE")
    release = ROOT / "current"
    require(release.is_symlink() and release.resolve().name==EXPECTED_SHA
            and release.resolve().parent==(ROOT/"releases").resolve(), "F9_RELEASE_CHANGED")
    require((ROOT/"releases/a266b25e06a9c8acf1fdc940d22b99070cd17ded/engine/ferrari.py").is_file(),
            "F9_KNOWN_ROLLBACK_MISSING")


def services():
    values = {}
    for name in SERVICES:
        p = command(["systemctl", "is-active", name], timeout=9)
        values[name] = p.stdout.strip() if p.returncode==0 else "failed"
    require(all(x=="active" for x in values.values()), "F9_PROTECTED_SERVICE_FAILED")
    return values


def installed_version(name):
    p = command(["dpkg-query", "-W", "-f=${Status}|${Version}", name], timeout=8)
    if p.returncode != 0 or not p.stdout.startswith("install ok installed|"):
        return None
    return p.stdout.split("|",1)[1].strip()


def policies():
    result = {}
    for name in NAMES:
        version = installed_version(name)
        require(version, "F9_MISSING_EXPECTED_OS_PACKAGE:"+name)
        p=command(["apt-cache","policy",name],timeout=8)
        candidate = next((x.strip().split(":",1)[1].strip() for x in p.stdout.splitlines()
                          if x.strip().startswith("Candidate:")),None)
        require(candidate==version, "F9_EXACT_ROLLBACK_VERSION_NOT_AVAILABLE:"+name)
        result[name] = version
    require(all(installed_version(x) for x in STAY), "F9_NONMIGRATED_PROGRAM_MISSING")
    return result


def private_catalog():
    sys.path.insert(0, str(ROOT/"current"))
    from engine import tool_runtime
    specs=tool_runtime.specs()
    require(len(specs)==40, "F9_ACTION_REGISTRY_CHANGED")
    require(all(tool_runtime.executable(x["tool"],x["binary"]) for x in specs.values()),
            "F9_FERRARI_PRIVATE_ACTION_MISSING")
    alternatives={}
    for pkg,(tool,binary) in BINARIES.items():
        x=tool_runtime.executable(tool,binary)
        require(x is not None, "F9_PRIVATE_ALTERNATIVE_MISSING:"+pkg)
        path=Path(x)
        require(path.is_file() and path.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)),
                "F9_PRIVATE_ALTERNATIVE_OUTSIDE_PROJECT:"+pkg)
        alternatives[pkg]=str(path)
    return alternatives


def direct_global_users():
    exe_names=set()
    for pkg in NAMES:
        p=command(["dpkg-query","-L",pkg],timeout=10)
        for raw in p.stdout.splitlines():
            if raw.startswith(("/usr/bin/","/usr/sbin/","/usr/libexec/")):
                try:
                    f=Path(raw)
                    if f.is_file() and os.access(f,os.X_OK):
                        exe_names.add(str(f.resolve()))
                except OSError:pass
    observed = 0
    for proc in Path("/proc").iterdir():
        if not proc.name.isdecimal():continue
        try:
            exe=os.readlink(proc/"exe")
            if exe in exe_names:observed+=1
        except OSError:pass
    require(observed==0, "F9_OS_EXECUTABLE_IN_USE")
    return len(exe_names)


def simulation():
    p=command(["apt-get","-s","purge",*NAMES],timeout=110)
    require(p.returncode==0, "F9_APT_SIMULATION_FAILED")
    steps=[line.split()[:2] for line in p.stdout.splitlines()
           if line.startswith(("Purg ","Remv ","Inst ","Conf "))]
    removal=[x[1] for x in steps if len(x)>1 and x[0] in ("Purg","Remv")]
    installs=[x[1] for x in steps if len(x)>1 and x[0]=="Inst"]
    require(len(removal)==len(NAMES) and set(removal)==set(NAMES) and not installs,
            "F9_APT_SIMULATION_WOULD_CHANGE_OTHER_PACKAGES")
    return removal


def digest(path):
    h=hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024*1024),b""):
            h.update(part)
    return h.hexdigest()


def backup():
    guard()
    services()
    versions=policies()
    paths=private_catalog()
    direct_global_users()
    simulation()
    require(not BACKUP.exists() and not BACKUP.is_symlink(), "F9_BACKUP_ALREADY_EXISTS")
    root=ROOT/".runtime"
    stage=Path(tempfile.mkdtemp(prefix=".f9-apt-eight-stage-",dir=root))
    saved={}
    try:
        stage.chmod(0o700)
        for pkg in NAMES:
            p=command(["apt-get","download",pkg+"="+versions[pkg]],cwd=stage,timeout=180)
            require(p.returncode==0,"F9_APT_BACKUP_DOWNLOAD_FAILED:"+pkg)
            matches=[]
            for path in stage.iterdir():
                if not path.is_file() or path.is_symlink() or not path.name.endswith(".deb"):
                    continue
                q=command(["dpkg-deb","-f",str(path),"Package"],timeout=12)
                v=command(["dpkg-deb","-f",str(path),"Version"],timeout=12)
                if q.returncode==0 and v.returncode==0 and q.stdout.strip()==pkg and v.stdout.strip()==versions[pkg]:
                    matches.append(path)
            require(len(matches)==1,"F9_APT_ROLLBACK_ARCHIVE_AMBIGUOUS:"+pkg)
            path=matches[0]
            saved[pkg]={"file":path.name,"sha256":digest(path),"size":path.stat().st_size,
                        "version":versions[pkg]}
        manifest={"schema":1,"purpose":"F9_OFFLINE_APT_ROLLBACK","release":EXPECTED_SHA,
                  "packages":saved,"verified_ferrari_private_actions":40,
                  "private_alternatives":list(paths),"only_exact_eight":True}
        marker=stage/"manifest.json"
        marker.write_text(json.dumps(manifest,sort_keys=True,indent=2)+"\n")
        marker.chmod(0o600)
        for p in stage.iterdir():
            p.chmod(0o600)
            os.chown(p,1000,1000)
        os.chown(stage,1000,1000)
        os.rename(stage,BACKUP)
        return {"phase":9,"status":"rollback_archives_ready","packages_backed_up":len(saved),
                "backup_bytes":sum(x["size"] for x in saved.values()),"private_executors":40,
                "protected_services_active":8,"package_changes":0}
    except BaseException:
        if stage.exists() and not stage.is_symlink():shutil.rmtree(stage)
        raise


def load_backup():
    require(BACKUP.is_dir() and not BACKUP.is_symlink(), "F9_ROLLBACK_DIRECTORY_MISSING")
    marker=BACKUP/"manifest.json"
    require(marker.is_file() and not marker.is_symlink() and marker.stat().st_size<=25000,
            "F9_ROLLBACK_MANIFEST_INVALID")
    manifest=json.loads(marker.read_text())
    require(manifest.get("schema")==1 and manifest.get("release")==EXPECTED_SHA
            and manifest.get("only_exact_eight") is True, "F9_ROLLBACK_MANIFEST_MISMATCH")
    data=manifest.get("packages")
    require(isinstance(data,dict) and set(data)==set(NAMES), "F9_ROLLBACK_INCOMPLETE")
    for pkg in NAMES:
        item=data[pkg]
        require(isinstance(item,dict) and isinstance(item.get("file"),str)
                and re.fullmatch(r"[a-zA-Z0-9+_.%~-]{4,170}\.deb",item["file"]),
                "F9_ROLLBACK_FILE_NAME_INVALID")
        p=BACKUP/item["file"]
        require(p.is_file() and not p.is_symlink()
                and p.resolve().parent==BACKUP.resolve()
                and digest(p)==item["sha256"],
                "F9_ROLLBACK_ARCHIVE_DAMAGED:"+pkg)
        q=command(["dpkg-deb","-f",str(p),"Package"],timeout=12)
        v=command(["dpkg-deb","-f",str(p),"Version"],timeout=12)
        require(q.returncode==0 and v.returncode==0 and q.stdout.strip()==pkg and v.stdout.strip()==item["version"],
                "F9_ROLLBACK_ARCHIVE_CONTENT_MISMATCH")
    return data


def apply():
    guard()
    services()
    versions=policies()
    private_catalog()
    direct_global_users()
    simulation()
    packages=load_backup()
    require(all(versions[name]==packages[name]["version"] for name in NAMES),
            "F9_OS_PACKAGE_VERSIONS_CHANGED")
    report={"phase":9,"status":"started","packages_targeted":list(NAMES),
            "packages_removed":0,"other_projects_changed":False,
            "rollback_archive_preserved":True}
    p=command(["apt-get","-y","--no-install-recommends","purge",*NAMES],timeout=420)
    log=BACKUP/"apt-purge-private.log"
    log.write_text((p.stdout+"\n"+p.stderr)[-250000:])
    log.chmod(0o600)
    failure=None
    if p.returncode != 0:
        failure="F9_APT_PURGE_FAILED"
    else:
        try:
            require(all(installed_version(pkg) is None for pkg in NAMES),
                    "F9_SELECTED_GLOBAL_PACKAGES_STILL_PRESENT")
            require(all(installed_version(pkg) is not None for pkg in STAY),
                    "F9_UNCERTIFIED_GLOBAL_PACKAGES_WERE_TOUCHED")
            services()
            private_catalog()
            guard()
        except Exception as exc:
            failure=str(exc)[:140]
    if failure:
        files=[str(BACKUP/packages[name]["file"]) for name in NAMES]
        restore=command(["apt-get","-y","--no-install-recommends","install",*files],timeout=420)
        rlog=BACKUP/"apt-rollback-private.log"
        rlog.write_text((restore.stdout+"\n"+restore.stderr)[-250000:])
        rlog.chmod(0o600)
        recovered=(restore.returncode==0 and all(installed_version(n) for n in NAMES))
        report.update({"status":"failed_rolled_back" if recovered else "failed_rollback_incomplete",
                        "failure":failure,"rollback_success":recovered})
        print(json.dumps(report,sort_keys=True),flush=True)
        return 2
    report.update({"status":"private_eight_global_purged","packages_removed":len(NAMES),
                   "packages_preserved_without_full_private_alternative":len(STAY),
                   "private_actions_unchanged":40,"protected_services_active":8,
                   "ferrari_release_unchanged":True,
                   "apt_autoremove_executed":False})
    print(json.dumps(report,sort_keys=True),flush=True)
    return 0


if __name__ == "__main__":
    try:
        mode=sys.argv[1] if len(sys.argv)==2 else ""
        if mode=="--backup":
            print(json.dumps(backup(),sort_keys=True))
            sys.exit(0)
        if mode=="--apply":
            sys.exit(apply())
        raise ValueError("F9_MODE_MUST_BE_BACKUP_OR_APPLY")
    except Exception as e:
        print(json.dumps({"phase":9,"status":"blocked","type":type(e).__name__,
                          "reason":str(e)[:160]},sort_keys=True))
        sys.exit(3)
