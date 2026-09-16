# POYO nano-banana-2-lite API Reference

## Model Details
- **Model ID:** `nano-banana-2-lite`
- **Price:** Cheapest option on POYO for image generation
- **Speed:** Fast (~15-30s generation)
- **Quality:** Good for Gammell/ink-wash style generation
- **9:16 support:** Yes via `size` param

## API Endpoint
```
POST https://api.poyo.ai/api/generate/submit
Authorization: Bearer <POYO_API_KEY>
Content-Type: application/json
```

## Request Body
```json
{
  "model": "nano-banana-2-lite",
  "input": {
    "prompt": "ink wash illustration in Stephen Gammell style...",
    "size": "9:16"
  }
}
```

## Key Parameters
| Param | Type | Required | Values |
|-------|------|----------|--------|
| `model` | string | Yes | `"nano-banana-2-lite"` |
| `input.prompt` | string | Yes | The image description |
| `input.size` | string | Yes | `"9:16"` (aspect ratio) |

**Notes:**
- `size`: Uses aspect ratios, not pixel values
- No `resolution` parameter needed (unlike gpt-image-2.5-flare)
- No `quality` parameter
- Prompts should mention: "ink wash illustration," "Stephen Gammell style," "textured aged book paper"

## Response
```json
{
  "code": 200,
  "data": {
    "task_id": "TASK_ID_HERE",
    "status": "not_started"
  }
}
```

## Polling for Result
```
GET https://api.poyo.ai/api/generate/status/{task_id}
Authorization: Bearer <POYO_API_KEY>
```

Poll every 2-3 seconds until:
- `status === "finished"` → download `files[0].file_url`
- `status === "failed"` → retry with simpler prompt

## Image Prompt Template (Gammell Style)
```
{A scene description}, ink wash illustration in Stephen Gammell style,
deep black shadows pooling like liquid ink, textured aged book paper,
crosshatched shadows, monochrome grayscale, high contrast chiaroscuro,
Scary Stories to Tell in the Dark illustration style
```

## Working Python Script
```python
import asyncio
import aiohttp
import requests
import os

POYO_KEY = os.environ.get("POYO_API_KEY")

async def generate_image(prompt, output_path):
    payload = {
        "model": "nano-banana-2-lite",
        "input": {
            "prompt": prompt,
            "size": "9:16"
        }
    }
    headers = {
        "Authorization": f"Bearer {POYO_KEY}",
        "Content-Type": "application/json"
    }
    
    async with aiohttp.ClientSession() as session:
        # Submit
        async with session.post(
            "https://api.poyo.ai/api/generate/submit",
            headers=headers,
            json=payload
        ) as resp:
            data = await resp.json()
            task_id = data["data"]["task_id"]
        
        # Poll
        for i in range(40):
            await asyncio.sleep(3)
            async with session.get(
                f"https://api.poyo.ai/api/generate/status/{task_id}",
                headers=headers
            ) as s:
                status = await s.json()
                st = status["data"]["status"]
                
                if st == "finished":
                    url = status["data"]["files"][0]["file_url"]
                    r = requests.get(url, timeout=30)
                    with open(output_path, "wb") as f:
                        f.write(r.content)
                    return True
                elif st in ("failed", "error"):
                    return False
    return False
```

## Troubleshooting
| Issue | Solution |
|-------|----------|
| Task fails with complex prompt | Simplify prompt, fewer adjectives |
| 400 error on size | Use `"9:16"` not pixel values like `"1080x1920"` |
| Slow generation | Normal; wait 15-30 seconds |
| Low quality | Switch to `nano-banana-2-official` or `gpt-image-2.5-flare` |
