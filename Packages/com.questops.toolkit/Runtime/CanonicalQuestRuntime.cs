using System;

namespace QuestOps
{
    public sealed class CanonicalQuestRuntime
    {
        public bool Active { get; private set; }
        public int Collected { get; private set; }
        public bool Completed { get; private set; }
        public bool RewardClaimed { get; private set; }
        public int Gold { get; private set; }

        public string TalkToBlacksmith(int playerLevel)
        {
            if (Completed) return "already_completed";
            if (!Active)
            {
                if (playerLevel < 5) return "level_too_low";
                Active = true;
                return "quest_started";
            }

            if (Collected < 3) return "need_more_items";

            Completed = true;
            if (!RewardClaimed)
            {
                Gold += 100;
                RewardClaimed = true;
            }
            return "quest_completed";
        }

        public int CollectIronOre(int amount = 1)
        {
            if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
            if (!Active || Completed) return Collected;
            Collected = Math.Min(3, Collected + amount);
            return Collected;
        }
    }
}
