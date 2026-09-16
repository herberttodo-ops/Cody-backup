# Buffer YouTube Publishing for Tales Untold

## Account Separation (CRITICAL)

Tales Untold uses a **separate Buffer account** from OptiRFP.

| Account | Email | Channels | Key Storage |
|---------|-------|----------|-------------|
| **OptiRFP** | `optirfp@gmail.com` | LinkedIn, Facebook | `~/.hermes/config.yaml` (MCP default) |
| **Tales Untold** | `apxherbert@gmail.com` | YouTube | `~/.openclaw/workspace/tales-untold/.env` |

### Tales Untold Account Details
| Field | Value |
|-------|-------|
| Email | `apxherbert@gmail.com` |
| Account ID | `6aa9a1ead___ID___d` |
| Org ID | `6aa9a1ead___ID___f` |
| Org Name | My organization |
| YouTube Channel Name | Tales Untold |
| YouTube Channel ID | `6aa9a22eea19ca0bde4e0e84` |

## MCP Auth Caching Issue (2026-09-15)

**Problem:** The Hermes MCP client caches the **first** Buffer account it connects to. Swapping keys in `config.yaml` does NOT change accounts — the MCP server returns stale data.

**Fix:** Use **direct curl** to the MCP endpoint with the correct token:

```bash
curl -s -X POST https://mcp.buffer.com/mcp \
  -H "Authorization: bearer ___TOKEN___" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "list_channels",
      "arguments": {"organizationId": "6aa9a1ead___ID___f"}
    }
  }' | python3 -m json.tool
```

## YouTube Post Requirements

| Field | Type | Notes |
|-------|------|-------|
| `channelId` | string | `6aa9a22eea19ca0bde4e0e84` |
| `text` | string | Description |
| `assets` | array | Must contain `video` with public URL |
| `metadata.youtube.title` | string | Max 100 chars |
| `metadata.youtube.categoryId` | string | `24` = Entertainment |
| `metadata.youtube.privacy` | enum | `public`, `private`, `unlisted` |
| `metadata.youtube.madeForKids` | bool | `false` for horror |
| `metadata.youtube.isAiGenerated` | bool | `true` — YouTube mandates disclosure |

### Category IDs
- Film & Animation: `1`
- Entertainment: `24`
- Science & Technology: `28`

## Video URL Problem (CRITICAL)

Buffer must **directly download** the video. Google Drive links do **NOT** work.

| Source | Works? | Notes |
|--------|--------|-------|
| Google Drive | ❌ HTML redirect page |
| GitHub raw | ✅ If <100MB, public |
| AWS S3 pre-signed | ✅ Best for production |
| ngrok tunnel | ✅ Temporary, needs authtoken |
| localhost | ❌ Buffer servers can't reach |

### URL Test
```bash
curl -sI "https://URL" | grep -i "content-type"
# Expected: video/mp4
```

## Current Status
- YouTube channel: Connected ✅
- Account verified: `apxherbert@gmail.com` ✅
- Video publishing: ❌ Blocked — need public video URL

## Token
- Active: `___LONG_STRING___`
- Store in: `~/.openclaw/workspace/tales-untold/.env`

## Automation Options

**A: Google Drive + Manual** — Agent uploads to Drive, user creates Buffer post
**B: ngrok Tunnel** — Briefly expose local file for Buffer to pull
**C: S3 / Static Host** — Permanent public URL for videos
**D: YouTube Data API** — Upload directly to YouTube, bypass Buffer entirely
