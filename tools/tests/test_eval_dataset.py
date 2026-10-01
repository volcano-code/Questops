import json, sys, unittest
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from evals.run_eval import load_cases, parse_envelope

class EvalDatasetTests(unittest.TestCase):
    def setUp(self):
        self.cases=load_cases(ROOT/"evals"/"cases.jsonl")

    def test_dataset_has_30_unique_cases(self):
        self.assertEqual(30,len(self.cases))
        self.assertEqual(30,len({c["id"] for c in self.cases}))

    def test_dataset_covers_required_behavior_classes(self):
        counts=Counter(c["category"] for c in self.cases)
        self.assertEqual({
            "normal":10,"missing":5,"unknown_resource":5,"out_of_scope":5,"requirement_drift":5
        },counts)

    def test_expected_decisions_are_well_formed(self):
        self.assertEqual({"draft","clarify","refuse"},{c["expectedDecision"] for c in self.cases})

    def test_envelope_parser_accepts_clarify_and_refuse(self):
        self.assertEqual("clarify",parse_envelope('{"decision":"clarify","missing":["itemCount"]}')["decision"])
        self.assertEqual("refuse",parse_envelope('{"decision":"refuse","reason":"unsupported"}')["decision"])

if __name__=="__main__": unittest.main()
