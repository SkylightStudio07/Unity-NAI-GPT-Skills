# Playing an effect sheet in game

What worked in Project-Vertex (Unity uGUI, enemies as `Image` with `preserveAspect`).

## Timing

- Start the effect on the character frame it was guided from (`make_guide.py`'s first frame), at the character sheet's frame rate.
- The first few frames (the swing, up to the impact) play **1:1** with the character. The rest (debris, smoke, fading trail) play at **half speed**. 12 frames with 5 synced last about 0.63 s at 30 fps. Without the slow tail the effect "appears and vanishes in one beat".
- Put the hit (damage number, screen shake, the target's hit flash) on the impact frame.

## Placement

- Use the effect rectangle `make_guide.py` prints, in units of the **drawn** character, not the UI box around it. With `preserveAspect` the sprite is fitted inside its `RectTransform`; using the whole box puts the effect too far out. This was the cause of "the trail is not on the weapon tip".
- Re-measure every frame so the effect follows recoil or knock-back.
- Additive material. Multiply a colour (`Image.color`) per character: the art is drawn white so one sheet can be bat-white, crystal-magenta or blood-red.
- A shared hit effect on the target (bullets): centre it on the hit point, move it a few pixels each time and flip it vertically at random so repeats are not obvious.

## uGUI sample

```csharp
// frames: the sliced sprites sorted by name. area: effect rect in character-cell units, e.g. (-1/3, 0, 4/3, 1).
IEnumerator PlaySheet(Image target, Sprite[] frames, Rect area, float fps, int synced, Color tint, Material additive)
{
    var go = new GameObject("FxSheet", typeof(RectTransform), typeof(Image));
    var img = go.GetComponent<Image>();
    img.material = additive; img.color = tint; img.raycastTarget = false;
    var rt = (RectTransform)go.transform;
    rt.SetParent(target.canvas.transform, false);
    float ticks = synced + (frames.Length - synced) * 2f, t = 0f;
    while (t < ticks)
    {
        // the drawn area of a preserveAspect Image
        Rect r = target.rectTransform.rect; Vector2 size = r.size;
        if (target.preserveAspect && target.sprite != null)
        {
            Rect sr = target.sprite.rect;
            size = sr.size * Mathf.Min(r.width / sr.width, r.height / sr.height);
        }
        Vector3 Point(Vector2 n) => target.rectTransform.TransformPoint(r.center + Vector2.Scale(n - new Vector2(0.5f, 0.5f), size));
        Vector3 a = Point(area.min), b = Point(area.max);
        rt.position = (a + b) * 0.5f;
        Vector3 la = rt.parent.InverseTransformPoint(a), lb = rt.parent.InverseTransformPoint(b);
        rt.sizeDelta = new Vector2(Mathf.Abs(lb.x - la.x), Mathf.Abs(lb.y - la.y));

        int frame = t < synced ? (int)t : synced + (int)((t - synced) * 0.5f);
        img.sprite = frames[Mathf.Min(frames.Length - 1, frame)];
        t += Time.deltaTime * fps;
        yield return null;
    }
    Object.Destroy(go);
}
```
