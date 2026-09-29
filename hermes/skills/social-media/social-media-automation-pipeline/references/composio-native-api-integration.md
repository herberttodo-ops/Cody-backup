# Composio Native API Integration

Session: LotSignal social automation build (September 28, 2026)

## Installation & Auth

```bash
# Install CLI
curl -fsSL https://composio.dev/install | sh

# Login (opens browser)
~/.composio/composio login

# After browser auth completes:
~/.composio/composio login --poll
```

## Platform Connection Status

| Platform | Status | Action | Notes |
|----------|--------|--------|-------|
| LinkedIn | ✅ ACTIVE | `composio link linkedin` | Ready for posting |
| Instagram | ✅ ACTIVE | `composio link instagram` | Business account required |
| Facebook | ✅ ACTIVE | `composio link facebook` | Page admin required |
| YouTube | ✅ ACTIVE | `composio link youtube` | Channel owner required |
| X/Twitter | ❌ BLOCKED | N/A | Requires paid API Basic tier ($100/mo) |
| TikTok | ❌ BLOCKED | N/A | Requires business dev approval |

Check status: `~/.composio/composio connections list`

## Python Integration

```python
from composio import ComposioToolSet

toolset = ComposioToolSet()

# Platform action mapping
ACTION_MAP = {
    "linkedin": "LINKEDIN_CREATE_LINKED_IN_POST",
    "instagram": "INSTAGRAM_POST_IG_USER_MEDIA",
    "facebook": "FACEBOOK_POST_TO_FEED",
    "youtube": "YOUTUBE_UPLOAD_VIDEO",
}

result = toolset.execute_action(
    action=ACTION_MAP["linkedin"],
    params={"text": post_text, "media_url": image_url}
)

# Returns: {"post_id": "...", "url": "..."}
```

## Cron Environment Setup

When running from cron, ensure PATH and config dir:

```bash
#!/bin/bash
export PATH="$HOME/.composio:$HOME/.local/bin:$PATH"
export COMPOSIO_CONFIG_DIR="$HOME/.composio"
```

## Logo Compositing Pitfall

The brand logo file must be the **full logo with wordmark**, not icon-only.

**Wrong:** `optirfp_icon.png` (feather + "O" only, missing "ptiRFP" text)  
**Right:** `optirfp_logo.jpg` (feather + full "OptiRFP" text)

**White background transparency:**
```python
data = logo.getdata()
newData = [(255, 255, 255, 0) if p[0] > 240 and p[1] > 240 and p[2] > 240 else p 
           for p in data]
logo.putdata(newData)
```

**Sizing for wide logos (3.7:1 aspect ratio):**
```python
# Target 30% image width for wide logos
target_width = int(img.width * 0.30)
aspect = logo.width / logo.height
logo = logo.resize((target_width, int(target_width / aspect)), 
                  Image.Resampling.LANCZOS)
```

## Pipeline Cron Schedule

| Job | Schedule | Purpose |
|-----|----------|---------|
| daily-pipeline | 8:00 AM | Generate draft → compliance → Telegram notify |
| publisher-6pm | 6:00 PM | Publish LinkedIn queue |
| publisher-7pm | 7:00 PM | Publish Instagram/Facebook |
| publisher-8pm | 8:00 PM | Publish YouTube |

## Approval Flow

1. Telegram DM with draft preview arrives
2. User replies: `✅` (approve), `❌` (reject), or `✏️ [text]` (edit)
3. Script updates `meta.json` status to `approved`
4. Draft added to `publish/queue.json`
5. Publisher cron picks up at scheduled time, posts via Composio

## Compliance Engine Learning

**Dollar/percentage regex issue:**  
Do NOT use `r"\$\d+\b"` or `r"\b\d+%\b"` for automotive content. Stats like "$500/month carrying cost" and "40% faster" are legitimate content, not prohibited offers. Only flag financing terms (`APR`, `cash back`, `down payment`).

## Free Tier Limits

Composio free: 100,000 tool calls/month.  
Typical usage: ~1,000-2,000 calls/month for daily posting + analytics harvest.  
Well within free tier for single-brand operations.
