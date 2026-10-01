using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace QuestOps.Editor
{
    public static class QuestOpsDemoSceneBuilder
    {
        public const string ScenePath = "Assets/QuestOpsDemo/QuestOpsDemo.unity";

        [MenuItem("QuestOps/Build Graybox Demo Scene")]
        public static void Build()
        {
            Directory.CreateDirectory("Assets/QuestOpsDemo");
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);

            var cameraGo = new GameObject("Main Camera");
            cameraGo.tag = "MainCamera";
            var camera = cameraGo.AddComponent<Camera>();
            cameraGo.transform.position = new Vector3(0f, 13f, -12f);
            cameraGo.transform.rotation = Quaternion.Euler(42f, 0f, 0f);
            camera.backgroundColor = new Color(0.06f, 0.08f, 0.12f);

            var lightGo = new GameObject("Directional Light");
            var light = lightGo.AddComponent<Light>();
            light.type = LightType.Directional;
            light.intensity = 1.2f;
            lightGo.transform.rotation = Quaternion.Euler(50f, -30f, 0f);

            var ground = GameObject.CreatePrimitive(PrimitiveType.Plane);
            ground.name = "Ground";
            ground.transform.localScale = new Vector3(2.2f, 1f, 2.2f);

            var player = Cube("Player", new Vector3(0f, 0.5f, -6f), new Color(0.2f, 0.65f, 1f));
            var blacksmith = Cube("npc_blacksmith_01", new Vector3(0f, 0.75f, 5f), new Color(1f, 0.45f, 0.15f));
            blacksmith.transform.localScale = new Vector3(1.5f, 1.5f, 1.5f);

            var ores = new Transform[3];
            ores[0] = Cube("item_iron_ore_01", new Vector3(-6f, 0.4f, 0f), new Color(0.55f, 0.58f, 0.62f)).transform;
            ores[1] = Cube("item_iron_ore_02", new Vector3(5f, 0.4f, 1f), new Color(0.55f, 0.58f, 0.62f)).transform;
            ores[2] = Cube("item_iron_ore_03", new Vector3(1f, 0.4f, 7f), new Color(0.55f, 0.58f, 0.62f)).transform;

            var controller = new GameObject("QuestOps Demo Controller").AddComponent<QuestOpsGrayboxDemo>();
            controller.player = player.transform;
            controller.blacksmith = blacksmith.transform;
            controller.oreNodes = ores;

            if (!EditorSceneManager.SaveScene(scene, ScenePath))
                throw new IOException("Failed to save QuestOps graybox scene");
            AssetDatabase.SaveAssets();
            Debug.Log("QuestOps graybox scene created: " + ScenePath);
        }

        private static GameObject Cube(string name, Vector3 position, Color color)
        {
            var go = GameObject.CreatePrimitive(PrimitiveType.Cube);
            go.name = name;
            go.transform.position = position;
            var renderer = go.GetComponent<Renderer>();
            var material = new Material(Shader.Find("Universal Render Pipeline/Lit") ?? Shader.Find("Standard"));
            material.color = color;
            renderer.sharedMaterial = material;
            return go;
        }
    }
}
