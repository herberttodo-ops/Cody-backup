# Upload Service Status - Sept 14, 2026

Last tested: September 14, 2026

## Status Summary

| Service | Status | Notes |
|---------|--------|-------|
| `transfer.sh` | ❌ Failing | Connection refused |
| `0x0.st` | ❌ Disabled | Uploads disabled due to spam |
| **catbox.moe** | ✅ **WORKING** | Returns public URLs successfully |
| `imgur` API | ❌ Unreliable | 503 errors, requires auth |
| `file.io` | ❌ Failing | 301 redirects, intermittent |
| **Google Drive** | ❌ **BROKEN** | Never use for Buffer image URLs |

## The September 13 Failure

The post on September 13 used: `https://drive.google.com/uc?export=view&id=18nlokVZ0Xyv7nB7EzbMFB7fXsDKkmQlY`

**Result:** "Does not look good"

**Why:** Google Drive URLs are NOT designed for hotlinking in social media posts. They cause:
- Broken LinkedIn image previews
- Permission/access issues
- Inconsistent rendering

## The ONLY Working Auto-Post Pattern

```
1. Ideogram V4 generates image + text
2. Logo compositing adds exact OptiRFP logo
3. catbox.moe upload → public URL (expires 1h)
4. Buffer MCP post with public URL
```

## Auto-Post Scripts

Two scripts exist for full automation:
- `scripts/optirfp_autopost.py` — Full pipeline: Ideogram → logo composite → catbox upload → output Buffer JSON
- `scripts/optirfp_post_generator.py` — Random content pool + calls autopost (use in cron jobs)

Run:
```bash
python3 ~/.hermes/scripts/optirfp_autopost.py "Your Headline" topic
```

## Cron Job Setup (CRITICAL: Use CLI, Not cronjob Tool)

Use `hermes cron create` CLI, NOT the `cronjob` tool:

```bash
hermes cron create "0 9 * * *" \
  "Run: python3 ~/.hermes/scripts/optirfp_post_generator.py" \
  --name "optirfp-linkedin-auto" \
  --workdir "/home/herby/.openclaw/workspace"
```

**Hard requirements:**
- Must use `hermes cron create` CLI — the `cronjob` tool requires a `schedule` property that is easy to forget (~18 failures in one proven session)
- `--workdir` points to the project directory
- NO `--no-agent` — agent mode is needed for MCP tools to post to Buffer
- Prompt should call the generator script, not inline the pipeline steps
- `hermes cron list` to verify after creation

## Catbox.moe Upload Command

```bash
curl -s -F "reqtype=fileupload" -F "time=1h" \
  -F "fileToUpload=@/path/to/image.png" \
  https://litterbox.catbox.moe/resources/internals/api.php
```

## Buffer MCP Post Template

```python
mcp__buffer__create_post(
    channelId="6a7f74bcb2d9d577437af9a4",
    text="Your headline\n\nBody text...\n\n#hashtags",
    assets=[{
        "image": {
            "url": "https://litter.catbox.moe/xxxxx.png",
            "metadata": {"altText": "OptiRFP branded graphic"}
        }
    }],
    schedulingType="automatic",
    mode="addToQueue"
)
```

## NEVER Use for Buffer Image URLs

- `file://` local paths → Buffer rejects
- `drive.google.com` URLs → Broken previews
- Any non-public URL → Validation fails
