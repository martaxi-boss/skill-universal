#!/usr/bin/env python3
"""Single Ferrari-owned F7 VPS smoke, no second coordinator or paid provider.

The caller is the existing GitHub Actions -> SSH bridge with a pinned commit.
All created state and outputs remain in /srv/projects/skill-universal/.runtime.
The script never edits services, Nginx, APT or another project's directory.
"""
from __future__ import annotations

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import resource
import shutil
import subprocess
import sys
import time

ROOT = Path("/srv/projects/skill-universal")
F7_ACTIVE = sys.argv[1] if len(sys.argv)>1 else ""
F6_FALLBACK = "146145d5ada9c13e368df18727e4dbf4f5807664"
WORK = ROOT / ".runtime/phase7-cert-20261105"
KEY = "checkpoint-demo-20261105"


def guarded():
    if not re.fullmatch(r"[0-9a-f]{40}", F7_ACTIVE):
        raise RuntimeError("F7 expected release SHA must be pinned")
    if os.geteuid() == 0 or ROOT.is_symlink() or not ROOT.is_dir():
        raise RuntimeError("Ferrari non-root private directory required")
    if not (ROOT / "current").is_symlink() or (ROOT/"current").resolve(strict=True) != ROOT/"releases"/F7_ACTIVE:
        raise RuntimeError("Ferrari F7 candidate is not the active release")
    if not (ROOT/"releases"/F6_FALLBACK/"engine/ferrari.py").is_file():
        raise RuntimeError("Ferrari F6 rollback release is not preserved")
    if WORK.exists() or WORK.is_symlink():
        raise RuntimeError("Unexpected Ferrari phase 7 test workspace; no overwrite")
    if (ROOT/".runtime").is_symlink():
        raise RuntimeError("Ferrari runtime root cannot be symlinked")


def private_ruflo():
    manifest=ROOT/".runtime/npm/ruflo/node_modules/ruflo/package.json"
    private_modules=ROOT/".runtime/npm/ruflo/node_modules"
    cli=private_modules/".bin/ruflo"
    node=ROOT/"runtimes/node-22.23.4/bin/node"
    response={"optional":True,"private_cli_present":False,"version":"unknown",
              "local_cli_test":"not_run","model_or_provider_called":False,
              "agent_workflow_certified":False}
    if (not manifest.is_file() or manifest.is_symlink()
            or not private_modules.is_dir() or private_modules.is_symlink()
            or not cli.is_file() or not node.is_file()
            or not cli.resolve(strict=True).is_relative_to(private_modules.resolve(strict=True))):
        response["classification"]="optional_not_certified"
        return response
    try:
        meta=json.loads(manifest.read_text(encoding="utf-8"))
        version=str(meta.get("version","unknown"))
        response["version"]=version[:40] if re.fullmatch(r"[0-9A-Za-z._+-]{1,40}",version) else "unknown"
        response["private_cli_present"]=True
        state=WORK/"ruflo-private-state"
        state.mkdir(mode=0o700)
        env={"PATH":str(node.parent)+":/usr/bin:/bin",
             "HOME":str(state),"XDG_CONFIG_HOME":str(state),
             "XDG_CACHE_HOME":str(state),"XDG_DATA_HOME":str(state),
             "TMPDIR":str(state),"NODE_OPTIONS":"--no-warnings",
             "CI":"1","LANG":"C"}
        p=subprocess.run([str(cli),"--version"],shell=False,env=env,cwd=str(state),
                         capture_output=True,text=True,timeout=25,check=False)
        response["local_cli_test"]="pass" if p.returncode==0 else "nonzero_exit"
        response["classification"]="optional_cli_working_no_agent_or_model_certification" if p.returncode==0 else "optional_not_certified"
    except (OSError,ValueError,subprocess.TimeoutExpired):
        response["local_cli_test"]="unavailable"
        response["classification"]="optional_not_certified"
    return response


def orchestrator_smoke():
    from unittest.mock import patch
    from engine import orchestrator, ferrari, tool_runtime

    actions=tool_runtime.specs()
    private_actions=0
    for action in actions.values():
        executable=tool_runtime.executable(action["tool"],action["binary"])
        if not executable or not Path(executable).resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
            raise RuntimeError("Ferrari typed action escaped its own project")
        private_actions+=1
    if private_actions!=40:
        raise RuntimeError("Ferrari registered private action count changed")
    plan={"version":1,"steps":[
        {"id":"site","operation":"web-template","title":"Ferrari F7 privado",
         "layout":"landing"},
        {"id":"extract","operation":"binary-strings",
         "depends_on":["site"],"input_from":"site"},
    ]}
    original=ferrari.run
    def cancel_after_site(*args, **kwargs):
        output=original(*args, **kwargs)
        if args and args[0]=="web-template":
            marker=Path(args[1]).parent/"cancel.request"
            if marker.is_symlink() or marker.exists():
                raise RuntimeError("Unsafe Ferrari cancellation marker")
            marker.write_text("cancel demonstration\n",encoding="utf-8")
        return output

    with patch.object(ferrari,"run",side_effect=cancel_after_site):
        interrupted=orchestrator.orchestrate(
            plan,str(WORK),execute=True,job_key=KEY,max_parallel=2,
            max_runtime_seconds=180,max_artifacts_bytes=67108864)
    if (interrupted["result"]["status"]!="cancelled" or
            set(interrupted["result"]["completed"])!={"site"} or
            interrupted["result"]["blocked"]!=["extract"]):
        raise RuntimeError("Ferrari cancelled checkpoint was not durable")
    site_file=Path(interrupted["result"]["completed"]["site"]["artifacts"][0])
    digest_before=site_file.read_bytes()
    marker=WORK/("ferrari-"+KEY)/"cancel.request"
    if not marker.is_file() or marker.is_symlink():
        raise RuntimeError("Ferrari private cancellation marker missing")
    marker.unlink()

    # The resumed DAG runs in a *separate private Python process*, proving
    # persistence across process termination rather than a same-process mock.
    planfile=WORK/"checkpoint-plan.json"
    planfile.write_text(json.dumps(plan,sort_keys=True),encoding="utf-8")
    python=ROOT/"runtimes/python3.12/bin/python3.12"
    if python.is_symlink() or not python.is_file() or not python.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("Ferrari private Python interpreter missing")
    env={"PATH":str(python.parent)+":/usr/bin:/bin",
         "HOME":str(WORK),"TMPDIR":str(WORK),
         "PYTHONNOUSERSITE":"1","PYTHONDONTWRITEBYTECODE":"1",
         "LANG":"C","LC_ALL":"C"}
    def independent_resume():
        p=subprocess.run(
            [str(python),"-B","-m","engine.orchestrator",
             "--plan",str(planfile),"--workspace",str(WORK),
             "--execute","--job-key",KEY,"--resume",
             "--max-parallel","2","--max-runtime-seconds","180",
             "--max-artifacts-bytes","67108864"],
            cwd=str(ROOT/"current"),env=env,timeout=180,
            capture_output=True,text=True,check=False)
        if p.returncode:
            raise RuntimeError("Ferrari private subprocess resume failed with exit "+str(p.returncode))
        return json.loads((WORK/("ferrari-"+KEY)/"report.json").read_text(encoding="utf-8"))
    report=independent_resume()
    if (report["status"]!="completed" or
            set(report["completed"])!={"site","extract"} or
            report["reused_steps"]!=["site"] or report["attempt"]!=2):
        raise RuntimeError("Ferrari F7 checkpoint replay did not complete correctly")
    if site_file.read_bytes()!=digest_before:
        raise RuntimeError("Ferrari F7 replay changed a completed artifact")
    extracted=Path(report["completed"]["extract"]["artifacts"][0])
    if not extracted.is_file() or b"Ferrari F7 privado" not in extracted.read_bytes():
        raise RuntimeError("Ferrari F7 dependent real extraction failed")
    final=independent_resume()
    if (final["status"]!="completed" or
            final["reused_steps"]!=["site"] or
            final["attempt"]!=2):
        raise RuntimeError("Ferrari idempotency on completed job is not respected")

    parallel={"version":1,"steps":[
        {"id":"site","operation":"web-template","title":"Ferrari Website"},
        {"id":"poster","operation":"svg-poster","title":"Ferrari Banner"},
        {"id":"scan","operation":"binary-strings","depends_on":["site"],"input_from":"site"},
    ]}
    second=orchestrator.orchestrate(
        parallel,str(WORK),execute=True,job_key="parallel-demo-20261105",
        max_parallel=2,max_runtime_seconds=180,max_artifacts_bytes=67108864)
    if second["result"]["status"]!="completed" or len(second["result"]["completed"])!=3:
        raise RuntimeError("Ferrari two-worker DAG smoke did not complete")
    for name,output in second["result"]["completed"].items():
        if not output.get("artifacts"):
            raise RuntimeError("Ferrari stage without artifacts: "+name)

    # Keep a small, self-contained evidence sample inside Ferrari.
    return {
        "registered_private_actions":private_actions,
        "sequential_checkpoint": {
            "first_status":interrupted["result"]["status"],
            "resumed_status":report["status"],
            "attempts":report["attempt"],"reused_steps":report["reused_steps"],
            "independent_resume_process":True,
            "completed_replay_no_repeat":final["attempt"]==2,
        },
        "parallel_dag":{"status":second["result"]["status"],
                        "steps_completed":len(second["result"]["completed"]),
                        "max_parallel":2},
        "artifact_locations_private":all(
            Path(a).resolve(strict=True).is_relative_to(ROOT.resolve(strict=True))
            for group in (report["completed"],second["result"]["completed"])
            for item in group.values() for a in item["artifacts"]),
    }


def uninstall_footprint():
    """Read-only, bounded ownership inventory; never remove the live Ferrari."""
    prefixes=(b"/srv/projects/skill-universal",b"/home/ubuntu/.local/share/motor-ferrari")
    roots=[
        Path("/etc/systemd/system"),
        Path("/etc/cron.d"),
        Path("/etc/nginx/sites-enabled"),
        Path("/etc/supervisor/conf.d"),
        Path("/home/ubuntu/.config/systemd/user"),
    ]
    findings=[]
    scanned=0
    incomplete=False
    for base in roots:
        if not base.is_dir():
            continue
        if base.is_symlink():
            incomplete=True
            continue
        for folder, directories, files in os.walk(base,followlinks=False):
            if scanned>=800:
                incomplete=True
                break
            for filename in files:
                if scanned>=800:
                    incomplete=True
                    break
                path=Path(folder)/filename
                if path.is_symlink():
                    try:
                        target=path.resolve(strict=True)
                        # Permit Ubuntu's own Nginx sites-enabled -> sites-available.
                        if base != Path("/etc/nginx/sites-enabled") or not target.is_relative_to(Path("/etc/nginx")):
                            continue
                        path=target
                    except (RuntimeError,OSError):
                        incomplete=True
                        continue
                try:
                    if not path.is_file() or path.stat().st_size>1024*1024:
                        continue
                    # Only test for Ferrari root references. Never print config content.
                    data=path.read_bytes()
                    scanned+=1
                    if any(pattern in data for pattern in prefixes):
                        findings.append(str(path))
                except (OSError,PermissionError):
                    incomplete=True
            if scanned>=800:
                break
    alias=Path("/home/ubuntu/.local/share/motor-ferrari")
    if alias.is_symlink():
        alias_status="project_alias" if alias.resolve(strict=True)==ROOT.resolve(strict=True) else "external_or_unsafe_alias"
    elif alias.exists():
        alias_status="unexpected_physical_object"
    else:
        alias_status="absent"
    root_children=sorted(p.name for p in ROOT.iterdir() if p.name not in (".", ".."))
    return {
        "scope":"read_only_uninstall_readiness",
        "exact_ownership_directory":str(ROOT),
        "project_folder_matches_github_repo":"skill-universal"==ROOT.name,
        "external_registrations_sampled":scanned,
        "external_registrations_with_ferrari_references":findings[:40],
        "unscanned_or_unreadable_possible":incomplete,
        "legacy_alias":alias_status,
        "root_top_level_entries":root_children[:120],
        "uninstall_executed":False,
        "global_package_removal_authorized":False,
        "other_project_files_touched":False,
        "limitations":"Bounded allowlisted service-config scan; not a proof of zero indirect or future consumers.",
    }


def main():
    guarded()
    before=time.monotonic()
    WORK.mkdir(parents=True,mode=0o700)
    dag=orchestrator_smoke()
    ruflo=private_ruflo()
    after=resource.getrusage(resource.RUSAGE_SELF)
    report={
        "schema":1,"phase":7,"status":"completed",
        "executed_utc":datetime.now(timezone.utc).isoformat(),
        "mode":"existing_private_orchestrator_real_vps_smoke",
        "root":str(ROOT),"release":F7_ACTIVE,"fallback":F6_FALLBACK,
        "dag":dag,"ruflo":ruflo,"uninstall_footprint":uninstall_footprint(),
        "usage":{"wall_seconds":round(time.monotonic()-before,2),
                 "maxrss_kib":int(after.ru_maxrss),
                 "timeout_policy":"cooperative_between_waves",
                 "max_dag_parallel":4,"max_dag_steps":24},
        "prohibited_actions":{"global_apt_install":0,"other_projects_written":0,
                              "new_coordinators":0,"paid_providers":0},
    }
    out=WORK/"phase7-certification.json"
    out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    if not out.resolve(strict=True).is_relative_to(ROOT.resolve(strict=True)):
        raise RuntimeError("Ferrari certification result escaped")
    print(json.dumps(report,sort_keys=True))
    print("FERRARI_PHASE7_DAG_PRIVATE_CERT=PASS")


if __name__=="__main__":
    try:
        main()
    except (RuntimeError,ValueError,OSError,KeyError,json.JSONDecodeError) as exc:
        print("FERRARI_PHASE7_CERT_BLOCKED="+type(exc).__name__+":"+str(exc)[:180],file=sys.stderr)
        sys.exit(2)
