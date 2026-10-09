"""Deterministic core for the QuestOps canonical vertical slice."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

CANONICAL_NPC = "npc_blacksmith_01"
CANONICAL_ITEM = "item_iron_ore"
REQUIRED_FIELDS = {
    "schemaVersion", "id", "minPlayerLevel", "npcId",
    "itemId", "itemCount", "goldReward", "claimPolicy",
}

class QuestValidationError(ValueError):
    pass

def _require_int(name: str, value: Any) -> int:
    if type(value) is not int:
        raise QuestValidationError(f"{name} must be an integer")
    return value

def validate_quest(data: dict[str, Any]) -> None:
    if not isinstance(data, dict):
        raise QuestValidationError("quest must be an object")
    missing = sorted(REQUIRED_FIELDS - data.keys())
    extra = sorted(data.keys() - REQUIRED_FIELDS)
    if missing:
        raise QuestValidationError("missing fields: " + ", ".join(missing))
    if extra:
        raise QuestValidationError("unexpected fields: " + ", ".join(extra))
    if _require_int("schemaVersion", data["schemaVersion"]) != 1:
        raise QuestValidationError("unsupported schemaVersion")
    if not isinstance(data["id"], str) or not data["id"].strip():
        raise QuestValidationError("id must be non-empty")
    if _require_int("minPlayerLevel", data["minPlayerLevel"]) != 5:
        raise QuestValidationError("canonical release case requires level 5")
    if data["npcId"] != CANONICAL_NPC:
        raise QuestValidationError("unknown npcId")
    if data["itemId"] != CANONICAL_ITEM:
        raise QuestValidationError("unknown itemId")
    if _require_int("itemCount", data["itemCount"]) != 3:
        raise QuestValidationError("canonical release case requires itemCount=3")
    if _require_int("goldReward", data["goldReward"]) != 100:
        raise QuestValidationError("canonical release case requires goldReward=100")
    if data["claimPolicy"] != "once":
        raise QuestValidationError("claimPolicy must be once")

@dataclass
class QuestRuntime:
    min_player_level: int = 5
    required_items: int = 3
    reward_gold: int = 100
    active: bool = False
    collected: int = 0
    completed: bool = False
    reward_claimed: bool = False
    gold: int = 0

    def talk_to_blacksmith(self, player_level: int) -> str:
        if type(player_level) is not int or player_level < 0:
            raise ValueError("player_level must be a non-negative integer")
        if self.completed:
            return "already_completed"
        if not self.active:
            if player_level < self.min_player_level:
                return "level_too_low"
            self.active = True
            return "quest_started"
        if self.collected < self.required_items:
            return "need_more_items"
        self.completed = True
        if not self.reward_claimed:
            self.gold += self.reward_gold
            self.reward_claimed = True
        return "quest_completed"

    def collect_iron_ore(self, amount: int = 1) -> int:
        if type(amount) is not int or amount < 0:
            raise ValueError("amount must be a non-negative integer")
        if not self.active or self.completed:
            return self.collected
        self.collected = min(self.required_items, self.collected + amount)
        return self.collected
