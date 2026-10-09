import json
import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "Agent"))

from questops_core import QuestRuntime, QuestValidationError, validate_quest

class CanonicalQuestTests(unittest.TestCase):
    def load(self):
        return json.loads((ROOT / "Schemas" / "canonical-quest.json").read_text(encoding="utf-8"))

    def test_contract_is_valid(self):
        validate_quest(self.load())

    def test_unknown_resource_is_rejected(self):
        data = self.load(); data["npcId"] = "npc_hallucinated"
        with self.assertRaises(QuestValidationError): validate_quest(data)

    def test_requirement_drift_is_rejected(self):
        data = self.load(); data["goldReward"] = 99
        with self.assertRaises(QuestValidationError): validate_quest(data)

    def test_extra_field_is_rejected(self):
        data = self.load(); data["hiddenRequirement"] = "quest_secret"
        with self.assertRaises(QuestValidationError): validate_quest(data)

    def test_bool_cannot_smuggle_integer(self):
        data = self.load(); data["minPlayerLevel"] = True
        with self.assertRaises(QuestValidationError): validate_quest(data)

    def test_float_cannot_smuggle_integer(self):
        data = self.load(); data["itemCount"] = 3.0
        with self.assertRaises(QuestValidationError): validate_quest(data)

    def test_level_gate(self):
        runtime = QuestRuntime()
        self.assertEqual("level_too_low", runtime.talk_to_blacksmith(4))
        self.assertFalse(runtime.active)

    def test_collect_before_start_does_nothing(self):
        runtime = QuestRuntime()
        self.assertEqual(0, runtime.collect_iron_ore(3))

    def test_collection_is_capped(self):
        runtime = QuestRuntime(); runtime.talk_to_blacksmith(5)
        self.assertEqual(3, runtime.collect_iron_ore(99))

    def test_invalid_runtime_inputs_are_rejected(self):
        runtime = QuestRuntime()
        for value in (-1, True, 5.0):
            with self.assertRaises(ValueError): runtime.talk_to_blacksmith(value)
        for value in (-1, True, 1.0):
            with self.assertRaises(ValueError): runtime.collect_iron_ore(value)

    def test_exactly_once_reward(self):
        runtime = QuestRuntime()
        self.assertEqual("quest_started", runtime.talk_to_blacksmith(5))
        self.assertEqual(3, runtime.collect_iron_ore(3))
        self.assertEqual("quest_completed", runtime.talk_to_blacksmith(5))
        self.assertEqual(100, runtime.gold)
        self.assertEqual("already_completed", runtime.talk_to_blacksmith(5))
        self.assertEqual(100, runtime.gold)

if __name__ == "__main__":
    unittest.main()
