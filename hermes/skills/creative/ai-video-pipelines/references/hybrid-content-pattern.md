# Hybrid Content Pattern: Human-Crafted Stories + API Media

Session: 2026-09-13 (Tales Untold)

## Overview

When user prefers direct creative control over AI story generation. Reduces API costs, enables quality review before any generation spend.

**Workflow:**
1. **You write stories** → Batch of 5-10 creative pieces (hook + twist + mood + visual)
2. **User selects** → Review, pick best before any API calls
3. **Poyo generates voice** → ElevenLabs via Poyo (~3 credits per 15s)
4. **Fal.ai generates images** → Flux Ultra, 3-5 scenes per story (~$0.15-0.25)
5. **Assemble and publish** → MoviePy with transitions

## Format Options

### Option A: Micro-Story (12-15 seconds)
**Best for:** Quick hooks, high volume, rapid testing

| Element | Details |
|---------|---------|
| **Duration** | 12-15s |
| **Images** | 1 static background |
| **Structure** | Hook → Twist |
| **Text** | Hook (white, first 4s), Twist (red, remaining) |

**Assembly:**
```python
hook = TextClip(text=hook_text, color='white').with_duration(4)
twist = TextClip(text=twist_text, color='#ff4444').with_start(4)
bg = ImageClip('image.png').with_duration(voice.duration)
final = CompositeVideoClip([bg, hook, twist])
```

### Option B: Extended Narrative (60 seconds) ← **RECOMMENDED**
**Best for:** Full storytelling, YouTube Shorts algorithm, engagement

| Timestamp | Section | Duration | Content |
|-----------|---------|----------|---------|
| 0-15s | Setup | 15s | Establish normal world |
| 15-30s | Rising tension | 15s | Something's off |
| 30-45s | Climax | 15s | Discovery/horror moment |
| 45-60s | Twist reveal | 15s | The gut punch |

**Total:** 4 images, ~60 seconds of voice

**Assembly:**
```python
scenes = [
    ImageClip('scene1.png').with_duration(15),
    ImageClip('scene2.png').with_duration(15),
    ImageClip('scene3.png').with_duration(15),
    ImageClip('scene4.png').with_duration(15),
]
video_sequence = concatenate_videoclips(scenes)
final = CompositeVideoClip([video_sequence, ...text_overlays...])
```

## Example: Tales Untold Extended Story (60s)

**Story: The Sleep Recorder**

**Scene 1 - Setup (0-15s):**
> "I've always been a heavy snorer. My girlfriend convinced me to record my sleep, hoping a doctor could help. I placed my phone on the nightstand and fell asleep."

**Scene 2 - Rising Tension (15-30s):**
> "The next morning, I checked the recording. Six hours of audio. But something was wrong with the waveform — long stretches where the pattern looked like two voices overlapping."

**Scene 3 - Climax (30-45s):**
> "I isolated a section from 3 AM. When I played it back, I heard myself speaking in full sentences. Clear conversations. But I was alone in the apartment. And the words weren't English."

**Scene 4 - Twist (45-60s):**
> "I sent the audio to a linguistics professor. His email back still haunts me. He said this language died 600 years ago. And whoever is speaking it... is asking when they can come through."

## Image Prompts by Scene

**Scene 1 (Setup):**
```
A cozy modern bedroom at night, person peacefully sleeping in bed, 
smartphone on nightstand with recording app glowing, warm ambient 
lighting, peaceful atmosphere, photorealistic, cinematic
```

**Scene 2 (Waveform):**
```
Close-up of smartphone screen showing complex audio waveform recording 
app, strange overlapping patterns, person finger touching screen in 
morning light, mysterious atmosphere, photorealistic
```

**Scene 3 (Possession):**
```
Same person sleeping in bed but now with eyes open glowing faintly, 
mouth slightly open speaking, dark supernatural shadowy presence 
above bed, horror atmosphere, dramatic lighting, cinematic
```

**Scene 4 (Twist):**
```
Computer screen showing email with chilling message about ancient 
dead language, occult symbols reflected in monitor glass, dark room, 
silhouette of person in front of screen, dread atmosphere, horror
```

## Cost Comparison

| Element | 15s Version | 60s Version |
|---------|-------------|-------------|
| Stories | You write | You write |
| Voice | ~3 credits | ~12 credits |
| Images | 1 (~$0.05) | 4 (~$0.20) |
| **Total** | ~$0.10 | ~$0.35 |

**Note:** 60s format uses ~3.5x more credits but performs better on Shorts algorithm.

## Visual Style

- **Format:** 9:16 vertical (1080×1920)
- **Transitions:** Simple cuts (0.3s) or subtle fades (0.5s)
- **Text:** White for setup, red (#ff4444) for twist, black stroke on all
- **Font:** Absolute path required: `/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf`
- **Pacing:** Match text appearance to voice narration
- **Branding:** End card with subscribe CTA (last 5s)

## Provider Strategy

**Recommended for Tales Untold / similar projects:**

| Component | Provider | Model | Why |
|-----------|----------|-------|-----|
| **Stories** | You (Hermes) | — | Zero cost, creative control |
| **Voice** | Poyo | `elevenlabs-v3-tts` | Reliable, async |
| **Images** | **Fal.ai** | `flux-pro/v1.1-ultra` | Faster, more reliable than Poyo |
| **Video** | MoviePy | — | Local assembly |

## Pitfalls

- **Poyo images unreliable:** `gpt-4o-image` often returns "Server exception". **Use Fal.ai as primary.**
- **MoviePy font paths:** Use absolute paths — system font names don't resolve.
- **60s voice cost:** Longer scripts use more Poyo credits (~3 credits per 15s).
- **Fal synchronous:** No polling — returns result directly in 2-5s.
- **Image sizing:** Fal accepts any dimensions divisible by 16 (1080×1920 works).
- **Fal dimensions:** Must be divisible by 16, max 3840px edge.
- **AI text artifacts in images:** Flux and other models often generate garbled text ("Thi language iss ancient dead language?", "CHARTEST"). **Always include "NO TEXT NO WORDS NO LETTERS" in prompts** for scenes that should be text-free. Regenerate if artifacts appear.
- **Text synchronization:** Text overlays must match actual narration timing. Parse the audio transcript or use hardcoded timestamps aligned with the voice script. Misaligned text breaks immersion.
- **MoviePy TextClip API:** Use `text=` (not `txt=`) and `font_size=` (not `fontsize=`) in newer versions.
- **System font availability:** Arial may not exist. Check `fc-list` first or use common fallbacks like DejaVu Sans paths.

## When to Use Hybrid

✅ **Use when:**
- User is creative writer/editor
- Quality control matters (review before generation)
- Cost optimization priority
- Stories need specific voice/brand tone
- 60s format needed for Shorts algorithm

❌ **Don't use when:**
- Fully automated batch generation needed
- User wants variety without curation
- Time is more valuable than cost
- 12-15s micro-stories sufficient

## Update Log

- **2026-09-13:** Initial hybrid pattern (15s micro-stories)
- **2026-09-13:** Extended to 60s format with 4-image structure, Fal.ai integration
- **2026-09-13:** Added AI text artifact prevention, text sync timing, MoviePy API notes
