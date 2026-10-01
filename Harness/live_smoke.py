#!/usr/bin/env python3
"""Run a real DeepSeek Harness turn and produce a validated QuestOps draft."""
from __future__ import annotations
import argparse, hashlib, importlib.metadata, json, os, re
from pathlib import Path
import shutil, subprocess, sys, tempfile, uuid

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"Agent"))
from questops_core import QuestValidationError, validate_quest

TOOLS=("questops_read_project_contract","questops_read_authoring_skill")
ALLOWED_TOOL_SET=set(TOOLS)

def visible_request_tools(events) -> set[str]:
    names=set()
    for event in events:
        if not isinstance(event,dict) or event.get("type")!="request/header": continue
        data=event.get("data")
        if not isinstance(data,dict): continue
        candidates=data.get("tools")
        if candidates is None and isinstance(data.get("request"),dict):
            candidates=data["request"].get("tools")
        if not isinstance(candidates,list): continue
        for tool in candidates:
            if not isinstance(tool,dict): continue
            name=tool.get("name")
            if name is None and isinstance(tool.get("function"),dict):
                name=tool["function"].get("name")
            if isinstance(name,str): names.add(name)
    return names

def fail(message: str, code: int=2) -> int:
    print(f"BLOCKED: {message}",file=sys.stderr); return code

def jsonable(value):
    if isinstance(value,dict): return {str(k):jsonable(v) for k,v in value.items()}
    if isinstance(value,(list,tuple)): return [jsonable(v) for v in value]
    if hasattr(value,"__dict__"): return jsonable(vars(value))
    return str(value)

def sha256_bytes(data: bytes) -> str: return hashlib.sha256(data).hexdigest()

def git_sha(workspace: Path) -> str:
    if os.getenv("GITHUB_SHA"): return os.environ["GITHUB_SHA"]
    r=subprocess.run(["git","rev-parse","HEAD"],cwd=workspace,capture_output=True,text=True,check=False)
    return r.stdout.strip() if r.returncode==0 else "unknown"

def parse_draft(text: str) -> dict:
    raw=text.strip()
    fenced=re.fullmatch(r"\s*```(?:json)?\s*(.*?)\s*```\s*",raw,re.DOTALL|re.IGNORECASE)
    if fenced: raw=fenced.group(1)
    value=json.loads(raw)
    if not isinstance(value,dict): raise ValueError("model response must be one JSON object")
    validate_quest(value)
    return value

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--workspace",default=".")
    p.add_argument("--dsh-home")
    p.add_argument("--model",default=os.getenv("QUESTOPS_DEEPSEEK_MODEL","deepseek-flash"))
    p.add_argument("--intent",default="Create the canonical QuestOps RC1 blacksmith iron-ore quest exactly as grounded.")
    p.add_argument("--provider",default="deepseek-official")
    p.add_argument("--evidence",default="artifacts/harness/live.json")
    p.add_argument("--draft",default="artifacts/harness/draft.json")
    p.add_argument("--keep-home",action="store_true")
    args=p.parse_args()

    if not os.getenv("DEEPSEEK_API_KEY"): return fail("DEEPSEEK_API_KEY is not configured")
    try: from deepseek_harness import DeepSeekHarness
    except ImportError: return fail("deepseek-harness-sdk is not installed")

    workspace=Path(args.workspace).resolve(); plugin=(workspace/"Harness"/"plugin").resolve()
    if not (plugin/"package.json").is_file(): return fail("QuestOps Harness bundle is missing")
    owned_home=args.dsh_home is None
    home=Path(args.dsh_home).resolve() if args.dsh_home else Path(tempfile.mkdtemp(prefix="questops-dsh-"))
    env=os.environ.copy(); env["DSH_HOME"]=str(home); env["QUESTOPS_PROJECT_ROOT"]=str(workspace)
    env["DSH_TOOLS_MODE"]="native"
    env["DSH_SYSTEM_PROMPT"]="You are the QuestOps RC1 authoring agent. Use only the provided read-only grounding tools."
    dsh=shutil.which("dsh")
    if not dsh: return fail("dsh executable from deepseek-harness-runtime-bin is unavailable")

    try:
        subprocess.run([dsh,"--profile","sdk-minimal","--dump-default-config"],env=env,cwd=workspace,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([dsh,"plugin","--profile","sdk-minimal","add",f"file:{plugin}"],env=env,cwd=workspace,check=True)
        session_id="questops-live-"+uuid.uuid4().hex[:12]
        prompt=(
            "User request: "+args.intent+"\n"
            "Create a draft only if that request is compatible with the frozen QuestOps RC1 capability. "
            "You MUST call "
            "questops_read_project_contract and questops_read_authoring_skill before answering. "
            "Return ONLY one JSON object with exactly these keys: schemaVersion,id,minPlayerLevel,npcId,"
            "itemId,itemCount,goldReward,claimPolicy. Preserve the grounded contract exactly. "
            "No markdown, explanation, hidden requirements, or invented identifiers."
        )
        with DeepSeekHarness(
            dsh_home=str(home),cwd=str(workspace),provider=args.provider,model=args.model,
            profile="sdk-minimal",env={
                "QUESTOPS_PROJECT_ROOT":str(workspace),
                "DSH_TOOLS_MODE":"native",
                "DSH_SYSTEM_PROMPT":"You are the QuestOps RC1 authoring agent. Use only the provided read-only grounding tools.",
            },request_timeout_seconds=120.0,
        ) as harness:
            result=harness.run(prompt,session_id=session_id)

        events=jsonable(result.events); serialized=json.dumps(events,ensure_ascii=False,sort_keys=True)
        visible=visible_request_tools(events)
        if not visible:
            print("FAIL: live Harness evidence contains no request/header tool surface",file=sys.stderr); return 1
        unexpected=sorted(visible-ALLOWED_TOOL_SET)
        if unexpected:
            print("FAIL: RC1 exposed tools outside the read-only allowlist: "+", ".join(unexpected),file=sys.stderr); return 1
        missing_visible=sorted(ALLOWED_TOOL_SET-visible)
        if missing_visible:
            print("FAIL: RC1 grounding tools were not visible: "+", ".join(missing_visible),file=sys.stderr); return 1
        missing=[name for name in TOOLS if name not in serialized]
        if missing:
            print("FAIL: real Harness turn omitted required tool calls: "+", ".join(missing),file=sys.stderr); return 1
        try: draft=parse_draft(result.final_response)
        except (json.JSONDecodeError,ValueError,QuestValidationError) as exc:
            print(f"FAIL: model draft is not a valid canonical quest: {exc}",file=sys.stderr); return 1

        draft_bytes=(json.dumps(draft,sort_keys=True,separators=(",",":"),ensure_ascii=False)+"\n").encode("utf-8")
        draft_path=Path(args.draft); draft_path.parent.mkdir(parents=True,exist_ok=True); draft_path.write_bytes(draft_bytes)
        evidence={
            "schemaVersion":2,"mode":"live","liveModel":True,"provider":args.provider,"model":args.model,
            "sessionId":result.session_id,"finishReason":result.finish_reason,"commitSha":git_sha(workspace),
            "sdkVersion":importlib.metadata.version("deepseek-harness-sdk"),"requiredTools":list(TOOLS),
            "visibleTools":sorted(visible),"toolSurfaceRestricted":visible==ALLOWED_TOOL_SET,
            "eventCount":len(result.events),"eventSha256":sha256_bytes(serialized.encode("utf-8")),
            "finalResponseSha256":sha256_bytes(result.final_response.encode("utf-8")),
            "draftPath":str(draft_path),"draftSha256":sha256_bytes(draft_bytes),
            "pluginManifestSha256":sha256_bytes((plugin/"package.json").read_bytes()),
        }
        path=Path(args.evidence); path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(evidence,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        print(json.dumps(evidence,ensure_ascii=False)); return 0
    finally:
        if owned_home and not args.keep_home: shutil.rmtree(home,ignore_errors=True)

if __name__=="__main__": raise SystemExit(main())
