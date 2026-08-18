---
name: video-clips-for-social
description: Create vertical video clips from YouTube videos for TikTok, Instagram Reels, and YouTube Shorts. Download, analyze, reframe, and add captions.
version: 1.0.0
---

# Video Clips for Social Media

Create engaging vertical clips from long-form YouTube videos for short-form platforms.

## Workflow

1. **Download** video from YouTube (with user consent)
2. **Analyze** transcript to find engaging moments
3. **Cut** clips at those timestamps
4. **Reframe** to vertical (9:16)
5. **Add captions** (burned-in or SRT)

## Prerequisites

```bash
pip install yt-dlp
```

FFmpeg must be installed (check with `which ffmpeg`)

## Step 1: Download Video

**Required:** Get user consent before downloading!

```bash
yt-dlp --no-playlist -f "bestvideo[height<=1080]+bestaudio/best[height<=1080]" \
  --merge-output-format mp4 "VIDEO_URL" -o "video.%(ext)s"
```

### Download Blocking Issues

YouTube frequently blocks downloads with **403 Forbidden** errors, even with cookies.

**When download fails:**
1. Ask user to download the video themselves (4K Video Downloader, browser extensions)
2. Have user share the file path to a local copy
3. Check if user already has the video saved locally

**Alternative: Analyze transcript first**
You can often analyze the video via transcript without downloading:
```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
result = api.fetch('VIDEO_ID')
# Find hook moments from transcript
```

This lets you identify clip timestamps before dealing with the video file.

## Step 2: Extract Transcript

```bash
# Using youtube-transcript-api
pip install youtube-transcript-api
```

See [references/video-analysis.md](references/video-analysis.md) for analyzing transcripts and finding clip-worthy moments.

## Step 3: Create Vertical Clips with FFmpeg

### Center Crop to Vertical (9:16)

```bash
ffmpeg -i input.mp4 -vf "crop=in_h*9/16:in_h" -c:a copy output_vertical.mp4
```

### Add Captions (Burned-in)

```bash
ffmpeg -i input.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&H00FFFFFF'" output.mp4
```

### Extract Clip Segment

```bash
ffmpeg -ss 00:01:30 -t 30 -i input.mp4 -c copy clip.mp4
```

## Clip Selection Criteria

**High-engagement moments:**
- Strong hooks (first 3 seconds)
- Emotional reactions
- Key revelations or punchlines
- Controversial statements
- Questions that create curiosity

**Optimal clip length:**
- TikTok: 15-60 seconds
- Reels: 15-90 seconds
- Shorts: 15-60 seconds

## File Locations

- Downloads: `/tmp/` (temporary)
- Clips: `~/.hermes/generated_clips/`
- Transcripts: `~/.hermes/video_transcripts/`

## Tools with Smart Reframing

For AI-powered face tracking/reframing (beyond FFmpeg crop):

| Tool | Feature | API Available |
|------|---------|---------------|
| **Descript** | AI reframing, eye contact | Yes (contact sales) |
| **VEED** | Subtitles, background removal | Yes (via fal.ai) |
| **Kapwing** | Smart Cut, auto-captions | Yes |
| **Runway** | Motion tracking | Yes |

## Error Patterns

| Error | Cause | Fix |
|-------|-------|-----|
| `yt-dlp: command not found` | Not installed | `pip install yt-dlp` |
| `Sign in to confirm you're not a bot` | YouTube blocking | Use cookies: `--cookies-from-browser firefox` |
| `FFmpeg not found` | Not installed | `apt install ffmpeg` or `brew install ffmpeg` |

## References

- [FFmpeg documentation](https://ffmpeg.org/documentation.html)
- [yt-dlp documentation](https://github.com/yt-dlp/yt-dlp)