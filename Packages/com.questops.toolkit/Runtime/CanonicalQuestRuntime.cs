using System;

namespace QuestOps
{
    [Serializable]
    public sealed class CanonicalQuestSpec
    {
        public int schemaVersion = 1;
        public string id = "quest_blacksmith_001";
        public int minPlayerLevel = 5;
        public string npcId = "npc_blacksmith_01";
        public string itemId = "item_iron_ore";
        public int itemCount = 3;
        public int goldReward = 100;
        public string claimPolicy = "once";

        public void Validate()
        {
            if (schemaVersion != 1) throw new ArgumentException("unsupported schemaVersion");
            if (id != "quest_blacksmith_001") throw new ArgumentException("unsupported quest id");
            if (minPlayerLevel != 5) throw new ArgumentException("canonical quest requires level 5");
            if (npcId != "npc_blacksmith_01") throw new ArgumentException("unknown npcId");
            if (itemId != "item_iron_ore") throw new ArgumentException("unknown itemId");
            if (itemCount != 3) throw new ArgumentException("canonical quest requires three items");
            if (goldReward != 100) throw new ArgumentException("canonical quest requires 100 gold");
            if (claimPolicy != "once") throw new ArgumentException("claimPolicy must be once");
        }
    }

    public sealed class CanonicalQuestRuntime
    {
        private readonly CanonicalQuestSpec spec;

        public bool Active { get; private set; }
        public int Collected { get; private set; }
        public bool Completed { get; private set; }
        public bool RewardClaimed { get; private set; }
        public int Gold { get; private set; }
        public CanonicalQuestSpec Spec => spec;

        public CanonicalQuestRuntime() : this(new CanonicalQuestSpec()) { }

        public CanonicalQuestRuntime(CanonicalQuestSpec spec)
        {
            this.spec = spec ?? throw new ArgumentNullException(nameof(spec));
            this.spec.Validate();
        }

        public string TalkToBlacksmith(int playerLevel)
        {
            if (playerLevel < 0) throw new ArgumentOutOfRangeException(nameof(playerLevel));
            if (Completed) return "already_completed";
            if (!Active)
            {
                if (playerLevel < spec.minPlayerLevel) return "level_too_low";
                Active = true;
                return "quest_started";
            }

            if (Collected < spec.itemCount) return "need_more_items";

            Completed = true;
            if (!RewardClaimed)
            {
                Gold += spec.goldReward;
                RewardClaimed = true;
            }
            return "quest_completed";
        }

        public int CollectIronOre(int amount = 1)
        {
            if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
            if (!Active || Completed) return Collected;
            Collected = Math.Min(spec.itemCount, Collected + amount);
            return Collected;
        }
    }
}
