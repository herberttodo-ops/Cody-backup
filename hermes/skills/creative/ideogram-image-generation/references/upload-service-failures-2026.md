# Upload Service Failure Log (Sept 2026)

**Date:** September 8, 2026  
**Context:** Attempting to upload generated images for Buffer MCP posting

## Service Status

| Service | Status | Error | Workaround |
|---------|--------|-------|------------|
| catbox.moe | ❌ Failing | HTTP 500 Internal Server Error | None - use manual upload |
| transfer.sh | ❌ Failing | Connection refused | None - use manual upload |
| file.io | ❌ Failing | HTTP 301 Moved Permanently | None - use manual upload |
| 0x0.st | ❌ Disabled | "uploads disabled because it's been almost nothing but AI botnet spam" | None - use manual upload |

## catbox.moe Specific Error

**Previous Status:** Working with `time=1h` parameter (documented Sept 2026)  
**Current Status:** Returns HTML error page with HTTP 500

```html
<!doctype html>
<title>500 | Internal Server Error</title>
...
<h1 class="error-code">500</h1>
<p class="error-description"><span>Internal Server Error</span></p>
```

The error comes from BunkerWeb WAF protection, not catbox.moe itself.

## Recommended Pattern

**For cron jobs, SKIP upload attempts entirely.**

```python
workflow:
  1. generate:
     tool: create_branded_social_graphic
     # OR use ideogram_logo_compositor.py script
  
  2. verify:
     tool: vision_analyze
     # Confirm quality >= 9/10
  
  3. output:
     # Provide manual upload package
     - Image path: ~/.hermes/generated_images/
     - Post copy
     - Hashtags
```

## Historical Context

These services were previously used for temporary image hosting:
- catbox.moe was the last reliable option (worked Sept 2026)
- All have now become unreliable for automated workflows
- Manual upload to Buffer web UI is the only reliable path

## Related

- `references/buffer-mcp-image-upload.md` - Historical upload patterns
- `references/successful-cron-workflow.md` - Complete cron workflow with manual fallback
