using System;
using System.IO;
using UnityEngine;

namespace QuestOps
{
    public sealed class QuestOpsGrayboxDemo : MonoBehaviour
    {
        public Transform player;
        public Transform blacksmith;
        public Transform[] oreNodes;
        public float moveSpeed = 5f;
        public float interactDistance = 2.25f;
        public int playerLevel = 5;

        private CanonicalQuestRuntime quest;
        private string status = "Walk to the blacksmith and press E.";
        private bool[] collectedNodes;

        private void Awake()
        {
            var spec = LoadSpec();
            quest = new CanonicalQuestRuntime(spec);
            collectedNodes = new bool[oreNodes?.Length ?? 0];
        }

        private CanonicalQuestSpec LoadSpec()
        {
            var explicitPath = Environment.GetEnvironmentVariable("QUESTOPS_CANONICAL_ARTIFACT");
            var path = string.IsNullOrWhiteSpace(explicitPath)
                ? Path.Combine(Directory.GetCurrentDirectory(), "Schemas", "canonical-quest.json")
                : explicitPath;
            if (!File.Exists(path)) return new CanonicalQuestSpec();
            var spec = JsonUtility.FromJson<CanonicalQuestSpec>(File.ReadAllText(path));
            if (spec == null) throw new InvalidDataException("QuestOps canonical quest JSON could not be parsed");
            spec.Validate();
            return spec;
        }

        private void Update()
        {
            if (player == null) return;
            var delta = new Vector3(Input.GetAxisRaw("Horizontal"), 0f, Input.GetAxisRaw("Vertical"));
            if (delta.sqrMagnitude > 1f) delta.Normalize();
            player.position += delta * moveSpeed * Time.deltaTime;

            if (Input.GetKeyDown(KeyCode.E)) Interact();
        }

        public void Interact()
        {
            if (player == null || blacksmith == null) return;
            if (Vector3.Distance(player.position, blacksmith.position) <= interactDistance)
            {
                var result = quest.TalkToBlacksmith(playerLevel);
                status = result switch
                {
                    "quest_started" => "Quest started: collect 3 iron ore.",
                    "need_more_items" => $"Need more iron ore ({quest.Collected}/{quest.Spec.itemCount}).",
                    "quest_completed" => $"Quest complete! +{quest.Spec.goldReward} gold.",
                    "already_completed" => "Already completed. No duplicate reward.",
                    "level_too_low" => $"Requires level {quest.Spec.minPlayerLevel}.",
                    _ => result,
                };
                return;
            }

            if (!quest.Active)
            {
                status = "Talk to the blacksmith first.";
                return;
            }

            for (var i = 0; i < (oreNodes?.Length ?? 0); i++)
            {
                if (collectedNodes[i] || oreNodes[i] == null) continue;
                if (Vector3.Distance(player.position, oreNodes[i].position) > interactDistance) continue;
                collectedNodes[i] = true;
                quest.CollectIronOre(1);
                oreNodes[i].gameObject.SetActive(false);
                status = $"Iron ore collected ({quest.Collected}/{quest.Spec.itemCount}).";
                return;
            }
            status = "Nothing to interact with here.";
        }

        private void OnGUI()
        {
            var style = new GUIStyle(GUI.skin.box) { alignment = TextAnchor.UpperLeft, fontSize = 16 };
            style.normal.textColor = Color.white;
            GUI.Box(new Rect(18, 18, 440, 145),
                $"QuestOps Graybox\nLevel: {playerLevel}   Gold: {quest?.Gold ?? 0}\n" +
                $"Ore: {quest?.Collected ?? 0}/{quest?.Spec.itemCount ?? 3}   Completed: {quest?.Completed ?? false}\n" +
                $"WASD: move   E: interact\n{status}", style);
        }
    }
}
