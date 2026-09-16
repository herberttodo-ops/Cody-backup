# Buffer YouTube Publishing — Working Pattern

Verified 2026-09-15 with the Tales Untold YouTube channel.

## Account Details
- **Account:** `apxherbert@gmail.com`
- **Organization ID:** `6aa9a1ead___ID___f`
- **YouTube Channel ID:** `6aa9a22eea19ca0bde4e0e84`
- **Auth Token:** `___LONG_STRING___`

## Step 1: Upload Video to Temporary Hosting

Use **litterbox.catbox.moe** (not catbox.moe directly). The `time` parameter is required.

```bash
curl -s -F "reqtype=fileupload" \
  -F "time=1h" \
  -F "fileToUpload=@output/FINAL_VIDEO.mp4" \
  https://litterbox.catbox.moe/resources/internals/api.php
```

Returns: `https://litter.catbox.moe/XXXXXX.mp4`

**Why litterbox, not catbox:**
- `catbox.moe/user/api.php` → uploads succeed, but Buffer's servers cannot read the file from the returned URL ("Video could not be read from its URL")
- `litterbox.catbox.moe/resources/internals/api.php` → uploads succeed AND Buffer can ingest the file

## Step 2: Publish via Buffer MCP (Direct curl)

The Hermes MCP client caches the first authenticated account. If you swap API keys in `~/.hermes/config.yaml`, the built-in tools may still return the old account data. Use direct curl to the MCP endpoint to force the correct auth.

```bash
curl -s -X POST https://mcp.buffer.com/mcp \
  -H "Authorization: Bearer $BUFFER_API_KEY" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "create_post",
      "arguments": {
        "channelId": "6aa9a22eea19ca0bde4e0e84",
        "text": "TITLE | Tales Untold — HOOK #shorts #horror",
        "assets": [{"video": {"url": "https://litter.catbox.moe/XXXXXX.mp4", "metadata": {"title": "TITLE | Tales Untold"}}}],
        "metadata": {
          "youtube": {
            "title": "TITLE | Tales Untold",
            "categoryId": "24",
            "privacy": "public",
            "madeForKids": false
          }
        },
        "mode": "shareNow",
        "schedulingType": "automatic"
      }
    }
  }'
```

## Key Parameters

| Parameter | Value | Notes |
|-----------|-------|-------|
| `mode` | `"shareNow"` | Publishes immediately |
| `schedulingType` | `"automatic"` | Required — `"notification"` fails with mobile device error |
| `privacy` | `"public"` / `"unlisted"` | Use `"unlisted"` for testing |
| `categoryId` | `"24"` | Entertainment category |
| `madeForKids` | `false` | Required boolean |

## Response Shape (Success)

```json
{
  "status": "sent",
  "sentAt": "2026-09-16T01:12:22.934Z",
  "error": null,
  "assets": [{
    "type": "video",
    "mimeType": "video/mp4",
    "source": "https://litter.catbox.moe/XXXXXX.mp4",
    "thumbnail": "https://images.buffer.com/thumbnail/..."
  }]
}
```

## Common Failures

| Error | Cause | Fix |
|-------|-------|-----|
| `"Video could not be read from its URL"` | Used catbox.moe (not litterbox) or URL expired | Use `litterbox.catbox.moe` with `time=1h` |
| `"Whoops! We are having trouble sending notifications to your mobile device"` | `schedulingType: "notification"` | Use `"automatic"` |
| Wrong account returned by MCP tools | Auth cached to first account | Use direct curl to MCP endpoint, or restart Hermes |
| `"YouTube posts require a video"` | Missing `assets` array or wrong asset shape | Include `[{"video": {"url": "...", "metadata": {"title": "..."}}}]` |
