# NovelAI image API: what was verified (2026-11)

- `POST https://image.novelai.net/ai/generate-image` with `Authorization: Bearer <persistent API token>` and `Content-Type: application/json`.
- **User-Agent:** Python urllib's default UA gets Cloudflare 403 / error 1010. Send an honest custom one (`nai-asset-tool/1.0`). Do not fake a browser Origin, Referer or UA.
- **Response:** a zip that holds `image_0.png`.
- **Concurrency:** one generation at a time per account. 429 means busy, so back off and retry.
- **Model:** `nai-diffusion-5-full`. V4.5 is `nai-diffusion-4-5-full`.

## Body (what `nai_gen.py` sends)

```json
{
  "input": "<prompt>",
  "model": "nai-diffusion-5-full",
  "action": "generate",
  "parameters": {
    "params_version": 3, "width": 1024, "height": 1024,
    "scale": 5.0, "sampler": "k_euler_ancestral", "steps": 23, "n_samples": 1,
    "seed": 123, "noise_schedule": "karras",
    "negative_prompt": "<negative>",
    "v4_prompt": {"caption": {"base_caption": "<prompt>", "char_captions": [
        {"char_caption": "<one character>", "centers": [{"x": 0.3, "y": 0.5}]}]},
      "use_coords": false, "use_order": true},
    "v4_negative_prompt": {"caption": {"base_caption": "<negative>", "char_captions": [
        {"char_caption": "<that character's negative>", "centers": [{"x": 0.3, "y": 0.5}]}]},
      "legacy_uc": false},
    "characterPrompts": [{"prompt": "...", "uc": "...", "center": {"x": 0.3, "y": 0.5}, "enabled": true}],
    "straight_alpha": true,
    "tag_hint_transparent_background": true
  }
}
```

- `use_coords` should be true only when the character centres actually matter.
- The last two flags, `straight_alpha` and `tag_hint_transparent_background`, are for transparent output only, together with `transparent background` in the prompt.

## Errors

| Code | Meaning |
|---|---|
| 401 | token wrong or expired |
| 402 | needs Opus, or the size/steps cost Anlas the account doesn't have |
| 403 / 1010 | Cloudflare didn't accept the User-Agent |
| 429 | another generation is still running; retry |

## Background removal: use native transparent generation

This workflow gets assets without a background (sprites, props, parallax layers) by having V5 generate the alpha channel directly:
- `transparent background` in the prompt plus `straight_alpha` and `tag_hint_transparent_background` in the parameters.
- `nai_gen.py` then cleans the result into `_clean.png`.

This method is free within the Opus limits, and all the environment assets of the original project were made this way.

The separate post-hoc remover, Director Tools `bg-removal` (`/ai/augment-image`), takes a finished image and cuts its background out. It costs Anlas and was never needed. Use it only for an image that already exists and can't be regenerated, and check its request shape against the NovelAI docs first.

## Not used here (exists in the API)

img2img, inpaint, upscale, the other Director Tools and vibe transfer (`/ai/encode-vibe`) are also unused. They were not verified in this workflow.
