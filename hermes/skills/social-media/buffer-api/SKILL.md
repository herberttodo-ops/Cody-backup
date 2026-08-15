---
name: buffer-api
description: Post to LinkedIn and Facebook via Buffer API/MCP. Schedule posts, manage queue, and handle media uploads.
version: 1.0.1
---

# Buffer API Integration

Post to LinkedIn and Facebook pages via Buffer.

**Two methods:** REST API (legacy, deprecated Feb 2027) and MCP (modern, recommended).

## MCP Setup (Recommended)

Add to `~/.hermes/config.yaml`:

```yaml
mcp_servers:
  buffer:
    url: "https://mcp.buffer.com/mcp"
    headers:
      Authorization: "bearer ___TOKEN___"
```

Get token: https://publish.buffer.com/settings/api

See [references/mcp-setup.md](references/mcp-setup.md) for:
- Platform-specific metadata requirements
- Image URL formatting
- Scheduling format
- Error patterns and fixes

### Buffer Plan Limits

**Scheduled posts limit:** Most Buffer plans have a 10 scheduled post limit. If you hit this:
```
"Limit reached: Scheduled posts limit reached. You have 10 scheduled posts out of 10 allowed"
```

**Workarounds:**
1. Wait for posts to publish, then add more
2. Upgrade Buffer plan for higher limits
3. Post immediately (`shareNow` mode) instead of scheduling

## Legacy REST API Documentation
- https://buffer.com/developers/api
- Deprecation: February 1, 2027

## Required Environment Variables
- BUFFER_API_TOKEN - Your Buffer access token

## Base URL
```
https://api.bufferapp.com/1
```

## Common Endpoints

### Get Profiles
```
GET /profiles.json
```
Returns all connected social media profiles.

### Create Post (Add to Queue)
```
POST /updates/create.json
```

Parameters:
- profile_ids[] - Array of profile IDs to post to
- text - Post content
- media[photo] - Image URL (optional)
- scheduled_at - Unix timestamp for scheduling (optional)

### Get Queue
```
GET /profiles/{id}/updates/queued.json
```

### Get Sent Updates
```
GET /profiles/{id}/updates/sent.json
```

## Usage Examples

### List Profiles
```bash
curl -s "https://api.bufferapp.com/1/profiles.json?access_token=$BUFFER_API_TOKEN"
```

### Create Post
```bash
curl -s -X POST "https://api.bufferapp.com/1/updates/create.json" \
  -d "access_token=$BUFFER_API_TOKEN" \
  -d "profile_ids[]=PROFILE_ID" \
  -d "text=Hello from Buffer API" \
  -d "media[photo]=https://example.com/image.jpg"
```

### Schedule Post
```bash
curl -s -X POST "https://api.bufferapp.com/1/updates/create.json" \
  -d "access_token=$BUFFER_API_TOKEN" \
  -d "profile_ids[]=PROFILE_ID" \
  -d "text=Scheduled post" \
  -d "scheduled_at=___ID_NUMBER___"
```

## Rate Limits
- 100 requests per 60 seconds for most endpoints
- 10 media uploads per 60 seconds

## Response Format
All responses are JSON.