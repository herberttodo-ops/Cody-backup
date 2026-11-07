# Tales Untold missed-slot triage (Nov 6 2026)

Trigger: "confirm today's posts will go out" / watchdog "Buffer schedule FAILED". Verify, do not assume.

## Checklist (in order)
1. `data/arm_schedule.json` has today's 3 keys (18/19/20:00). `data/arm_log.json` last entries: status scheduled vs failed.
2. Check for `output/FINAL_<name>_<date>.mp4`. No file = not produced, whatever the cron said.
3. Read `logs/pipeline_<date>_*.log` tail. Cron summaries can say "ok" while the pipeline failed.
4. Word count of `queue/<name>.txt` (must be 100-135). Duration gate: whisper end + 3s >= 38s.
5. Verify the schedule landed: Buffer queue OR YouTube `status.publishAt` (see below). A "PIPELINE COMPLETE" log is NOT proof.

## Failure modes found
- **Short stories (65-75 words)**: generator `~/.hermes/scripts/tale_arm_schedule_refill.py` (9am cron, script job 82dfb9b234c0) had its own 5 short templates. Fixed by importing TEMPLATES from `tales-untold/arm_schedule_refill.py` (100-111 words). After any template change, audit `wc -w queue/*.txt` for the next 7 days.
- **Buffer 429 "Too many requests"**: response includes a `rateLimit` array with `resetSeconds` per bucket; one bucket at remaining 0 with resetSeconds ~719000 (~8 days) means waiting is pointless. pipeline_v3 only logged a warning ("Buffer output unclear") and still wrote "PIPELINE COMPLETE" and marked status scheduled. This was the real cause of watchdog alerts on Nov 2, 4, 5.
- **YouTube OAuth `invalid_grant`** on `~/.config/youtube_credentials.json`: re-auth with `~/.hermes/scripts/youtube_oauth_device.py` (run in background, print the code to the user, user approves at google.com/device on the Tales Untold account). Google returns `verification_url` not `verification_uri`; the script is patched to accept both. Credentials only carry the `youtube.upload` scope, so `videos().list` returns 403; verify through Composio instead.
- **Composio YOUTUBE_UPLOAD_VIDEO daily quota 429** is separate from the OAuth upload path, which still worked the same day.

## Working direct-upload fallback (verified)
```
python3 -W ignore ~/.hermes/scripts/youtube_upload_oauth.py <mp4> "<title>" "<desc>" --publish-at 2026-11-06T23:00:00Z
```
Uploads private with `publishAt` = slot time in UTC (6pm ET = 23:00Z in Nov). Verify:
`composio execute YOUTUBE_GET_VIDEO_DETAILS_BATCH --account youtube_trader-relink -d '{"id":["<id>"],"parts":["status"]}'` (key is `parts`, not `part`); expect privacyStatus private, publishAt set, uploadStatus processed.

pipeline_v3.py phase 9 now falls back to this automatically when Buffer errors or is unconfirmed, and raises if both fail (backup: pipeline_v3.py.bak_20261106). The fallback's first in-pipeline run was still pending when this note was written; confirm it on the next cron result.

## Misc
- Foreground shell refuses nohup/setsid wrappers: use terminal(background=true, notify_on_complete=true).
- Searching `/home/herby` with find times out; scripts live in `~/.hermes/scripts/`.
- Watchdog `tales_watchdog.py` greps pipeline logs for "Buffer schedule confirmed" / "Buffer exit code: 0"; it will flag direct-YouTube-scheduled slots as failed unless updated to also accept "scheduled via direct YouTube upload".
