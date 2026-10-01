#!/usr/bin/env python3
from __future__ import annotations
import argparse, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--host",default="127.0.0.1")
    p.add_argument("--port",type=int,default=8765)
    args=p.parse_args()
    import uvicorn
    uvicorn.run("Agent.api:app",host=args.host,port=args.port,reload=False)
    return 0

if __name__=="__main__": raise SystemExit(main())
