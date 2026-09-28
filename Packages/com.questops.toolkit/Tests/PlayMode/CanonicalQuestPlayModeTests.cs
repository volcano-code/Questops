using System.Collections;
using NUnit.Framework;
using UnityEngine.TestTools;

namespace QuestOps.Tests.PlayMode
{
    public sealed class CanonicalQuestPlayModeTests
    {
        [UnityTest]
        public IEnumerator Level5_Blacksmith_ThreeIron_OneHundredGold_ExactlyOnce()
        {
            var quest = new CanonicalQuestRuntime();

            Assert.AreEqual("level_too_low", quest.TalkToBlacksmith(4));
            Assert.AreEqual("quest_started", quest.TalkToBlacksmith(5));
            Assert.AreEqual(3, quest.CollectIronOre(3));
            Assert.AreEqual("quest_completed", quest.TalkToBlacksmith(5));
            Assert.IsTrue(quest.Completed);
            Assert.IsTrue(quest.RewardClaimed);
            Assert.AreEqual(100, quest.Gold);

            Assert.AreEqual("already_completed", quest.TalkToBlacksmith(5));
            Assert.AreEqual(100, quest.Gold, "reward must be granted exactly once");

            yield return null;
        }
    }
}
