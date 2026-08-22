# Daily Heartbeat Checklist

## OptiRFP Buffer Queue Management
**Status:** Auto-managing remaining 12 posts (Days 19-24)
**Checks:** During each heartbeat
**Action:** Add posts if slots available

### What to do:
1. Check current scheduled post count using `mcp__buffer__list_posts`
2. If < 10 scheduled, add next available day(s) from `~/.hermes/optirfp_buffer_queue.md`
3. Update the queue file with status changes
4. Continue until all 24 days complete

### Remaining Content (ready to post):
- Days 19-24: Sep 1 - Sep 6
- All copy and images prepared
- Just needs Buffer `customScheduled` mode

### Tracking:
- Days 2-18: ✅ Scheduled/published
- Days 19-24: ⏳ Waiting for slots

## Other Checks
- [ ] Any urgent messages
- [ ] Calendar events next 24h
- [ ] Any failed/completed background processes

## If Nothing Urgent
Reply: **HEARTBEAT_OK** (Buffer management runs silently)
