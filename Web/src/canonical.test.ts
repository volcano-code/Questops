import { describe, expect, it } from "vitest";
import { canonicalQuest, canonicalSummary } from "./canonical";

describe("canonical quest", () => {
  it("preserves the frozen release requirements", () => {
    expect(canonicalQuest).toEqual({
      schemaVersion: 1,
      id: "quest_blacksmith_001",
      minPlayerLevel: 5,
      npcId: "npc_blacksmith_01",
      itemId: "item_iron_ore",
      itemCount: 3,
      goldReward: 100,
      claimPolicy: "once",
    });
  });

  it("renders an auditable summary", () => {
    expect(canonicalSummary()).toContain("100 gold");
    expect(canonicalSummary()).toContain("item_iron_ore ×3");
  });
});
