#!/usr/bin/env python3
"""Create an explicit human approval artifact bound to one draft hash."""
from __future__ import annotations
import argparse, json, os
from datetime import datetime, timezone
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Agent"))
from change_control import canonical_bytes, sha256_bytes
from questops_core import validate_quest

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--draft",required=True)
    p.add_argument("--execution-id",required=True)
    p.add_argument("--actor",default=os.getenv("GITHUB_ACTOR") or os.getenv("USER") or "")
    p.add_argument("--confirm",required=True,help="must be exactly APPROVE")
    p.add_argument("--output",default="artifacts/e2e/approval.json")
    args=p.parse_args()
    if args.confirm != "APPROVE":
        p.error("--confirm must be exactly APPROVE")
    if not args.actor.strip(): p.error("--actor is required")
    draft=json.loads(Path(args.draft).read_text(encoding="utf-8")); validate_quest(draft)
    digest=sha256_bytes(canonical_bytes(draft))
    approval={
        "schemaVersion":1,"executionId":args.execution_id,"approved":True,
        "approvedBy":args.actor,"approvedAt":datetime.now(timezone.utc).isoformat(),
        "draftSha256":digest,
    }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(approval,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(approval)); return 0

if __name__=="__main__": raise SystemExit(main())
