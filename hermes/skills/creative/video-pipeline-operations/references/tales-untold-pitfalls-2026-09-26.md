# Tales Untold Shorts — Verified Pitfalls & Corrections

## Voice: Ezekiel, Not Adam

- **The brand voice for Tales Untold is Ezekiel.** Adam was incorrectly hardcoded into multiple pipeline files (`pipeline.py`, `process_queue.py`, `pilot_builder.py`, `pilot_builder_v2.py`, `run_pipeline.py`, `generate_pilot.sh`) and the spielberg skill reference.
- **Discovery:** User caught this during review of produced shorts on 2026-09-26.
- **Verification**: After TTS generation, verify via audio fingerprint — POYO does NOT error on a bad voice ID; it silently falls back. A voice swap must be verified via MD5 + duration + band RMS.

## Video Hosting: Use litterbox.catbox.moe for Buffer

Buffer **cannot read Google Drive URLs** for videos. It receives a virus-scan confirmation redirect and fails with:
```
"Video could not be read from its URL", httpCode=400
```

**Working host:** `litterbox.catbox.moe` (NOT `catbox.moe` directly):
```bash
curl -s -F "reqtype=fileupload" -F "time=1h" \
  -F "fileToUpload=@FINAL_VIDEO.mp4" \
  https://litterbox.catbox.moe/resources/internals/api.php
```
Returns: `https://litter.catbox.moe/XXXXXX.mp4`

**BunnyCDN:** Failed in session with `401 Unauthorized` on both configured storage zones (`tales-untold` and `tales-untold-longform`). Do not rely on BunnyCDN for Buffer posting without prior verification.

## Cron Scheduling: 3-Time-Slot Pattern

**Problem:** Single cron job running at `0 8,12,16 * * *` with time-detection logic inside the prompt consistently schedules ALL posts at 22:00 UTC (6pm ET), missing 23:00 UTC (7pm) and 00:00+1 UTC (8pm) slots.

**Root cause:** Agent fails to correctly detect which cron run triggered it. Multiple observed failures:
- Sep 26: All 6 scheduled posts were at 22:00 UTC only
- Sep 24: 2 of 3 posts went to correct slots; 7pm slot empty

**Fix:** Replace single cron with 3 separate cron jobs:
| Cron Job | Trigger Time (ET) | Target Post Time (UTC) |
|----------|-------------------|----------------------|
| spielberg-6pm-slot | 0 8 * * * | 22:00 UTC |
| spielberg-7pm-slot | 0 12 * * * | 23:00 UTC |
| spielberg-8pm-slot | 0 16 * * * | 00:00+1 UTC |

Each job has its target time hardcoded in the prompt. No runtime detection needed.

## POYO API Key Shell-Truncation Bug

Passing `$POYO_API_KEY` via shell interpolation in `curl` truncates the key to ~13 characters, causing:
```
Invalid API key format
```

**Fix:** Use Python `subprocess` with `env=` dict:
```python
import subprocess, os
subprocess.run([...], env={"POYO_API_KEY": api_key})
```

Or read the key in Python and pass directly via requests library. Never pass sensitive keys through bash variable interpolation.
