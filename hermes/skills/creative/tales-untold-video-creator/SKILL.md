---
name: tales-untold-video-creator
description: Complete end-to-end Tales Untold horror short video pipeline with Ken Burns, proper text wrapping, and background music
target_model: anthropic/claude-opus-5
---

# Tales Untold Complete Video Pipeline

Full end-to-end agent for creating 9:16 vertical horror shorts from NOTHING.

## CRITICAL: Parent Agent Role
The PARENT AGENT must **NOT build videos directly**. The user explicitly stated: "I don't want you Cody to actually be building these videos." This skill is for dispatching to SUBAGENTS only.

## User Requirements (NON-NEGOTIABLE)

The user made these **explicit corrections** - they are REQUIRED:

### 1. PROPER TEXT WRAPPING (No Mid-Word Breaks)
- Words must NOT break mid-word: NO "conversa-tion", NO "whispe-red"
- Use manual word wrapping at word boundaries only
- See: `references/text-wrapping-technique.md`

### 2. KEN BURNS EFFECT (Required on EVERY Scene)
- Every image MUST have subtle zoom or pan motion
- No static images allowed - creates unprofessional look
- See: `references/ken-burns-effect.md`

### 3. BACKGROUND MUSIC (Required)
- Dark ambient horror music mixed underneath narration
- Creates atmosphere and tension
- See: `references/background-music-generation.md`

## Capabilities
- **Script Writing:** Original 200-250 word horror stories
- **Image Generation:** Fal.ai Flux
- **Audio Generation:** ElevenLabs (fallback to Edge TTS)
- **Transcription:** OpenAI Whisper
- **Video Composition:** MoviePy with Ken Burns + proper text + music

## Required APIs
- FAL_KEY for Fal.ai
- ElevenLabs API key (or fallback to Edge TTS)

## COMPLETE Pipeline

### PHASE 1: Script Writing
Create original 200-250 word horror story with supernatural twist.

### PHASE 2: Image Generation (10 scenes)
Generate 10 horror scenes via Fal.ai with 9:16 aspect ratio.

### PHASE 3: Audio Generation
Generate narration using ElevenLabs or Edge TTS fallback.

### PHASE 4: Transcription
Whisper for exact word-level timestamps.

### PHASE 5: Video Composition with REQUIREMENTS

#### Text Rendering (REQUIRED)
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
- `references/text-wrapping-technique.md` - Manual word wrapping
- `references/ken-burns-effect.md` - Motion effects
- `references/background-music-generation.md` - Audio generation

## Pitfalls
- **Parent agent building video** - User explicitly said NOT to do this
- **Mid-word text breaks** - Use manual wrapping
- **Static images** - Ken Burns REQUIRED
- **No background music** - Music REQUIRED
- **Text cutoff** - Position at y=1200 max

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