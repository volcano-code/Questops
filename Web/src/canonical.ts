export const canonicalQuest = {
  minPlayerLevel: 5,
  npcId: "npc_blacksmith_01",
  itemId: "item_iron_ore",
  itemCount: 3,
  goldReward: 100,
  claimPolicy: "once",
} as const;

export function canonicalSummary(): string {
  return `Lv${canonicalQuest.minPlayerLevel} → ${canonicalQuest.npcId} → ${canonicalQuest.itemId} ×${canonicalQuest.itemCount} → ${canonicalQuest.goldReward} gold → ${canonicalQuest.claimPolicy}`;
}
