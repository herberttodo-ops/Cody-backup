# POYO Image Generation API Reference

Discovered during Sept 15, 2026 session with Andrew.

## Endpoint

**Submit:** `POST https://api.poyo.ai/api/generate/submit`  
**Status:** `GET https://api.poyo.ai/api/generate/status/{task_id}`  
**Auth:** `Authorization: Bearer {POYO_API_KEY}`

## Correct Payload (Working)

```json
{
  "model": "gpt-image-2.5-flare",
  "input": {
    "prompt": "your prompt here",
    "size": "9:16",
    "resolution": "2K",
    "quality": "high"
  }
}
```

## Parameters

| Field | Type | Required | Options |
|-------|------|----------|---------|
| `model` | string | Yes | `gpt-image-2.5-flare`, `gpt-image-2.5-sunburst` |
| `input.prompt` | string | Yes | Your image prompt |
| `input.size` | string | Yes | Aspect ratio: `"9:16"`, `"16:9"`, `"1:1"`, `"4:3"`, etc. |
| `input.resolution` | string | Yes | `"1K"`, `"2K"`, `"4K"` |
| `input.quality` | string | No | `"low"`, `"medium"`, `"high"` (default) |
| `input.image_urls` | array | No | For image-to-image editing |

## What NOT to do (Common Errors)

**❌ WRONG — Custom pixel size:**
```json
{"size": "1200x2160", "resolution": "2K"}
```
Error: `"Custom size requires resolution 2K or 4K"`

**❌ WRONG — Old model name:**
```json
{"model": "gpt-image-2"}
```

**❌ WRONG — Pixel values for size:**
```json
{"size": "1024x1536"}
```

**✅ CORRECT — Aspect ratio + resolution preset:**
```json
{"size": "9:16", "resolution": "2K", "model": "gpt-image-2.5-flare"}
```

## Alternative Cheaper Models (Sept 2026)

| Model | Gammell Quality | Price | Notes |
|-------|-----------------|-------|-------|
| `nano-banana-2-lite` | ⭐⭐⭐⭐ Strong crosshatching, ink bleeds, grotesque figures | Cheap / Fast | **Best Gammell match** |
| `flux-schnell` | ⭐⭐ Too clean, modern digital look | Cheapest / Fast | Use for non-Gammell or photorealistic |
| `gpt-image-2.5-flare` | ⭐⭐⭐ Good but overpriced for Gammell | Expensive / Slow | Works for all styles |

**Discover the catalog**: Install the official skill `PoyoAPI/poyo-devtools --skill poyo-ai-models` (via `npx skills add`) to browse available models, inspect schemas, and run via MCP or CLI with typed tools.

## Prompt Complexity
- **Complex long prompts fail more often** (task fails after "running" status)
- **Simpler prompts succeed more reliably**
- Keep prompts concise — 3-4 key descriptors work better than paragraphs
- Example that works: `"Ink wash illustration, Stephen Gammell style, deep shadows, monochrome"`
- Example that fails: Long multi-line prompt with 10+ descriptors

### Async Pattern
```python
async with aiohttp.ClientSession() as session:
    # 1. Submit
    async with session.post(url, headers=headers, json=payload) as resp:
        data = await resp.json()
        task_id = data["data"]["task_id"]
    
    # 2. Poll every 3 seconds
    for i in range(60):
        await asyncio.sleep(3)
        async with session.get(f"{url}/status/{task_id}", headers=headers) as s:
            status = await s.json()
            st = status["data"]["status"]
            if st == "finished":
                file_url = status["data"]["files"][0]["file_url"]
                # Download
            elif st in ("failed", "error"):
                # Handle failure
```

### Typical Timeline
- Submit: Instant
- `not_started`: 0-12 seconds
- `running`: 12-60 seconds
- `finished`: ~45-60 seconds for 2K images

## Gammell Style Prompt Template (Working)

```
Ink wash illustration, Stephen Gammell style, deep black shadows 
pooling like liquid ink, textured aged book paper, monochrome 
grayscale, high contrast chiaroscuro, Scary Stories to Tell in 
the Dark illustration style
```

Keep it concise for reliability.