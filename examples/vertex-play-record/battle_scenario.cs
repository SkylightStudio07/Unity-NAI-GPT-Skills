// Project-Vertex scenario for unity-play-record (deck-building battle). job.txt: tag, encounter asset path, battle type.
// record.sh ... --scenario battle_scenario.cs --arg "Assets/Data/.../Encounter_Weak_Bandit.asset" --arg Normal
// Starts that battle, records 120 idle frames, ends turns (with 300 block) until an enemy attacks, records 105 frames,
// writes Temp/PlayRec/<tag>/done.txt. 960x540 JPG at a fixed 30 fps (Time.captureFramerate).
if (!UnityEngine.Application.isPlaying) return "NOT PLAYING";
if (UnityEngine.GameObject.Find("__rec_marker") != null) return "already running"; // a retried eval must not record twice
new UnityEngine.GameObject("__rec_marker");
var job = System.IO.File.ReadAllLines("Temp/PlayRec/job.txt");
var enc = UnityEditor.AssetDatabase.LoadAssetAtPath<EnemyEncounter>(job[1].Trim());
if (enc == null) return "NO ENCOUNTER " + job[1];
var type = (BattleType)System.Enum.Parse(typeof(BattleType), job[2].Trim());
var dir = System.IO.Path.GetFullPath("Temp/PlayRec/" + job[0].Trim()) + "/";
System.IO.Directory.CreateDirectory(dir); foreach (var f in System.IO.Directory.GetFiles(dir)) System.IO.File.Delete(f);
var gm = GameManager.Instance; var bm = BattleManager.Instance;
bool attackStarted = false;
System.Action<EnemyInstance, EnemyAction, float> h = (e, a, t) => { System.IO.File.AppendAllText(dir + "actions.txt", a.DisplayName + " " + a.intentType + System.Environment.NewLine); if (a.intentType == IntentType.Attack) attackStarted = true; };
System.Collections.IEnumerator W(float s) { float t0 = UnityEngine.Time.unscaledTime; while (UnityEngine.Time.unscaledTime - t0 < s) yield return null; }
System.Collections.IEnumerator Rec(string tag, int frames) {
  UnityEngine.Time.captureFramerate = 30;
  for (int i = 0; i < frames; i++) {
    yield return new UnityEngine.WaitForEndOfFrame();
    var t = UnityEngine.ScreenCapture.CaptureScreenshotAsTexture();
    var small = UnityEngine.RenderTexture.GetTemporary(960, 540, 0); UnityEngine.Graphics.Blit(t, small);
    var prev = UnityEngine.RenderTexture.active; UnityEngine.RenderTexture.active = small;
    var tex = new UnityEngine.Texture2D(960, 540, UnityEngine.TextureFormat.RGB24, false); tex.ReadPixels(new UnityEngine.Rect(0, 0, 960, 540), 0, 0); tex.Apply();
    UnityEngine.RenderTexture.active = prev; UnityEngine.RenderTexture.ReleaseTemporary(small);
    System.IO.File.WriteAllBytes(dir + $"{tag}_{i:000}.jpg", tex.EncodeToJPG(90));
    UnityEngine.Object.Destroy(t); UnityEngine.Object.Destroy(tex);
  }
  UnityEngine.Time.captureFramerate = 0;
}
System.Collections.IEnumerator R() {
  gm.StartEncounterBattle(enc, type);
  foreach (var b in UnityEngine.Object.FindObjectsByType<BlessingView>(UnityEngine.FindObjectsInactive.Include, UnityEngine.FindObjectsSortMode.None)) b.gameObject.SetActive(false);
  yield return W(3.5f);
  yield return Rec("idle", 120);
  bm.OnEnemyActionStarting += h;
  for (int turn = 0; turn < 4 && !attackStarted; turn++) {
    bm.State.Player.AddBlock(300); bm.PlayerTurnEnd();
    float t0 = UnityEngine.Time.unscaledTime;
    while (bm.State.Phase == BattlePhase.PlayerTurn && UnityEngine.Time.unscaledTime - t0 < 5f && !attackStarted) yield return null;
    while (bm.State.Phase != BattlePhase.PlayerTurn && !attackStarted && UnityEngine.Time.unscaledTime - t0 < 20f) yield return null;
    if (!attackStarted) yield return W(1f);
  }
  if (attackStarted) yield return Rec("attack", 105);
  bm.OnEnemyActionStarting -= h;
  var bg = UnityEngine.Object.FindFirstObjectByType<BattleStageView>();
  System.IO.File.WriteAllText(dir + "done.txt", (attackStarted ? "ok" : "no attack") + " attack=" + attackStarted + " stage=" + (bg != null && bg.Current != null ? bg.Current.name : "none"));
}
gm.StartCoroutine(R());
return "ok";
