---
name: tales-untold-video-creator
description: Complete end-to-end Tales Untold horror short video pipeline with Ken Burns, proper text wrapping, and background music
target_model: anthropic/claude-opus-5
---

# Tales Untold Complete Video Pipeline

Full end-to-end agent for creating 9:16 vertical horror shorts from NOTHING.

## User Communication Style (Andrew)

When working on Tales Untold:
- **Be concise.** Report what was done, not what was considered.
- **Skip the preamble.** Do not narrate "First I will X, then Y" — just execute and report results.
- **Surface errors directly.** If a tool fails, state the failure and the blocker plainly. Do not wrap it in multiple paragraphs of explanation.
- **Confirm when uncertain.** "Music needs attention" is ambiguous — ask explicitly whether it's volume, track swap, or new generation before acting.
- **Show, don't tell.** Upload the file. Share the Drive link. Let the artifact speak.
The PARENT AGENT must **NOT build videos directly**. The user explicitly stated: "I don't want you to actually be building these videos." This skill is for dispatching to SUBAGENTS only.

## User Requirements (NON-NEGOTIABLE)

The user made these **explicit corrections** - they are REQUIRED:

### 1. PROPER TEXT WRAPPING (No Mid-Word Breaks)
- Words must NOT break mid-word: NO "conversa-tion", NO "whispe-red"
- Use manual word wrapping at word boundaries only
- See: `references/text-wrapping-technique.md`

### 2. KEN BURNS EFFECT (Required on EVERY Scene)
- Every image MUST have subtle zoom or pan motion
- No static images allowed
- If MoviePy `vfx.Resize` produces invisible motion, pre-transform images with Pillow
- See: `references/ken-burns-effect.md`

### 3. BACKGROUND MUSIC (Required)
- Dark ambient horror music mixed underneath narration
- **User preference: subtle background level, NOT prominently audible**
- Measure source music first: `ffmpeg -i music.wav -af volumedetect`
- If source mean is ~-15 dB, **start at 0.5–0.7× scale** and adjust from there
- User specifically dialed music DOWN from 3.0× to 0.6× when it was too loud — prefers a subtle bed under narration
- Never assume "more audible = better" — verify with user or start conservative
- Always verify on the FINAL MIXED mp4 with volumedetect, not just source files
- See: `references/music-volume-and-mixing.md`

### 4. VOICE: ELEVENLABS ADAM (via POYO)
- Direct ElevenLabs key often invalid or missing; POYO is the reliable route
- Model: `elevenlabs-v3-tts`, input field: `voice: "Adam"`
- **Never** include `voice_id` or `model_id` in the POYO payload — they are rejected
- POYO key validation: submit a 1-sentence test first; if it returns `{code: 401}`, key is bad — do NOT proceed with the full script
- If POYO also fails, fall back to Edge-TTS immediately
- See: `references/poyo-elevenlabs-tts.md`

## Capabilities
- **Script Writing:** Original 200-250 word horror stories
- **Image Generation:** POYO (gpt-image-2.5-flare) or FAL.ai Flux
- **Audio Generation:** ElevenLabs (fallback to Edge TTS)
- **Transcription:** OpenAI Whisper
- **Video Composition:** HyperFrames + MoviePy hybrid

## Required APIs
- POYO_API_KEY for POYO image generation and TTS
- FAL_KEY as fallback

## COMPLETE Pipeline

### PHASE 1: Script Writing
Create original 200-250 word horror story with supernatural twist.

### PHASE 2: Image Generation (10 scenes)
Generate 10 horror scenes via POYO with Gammell style.

### PHASE 3: Audio Generation
Generate narration using ElevenLabs or Edge TTS fallback.

### PHASE 4: Transcription
Whisper for exact word-level timestamps.

### PHASE 5: Video Composition (Hybrid Pipeline — Recommended)

**Visuals:** HyperFrames renders HTML+GSAP to MP4 (Ken Burns, grain, vignette, captions)
**Audio:** MoviePy overlays Adam voice + background music onto HyperFrames silent video

**Why hybrid:**
- HyperFrames: Smooth CSS Ken Burns, film grain, vignette, sharp browser-rendered text
- MoviePy: Precise audio mixing (voice + music), familiar audio pipeline already dialled in

#### Full HyperFrames Composition (auto-generated from transcript)

**User preference: Gammell style (Scary Stories to Tell in the Dark)**

**CRITICAL: Post-processing does NOT work.** Images must be generated NATIVE in Gammell style via the image generation prompt — not filtered after generation.

**Gammell Style Requirements (for image generation prompts):**
- **Prompt keywords:** "Stephen Gammell ink wash illustration," "deep black shadows pooling like liquid ink," "textured aged book paper," "monochrome grayscale," "high contrast chiaroscuro," "Scary Stories to Tell in the Dark illustration style"
- **Negative prompts:** color, bright lighting, digital art, smooth shading, 3D render, photograph, cartoon, anime, CGI, vibrant colors
- **Visual treatment:** Grayscale with high contrast, heavy vignette (post-render), serif italic typography for captions, slower Ken Burns motion
- **NO grain** — clean ink wash aesthetic (grain was too heavy at 38%, removed entirely)

**POYO Image Generation:**
- **Endpoint:** `POST https://api.poyo.ai/api/generate/submit`
- **Model:** `gpt-image-2.5-flare` (NOT `gpt-image-2`)
- **Size:** Aspect ratio string `"9:16"` (NOT pixel values)
- **Resolution:** Preset `"1K"`, `"2K"`, or `"4K"`
- **Correct payload:** `{"model": "gpt-image-2.5-flare", "input": {"prompt": "...", "size": "9:16", "resolution": "2K", "quality": "high"}}`
- **Poll:** `GET /api/generate/status/{task_id}` until `"finished"`
- **Complex prompts fail:** Simpler prompts (3-4 keywords) succeed more reliably

**Other Image Options:**
- **FAL/Flux:** Requires working auth key (may fail with "Authentication required")
- **OpenAI Image Gen:** Subject to rate limits (429 errors)
- **Fallback:** Generate images manually (Midjourney, DALL-E web)

See: `references/poyo-image-generation-api.md`, `references/hyperframes-atmospheric-effects.md`

Generate HTML with Python:
```python
import json
import html

data = json.load(open("transcript_adam.json"))
segments = data["segments"]

scene_dur = audio_duration / 10

# Gammell-style: slower, more ominous motion
ken_burns = [
    ("scale: 1.05, x: 0", "scale: 1.18, x: -30"),
    ("scale: 1.15, x: 25", "scale: 1.00, x: -20"),
    # ... 10 variations with smaller scale range
]

# Build <div class="scene"> + <div class="caption"> for each
# Build GSAP timeline: fade in → Ken Burns → captions → crossfade
# Register: window.__timelines = [tl]
```

**Critical:**
- Copy all scene images to same directory as HTML — use `./scene1.png`, not absolute/relative paths
- Duration inferred from GSAP timeline end — ensure timeline covers full 81.3s
- Render: `npx hyperframes render --composition composition.html --format mp4 --fps 30 --output video.mp4`

#### Hybrid Audio Assembly (MoviePy)
```python
from moviepy import AudioFileClip, CompositeAudioClip, VideoFileClip

visual = VideoFileClip("tales_visual_hf.mp4")  # HyperFrames silent output
voice  = AudioFileClip("narration_adam_poyo.mp3")
music  = AudioFileClip("background_music.mp3")

# User preference: 0.6× = subtle bed under narration
music = music.subclipped(0, voice.duration).with_volume_scaled(0.6)
music = music.with_effects([afx.AudioFadeOut(3.0)])

final_audio = CompositeAudioClip([voice, music])
final = visual.with_audio(final_audio)
final.write_videofile("FINAL_HYBRID.mp4", fps=30, codec="libx264", audio_codec="aac")
```

---

#### Legacy: Pure MoviePy Pipeline (fallback)
```python
def manual_word_wrap(text, max_chars=28):
    """Wrap text at word boundaries only - NO mid-word breaks."""
    words = text.split()
    lines = []
    current = ""
    for word in words:
        if len(current) + len(word) + 1 <= max_chars:
            current += " " + word if current else word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)
```

#### Ken Burns Effect (REQUIRED)
```python
def ken_burns_clip(image, duration, variation='zoom_in'):
    """Apply subtle motion to every scene."""
    if variation == 'zoom_in':
        return image.resized(lambda t: 1 + 0.15 * (t / duration))
    elif variation == 'pan_left':
        return image.with_position(lambda t: (50 - 100 * (t / duration), 'center'))
```

#### Background Music (REQUIRED)
```python
from moviepy import CompositeAudioClip

voice = AudioFileClip("audio.mp3")
music = AudioFileClip("music.wav").with_volume(0.12)  # -20dB
final_audio = CompositeAudioClip([voice, music])
```

## Reference Files
- `references/poyo-image-generation-api.md` — **POYO image generation** (correct payload, pitfalls, async pattern)
- `references/gammell-image-generation-guide.md` — Complete scene prompts and negative prompts for native Gammell-style generation
- `references/hyperframes-install-and-test-render.md` — HyperFrames setup + first render
- `references/hyperframes-full-composition-template.md` — Full 10-scene HTML+GSAP composition template for production
- `references/hyperframes-atmospheric-effects.md` — Grain, vignette, and Gammell style guide
- `references/text-wrapping-technique.md` — Manual word wrapping
- `references/ken-burns-effect.md` — Motion effects
- `references/background-music-generation.md` — Audio generation
- `references/music-volume-and-mixing.md` — Music level calibration and user preference

## Pitfalls
- **Parent agent building video** — User explicitly said NOT to do this
- **Mid-word text breaks** — Use manual wrapping
- **Static images** — Ken Burns REQUIRED
- **No background music** — Music REQUIRED
- **Text cutoff** — Position at y=1200 max
- **Black gaps between scenes** — Scene transitions must overlap (use 4.85s per scene not 4.8s) or add crossfadein(0.1) between clips
- **ElevenLabs key invalid** — ALWAYS validate key first. If rejected, immediately fall back to Edge TTS. Do NOT retry ElevenLabs with same key.
- **Background music too quiet** — After mixing, verify mean_volume > -30 dB with ffmpeg volumedetect. Boost if needed.
- **POYO image generation wrong parameters** — Use `"size": "9:16"` (aspect ratio) and `"resolution": "2K"` (preset), NOT pixel values like `"1200x2160"`. Use model `gpt-image-2.5-flare`, NOT `gpt-image-2`.
- **POYO complex prompts fail** — Long multi-line prompts with 10+ descriptors fail silently. Use concise 3-4 keyword prompts.
- **Image generation APIs failing** — FAL auth often fails, OpenAI hits rate limits (429). POYO is the reliable route with correct parameters.
- **Ken Burns invisible** — MoviePy vfx.Resize produces subtle motion that may not render visibly. Apply scale transforms via Pillow before MoviePy for reliable effect.
- **Google Drive video uploads** — Use existing `google_token.json` with Python SDK (googleapiclient). Resumable uploads handle 85MB files reliably.

## Output Files
```
output/
  script.txt
  shorts/scene{1..10}.png
  audio.mp3
  transcript.json
  background_music.wav  # REQUIRED
  FINAL_TALES_UNTOLD_SHORT.mp4
```