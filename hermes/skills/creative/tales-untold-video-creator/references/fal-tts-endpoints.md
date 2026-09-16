# Fal.ai TTS Endpoints for Tales Untold

## Discovery (Sept 15, 2026)

The generic `/tts` endpoint does NOT exist on Fal.ai. Model-specific endpoints must be used.

### Available Endpoints (vetted)

| Endpoint | Status | Notes |
|----------|--------|-------|
| `https://fal.run/fal-ai/elevenlabs/tts` | ❌ 404 | Path not found |
| `https://fal.run/fal-ai/tts` | ❌ 404 | Path not found |
| `https://fal.run/fal-ai/kokoro` | ⚠️ Unknown | Not tested |
| `https://fal.run/fal-ai/playai` | ⚠️ Unknown | Not tested |
| `https://fal.run/fal-ai/f5-tts` | ⚠️ Unknown | Not tested |

### Working Alternative: Direct ElevenLabs API
```python
from elevenlabs.client import ElevenLabs
client = ElevenLabs(api_key="YOUR_KEY")

# Adam voice ID for horror
VOICE_ID = "pNInz6obpgDQGcFmaJgB"

audio = client.text_to_speech.convert(
    voice_id=VOICE_ID,
    text=script_text,
    model_id="eleven_monolingual_v1"
)
```

### Fallback Chain (always ordered)
1. **ElevenLabs direct** — Primary, Adam voice
2. **Edge TTS** — `edge-tts --voice en-US-BrianNeural` (free, local)
3. **Fal.ai** — If viable model found later

### Key Validation
Always test the key BEFORE the pipeline:
```python
import requests
resp = requests.get("https://api.elevenlabs.io/v1/voices",
    headers={"xi-api-key": key}, timeout=10)
assert resp.status_code == 200, f"Invalid key: {resp.text}"
```

### POYO.ai Note
User reported POYO.ai has ElevenLabs access. If ElevenLabs key fails, query POYO.ai API for voice generation. Credentials stored in env: `POYO_API_KEY`.
