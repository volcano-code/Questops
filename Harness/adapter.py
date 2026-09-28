"""Fail-closed adapter boundary for DeepSeek Harness.

Mock evidence can validate orchestration, but it can never promote harnessLive.
The HTTP adapter is a QuestOps-owned gateway boundary; a real Harness plugin or
SDK process must sit behind it and return liveModel=true plus a non-empty trace.
"""
from __future__ import annotations
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any
from urllib import request, error

ROOT = Path(__file__).resolve().parents[1]

class HarnessAdapterError(RuntimeError):
    pass

@dataclass(frozen=True)
class AdapterRequest:
    request_id: str
    intent: str
    project_root: str = "."

    def validate(self) -> None:
        if not self.request_id.strip():
            raise HarnessAdapterError("request_id is required")
        if not self.intent.strip():
            raise HarnessAdapterError("intent is required")

@dataclass(frozen=True)
class AdapterResponse:
    request_id: str
    draft: dict[str, Any]
    mode: str
    live_model: bool
    provider: str
    trace_id: str | None = None

class MockHarnessAdapter:
    def generate_quest_draft(self, payload: AdapterRequest) -> AdapterResponse:
        payload.validate()
        draft = json.loads((ROOT / "Schemas" / "canonical-quest.json").read_text(encoding="utf-8"))
        return AdapterResponse(
            request_id=payload.request_id,
            draft=draft,
            mode="mock",
            live_model=False,
            provider="questops-deterministic-fixture",
            trace_id=None,
        )

class HttpHarnessAdapter:
    def __init__(self, endpoint: str, token: str, timeout: float = 30.0):
        if not endpoint.startswith(("http://", "https://")):
            raise HarnessAdapterError("endpoint must be http(s)")
        if not token:
            raise HarnessAdapterError("token is required")
        self.endpoint = endpoint.rstrip("/")
        self.token = token
        self.timeout = timeout

    def generate_quest_draft(self, payload: AdapterRequest) -> AdapterResponse:
        payload.validate()
        body = json.dumps({
            "requestId": payload.request_id,
            "intent": payload.intent,
            "projectRoot": payload.project_root,
        }).encode("utf-8")
        req = request.Request(
            self.endpoint + "/adapter/v1/generate-quest-draft",
            data=body,
            headers={
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout) as response:
                raw = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise HarnessAdapterError(f"live Harness unavailable: {exc}") from exc

        evidence = raw.get("evidence") or {}
        if raw.get("status") != "ok":
            raise HarnessAdapterError("live Harness returned non-ok status")
        if evidence.get("mode") != "live" or evidence.get("liveModel") is not True:
            raise HarnessAdapterError("live endpoint did not prove a live model call")
        trace_id = evidence.get("traceId")
        if not isinstance(trace_id, str) or not trace_id.strip():
            raise HarnessAdapterError("live endpoint did not return traceId")
        draft = raw.get("draft")
        if not isinstance(draft, dict):
            raise HarnessAdapterError("live endpoint did not return a draft object")
        return AdapterResponse(
            request_id=payload.request_id,
            draft=draft,
            mode="live",
            live_model=True,
            provider=str(evidence.get("provider") or "deepseek-harness"),
            trace_id=trace_id,
        )
