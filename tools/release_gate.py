#!/usr/bin/env python3
"""QuestOps release-gate checker.

This script deliberately treats missing evidence as NOT_RUN/BLOCKED rather than
promoting source presence to execution success.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ALLOWED = {"PASS", "FAIL", "BLOCKED", "NOT_RUN"}
REQUIRED = (
    "backend",
    "web",
    "harnessLive",
    "unityEditMode",
    "unityPlayMode",
    "fullE2E",
)


def load_manifest(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate(manifest: dict) -> list[str]:
    errors: list[str] = []
    gates = manifest.get("gates")
    if not isinstance(gates, dict):
        return ["gates must be an object"]

    for name in REQUIRED:
        gate = gates.get(name)
        if not isinstance(gate, dict):
            errors.append(f"missing gate: {name}")
            continue
        status = gate.get("status")
        if status not in ALLOWED:
            errors.append(f"{name}: invalid status {status!r}")
        if status == "PASS" and not gate.get("evidence"):
            errors.append(f"{name}: PASS requires evidence")

    policy = manifest.get("policy", {})
    if policy.get("fixtureIsNotLiveModel") is not True:
        errors.append("fixtureIsNotLiveModel must remain true")
    if policy.get("inventoryIsNotUnityExecution") is not True:
        errors.append("inventoryIsNotUnityExecution must remain true")
    if policy.get("approvalRequiredBeforeApply") is not True:
        errors.append("approvalRequiredBeforeApply must remain true")
    return errors


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "verification/release-gates.json")
    manifest = load_manifest(path)
    errors = validate(manifest)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1

    statuses = {name: manifest["gates"][name]["status"] for name in REQUIRED}
    for name, status in statuses.items():
        print(f"{name}: {status}")

    if all(status == "PASS" for status in statuses.values()):
        print("OVERALL: PASS")
        return 0
    if any(status == "FAIL" for status in statuses.values()):
        print("OVERALL: FAIL")
        return 1

    print("OVERALL: INCOMPLETE")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
