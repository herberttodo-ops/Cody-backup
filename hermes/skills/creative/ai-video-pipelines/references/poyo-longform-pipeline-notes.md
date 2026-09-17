# POYO API & Long-Form Pipeline Notes
*Session-hardened patterns and pitfalls from building 15-min long-form videos*

## POYO Response Format (Critical)

**ALL POYO API responses nest the payload under `data["data"]`**:

```python
# Submit response
resp = requests.post(...)
data = resp.json()

# ❌ WRONG — returns None, breaks scripts
task_id = data.get("task_id")

# ✅ CORRECT
task_id = data.get("data", {}).get("task_id")
```

**Same pattern for status polling**:

```python
status_data = requests.get(...).json()
status = status_data.get("data", {}).get("status")  # not status_data["status"]
files = status_data.get("data", {}).get("result", {}).get("files", [])
```

**Checking errors**:

```python
# After status returns "finished", ALWAYS check result for embedded error
result = status_data.get("data", {}).get("result", {})
if "error" in result:
    # Task "finished" but actually failed inside the model
    raise ValueError(f"Model error: {result['error']}")
```

## nano-banana-2-lite for 16:9 Images

**Model**: `nano-banana-2-lite` works for long-form (16:9) images.

**Payload**:

```python
payload = {
    "model": "nano-banana-2-lite",
    "input": {
        "prompt": "Stephen Gammell ink wash illustration. Dark unsettling...",
        "size": "16:9"  # Works for wide images
    }
}
```

**Known issue**: The model occasionally returns `finished` status with empty or missing `files`. Always check `files` before downloading.

## Adam Voice TTS via POYO

**Model**: `elevenlabs-tts-turbo-2-5`

**Payload**:

```python
payload = {
    "model": "elevenlabs-tts-turbo-2-5",
    "input": {
        "voice": "Adam",       # String name, not voice_id
        "text": narration_text # Full 3000-word text works
    }
}
```

**Credit cost**: ~56 credits for 7 minutes of narration

**Duration limit**: Successfully generated 418 seconds (7 min) in one call

## Repurposing Shorts Images for Long-Form

Existing Tales Untold shorts images are **9:16 (768x1376)**. When building 16:9 long-form:

- **Option A**: Generate new 16:9 images via `nano-banana-2-lite`
- **Option B**: Use 9:16 images and accept vertical format (YouTube accepts both)
- **Option C**: Crop/pad 9:16 to 16:9 (loses top/bottom or adds black bars)

**Recommendation**: For pilot/prototype, use existing 9:16 images directly. YouTube Shorts algorithm accepts vertical long-form.

## FFmpeg Assembly: Long-Form Pattern

### Scene Clip Generation (14s per scene)

```bash
ffmpeg -y -loop 1 -i scene.png \
  -vf "fade=t=out:st=12:d=2,format=yuv420p" \
  -c:v libx264 -preset fast -crf 22 \
  -t 14 -pix_fmt yuv420p scene_clip.mp4
```

### Concatenate with Crossfade

```python
# Build concat list
with open("concat.txt", "w") as f:
    for clip in clips:
        f.write(f"file '{clip.absolute()}'\n")

# Simple concat (crossfade handled in clips)
ffmpeg -y -f concat -safe 0 -i concat.txt -c:v libx264 raw.mp4
```

### Mix Narration + Ambient Music

```python
ffmpeg -y \
  -i raw_video.mp4 \
  -i narration.mp3 \
  -i ambient_music.m4a \
  -filter_complex \
    "[2:a]atrim=0:TARGET_DURATION,volume=0.15[mus];\
     [1:a][mus]amix=inputs=2:duration=first[aout]" \
  -map "0:v" -map "[aout]" \
  -c:v libx264 -preset slow -crf 18 \
  -c:a aac -b:a 192k \
  -shortest \
  final.mp4
```

**Ambient music generation** (local, no API needed):

```bash
ffmpeg -y \
  -f lavfi -i "anoisesrc=d=1200:c=brown:r=44100" \
  -af "volume=0.06,highpass=f=80" \
  -c:a aac -b:a 128k \
  ambient_bed.m4a
```

## BunnyCDN Upload Pattern

**API**: Direct storage upload via curl

```python
import subprocess

cmd = [
    "curl", "-fsS", "-T", str(video_path),
    "https://ny.storage.bunnycdn.com/{STORAGE_ZONE}/{filename}",
    "-H", f"AccessKey: {api_key}"
]
result = subprocess.run(cmd, capture_output=True, timeout=300)
```

**Direct URL after upload**:
```
https://{STORAGE_ZONE}.b-cdn.net/{filename}
```

**Note**: Storage zone must exist in BunnyCDN dashboard. If 401, check:
1. Zone exists with correct name
2. API key has read/write permissions
3. Region matches (ny, de, etc.)

## Pipeline Cost Estimation

| Component | Per 15-Min Video | Notes |
|-----------|-------------------|-------|
| Script | $0 (pre-written) | Or ~$0.05 via LLM |
| TTS (Adam) | ~$0.23 | 56 credits @ ~$0.004/credit |
| Images (8x) | ~$0.32 | 8 images @ ~$0.04 each |
| Ambient music | $0 | ffmpeg-generated |
| Upload/ CDN | ~$0.01 | Bunny bandwidth |
| **Total** | **~$0.56** | Per 15-min video |

## Complete Orchestrator Script

See `scripts/build_longform_video.py` in the longform workspace for the full orchestrator that runs:
1. Generate script (or use pre-written)
2. Generate Adam narration via POYO
3. Generate 8 Gammell illustrations via nano-banana-2-lite
4. Render scene clips with fade-out
5. Generate ambient music via ffmpeg
6. Assemble with narration + music
7. Upload to BunnyCDN
8. Schedule to YouTube via Buffer
