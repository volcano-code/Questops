#!/usr/bin/env python3
"""Generate the playable QuestOps graybox scene using the real Unity Editor."""
from __future__ import annotations
import argparse, json, subprocess
from pathlib import Path

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--unity",required=True); p.add_argument("--project",default=".")
    p.add_argument("--output",default="artifacts/unity/demo-build.json")
    args=p.parse_args()
    unity=Path(args.unity).resolve(); project=Path(args.project).resolve()
    if not unity.is_file():
        print(f"BLOCKED: Unity executable not found: {unity}"); return 2
    log=project/"artifacts"/"unity"/"demo-build.log"; log.parent.mkdir(parents=True,exist_ok=True)
    cmd=[str(unity),"-batchmode","-nographics","-quit","-projectPath",str(project),
         "-executeMethod","QuestOps.Editor.QuestOpsDemoSceneBuilder.Build","-logFile",str(log)]
    completed=subprocess.run(cmd,check=False)
    scene=project/"Assets"/"QuestOpsDemo"/"QuestOpsDemo.unity"
    evidence={"schemaVersion":1,"processExitCode":completed.returncode,"scene":str(scene),"sceneExists":scene.is_file(),"log":str(log)}
    out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(evidence,indent=2)+"\n",encoding="utf-8")
    if completed.returncode!=0 or not scene.is_file():
        print("FAIL: Unity did not generate the graybox demo scene"); return 1
    print(json.dumps(evidence)); return 0

if __name__=="__main__": raise SystemExit(main())
