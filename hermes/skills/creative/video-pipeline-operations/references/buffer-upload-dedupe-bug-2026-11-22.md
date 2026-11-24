# Buffer-to-YouTube Duplicate Upload Bug — 2026-11-22

## Symptom
Videos scheduled through Buffer are also uploaded directly to YouTube, producing **two identical videos** published minutes apart. The duplicate degrades algorithm performance (splits impressions), wastes credits, and contaminates A/B test data.

Confirmed on Tales Untold channel (Nov 15-22): every video had a duplicate. Example:
- Dogman (Nov 22): `r7TVg6n-7Q0` (Buffer) + `_L9fKTLbf7w` (YouTube direct), 25s apart
- Nian (Nov 22): two copies, 21 min apart
- Asanbosam (Nov 19): two copies, 12s apart

## Root Cause
`pipeline_v3.py` line ~830 uses naive string matching on Buffer's JSON-RPC response text:

```python
_bl = buffer_result.lower()
_buffer_ok = bool(buffer_result) and ("error" not in _bl) and ("429" not in _bl) and ("too many requests" not in _bl)
```

Buffer's response **always** contains `"error": null` on success (it's part of every node object). The `"error" not in _bl` check is therefore **always False**, so the pipeline **always** falls through to the direct-YouTube-upload fallback — even when Buffer successfully queued the video.

## Why It Went Unnoticed
- Buffer MCP calls returned exit code 0
- Logs showed "Buffer exit code: 0" then "Buffer output unclear" (the output was JSON, not plain English)
- The fallback upload succeeded silently
- No pre-upload dedupe check existed ("already on YouTube?")

## Fix Approaches

### Option A: Parse Buffer Response Properly (Recommended)
Instead of string matching on raw response text, parse the JSON-RPC envelope:

```python
import json

def buffer_response_ok(buffer_result):
    """Check if Buffer JSON-RPC response indicates success."""
    try:
        data = json.loads(buffer_result)
        inner = json.loads(data["result"]["content"][0]["text"])
        # Check for actual error value (not "error": null)
        if inner.get("error") is not None:
            return False, f"Buffer error: {inner['error']}"
        # Check for data/edges presence
        if "data" not in inner and "result" not in inner:
            return False, "No data in Buffer response"
        return True, "Buffer confirmed"
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        return False, f"Could not parse Buffer response: {e}"

# Usage:
_buffer_ok, msg = buffer_response_ok(buffer_result)
if not _buffer_ok:
    logger.warning(f"Buffer not confirmed: {msg}. Falling back to YouTube direct upload.")
    # ... fallback code ...
```

### Option B: Pre-Upload YouTube Deduplication
Before ANY upload (Buffer or YouTube direct), check YouTube Data API for a video with the same title scheduled within the next 24 hours:

```python
# Query uploads playlist for pending/scheduled videos
def already_scheduled(title_prefix, window_hours=24):
    # Search YouTube uploads playlist for matching title + publishAt within window
    pass
```

### Option C: Fix the Naive Check (Minimal)
If keeping the string approach, check for `"error":null` vs an actual error:

```python
# Naive but functional: distinguish "error":null from error with a value
_buffer_ok = bool(buffer_result) and ('"error": null' in buffer_result or '"error":null' in buffer_result)
```
This is fragile — parsing (Option A) is strongly preferred.

## Prevention Patterns
1. **Never do semantic checks on stringified JSON.** Always parse to data structures.
2. **Never assume exit code 0 means success.** APIs return 200 with errors in body.
3. **Add a pre-upload gate.** Check the target platform (YouTube/Buffer) before uploading.
4. **Add a post-upload verification.** Query back from YouTube API to confirm `publishAt`/`privacyStatus`.
5. **Log both paths clearly.** The log should say "Buffer: SUCCESS, skipping fallback" when Buffer works, and "Buffer: FAILED, attempting fallback" only when it truly failed.

## Testing the Fix
After patching, verify:
1. Buffer response parses correctly (success case)
2. Buffer error response does NOT trigger fallback (genuine failure case)
3. Only one YouTube video exists per scheduled slot
4. `data/arm_log.json` `youtube_id` field is populated (not "N/A")
