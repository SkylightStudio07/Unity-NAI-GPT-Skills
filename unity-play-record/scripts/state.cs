var s = UnityEngine.SceneManagement.SceneManager.GetActiveScene();
return $"playing={UnityEditor.EditorApplication.isPlaying} compiling={UnityEditor.EditorApplication.isCompiling} dirty={s.isDirty} scene={s.name} gfx={UnityEngine.SystemInfo.graphicsDeviceType}";
