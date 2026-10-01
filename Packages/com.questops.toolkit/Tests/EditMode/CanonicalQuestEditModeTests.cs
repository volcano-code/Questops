using NUnit.Framework;

namespace QuestOps.Tests.EditMode
{
    public sealed class CanonicalQuestEditModeTests
    {
        [Test]
        public void LevelGateAndRewardContractAreDeterministic()
        {
            var quest = new CanonicalQuestRuntime();
            Assert.AreEqual("level_too_low", quest.TalkToBlacksmith(4));
            Assert.AreEqual("quest_started", quest.TalkToBlacksmith(5));
            Assert.AreEqual(3, quest.CollectIronOre(3));
            Assert.AreEqual("quest_completed", quest.TalkToBlacksmith(5));
            Assert.AreEqual(100, quest.Gold);
            Assert.AreEqual("already_completed", quest.TalkToBlacksmith(5));
            Assert.AreEqual(100, quest.Gold);
        }
    }
}
