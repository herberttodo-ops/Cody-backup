# Tales Untold: "will today's posts go out?" triage

1. Slot map: tales-untold/data/arm_schedule.json (18/19/20:00 ET), data/arm_log.json (scheduled vs failed; duplicate failed rows = retry), logs/pipeline_*.log, cron output ~/.hermes/cron/output/7bb4ab80b2c2/.
2. No output/FINAL_*_YYYYMMDD.mp4 for today = nothing produced yet.
3. pipeline_v3.py gate: 100-135 words, >=38s. Error "Duration 31s below 38s min". Root cause Nov 2026: ~/.hermes/scripts/tale_arm_schedule_refill.py (9am no_agent cron) had its own 65-75 word TEMPLATES; fixed by importing TEMPLATES from workspace arm_schedule_refill.py (100-111 words). After any refill verify: wc -w queue/*.txt | sort -n | head.
4. Manual produce: run_arm_slot.py 18:00:00 with background=true (~4-5 min). Exit 3 = slot already scheduled.
5. "PIPELINE COMPLETE" does NOT prove scheduling: pipeline_v3 only logs "Buffer output unclear" when Buffer returns an error JSON. Grep log for "Too many requests"/429. logs/watchdog_alerts.json shows repeated "Buffer schedule FAILED".
6. Buffer MCP 429 response lists rateLimit buckets; a bucket with remaining 0 and resetSeconds in the hundreds of thousands (~8 days) will not clear by waiting 5 min. Queue check via `buffer_dual_account.py check tales_untold` fails too.
7. Fallbacks to offer (need user decision): re-auth ~/.config/youtube_credentials.json (invalid_grant; youtube_oauth_device.py needs user approval code); composio execute YOUTUBE_UPLOAD_VIDEO --account youtube_trader-relink --file <mp4> may hit daily upload quota 429.
8. Avoid `find /home/herby` (exceeds 180s); look in ~/.hermes/scripts directly.
