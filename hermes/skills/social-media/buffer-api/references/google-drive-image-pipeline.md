# Buffer MCP Image Hosting Pipeline

**Date:** September 13, 2026
**Session:** OptiRFP Buffer post repair — 6 dead catbox.moe URLs needed replacement

## Summary

Buffer requires publicly accessible, persistent HTTPS URLs for images. Local paths and temporary image hosts fail after days or weeks. This reference documents the working Google Drive pipeline and pitfalls discovered.

## Verified Image Hosts for Buffer

| Host | Status | Notes |
|------|--------|-------|
| **Google Drive (`uc?export=view&id=`)** | ✅ Working | Permanent if file stays shared. Verified Aug-Sep 2026 |
| `files.catbox.moe` | ❌ Dead | Returns HTML error pages after 30-90 days |
| `litter.catbox.moe` | ❌ Dead | Same as above |
| `ideogram.ai/api/images/ephemeral/` | ❌ Expiring | Signed URLs with explicit `exp=` timestamps |
| `transfer.sh` | ❌ Temporary | Short-lived by design |
| Local file paths | ❌ Fails | Buffer cannot access `/home/herby/...` |

## Google Drive Pipeline

### 1. Upload Script

Use the auto-upload script in the workspace:

```python
import sys
sys.path.insert(0, '/home/herby/.openclaw/workspace/scripts')
from auto_upload_to_drive import upload_image

url = upload_image("/path/to/image.png")
# Returns: https://drive.google.com/uc?export=view&id=FILE_ID
```

### 2. Manual Bulk Upload

For batch uploading many images:

```bash
cd ~/.hermes/skills/productivity/google-workspace/scripts
python3 upload_images_to_drive.py --source-dir ~/.hermes/generated_images/ --folder-id YOUR_FOLDER_ID
```

### 3. Drive Sharing Requirements

The Drive folder AND each file must be:
- Shared with "Anyone with the link" as **Viewer**
- The folder ID used in parent queries

**Verify sharing programmatically:**
```python
from google_api import build_service
service = build_service('drive', 'v3')
permissions = service.permissions().list(
    fileId='FILE_ID',
    fields='permissions(id, type, role)'
).execute()
# Should show: {'id': 'anyoneWithLink', 'type': 'anyone', 'role': 'reader'}
```

### 4. Correct URL Format

```
https://drive.google.com/uc?export=view&id=YOUR_FILE_ID
```

**Wrong formats that fail:**
- `https://drive.google.com/file/d/ID/view` — HTML page, not direct image
- `https://drive.usercontent.google.com/download?id=ID` — Works for curl but Buffer rejects
- `https://lh3.googleusercontent.com/d/ID` — 404 for Drive files

## Key Discovery: edit_post Cannot Add Images

**Critical finding from September 2026 session:**

Buffer's `edit_post` MCP tool **silently ignores asset changes**. Once a post is created text-only, it is permanently text-only through the API.

**Evidence:**
- `edit_post` with `assets` array returns success but assets stay empty
- Multiple URL formats tested (drive.google.com, drive.usercontent.google.com)
- 10+ attempts across 4 posts confirmed the pattern

**Implication:**
If an image URL expires (catbox.moe, ephemeral URLs), the ONLY fix is:
1. Delete the broken post with `delete_post`
2. Create a new post with `create_post` including the correct `assets` from the start

## Buffer MCP Server Cooldown

After heavy batch operations:
- 3-5 failures → ~50 second cooldown
- 10+ deletions → 3-4 minute cooldown
- Server returns: `MCP server 'buffer' is unreachable after N consecutive failures`

**Recovery strategy:**
- Save content locally before starting batches
- If server goes down, wait then verify remaining work with `list_posts`
- Never assume a `create_post` succeeded until you see it in the queue

## Future-Proofing Checklist

When creating Buffer posts with images:
- [ ] Image uploaded to Google Drive with public access
- [ ] URL uses `uc?export=view&id=` format
- [ ] URL tested with `curl | file` returning "PNG image data"
- [ ] Post created with `assets` in the initial `create_post` call
- [ ] Never rely on `edit_post` to fix broken image URLs later
