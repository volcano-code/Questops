#!/usr/bin/env python3
"""Install the published Harness runtime, install QuestOps bundle, verify composition.

This does not call a model and therefore cannot make harnessLive PASS.
"""
from __future__ import annotations
import argparse, json, os
from pathlib import Path
import shutil, subprocess, sys, tempfile

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--workspace",default=".")
    p.add_argument("--dsh-home")
    p.add_argument("--profile",default="sdk-minimal")
    p.add_argument("--evidence",default="artifacts/harness/install.json")
    p.add_argument("--keep-home",action="store_true")
    args=p.parse_args()

    workspace=Path(args.workspace).resolve()
    plugin=(workspace/"Harness"/"plugin").resolve()
    dsh=shutil.which("dsh")
    pnpm=shutil.which("pnpm")
    if not dsh:
        print("BLOCKED: dsh is unavailable; install deepseek-harness-sdk",file=sys.stderr); return 2
    if not pnpm:
        print("BLOCKED: pnpm is required only for dsh plugin management",file=sys.stderr); return 2

    owned=args.dsh_home is None
    home=Path(args.dsh_home).resolve() if args.dsh_home else Path(tempfile.mkdtemp(prefix="questops-dsh-install-"))
    env=os.environ.copy(); env["DSH_HOME"]=str(home); env["QUESTOPS_PROJECT_ROOT"]=str(workspace)
    try:
        subprocess.run([dsh,"--profile",args.profile,"--dump-default-config"],env=env,cwd=workspace,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([dsh,"plugin","--profile",args.profile,"add",f"file:{plugin}"],env=env,cwd=workspace,check=True)
        profile_manifest=home/"profiles"/args.profile/"package.json"
        manifest=json.loads(profile_manifest.read_text(encoding="utf-8"))
        bundles=((manifest.get("dsh") or {}).get("profile") or {}).get("bundles") or []
        if "questops-harness-tools" not in bundles:
            print("FAIL: plugin dependency installed but bundle is not active in profile",file=sys.stderr); return 1

        config=subprocess.run(
            [dsh,"--profile",args.profile,"--dump-config"],
            env=env,cwd=workspace,check=True,capture_output=True,text=True,
        ).stdout
        if "questops-project-tools" not in config or "questops-harness-tools" not in config:
            print("FAIL: composed config does not contain QuestOps plugin row",file=sys.stderr); return 1

        evidence={
            "schemaVersion":1,
            "kind":"harness-install-smoke",
            "profile":args.profile,
            "plugin":"questops-harness-tools",
            "bundleActive":True,
            "composedRowPresent":True,
            "liveModel":False,
        }
        out=Path(args.evidence); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(evidence))
        return 0
    finally:
        if owned and not args.keep_home: shutil.rmtree(home,ignore_errors=True)

if __name__=="__main__": raise SystemExit(main())
