# POYO API Response Format

POYO API returns responses wrapped in a `data` envelope, unlike standard REST APIs.

## Standard Response Structure

```json
{
  "code": 200,
  "data": {
    "task_id": "ABC123",
    "status": "finished|not_started|running|error",
    "result": {
      "files": [{"file_url": "..."}]
    }
  }
}
```

## Common Access Pattern (with fallback)

```python
def get_poyo_value(response, key, default=None):
    """Safely extract values from POYO response with fallback."""
    data = response.get("data") or response
    return data.get(key, default)

# Usage
task_id = get_poyo_value(json_response, "task_id")
status = get_poyo_value(json_response, "status")
```

## Why This Matters

POYO uses this wrapper for all generate endpoints:
- Image generation (nano-banana-2-lite)
- TTS (elevenlabs-tts-turbo-2-5)
- Text generation
- Video generation

Direct access like `response["task_id"]` fails silently; always use `.get("data", {}).get("...")` pattern.

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `https://api.poyo.ai/api/generate/submit` | POST | Submit generation job |
| `https://api.poyo.ai/api/generate/status/{task_id}` | GET | Poll for completion |

## Authentication

```python
headers = {
    "Authorization": f"Bearer {POYO_API_KEY}",
    "Content-Type": "application/json"
}
```
