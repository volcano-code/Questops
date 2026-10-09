import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from Harness.adapter import AdapterRequest, HarnessAdapterError, HttpHarnessAdapter, MockHarnessAdapter
from Agent.questops_core import validate_quest

class HarnessAdapterTests(unittest.TestCase):
    def test_mock_is_deterministic_and_valid(self):
        adapter = MockHarnessAdapter()
        first = adapter.generate_quest_draft(AdapterRequest("r1", "canonical"))
        second = adapter.generate_quest_draft(AdapterRequest("r1", "canonical"))
        self.assertEqual(first.draft, second.draft)
        validate_quest(first.draft)

    def test_mock_can_never_be_live_evidence(self):
        result = MockHarnessAdapter().generate_quest_draft(AdapterRequest("r1", "canonical"))
        self.assertEqual("mock", result.mode)
        self.assertFalse(result.live_model)
        self.assertIsNone(result.trace_id)

    def test_request_requires_identity_and_intent(self):
        for payload in (AdapterRequest("", "x"), AdapterRequest("r", "")):
            with self.assertRaises(HarnessAdapterError):
                MockHarnessAdapter().generate_quest_draft(payload)

    def test_live_adapter_requires_endpoint_and_token(self):
        with self.assertRaises(HarnessAdapterError): HttpHarnessAdapter("file:///tmp/x", "token")
        with self.assertRaises(HarnessAdapterError): HttpHarnessAdapter("https://localhost", "")

if __name__ == "__main__":
    unittest.main()
