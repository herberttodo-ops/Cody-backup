# Buffer Scheduling: 3x/Daily Staggered Slot Pattern

## Problem
When a channel posts 3 times per day (e.g., 6pm, 7pm, 8pm ET), a single daily cron that produces 1 video will **always** place it at the first slot it checks (typically 22:00 UTC / 6pm ET). The 7pm and 8pm slots remain permanently empty unless a human or a separate cron explicitly targets them.

## Solution: Multiple Cron Runs Per Day
Split production across 3 short cron runs, each targeting a single time slot.

### Slot Mapping
| Cron Run Time | Target Slot (UTC) | Target Slot (ET) | due_at value |
|---------------|-------------------|-------------------|--------------|
| 8:00 AM ET | 22:00 UTC | 6:00 PM ET | `YYYY-MM-DDT22:00:00Z` |
| 12:00 PM ET | 23:00 UTC | 7:00 PM ET | `YYYY-MM-DDT23:00:00Z` |
| 4:00 PM ET | 00:00+1 UTC | 8:00 PM ET | `YYYY-MM-DDT00:00:00Z` (next day) |

### Cron Schedule
```
0 8,12,16 * * *
```

### Prompt Logic
Each run determines its target slot from the current time, then queries Buffer to find the earliest date that does NOT already have a post at that specific hour. This naturally fills 7pm and 8pm slots without any run guessing which gap to backfill.

### Why Not 3 Videos Per Cron Run?
Serializing ~60-90 minutes of TTS + image generation into one session is fragile. If POYO TTS hangs or HyperFrames render crashes, the entire batch dies silently. Three short runs are resilient: if one fails, the next picks up.

## Lessons from Production (Tales Untold, 2026-09-24)
- **Single daily cron (`0 8 * * *`):** Posted all videos to 22:00 UTC (6pm ET) for weeks. The 7pm and 8pm slots were completely empty. The user had to point this out explicitly.
- **After switching to `0 8,12,16 * * *`:** The 12pm and 4pm runs immediately populated the 7pm and 8pm slots for the same day.
- **Critical verification step:** Always check Buffer output shows the **expected times**, not just that posts exist. A post at the wrong hour is as bad as no post.

## Anti-Patterns to Avoid
- **Posting all videos at the same hour** — defeats staggered scheduling intent
- **Producing 3 videos in one cron run** — serializes fragile; one failure kills the whole batch
- **Not checking actual scheduled times** — "scheduled_count: 6" means nothing if all 6 are at 6pm
- **Using `addToQueue` without `dueAt`** — Buffer places posts at unpredictable times (seen: 7:31 PM instead of 7:00 PM)
