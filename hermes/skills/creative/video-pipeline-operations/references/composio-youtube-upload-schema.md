# Composio YouTube Upload Schema — Verified Fix Log

## Problem (2026-09-30)
`YOUTUBE_MULTIPART_UPLOAD_VIDEO` failed with schema validation error:
```
"Input validation failed for YOUTUBE_MULTIPART_UPLOAD_VIDEO.
Schema: /home/herby/.composio/tool_definitions/YOUTUBE_MULTIPART_UPLOAD_VIDEO.json\n- <root>: Unknown property: publishAt"
```

## Root Cause
The tool only allows these parameters:
- `tags` (array of strings)
- `title` (string)
- `videoFile` (file path — passed via `--file` CLI flag)
- `categoryId` (string, not integer)
- `description` (string)
- `privacyStatus` (string: "public" | "private" | "unlisted")

`publishAt` is silently rejected. `categoryId` as integer `24` also fails; must be `"24"`.

## Verified Working Call (2026-09-30)
```python
import subprocess, json

cmd = [
    str(Path.home() / ".composio/composio"),
    "execute", "YOUTUBE_MULTIPART_UPLOAD_VIDEO",
    "-d", json.dumps({
        "title": title,
        "description": desc,
        "categoryId": "24",  # MUST be string "24", not int 24
        "privacyStatus": "private" if publish_at else "public",
        # "publishAt": ... ← DO NOT ADD. Tool rejects it silently.
    }),
    "--file", str(video_path),
    "--account", "youtube_trader-relink",
]
result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
```

## Alternative: Direct Video Upload
If multipart fails, use `YOUTUBE_UPLOAD_VIDEO` (resumable, ~500 API units vs ~1600):
```bash
~/.composio/composio execute YOUTUBE_UPLOAD_VIDEO \
  -d '{"title":"TITLE","description":"DESC","categoryId":"24","privacyStatus":"public","tags":["horror","shorts"]}' \
  --file FINAL.mp4 \
  --account youtube_trader-relink
```

## Account
- **Tales Untold channel:** `youtube_trader-relink`
- **Quota reset:** ~3am ET / midnight PT
- **Shared quota:** ~10,000 units/day across Composio's OAuth app

## Pitfall Checklist
- [ ] `categoryId` is string `"24"` — not integer `24`
- [ ] No `publishAt` in the data payload — schedule via cron or Buffer instead
- [ ] `"videoFile"` is NOT in the `-d` payload — pass actual file via `--file` flag
- [ ] `--account` points to correct stored auth (`youtube_trader-relink` for Tales)
- [ ] `"tags"` is array of strings: `["horror","shorts","folklore"]` not `"horror shorts"`

---
Last verified: 2026-09-30
