#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--template",required=True)
    p.add_argument("--fragments",required=True)
    p.add_argument("--output",required=True)
    args=p.parse_args()
    result=json.loads(Path(args.template).read_text(encoding="utf-8"))
    for path in Path(args.fragments).rglob("*.json"):
        try: fragment=json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError,UnicodeDecodeError): continue
        gate=fragment.get("gate")
        if gate in result.get("gates",{}):
            result["gates"][gate]={
                "status":fragment.get("status"),
                "evidence":fragment.get("evidence"),
                "reason":fragment.get("reason"),
            }
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    return 0
if __name__=="__main__": raise SystemExit(main())
