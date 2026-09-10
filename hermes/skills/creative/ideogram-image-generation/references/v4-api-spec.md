# Ideogram V4 API Specification

**Endpoint:** `POST https://api.ideogram.ai/v1/ideogram-v4/generate`

**Authentication:** `Api-Key: <your_api_key>` header (NOT `Authorization: Bearer`)

**Content-Type:** `multipart/form-data` (NOT JSON)

## Form Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text_prompt` | string | Yes | The prompt describing the image to generate |
| `aspect_ratio` | string | No | Image dimensions: `ASPECT_1_1`, `ASPECT_16_9`, `ASPECT_9_16`, `ASPECT_4_3`, `ASPECT_3_2` |
| `model` | string | No | Model version: `V_4` (recommended), `V_2A`, `V_2`, `V_1` |
| `magic_prompt_option` | string | No | `AUTO` (default) or `OFF` - controls prompt enhancement |

## Response Format

```json
{
  "created": "2026-08-12T20:00:29.583738+00:00",
  "data": [
    {
      "is_image_safe": true,
      "prompt": "...expanded prompt...",
      "resolution": "1024x1024",
      "seed": ___ID___,
      "style_type": "GENERAL",
      "url": "https://ideogram.ai/api/images/ephemeral/..."
    }
  ]
}
```

## Key Differences from V2 API

| Aspect | V2 API | V4 API |
|--------|--------|--------|
| Endpoint | `/generate` | `/v1/ideogram-v4/generate` |
| Content-Type | `application/json` | `multipart/form-data` |
| Prompt field | `image_request.prompt` | `text_prompt` |
| JSON wrapper | `{"image_request": {...}}` | Flat form fields |
| Request method | `json=payload` | `files=fields` |

## Python Example

```python
import requests

IDEOGRAM_API_KEY = "your_key_here"

url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
headers = {"Api-Key": IDEOGRAM_API_KEY}

# Multipart form data (NOT JSON)
files = {
    "text_prompt": (None, "A professional LinkedIn graphic..."),
    "aspect_ratio": (None, "ASPECT_1_1"),
    "model": (None, "V_4"),
    "magic_prompt_option": (None, "OFF")
}

response = requests.post(url, headers=headers, files=files, timeout=120)
data = response.json()
image_url = data["data"][0]["url"]
```

## Common Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `415 Unsupported Media Type` | Sent JSON instead of multipart | Use `files=` not `json=` |
| `401 Unauthorized` | Used `Authorization: Bearer` | Use `Api-Key` header |
| `404 Not Found` | Wrong endpoint | Use `/v1/ideogram-v4/generate` |
| `V_3 not supported` | Tried V_3 model | V_3 uses different endpoint; use V_4 |

## Source

Based on user-provided documentation and testing session on 2026-08-12.
