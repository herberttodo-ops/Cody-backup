# Whisper Transcription & Caption Workflow

Extracting transcripts from video clips for burned-in captions.

## Prerequisites

```bash
pip install openai-whisper
pip install youtube-transcript-api
```

## Extract Transcript from Existing Video

```bash
# Extract audio from video
ffmpeg -hide_banner -loglevel warning -i input.mp4 \
  -vn -acodec libmp3lame -q:a 2 /tmp/audio.mp3 -y

# Transcribe with Whisperwhisper /tmp/audio.mp3 --model tiny --output_format srt \
  --output_dir /tmp --fp16 False
```

## Model Options

| Model | Size | Speed | Accuracy | Use For |
|-------|------|-------|----------|---------|
| tiny | 39 MB | ~10x | Good | Quick transcription, caption timing |
| base | 74 MB | ~7x | Better | Standard use |
| small | 244 MB | ~4x | Good | Better accuracy |
| medium | 769 MB | ~2x | Better | Broadcast quality |
| large-v3 | 2.9 GB | 1x | Best | Publication quality |

## Quick Transcript (No File Save)

```python
import whisper

model = whisper.load_model("tiny")
result = model.transcribe("/tmp/audio.mp3")

for seg in result["segments"]:
    print(f"[{seg['start']:.1f}s] {seg['text']}")
```

## Manual SRT Creation (Lightweight)

If Whisper isn't needed, create simple SRT files manually:

```
1
00:00:00,000 --> 00:00:30,000
[Clip description or reaction note]
```

Then burn in with:

```bash
ffmpeg -i clip.mp4 -vf "subtitles=captions.srt" output.mp4
```

## Burned-in Captions (No SRT file)

Fast one-liner using drawtext:

```bash
ffmpeg -i clip.mp4 -vf "drawtext=text='[Reaction!]':fontcolor=white:fontsize=48:box=1:boxcolor=black@0.5:boxborderw=5:x=(w-text_w)/2:y=h*0.7" -c:v libx264 -c:a copy output.mp4
```

Position options:
- Bottom third: `y=h*0.7`
- Top: `y=h*0.1`
- Centered: `y=(h-text_h)/2`
- Bottom edge: `y=h-text_h-50`