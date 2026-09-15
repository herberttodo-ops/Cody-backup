# Tales Untold — Equal Segments Builder Pattern

Session-specific build pattern for 48-second horror shorts with 10 equal scene segments.

## Builder Configuration

```python
CONFIG = {
    "WIDTH": 1080,
    "HEIGHT": 1920,
    "FPS": 30,
    "DURATION": 48,
    "NUM_SCENES": 10,
    "SEGMENT_DURATION": 4.8,  # 48 / 10
    "TEXT_SAFE_Y": 1200,      # Upper portion of bottom third, avoids TikTok UI
    "FONT": "DejaVuSans-Bold", # System fallback — NEVER use Arial (missing on Linux)
    "FONT_SIZE": 52,
    "STROKE_WIDTH": 5,
    "STROKE_COLOR": "black",
    "COLOR_SETUP": "white",
    "COLOR_HORROR": "#ff4444",
    "HORROR_START_TIME": 19.0,  # When text color switches to red
}
```

## Scene Image Mapping

10 scenes mapped to available images in `output/shorts/`:

| Scene | Time Window | Image (preferred) |
|-------|------------|-------------------|
| 1 | 0.0–4.8s | `scene1_heavy_sleeper.png` |
| 2 | 4.8–9.6s | `scene2_nightstand.png` |
| 3 | 9.6–14.4s | `scene3_morning_check.png` |
| 4 | 14.4–19.2s | `scene4_six_hours.png` |
| 5 | 19.2–24.0s | `scene5_weird_waveform.png` |
| 6 | 24.0–28.8s | `scene6_playback.png` |
| 7 | 28.8–33.6s | `scene7_alone.png` |
| 8 | 33.6–38.4s | `scene8_ancient.png` |
| 9 | 38.4–43.2s | `scene8_email.png` |
| 10 | 43.2–48.0s | `scene1_heavy_sleeper.png` (or any closing scene) |

## Font Fallback

**Critical:** `Arial` is NOT available on headless Linux. Always probe first:
```python
from PIL import ImageFont
try:
    ImageFont.truetype("Arial-Bold.ttf", 1)
    FONT = "Arial-Bold"
except OSError:
    FONT = "DejaVuSans-Bold"  # Always available on Debian/Ubuntu
```

## PIL Image Scaling (More Reliable)

MoviePy's ImageClip.resize behavior is inconsistent. Use PIL for pre-processing:
```python
from PIL import Image
import numpy as np

def load_and_crop_9x16(path, width=1080, height=1920):
    img = Image.open(path).convert("RGB")
    img_w, img_h = img.size
    target_ratio = width / height
    img_ratio = img_w / img_h

    if img_ratio > target_ratio:
        new_h = height
        new_w = int(img_w * (height / img_h))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        left = (new_w - width) // 2
        img = img.crop((left, 0, left + width, height))
    else:
        new_w = width
        new_h = int(img_h * (width / img_w))
        img = img.resize((new_w, new_h), Image.LANCZOS)
        top = (new_h - height) // 2
        img = img.crop((0, top, width, top + height))

    return np.array(img)
```

## TextClip Positioning at y=1200

```python
from moviepy import TextClip

txt = TextClip(
    text=text.strip(),
    font_size=52,
    color="#ff4444" if start_time >= 19 else "white",
    font="DejaVuSans-Bold",
    stroke_color="black",
    stroke_width=5,
    size=(980, None),
    method="caption",
    text_align="center",
).with_duration(end - start).with_start(start).with_position(("center", 1200))
```

## MoviePy v2 vs v1 API

This session used MoviePy 2.x. If using v1, substitute:
- `.with_start(t)` → `.set_start(t)`
- `.with_duration(d)` → `.set_duration(d)`
- `.with_position(p)` → `.set_position(p)`
- `.with_audio(a)` → `.set_audio(a)`

## Audio Sync from Whisper JSON

```python
import json

def load_whisper_segments(json_path):
    with open(json_path, 'r') as f:
        data = json.load(f)
    return data['segments']  # Each: {start, end, text, ...}
```

## Key Learning: y=1200 > y=1420

User explicitly required y=1200 (safe zone). Previous skill documentation incorrectly stated y=1420. The safe zone for TikTok/YouTube Shorts is the upper portion of the bottom third — y=1200 positions text well above the bottom UI bars while keeping it readable.
