# MCP Server Auth Caching & Account Separation

## Discovery Date
2026-09-15

## Problem
The Hermes MCP client caches the **first** Buffer account it authenticates with. Swapping the `Authorization: Bearer` token in `~/.hermes/config.yaml` does **NOT** switch to a different account — the MCP server continues returning the originally cached account data.

## Symptoms
- `mcp__buffer__get_account` returns the wrong account even after changing the token
- `list_channels` returns OptiRFP channels (LinkedIn/Facebook) instead of Tales Untold (YouTube)
- Direct curl to the MCP endpoint with the new token works correctly

## Accounts Involved
| Account | Email | Key | Connected Channels |
|---------|-------|-----|-------------------|
| OptiRFP | `optirfp@gmail.com` | `___LONG_STRING___` | LinkedIn, Facebook |
| Tales Untold | `apxherbert@gmail.com` | `___LONG_STRING___` | YouTube |

## Affected Commands
These commands return WRONG data when the MCP client is stuck on OptiRFP:
- `mcp__buffer__get_account` → returns `optirfp@gmail.com`
- `mcp__buffer__list_channels` → returns LinkedIn + Facebook
- `mcp__buffer__create_post` → would post to wrong channels

## Workaround: Direct MCP Calls via curl
Bypass Hermes' cached MCP client by calling the MCP endpoint directly:

```bash
# Test Tales Untold account directly
curl -s -X POST https://mcp.buffer.com/mcp \
  -H "Authorization: bearer ___TOKEN___" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_account",
      "arguments": {}
    }
  }' | python3 -m json.tool
```

This correctly returns `apxherbert@gmail.com` and the Tales Untold YouTube channel.

## Verified Tales Untold Account Details

| Field | Value |
|-------|-------|
| Account ID | `6aa9a1ead___ID___d` |
| Org ID | `6aa9a1ead___ID___f` |
| Org Name | My organization |
| YouTube Channel ID | `6aa9a22eea19ca0bde4e0e84` |
| YouTube Channel Name | Tales Untold |

## Posting to YouTube via Direct MCP

Since Hermes' built-in tools won't work for the Tales Untold account, use direct curl for the `create_post` call:

```bash
curl -s -X POST https://mcp.buffer.com/mcp \
  -H "Authorization: bearer ___TOKEN___" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
      "name": "create_post",
      "arguments": {
        "channelId": "6aa9a22eea19ca0bde4e0e84",
        "text": "Story description text",
        "assets": [{
          "video": {
            "url": "https://PUBLIC_URL_TO_VIDEO.mp4",
            "metadata": {"title": "Story Title | Tales Untold"}
          }
        }],
        "metadata": {
          "youtube": {
            "title": "Story Title | Tales Untold",
            "categoryId": "24",
            "privacy": "public",
            "madeForKids": false,
            "isAiGenerated": true,
            "notifySubscribers": true
          }
        },
        "mode": "shareNow",
        "schedulingType": "notification"
      }
    }
  }'
```

## Token Management

### Where to Store
- **OptiRFP key:** `~/.hermes/config.yaml` (MCP default)
- **Tales Untold key:** `~/.openclaw/workspace/tales-untold/.env` as `BUFFER_API_KEY=ftBYq3...`
- **Regenerate:** buffer.com → Settings → Account → API Access

### Valid Tokens (as of 2026-09-15)
| Token | Status | Account |
|-------|--------|---------|
| `aS1mez...XYEb` | Active | OptiRFP |
| `wqfJWu...yjZy` | Expired | — |
| `ftBYq3...IVOv` | Active | Tales Untold |

## Root Cause Hypothesis
The MCP server process maintains an authentication session/cache keyed to its own internal state, not per-request headers. Hermes opens a persistent connection to the MCP server during startup; changing the config file doesn't invalidate or recreate that connection. The MCP server likely uses the first token it sees to establish a session that persists across requests.

## Fix Status
**No known fix within agent's control.** Options:
1. **Use direct curl** for all Tales Untold operations (current workaround)
2. **Restart Hermes agent** to re-establish MCP connection with new token (untested)
3. **Use YouTube Data API directly** to bypass Buffer entirely

## When This Applies
- Multiple Buffer organizations on one machine
- When switching between personal and business Buffer accounts
- Any scenario where `list_channels` returns channels that don't match the expected account
