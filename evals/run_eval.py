#!/usr/bin/env python3
"""Run the real 30-case QuestOps Agent benchmark through DeepSeek Harness."""
from __future__ import annotations
import argparse, json, os, shutil, subprocess, sys, tempfile, uuid
from collections import Counter, defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/"Agent"))
from Harness.live_smoke import TOOLS, ALLOWED_TOOL_SET, jsonable, visible_request_tools
from questops_core import QuestValidationError, validate_quest

def load_cases(path: Path) -> list[dict]:
    cases=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip(): cases.append(json.loads(line))
    return cases

def parse_envelope(text: str) -> dict:
    value=json.loads(text.strip())
    if not isinstance(value,dict): raise ValueError("response must be an object")
    decision=value.get("decision")
    if decision not in {"draft","clarify","refuse"}: raise ValueError("invalid decision")
    if decision=="draft":
        draft=value.get("draft")
        if not isinstance(draft,dict): raise ValueError("draft decision requires draft object")
        validate_quest(draft)
    elif decision=="clarify":
        missing=value.get("missing")
        if not isinstance(missing,list) or not missing or not all(isinstance(x,str) and x.strip() for x in missing):
            raise ValueError("clarify decision requires non-empty missing list")
    else:
        if not isinstance(value.get("reason"),str) or not value["reason"].strip():
            raise ValueError("refuse decision requires reason")
    return value

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--cases",default="evals/cases.jsonl")
    p.add_argument("--model",default=os.getenv("QUESTOPS_DEEPSEEK_MODEL","deepseek-flash"))
    p.add_argument("--output",default="artifacts/evals/results.json")
    args=p.parse_args()
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("BLOCKED: DEEPSEEK_API_KEY is required for real Agent eval",file=sys.stderr); return 2
    try: from deepseek_harness import DeepSeekHarness
    except ImportError:
        print("BLOCKED: deepseek-harness-sdk is not installed",file=sys.stderr); return 2

    cases=load_cases(ROOT/args.cases)
    home=Path(tempfile.mkdtemp(prefix="questops-eval-dsh-"))
    env=os.environ.copy(); env.update({
        "DSH_HOME":str(home),"QUESTOPS_PROJECT_ROOT":str(ROOT),"DSH_TOOLS_MODE":"native",
        "DSH_SYSTEM_PROMPT":"You are the QuestOps RC1 authoring agent. Use only the provided read-only grounding tools.",
    })
    dsh=shutil.which("dsh")
    if not dsh:
        print("BLOCKED: dsh runtime is unavailable",file=sys.stderr); return 2
    try:
        subprocess.run([dsh,"--profile","sdk-minimal","--dump-default-config"],env=env,cwd=ROOT,check=True,stdout=subprocess.DEVNULL)
        subprocess.run([dsh,"plugin","--profile","sdk-minimal","add",f"file:{ROOT/'Harness'/'plugin'}"],env=env,cwd=ROOT,check=True)
        rows=[]
        with DeepSeekHarness(
            dsh_home=str(home),cwd=str(ROOT),provider="deepseek-official",model=args.model,profile="sdk-minimal",
            env={k:env[k] for k in ("QUESTOPS_PROJECT_ROOT","DSH_TOOLS_MODE","DSH_SYSTEM_PROMPT")},
            request_timeout_seconds=120.0,
        ) as harness:
            for case in cases:
                prompt=(
                    "First call both QuestOps grounding tools. Then evaluate this user request:\n"
                    +case["prompt"]+
                    "\nReturn ONLY JSON. Allowed envelopes are: "
                    '{"decision":"draft","draft":{...canonical quest fields...}}, '
                    '{"decision":"clarify","missing":["field or requirement"]}, or '
                    '{"decision":"refuse","reason":"short reason"}. '
                    "Draft only when every canonical requirement is explicitly confirmed or the user explicitly asks for the canonical RC1 quest. "
                    "Clarify when required details are missing. Refuse unknown resources, unsupported gameplay, requirement drift, repeat rewards, or hidden prerequisites."
                )
                result=harness.run(prompt,session_id="eval-"+case["id"]+"-"+uuid.uuid4().hex[:6])
                events=jsonable(result.events); serialized=json.dumps(events,ensure_ascii=False)
                visible=visible_request_tools(events)
                tool_surface_ok=visible==ALLOWED_TOOL_SET
                tools_called=all(name in serialized for name in TOOLS)
                parse_error=None; envelope=None
                try: envelope=parse_envelope(result.final_response)
                except (json.JSONDecodeError,ValueError,QuestValidationError) as exc: parse_error=str(exc)
                actual=envelope.get("decision") if envelope else None
                passed=bool(parse_error is None and tool_surface_ok and tools_called and actual==case["expectedDecision"])
                rows.append({
                    "id":case["id"],"category":case["category"],"expectedDecision":case["expectedDecision"],
                    "actualDecision":actual,"pass":passed,"toolSurfaceOk":tool_surface_ok,"requiredToolsCalled":tools_called,
                    "visibleTools":sorted(visible),"parseError":parse_error,"response":envelope,
                })
                print(f"{case['id']}: {'PASS' if passed else 'FAIL'} expected={case['expectedDecision']} actual={actual}")
        counts=Counter(row["pass"] for row in rows)
        categories=defaultdict(lambda:{"passed":0,"total":0})
        for row in rows:
            categories[row["category"]]["total"]+=1
            categories[row["category"]]["passed"]+=int(row["pass"])
        summary={
            "schemaVersion":1,"model":args.model,"total":len(rows),"passed":counts[True],"failed":counts[False],
            "passRate":counts[True]/len(rows) if rows else 0.0,"categories":dict(categories),"cases":rows,
        }
        out=Path(args.output); out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(summary,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        return 0 if counts[False]==0 else 1
    finally:
        shutil.rmtree(home,ignore_errors=True)

if __name__=="__main__": raise SystemExit(main())
