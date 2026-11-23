# Tales Untold Duplicate Slot Bug — 2026-11-22

## Symptom
`arm_log.json` accumulates duplicate entries for the same date+entity+region combination. Refill cron produces "next to duplicate" videos — two slots with same content back-to-back or within hours.

## Root Cause
The refill cron (`7bb4ab80b2c2`) has a "retry once after 5 min" guard in its prompt. When a run fails, it re-queues. The dedupe guard in `run_arm_slot.py` only checks:

```python
if slot.get("status") == "scheduled":
    return None  # Skip
```

This FAILS to block retries of "failed" runs. A slot that failed 5 minutes ago is not "scheduled", so the retry creates a brand new slot with identical content.

## Impact
- 44 duplicate entries found in arm_log.json at time of discovery
- Wasted arm slots
- Pipeline confusion: refill logic can't distinguish real failures from retry-dups
- Compounds silently over time

## The Fix

### Immediate — broaden dedupe check
```python
# Current (broken):
if slot.get("status") == "scheduled":
    return None

# Fix:
if any(s.get("status") in ("scheduled", "processing", "failed")
       for s in existing_slots):
    return None
```

### Better — hash-based dedupe
Check `arm_log.json` by `date + entity + region` hash before submitting any new slot, regardless of status. Use a deterministic fingerprint (MD5 of sorted keys) to guarantee uniqueness.

```python
import hashlib
slot_hash = hashlib.md5(
    f"{date}:{entity}:{region}".encode()
).hexdigest()
if slot_hash in seen_hashes:
    return None
```

## Prevention
- All retry logic must check against ALL statuses, not just "scheduled"
- Retry policies should be idempotent: identical inputs → identical outputs → deduped
- Log a warning when dedupe fires so it's visible in cron output
