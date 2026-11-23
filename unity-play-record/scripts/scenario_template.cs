// Scenario template (runs inside play mode via `unity command eval_file`). Copy it next to your project's
// notes, fill in the two TODO parts, and pass the copy to record.sh with --scenario.
//
// Contract with record.sh:
//   - Temp/PlayRec/job.txt line 1 = tag, lines 2.. = whatever record.sh got after --arg (free use)
//   - write frames as Temp/PlayRec/<tag>/<part>_NNN.jpg (960x540), then Temp/PlayRec/<tag>/done.txt
//   - done.txt text is printed in the RESULT line; start it with "ok" or explain what went wrong
// Rec() captures at a fixed 30 fps (Time.captureFramerate), so the video plays at real speed even if the
// editor renders slower.
if (!UnityEngine.Application.isPlaying) return "NOT PLAYING";
if (UnityEngine.GameObject.Find("__rec_marker") != null) return "already running"; // a retried eval must not record twice
new UnityEngine.GameObject("__rec_marker");
var job = System.IO.File.ReadAllLines("Temp/PlayRec/job.txt");
var dir = System.IO.Path.GetFullPath("Temp/PlayRec/" + job[0].Trim()) + "/";
System.IO.Directory.CreateDirectory(dir); foreach (var f in System.IO.Directory.GetFiles(dir)) System.IO.File.Delete(f);
string Arg(int i) => job.Length > i ? job[i].Trim() : "";

System.Collections.IEnumerator W(float s) { float t0 = UnityEngine.Time.unscaledTime; while (UnityEngine.Time.unscaledTime - t0 < s) yield return null; }
System.Collections.IEnumerator Rec(string part, int frames) {
  UnityEngine.Time.captureFramerate = 30;
  for (int i = 0; i < frames; i++) {
    yield return new UnityEngine.WaitForEndOfFrame();
    var t = UnityEngine.ScreenCapture.CaptureScreenshotAsTexture();
    var small = UnityEngine.RenderTexture.GetTemporary(960, 540, 0); UnityEngine.Graphics.Blit(t, small);
    var prev = UnityEngine.RenderTexture.active; UnityEngine.RenderTexture.active = small;
    var tex = new UnityEngine.Texture2D(960, 540, UnityEngine.TextureFormat.RGB24, false); tex.ReadPixels(new UnityEngine.Rect(0, 0, 960, 540), 0, 0); tex.Apply();
    UnityEngine.RenderTexture.active = prev; UnityEngine.RenderTexture.ReleaseTemporary(small);
    System.IO.File.WriteAllBytes(dir + $"{part}_{i:000}.jpg", tex.EncodeToJPG(90));
    UnityEngine.Object.Destroy(t); UnityEngine.Object.Destroy(tex);
  }
  UnityEngine.Time.captureFramerate = 0;
}

System.Collections.IEnumerator Run() {
  // TODO 1: set up the situation (load a level, spawn the character, start a battle with Arg(1)...).
  yield return W(2f);
  yield return Rec("idle", 120);            // 4 s of the resting state

  // TODO 2: trigger the action (attack, ability, UI transition) and wait until it starts.
  yield return Rec("attack", 105);          // 3.5 s from the moment it starts

  System.IO.File.WriteAllText(dir + "done.txt", "ok");
}
// Any MonoBehaviour that lives through the whole scenario can run the coroutine (a game manager, the EventSystem).
// Pick one that survives scene loads if TODO 1 loads a scene.
UnityEngine.MonoBehaviour host = UnityEngine.Object.FindFirstObjectByType<UnityEngine.EventSystems.EventSystem>();
if (host == null) host = UnityEngine.Object.FindFirstObjectByType<UnityEngine.MonoBehaviour>();
if (host == null) return "NO HOST to run the coroutine";
host.StartCoroutine(Run());
return "ok";
