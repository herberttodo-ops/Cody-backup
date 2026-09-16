# POYO.ai TTS Discovery & Audio Lessons

## POYO.ai DOES Support ElevenLabs TTS

**Discovered [2026-09-15]**: POYO.ai **does** support ElevenLabs TTS via the async task API (`POST /api/generate/submit`). The model name is **`elevenlabs-v3-tts`**.

### Working TTS Configuration
```json
{
  "model": "elevenlabs-v3-tts",
  "input": {
    "text": "your narration text here",
    "voice": "Adam"
  }
}
```

### Key Rules
- **Field name is `voice`** (NOT `voice_id` or `model_id`)
- **Value is the display name** like `"Adam"` (NOT an API ID like `pNInz6obpgDQGcFmaJgB`)
- **Never include `voice_id` or `model_id`** in the POYO payload — they are rejected
- Poll `GET /api/generate/status/{task_id}` until status is `"finished"`

### Failed Model Names (History — pre-2026-09-15)
These were tested before discovering the correct model name:
| Model | Result |
|-------|--------|
| `elevenlabs` | 404 — resource_not_found_error |
| `tts-1` | 404 — resource_not_found_error |
| `eleven-tts` | 404 — resource_not_found_error |
| `eleven_multilingual_v2` | 404 — resource_not_found_error |
| `eleven_turbo_v2_5` | 404 — resource_not_found_error |
| `eleven_mono_v1` | 404 — resource_not_found_error |

### Direct ElevenLabs Also Fails Here
- Key in `.env` (`sk_ac2e...`) returns `invalid_api_key` via both REST API and Python SDK v2.68.0
- Adam voice ID `pNInz6obpgDQGcFmaJgB` is correct, but unreachable directly — use POYO instead

## Audio Lessons

### Crossfade Gap Fix (MoviePy v2)
```python
# WRONG (MoviePy v2):
from moviepy import afx
clip.with_effects([afx.CrossFadeOut(0.15)])

# CORRECT (MoviePy v2):
from moviepy import vfx
clip.with_effects([vfx.CrossFadeOut(0.15)])
```
- `vfx` = video effects module
- `afx` = audio effects (separate module, different functions)

### Music Volume Verification
**Always verify after mixing:**
```bash
ffmpeg -i video.mp4 -vn -af "volumedetect" -f null - 2>&1 | grep mean_volume
```

| Build | Music mean_volume | Verdict |
|-------|-------------------|---------|
| v2/v3 | **-24.7 dB** | Too quiet |
| v3b | **TBD** | Target -15 to -20 dB |

**Fix:** `music.with_volume_scaled(0.3)` instead of `0.1` (3x louder, ~10dB increase)