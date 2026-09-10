# Buffer MCP + Cron Job Limitations

## The Problem

MCP tools (like Buffer) are discovered at runtime and are **NOT available in isolated cron contexts**. 

If you attempt to create a cron job that uses MCP tools:
```yaml
# This will FAIL
- name: daily-buffer-post
  schedule: "0 8 * * *"
  prompt: "Create a post using mcp__buffer__create_post..."  # ❌ MCP not available in cron
```

## Why It Fails

Cron jobs run in isolated contexts where:
- MCP server connections aren't established
- Tool discovery doesn't happen
- `mcp__*` prefixed tools are undefined

## Workarounds

### Option 1: Pre-schedule in Buffer (Recommended)
Create posts directly in Buffer's queue using `customScheduled` mode:
```python
# Batch create all posts at once
for day in range(1, 24):
    mcp__buffer__create_post(
        channelId="...",
        dueAt=f"2026-08-{day:02d}T08:00:00-04:00",
        mode="customScheduled",
        # ...
    )
```
Buffer will auto-publish when scheduled time arrives.

### Option 2: Use Buffer REST API Directly
Create a script that calls Buffer's REST API (not MCP):
```python
import requests

# Direct API call, no MCP needed
response = requests.post(
    "https://api.bufferapp.com/1/updates/create.json",
    data={
        "access_token": token,
        "profile_ids[]": profile_id,
        "text": content,
        "scheduled_at": timestamp
    }
)
```

### Option 3: Manual Daily Execution
User runs a command daily: "Post today's OptiRFP content"

## Content Guidelines for Andrew

When creating OptiRFP posts:
- Use **business page copy only** (formal "we" perspective)
- Do NOT paraphrase - use copy exactly as generated
- Include image with descriptive alt text
- Schedule for 8 AM EST
- Check Buffer's 10-post scheduled limit
