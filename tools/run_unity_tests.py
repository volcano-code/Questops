#!/usr/bin/env python3
"""Run real Unity Test Framework tests and emit fail-closed evidence."""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess
from pathlib import Path
import xml.etree.ElementTree as ET

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda:handle.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def commit_sha(project: Path) -> str:
    from_env=os.getenv("GITHUB_SHA")
    if from_env: return from_env
    completed=subprocess.run(["git","rev-parse","HEAD"],cwd=project,capture_output=True,text=True,check=False)
    return completed.stdout.strip() if completed.returncode==0 else "unknown"

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
    if total <= 0: raise ValueError("Unity result XML contains zero tests")
    return {"total":total,"passed":passed,"failed":failed,"skipped":skipped}

def run_one(unity: Path, project: Path, platform: str, results: Path, log: Path, assembly: str|None, env: dict[str,str]) -> dict:
    results.parent.mkdir(parents=True,exist_ok=True); log.parent.mkdir(parents=True,exist_ok=True)
    cmd=[str(unity),"-batchmode","-nographics","-runTests","-projectPath",str(project),
         "-testPlatform",platform,"-testResults",str(results),"-logFile",str(log)]
    if assembly: cmd += ["-assemblyNames",assembly]
    completed=subprocess.run(cmd,check=False,env=env)
    if not results.exists(): raise RuntimeError(f"Unity {platform} produced no result XML (exit={completed.returncode})")
    summary=parse_results(results)
    summary.update({
        "platform":platform,"processExitCode":completed.returncode,
        "results":str(results),"resultsSha256":sha256_file(results),
        "log":str(log),"logSha256":sha256_file(log) if log.exists() else None,
    })
    if completed.returncode != 0 or summary["failed"] != 0: raise RuntimeError(f"Unity {platform} failed: {summary}")
    return summary

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--unity",required=True)
    p.add_argument("--project",default=".")
    p.add_argument("--mode",choices=["EditMode","PlayMode","all"],default="all")
    p.add_argument("--output",default="artifacts/unity")
    p.add_argument("--canonical-artifact")
    args=p.parse_args()
    unity=Path(args.unity).resolve(); project=Path(args.project).resolve(); out=Path(args.output).resolve()
    if not unity.is_file():
        print(f"BLOCKED: Unity executable not found: {unity}"); return 2
    env=os.environ.copy()
    artifact=None
    if args.canonical_artifact:
        artifact=Path(args.canonical_artifact).resolve()
        if not artifact.is_file():
            print(f"BLOCKED: canonical artifact not found: {artifact}"); return 2
        env["QUESTOPS_CANONICAL_ARTIFACT"]=str(artifact)
    modes=["EditMode","PlayMode"] if args.mode=="all" else [args.mode]
    assemblies={"EditMode":"QuestOps.Tests.EditMode","PlayMode":"QuestOps.Tests.PlayMode"}
    evidence={
        "schemaVersion":2,"commitSha":commit_sha(project),"unityExecutable":str(unity),
        "project":str(project),"canonicalArtifact":str(artifact) if artifact else None,
        "canonicalArtifactSha256":sha256_file(artifact) if artifact else None,"runs":[],
    }
    try:
        for mode in modes:
            evidence["runs"].append(run_one(unity,project,mode,out/f"{mode}.xml",out/f"{mode}.log",assemblies[mode],env))
    except (RuntimeError,ValueError,ET.ParseError) as exc:
        evidence["error"]=str(exc); out.mkdir(parents=True,exist_ok=True)
        (out/"verification.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
        print("FAIL:",exc); return 1
    out.mkdir(parents=True,exist_ok=True)
    (out/"verification.json").write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(evidence)); return 0

if __name__=="__main__": raise SystemExit(main())
