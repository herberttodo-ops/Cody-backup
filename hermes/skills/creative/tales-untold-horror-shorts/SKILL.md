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
- **NO intro slide / title card** — Video starts immediately on first frame (Scene 1 at 0s). User explicitly rejected title cards.
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
- **Scene timing:** Map Whisper segments to scenes visually. Each scene covers ~8-14s of narration.
- **Duration:** Must match actual narration length exactly (read from Whisper `segments[-1]["end"]`). Do NOT guess. Add 2-3s for CTA. Typical targets: ~55-60s for 140-180 word stories, ~80s for longer stories.
- **Music continues through end:** Use `amix=inputs=2:duration=longest` so background music plays during CTA after narration ends.
- **Image count:** ~5-7 scenes for 55-60s, ~7-10 scenes for longer stories.

### Content Requirements
- **ALWAYS** transcribe audio with Whisper first
- **NEVER** guess captions — use EXACT Whisper transcript text, word-for-word
- **Caption timing** — use exact segment start/end times from Whisper, offset by +0.2s fade-in and -0.3s fade-out
- **NEVER** paraphrase or "improve" caption text — the voiceover IS the ground truth
- **NEVER** use AI-generated images with text artifacts
- Clean, photorealistic horror imagery

### Duration Checklist
| Check | Rule |
|-------|------|
| ✅ Get actual narration length | Read from Whisper transcript `segments[-1]["end"]` |
| ✅ Never guess duration | User said "stories should be ~60 seconds, scripts 140-180 words" |
| ✅ Define `data-duration` from transcript end time + 2-3s for CTA |
| ✅ Music continues through end | Use `amix=inputs=2:duration=longest` so music plays after narration |

### Music
- Use Andrew's provided tracks in `assets/music/` (stored permanently).
- **Never** generate synthetic drone music.
- Volume: ~0.4x under narration.

### Story Guidelines
| Target | Value |
|--------|-------|
| Word count | 140-180 words |
| Duration | ~55-60 seconds |
| Complexity | Simple — avoid multiple numbers/timestamps per story |
| Narration fallback | edge-tts `en-US-GuyNeural` when POYO TTS unavailable |

---

## Production Workflow v3 (HyperFrames + Hybrid Pipeline)

### CRITICAL: Voice is Brand — Never Silent Fallback
Adam (ElevenLabs) is the narrative voice for Tales Untold. If POYO TTS fails:

1. **Check POYO docs** at `https://docs.poyo.ai/api-manual/music-series/elevenlabs-tts-turbo-2-5`
2. **Current working model:** `elevenlabs-tts-turbo-2-5` (NOT `elevenlabs`)
3. **Request format:**
```json
POST https://api.poyo.ai/api/generate/submit
{
  "model": "elevenlabs-tts-turbo-2-5",
  "input": {
    "voice": "Adam",
    "text": "Your story here..."
  }
}
```
4. **Response format:** `{"code": 200, "data": {"task_id": "...", "status": "not_started"}}` — read from `data.task_id`, not top-level
5. **Only if POYO is genuinely unavailable** → use edge-tts `en-US-GuyNeural` with rate +5% as last resort
6. **NEVER silently fall back** — tell the user the voice changed

---

**Why HyperFrames:** HTML/CSS → MP4 via headless Chrome = smoother Ken Burns, atmospheric effects, better text rendering than MoviePy PIL.

**Architecture:**
```
HyperFrames (HTML/CSS) → Silent MP4 (visuals)
         ↓
MoviePy (audio mix) → Final MP4 (voice + music + CTA)
```

### Image Style: Stephen Gammell / Scary Stories

**CRITICAL — USER CORRECTED:** Post-processing (CSS filters on color photos) does NOT work. The user explicitly said: "Post processing does not work." Images MUST be generated natively in Gammell style using the correct prompt at the source. Filtered color photos always look like filtered photos, not authentic ink wash illustrations.

**Use POYO nano-banana-2-lite** (best Gammell match found; flux-schnell rejected as too clean/modern). Prompt elements:
- "ink wash illustration in Stephen Gammell style"
- "deep black shadows pooling like liquid ink"
- "textured aged book paper"
- "crosshatched shadows"
- "monochrome grayscale, high contrast chiaroscuro"
- "Scary Stories to Tell in the Dark illustration"

**Working POYO API format:**
```json
POST https://api.poyo.ai/api/generate/submit
{
  "model": "nano-banana-2-lite",
  "input": {
    "prompt": "A person sleeping in bed, moonlight through window, ink wash illustration in Stephen Gammell style...",
    "size": "9:16"
  }
}
```
- `size: "9:16"` — aspect ratio string, NOT pixel dimensions
- No `resolution` or `quality` param for nano-banana-2-lite
- Poll `GET https://api.poyo.ai/api/generate/status/{task_id}` until `"finished"`
- Download `result["files"][0]["file_url"]` immediately — URLs expire

Common failures:
- `gpt-image-2` with custom sizes → "Custom size requires resolution 2K or 4K" (nano-banana avoids this)
- Complex multi-line prompts → task fails; keep prompts concise
- Forgotten auth header `Authorization: Bearer $POYO_API_KEY`

**Step 1: Build HyperFrames Composition**

Create `composition.html`:
```html
<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=1080, height=1920">
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <style>
    html, body { width: 1080px; height: 1920px; background: #020202; }
    .scene { position: absolute; inset: 0; opacity: 0; }
    .scene img { position: absolute; min-width: 125%; min-height: 125%; object-fit: cover; }
    .caption { 
      position: absolute; bottom: 240px; left: 50%; transform: translateX(-50%);
      width: 94%; text-align: center; color: #fff; font-size: 54px; font-weight: bold;
      text-shadow: -4px -4px 0 #000, 4px -4px 0 #000, -4px 4px 0 #000, 4px 4px 0 #000;
      z-index: 10; opacity: 0;
    }
    .caption.horror { color: #ff2222; }
    
    /* INTENSE VIGNETTE — heavy dark corners */
    .vignette {
      position: absolute; inset: 0;
      background: radial-gradient(
        ellipse at 50% 38%,
        transparent 0%, transparent 12%,
        rgba(0,0,0,0.6) 35%,
        rgba(0,0,0,0.95) 60%,
        rgba(0,0,0,0.98) 100%
      );
      z-index: 5; pointer-events: none;
    }
    
    /* VISIBLE GRAIN — film texture */
    .grain {
      position: absolute; inset: 0;
      opacity: 0.38;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 400 400' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='5' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
      z-index: 6; pointer-events: none;
    }
    
    /* FILM SCRATCHES */
    .scratches {
      position: absolute; inset: 0;
      opacity: 0.12;
      background: repeating-linear-gradient(90deg, transparent, transparent 1px, rgba(255,255,255,0.04) 1px, rgba(255,255,255,0.04) 2px);
      z-index: 7; pointer-events: none;
    }
  </style>
</head>
<body>
  <div class="scene" id="s1"><img src="./scene1.png"></div>
  <!-- scenes 2-10... -->
  <div class="caption" id="c0">Hook text here</div>
  <!-- captions 1-19... -->
  
  <div class="vignette"></div>
  <div class="grain"></div>
  <div class="scratches"></div>

  <script>
    const tl = gsap.timeline({ paused: true });
    window.__timelines = [tl];
    const SD = 8.13; // scene duration
    
    // Scene 1 + Ken Burns
    tl.to('#s1', { opacity: 1, duration: 0.4 }, 0);
    tl.fromTo('#s1 img', 
      { scale: 1.08, x: 0 }, 
      { scale: 1.24, x: -50, duration: SD, ease: 'none' }, 0);
    
    // Caption timing (from Whisper)
    tl.to('#c0', { opacity: 1, duration: 0.25 }, 0.0);
    tl.to('#c0', { opacity: 0, duration: 0.3 }, 7.38);
    
    // ... more scenes and captions
  </script>
</body>
</html>
```

**Step 2: Render with HyperFrames**
```bash
npx hyperframes render --composition composition.html --format mp4 --fps 30 --quality looks --output visuals.mp4
```

**Step 3: Add Audio in MoviePy**
```python
from moviepy import VideoFileClip, AudioFileClip, CompositeAudioClip, TextClip, CompositeVideoClip

# Load HyperFrames visual
video = VideoFileClip("visuals.mp4")

# Mix audio
narration = AudioFileClip("adam_voice.mp3")
music = AudioFileClip("background.mp3").subclipped(0, narration.duration)
music = music.with_volume_scaled(0.6)
final_audio = CompositeAudioClip([narration, music])

# Add CTA overlay (last 4s)
cta = TextClip(
    text="LIKE & SUBSCRIBE\nfor more Tales Untold",
    font="DejaVuSans-Bold", font_size=72, color="white",
    stroke_color="black", stroke_width=6,
    size=(1000, None), method="caption", text_align="center"
).with_position("center").with_start(video.duration - 4).with_end(video.duration)

final = CompositeVideoClip([video, cta], size=video.size)
final = final.with_audio(final_audio)
final.write_videofile("FINAL.mp4", fps=30)
```

### Atmospheric Effects (CSS in HyperFrames)

| Effect | CSS Implementation | Recommended Values |
|--------|-------------------|-------------------|
| **Vignette** | `radial-gradient()` | `transparent 0% 18%, rgba(0,0,0,0.5) 42%, rgba(0,0,0,0.85) 68%, rgba(0,0,0,0.98) 100%` |

### Vignette Balancing
If user says "hard to see center" or "too dark":
- **Expand transparent zone:** 12% → 18%
- **Reduce mid-opacity:** 0.6 → 0.5
- **Ease corner falloff:** 0.95 → 0.85
- Keep corners dark (0.98) — maintain atmosphere
- Never remove vignette entirely — it's part of the Tales Untold look
| **Grain** | SVG `feTurbulence` noise | opacity: 0.35-0.42, baseFrequency: 0.85 |
| **Scratches** | `repeating-linear-gradient()` | opacity: 0.10-0.15, 1-2px lines |

### OPTION B: MoviePy-Only Pipeline (Legacy)

For cases where HyperFrames isn't available or simpler motion is acceptable.

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

### IMPROVEMENT 3: Background Music
**NEVER generate synthetic drone music.** Andrew provided two tracks specifically:

- `assets/music/tales_track_1.mp3` — Primary (100s, ~-15dB, stereo 48kHz)
- `assets/music/tales_track_2.mp3` — Alternate (90s, ~-16dB, stereo 48kHz)

Mix audio (narration + provided music):
```python
from moviepy import AudioFileClip, CompositeAudioClip

narration = AudioFileClip("output/narration_adam_poyo.mp3")
music = AudioFileClip("assets/music/tales_track_1.mp3").subclipped(0, narration.duration)
music = music.with_volume_scaled(0.4)  # ~-12dB under narration

mixed = CompositeAudioClip([narration, music])
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
- `references/whisper-timestamps.md` — Example transcript format
- `references/hyperframes-setup.md` — HyperFrames setup, timeline registration, common issues
- `references/poyo-edge-cases.md` — POYO API quirks: response nesting (`data.task_id`), TTS model changes (`elevenlabs-tts-turbo-2-5`), shell key mangling
- `templates/hyperframes-base.html` — Known-good composition template
- `templates/segments.json` — Scene mapping template