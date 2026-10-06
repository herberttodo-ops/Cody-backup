# Buffer Google Drive URL Format Fix
**Date:** 2026-10-05
**Session:** Tales Untold 3-video production run
**Severity:** Publishing blocker — videos render successfully but Buffer refuses to schedule them

## The Problem

Buffer's `create_post` tool rejects Google Drive URLs in the format:
```
https://drive.google.com/uc?export=download&id=FILE_ID
```

Error returned:
```json
{"error":"Invalid post: Video could not be read from its URL.","httpCode":400}
```

This affects ALL videos uploaded via `upload_video_to_drive.py` prior to this fix.

## The Working Format

Use `drive.usercontent.google.com` with `confirm=t`:
```
https://drive.usercontent.google.com/download?id=FILE_ID&export=download&confirm=t
```

The `confirm=t` parameter bypasses Google's virus-scan HTML interstitial and returns `Content-Type: video/mp4`, which Buffer's ingest pipeline can read.

## Files Changed

| File | Change |
|------|--------|
| `~/.hermes/scripts/upload_video_to_drive.py` | Return URL now uses `drive.usercontent.google.com/download?id={file_id}&export=download&confirm=t` |

## Verification

After fix, Buffer `create_post` succeeds:
```json
{"id":"6ac43b71032d05299872ce59","status":"scheduled",...}
```

## Buffer MCP delete_post Behavior

Tool name: `delete_post` (snake_case, NOT `deletePost`)
Parameter: `postId` (camelCase, NOT `id`)

Working call:
```python
buffer_api_call("tales_untold", "delete_post", {"postId": "6ac2ab2dca1380ada834bfcf"})
```

NOT exposed via MCP (return -32602):
- `publishPostNow` / `publish_post_now`
- `updatePostSchedule` / `update_post_schedule`
- `movePostToDraft` / `move_post_to_draft`

**Implication:** Once a post is scheduled, its time CANNOT be changed via MCP. Time corrections require deleting and recreating the post.
