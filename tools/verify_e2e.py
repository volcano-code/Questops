#!/usr/bin/env python3
"""Promote fullE2E only when live Harness, approval/apply and Unity evidence form one hash chain."""
from __future__ import annotations
import argparse, json, os, subprocess
from pathlib import Path

REQUIRED_TOOLS={"questops_read_project_contract","questops_read_authoring_skill"}

def load(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))

def current_sha(project: Path) -> str:
    if os.getenv("GITHUB_SHA"): return os.environ["GITHUB_SHA"]
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=project,capture_output=True,text=True,check=False)
    return r.stdout.strip() if r.returncode==0 else "unknown"

def verify(harness: dict, approval: dict, receipt: dict, unity: dict, expected_commit: str) -> list[str]:
    errors=[]
    if harness.get("liveModel") is not True or harness.get("mode")!="live": errors.append("Harness evidence is not live")
    if not REQUIRED_TOOLS.issubset(set(harness.get("requiredTools") or [])): errors.append("Harness required tool evidence is incomplete")
    if harness.get("commitSha") != expected_commit: errors.append("Harness commit does not match")
    draft_sha=harness.get("draftSha256")
    if not isinstance(draft_sha,str) or len(draft_sha)!=64: errors.append("Harness draft SHA is missing")
    if approval.get("approved") is not True: errors.append("approval is not affirmative")
    if approval.get("draftSha256") != draft_sha: errors.append("approval is not bound to Harness draft")
    execution_id=approval.get("executionId")
    if not execution_id: errors.append("approval executionId is missing")
    if receipt.get("executionId") != execution_id: errors.append("apply receipt executionId does not match approval")
    if receipt.get("draft_sha256") != draft_sha: errors.append("apply receipt draft hash does not match")
    applied_sha=receipt.get("applied_sha256")
    if applied_sha != draft_sha: errors.append("applied artifact differs from approved draft")
    if unity.get("commitSha") != expected_commit: errors.append("Unity commit does not match")
    if unity.get("canonicalArtifactSha256") != applied_sha: errors.append("Unity did not execute the applied artifact")
    runs={r.get("platform"):r for r in unity.get("runs") or []}
    for mode in ("EditMode","PlayMode"):
        run=runs.get(mode)
        if not run:
            errors.append(f"Unity {mode} evidence is missing"); continue
        if run.get("processExitCode") != 0 or int(run.get("total") or 0)<=0 or int(run.get("failed") or 0)!=0:
            errors.append(f"Unity {mode} did not pass")
    return errors

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--harness",required=True); p.add_argument("--approval",required=True)
    p.add_argument("--receipt",required=True); p.add_argument("--unity",required=True)
    p.add_argument("--project",default="."); p.add_argument("--output",default="artifacts/e2e/evidence.json")
    p.add_argument("--gate-output")
    args=p.parse_args(); commit=current_sha(Path(args.project).resolve())
    harness,approval,receipt,unity=map(load,(args.harness,args.approval,args.receipt,args.unity))
    errors=verify(harness,approval,receipt,unity,commit)
    evidence={
        "schemaVersion":1,"status":"PASS" if not errors else "FAIL","commitSha":commit,
        "executionId":approval.get("executionId"),"draftSha256":harness.get("draftSha256"),
        "appliedSha256":receipt.get("applied_sha256"),"errors":errors,
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    if args.gate_output:
        gate_path=Path(args.gate_output); gate_path.parent.mkdir(parents=True,exist_ok=True)
        gate={
            "gate":"fullE2E","status":"PASS" if not errors else "FAIL",
            "evidence":str(out) if not errors else None,
            "reason":None if not errors else "; ".join(errors),
        }
        gate_path.write_text(json.dumps(gate,indent=2)+"\n",encoding="utf-8")
    if errors:
        for error in errors: print("FAIL:",error)
        return 1
    print(json.dumps(evidence)); return 0

if __name__=="__main__": raise SystemExit(main())
