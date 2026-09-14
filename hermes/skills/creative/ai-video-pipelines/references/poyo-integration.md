# Poyo.ai Integration Reference

## Overview

Poyo.ai provides a unified API for multiple AI services (OpenAI, ElevenLabs, image generation) with async task processing.

## Base URL

```
https://api.poyo.ai
```

## Authentication

**Header format:**
```
Authorization: Bearer <api_key>
```

**Common issue:** If you get "Invalid API key" (401), check:
1. Key is active in Poyo dashboard
2. Account has available credits
3. Key is copied correctly (no trailing spaces)

## Endpoints

### Submit Task
```
POST /api/generate/submit
```

Request body:
```json
{
  "model": "gpt-4o-mini",
  "input": {
    "messages": [{"role": "user", "content": "..."}]
  }
}
```

Response:
```json
{
  "code": 200,
  "data": {
    "task_id": "task-...",
    "status": "not_started"
  }
}
```

### Query Status
```
GET /api/generate/status/{task_id}
```

Response:
```json
{
  "code": 200,
  "data": {
    "task_id": "...",
    "status": "finished",
    "progress": 100,
    "files": [
      {"file_url": "https://...", "file_type": "image"}
    ]
  }
}
```

## Models Available

| Task | Model | Notes |
|------|-------|-------|
| Chat | `gpt-4o-mini`, `gpt-4o`, `claude-*` | Standard chat completion |
| Voice | `eleven_multilingual_v2` | ElevenLabs backend |
| Images | `gpt-image-2`, `flux-*` | Various image models |

## Async Pattern

```python
async def generate_with_poyo():
    # 1. Submit
    task_id = await client.submit_task(payload)
    
    # 2. Poll
    while True:
        status = await client.query_status(task_id)
        if status["data"]["status"] == "finished":
            break
        await asyncio.sleep(2)
    
    # 3. Download
    file_url = status["data"]["files"][0]["file_url"]
    await client.download(file_url, output_path)
```

## Troubleshooting

### 401 Unauthorized
- Verify key in Poyo dashboard
- Check credits balance
- Try regenerating key

### Task Times Out
- Increase poll timeout (some tasks take 60-300s)
- Check task status manually: `curl https://api.poyo.ai/api/generate/status/{task_id}`

### Download Fails
- File URLs expire after some time
- Download immediately when status shows "finished"
