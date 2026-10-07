# Cron LLM Timeout — Silent Slot Loss

**Date:** 2026-10-06  
**Affected Job:** `spielberg-buffer-refill-daily` (7bb4ab80b2c2)  
**Session:** Tales Untold shorts pipeline investigation

## What Happened

The 4 PM ET cron run targeting the 8 PM ET posting slot died with a provider timeout before executing any pipeline code:

```
RuntimeError: Non-streaming API call timed out after 150s with no response (threshold: 150s)
```

No video was produced. The 8 PM ET slot was entirely missed.

## Diagnosis Pattern

| Signal | Meaning |
|--------|---------|
| `last_status: error` | The cron agent itself crashed, not the pipeline |
| Cron output file unusually short | A normal run is ~520+ lines; this timeout produced ~489 lines |
| No pipeline logs after the cron start time | The agent timed out during planning, before touching any tools |
| No new files in `hyperframes-test/` or `output/` | Confirms zero progress was made |

This is **not** a Buffer failure, POYO failure, code bug, or delivery failure. It is a transient upstream LLM/provider stall. The cron executor on the Hermes side timed out the non-streaming API call to the model provider (OpenRouter / kimi-k2.5) after 150 seconds.

## Lesson: A 3x/Day Refill Is More Fragile Than It Appears

A 3x/day posting schedule with 3 separate cron runs (6 PM, 7 PM, 8 PM ET) means **any single LLM timeout drops a slot permanently**. There is no automatic catch-up. The next cron runs on its own fixed schedule and targets its own designated slot. A 4 PM timeout means the 8 PM slot stays empty until a manual run fills it or the next day's 8 PM slot is targeted.

## Mitigations

1. **Separate hardcoded-slot cron jobs** are already the right architecture (not one job that tries to detect time). If one slot fails, the others are independent.

2. **Manual fill as backstop.** When investigating cron health, check whether the expected number of videos was produced for the day. If one is missing, trigger a manual run:
   ```
   cronjob run --job_id JOB_ID
   ```
   The manual run uses a fresh LLM session and usually succeeds when the prior timed-out run failed.

3. **Do NOT over-engineer retry loops inside the cron prompt.** A ~150s timeout is an upstream provider issue; immediate local retry will likely hit the same stall. Wait 5-10 minutes or trigger manually.

## Related

- `cronjob-delivery-debugging` skill for distinguishing execution vs delivery failures
- `references/pipeline-resilience-oct2026.md` for resource-exhaustion timeouts (different cause, different fix)
