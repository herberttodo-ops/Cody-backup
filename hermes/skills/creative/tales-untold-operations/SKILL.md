---
name: tales-untold-operations
description: Use for any Tales Untold task. Current rules.
version: 1.0.0
---

# Tales Untold Operations (load first, every time)

The canonical rules live in the Obsidian vault and are the source of truth. Older skills (spielberg, tales-untold-video-creator, tales-untold-horror-shorts) and old plan docs may be outdated. When they conflict with the vault doc, the vault doc wins.

## Step 1: read the canonical doc
`read_file "~/Documents/Obsidian Vault/Agent-Shared/Tales Untold Operating Rules.md"`

## Step 2: hard rules (summary, the doc has the detail)
1. Follow instructions literally. "Publish now" = PUBLIC now. Private + scheduled is not published. If you cannot do exactly what was asked, say so BEFORE reporting success, and ask before deviating.
2. Content is a 4-arm experiment (E, S, H, C). Only arm C is first person. Never write or regenerate stories outside `make_story(arm, ...)` in `~/.openclaw/workspace/tales-untold/arm_schedule_refill.py`. Never switch arms mid-test. Schedule runs Nov 7 to Nov 25, 14 per arm.
3. Stories must be 100-130 words. Never lower pipeline gates (100 words, 38-58s, caption gate) to pass a bad story.
4. Production: cron 7bb4ab80b2c2 -> run_arm_slot.py -> pipeline_v3.py. Watchdog d9cbff5d6e8a. Refill 82dfb9b234c0.
5. Publishing: Buffer is rate-limited; the pipeline falls back to direct YouTube upload (private + publishAt) via OAuth token `~/.config/youtube_credentials.json` (full `youtube` scope). Re-auth: `~/.hermes/scripts/youtube_oauth_device.py`. Verify every schedule by reading back privacyStatus + publishAt.
6. Cedric voice only. Gammell ink wash. No end overlay. No em dashes. Alert-only, no "all clear" messages.
7. Verify with live data before claiming anything works (API read-back, frame extraction, logs).

## Step 3: after any change
Append what changed to `Agent-Shared/decisions-log.md` and update the canonical doc if a rule changed. Back up files before editing (`.bak_YYYYMMDD`).
