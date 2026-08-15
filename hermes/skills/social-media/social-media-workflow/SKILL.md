---
name: social-media-workflow
description: Unified workflow for multi-platform social media posting via Buffer MCP. Covers setup, scheduling, multi-channel publishing, and common error patterns.
version: 1.0.0
---

# Social Media Posting Workflow

Complete workflow for creating and publishing content to LinkedIn, Facebook, and other social platforms via Buffer MCP.

## Prerequisites

1. **Buffer account** with connected social profiles
2. **API Token** from https://publish.buffer.com/settings/api
3. **MCP configured** in `~/.hermes/config.yaml` (see buffer-api skill)

## Quick Start

### Step 1: Connect Profiles
```
mcp__buffer__get_account → get organization ID
mcp__buffer__list_channels → get channel IDs
```

Save these channel IDs for reuse.

### Step 2: Create Content
```
linkedin-content-system → generate post text
branded-social-graphics → generate image
```

### Step 3: Upload Image and Get URL
- Upload to Google Drive
- Get shareable link: `https://drive.google.com/uc?export=view&id=IMAGE_ID`

### Step 4: Schedule Posts

**LinkedIn:**
```json
{
  "channelId": "LINKEDIN_ID",
  "text": "Post content",
  "mode": "customScheduled",
  "dueAt": "2026-08-15T08:00:00-04:00",
  "assets": [{"image": {"url": "DRIVE_URL", "metadata": {"altText": "..."}}}],
  "metadata": {"linkedin": {"type": "post"}}
}
```

**Facebook (REQUIRES type):**
```json
{
  "channelId": "FACEBOOK_ID",
  "text": "Post content",
  "mode": "customScheduled",
  "dueAt": "2026-08-15T08:00:00-04:00",
  "assets": [{"image": {"url": "DRIVE_URL", "metadata": {"altText": "..."}}}],
  "metadata": {"facebook": {"type": "post"}}  // REQUIRED
}
```

## Multi-Channel Batch Publishing

For N days × M channels:

1. Create content schedule (days, topics, images)
2. Loop through each day:
   - Create LinkedIn post first
   - Create Facebook post second (same content, different channel ID)
3. Use `mode: "customScheduled"` with dates 24 hours apart

## Common Error Patterns

| Error | Cause | Solution |
|-------|-------|----------|
| `Facebook posts require a type` | Missing metadata.facebook.type | Add `"facebook": {"type": "post"}` |
| `Invalid image URL` | Drive URL format wrong | Use `uc?export=view&id=` format |
| `Channel not found` | Wrong channel ID | Re-fetch via list_channels |

## First Comments

**Limitation:** Buffer API cannot post first comments programmatically.

**Workaround:**
1. Schedule main post via Buffer
2. After posting (check via `list_posts`), get post ID
3. Use platform APIs directly to add first comment
4. OR add as second Buffer post with reply reference

## Daily Posting Template

```python
# Daily at 8am EST
scheduled_posts = [
    {
        "day": 1,
        "date": "2026-08-15T08:00:00-04:00",
        "text": "...",
        "image_id": "DRIVE_IMAGE_ID",
        "channels": ["linkedin", "facebook"]
    },
    # ... repeat for N days
]

for post in scheduled_posts:
    for channel in post["channels"]:
        create_post(channel_id[channel], post)
```

## Related Skills

- `buffer-api` — MCP setup and API details
- `linkedin-content-system` — Content creation with quality scoring
- `branded-social-graphics` — Image generation with brand consistency
