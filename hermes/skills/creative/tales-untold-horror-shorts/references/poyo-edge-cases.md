# POYO API Edge Cases

## ElevenLabs TTS Model Change (2026-09-15)

POYO removed `elevenlabs` and `elevenlabs-tts` models. The new working model is **`elevenlabs-tts-turbo-2-5`**.

### Working Request
```json
POST https://api.poyo.ai/api/generate/submit
{
  "model": "elevenlabs-tts-turbo-2-5",
  "input": {
    "voice": "Adam",
    "text": "Your story here...",
    "speed": 1.0
  }
}
```

### Response Format
```json
{"code": 200, "data": {"task_id": "...", "status": "not_started"}}
```
Extract `task_id` from `data.task_id`, not top-level.

## Response Format Change (Image/Video Also)

All POYO responses now nest under `"data"`:

```python
result = r.json()
# WRONG (old format)
# task_id = result["task_id"]

# CORRECT
if "data" in result and "task_id" in result["data"]:
    task_id = result["data"]["task_id"]
```

## Shell Key Mangling

Passing `POYO_API_KEY` via shell commands causes truncation. Always read via Python `os.environ` or `.env` file directly.

```python
# WRONG - shell mangles the key
# API_KEY = subprocess.run("echo $POYO_API_KEY", ...)

# CORRECT
import os
API_KEY = os.environ.get("POYO_API_KEY", "")
```

## Download Immediately

Image and audio URLs expire. Download within minutes of `status: "finished"`.

```python
url = status["data"]["files"][0]["file_url"]
img = requests.get(url, timeout=60)
```

## Image Size

nano-banana-2-lite returns JPEG at 768×1376 regardless of requesting `"9:16"`. Image source dimension is fine; CSS `object-fit: cover` handles it.
