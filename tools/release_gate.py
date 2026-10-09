#!/usr/bin/env python3
"""Fail-closed QuestOps release-gate checker."""
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ALLOWED={"PASS","FAIL","BLOCKED","NOT_RUN"}
REQUIRED=("backend","web","harnessLive","unityEditMode","unityPlayMode","fullE2E")

def load_manifest(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))

def validate(manifest: dict) -> list[str]:
    errors=[]
    gates=manifest.get("gates")
    if not isinstance(gates,dict): return ["gates must be an object"]
    for name in REQUIRED:
        gate=gates.get(name)
        if not isinstance(gate,dict):
            errors.append(f"missing gate: {name}"); continue
        status=gate.get("status")
        if status not in ALLOWED: errors.append(f"{name}: invalid status {status!r}")
        if status=="PASS" and not gate.get("evidence"): errors.append(f"{name}: PASS requires evidence")
        if status in {"BLOCKED","NOT_RUN"} and not gate.get("reason"):
            errors.append(f"{name}: {status} requires reason")
    policy=manifest.get("policy",{})
    for key in ("fixtureIsNotLiveModel","inventoryIsNotUnityExecution","approvalRequiredBeforeApply"):
        if policy.get(key) is not True: errors.append(f"{key} must remain true")
    return errors

def main() -> int:
    parser=argparse.ArgumentParser(description="QuestOps release gate checker")
    parser.add_argument("manifest",nargs="?",default="verification/release-gates.json")
    parser.add_argument("--require-complete",action="store_true",
                        help="Fail release if any gate is BLOCKED or NOT_RUN")
    args=parser.parse_args()
    manifest=load_manifest(Path(args.manifest))
    errors=validate(manifest)
    if errors:
        for error in errors: print("FAIL:",error)
        return 1
    statuses={name:manifest["gates"][name]["status"] for name in REQUIRED}
    for name,status in statuses.items(): print(f"{name}: {status}")
    if all(v=="PASS" for v in statuses.values()):
        print("OVERALL: PASS"); return 0
    if any(v=="FAIL" for v in statuses.values()):
        print("OVERALL: FAIL"); return 1
    print("OVERALL: INCOMPLETE")
    return 1 if args.require_complete else 2
if __name__=="__main__": raise SystemExit(main())
