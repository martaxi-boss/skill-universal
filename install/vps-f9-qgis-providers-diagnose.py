#!/usr/bin/env python3
"""Ferrari F9: isolate QGIS/OGR crashes and PDAL HDF5 loader gaps (read-only).

Actual QGIS and GDAL probes use *separate* processes on a synthetic GeoJSON.
Any C++ abort remains isolated. Nothing is installed, removed, or written
outside Ferrari/.runtime, and a diagnostics PASS is not a provider PASS.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import resource
import signal
import subprocess
import sys
import tempfile

ROOT = Path("/srv/projects/skill-universal")
TARGET = ROOT / "tools/qgis-4.2.3-condaforge"
RUNTIME = ROOT / ".runtime"
ACTIVE = "7bf6dcecf15da26502c5969b5eee54d5e116fc32"
FALLBACK = "952b0a75ba798471b07053677d53791bd078ed56"
OPTIONAL_PLUGINS = (
    "libpdal_plugin_reader_hdf.so",
    "libpdal_plugin_reader_icebridge.so",
)

GDAL_PROBE = r"""
import json,sys
from osgeo import ogr,gdal
dataset=ogr.Open(sys.argv[1],0)
assert dataset is not None, "GDAL OGR Open failed"
layer=dataset.GetLayerByIndex(0)
assert layer is not None and layer.GetFeatureCount()==1, "GDAL invalid layer"
obj={"driver":dataset.GetDriver().GetName(),"count":layer.GetFeatureCount(),
     "gdal_version":gdal.VersionInfo()}
assert obj["driver"]=="GeoJSON", "Unexpected GDAL driver"
print(json.dumps(obj,sort_keys=True),flush=True)
"""

QGIS_OGR_PROBE = r"""
import json,sys
from qgis.core import QgsApplication,QgsVectorLayer
QgsApplication.setPrefixPath(sys.argv[2],True)
app=QgsApplication([],False)
app.initQgis()
layer=QgsVectorLayer(sys.argv[1],"ferrari-synthetic-ogr","ogr")
assert layer.isValid(), "QGIS OGR layer invalid"
assert layer.featureCount()==1, "QGIS OGR wrong feature count"
print(json.dumps({"valid":True,"features":1},sort_keys=True),flush=True)
"""

def require(condition: bool, failure: str) -> None:
    if not condition:
        raise RuntimeError(failure)

def guard() -> None:
    require(os.geteuid()!=0,"F9_QGIS_PROVIDER_AUDIT_NO_ROOT")
    for d in (ROOT, TARGET, RUNTIME):
        require(d.is_dir() and not d.is_symlink(),"F9_QGIS_UNSAFE_PRIVATE_ROOT")
    current=ROOT/"current"
    require(current.is_symlink()
            and current.resolve(strict=True)==ROOT/"releases"/ACTIVE,
            "F9_QGIS_RELEASE_DRIFT")
    require((ROOT/"releases"/FALLBACK/"engine/ferrari.py").is_file(),
            "F9_QGIS_FALLBACK_MISSING")
    manifest=json.loads((current/"engine/catalog.json").read_text(encoding="utf-8"))
    require(manifest["counts"]["all_catalog_entries"]==450
            and len(manifest["tools"])==173 and len(manifest["functions"])==272,
            "F9_QGIS_CATALOG_DRIFT")
    exe=TARGET/"bin/python"
    require(exe.is_file() and os.access(exe,os.X_OK)
            and exe.resolve().is_relative_to(TARGET),"F9_QGIS_PRIVATE_PYTHON_MISSING")
    require((TARGET/"conda-meta").is_dir(),"F9_QGIS_CONDA_PROVENANCE_MISSING")
    require((TARGET/"lib").is_dir(),"F9_QGIS_PRIVATE_LIBRARY_PATH_MISSING")

def env(work: Path) -> dict[str,str]:
    result={k:v for k,v in os.environ.items()
            if k not in {"LD_LIBRARY_PATH","PYTHONPATH","QT_PLUGIN_PATH",
                         "QT_QPA_PLATFORM_PLUGIN_PATH","GDAL_DRIVER_PATH"}}
    dirs=(TARGET/"share/qgis/python",TARGET/"share/qgis/python/plugins")
    result.update({
        "HOME":str(work),"TMPDIR":str(work),"XDG_CACHE_HOME":str(work),
        "XDG_CONFIG_HOME":str(work),"XDG_DATA_HOME":str(work),
        "XDG_RUNTIME_DIR":str(work),"PYTHONNOUSERSITE":"1",
        "QT_QPA_PLATFORM":"offscreen","LIBGL_ALWAYS_SOFTWARE":"1",
        "QGIS_PREFIX_PATH":str(TARGET),"LD_LIBRARY_PATH":str(TARGET/"lib"),
        "PYTHONPATH":os.pathsep.join(str(p) for p in dirs if p.is_dir()),
        "GDAL_DATA":str(TARGET/"share/gdal"),
        "PROJ_DATA":str(TARGET/"share/proj"),
        "PATH":str(TARGET/"bin")+":/usr/bin:/bin",
        "HTTP_PROXY":"http://127.0.0.1:9",
        "HTTPS_PROXY":"http://127.0.0.1:9",
        "ALL_PROXY":"socks5://127.0.0.1:9",
        "CPL_VSIL_CURL_ALLOWED_EXTENSIONS":"",
        "OMP_NUM_THREADS":"2",
    })
    return result

def sample(path:Path) -> None:
    # Public synthetic geometry: no real addresses, maps or user data.
    ring=[[0,0],[1,0],[1,1],[0,1],[0,0]]
    geo={"type":"FeatureCollection","features":[
        {"type":"Feature","properties":{"synthetic":True},
         "geometry":{"type":"Polygon","coordinates":[ring]}}]}
    path.write_text(json.dumps(geo,sort_keys=True),encoding="utf-8")

def check_process(label:str, source:str, test_data:Path, environment:dict) -> dict:
    cmd=[str(TARGET/"bin/python"),"-B","-c",source,str(test_data),str(TARGET)]
    p=subprocess.Popen(cmd,cwd=test_data.parent,env=environment,
                       text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                       start_new_session=True)
    timed_out=False
    try:
        out,err=p.communicate(timeout=40)
    except subprocess.TimeoutExpired:
        timed_out=True
        os.killpg(p.pid,signal.SIGKILL)
        out,err=p.communicate(timeout=6)
    outcome=None
    if p.returncode==0 and not timed_out:
        try:
            outcome=json.loads(out.strip().splitlines()[-1])
        except (ValueError,IndexError):
            pass
    diagnostic=(err or "").strip()[-450:]
    diagnostic=re.sub(re.escape(str(ROOT)),"<FERRARI>",diagnostic)
    return {"probe":label, "success":bool(outcome is not None),
            "exit_code":p.returncode, "timed_out":timed_out,
            "result":outcome,
            "stderr_tail":diagnostic,
            "host_persisted":False}

def optional_provider_paths() -> dict[str,Path]:
    # Inspect only files in the QGIS lib tree, never traverse other projects.
    lib=TARGET/"lib"
    found={}
    visits=0
    for base,dirs,files in os.walk(lib,followlinks=False):
        dirs[:]=[d for d in dirs if not (Path(base)/d).is_symlink()]
        visits+=len(files)
        require(visits<260000,"F9_QGIS_PROVIDER_TREE_LIMIT")
        for filename in OPTIONAL_PLUGINS:
            if filename in files and filename not in found:
                candidate=Path(base)/filename
                if candidate.is_file() and not candidate.is_symlink() and candidate.resolve().is_relative_to(lib):
                    found[filename]=candidate
        if len(found)==len(OPTIONAL_PLUGINS):
            break
    return found

def optional_linker_audit(environment:dict) -> dict:
    lib=TARGET/"lib"
    available=sorted(p.name for p in lib.glob("libhdf5_cpp.so*")
                     if p.is_file() and p.resolve().is_relative_to(lib))
    conda=[]
    for p in sorted((TARGET/"conda-meta").glob("*hdf5*.json")):
        if not p.is_file() or p.is_symlink() or p.stat().st_size>500000:
            continue
        meta=json.loads(p.read_text(encoding="utf-8"))
        conda.append({"name":str(meta.get("name",""))[:80],
                      "version":str(meta.get("version",""))[:40],
                      "build":str(meta.get("build",""))[:80]})
    audit={}
    for name,path in optional_provider_paths().items():
        r=subprocess.run(["/usr/bin/ldd",str(path)],capture_output=True,
                         text=True,env=environment,timeout=30,check=False)
        missing=sorted(set(re.findall(r"\b([A-Za-z0-9_.+-]+)\s+=>\s+not found\b",
                                      (r.stdout or "")+(r.stderr or ""))))
        audit[name]={"private_file_present":True,
                     "ldd_exit_code":r.returncode,
                     "unresolved_sonames":missing,
                     "linked_private_library_count":(r.stdout or "").count(str(TARGET))}
    for name in OPTIONAL_PLUGINS:
        audit.setdefault(name,{"private_file_present":False,
                               "unresolved_sonames":[],
                               "ldd_exit_code":None,
                               "linked_private_library_count":0})
    return {"private_hdf5_cpp_sonames":available,
            "private_hdf5_conda_metadata":conda,
            "optional_plugins":audit,
            "all_transitive_dependencies_certified":False}

def diagnose()->dict:
    guard()
    # Prevent aborting C++ library tests from producing enormous core dumps.
    resource.setrlimit(resource.RLIMIT_CORE,(0,0))
    with tempfile.TemporaryDirectory(prefix=".f9-qgis-providers-",dir=RUNTIME) as td:
        work=Path(td)
        geojson=work/"synthetic-geojson.json"
        sample(geojson)
        environment=env(work)
        dependency=optional_linker_audit(environment)
        gdal=check_process("gdal_ogr",GDAL_PROBE,geojson,environment)
        qgis=check_process("qgis_ogr",QGIS_OGR_PROBE,geojson,environment)
    current=ROOT/"current"
    require(current.resolve(strict=True)==ROOT/"releases"/ACTIVE,
            "F9_QGIS_RELEASE_CHANGED_DURING_TEST")
    return {"status":"diagnostic_complete","mode":"read_only",
            "active_release":ACTIVE,"fallback":FALLBACK,"catalog_entries":450,
            "gdal_ogr_probe":gdal,"qgis_ogr_probe":qgis,"pdal_loader":dependency,
            "full_qgis_certified":False,"gui_certified":False,
            "provider_issue_resolved":bool(gdal["success"] and qgis["success"]
                                         and all(not item["unresolved_sonames"]
                                         for item in dependency["optional_plugins"].values())
                                         and all(item["private_file_present"]
                                         for item in dependency["optional_plugins"].values())),
            "global_apt_changed":False,"other_projects_changed":False,
            "test_artifacts_cleaned":True}

if __name__=="__main__":
    if sys.argv[1:]!=["--diagnose"]:
        raise SystemExit("F9_QGIS_DIAGNOSE_ONLY")
    try:
        print(json.dumps(diagnose(),sort_keys=True),flush=True)
        print("FERRARI_QGIS_PROVIDERS_DIAGNOSTIC=COMPLETE",file=sys.stderr)
    except (OSError,RuntimeError,subprocess.SubprocessError,ValueError) as exc:
        print(json.dumps({"status":"blocked","reason":str(exc)[-350:],
                          "global_apt_changed":False,
                          "other_projects_changed":False}),flush=True)
        sys.exit(3)
