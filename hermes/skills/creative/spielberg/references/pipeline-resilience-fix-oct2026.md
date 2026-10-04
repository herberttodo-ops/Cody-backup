# Tales Untold Pipeline Resilience Fix — October 2026

## Incident: October 2, 2026 — All 3 Daily Slots Failed

### Failure Pattern
| Slot | Failure Point | Root Cause |
|------|--------------|------------|
| 6pm ET | YouTube upload | Composio -> Google API returned `429 Too Many Requests`. No retry logic. Video rendered, never posted. |
| 7pm ET | TTS generation | `poyo_submit()` returned `task_id: None`. `poll(None)` hit HTTP 404. No retry. Pipeline died immediately. |
| 8pm ET | TTS generation | Same `task_id: None` issue. |

### Compounding Factor
Two independent failure modes coincided: TTS API was returning null task_ids for 7pm/8pm, while Google rate-limited the 6pm upload.

---

## Permanent Fixes Applied

All changes in `~/.openclaw/workspace/tales-untold/scripts/auto_producer.py`.

### 1. `poyo_submit()` — Submission with Retry & Validation

Replaces the old `poyo()` helper that blindly returned whatever the API gave.

```python
def poyo_submit(model, inp, retries=5):
    for attempt in range(retries):
        try:
            r = requests.post("https://api.poyo.ai/api/generate/submit", ...)
            if r.status_code in (429, 502, 503, 504):
                wait = min(2 ** attempt * 5, 60)
                time.sleep(wait)
                continue
            r.raise_for_status()
            data = r.json()
            inner = data.get("data", data)
            task_id = inner.get("task_id") or inner.get("id")
            if task_id and isinstance(task_id, str) and len(task_id) > 3:
                return task_id
            # Log bad response for diagnostics
            wait = min(2 ** attempt * 5, 60)
            time.sleep(wait)
        except requests.exceptions.RequestException as e:
            wait = min(2 ** attempt * 5, 60)
            time.sleep(wait)
    raise RuntimeError(f"POYO submit failed after {retries} attempts")
```

**Key improvements:**
- Validates `task_id` is a string with length > 3 before returning
- Retries on HTTP 429, 502, 503, 504
- Exponential backoff from 5s up to 60s
- Logs raw response when task_id is missing/null

### 2. `retry_stage()` — Entire Pipeline Stage Wrapper

```python
def retry_stage(name, fn, retries=3, base_wait=None):
    base = base_wait or 10
    for attempt in range(retries):
        try:
            return fn()
        except Exception as e:
            wait = min(2 ** attempt * base, 300)
            print(f"  {name} attempt {attempt+1}/{retries} failed: {e}")
            if attempt < retries - 1:
                time.sleep(wait)
            else:
                raise
```

**Applied to:** TTS, Images, HyperFrames Render.
- TTS: 3 retries, 5s base wait
- Images: 3 retries, 5s base wait  
- Render: 2 retries, 15s base wait

**Why these numbers:** TTS and images depend on POYO API which is fast but flaky. Render depends on HyperFrames which is slow but stable — fewer retries with longer waits.

### 3. `upload_composio()` — Upload with Retry & 429 Handling

```python
def upload_composio(video_path, title, desc, ...):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            out = subprocess.check_output(cmd, ...)
            # ... extract video_id ...
            # Check for 429 in response body even on HTTP 200
            if "429" in out_str or "Too Many Requests" in out_str:
                wait = min(2 ** attempt * 30, 300)
                time.sleep(wait)
                continue
            return out, video_id
        except subprocess.CalledProcessError as e:
            if "429" in err:
                wait = min(2 ** attempt * 30, 300)
            else:
                wait = min(2 ** attempt * 10, 120)
            time.sleep(wait)
    return json.dumps({"successful": False, ...}), None
```

**Key improvements:**
- 5 retries with 30s base backoff for 429s (30s, 60s, 120s, 240s, 300s)
- Catches 429 in Composio response body even when HTTP status is 200
- Returns structured failure object instead of crashing

### 4. `rescue_orphan_uploads()` — Stranded Video Recovery

Runs at the start of every `main()` call before producing new videos:

```python
def rescue_orphan_uploads():
    for f in OUTPUT.glob("FINAL_*.mp4"):
        state = json.loads(POOL_STATE.read_text())
        if vid_name not in state.get("produced", []):
            # Attempt upload of stranded video
            upload_composio(vid_path, title, desc, thumbnail_path=thumb)
```

**Purpose:** If upload fails but render succeeds, the video isn't lost forever. Next cron run will pick it up and retry the upload.

---

## Failure Modes This Fix Addresses

| Failure | Old Behavior | New Behavior |
|---------|-------------|--------------|
| POYO returns `task_id: null` | `poll(None)` hits 404, immediate crash | Retried up to 5x with backoff, then raises cleanly |
| POYO HTTP 429/502/503/504 | `raise_for_status()` crashes | Retried with exponential backoff |
| YouTube upload 429 | `check_output()` crashes, video lost | Retried up to 5x with 30s base backoff, then orphan-rescued next run |
| HyperFrames render fails | Entire pipeline dies | Retried 2x with 15s base wait |
| Orphan video (upload failed post-render) | Lost forever | Auto-rescued on next cron run |

---

## Monitoring: How to Spot Future Failures

Check cron output directories for patterns:

```bash
# TTS null task_id (should no longer happen)
grep "TTS task None" ~/.hermes/cron/output/bcd4e38c8de3/*.md

# POYO retry events (expected occasionally, should succeed on retry)
grep "POYO submit empty task_id\|POYO submit HTTP" ~/.hermes/cron/output/*/latest.md

# YouTube 429 (expected occasionally, should succeed on retry)
grep "429" ~/.hermes/cron/output/*/latest.md

# Orphan rescue events
grep "RESCUING ORPHAN" ~/.hermes/cron/output/*/latest.md
```

**Thresholds for alerting:**
- POYO submit fails all 5 retries: investigate POYO API health
- YouTube 429 persists across 5 retries: quota may be depleted, investigate Composio account
- Orphan rescue fails 2 consecutive runs: upload path may be permanently broken

---

## Related Files

- `~/.openclaw/workspace/tales-untold/scripts/auto_producer.py` — main pipeline script
- `~/.hermes/skills/creative/spielberg/references/poyo-api-quirks.md` — POYO API behavior
- `~/.hermes/scripts/tales_auto_producer.sh` — cron wrapper (sets POYO_API_KEY)
- `~/.hermes/cron/output/bcd4e38c8de3/` — 6pm slot logs
- `~/.hermes/cron/output/d41d210b5edb/` — 7pm slot logs
- `~/.hermes/cron/output/06c25f1cb777/` — 8pm slot logs

---

## Date Applied
October 3, 2026
