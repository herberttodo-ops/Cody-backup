# Fal.ai Integration Reference

Session: 2026-09-13 (Tales Untold extended workflow)

## Overview

Fal.ai provides fast, reliable image generation via Flux models. Use as **fallback** when Poyo image generation fails or for higher reliability.

**When to use Fal over Poyo for images:**
- Poyo `gpt-4o-image` returns "Server exception" errors
- Need faster generation (~2-5s vs ~30-60s)
- Want higher quality (Flux Ultra > GPT-4o-image for many use cases)

## Authentication

```python
api_key = "eda2be69-1afe-42bc-8d7f-ab19c41d84c7:b9b51ea16760c61e19ec928d844f3d57"
# Format: Key {api_key}
```

## Base URL

```
https://fal.run
```

## Models

| Model | Speed | Quality | Best For |
|-------|-------|---------|----------|
| `fal-ai/flux-pro/v1.1-ultra` | Medium | Highest | Final production images |
| `fal-ai/flux/schnell` | Fast | Good | Drafts, rapid iteration |
| `fal-ai/flux/dev` | Medium | Very Good | Balanced quality/speed |

## Request Format

```python
url = "https://fal.run/fal-ai/flux-pro/v1.1-ultra"

payload = {
    "prompt": "A phone screen showing audio waveform...",
    "width": 1080,
    "height": 1920
    # Note: Fal accepts any dimensions divisible by 16
}

headers = {
    "Authorization": f"Key {api_key}",
    "Content-Type": "application/json"
}

# Fal is SYNCHRONOUS - returns result immediately
async with session.post(url, json=payload, headers=headers) as resp:
    data = await resp.json()
    image_url = data["images"][0]["url"]
```

## Response Format

```json
{
  "images": [
    {
      "url": "https://v3b.fal.media/files/.../....jpg",
      "width": 1536,
      "height": 2752,
      "content_type": "image/jpeg"
    }
  ],
  "timings": {
    "inference": 2.___ID___
  },
  "seed": ___ID___,
  "has_nsfw_concepts": [false]
}
```

## Synchronous vs Async

**Key difference from Poyo:**
- **Poyo**: Async (submit → poll → download)
- **Fal**: Synchronous (single request returns result)

No polling needed - Fal handles queueing internally and returns when complete.

## Dimension Constraints

Fal is flexible with dimensions:
- Width and height must be **divisible by 16**
- Max edge: **3840 pixels**
- Aspect ratio: up to **3:1**
- Total pixels: between **655,360 and 8,294,400**

**Common sizes:**
- Shorts (9:16): 1080×1920 ✅
- Square: 1024×1024 ✅
- Wide: 1920×1080 ✅

## Cost

Approximately **$0.03-0.05 per image** depending on model.

## Python Client

```python
import aiohttp

class FalClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://fal.run"
    
    async def generate_image(
        self,
        prompt: str,
        model: str = "fal-ai/flux-pro/v1.1-ultra",
        width: int = 1080,
        height: int = 1920
    ) -> str:
        """Generate image, return URL."""
        url = f"{self.base_url}/{model}"
        payload = {"prompt": prompt, "width": width, "height": height}
        headers = {"Authorization": f"Key {self.api_key}"}
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload, headers=headers) as resp:
                resp.raise_for_status()
                data = await resp.json()
                return data["images"][0]["url"]
```

## Hybrid Provider Strategy

**Recommended workflow:**

```
Story (You/Hermes) → Voice (Poyo elevenlabs-v3-tts) → Images (Fal Flux Ultra) → Video (MoviePy)
```

| Component | Provider | Why |
|-----------|----------|-----|
| **Stories** | Hermes direct | Zero cost, quality control |
| **Voice** | Poyo | Reliable ElevenLabs integration |
| **Images** | **Fal.ai** | Faster, more reliable than Poyo for images |
| **Video** | MoviePy | Local assembly, no API needed |

## Pitfalls

- **Not async**: Don't implement polling - Fal is synchronous
- **Dimensions**: Must be divisible by 16, check constraints
- **Cost tracking**: No built-in cost reporting, track manually
- **No voice/chat**: Fal is image-only; use Poyo for other modalities

## When Fal vs Poyo

| Situation | Use |
|-----------|-----|
| Quick drafts, high volume | Fal `flux/schnell` |
| Production quality | Fal `flux-pro/v1.1-ultra` |
| Single API key for everything | Poyo (voice + image + chat) |
| Poyo images failing | Fal (reliable fallback) |

## Update Log

- **2026-09-13**: Initial Fal.ai integration, Flux Ultra model validated
