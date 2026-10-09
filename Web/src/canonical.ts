import source from "../../Schemas/canonical-quest.json";

export type CanonicalQuest = {
  schemaVersion: number;
  id: string;
  minPlayerLevel: number;
  npcId: string;
  itemId: string;
  itemCount: number;
  goldReward: number;
  claimPolicy: string;
};

export const canonicalQuest: Readonly<CanonicalQuest> = Object.freeze(source);

export function canonicalSummary(): string {
  return `Lv${canonicalQuest.minPlayerLevel} → ${canonicalQuest.npcId} → ${canonicalQuest.itemId} ×${canonicalQuest.itemCount} → ${canonicalQuest.goldReward} gold → ${canonicalQuest.claimPolicy}`;
}
