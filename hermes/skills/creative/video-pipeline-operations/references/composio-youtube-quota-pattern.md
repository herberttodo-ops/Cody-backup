# ComposIO YouTube Publishing — Quota Exhaustion Pattern
**Session context:** Oct 4, 2026. Attempting immediate YouTube publish via ComposIO for Tales Untold shorts.

## What Works

| Component | Status |
|-----------|--------|
| ComposIO CLI auth | ✅ Active (`apxherbert@gmail.com`) |
| YouTube connection (Tales UnTold) | ✅ `ACTIVE` — `youtube_trader-relink` |
| YouTube connection (LotSignal) | ✅ `ACTIVE` — `youtube_chub-unshot` |
| Available tools | `YOUTUBE_MULTIPART_UPLOAD_VIDEO` (1600 API units), `YOUTUBE_UPLOAD_VIDEO` (500 API units) |
| Read-only tools (list/get) | `YOUTUBE_LIST_CHANNELS`, `YOUTUBE_GET_VIDEO_DETAILS_BATCH`, `YOUTUBE_LIST_USER_SUBSCRIPTIONS`, `YOUTUBE_LIST_CAPTION_TRACK` |
| Buffer MCP | ✅ Working for Tales Untold scheduling |

## What Blocked Us

**YouTube Data API v3 quota exhaustion.** Every YouTube tool call (even read-only `LIST_CHANNELS`, `GET_CHANNEL_ID_BY_HANDLE`) returned:

```json
{
  "error": {
    "code": 403,
    "message": "The request cannot be completed because you have exceeded your quota.",
    "errors": [{"domain": "youtube.quota", "reason": "quotaExceeded"}]
  }
}
```

This is a **Google project-level limit** (default new project: 10,000 units/day). ComposIO's connection to YouTube uses its own Google project or the user's project — either way, the quota was consumed.

## Recovery Path

1. **Wait for daily reset.** Quota resets at midnight Pacific Time (3:00 AM ET). No action needed.
2. **Request quota increase.** Via Google Cloud Console → APIs & Services → Quotas → YouTube Data API v3. Standard request form; typically approved for small channels within 48 hours for 100,000 units/day.
3. **Use resumable upload format.** `YOUTUBE_UPLOAD_VIDEO` costs ~500 API units vs ~1600 for `YOUTUBE_MULTIPART_UPLOAD_VIDEO`. Triples daily capacity. Already noted in `references/pipeline-resilience-oct2026.md`.

## When ComposIO Works for YouTube Publishing

| Condition | Recommendation |
|-----------|---------------|
| Quota available | Use `YOUTUBE_UPLOAD_VIDEO` (500 units) with FileUploadable or staged S3 file |
| Quota exhausted | Fall back to Buffer scheduling (separate auth/connection) |
| Immediate publish needed | Buffer with `dueAt = now + 2 minutes` (Buffer's own scheduling, not YouTube API) |
| Direct upload needed | Re-authorize YouTube OAuth via `youtube_oauth_setup.py` (bypasses ComposIO entirely) |

## Detecting Quota Exhaustion Proactively

Check before attempting uploads:
```bash
composio execute YOUTUBE_LIST_CHANNELS -d '{"mine": true}' --account youtube_trader-relink
```

If this lightweight read call returns `quotaExceeded`, DO NOT attempt upload. The error is permanent for the day.

## Buffer vs ComposIO for YouTube

| Aspect | Buffer MCP | ComposIO |
|--------|-----------|----------|
| Auth type | OAuth via Buffer's app | OAuth via ComposIO/Google |
| Quota impact | None (uses Buffer's backend) | Consumes YouTube Data API quota |
| Scheduling | Explicit `dueAt` or auto-queue | Immediate upload via `YOUTUBE_UPLOAD_VIDEO` |
| Reliability | High for scheduling | Depends on quota state |
| Best for | Scheduled posting | Direct immediate upload (when quota available) |
