#if UNITY_EDITOR
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;

namespace Ramakien.Moba.EditorTools
{
    /// <summary>Runs once when the project opens: creates the Main scene, adds it to the build and sets the player options.
    /// The game builds itself at runtime (see GameController.Boot), so the scene can stay empty.</summary>
    [InitializeOnLoad]
    public static class ProjectSetup
    {
        const string ScenePath = "Assets/Scenes/Main.unity";

        static ProjectSetup()
        {
            EditorApplication.delayCall += Run;
        }

        [MenuItem("Ramakien/Run setup again")]
        public static void Run()
        {
            if (EditorApplication.isPlayingOrWillChangePlaymode) return;
            PlayerSettings.companyName = "Prontera Ramakien";
            PlayerSettings.productName = "Suek Lanka MOBA";
            PlayerSettings.colorSpace = ColorSpace.Gamma;          // colours in the shaders are authored for gamma space
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.ramakien.suuklanka");
            PlayerSettings.runInBackground = true;

            if (!File.Exists(ScenePath))
            {
                Directory.CreateDirectory("Assets/Scenes");
                var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
                EditorSceneManager.SaveScene(scene, ScenePath);
                AssetDatabase.Refresh();
            }
            var inBuild = false;
            foreach (var s in EditorBuildSettings.scenes) if (s.path == ScenePath) inBuild = true;
            if (!inBuild) EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(ScenePath, true) };
            if (!EditorSceneManager.GetActiveScene().IsValid() || EditorSceneManager.GetActiveScene().path != ScenePath)
            {
                if (!EditorApplication.isPlaying) EditorSceneManager.OpenScene(ScenePath, OpenSceneMode.Single);
            }
        }
    }

    public static class BuildTools
    {
        [MenuItem("Ramakien/Build Windows (.exe)")]
        public static void BuildWindows()
        {
            ProjectSetup.Run();
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { "Assets/Scenes/Main.unity" },
                locationPathName = "Builds/Windows/SuekLanka.exe",
                target = BuildTarget.StandaloneWindows64,
                options = BuildOptions.None
            });
            Debug.Log("Windows build: " + report.summary.result + "  -> Builds/Windows/SuekLanka.exe");
            EditorUtility.RevealInFinder("Builds/Windows/SuekLanka.exe");
        }

        [MenuItem("Ramakien/Build Android (.apk)")]
        public static void BuildAndroid()
        {
            ProjectSetup.Run();
            EditorUserBuildSettings.buildAppBundle = false;
            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                scenes = new[] { "Assets/Scenes/Main.unity" },
                locationPathName = "Builds/Android/SuekLanka.apk",
                target = BuildTarget.Android,
                options = BuildOptions.None
            });
            Debug.Log("Android build: " + report.summary.result + "  -> Builds/Android/SuekLanka.apk");
        }
    }
}
#endif
