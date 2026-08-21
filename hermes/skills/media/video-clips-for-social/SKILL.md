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

## Continuing from Previous Session

If video was downloaded previously and saved to a known path:

```bash
# Check video exists and get duration
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 /path/to/video.mp4

# Create output directory
mkdir -p ~/.hermes/generated_clips
```

Then proceed directly to **Step 3: Create Vertical Clips**.

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
4. **Use transcript-only analysis** — See Step 2 below

**Alternative: Analyze transcript only**
You can analyze the video via transcript without downloading the video file (works even when download is blocked):

```python
from youtube_transcript_api import YouTubeTranscriptApi
api = YouTubeTranscriptApi()
result = api.fetch('VIDEO_ID')

# Find hook moments from transcript
segments = [{"text": seg.text, "start": seg.start, "duration": seg.duration} for seg in result]

# Look for engagement signals
hooks = []
for seg in segments:
    text = seg['text'].upper()
    if any(word in text for word in ['OH MY', 'WOW', 'HOLY', 'WHAT', 'NO WAY', 'GOD', 'INSANE']):
        hooks.append((seg['start'], seg['text']))
```

This lets you identify clip timestamps before dealing with the video file. The transcript is available even when download is blocked.

## Step 2: Extract Transcript

```bash
# Using youtube-transcript-api
pip install youtube-transcript-api
```

For extracting transcripts from local video files with Whisper, see [references/whisper-transcription.md](references/whisper-transcription.md).

See [references/video-analysis.md](references/video-analysis.md) for analyzing transcripts and finding clip-worthy moments.

## Step 3: Create Vertical Clips with FFmpeg

### Center Crop to Vertical (9:16)

Full command including scaling to 1080x1920:

```bash
ffmpeg -i input.mp4 -vf "crop=in_h*9/16:in_h,scale=1080:1920,setsar=1" \
  -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k output_vertical.mp4
```

### Extract Clip + Reframe + Scale (One Command)

Extract segment and convert to vertical in one step:

```bash
ffmpeg -ss 00:03:30 -t 30 -i input.mp4 \
  -vf "crop=in_h*9/16:in_h,scale=1080:1920,setsar=1" \
  -c:v libx264 -crf 23 -preset fast -c:a aac -b:a 128k clip.mp4
```

### Add Captions (Burned-in with SRT)

```bash
ffmpeg -i input.mp4 -vf "subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&H00FFFFFF'" output.mp4
```

### Add Simple Burned-in Captions (No SRT file needed)

Use drawtext for quick captions without creating SRT files:

```bash
ffmpeg -i input.mp4 -vf "drawtext=text='[Caption text]':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=h*0.7" -c:v libx264 -c:a copy output.mp4
```

Position at bottom 30%: `y=h*0.7`
Position at top: `y=h*0.1`
Position centered: `y=(h-text_h)/2`

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