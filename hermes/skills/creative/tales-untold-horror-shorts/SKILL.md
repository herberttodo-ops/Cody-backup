---
name: tales-untold-horror-shorts
title: Tales Untold Horror Shorts Production
description: |
  Create 9:16 vertical horror shorts with exact brand specifications.
  Critical: Whisper transcript for captions, never guess. Scene every 4-6s.
  White text (0-4s), red #ff4444 (twist onward), black stroke, y=1200 safe-zone position.
version: 1.0.0
author: Andrew
tags: [video, shorts, horror, moviepy, whisper]
---

# Tales Untold Horror Shorts

## Brand Requirements (CRITICAL)

### Visual Design
- **Format:** 9:16 vertical (1080x1920)
- **Text colors:**
  - White (#ffffff) for setup/hook (first ~19s for 48s, or ~4s per story arc)
  - Red (#ff4444) after horror twist/escalation
- **Text positioning:**
  - **y=1200 max** (safe zone — upper portion of bottom third, avoids TikTok/Shorts UI)
  - Do NOT use y=1420; text gets cut off by platform overlays
- **Text styling:**
  - Font: DejaVuSans-Bold (fallback; Arial is usually missing on Linux)
  - Size: 46-52pt depending on length
  - Black stroke: 4-5px
- **Scene timing:** 10 equal segments at 4.8s each for 48s total

### Content Requirements
- **ALWAYS** transcribe audio with Whisper first
- **NEVER** guess captions - use exact Whisper timestamps
- **NEVER** use AI-generated images with text artifacts
- Clean, photorealistic horror imagery

## Production Workflow v2 (with Improvements)

### IMPROVEMENT 1: Ken Burns Effect (Zoom/Pan on Every Scene)
Every static image should have motion to avoid "slideshow" feel.

```python
def make_ken_burns_clip(img_path, duration, start_zoom, end_zoom,
                        start_pan=(0, 0), end_pan=(0, 0), size=(1080, 1920)):
    """Create VideoClip with Ken Burns zoom/pan effect.
    zoom: scale factor (1.0 = fill frame)
    pan: (dx, dy) in pixels relative to center
    """
    from PIL import Image
    import numpy as np
    from moviepy import VideoClip
    
    img = Image.open(img_path)
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    max_zoom = max(start_zoom, end_zoom)
    base_w = int(size[0] * max_zoom * 1.3)
    base_h = int(base_w * img.height / img.width)
    img_base = img.resize((base_w, base_h), Image.Resampling.LANCZOS)
    
    def make_frame(t):
        progress = min(t / duration, 1.0)
        zoom = start_zoom + (end_zoom - start_zoom) * progress
        pan_x = start_pan[0] + (end_pan[0] - start_pan[0]) * progress
        pan_y = start_pan[1] + (end_pan[1] - start_pan[1]) * progress
        
        crop_w = int(size[0] / zoom)
        crop_h = int(size[1] / zoom)
        img_w, img_h = img_base.size
        cx = img_w // 2 + int(pan_x)
        cy = img_h // 2 + int(pan_y)
        
        x1 = max(0, min(cx - crop_w // 2, img_w - crop_w))
        y1 = max(0, min(cy - crop_h // 2, img_h - crop_h))
        cropped = img_base.crop((x1, y1, x1 + crop_w, y1 + crop_h))
        return np.array(cropped.resize(size, Image.Resampling.LANCZOS))
    
    return VideoClip(make_frame, duration=duration)

# Ken Burns presets (diverse motions)
ken_presets = [
    (1.00, 1.15, (0, 0), (0, 0)),      # slow zoom in
    (1.10, 1.00, (0, 0), (0, 0)),      # slow zoom out
    (1.00, 1.12, (-40, 0), (40, 0)),   # zoom in + pan right
    (1.05, 1.05, (50, 0), (-50, 0)),   # pan left
    (1.00, 1.10, (0, -30), (0, 30)),   # zoom in + pan down
    (1.08, 1.00, (0, 30), (0, -30)),   # zoom out + pan up
]
```

### IMPROVEMENT 2: Manual Word Wrapping (No Mid-Word Breaks)
MoviePy's `caption` method breaks mid-word. Use custom wrapping:

```python
def wrap_text(text, max_chars=28):
    """Hard-wrap at word boundaries, no mid-word breaks."""
    words = text.split()
    lines = []
    current = ""
    for w in words:
        if current == "":
            current = w
        elif len(current) + 1 + len(w) <= max_chars:
            current += " " + w
        else:
            lines.append(current)
            current = w
    if current:
        lines.append(current)
    return "\n".join(lines)

# Use with TextClip:
wrapped = wrap_text(raw_text, max_chars=28)
txt = TextClip(
    text=wrapped, font="DejaVuSans-Bold", font_size=48,
    color=color, stroke_color="black", stroke_width=4,
    size=(950, None), method="caption",
    text_align="center", bg_color=None
)
```

### IMPROVEMENT 3: Spooky Ambient Background Music
Generate dark ambient music programmatically to mix under narration:

```python
import numpy as np
from scipy import signal
from scipy.io import wavfile

def generate_horror_ambient(duration_sec, output_path):
    sr = 44100
    samples = int(sr * duration_sec)
    t = np.linspace(0, duration_sec, samples, endpoint=False)
    
    # Layer 1: Deep sub-bass drone (~55Hz) with slow LFO
    lfo1 = 0.5 + 0.5 * np.sin(2 * np.pi * 0.1 * t)
    drone1 = 0.15 * np.sin(2 * np.pi * 55 * t) * lfo1
    
    # Layer 2: Low drone (~82Hz), slightly detuned
    drone2 = 0.12 * np.sin(2 * np.pi * 82.3 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.07 * t))
    
    # Layer 3: Very low rumble (~30Hz)
    drone3 = 0.10 * np.sin(2 * np.pi * 30 * t) * (0.5 + 0.5 * np.sin(2 * np.pi * 0.05 * t))
    
    # Layer 4: Dissonant mid-tone for tension
    tension = 0.08 * (np.sin(2 * np.pi * 150 * t) + np.sin(2 * np.pi * 155.2 * t))
    
    # Layer 5: Dark noise (filtered brown noise)
    np.random.seed(42)
    white = np.random.randn(samples)
    brown = np.cumsum(white)
    brown = brown / (np.max(np.abs(brown)) + 1e-9)
    sos = signal.butter(4, 400/(sr/2), btype='low', output='sos')
    dark_noise = 0.04 * signal.sosfilt(sos, brown)
    
    # Combine and normalize
    audio = drone1 + drone2 + drone3 + tension + dark_noise
    audio = audio / np.max(np.abs(audio)) * 0.70
    
    # Fade in/out
    fade_in = int(2 * sr)
    fade_out = int(3 * sr)
    audio[:fade_in] *= np.linspace(0, 1, fade_in)
    audio[-fade_out:] *= np.linspace(1, 0, fade_out)
    
    wavfile.write(output_path, sr, (audio * 32767).astype(np.int16))
```

Mix audio (narration + background):
```python
from moviepy import AudioFileClip, CompositeAudioClip

narration = AudioFileClip("audio.mp3")
bg = AudioFileClip("background_music.wav").subclipped(0, narration.duration)
bg = bg.with_volume_scaled(0.12)  # ~-20dB under narration

mixed = CompositeAudioClip([narration, bg])
```

---

## Production Workflow

### Step 1: Transcribe Audio
```bash
whisper audio.mp3 --model tiny --output_format json
```
- Use tiny model for speed
- Verify transcript matches actual spoken words

### Step 2: Map Scenes to Timestamps
- Divide 48s video into ~10 scenes
- Each scene: 4.8s average
- Map Whisper segments to scene slots

### Step 3: Select Images
Check available images in `output/shorts/`:
- scene1_* : Snorer/setup
- scene2_* : Phone/nightstand
- scene3_* : Morning/audio check
- scene4_* : Twist/unnatural
- scene5_* : Waveform/technical
- scene6_* : Playback/3AM
- scene7_* : Alone/realization
- scene8_* : Email/ancient

### Step 4: Build Video
Use MoviePy with this pattern:
- Load audio, get duration
- Create segments list: (start, end, text, image_file, color, stroke_width)
- Each segment = ImageClip + TextClip composited
- No base layer (causes black gaps)

### Step 5: Verify
- Extract frames at 2s, 15s, 25s, 40s
- Confirm scene changes
- Check caption visibility

## Code Template
```python
from moviepy import *
from PIL import Image
import numpy as np

def load_and_crop(path):
    img = Image.open(path)
    # 9:16 crop and resize
    return np.array(img)

def make_text(text, start, duration, color, stroke):
    return TextClip(
        text=text, font='DejaVuSans-Bold', font_size=50,
        color=color, stroke_color="black", stroke_width=stroke,
        size=(950, None), method='caption',
        text_align='center', bg_color=None
    ).with_start(start).with_duration(duration).with_position(('center', 1200))

# Build segments from Whisper timestamps
segments = [
    (0.0, 4.8, "Hook text", "scene1.png", "white", 4),
    # ... etc
]
```

## Common Mistakes
- Using wrong image filenames (always check `ls` first)
- Caption position too low (cut off by UI) — use **y=1200 max**, NOT y=1420
- Not enough scene variety (10 distinct images for 48s)
- Black gaps from base layer — remove ColorClip base
- Using `Arial` font fails with `OSError: cannot open resource` — use `DejaVuSans-Bold`
- MoviePy v2 API uses `with_*` methods, not v1 `set_*`

## References
- `references/whisper-timestamps.md` - Example transcript format
- `templates/segments.json` - Scene mapping template