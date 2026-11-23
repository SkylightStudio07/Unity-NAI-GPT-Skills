// (unity eval_file, editor not playing) Encodes Temp/PlayRec/_frames/f_*.jpg (1920x540) into the mp4 named in
// Temp/PlayRec/encode.txt, 30 fps. Writes Temp/PlayRec/encode_done.txt. Long runs time out the CLI call; wait for the file.
var outPath = System.IO.Path.GetFullPath(System.IO.File.ReadAllText("Temp/PlayRec/encode.txt").Trim());
var files = System.IO.Directory.GetFiles("Temp/PlayRec/_frames", "f_*.jpg"); System.Array.Sort(files, System.StringComparer.Ordinal);
if (files.Length == 0) return "NO FRAMES";
var va = new UnityEditor.Media.VideoTrackAttributes { frameRate = new UnityEditor.Media.MediaRational(30), width = 1920, height = 540, includeAlpha = false, bitRateMode = UnityEditor.VideoBitrateMode.High };
var tex = new UnityEngine.Texture2D(1920, 540, UnityEngine.TextureFormat.RGBA32, false);
var tmp = new UnityEngine.Texture2D(2, 2);
using (var enc = new UnityEditor.Media.MediaEncoder(outPath, va)) {
  foreach (var f in files) { tmp.LoadImage(System.IO.File.ReadAllBytes(f)); tex.SetPixels32(tmp.GetPixels32()); tex.Apply(); enc.AddFrame(tex); }
}
UnityEngine.Object.DestroyImmediate(tex); UnityEngine.Object.DestroyImmediate(tmp);
System.IO.File.WriteAllText("Temp/PlayRec/encode_done.txt", files.Length + " " + outPath);
return "encoded " + files.Length;
