# Tales Untold Pipeline v3.0 — Resource-Aware Auto-Producer

**Applied:** October 4, 2026  
**Replaces:** v2.1 (retry-only fix)  
**Purpose:** Handle resource exhaustion (credits, quota) without wasting retries or spamming failures

---

## The Real Problem with v2.1

v2.1 added retry logic for transient failures. Tonight's failure was **resource exhaustion**:

| Failure | Type | Retry Helps? | What Actually Happened |
|---------|------|--------------|------------------------|
| POYO HTTP 402 "insufficient credits" | Resource exhaustion | **NO** — 15 retries × 3 slots = 45 wasted attempts | Credits at zero |
| YouTube 429 persistent across 5 retries | Quota exhaustion | **NO** — kept burning quota | Google API quota depleted |

**Result:** 0 videos produced, 0 videos uploaded, quota/credits wasted on doomed retries.

---

## v3.0 Solution: Resource Guards

### 1. POYO Credit Guard
**Before any production:**
```python
credits, should_halt = check_poyo_credits()
if should_halt:
    send_alert("POYO_CREDITS")
    queue_story_for_later()
    exit_cleanly()
```
- Calls POYO `/api/billing/credits` endpoint
- Halts if credits < 3 (need ~1 per video for TTS + images)
- Queues story instead of failing
- Sends **one alert** per depletion event

### 2. YouTube Quota Guard
**Tracks 429 history:**
```python
if youtube_429_count >= 3:
    send_alert("YOUTUBE_QUOTA")
    halt_until_quota_resets()
```
- Counts consecutive 429 responses
- Alerts after threshold (configurable)
- Prevents burning remaining quota on doomed uploads

### 3. Upload Ledger (replaces fragile pool_state tracking)
**`upload_log.json` structure:**
```json
{
  "uploaded": [
    {"name": "skinwalker_tracking", "video_id": "abc123", "uploaded_at": "2026-10-03T18:00:00-04:00"}
  ]
}
```
- Source of truth for "was this video uploaded?"
- Survives `pool_state.json` wipes/corruption
- Orphan rescue uses this — never re-rescues already-uploaded videos

### 4. Production Queue
**`production_queue.json`:**
```json
{
  "pending": [
    {"name": "mothman_second_visitor", "slot_label": "6pm ET", "due_at": "...", "queued_at": "..."}
  ]
}
```
- Stories queued when resources exhausted
- Auto-processed when resources return
- Prevents story loss during outages

### 5. Resumable Upload Format
Changed `YOUTUBE_MULTIPART_UPLOAD_VIDEO` → `YOUTUBE_UPLOAD_VIDEO`:
- **Old:** ~1600 API units per upload (~6 uploads/day with 10k quota)
- **New:** ~500 API units per upload (~20 uploads/day)
- **3x capacity** for same quota

### 6. Rate-Limited Alerts
```python
def should_alert(state, alert_type):
    # Max 1 alert per hour per type
    return (now - last_alert) > 3600 seconds
```
- Prevents spam during extended outages
- Only actionable notifications
- Follows your heartbeat policy

---

## Flowchart

```
CRON TRIGGER (6/7/8 PM ET)
    │
    ▼
CHECK RESOURCES
    ├── POYO credits >= 3? ──NO──► QUEUE STORY + ALERT + EXIT
    └── YouTube 429 count < 3? ──NO──► ALERT + EXIT
    │
    YES
    ▼
RESCUE ORPHANS (using upload_log, not pool_state)
    │
    ▼
CHECK QUEUE
    ├── Queued story? ──YES──► PROCESS QUEUED
    └── No queue? ──NO──► PICK NEW STORY
    │
    ▼
PRODUCE VIDEO
    ├── TTS (with retry)
    ├── Images (with retry)
    ├── Render (with retry)
    └── Upload (with retry + 429 tracking)
    │
    ▼
ON UPLOAD SUCCESS
    ├── Log to upload_log.json
    ├── Log to pool_state.json
    └── Clear any queue entry
    │
    ON RESOURCE FAILURE DURING PRODUCTION
    └── QUEUE STORY + EXIT
```

---

## Data Files

| File | Purpose | Format |
|------|---------|--------|
| `upload_log.json` | Tracks successfully uploaded videos | `{"uploaded": [{name, video_id, uploaded_at}]}` |
| `production_queue.json` | Queued stories when resources exhausted | `{"pending": [{name, slot_label, due_at, queued_at}]}` |
| `resource_state.json` | Credit/quota tracking | `{poyo_credits, youtube_429_count, last_alert}` |
| `pool_state.json` | Story pool index (legacy) | `{"produced": [], "pool_index": 0}` |

---

## Alert Thresholds

| Resource | Threshold | Action |
|----------|-----------|--------|
| POYO credits | < 3 | Halt production, queue stories, send alert |
| YouTube 429s | 3 consecutive | Halt uploads, send alert |
| Alert rate limit | 1 per hour | Prevent spam during outages |

---

## Recovery Behavior

When POYO credits return:
1. Next cron run passes credit check
2. Processes queued stories first (FIFO)
3. Resumes normal production

When YouTube quota returns:
1. 429 count resets on successful upload
2. Orphan rescue attempts re-upload
3. Normal flow resumes

---

## Monitoring

Check resource state:
```bash
cat ~/.openclaw/workspace/tales-untold/data/resource_state.json
```

Check queue:
```bash
cat ~/.openclaw/workspace/tales-untold/data/production_queue.json
```

Check upload history:
```bash
cat ~/.openclaw/workspace/tales-untold/data/upload_log.json | jq '.uploaded[-5:]'
```

---

## Backwards Compatibility

- `pool_state.json` still used for story pool indexing
- `upload_log.json` is additive — doesn't break existing logic
- Orphan rescue now uses `upload_log` as primary source, falls back to `pool_state`

---

## Files Modified

- `scripts/auto_producer.py` — complete rewrite (v3.0)
- `data/upload_log.json` — new
- `data/production_queue.json` — new  
- `data/resource_state.json` — new

---

**Status:** Live as of October 4, 2026. Next cron run at 10pm ET will use v3.0.
