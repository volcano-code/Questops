"""Regression tests for release gate integrity (no external execution claims)."""
import copy
import unittest
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from tools.release_gate import main

from tools.release_gate import validate

BASE = {
    "gates": {
        name: {"status": "NOT_RUN", "reason": "not executed", "evidence": None}
        for name in ("backend", "web", "harnessLive", "unityEditMode", "unityPlayMode", "fullE2E")
    },
    "policy": {
        "fixtureIsNotLiveModel": True,
        "inventoryIsNotUnityExecution": True,
        "approvalRequiredBeforeApply": True,
    },
}


class ReleaseGatePolicyTests(unittest.TestCase):
    def test_not_run_requires_reason(self):
        case = copy.deepcopy(BASE)
        case["gates"]["unityPlayMode"]["reason"] = None
        self.assertTrue(any("unityPlayMode" in x for x in validate(case)))

    def test_blocked_requires_reason(self):
        case = copy.deepcopy(BASE)
        case["gates"]["harnessLive"] = {"status": "BLOCKED", "reason": "", "evidence": None}
        self.assertTrue(validate(case))

    def test_pass_requires_evidence(self):
        case = copy.deepcopy(BASE)
        case["gates"]["fullE2E"] = {"status": "PASS", "evidence": None}
        self.assertTrue(validate(case))

    def test_policy_cannot_be_disabled(self):
        for key in BASE["policy"]:
            case = copy.deepcopy(BASE)
            case["policy"][key] = False
            self.assertTrue(any(key in x for x in validate(case)))

    def test_strict_release_rejects_incomplete_but_normal_ci_allows_it(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gates.json"
            path.write_text(json.dumps(BASE), encoding="utf-8")
            with patch("sys.argv", ["release_gate.py", str(path)]):
                self.assertEqual(main(), 2)
            with patch("sys.argv", ["release_gate.py", str(path), "--require-complete"]):
                self.assertEqual(main(), 1)

    def test_strict_release_accepts_all_pass_with_evidence(self):
        case = copy.deepcopy(BASE)
        for gate in case["gates"].values():
            gate.update(status="PASS", evidence="artifacts/verified.json", reason=None)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "gates.json"
            path.write_text(json.dumps(case), encoding="utf-8")
            with patch("sys.argv", ["release_gate.py", str(path), "--require-complete"]):
                self.assertEqual(main(), 0)

    def test_unexecuted_gates_remain_valid_but_incomplete(self):
        self.assertEqual(validate(BASE), [])


if __name__ == "__main__":
    unittest.main()
