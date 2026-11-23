# POYO Model ID Discovery — 2026-11-22

## Problem
POYO has no `/api/models` list endpoint. Every model ID must be known in advance. When a model (e.g. Wan 3.0) is advertised on the public site (`poyo.ai/models/wan-3-0-video-prime`), the URL slug does NOT match the API model ID.

## What does NOT work
- Guessing canonical model names (`wan-3-0-t2v-14b`, `wan-3-0-i2v-14b`, etc.) — all return 404
- URL-derived names (`wan-3-0-video-prime`) — also 404
- No GET endpoint at `/api/models`, `/api/v1/models`, `/api/generate/models`

## What DOES work
1. **Tested working IDs on this key:**
   - `gpt-image-2` — Image generation
   - `elevenlabs-v3-tts` / `elevenlabs-tts-turbo-2-5` — Voice
   - `gpt-4o-mini` — Chat
   - `nano-banana-2-lite` — Tales Untold image pipeline

2. **Discovery via submit probe:** The only reliable method is submitting dummy tasks with candidate slugs to `/api/generate/submit` and checking for "Model not found" vs. other errors (auth, param validation). A 404 on the model specifically means the ID is wrong or the key lacks access. A non-404 means the model exists but the request was malformed.

```python
import json, urllib.request

# Probe pattern
def probe_model(model_id, api_key):
    req = urllib.request.Request(
        'https://api.poyo.ai/api/generate/submit',
        data=json.dumps({'model': model_id, 'input': {'prompt':'test'}}).encode(),
        headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}
    )
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        return json.loads(resp.read().decode())  # Valid task_id = EXISTS
    except urllib.error.HTTPError as e:
        body = json.loads(e.read().decode())
        msg = body.get('error',{}).get('message','')
        if 'not found' in msg.lower() or msg.startswith('Model not found'):
            return None  # Model ID is wrong or key lacks access
        else:
            return body  # Model EXISTS but request was bad
```

3. **Web page scraping (fallback):** The public site `poyo.ai/models/<slug>` is a React SPA. The HTML contains the slug in `<script>` tags and `<meta>` tags, but NOT the API model ID. Do not rely on URL slugs as API IDs.

## Key Lesson
**POYO's public marketing site and its API use different namespaces.** A model being listed on `poyo.ai/models/X` does NOT mean API key has access to X, nor that the API ID matches the URL slug. Always verify with a probe before committing to a model in production.
