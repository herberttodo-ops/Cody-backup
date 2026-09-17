# Long-Form Video Production Reference

## Context
Reference for Tales Untold long-form horror video production. This complements the shorts pipeline.

## Key Differences: Long-Form vs Shorts

| Aspect | Shorts | Long-Form |
|--------|--------|-----------|
| Duration | ~60s | 7-15+ min |
| Scenes | 5-8 | 8-30+ |
| Aspect Ratio | 9:16 (1080x1920) | 16:9 preferred, 9:16 accepted |
| Scene Display | 10s per scene | 60s+ per scene |
| Audio | Voice + music | Voice + longer ambient bed |
| Hosting | Google Drive works | BunnyCDN needed for 500MB+ |

## Asset Reuse Strategy

When image generation APIs fail or are slow, **reuse existing assets**:

```python
# Copy existing Gammell illustrations from shorts
import shutil
from pathlib import Path

src_dir = Path("~/.openclaw/workspace/tales-untold/hyperframes-test")
dst_dir = Path("~/.openclaw/workspace/tales-untold/longform/illustrations")

existing = list(src_dir.glob("*_*.png"))
for i, img in enumerate(existing[:8], 1):
    shutil.copy(img, dst_dir / f"scene_{i:03d}.png")
```

**When to use:**
- POYO down or rate-limited
- Need fast turnaround for pilot/demo
- Accepting slightly mismatched visuals for proof-of-concept

## Scene Timing Formula

For crossfade transitions:
```
Scene duration = total_audio_duration / num_scenes
Clip duration = scene_duration + fade_buffer (2s)
Fade start = clip_duration - 2
Fade duration = 2s
```

Example for 8 scenes, 420s audio:
- Scene duration: 52.5s
- Clip duration: 54.5s
- Fade starts at 52.5s, lasts 2s

## FFmpeg Assembly for Long-Form

```bash
# Concatenate scenes with crossfades
ffmpeg -f concat -safe 0 -i scenes.txt -c:v libx264 -crf 18 raw_video.mp4

# Mix audio (Adam voice + ambient bed)
ffmpeg -i raw_video.mp4 -i narration.mp3 -i ambient.m4a \
  -filter_complex "[2:a]atrim=0:TARGET_DURATION,volume=0.15[mus];[1:a][mus]amix=inputs=2[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -shortest final_video.mp4
```

Key flags:
- `-shortest`: End when shortest input ends
- `amix`: Mix multiple audio streams
- `atrim`: Trim ambient to match narration length
- `volume=0.15`: Subtle background (15%)

## POYO API Response Format

**CRITICAL:** POYO responses are nested under a `data` key. Missing this causes silent failures.

```python
resp = requests.post("https://api.poyo.ai/api/generate/submit", ...)
data = resp.json()

# WRONG - returns None
task_id = data.get("task_id")

# CORRECT - POYO nests everything under 'data'
task_id = data.get("data", {}).get("task_id")

# Status polling - same pattern
status_data = requests.get(f"https://api.poyo.ai/api/generate/status/{task_id}", headers=headers).json()
status = status_data.get("data", {}).get("status")  # "not_started", "running", "finished", "error"

# Get result files
files = status_data.get("data", {}).get("result", {}).get("files", [])
file_url = files[0]["file_url"] if files else None
```

### Common POYO API Endpoints

| Task | Model | Endpoint | Input |
|------|-------|----------|-------|
| TTS | `elevenlabs-tts-turbo-2-5` | `/api/generate/submit` | `{"voice": "Adam", "text": "..."}` |
| Images | `nano-banana-2-lite` | `/api/generate/submit` | `{"prompt": "...", "size": "16:9"}` |
| Poll | - | `/api/generate/status/{task_id}` | GET |

**Retry loop pattern:** Poll every 5s, timeout 5-10 min depending on job type.

## Publishing Long-Form to YouTube

Buffer accepts long-form videos the same way as shorts:

```python
# Upload to temporary hosting first (Drive or BunnyCDN)
video_url = "https://drive.google.com/uc?export=view&id=FILE_ID"

# Post via Buffer MCP - long-form detected automatically
{
  "channelId": "YOUTUBE_CHANNEL_ID",
  "text": "Description with #hashtags",
  "assets": [{
    "video": {
      "url": video_url,
      "metadata": {
        "title": "Video Title | Tales Untold",
        "thumbnailOffset": 0
      }
    }
  }],
  "metadata": {
    "youtube": {
      "title": "Video Title | Tales Untold",
      "categoryId": "24",  # Entertainment
      "privacy": "public",
      "madeForKids": false
    }
  }
}
```

## Cost Estimation: Long-Form (7-15 min)

| Component | Cost |
|-----------|------|
| Script generation (POYO Claude) | ~$0.10-0.20 |
| TTS (Adam, ~1000 words) | ~$0.10 |
| Images (8 scenes, reuse or generate) | $0-0.24 |
| Ambient music (Suno or procedural) | $0-0.10 |
| **Total per video** | **$0.20-0.65** |

At 3x/week: ~$2-3/month

## Common Pitfalls

1. **Google Drive 404 on large files** - Use `uc?export=view&id=` not `file/d/ID/view`
2. **Audio sync drift** - Always use `-shortest` flag to prevent desync
3. **Scene black frames** - Ensure fade out completes before next scene starts
4. **POYO nested response** - Always access via `data.get("data", {})` not root

## BunnyCDN Troubleshooting

### Upload Works But CDN Returns 403/401

If `storage.bunnycdn.com` accepts uploads but `*.b-cdn.net` returns errors:

1. **Verify Storage Zone exists** — List with: `curl -H "AccessKey: KEY" https://storage.bunnycdn.com/`
2. **Create Pull Zone** — Storage is private by default
   - Dashboard → Pull Zones → Add Pull Zone
   - Origin URL: `https://storage.bunnycdn.com/ZONE_NAME/`
   - Results in: `https://ZONE-NAME.b-cdn.net/`
3. **Wait for propagation** — 1-5 minutes after Pull Zone creation

### Authentication Key Types

| Key Type | Purpose | Used For |
|----------|---------|----------|
| **Storage Password** | Storage zone API | Upload, list, delete files |
| **Storage API Key** | Alternative auth | Some legacy integrations |
| **Account API Key** | Account management | Creating zones, billing |

**For file operations:** Use the Storage Password from FTP & API Access tab.

### Testing Upload

```bash
# Should return [] for empty zone
curl -H "AccessKey: STORAGE_PASSWORD" https://storage.bunnycdn.com/YOUR_ZONE/

# Should return 201 on success
curl -T file.mp4 \
  -H "AccessKey: STORAGE_PASSWORD" \
  https://storage.bunnycdn.com/YOUR_ZONE/path/file.mp4
```

## Migration Path: Shorts → Long-Form

To convert existing shorts pipeline:

1. Reuse hyperframes-test/ images
2. Generate longer script (~1000+ words)
3. Use same Adam TTS endpoint
4. Extend scene duration from 10s to 60s+
5. Add crossfade transitions
6. Mix with longer ambient bed
7. Upload to Drive/Bunny instead of direct Buffer embed

## Scripts Location
- Pilot builder: `~/.openclaw/workspace/tales-untold/scripts/pilot_fallback.py`
- Bunny uploader: `~/.openclaw/workspace/tales-untold/scripts/bunny_uploader.py`
- Long-form generator: `~/.openclaw/workspace/tales-untold/scripts/longform_generator.py`
