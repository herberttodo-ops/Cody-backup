# Buffer MCP Post Creation Patterns

Discovered patterns from OptiRFP scheduling session (Aug 14, 2026).

## Working JSON Format

### LinkedIn Post (Scheduled)
```json
{
  "channelId": "6a7f74bcb2d9d577437af9a4",
  "text": "Hook line.\n\nBody paragraph here.\n\nTemplate is a starting point. Not a destination.\n\nSimple shift. Hard habit.",
  "mode": "customScheduled",
  "schedulingType": "automatic",
  "dueAt": "2026-08-15T08:00:00-04:00",
  "assets": [{
    "image": {
      "url": "https://drive.google.com/uc?export=view&id=IMAGE_ID",
      "metadata": {
        "altText": "Description here"
      }
    }
  }],
  "metadata": {
    "linkedin": {
      "type": "post"
    }
  }
}
```

### Facebook Post (Scheduled)
**CRITICAL:** Facebook REQUIRES the metadata field.

```json
{
  "channelId": "6a7f7476b2d9d577437af67f",
  "text": "Same content as LinkedIn",
  "mode": "customScheduled",
  "schedulingType": "automatic",
  "dueAt": "2026-08-15T08:00:00-04:00",
  "assets": [{
    "image": {
      "url": "https://drive.google.com/uc?export=view&id=IMAGE_ID",
      "metadata": {
        "altText": "Description"
      }
    }
  }],
  "metadata": {
    "facebook": {
      "type": "post"  // REQUIRED
    }
  }
}
```

## Image URL Formats

**Google Drive:**
- ❌ Fails: `https://drive.google.com/file/d/ID/view`
- ✅ Works: `https://drive.google.com/uc?export=view&id=ID`

## Scheduling Format

Buffer accepts multiple formats:
- ISO 8601 with timezone: `"2026-08-15T08:00:00-04:00"`
- Buffer converts to UTC internally
- Posts appear in buffer at requested local time

## Multi-Channel Workflow

For same content to multiple platforms:
1. Create LinkedIn post first
2. Create Facebook post second (same text/image)
3. Both will be scheduled independently in Buffer

## Error Recovery

**`Facebook posts require a type`:**
- Error code: 400
- Fix: Add `"metadata": {"facebook": {"type": "post"}}`

**`Invalid image URL`:**
- Check URL format (uc?export=view format)
- Verify image is publicly accessible

## Rate Limiting

Buffer MCP seems to have reasonable limits, but batch slowly:
- Wait 1-2 seconds between calls
- If rate limited, pause and retry

## Response Fields

Key fields in success response:
- `id`: Post ID (save this if you need to reference later)
- `status`: "scheduled" or "sending"
- `dueAt`: When it will post
- `channelService`: "linkedin" or "facebook"
