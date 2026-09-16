# Image Upload Methods & Cron Patterns (2026-09-15)

## Image Upload — Battle Tested

| Method | Status | Command / Pattern |
|--------|--------|-------------------|
| **catbox.moe** | ✅ Working | `curl -s -F "reqtype=fileupload" -F "time=1h" -F "fileToUpload=@img.png" https://litterbox.catbox.moe/resources/internals/api.php` → `https://litter.catbox.moe/XXXXXX.png` |
| Google Drive image URL | ⚠️ LinkedIn previews break | Use for VIDEO review only. For Buffer posts, LinkedIn doesn't render Drive hotlinks properly. |
| file:// URL | ❌ Fails | Buffer requires public HTTPS URL. |
| imgbb / freeimage | ❌ Not configured | Require dedicated API keys. |
| 0x0.st | ❌ Disabled | Message: "Uploads disabled — almost nothing but AI botnet spam" (still true 2026-09). |

**catbox.moe notes:**
- URLs expire in exactly 1 hour (the `time=1h` parameter).
- Buffer `addToQueue` mode processes immediately — safe.
- Buffer `customScheduled` >1 hour ahead risks 404 when Buffer fetches image.
- If Buffer queue is slow or delayed, re-upload before the scheduled slot.

## Cron Job Creation — Hermes CLI Only

**NEVER use the `cronjob` Python tool.** It fails with `schedule is required` every time due to parameter field ordering in the runtime. This was confirmed across 20+ attempts in this session.

**Use the Hermes CLI instead:**
```bash
hermes cron create "0 9 * * *" \
  "Self-contained prompt describing the workflow..." \
  --name "optirfp-linkedin-auto" \
  --workdir "/home/herby/.openclaw/workspace"
```

**Auto-post pipeline validated 2026-09-15:**
1. `python3 ~/.hermes/scripts/optirfp_autopost.py "Headline" topic`
2. Script generates image with Ideogram + logo, uploads to catbox, returns JSON
3. Extract `image_url` from JSON
4. `mcp__buffer__create_post(channelId=OPTIRFP_LINKEDIN, text=..., assets=[image_url], mode="addToQueue", schedulingType="automatic")`

**OptiRFP LinkedIn channel ID:** `6a7f74bcb2d9d577437af9a4`

**Buffer rate limits observed:**
| Window | Limit | Typical Remaining |
|--------|-------|-------------------|
| 15 min | 100 | ~99 |
| 24 hours | 250 | ~243 |
| 30 days | 3000 | ~2991 |

## Google Drive Video Upload (Working)

For Tales Untold / video review workflows:
```python
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

service = build('drive', 'v3', credentials=creds)
# Create folder "Tales Untold" (if missing)
# Upload with MediaFileUpload(..., resumable=True)
# Set permissions: type='anyone', role='reader'
# Get webViewLink for human review
```

**Prerequisites:**
- `~/.hermes/google_token.json` with `https://www.googleapis.com/auth/drive` scope
- `googleapi` dependencies in `~/.hermes/google_venv/bin/python`

**Known working:** 85MB MP4 files upload successfully via resumable upload.
