#!/usr/bin/env python3
"""Run one real DeepSeek Harness turn and require QuestOps tool-call evidence."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid

TOOLS = ("questops_read_project_contract", "questops_read_authoring_skill")

def fail(message: str, code: int = 2) -> int:
    print(f"BLOCKED: {message}", file=sys.stderr)
    return code

def jsonable(value):
    if isinstance(value, dict):
        return {str(k): jsonable(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [jsonable(v) for v in value]
    if hasattr(value, "__dict__"):
        return jsonable(vars(value))
    return str(value)

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--workspace", default=".")
    p.add_argument("--dsh-home")
    p.add_argument("--model", default=os.getenv("QUESTOPS_DEEPSEEK_MODEL", "deepseek-v4-flash"))
    p.add_argument("--provider", default="deepseek-official")
    p.add_argument("--evidence", default="artifacts/harness/live.json")
    p.add_argument("--keep-home", action="store_true")
    args=p.parse_args()

    if not os.getenv("DEEPSEEK_API_KEY"):
        return fail("DEEPSEEK_API_KEY is not configured")

    try:
        from deepseek_harness import DeepSeekHarness
    except ImportError:
        return fail("deepseek-harness-sdk is not installed")

    workspace=Path(args.workspace).resolve()
    plugin=(workspace/"Harness"/"plugin").resolve()
    if not (plugin/"package.json").is_file():
        return fail("QuestOps Harness bundle is missing")

    owned_home=args.dsh_home is None
    home=Path(args.dsh_home).resolve() if args.dsh_home else Path(tempfile.mkdtemp(prefix="questops-dsh-"))
    env=os.environ.copy()
    env["DSH_HOME"]=str(home)
    env["QUESTOPS_PROJECT_ROOT"]=str(workspace)

    dsh=shutil.which("dsh")
    if not dsh:
        return fail("dsh executable from deepseek-harness-runtime-bin is unavailable")

    try:
        subprocess.run([dsh,"--profile","sdk-minimal","--dump-default-config"],env=env,cwd=workspace,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([dsh,"plugin","--profile","sdk-minimal","add",f"file:{plugin}"],env=env,cwd=workspace,check=True)

        session_id="questops-live-"+uuid.uuid4().hex[:12]
        prompt=(
            "You are validating the QuestOps RC1 integration. "
            "You MUST call questops_read_project_contract and questops_read_authoring_skill. "
            "After reading both, summarize the exact canonical quest requirements. "
            "Do not modify files and do not invent identifiers."
        )
        with DeepSeekHarness(
            dsh_home=str(home),
            cwd=str(workspace),
            provider=args.provider,
            model=args.model,
            profile="sdk-minimal",
            env={"QUESTOPS_PROJECT_ROOT": str(workspace)},
            request_timeout_seconds=120.0,
        ) as harness:
            result=harness.run(prompt, session_id=session_id)

        events=jsonable(result.events)
        serialized=json.dumps(events,ensure_ascii=False,sort_keys=True)
        missing=[name for name in TOOLS if name not in serialized]
        if missing:
            print("FAIL: real Harness turn completed without required QuestOps tool calls: "+", ".join(missing),file=sys.stderr)
            return 1

        evidence={
            "schemaVersion":1,
            "mode":"live",
            "liveModel":True,
            "provider":args.provider,
            "model":args.model,
            "sessionId":result.session_id,
            "finishReason":result.finish_reason,
            "requiredTools":list(TOOLS),
            "eventCount":len(result.events),
            "eventSha256":hashlib.sha256(serialized.encode("utf-8")).hexdigest(),
        }
        path=Path(args.evidence); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(evidence,ensure_ascii=False))
        return 0
    finally:
        if owned_home and not args.keep_home:
            shutil.rmtree(home,ignore_errors=True)

if __name__=="__main__":
    raise SystemExit(main())
