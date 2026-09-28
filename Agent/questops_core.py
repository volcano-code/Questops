"""Deterministic core for the QuestOps canonical vertical slice."""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any

CANONICAL_NPC = "npc_blacksmith_01"
CANONICAL_ITEM = "item_iron_ore"

class QuestValidationError(ValueError):
    pass

def validate_quest(data: dict[str, Any]) -> None:
    required = {
        "schemaVersion", "id", "minPlayerLevel", "npcId",
        "itemId", "itemCount", "goldReward", "claimPolicy",
    }
    missing = sorted(required - data.keys())
    if missing:
        raise QuestValidationError("missing fields: " + ", ".join(missing))
    if data["schemaVersion"] != 1:
        raise QuestValidationError("unsupported schemaVersion")
    if not isinstance(data["id"], str) or not data["id"].strip():
        raise QuestValidationError("id must be non-empty")
    if data["minPlayerLevel"] != 5:
        raise QuestValidationError("canonical release case requires level 5")
    if data["npcId"] != CANONICAL_NPC:
        raise QuestValidationError("unknown npcId")
    if data["itemId"] != CANONICAL_ITEM:
        raise QuestValidationError("unknown itemId")
    if data["itemCount"] != 3:
        raise QuestValidationError("canonical release case requires itemCount=3")
    if data["goldReward"] != 100:
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
        if amount < 0:
            raise ValueError("amount must be non-negative")
        if not self.active or self.completed:
            return self.collected
        self.collected = min(self.required_items, self.collected + amount)
        return self.collected
