# Tales Untold Pipeline Session: October 4, 2026
**Session context:** Pipeline v3 validation, folklore pivot enforcement, crontab replacement, immediate-publish failure path.

## 1. Buffer `addToQueue` ≠ Immediate Publish
When `create_post` is called **without** an explicit `dueAt`, Buffer internally assigns the next available queue slot. Observed behavior: posts intended for "right now" landed at **Oct 5 7:31 PM ET, Oct 5 8:18 PM ET, Oct 5 9:34 PM ET** because the queue is auto-slotted.

**Lesson:** To publish at a specific time, always pass `dueAt` with an explicit ISO timestamp. To publish "now", pass `dueAt = current UTC + 2 minutes` (Buffer needs processing time) and verify via `list_posts`.

**Attempted workarounds that FAILED:**
- `mode: "shareNext"` — not accepted by `create_post` (invalid value)
- `mode: "addToQueue"` with `schedulingType: "auto"` — auto-scheduled, not immediate
- `tools/call` `publishPostNow` — tool not exposed in MCP
- `tools/call` `update_post_schedule` — tool not exposed in MCP
- `tools/call` `delete_post` — works
- `tools/call` `create_post` — only way to create; no immediate-publish tool exists

## 2. YouTube OAuth Token Expiry (Sept 18 → Oct 5)
Direct YouTube API upload via `google.oauth2` token issued Sept 18 was **expired and revoked** by Oct 5. `refresh_token` grant returned `invalid_grant`.

**Lesson:** Tokens need re-auth every ~2 weeks. The device/headless OAuth flow in `youtube_oauth_headless.py` or `youtube_oauth_setup.py` should be run proactively before the token hits expiry. Do not rely on refresh_token if the user revoked it via Google Account settings.

## 3. POYO API Connection Validation
The `pipeline_v3.py` preflight check initially used `curl -H "Authorization: Bearer …" https://api.poyo.com/api/user/profile` which returns **404 Not Found**. The endpoint `/api/user/profile` does not exist at POYO.

**Correct validation:** Use a POST to the task creation endpoint with a minimal payload (e.g., `"hello"` in text field) and check for 401 vs actual task creation. A 401 means bad key; any other 4xx/5xx is a server issue.

## 4. Background Process Execution Pitfalls
**`terminal(command="…", background=True)` with `$()` evaluation fails:**
The bash `$()` in the command string gets evaluated at dispatch time, not at shell execution time inside the background process. This means `due_at="$(date -u …)"` can bind the *dispatch* time rather than the background-process start time.

**Fix:** Calculate date strings in Python before constructing the command, or accept that the exact due time will be off by a few seconds.

**Piping stdout in background (`| tee`) causes shell-level buffering issues.** When `background=True` is used with pipes, the shell may buffer and the tee subprocess may be orphaned.

**Fix:** Either redirect stdout to a known log file (`> /path/to/log` without pipe), or run `terminal(command="… > /path/to/log 2>&1", background=True)`.

## 5. Word Count Enforcement for 40-55s Duration
Target: 100-120 words = 40-55s TTS (ElevenLabs Cedric voice at normal pace).
Observed mapping:

| Words | Actual Duration | Deviation from target |
|-------|---------------|-----------------------|
| 129 | 64s | Too long (+14s) |
| 120 | 52s | Acceptable (+7s) |
| 112 | 49s | Optimal |
| 111 | 50.60s | Optimal |
| 109 | 47-48s | Optimal |

The hard enforcer at 120 words is correct but stories at the upper bound (112-120) can still run 1-3s over 55s due to pauses and longer words.

**Recommendation:** Target 100-115 words for safety, not 100-120.

## 6. Crontab vs Hermes Cron Jobs
The old Hermes cron jobs (`spielberg-6pm-slot`, `spielberg-7pm-slot`, `spielberg-8pm-slot`) were erroring silently. They were deleted and replaced with **system crontab entries** for reliability.

Crontab lines:
```
0 22 * * * cd /home/herby/.openclaw/workspace/tales-untold && export HOME=/home/herby && ./tales_v3_producer.sh 18:00:00 A >> logs/cron_6pm.log 2>&1
0 23 * * * cd /home/herby/.openclaw/workspace/tales-untold && export HOME=/home/herby && ./tales_v3_producer.sh 19:00:00 B >> logs/cron_7pm.log 2>&1
0 0 * * * cd /home/herby/.openclaw/workspace/tales-untold && export HOME=/home/herby && ./tales_v3_producer.sh 20:00:00 A >> logs/cron_8pm.log 2>&1
```

**Why system crontab over Hermes cron:** System crontab is simpler for script-only execution, has no LLM invocation overhead, and logs go directly to files. Hermes cron is better when the task requires reasoning, model calls, or multi-step logic.

## 7. HyperFrames Render Timing
Rendering a 50s composition via `npx hyperframes render` takes **2-4 minutes** depending on system load. The render subprocess (`chrome-headless` via puppeteer) uses significant CPU.

**Do not attempt to speed this up** — the render is the slowest phase and cannot be bypassed. Plan pipeline batches accordingly (1 video ~6-8 min end to end, parallel runs ~10 min).

## 8. Buffer Queue Verification Pattern
Always verify `create_post` results by calling `list_posts` afterward:
```python
result = buffer_call("list_posts", {"organizationId": org_id, "status": ["scheduled"]})
# Parse edges array to confirm the new post exists at the expected dueAt
```

Observed queue state after Oct 4 session:
| Post | Status | Due (ET) |
|------|--------|----------|
| Beast of Gévaudan | scheduled | Oct 5 7:31 PM |
| Baba Yaga | scheduled | Oct 5 8:18 PM |
| Bell Witch | scheduled | Oct 5 9:34 PM |
| Wendigo (v2) | scheduled | Oct 7 6:00 PM |
| Wendigo | scheduled | Oct 6 6:00 PM |

## 9. Tales Untold Content Pivot Plan Compliance
User enforced compliance with the Content Pivot Plan on Oct 4. All stories must be:
- **Tier 1 folklore/cryptid entities** (named entities: Wendigo, Mothman, Skinwalker, etc.)
- **100-120 words** for 40-55s duration
- **Title format:** `[Entity]: [Specific Angle]` — NO `| Tales Untold` suffix (burns title chars at low sub count)

Generic horror stories (e.g., "The Last Photograph") were **rejected and deleted** from Buffer.

Current approved entity list with story templates lives in `tales_v3_producer.sh` — 14 entities including: Wendigo, Mothman, Skinwalker, Chupacabra, Jersey Devil, Beast of Gévaudan, Bell Witch, Baba Yaga, La Llorona, Phantom Hiker, Loch Ness, Dracula, Banshee, Bigfoot/Sasquatch.
