using System;
using System.Collections;
using System.IO;
using NUnit.Framework;
using UnityEngine;
using UnityEngine.TestTools;

namespace QuestOps.Tests.PlayMode
{
    [Serializable]
    internal sealed class CanonicalQuestDocument
    {
        public int schemaVersion;
        public string id;
        public int minPlayerLevel;
        public string npcId;
        public string itemId;
        public int itemCount;
        public int goldReward;
        public string claimPolicy;
    }

    public sealed class CanonicalQuestPlayModeTests
    {
        private static string ResolveArtifact()
        {
            var explicitPath = Environment.GetEnvironmentVariable("QUESTOPS_CANONICAL_ARTIFACT");
            if (!string.IsNullOrWhiteSpace(explicitPath)) return explicitPath;
            return Path.Combine(Directory.GetCurrentDirectory(), "Schemas", "canonical-quest.json");
        }

        [UnityTest]
        public IEnumerator AppliedArtifact_DrivesCanonicalOutcome_ExactlyOnce()
        {
            var artifactPath = ResolveArtifact();
            Assert.IsTrue(File.Exists(artifactPath), $"canonical artifact missing: {artifactPath}");
            var doc = JsonUtility.FromJson<CanonicalQuestDocument>(File.ReadAllText(artifactPath));

            Assert.NotNull(doc);
            Assert.AreEqual(1, doc.schemaVersion);
            Assert.AreEqual("quest_blacksmith_001", doc.id);
            Assert.AreEqual(5, doc.minPlayerLevel);
            Assert.AreEqual("npc_blacksmith_01", doc.npcId);
            Assert.AreEqual("item_iron_ore", doc.itemId);
            Assert.AreEqual(3, doc.itemCount);
            Assert.AreEqual(100, doc.goldReward);
            Assert.AreEqual("once", doc.claimPolicy);

            var quest = new CanonicalQuestRuntime();
            Assert.AreEqual("level_too_low", quest.TalkToBlacksmith(4));
            Assert.AreEqual("quest_started", quest.TalkToBlacksmith(doc.minPlayerLevel));
            Assert.AreEqual(doc.itemCount, quest.CollectIronOre(doc.itemCount));
            Assert.AreEqual("quest_completed", quest.TalkToBlacksmith(doc.minPlayerLevel));
            Assert.IsTrue(quest.Completed);
            Assert.IsTrue(quest.RewardClaimed);
            Assert.AreEqual(doc.goldReward, quest.Gold);

            Assert.AreEqual("already_completed", quest.TalkToBlacksmith(doc.minPlayerLevel));
            Assert.AreEqual(doc.goldReward, quest.Gold, "reward must be granted exactly once");
            yield return null;
        }
    }
}
