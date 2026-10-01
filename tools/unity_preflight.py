#!/usr/bin/env python3
"""Fail closed unless the installed Unity Editor exactly matches the project."""
from __future__ import annotations
import argparse, json, re, subprocess
from pathlib import Path

VERSION_RE=re.compile(r"^m_EditorVersion:\s*(\S+)\s*$",re.MULTILINE)

def project_version(project: Path) -> str:
    path=project/"ProjectSettings"/"ProjectVersion.txt"
    match=VERSION_RE.search(path.read_text(encoding="utf-8"))
    if not match: raise ValueError("ProjectVersion.txt has no m_EditorVersion")
    return match.group(1)

def editor_version(unity: Path) -> str:
    completed=subprocess.run([str(unity),"-version"],capture_output=True,text=True,check=False)
    text=(completed.stdout+"\n"+completed.stderr).strip()
    if completed.returncode != 0: raise RuntimeError(f"Unity -version failed ({completed.returncode}): {text}")
    match=re.search(r"\b\d+\.\d+\.\d+[abfp]\d+\b",text)
    if not match: raise ValueError(f"could not parse Unity version from: {text!r}")
    return match.group(0)

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--unity",required=True)
    p.add_argument("--project",default=".")
    p.add_argument("--output",default="artifacts/unity/preflight.json")
    args=p.parse_args()
    unity=Path(args.unity).resolve(); project=Path(args.project).resolve()
    if not unity.is_file():
        print(f"BLOCKED: Unity executable not found: {unity}"); return 2
    try:
        expected=project_version(project); actual=editor_version(unity)
    except (OSError,ValueError,RuntimeError) as exc:
        print("FAIL:",exc); return 1
    evidence={"schemaVersion":1,"expectedVersion":expected,"actualVersion":actual,"match":expected==actual}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    if expected != actual:
        print(f"FAIL: Unity version mismatch: expected {expected}, got {actual}"); return 1
    print(json.dumps(evidence)); return 0

if __name__=="__main__": raise SystemExit(main())
