#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--gate",required=True)
    p.add_argument("--status",required=True,choices=["PASS","FAIL","BLOCKED","NOT_RUN"])
    p.add_argument("--evidence")
    p.add_argument("--reason")
    p.add_argument("--output",required=True)
    args=p.parse_args()
    if args.status=="PASS" and not args.evidence:
        p.error("PASS requires --evidence")
    if args.status in {"BLOCKED","NOT_RUN"} and not args.reason:
        p.error("BLOCKED/NOT_RUN requires --reason")
    out={"gate":args.gate,"status":args.status,"evidence":args.evidence,"reason":args.reason}
    path=Path(args.output); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(out,indent=2)+"\n",encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
