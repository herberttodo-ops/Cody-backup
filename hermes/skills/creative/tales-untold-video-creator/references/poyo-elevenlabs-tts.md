## WORKING POYO ElevenLabs TTS Configuration

Endpoint: `POST https://api.poyo.ai/api/generate/submit`

### Correct Request Body
```json
{
  "model": "elevenlabs-v3-tts",
  "input": {
    "text": "Your narration script here",
    "voice": "Adam"
  }
}
```

### CRITICAL: Do NOT Use These Fields
| Field | Status | Why |
|-------|--------|-----|
| `voice_id` | ❌ Rejected | Returns `unsupported fields: voice_id` |
| `model_id` | ❌ Rejected | Returns `unsupported fields: model_id` |
| `prompt` | ❌ Rejected | Returns `unsupported fields: prompt` |

### Response Format
```json
{
  "code": 200,
  "data": {
    "task_id": "UIACVS8JKS6OSLRT",
    "status": "not_started",
    "created_time": "..."
  }
}
```

**Note:** Response is nested under `data` key. Do NOT look for top-level `task_id`.

### Polling
```
GET https://api.poyo.ai/api/generate/status/{task_id}
Headers: Authorization: Bearer {key}
```

Poll every 3-5 seconds. Status values: `not_started` → `running` → `finished`/`failed`

### Download Result
When `status == "finished"`:
```json
{
  "code": 200,
  "data": {
    "status": "finished",
    "progress": 100,
    "files": [{"file_url": "https://cdn.doculator.org/audios/...", "file_type": "audio/mp3"}]
  }
}
```

Download from `data.files[0].file_url`
