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
| `MCP server unreachable` | Server overload after failures | Wait ~50s cooldown; save content locally for manual retry |
| `Invalid Bearer token` | Wrong header format | Use `Api-Key:` not `Authorization: Bearer` |
| `Invalid arguments: schedulingType` | Wrong value used | Use `"automatic"` or `"notification"`, not `"addToQueue"` |
| `Image could not be read` | Local file:// URL or placeholder | Must use publicly accessible HTTPS URL |

### Buffer MCP Server Reliability

**Pattern:** After 3-4 failed post attempts, server becomes unreachable.

**Symptoms:**
```
MCP server 'buffer' is unreachable after 3 consecutive failures.
Auto-retry available in ~50s.
```

**Workaround:**
1. Always save generated content locally first
2. Design workflows with graceful degradation
3. If Buffer fails, provide user with:
   - Image file path
   - Post copy text
   - Recommended hashtags
   - Instructions for manual upload

**Cron Environment Issues:**
- Third-party image upload services (transfer.sh, catbox.moe, imgur) often fail
- Save images locally to `~/.hermes/generated_images/`
- Use `file://` URLs only for local verification, not for Buffer posts
- Buffer requires publicly accessible HTTPS URLs for images

### Image Upload Alternatives

**Option 1: Google Drive (Recommended)**
```
https://drive.google.com/uc?export=view&id=YOUR_IMAGE_ID
```

**Option 2: Save locally + manual upload**
- Generate image
- Save to `~/.hermes/generated_images/`
- User uploads via Buffer web UI
- More reliable than automated upload services

**Option 3: Buffer native image upload**
- Use Buffer's built-in image upload via web interface
- Reference uploaded image by ID in API calls
- Most reliable but requires manual step

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
