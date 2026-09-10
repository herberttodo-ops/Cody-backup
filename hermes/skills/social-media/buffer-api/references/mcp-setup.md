# Buffer MCP Setup and Usage Guide

## MCP Configuration

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  buffer:
    url: "https://mcp.buffer.com/mcp"
    headers:
      Authorization: "bearer ___TOKEN___"
```

Get your token from: https://publish.buffer.com/settings/api

## Required Metadata by Platform

### LinkedIn Posts
```json
{
  "metadata": {
    "linkedin": {
      "type": "post"
    }
  }
}
```

### Facebook Posts  
**REQUIRED** - will fail without this:
```json
{
  "metadata": {
    "facebook": {
      "type": "post"  // or "story" or "reel"
    }
  }
}
```

## Image URL Format

**Google Drive images:**
- Wrong: `https://drive.google.com/file/d/ID/view`
- Correct: `https://drive.google.com/uc?export=view&id=ID`

## Scheduling Format

ISO 8601 with timezone offset:
- Format: `YYYY-MM-DDTHH:MM:SS-04:00` (EST example)
- Buffer converts to UTC internally

## Multi-Channel Posting

Create separate posts for each channel:
1. First call: LinkedIn channel ID
2. Second call: Facebook channel ID  
3. Same text and image for both

## Complete Post Example

```json
{
  "channelId": "6a7f74bcb2d9d577437af9a4",
  "text": "Your post text here...",
  "assets": [{
    "image": {
      "url": "https://drive.google.com/uc?export=view&id=IMAGE_ID",
      "metadata": {
        "altText": "Image description"
      }
    }
  }],
  "mode": "customScheduled",
  "schedulingType": "automatic",
  "dueAt": "2026-08-15T08:00:00-04:00",
  "metadata": {
    "linkedin": {
      "type": "post"
    }
  }
}
```

## Common JSON Structure Mistake

❌ **WRONG** - Putting parameters inside assets array:
```json
{
  "assets": [{
    "image": { "url": "..." },
    "channelId": "...",  // WRONG - inside assets
    "dueAt": "..."       // WRONG - inside assets
  }]
}
```

✅ **CORRECT** - Parameters at top level:
```json
{
  "assets": [{
    "image": { "url": "..." }
  }],
  "channelId": "...",  // CORRECT - top level
  "dueAt": "...",        // CORRECT - top level
  "text": "...",
  "mode": "customScheduled"
}
```

## Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `Facebook posts require a type` | Missing metadata.facebook.type | Add metadata.facebook.type="post" |
| `Invalid post` | Wrong image URL format | Use uc?export=view format |
| `'Limit reached: Scheduled posts'` | Buffer 10-post limit | Wait or upgrade plan |
| `Invalid input: expected string, received undefined` | Parameters inside assets array | Move channelId, dueAt, etc. to top level, NOT inside assets |
| `Unrecognized keys` | Parameters misplaced | Ensure channelId, dueAt, metadata are at root level |

## Buffer Plan Limits

**Scheduled posts limit:** Most Buffer plans have a 10 scheduled post maximum.

**When limit is reached:**
```
"Limit reached: Scheduled posts limit reached. You have 10 scheduled posts out of 10 allowed."
```

**Workarounds:**
1. Wait for posts to publish (they auto-publish)
2. Check current queue with list_posts to see status
3. Use `shareNow` mode for immediate posting instead of scheduling
4. Upgrade Buffer plan for higher limits

## Creating Multiple Posts

**Batch workflow:**
1. Create posts one at a time (not parallel) to avoid rate limits
2. Check for `Limit reached` error after each post
3. Stop when limit is hit
4. Track successful posts in a file
5. Resume later when queue clears

**Post tracking:** Save post IDs to `~/.hermes/buffer_posts.json` to track what was scheduled.