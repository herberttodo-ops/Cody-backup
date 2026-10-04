# Pipeline Resilience — Tales Untold Auto-Producer v3.0

**Session:** October 3-4, 2026  
**Problem:** 3 consecutive days of silent posting failures (0-1 videos/day vs target 3/day)  
**Root cause class:** Retry logic was built for transient failures, but resource exhaustion (credits, quota) caused permanent failures that retries only made worse.

---

## Failure History

| Date | 6pm slot | 7pm slot | 8pm slot | Root cause |
|------|----------|----------|----------|------------|
| Oct 1 | Rendered, upload 429 | Rendered, upload 429 | Produced successfully | YouTube quota intermittent |
| Oct 2 | Rendered, upload 429 | TTS task_id=None | TTS task_id=None | POYO returning null task_ids + YouTube 429 |
| Oct 3 | TTS 402 "credits depleted" | TTS 402 | TTS 402 | POYO credits at zero + YouTube 429 persistent |

**Key insight:** After the first slot fails with a resource error, the second and third slots will also fail. Retrying 5+ times per slot × 3 slots = 15+ wasted attempts that burn remaining quota and delay user notification.

---

## v2.1 Fix (Retry-only — Insufficient)

Added to `auto_producer.py` on Oct 3:
- `poyo_submit()` with 5 retry attempts and exponential backoff
- `retry_stage()` wrapper for TTS, Images, Render
- `upload_composio()` with 5 retry attempts for YouTube 429
- `rescue_orphan_uploads()` for rendered-but-unuploaded videos

**Why it failed:**
- POYO HTTP 402 "insufficient credits" is a **permanent error** — retry will never succeed
- YouTube 429 that persists across 5 retries means **quota fully depleted** — more retries burn the small remaining quota
- `pool_state.json` got wiped, so orphan rescue rescued random videos instead of actual orphans

---

## v3.0 Fix (Resource-Aware — Sufficient)

### 1. POYO Credit Guard
```python
def check_poyo_credits():
    r = requests.get("https://api.poyo.ai/api/billing/credits", ...)
    credits = r.json().get("credits", 0)
    return credits, credits < POYO_CREDITS_MIN  # Min = 3
```
- Called at start of every production run
- Halts immediately, queues story, sends one alert
- No wasted retries on depleted credits

### 2. YouTube Quota Guard
- Tracks consecutive 429 count in `resource_state.json`
- Halts uploads after threshold (default 3)
- Resets counter on successful upload
- Prevents burning remaining quota on doomed retries

### 3. Upload Ledger (`upload_log.json`)
```json
{
  "uploaded": [
    {"name": "skinwalker_tracking", "video_id": "abc123", "uploaded_at": "2026-10-03T18:00:00-04:00"}
  ]
}
```
- Source of truth for "was this video uploaded?"
- Survives `pool_state.json` corruption/wipes
- Orphan rescue uses this as primary check

### 4. Production Queue (`production_queue.json`)
```json
{
  "pending": [
    {"name": "mothman_second_visitor", "slot_label": "6pm ET", "due_at": "...", "queued_at": "..."}
  ]
}
```
- Stories queued when resources exhausted
- Auto-processed when resources return
- FIFO order prevents story loss

### 5. Resumable Upload Format
Changed from `YOUTUBE_MULTIPART_UPLOAD_VIDEO` to `YOUTUBE_UPLOAD_VIDEO`:
- **Multipart:** ~1600 API units per upload (~6/day with 10k quota)
- **Resumable:** ~500 API units per upload (~20/day)
- **3x daily capacity** for same quota

---

## Alert Design (Critical)

Per user policy: **only actionable issues**, no "all clear" spam.

```python
def should_alert(state, alert_type):
    last = state.get("last_alert")
    if last and (now - last) < 3600:
        return False  # Rate limit: 1 alert/hour
    return True
```

Triggers:
- POYO credits < 3: one alert with top-up instructions
- YouTube 429 count >= 3: one alert with quota reset time
- Queue backlog > 3 videos: one alert

---

## Implementation Checklist

When setting up or auditing a Tales Untold pipeline:

- [ ] `data/upload_log.json` exists and is writable
- [ ] `data/production_queue.json` exists and is writable
- [ ] `data/resource_state.json` exists and is writable
- [ ] `poyo_submit()` detects HTTP 402 and raises immediately (no retry)
- [ ] `check_resources()` runs before every production cycle
- [ ] `upload_composio()` uses `YOUTUBE_UPLOAD_VIDEO` (resumable), not multipart
- [ ] `rescue_orphan_uploads()` checks `upload_log.json` first, `pool_state.json` only as fallback
- [ ] Alerts are rate-limited to 1/hour per alert type
- [ ] Cron jobs use the correct `tales_auto_producer.sh` wrapper (not direct `auto_producer.py`)

---

## Data Files

| File | Purpose | Created by |
|------|---------|------------|
| `upload_log.json` | Tracks uploaded videos | Pipeline success path |
| `production_queue.json` | Queued stories during outages | Pipeline halt path |
| `resource_state.json` | Credit/quota tracking | Resource guards |
| `pool_state.json` | Story pool index (legacy) | Story selection |

All in `~/.openclaw/workspace/tales-untold/data/`
