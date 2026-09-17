# Buffer YouTube Integration — Format Constraints & Workarounds

## Channel-Level Configuration Matters

Buffer YouTube channels are **not automatically compatible** with all video formats. A YouTube channel can be configured in Buffer as:

- **Shorts-only** → Requires **9:16 vertical** videos
- **Mixed** → Accepts both Shorts (9:16) and regular videos (16:9)
- **Long-form** → Requires **16:9 horizontal** videos

You **cannot override this via API parameters**. The channel configuration is set in Buffer's dashboard when the channel is connected.

## Detecting Shorts-Only Channels

If Buffer MCP returns:
```json
{
  "error": "Invalid post: Video must be vertical (portrait orientation) for YouTube Shorts.",
  "httpCode": 400
}
```

This confirms the channel is **Shorts-only**. The following methods **will NOT work**:
- Setting `isShorts: false` in metadata ❌
- Setting `shorts: false` in video metadata ❌  
- Using different aspect ratios ❌
- Any API parameter ❌

## Solutions for Long-Form Videos (16:9)

### Option 1: Add a Second YouTube Channel in Buffer

1. Go to Buffer dashboard → Channels → Add Channel
2. Connect the same YouTube channel but **configure it as "Videos"** (not Shorts)
3. Use the new channel ID for long-form uploads
4. Keep the original channel ID for YouTube Shorts

### Option 2: Direct YouTube Data API Upload

When Buffer is Shorts-only, fall back to YouTube's native API:

```python
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

# OAuth flow
creds = Credentials.from_authorized_user_file('credentials.json', SCOPES)
youtube = build('youtube', 'v3', credentials=creds)

# Upload
request = youtube.videos().insert(
    part='snippet,status',
    body={
        'snippet': {
            'title': 'Your Video Title',
            'description': 'Your description #horror #story',
            'tags': ['horror', 'storytelling'],
            'categoryId': '24'  # Entertainment
        },
        'status': {
            'privacyStatus': 'public',
            'selfDeclaredMadeForKids': False
        }
    },
    media_body=MediaFileUpload('video.mp4', mimetype='video/mp4', resumable=True)
)

response = request.execute()
print(f"Uploaded: https://youtube.com/watch?v={response['id']}")
```

See `scripts/youtube_upload.py` in this skill for full implementation.

**Requirements:**
- Google Cloud project with YouTube Data API v3 enabled
- OAuth 2.0 client credentials
- First run requires interactive OAuth consent

### Option 3: Manual Upload

Simplest fallback when automation isn't configured:

```bash
# Video ready at:
~/.openclaw/workspace/tales-untold/longform/finals/*.mp4

# Upload manually:
# 1. Go to youtube.com/upload
# 2. Select file
# 3. Set title, description, tags
# 4. Publish as "Public"
```

## Verified Buffer YouTube Format Requirements

| Format | Resolution | Aspect Ratio | Buffer Channel Type |
|--------|-----------|--------------|---------------------|
| Shorts | 1080×1920 | 9:16 (0.56) | Shorts-only ✓ |
| Shorts | 720×1280 | 9:16 (0.56) | Shorts-only ✓ |
| Regular | 1920×1080 | 16:9 (1.78) | Mixed or Long-form only ✓ |
| Regular | 1280×720 | 16:9 (1.78) | Mixed or Long-form only ✓ |
| Regular | 1920×1080 | 16:9 (1.78) | Shorts-only ❌ FAILS |

## Dual-Format Publishing Strategy

For channels producing both Shorts and long-form:

```python
if video_duration <= 60 and aspect_ratio <= 0.7:
    # Shorts → use Buffer
    buffer_api_call(channel_id_shorts, ...)
elif aspect_ratio >= 1.5:
    # Long-form → YouTube API or manual
    youtube_api_upload(...)
else:
    # Ambiguous → try Buffer, fall back to manual
    try_buffer_else_manual(...)
```

## MCP Limitations for YouTube

The Buffer MCP server **does not expose**:
- Channel format configuration (read-only)
- Video dimension validation before upload
- Format conversion/transcoding
- Separate Shorts vs long-form queue management

All format constraints are enforced server-side after the upload starts.

## Error Reference

| Error | Meaning | Fix |
|-------|---------|-----|
| `Video must be vertical (portrait orientation) for YouTube Shorts` | Channel locked to Shorts format | Use different channel or YouTube API |
| `Invalid video format` | Video codec/container not supported | Re-encode as H.264/MP4 |
| `Video too long for Shorts` | >60 seconds on Shorts channel | Trim or use long-form channel |
| `Video file too large` | >500MB limit | Compress or split |

---

**Session Reference:** September 2026 — Buffer MCP YouTube format testing for Tales Untold long-form pipeline
