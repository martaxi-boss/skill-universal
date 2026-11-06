#!/usr/bin/env python3
"""F9: close SolveSpace private Debian resource links with signed Ubuntu packages.

The extracted SolveSpace 3.1 package contains two relative resource links to
other Ubuntu packages. This installer verifies pinned signed-APT downloads,
extracts just the required data files *inside* the Ferrari-owned SolveSpace
tree, preserving the relative links. No sudo, APT install, or host writes.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT=Path("/srv/projects/skill-universal")
TARGET=ROOT/"tools/solvespace-3.1-ubuntu24"
RUNTIME=ROOT/".runtime"
PACKAGE_INFO={
    "libjs-three":{
        "version":"111+dfsg1-3",
        "bytes":1106842,
        "sha256":"ef7cc260f96bd469245f1f2405981e305f6bf001965cfd7a750e37dc5d87a963",
        "relative":"usr/share/javascript/three/three.js",
        "link":"usr/share/solvespace/threejs/three.js",
        "link_target":"../../javascript/three/three.js",
    },
    "unifont":{
        "version":"1:15.1.01-1build1",
        "bytes":5908726,
        "sha256":"f5d7516c5a430dc6ee8266fd333cc49339407865916462d608b8478b1e3a84a1",
        "relative":"usr/share/unifont/unifont.hex",
        "link":"usr/share/solvespace/fonts/unifont.hex",
        "link_target":"../../unifont/unifont.hex",
    },
}
MANIFEST=TARGET/"ferrari-private-resources.json"

def require(condition: bool,message: str) -> None:
    if not condition:
        raise RuntimeError(message)

def guard() -> None:
    require(os.geteuid()!=0,"F9_SOLVESPACE_RESOURCES_NO_ROOT")
    require(os.uname().machine=="x86_64","F9_SOLVESPACE_RESOURCES_ARCH")
    release=Path("/etc/os-release").read_text()
    require("ID=ubuntu" in release and 'VERSION_ID="24.04"' in release,
            "F9_SOLVESPACE_RESOURCES_UBUNTU_2404_ONLY")
    require(ROOT.resolve(strict=True)==Path("/srv/projects/skill-universal"),
            "F9_SOLVESPACE_RESOURCES_UNSAFE_ROOT")
    for path in (ROOT,ROOT/"tools",TARGET,RUNTIME):
        require(path.is_dir() and not path.is_symlink(),
                "F9_SOLVESPACE_RESOURCES_UNSAFE_DIRECTORY:"+str(path))
    require(MANIFEST.parent==TARGET,"F9_SOLVESPACE_RESOURCES_MANIFEST_OUTSIDE_PROJECT")

def hashed(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def apt_metadata(name: str) -> dict:
    info=PACKAGE_INFO[name]
    r=subprocess.run(["/usr/bin/apt-cache","show",name],capture_output=True,
                     text=True,check=False,timeout=25,env={"LC_ALL":"C","PATH":"/usr/bin:/bin"})
    require(r.returncode==0,"F9_SOLVESPACE_APT_CACHE_MISSING:"+name)
    for stanza in r.stdout.split("\n\n"):
        fields={}
        for line in stanza.splitlines():
            if ": " in line and not line.startswith((" ","\t")):
                k,v=line.split(": ",1)
                fields[k]=v
        if fields.get("Package") != name or fields.get("Version")!=info["version"]:
            continue
        require(fields.get("Architecture")=="all" and
                fields.get("SHA256")==info["sha256"] and
                fields.get("Size")==str(info["bytes"]),
                "F9_SOLVESPACE_RESOURCE_APT_METADATA_MISMATCH:"+name)
        return fields
    raise RuntimeError("F9_SOLVESPACE_RESOURCE_APT_VERSION_NOT_FOUND:"+name)

def source_link(name: str) -> Path:
    info=PACKAGE_INFO[name]
    link=TARGET/info["link"]
    require(link.is_symlink() and os.readlink(link)==info["link_target"],
            "F9_SOLVESPACE_EXPECTED_RELATIVE_LINK_MISSING:"+name)
    resolved=link.resolve(strict=False)
    require(resolved==TARGET/info["relative"] and
            resolved.is_relative_to(TARGET.resolve(strict=True)),
            "F9_SOLVESPACE_LINK_ESCAPES_PROJECT:"+name)
    return link

def verify_private_resource(name: str,expected_sha: str) -> dict:
    info=PACKAGE_INFO[name]
    source_link(name)
    path=TARGET/info["relative"]
    require(path.is_file() and not path.is_symlink() and
            path.resolve(strict=True).is_relative_to(TARGET.resolve(strict=True)),
            "F9_SOLVESPACE_RESOURCE_NOT_PRIVATE:"+name)
    require(hashed(path)==expected_sha,"F9_SOLVESPACE_RESOURCE_HASH_MISMATCH:"+name)
    require(source_link(name).is_file(),"F9_SOLVESPACE_RESOURCE_LINK_BROKEN:"+name)
    return {"package":name,"package_sha256":info["sha256"],"version":info["version"],
            "payload_sha256":expected_sha,"payload_bytes":path.stat().st_size,
            "private_path":str(path)}

def check() -> dict:
    guard()
    require(MANIFEST.is_file() and not MANIFEST.is_symlink() and
            MANIFEST.stat().st_size<6000,"F9_SOLVESPACE_RESOURCE_MANIFEST_MISSING")
    data=json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(data.get("source")=="ubuntu-24.04-signed-apt-index" and
            data.get("global_apt_changed") is False and
            data.get("gui_runtime_certified") is False,
            "F9_SOLVESPACE_RESOURCE_MANIFEST_INCORRECT")
    resources=data.get("resources")
    require(isinstance(resources,dict) and set(resources)==set(PACKAGE_INFO),
            "F9_SOLVESPACE_RESOURCE_MANIFEST_KEYS")
    results={}
    for name in PACKAGE_INFO:
        item=verify_private_resource(name,resources[name]["payload_sha256"])
        require(item==resources[name],"F9_SOLVESPACE_RESOURCE_MANIFEST_MISMATCH:"+name)
        results[name]=item
    return {"status":"two_private_resource_links_verified",
            "resources":results,"gui_runtime_certified":False,
            "dependency_isolation_certified":False,"global_apt_changed":False}

def fetch_and_extract(name: str,scratch: Path) -> tuple[Path,Path]:
    info=PACKAGE_INFO[name]
    apt_metadata(name)
    loc=scratch/name
    loc.mkdir(mode=0o700)
    env={"PATH":"/usr/bin:/bin","HOME":str(scratch),
         "TMPDIR":str(scratch),"DEBIAN_FRONTEND":"noninteractive","LC_ALL":"C"}
    r=subprocess.run(["/usr/bin/apt-get","download",name+"="+info["version"]],
                     cwd=loc,env=env,capture_output=True,text=True,timeout=180,check=False)
    require(r.returncode==0,"F9_SOLVESPACE_RESOURCE_DOWNLOAD_FAILED:"+name+":"+r.stderr[-160:])
    files=list(loc.glob("*.deb"))
    require(len(files)==1 and files[0].is_file() and not files[0].is_symlink(),
            "F9_SOLVESPACE_UNEXPECTED_DOWNLOAD:"+name)
    deb=files[0]
    require(deb.stat().st_size==info["bytes"] and hashed(deb)==info["sha256"],
            "F9_SOLVESPACE_RESOURCE_APT_SHA256_FAIL:"+name)
    out=loc/"unpacked"
    out.mkdir(mode=0o700)
    r=subprocess.run(["/usr/bin/dpkg-deb","-x",str(deb),str(out)],
                     env=env,capture_output=True,text=True,timeout=90,check=False)
    require(r.returncode==0,"F9_SOLVESPACE_RESOURCE_EXTRACT_FAIL:"+name+":"+r.stderr[-160:])
    data=out/info["relative"]
    require(data.is_file() and not data.is_symlink() and
            data.resolve(strict=True).is_relative_to(out.resolve(strict=True)),
            "F9_SOLVESPACE_EXPECTED_RESOURCE_NOT_IN_PACKAGE:"+name)
    return data,deb

def repair() -> dict:
    guard()
    if MANIFEST.exists() or MANIFEST.is_symlink():
        return check()
    require(not MANIFEST.is_symlink(),"F9_SOLVESPACE_RESOURCE_MANIFEST_UNSAFE")
    for name in PACKAGE_INFO:
        source_link(name)
        dest=TARGET/PACKAGE_INFO[name]["relative"]
        require(not dest.exists() and not dest.is_symlink(),
                "F9_SOLVESPACE_RESOURCE_DEST_CONFLICT:"+name)
    space=os.statvfs(RUNTIME)
    require(space.f_bavail*space.f_frsize>2*1024**3,
            "F9_SOLVESPACE_RESOURCE_DISK_TOO_LOW")
    installed=[]
    created_dirs=[]
    try:
        with tempfile.TemporaryDirectory(prefix=".f9-solvespace-res-",dir=RUNTIME) as td:
            scratch=Path(td)
            validated={}
            for name in PACKAGE_INFO:
                payload,archive=fetch_and_extract(name,scratch)
                validated[name]={"payload":payload,
                                 "hash":hashed(payload),"size":payload.stat().st_size}
            results={}
            for name in PACKAGE_INFO:
                item=validated[name]
                dest=TARGET/PACKAGE_INFO[name]["relative"]
                parents=[]
                parent=dest.parent
                while not parent.exists():
                    parents.append(parent)
                    parent=parent.parent
                require(parent.resolve(strict=True).is_relative_to(TARGET.resolve(strict=True)),
                        "F9_SOLVESPACE_RESOURCE_PARENT_ESCAPED")
                for p in reversed(parents):
                    p.mkdir(mode=0o700)
                    created_dirs.append(p)
                require(not dest.exists() and not dest.is_symlink(),
                        "F9_SOLVESPACE_RESOURCE_CONCURRENT_WRITE:"+name)
                shutil.copyfile(item["payload"],dest,follow_symlinks=False)
                dest.chmod(0o600)
                installed.append(dest)
                results[name]=verify_private_resource(name,item["hash"])
            data={"source":"ubuntu-24.04-signed-apt-index",
                  "global_apt_changed":False,"gui_runtime_certified":False,
                  "resources":results}
            with tempfile.NamedTemporaryFile(prefix=".f9-manifest-",dir=TARGET,
                                             delete=False) as tmp:
                staged=Path(tmp.name)
            try:
                staged.write_text(json.dumps(data,sort_keys=True,indent=2)+"\n")
                require(not MANIFEST.exists() and not MANIFEST.is_symlink(),
                        "F9_SOLVESPACE_RESOURCE_CONCURRENT_MANIFEST")
                os.replace(staged,MANIFEST)
            finally:
                if staged.exists():
                    staged.unlink()
        return check()
    except BaseException:
        if MANIFEST.is_file() and not MANIFEST.is_symlink():
            # Successful manifest publication is the commit point.
            return check()
        for path in reversed(installed):
            if (path.is_file() and not path.is_symlink() and
                    path.resolve(strict=True).is_relative_to(TARGET.resolve(strict=True))):
                path.unlink()
        for p in reversed(created_dirs):
            if p.is_dir() and not p.is_symlink():
                p.rmdir()
        raise

def main() -> int:
    p=argparse.ArgumentParser()
    g=p.add_mutually_exclusive_group(required=True)
    g.add_argument("--repair",action="store_true")
    g.add_argument("--check",action="store_true")
    args=p.parse_args()
    try:
        data=repair() if args.repair else check()
        print(json.dumps(data,sort_keys=True),flush=True)
        return 0
    except Exception as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)[-350:],
                          "global_apt_changed":False},sort_keys=True),flush=True)
        return 3

if __name__=="__main__":
    sys.exit(main())
