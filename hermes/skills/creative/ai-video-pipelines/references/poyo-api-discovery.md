# Poyo API Discovery Notes

Session: 2026-09-13 (Tales Untold migration)

## Authentication Format

**Correct format:** `Authorization: Bearer sk-{key}`

```bash
# ❌ Wrong (401 Invalid API key)
Authorization: Bearer jLzbNumV7mm...

# ✅ Correct
Authorization: Bearer sk-jLzbNumV7mm...
```

Poyo keys include the `sk-` prefix in the actual key value, not just as a label.

## Base URL

```
https://api.poyo.ai
```

## Endpoints

| Operation | Method | Endpoint |
|-----------|--------|----------|
| Submit Task | POST | `/api/generate/submit` |
| Query Status | GET | `/api/generate/status/{task_id}` |

## Working Models (Account-Dependent)

**Verified working:**

| Model | Type | Notes |
|-------|------|-------|
| `gpt-4o-image` | Image generation | ~4 credits per image |
| `elevenlabs-v3-tts` | Voice synthesis | Uses `voice` field, not `voice_id` |
| `claude-sonnet-5` | Chat/LLM | **Preferred** - cost-efficient Sonnet |

**Deprecated/Costly:**
- `claude-fable-5-1` - Works but expensive/overkill

**NOT working (404 Model not found):**
- `gpt-4o-mini`, `gpt-4o`, `gpt-3.5-turbo` - OpenAI chat models
- `eleven_multilingual_v2` - Use `elevenlabs-v3-tts` instead

## Request/Response Format

### Submit Task (Image)

```python
payload = {
    "model": "gpt-4o-image",
    "input": {
        "prompt": "A red apple",
        "size": "1024x1536",  # 9:16 for shorts
        "quality": "high"
    }
}
```

### Submit Task (Voice) - Correct Format

```python
# ❌ WRONG - eleven_multilingual_v2 doesn't exist
payload = {
    "model": "eleven_multilingual_v2",
    "input": {"text": "Hello", "voice_id": "..."}  # Wrong field name
}

# ✅ CORRECT
payload = {
    "model": "elevenlabs-v3-tts",
    "input": {
        "text": "Hello this is a test",
        "voice": "pNInz6obpgDQGcFmaJgB"  # Note: "voice" not "voice_id"
    }
}
# No voice_settings supported - use default settings
```

### Submit Task (Chat)

```python
# ✅ RECOMMENDED - claude-sonnet-5 (cost-efficient)
payload = {
    "model": "claude-sonnet-5",
    "input": {
        "messages": [{"role": "user", "content": "Hello"}],
        "temperature": 0.9,
        "max_tokens": 2000
    }
}

# ⚠️ Works but costly - claude-fable-5-1
payload = {
    "model": "claude-fable-5-1",
    "input": {"messages": [...], "temperature": 0.9, "max_tokens": 2000}
}
```

### Response

```json
{
  "code": 200,
  "data": {
    "task_id": "UGWP56QNBFP5KLXU",
    "status": "not_started",
    "created_time": "2026-09-13T19:21:41"
  }
}
```

### Poll Status

```bash
curl "https://api.poyo.ai/api/generate/status/{task_id}" \
  -H "Authorization: Bearer $KEY"
```

Response:
```json
{
  "code": 200,
  "data": {
    "task_id": "...",
    "status": "running",  # or "finished", "failed"
    "progress": 100.0,
    "credits_amount": 0.928,
    "files": [
      {"file_url": "https://cdn.doculator.org/audios/.../....mp3", "file_type": "audio"}
    ]
  }
}
```

## Async Workflow Pattern

```python
async def generate_with_poyo(prompt):
    # 1. Submit
    task_id = await submit_task(payload)
    
    # 2. Poll until complete
    while True:
        status = await query_status(task_id)
        if status["data"]["status"] == "finished":
            break
        await asyncio.sleep(2)
    
    # 3. Download
    file_url = status["data"]["files"][0]["file_url"]
    await download(file_url, output_path)
    
    return output_path
```

## Pitfalls Discovered

1. **Key format matters**: Must include `sk-` prefix in the Authorization header value
2. **Voice API field names**: Use `"voice"` not `"voice_id"`. No `voice_settings` supported.
3. **Voice model name**: Use `elevenlabs-v3-tts` not `eleven_multilingual_v2`
4. **Model availability varies**: Test each model type before building
5. **Failed tasks**: Not charged (credits_amount: 0 on failed)
6. **Image server stability**: `gpt-4o-image` model exists but servers may return "Server exception" intermittently
7. **Chat model cost**: `claude-sonnet-5` is preferred over `claude-fable-5-1` for cost efficiency

## Recommended Hybrid Approach

Use Poyo for everything it's good at, fall back to direct APIs where needed:

| Component | Primary | Fallback |
|-----------|---------|----------|
| Stories | Poyo `claude-sonnet-5` | OpenAI `gpt-4o-mini` |
| Voice | Poyo `elevenlabs-v3-tts` | Direct ElevenLabs |
| Images | Poyo `gpt-4o-image` | OpenAI DALL-E 3 |

This gives you one Poyo key for all AI generation, with fallbacks if Poyo has issues.

## Update Log

- **2026-09-13**: Initial discovery, key format `sk-` prefix, working models identified
- **2026-09-13**: Updated chat model to `claude-sonnet-5` (cost preference)
