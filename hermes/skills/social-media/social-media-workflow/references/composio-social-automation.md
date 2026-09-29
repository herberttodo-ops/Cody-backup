# Composio-Based Social Media Automation

## Overview

Replace Buffer MCP with Composio for native API posting. Removes 10-post caps, enables analytics feedback loops.

## Architecture

```
SIGNALS → DRAFT → COMPLIANCE → APPROVAL → PUBLISH → ANALYTICS → LEARN
```

## Composio Setup

```bash
# Install CLI
curl -fsSL https://composio.dev/install | sh

# Login (browser auth required)
~/.composio/composio login
~/.composio/composio login --poll  # After browser approval

# Link platforms
~/.composio/composio link linkedin
~/.composio/composio link instagram
~/.composio/composio link facebook
~/.composio/composio link youtube

# Check status
~/.composio/composio connections list
```

## Platform Availability

| Platform | Composio Action | Status | Notes |
|----------|-----------------|--------|-------|
| LinkedIn | `LINKEDIN_CREATE_LINKED_IN_POST` | ✅ Ready | Personal + Company pages |
| Instagram | `INSTAGRAM_POST_IG_USER_MEDIA` | ✅ Ready | Requires media container first |
| Facebook | `FACEBOOK_POST_TO_FEED` | ✅ Ready | Pages + Profiles |
| YouTube | `YOUTUBE_UPLOAD_VIDEO` | ✅ Ready | Video uploads |
| X/Twitter | `TWITTER_CREATION_OF_A_POST` | ❌ Blocked | Requires paid API tier ($100/mo) |
| TikTok | `TIKTOK_UPLOAD_VIDEO` | ❌ Blocked | Business dev approval required |

## Python Integration

```python
from composio import ComposioToolSet

toolset = ComposioToolSet()

# Post to LinkedIn
result = toolset.execute_action(
    action="LINKEDIN_CREATE_LINKED_IN_POST",
    params={
        "text": "Your post content here",
        # Optional: "media_url": "https://cdn.example.com/image.png"
    }
)

# Returns: {"post_id": "...", "url": "https://linkedin.com/posts/..."}
```

## Pipeline Scripts

| Script | Purpose | Cron Schedule |
|--------|---------|---------------|
| `generate_draft.py` | Create content from rotation | Daily 8 AM |
| `run_compliance.py` | Brand voice + legal checks | After generation |
| `notify_approval.py` | Telegram DM to user | After compliance |
| `publish_queue.py` | Composio API posting | 6/7/8 PM ET |

## Key Files

```
~/.hermes/lotsignal-social/
├── brand/
│   ├── brand_voice.json        # Tone, vocab, prohibited terms
│   └── logo_assets/              # Full logos (not icon-only)
├── drafts/                       # Draft content by date
├── compliance/
│   ├── check_results/            # Compliance scores
│   └── guardrail_config.yaml     # Legal guardrails
├── publish/
│   ├── queue.json                # Approved posts waiting
│   ├── published_log.csv         # Success log
│   └── failed_log.csv            # Retry tracking
├── analytics/
│   └── performance.db            # SQLite analytics DB
└── scripts/
    ├── generate_draft.py
    ├── run_compliance.py
    ├── notify_approval.py
    └── publish_queue.py
```

## Lessons Learned

1. **Logo compositing**: Must use FULL logo file (icon + wordmark), position bottom RIGHT with fixed 150px margins (not percentage) to prevent social platform crop.

2. **Composio auth**: Browser-based OAuth for each platform. Connection shows `INITIATED` → browser auth → `ACTIVE`.

3. **Twitter/X & TikTok**: Platform restrictions, not Composio limitations. Require paid API tiers or business approvals.

4. **Free tier**: 100K tool calls/month on Composio free tier covers most use cases (1K-2K calls for daily posting + analytics).
