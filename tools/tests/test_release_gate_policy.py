"""Regression tests for release gate integrity (no external execution claims)."""
import copy
import unittest

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

    def test_unexecuted_gates_remain_valid_but_incomplete(self):
        self.assertEqual(validate(BASE), [])


if __name__ == "__main__":
    unittest.main()
