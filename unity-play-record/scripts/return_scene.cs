// After play mode: reopens the scene the editor was on before (line 2 of Temp/PlayRec/scene.txt: a path or a
// scene name), so the user finds the editor as they left it.
if (UnityEditor.EditorApplication.isPlaying) return "playing";
if (UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty) return "dirty";
var lines = System.IO.File.ReadAllLines("Temp/PlayRec/scene.txt");
var back = lines.Length > 1 ? lines[1].Trim() : "";
if (back == "") return "stay";
if (!back.EndsWith(".unity")) {
  foreach (var g in UnityEditor.AssetDatabase.FindAssets("t:Scene " + back)) {
    var p = UnityEditor.AssetDatabase.GUIDToAssetPath(g);
    if (System.IO.Path.GetFileNameWithoutExtension(p) == back) { back = p; break; }
  }
}
if (!back.EndsWith(".unity")) return "scene not found: " + back;
UnityEditor.SceneManagement.EditorSceneManager.OpenScene(back);
return "back to " + back;
