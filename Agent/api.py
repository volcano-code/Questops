"""Small local QuestOps browser API. Approval/apply are intentionally not exposed."""
from __future__ import annotations
import json, os, subprocess, sys, tempfile, uuid
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Agent"))
from questops_core import validate_quest

app=FastAPI(title="QuestOps Local API",version="0.1.0")

class RunRequest(BaseModel):
    intent: str=Field(min_length=3,max_length=2000)
    mode: Literal["fixture","live"]="fixture"
    allow_model_call: bool=False

class RunResponse(BaseModel):
    runId: str
    mode: Literal["fixture","live"]
    liveModel: bool
    draft: dict
    evidence: dict

def canonical() -> dict:
    value=json.loads((ROOT/"Schemas"/"canonical-quest.json").read_text(encoding="utf-8"))
    validate_quest(value); return value

@app.get("/api/health")
def health():
    return {"status":"ok","project":"QuestOps","approvalInBrowser":False}

@app.get("/api/canonical")
def get_canonical():
    return canonical()

@app.post("/api/runs",response_model=RunResponse)
def create_run(req: RunRequest):
    run_id="run-"+uuid.uuid4().hex[:12]
    if req.mode=="fixture":
        draft=canonical()
        return RunResponse(
            runId=run_id,mode="fixture",liveModel=False,draft=draft,
            evidence={"kind":"deterministic-fixture","warning":"fixture is not a model call"},
        )

    if not req.allow_model_call:
        raise HTTPException(400,"live mode requires allow_model_call=true")
    if not os.getenv("DEEPSEEK_API_KEY"):
        raise HTTPException(503,"DEEPSEEK_API_KEY is not configured on the server")

    with tempfile.TemporaryDirectory(prefix="questops-api-") as td:
        evidence=Path(td)/"live.json"; draft_path=Path(td)/"draft.json"
        completed=subprocess.run([
            sys.executable,str(ROOT/"Harness"/"live_smoke.py"),"--workspace",str(ROOT),
            "--evidence",str(evidence),"--draft",str(draft_path),
        ],cwd=ROOT,capture_output=True,text=True,check=False,timeout=180)
        if completed.returncode != 0 or not evidence.is_file() or not draft_path.is_file():
            raise HTTPException(502,"real Harness run failed; inspect server logs")
        live=json.loads(evidence.read_text(encoding="utf-8"))
        draft=json.loads(draft_path.read_text(encoding="utf-8")); validate_quest(draft)
        if live.get("liveModel") is not True:
            raise HTTPException(502,"Harness evidence did not prove a live model call")
        return RunResponse(runId=run_id,mode="live",liveModel=True,draft=draft,evidence=live)

# Mount the built workbench last so /api routes retain priority.
WEB_DIST=ROOT/"Web"/"dist"
if WEB_DIST.is_dir():
    from fastapi.staticfiles import StaticFiles
    app.mount("/",StaticFiles(directory=str(WEB_DIST),html=True),name="workbench")
