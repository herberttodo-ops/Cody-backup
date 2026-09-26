# Tales Untold Voice Change Procedure

Changing the narrator voice requires updating **all** production scripts to maintain consistency.

## Voice Configuration

**Current Voice:** Ezekiel (`vtgK8BnczFgE1AamLPao`) — raspy narrator
**Previous Voice:** Adam (`pNInz6obpgDQGcFmaJgB`)

**Model:** `elevenlabs-tts-turbo-2-5` via POYO API

## Files to Update

| File | Line Pattern | Count |
|------|--------------|-------|
| `scripts/run_folklore_spielberg.py` | `{"voice": "Ezekiel", "text": text}` | 1 |
| `scripts/batch_folklore_producer.py` | `{"voice": "Ezekiel", "text": text}` | 1 |
| `scripts/run_bell_witch_24.py` | `{"voice": "Ezekiel", "text": text}` | 1 |
| `scripts/pilot_fallback.py` | `{"voice": "Ezekiel", "text": text}` | 1 |
| `batch_process.py` | `"voice": "Ezekiel"` | 1 |
| `poyo_client.py` | `voice_id = "..."` (default param) | 1 |

## Update Command

```bash
# Replace Adam → Ezekiel in all scripts
sed -i 's/"voice": "Adam"/"voice": "Ezekiel"/g' \
  scripts/run_folklore_spielberg.py \
  scripts/batch_folklore_producer.py \
  scripts/run_bell_witch_24.py \
  scripts/pilot_fallback.py \
  batch_process.py

# Update poyo_client.py default voice_id
sed -i 's/voice_id = "pNInz6obpgDQGcFmaJgB"/voice_id = "vtgK8BnczFgE1AamLPao"  # Ezekiel/' poyo_client.py
```

## Voice IDs Reference

| Voice | ID | Quality | Notes |
|-------|-----|---------|-------|
| Adam | `pNInz6obpgDQGcFmaJgB` | Clear, neutral | Original Tales voice |
| Ezekiel | `vtgK8BnczFgE1AamLPao` | Raspy, aged | Horror-optimized |

**Verify a voice swap via:** MD5 hash + duration + band RMS comparison of output files.

## Background

POYO takes raw ElevenLabs voice IDs without validation — bad IDs fail silently. Always verify voice changes by generating a test clip and checking audio characteristics match expectations.
