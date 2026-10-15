# Tales Untold Date Calculation Bug — October 14, 2026

**Issue:** Cron-scheduled video production was scheduling videos for the wrong day, causing persistent evening slot misses.

## Symptoms

- Watchdog reports "missed slots" for 6pm/7pm/8pm ET
- 3 videos ARE produced daily (8am, 12pm, 4pm cron runs)
- But evening slots still appear empty
- Logs show `due_at` timestamps for tomorrow instead of today

## Root Cause

The producer script used `date -d 'tomorrow'` unconditionally:

```bash
# OLD (BROKEN) — Always schedules for tomorrow
DUE_DATE="${2:-$(TZ=America/New_York date -d 'tomorrow' +%Y-%m-%d)}"
```

When cron runs at 8am ET to produce a 6pm same-day video, this scheduled it for tomorrow 6pm instead.

## The Fix (v3.1)

Intelligent date calculation based on current time:

```bash
CURRENT_HOUR_ET=$(TZ=America/New_York date +%H)

if [ "$CURRENT_HOUR_ET" -lt 18 ]; then
    # Before 6pm ET: schedule for TODAY
    DUE_DATE="${2:-$(TZ=America/New_York date +%Y-%m-%d)}"
else
    # After 6pm ET: schedule for TOMORROW
    DUE_DATE="${2:-$(TZ=America/New_York date -d 'tomorrow' +%Y-%m-%d)}"
fi
```

## Scheduling Patterns

| Cron Run Time | Target Slot | Correct Due Date |
|--------------|-------------|------------------|
| 8:00 AM ET | 6:00 PM same day | Today |
| 12:00 PM ET | 7:00 PM same day | Today |
| 4:00 PM ET | 8:00 PM same day | Today |
| 6:00 PM ET+ | Next day's slots | Tomorrow |

## Detection

If investigating "missed evening slots":

1. Check watchdog alerts in `~/.openclaw/workspace/tales-untold/logs/watchdog_alerts.json`
2. Verify videos were produced that day: `ls -lt output/FINAL_*.mp4`
3. Check scheduled `due_at` in pipeline logs: `grep "due=" logs/pipeline_*.log`
4. If due_at is tomorrow → date bug confirmed

## Prevention

- Always use time-aware date calculation for scheduled content
- Add explicit logging: `"Scheduling for TODAY/TOMORROW ($DUE_DATE)"`
- Validate due_at is within 24 hours when same-day slots are expected
- Consider using explicit date parameters in cron commands instead of auto-calculation

## Emergency Fix

When this bug leaves slots empty:

1. Run manual bulk refill: `~/.openclaw/workspace/tales-untold/emergency_bulk_refill.sh`
2. Or trigger individual producer runs with explicit dates:
   ```bash
   bash tales_v3_producer_v3.1.sh "18:00:00" "$(date +%Y-%m-%d)" A
   ```

## Related

- `tales_v3_producer_v3.1.sh` — Fixed version with smart date calculation
- `cron-3x-daily-slot-patterns.md` — Cron scheduling patterns for Tales Untold
- `pipeline-resilience-oct2026.md` — General pipeline reliability patterns
