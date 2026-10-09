#!/usr/bin/env python3
"""QuestOps local developer entry point."""
from __future__ import annotations
import argparse, os, shutil, subprocess, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def run(cmd, cwd=ROOT) -> int:
    print("+"," ".join(map(str,cmd)))
    return subprocess.run(list(map(str,cmd)),cwd=cwd,check=False).returncode

def doctor(args) -> int:
    checks={
        "python":sys.version.split()[0],
        "node":shutil.which("node") or "MISSING",
        "npm":shutil.which("npm") or "MISSING",
        "dsh":shutil.which("dsh") or "MISSING (installed by deepseek-harness-sdk)",
        "DEEPSEEK_API_KEY":"configured" if os.getenv("DEEPSEEK_API_KEY") else "MISSING (live Harness blocked)",
    }
    if args.unity:
        checks["unity"]=str(Path(args.unity).resolve()) if Path(args.unity).is_file() else "MISSING"
    for key,value in checks.items(): print(f"{key}: {value}")
    return 0

def setup(_args) -> int:
    if run([sys.executable,"-m","pip","install","-r","Agent/requirements.txt"]): return 1
    if run(["npm","install"],ROOT/"Web"): return 1
    if run(["npm","test"],ROOT/"Web"): return 1
    return run(["npm","run","build"],ROOT/"Web")

def serve(args) -> int:
    return run([sys.executable,"tools/serve.py","--host",args.host,"--port",str(args.port)])

def main() -> int:
    p=argparse.ArgumentParser(prog="questops")
    sub=p.add_subparsers(dest="command",required=True)
    d=sub.add_parser("doctor"); d.add_argument("--unity"); d.set_defaults(func=doctor)
    s=sub.add_parser("setup"); s.set_defaults(func=setup)
    v=sub.add_parser("serve"); v.add_argument("--host",default="127.0.0.1"); v.add_argument("--port",type=int,default=8765); v.set_defaults(func=serve)
    args=p.parse_args(); return args.func(args)

if __name__=="__main__": raise SystemExit(main())
