// Unity (run with `unity command --project-path <root> eval_file --file <copy of this>`, or paste into an editor
// script). Slices an effect sheet into <name>_00 .. <name>_NN sprites, row by row from the top left, and sets
// high-quality block compression. Edit the values below.
if (UnityEditor.EditorApplication.isPlaying || UnityEditor.EditorApplication.isCompiling) return "BUSY";
string path = "Assets/Resources/Fx/Swing_Example.png";   // the PNG written by cut_fx.py
int count = 12, cols = 4, cellW = 480, cellH = 360;       // as printed by cut_fx.py

var name = System.IO.Path.GetFileNameWithoutExtension(path);
UnityEditor.AssetDatabase.ImportAsset(path, UnityEditor.ImportAssetOptions.ForceUpdate);
var ti = (UnityEditor.TextureImporter)UnityEditor.AssetImporter.GetAtPath(path);
ti.textureType = UnityEditor.TextureImporterType.Sprite; ti.spriteImportMode = UnityEditor.SpriteImportMode.Multiple;
ti.mipmapEnabled = false; ti.alphaIsTransparency = true;
ti.maxTextureSize = 2048; ti.textureCompression = UnityEditor.TextureImporterCompression.CompressedHQ;
ti.GetSourceTextureWidthAndHeight(out int tw, out int th); int rows = th / cellH;
var metas = new UnityEditor.SpriteMetaData[count];
for (int i = 0; i < count; i++) metas[i] = new UnityEditor.SpriteMetaData { name = name + "_" + i.ToString("00"), rect = new UnityEngine.Rect(i % cols * cellW, (rows - 1 - i / cols) * cellH, cellW, cellH), alignment = 0, pivot = new UnityEngine.Vector2(0.5f, 0.5f) };
#pragma warning disable 618
ti.spritesheet = metas; // the newer ISpriteEditorDataProvider API also works; this one is shorter
#pragma warning restore 618
ti.SaveAndReimport();
int n = 0; foreach (var o in UnityEditor.AssetDatabase.LoadAllAssetsAtPath(path)) if (o is UnityEngine.Sprite) n++;
var t = UnityEditor.AssetDatabase.LoadAssetAtPath<UnityEngine.Texture2D>(path);
return $"sprites {n} fmt {t.format} {t.width}x{t.height}";
