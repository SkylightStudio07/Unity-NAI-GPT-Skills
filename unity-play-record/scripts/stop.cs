if (!UnityEditor.EditorApplication.isPlaying) return "not playing";
UnityEditor.EditorApplication.ExitPlaymode();
return "exiting";
