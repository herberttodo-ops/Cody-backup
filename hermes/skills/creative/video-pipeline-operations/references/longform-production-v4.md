# Long-Form Video Production V4 Reference

## Tales Untold Long-Form: 12–17 Minute Pipeline

### User Requirements
- Duration: 12–17 minutes
- Scene rate: 1 new image every 10–15 seconds (≈60–90 scenes per 15 min video)
- Animation: Ken Burns (slow zoom + pan) on every image via ffmpeg zoompan
- Captions: Hard-burned closed captions (white text, black outline, centered bottom)
- Audio: Adam TTS narration + brown noise ambient bed mixed at low volume
- Thumbnail: Gammell-style 16:9 image uploaded with the video
- Upload: Direct YouTube Data API OAuth (Buffer Shorts-only channel is unsuitable for long-form)
- Hosting: Google Drive or BunnyCDN for temporary asset storage
- Cron: Mon/Thu 10 AM ET automatic production and publish

### Architecture V4

```
Story (2000–2500 words) → TTS (Adam, POYO) → 60–90 16:9 Images (nano-banana-2-lite)
     → Ken Burns per scene (ffmpeg zoompan) → Caption SRT from text segmentation
     → ffmpeg concat + amix ambient → YouTube OAuth upload + thumbnail
```

### Key FFmpeg Commands

#### Ken Burns Effect (zoompan)
```bash
# 12s scene at 30fps with slow zoom in + pan from different angles
ffmpeg -y -loop 1 -i image.png -vf "zoompan=z='zoom+0.001':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=360:s=1920x1080" -t 12 -c:v libx264 -pix_fmt yuv420p scene.mp4
```

Direction variants (rotate by scene index):
- Center zoom
- Top-left to center
- Top-right to center
- Bottom-left to center
- Bottom-right to center

#### Caption Burn-In (subtitles filter)
```bash
ffmpeg -i video.mp4 -i narration.mp3 -i ambient.m4a \
  -filter_complex "[2:a]atrim=0:DURATION,volume=0.12[mus];[1:a][mus]amix=inputs=2:duration=first[aout];[0:v]subtitles=captions.srt:force_style='FontSize=24,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Shadow=0,Alignment=2,MarginV=40'[vout]" \
  -map "[vout]" -map "[aout]" -c:v libx264 -preset slow -crf 18 -c:a aac -b:a 192k -shortest final.mp4
```

### Caption SRT Generation

Segment text into ~3.5-second chunks from TTS script:
- Calculate words/second from total words ÷ audio duration
- Group words into segments of 3.5s duration
- Write SRT format with HH:MM:SS,mmm timing

### POYO API Notes for Long-Form

**16:9 image generation works at standard sizes.** POYO nano-banana-2-lite returns 1376×768 (ratio 1.79), close to 16:9. Use directly or scale in ffmpeg.

**Response path for images:** Files are at `data.files` not `data.result.files` (inconsistent with TTS which uses `data.result.files`).

### YouTube OAuth Setup (Device Flow for Headless Servers)

Google deprecated out-of-band OAuth (`urn:ietf:...:oob`). For servers with no browser:

1. Create "TV and Limited Input device" OAuth client in Google Cloud Console
2. Client sends `POST https://oauth2.googleapis.com/device/code` with client_id + scope
3. User opens `verification_url` on any device, enters `user_code`
4. Server polls `POST https://oauth2.googleapis.com/token` with `grant_type=urn:ietf:params:oauth:grant-type:device_code`
5. Poll returns access_token + refresh_token on authorization
6. Save credentials json for future uploads
7. If test user added in consent screen, publish app to production to avoid "not verified" errors

### Upload Script
```python
# ~/.hermes/scripts/youtube_upload_oauth.py
# Expects: ~/.config/youtube_credentials.json
youtube.videos().insert(part="snippet,status", body={
  "snippet": {"title": title, "description": desc, "categoryId": "24"},
  "status": {"privacyStatus": privacy}
}, media_body=MediaFileUpload(video_file)).execute()
# Optional thumbnail: youtube.thumbnails().set(videoId=..., media_body=...)
```

### Cost Estimation (V4)

| Component | Count | Est. Cost |
|-----------|-------|-----------|
| Scenes (75 images) | 75 × nano-banana | ~$0.60 |
| Thumbnail (1 image) | 1 × nano-banana | ~$0.05 |
| Adam TTS (~15 min) | elevenlabs-tts-turbo-2-5 | ~$0.18 |
| **Total per video** | | **~$0.83** |

### Pitfalls
- **Ken Burns with zoompan**: `zoompan` filter can be slow. Use `-preset fast` for scene clips, `-preset slow` only for final encode
- **Subtitle filter escape**: Cannot include backslash inside Python f-string expression. Pre-escape the caption path before passing to filter_complex
- **Scene count mismatch**: Always use `min(img_count, ceil(audio_dur / scene_duration))` to avoid concat errors
- **Audio desync**: Always use `-shortest` and trim ambient to narration length
- **POYO credits**: YouTube Data API v3 does NOT use IAM roles for YouTube channel access; OAuth is required, service accounts do not work for channel uploads
- **Buffer Shorts-only**: Tales Untold Buffer channel enforces 9:16 vertical. Long-form 16:9 must use YouTube API direct upload, not Buffer

### Scripts

| Script | Purpose |
|--------|---------|
| `tales_longform_producer_v4.py` | Main orchestrator (Python) |
| `youtube_upload_oauth.py` | YouTube direct upload with thumbnail |
| `youtube_oauth_device.py` | One-time OAuth setup helper |
| `gen_single.py` | Single POYO image generation utility |

### Cron Job

```
Job: tales-untold-longform-v4-youtube
Schedule: 0 10 * * 1,4 (Mon/Thu 10 AM ET)
Script: tales_longform_producer_v4.sh
Workdir: ~/.openclaw/workspace/tales-untold
```

### Video Outputs Location

```
~/.openclaw/workspace/tales-untold/longform/
  finals/        # Finished MP4s
  illustrations/ # Generated 16:9 Gammell images
  thumbnails/    # Video thumbnails
  scenes/        # Ken Burns clip segments
  assets/        # TTS + ambient audio + captions SRT
```
