# POYO API Quirks — Tales Untold

## Shell Key Mangling (Critical)

**Never pass `POYO_API_KEY` via shell `$VAR` interpolation.** Both bash and curl mangle the value, truncating it to ~13 characters and causing "Invalid API key format" errors.

### Fails
```bash
# WRONG — bash interprets special chars in the key
API_KEY=$(grep POYO_API_KEY .env | cut -d= -f2)
curl -s -H "Authorization: Bearer $API_KEY" https://api.poyo.ai/...

# Also wrong — heredoc/substitution breaks it
curl -s ... -d "{\"Authorization\":\"Bearer $API_KEY\"}"
```

### Works
```python
import os, requests
API_KEY = os.environ.get("POYO_API_KEY", "")
# Or read directly from .env file
r = requests.post(
    "https://api.poyo.ai/api/generate/submit",
    headers={"Authorization": f"Bearer {API_KEY}"},
    json={"model": "nano-banana-2-lite", "input": {...}}
)
```

```bash
# If you must use curl, export the full key explicitly, unquoted
cd ~/.openclaw/workspace/tales-untold
export POYO_KEY=$(python3 -c "import os; print(os.environ.get('POYO_API_KEY',''))")
echo "Key length: ${#POYO_KEY}"
curl -s -H "Authorization: Bearer $POYO_KEY" ...
```

### Verification
```bash
# Always verify env var length
python3 -c "import os; k=os.environ.get('POYO_API_KEY',''); print(f'Length: {len(k)}, first 15: {k[:15]}')"
```

---

## Response Format: Nesting Under "data"

All POYO responses (image, TTS, video) now nest results under `"data"`:

```python
result = r.json()

# WRONG (old format expected top-level)
task_id = result["task_id"]

# CORRECT (all models, 2026-09-15+)
task_id = result["data"]["task_id"]
status = result["data"]["status"]
url = result["data"]["files"][0]["file_url"]  # for completed tasks
```

---

## TTS Model Change (2026-09-15)

POYO removed `elevenlabs` and `elevenlabs-tts` models. Current working model:

```json
{
  "model": "elevenlabs-tts-turbo-2-5",
  "input": {
    "voice": "Adam",
    "text": "Your story here",
    "speed": 1.0
  }
}
```

**Voice "Adam" is Tales Untold brand.** Never silently fallback to other voices. If Adam fails, report to user — do NOT substitute without explicit permission.

---

## Image Model

`nano-banana-2-lite` is the approved Gammell-style generator.

```json
{
  "model": "nano-banana-2-lite",
  "input": {
    "prompt": "Scene description, ink wash illustration in Stephen Gammell style, monochrome grayscale",
    "size": "9:16"
  }
}
```

Returns JPEG at ~768×1376 regardless of `"size": "9:16"` param. CSS `object-fit: cover` handles scaling in HyperFrames.

---

## Poll Timing

Image tasks: 30-60 seconds typical TTS tasks: 10-30 seconds typical

```python
for attempt in range(60):
    status = requests.get(f"https://api.poyo.ai/api/generate/status/{task_id}", ...).json()
    state = status["data"]["status"]
    if state == "finished":
        # download immediately — URLs expire
        url = status["data"]["files"][0]["file_url"]
        break
    elif state == "failed":
        # report failure to user
        break
    time.sleep(5)
```

---

## API Limits (Observed)

- 5 concurrent image tasks seems stable
- 6+ concurrent tasks may queue longer or timeout
- TTS: submit sequentially (no concurrency needed, fast)
- Health endpoint: `GET https://api.poyo.ai/api/health` → always returns OK even when individual models are down
