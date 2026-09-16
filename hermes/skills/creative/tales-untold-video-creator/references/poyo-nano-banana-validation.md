# POYO nano-banana-2-lite — Validated API & Gammell Generation

## User-Corrected Findings

### Image Generation: NATIVE Gammell ONLY
User explicitly rejected post-processing: **"Post processing does not work."**  
CSS `filter: grayscale()`, `contrast()`, `saturate()` on color photos produces filtered photos, not authentic ink wash. **Generate images natively in Gammell style** using prompt engineering at the source.

### Model Selection
After testing 3 POYO models:

| Model | Gammell Match | Result |
|-------|--------------|--------|
| `nano-banana-2-lite` | ⭐⭐⭐⭐ Crosshatched shadows, ink bleeds, grotesque figures, textured paper | **SELECTED** |
| `flux-schnell` | ⭐⭐ Too clean, modern, polished digital look | Rejected |
| `gpt-image-2.5-flare` | N/A "Custom size requires resolution 2K or 4K" errors | Failed |

### Correct POYO API Format (nano-banana-2-lite)

```bash
POST https://api.poyo.ai/api/generate/submit
Authorization: Bearer $POYO_API_KEY
Content-Type: application/json
```

```json
{
  "model": "nano-banana-2-lite",
  "input": {
    "prompt": "A pale figure sitting up in bed in darkness, Stephen Gammell ink wash illustration, deep black shadows pooling like liquid ink, textured aged book paper, grotesque surreal horror, monochrome",
    "size": "9:16"
  }
}
```

**Key points:**
- `size: "9:16"` — aspect ratio string, NOT pixel dimensions
- No `resolution` or `quality` param (unlike gpt-image-2.5)
- Concise prompts work better than long multi-line prompts

### Async Pattern

```python
import asyncio, aiohttp, requests

async def generate(prompt: str, output_path: str):
    headers = {"Authorization": "Bearer " + POYO_KEY}
    payload = {
        "model": "nano-banana-2-lite",
        "input": {"prompt": prompt, "size": "9:16"}
    }
    
    async with aiohttp.ClientSession() as session:
        # Submit
        r = await session.post("https://api.poyo.ai/api/generate/submit", headers=headers, json=payload)
        task_id = (await r.json())["data"]["task_id"]
        
        # Poll
        for i in range(60):
            await asyncio.sleep(3)
            r = await session.get(f"https://api.poyo.ai/api/generate/status/{task_id}", headers=headers)
            status = (await r.json())["data"]["status"]
            if status == "finished": break
            if status in ("failed", "error"): raise RuntimeError("Generation failed")
        
        # Download immediately (URLs expire)
        r = await session.get(file_url)
        with open(output_path, "wb") as f:
            f.write(await r.read())
```

### Gammell Prompt Template

```
{scene_description}, ink wash illustration in the style of Stephen Gammell,
deep black shadows pooling like liquid ink, textured aged book paper,
surreal horror aesthetic, crosshatched shadows, monochrome grayscale,
high contrast chiaroscuro, Scary Stories to Tell in the Dark illustration style
```

### Common Pitfalls

| Issue | Cause | Fix |
|-------|-------|-----|
| "Custom size requires 2K or 4K" | Using gpt-image-2 models | Switch to nano-banana-2-lite |
| Task fails silently | Prompt too long/complex | Keep concise (3-4 phrases) |
| 404 on download | URL expired | Download immediately after "finished" |
| Images look like filtered photos | Post-processing color images | Generate natively in Gammell style |

## User Rules Applied

- **NO grain** — user removed grain entirely after testing
- **NO title card** — user: "go directly into the first frame"
- **Captions MUST match Whisper timestamps exactly** — guessing causes degradation
- **Visual duration MUST match narration + CTA** — measure audio first, never assume fixed duration
