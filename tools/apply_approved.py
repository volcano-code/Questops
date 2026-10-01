#!/usr/bin/env python3
"""Validate approval and perform a create-only application of the approved draft."""
from __future__ import annotations
import argparse, json, sys
from dataclasses import asdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Agent"))
from change_control import Approval, ChangeControlError, apply_create_only
from questops_core import validate_quest

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--draft",required=True)
    p.add_argument("--approval",required=True)
    p.add_argument("--target",required=True)
    p.add_argument("--receipt",default="artifacts/e2e/apply-receipt.json")
    args=p.parse_args()
    draft=json.loads(Path(args.draft).read_text(encoding="utf-8")); validate_quest(draft)
    raw=json.loads(Path(args.approval).read_text(encoding="utf-8"))
    if raw.get("approved") is not True: raise SystemExit("FAIL: approval is not affirmative")
    execution_id=raw.get("executionId")
    if not isinstance(execution_id,str) or not execution_id: raise SystemExit("FAIL: approval has no executionId")
    approval=Approval(execution_id,str(raw.get("draftSha256") or ""))
    try: receipt=apply_create_only(Path(args.target),draft,approval)
    except ChangeControlError as exc:
        print("FAIL:",exc,file=sys.stderr); return 1
    payload=asdict(receipt); payload["schemaVersion"]=1; payload["executionId"]=payload.pop("run_id")
    out=Path(args.receipt); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(payload)); return 0

if __name__=="__main__": raise SystemExit(main())
