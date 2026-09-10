# Hermes Update: Post-Update Buffer MCP Recovery

Session: August 2026

## Problem

After Hermes update from v0.18.2 to v0.20.4, the Buffer MCP server became unreachable.

## Symptoms

```
MCP server 'buffer' is unreachable after 8 consecutive failures.
Auto-retry available in ~57s.
```

## Root Cause

The MCP server configuration in `~/.hermes/config.yaml` was reset or the token became invalid during the update process.

## Recovery Steps

### Step 1: Verify Current Config

Check `~/.hermes/config.yaml`:
```yaml
mcp_servers:
  buffer:
    url: https://mcp.buffer.com/mcp
    headers:
      Authorization: Bearer TOKEN_HERE
```

### Step 2: Get New Token if Needed

1. Go to https://publish.buffer.com/settings/api
2. Copy the Access Token
3. Update config.yaml with new token

### Step 3: Verify Connection

```python
mcp__buffer__get_account
```

Expected result:
```json
{
  "id": "6a7f74229bd9eca99cf9f775",
  "email": "optirfp@gmail.com",
  "organizations": [...]
}
```

### Step 4: Verify Channels

```python
mcp__buffer__list_channels(organizationId="YOUR_ORG_ID")
```

Expected channels:
- LinkedIn: `6a7f74bcb2d9d577437af9a4`
- Facebook: `6a7f7476b2d9d577437af67f`

### Step 5: Verify Existing Posts

```python
mcp__buffer__list_posts(status=["scheduled"])
```

## Post-Update Verification Checklist

- [ ] MCP config present in `~/.hermes/config.yaml`
- [ ] Buffer token valid and not expired
- [ ] `mcp__buffer__get_account` returns account info
- [ ] Channel IDs match expected values
- [ ] Existing scheduled posts intact
- [ ] Can create test post successfully

## Prevention

Before future Hermes updates:
1. Backup `~/.hermes/config.yaml`
2. Document current MCP tokens
3. Note organization and channel IDs
4. Export current post schedule

## Related Commands

**Check current scheduled posts:**
```python
mcp__buffer__list_posts(
    organizationId="YOUR_ORG_ID",
    status=["scheduled"]
)
```

**Delete duplicate posts:**
```python
mcp__buffer__delete_post(postId="POST_ID")
```

**Create test post:**
```python
mcp__buffer__create_post(
    channelId="TEST_CHANNEL_ID",
    text="Test post",
    mode="addToQueue"
)
```
