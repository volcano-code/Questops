#!/usr/bin/env python3
"""Run real Unity Test Framework tests and emit fail-closed evidence."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

def parse_results(path: Path) -> dict:
    root=ET.parse(path).getroot()
    def integer(*names):
        for name in names:
            raw=root.attrib.get(name)
            if raw is not None:
                try: return int(raw)
                except ValueError: pass
        return 0
    total=integer("total","testcasecount")
    passed=integer("passed","passedcount")
    failed=integer("failed","failedcount")
    skipped=integer("skipped","inconclusive","skippedcount")
    if total <= 0:
        raise ValueError("Unity result XML contains zero tests")
    return {"total":total,"passed":passed,"failed":failed,"skipped":skipped}

def run_one(unity: Path, project: Path, platform: str, results: Path, log: Path, assembly: str|None) -> dict:
    results.parent.mkdir(parents=True,exist_ok=True); log.parent.mkdir(parents=True,exist_ok=True)
    cmd=[str(unity),"-batchmode","-nographics","-runTests","-projectPath",str(project),
         "-testPlatform",platform,"-testResults",str(results),"-logFile",str(log)]
    if assembly: cmd += ["-assemblyNames",assembly]
    completed=subprocess.run(cmd,check=False)
    if not results.exists():
        raise RuntimeError(f"Unity {platform} produced no result XML (exit={completed.returncode})")
    summary=parse_results(results)
    summary.update({"platform":platform,"processExitCode":completed.returncode,"results":str(results),"log":str(log)})
    if completed.returncode != 0 or summary["failed"] != 0:
        raise RuntimeError(f"Unity {platform} failed: {summary}")
    return summary

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--unity",required=True)
    p.add_argument("--project",default=".")
    p.add_argument("--mode",choices=["EditMode","PlayMode","all"],default="all")
    p.add_argument("--output",default="artifacts/unity")
    args=p.parse_args()
    unity=Path(args.unity).resolve(); project=Path(args.project).resolve(); out=Path(args.output).resolve()
    if not unity.is_file():
        print(f"BLOCKED: Unity executable not found: {unity}"); return 2
    modes=["EditMode","PlayMode"] if args.mode=="all" else [args.mode]
    assemblies={"EditMode":"QuestOps.Tests.EditMode","PlayMode":"QuestOps.Tests.PlayMode"}
    evidence={"schemaVersion":1,"unityExecutable":str(unity),"project":str(project),"runs":[]}
    try:
        for mode in modes:
            evidence["runs"].append(run_one(unity,project,mode,out/f"{mode}.xml",out/f"{mode}.log",assemblies[mode]))
    except (RuntimeError,ValueError,ET.ParseError) as exc:
        evidence["error"]=str(exc)
        (out/"verification.json").parent.mkdir(parents=True,exist_ok=True)
        (out/"verification.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
        print("FAIL:",exc); return 1
    (out/"verification.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(evidence))
    return 0

if __name__=="__main__": raise SystemExit(main())
