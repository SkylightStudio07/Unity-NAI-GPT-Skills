// Opens the scene named on line 1 of Temp/PlayRec/scene.txt and enters play mode. Refuses if playing or dirty.
if (UnityEditor.EditorApplication.isPlaying) return "playing";
if (UnityEngine.SceneManagement.SceneManager.GetActiveScene().isDirty) return "dirty";
var scene = System.IO.File.ReadAllLines("Temp/PlayRec/scene.txt")[0].Trim();
UnityEditor.SceneManagement.EditorSceneManager.OpenScene(scene);
UnityEditor.EditorApplication.isPlaying = true;
return "entering " + scene;
