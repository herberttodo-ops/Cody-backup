---
name: ai-video-pipelines
description: Build end-to-end automated video generation pipelines using async AI APIs
category: creative
tags:
  - video
  - automation
  - ai
  - ffmpeg
  - content-creation
---

# AI Video Pipelines

Build end-to-end automated video generation pipelines using async AI APIs. Covers story generation, voice synthesis, image generation, video assembly, and publishing.

## When to Use

- Automated YouTube Shorts/TikTok/Reels generation
- AI-narrated content with custom visuals
- Batch video production from text prompts
- Any workflow needing: LLM → Voice → Images → Video → Publish

## Architecture Pattern

```
Story Generation → Voice Synthesis → Image Generation → Video Assembly → Upload
       (LLM)            (TTS)            (Image)           (FFmpeg)      (Platform)
```

All AI operations use **async task APIs**: submit → poll → download.

## Core Components

### 1. Authentication: Poyo Key Format

**Critical:** Poyo keys include the `sk-` prefix in the actual key value.

```bash
# ❌ Wrong - returns 401 Invalid API key
Authorization: Bearer jLzbNumV7mmGWYT...

# ✅ Correct
Authorization: Bearer sk-jLzbNumV7mmGWYT...
```

### 2. Async Task Client Pattern

Most AI providers (Poyo, Replicate, Fal) use the same pattern:

```python
# Submit task → Get task_id
task_id = await client.submit(payload)

# Poll until complete
result = await client.poll_until_done(task_id)

# Download output files
await client.download(result["files"][0]["url"], output_path)
```

See `references/poyo-client.py` for full implementation.

### 3. Provider Selection (Hybrid Strategy)

| Provider | Models | Strengths |
|----------|--------|-----------|
| **Poyo** | GPT-4o-image, claude-sonnet-5, elevenlabs-v3-tts | One API key, credit-based |
| **Replicate** | Open-source models | Good for specific models |
| **Fal** | Fast inference | Low latency |
| **OpenAI** | GPT-4o-mini | Chat/LLM when Poyo unavailable |
| **ElevenLabs** | Multilingual v2 | Voice when Poyo unavailable |

**Hybrid when Poyo models unavailable:**
Poyo model availability varies by account. If chat/voice models return 404:

| Component | Provider | Model |
|-----------|----------|-------|
| Stories | OpenAI | `gpt-4o-mini` |
| Voice | ElevenLabs | `eleven_multilingual_v2` |
| Images | **Poyo** | `gpt-4o-image` |

This consolidates from 3 separate keys to 2 (OpenAI+ElevenLabs share one approach, Poyo for images).

### 4. Poyo-Specific Notes

- **Image model**: `gpt-4o-image` (4 credits per generation)
- **Chat model**: Use `claude-sonnet-5` (cost-efficient), NOT `claude-fable-5-1`
- **Voice model**: `elevenlabs-v3-tts` (uses `"voice"` field, not `"voice_id"`)
- See `references/poyo-api-discovery.md` for full API details
- Async pattern: submit → poll `/api/generate/status/{task_id}` → download

### 6. Voice-to-Text Caption Synchronization (Critical)

**The Issue**: Audio captions must match voiceover word-for-word. TTS providers may merge lines, so the text actually spoken can drift from the input.

**Solution**: Script-First Workflow
1. ✍️ Write script → Save to `.txt` file
2. 🎙️ Generate voice FROM that exact file  
3. 📝 Use SAME file for captions
4. ✅ Caption count CAN exceed visual scene count - more captions ensure full coverage

**Key Rules**:
- NEVER guess at voiceover text
- Captions = Script = Voice (same source)
- More caption segments than images is OK for engagement (4-6s per visual scene)
- Position captions at y=1300 to avoid bottom cutoff

See `references/voice-text-sync-workflow.md` for complete details.

## Project Structure

```
project/
├── scripts/
│   ├── poyo_client.py      # Async API client
│   ├── generate_story.py   # LLM story generation
│   ├── synthesize_voice.py # TTS via async API
│   ├── generate_image.py   # Image generation
│   ├── assemble_shorts.py  # FFmpeg assembly
│   ├── upload_youtube.py   # YouTube upload
│   └── pipeline.py         # Orchestrator
├── prompts/
│   └── system.txt          # LLM system prompt
├── output/
│   ├── shorts/             # Generated videos
│   └── thumbnails/         # Generated thumbnails
└── data/
    └── archive.json        # Story history
```

## Quality Gates

Always implement AI output validation:

```python
# Score generated content, retry if below threshold
best = await generate_batch(size=15)
if best.score < threshold:
    best = await retry_with_feedback(best.issues)
```

## Alternative: Human-Crafted Stories

When the user prefers direct story generation over AI APIs (as Andrew does for Tales Untold):

**Workflow:**
1. **You (Hermes) write stories** → Batch of 5 supernatural micro-stories
2. **User selects the best** → Review hook, twist, mood, visual potential
3. **Poyo generates assets** → Voice + images only (saves credits)
4. **Assemble and publish** → Same pipeline from step 3 onwards

**Advantages:**
- **Zero API cost** for story generation
- **Quality control** — user selects before any API calls
- **Poyo credits conserved** — only used for voice (~0.9 credits) and images (~4 credits)
- **Creative control** — user shapes the content before automation takes over

See `references/twisty-microfiction-pattern.md` for story generation guidelines.

## Caption Synchronization Workflow

**Critical**: Captions must match voiceover EXACTLY. Use the Script-First pattern:

1. **Write script** → Save to `script.txt`
2. **Generate voice** from `script.txt`
3. **Use same script** for captions
4. **Caption density > Image density** — more caption segments than visual scenes is OK

See `references/voice-text-sync-workflow.md` for full details and troubleshooting.

### Key Rules

| Rule | Detail |
|------|--------|
| **Script storage** | ALWAYS save script to file before voice generation |
| **Word-for-word** | Captions must be EXACT text, no paraphrasing |
| **Caption density** | Can have more captions than images (e.g., 9 captions, 8 scenes) |
| **Scene timing** | 4-6 seconds per visual scene for engagement |
| **Text position** | y=1300 to avoid bottom cutoff |
| **High contrast** | 4-5px stroke opposite color of text fill |

## Pitfalls

### Image Generation
- **AI text artifacts**: Flux/Fal models often generate garbled text in images. **Always include "NO TEXT NO WORDS NO LETTERS" in prompts** to avoid unprofessional artifacts like "CHARTEST" or fake languages.
- **9:16 cropping**: Images must be cropped to 1080x1920 exactly. Use PIL to resize then center-crop to avoid black bars or stretched content.

### Video Assembly (MoviePy)
- **API changes**: Newer MoviePy uses `text=` and `font_size=`, not `txt=` and `fontsize=`. Check with `help(TextClip.__init__)` if unsure.
- **Font availability**: Arial often unavailable on Linux. Use system fonts like 'DejaVuSans' which ships with most distros.
- **Text positioning**: Place text at y=1300 (not 1400-1600) to avoid bottom cutoff on mobile.
- **High contrast strokes**: Use thick strokes (4-5px) matching the text color's opposite:
  - White text → 4px black stroke
  - Red text (#ff3333) → 5px black stroke  
  - Red on black bg → 4px white stroke

### Content Sync (CRITICAL — Read Before Any Video Build)

**I got this wrong multiple times. Learn from my mistakes.**

**Rule 1: NEVER guess the transcript**
- I assumed the narration matched the script I wrote. It didn't. The actual audio said something completely different.
- **Always transcribe first** if you don't have the exact script that generated the voice
- Options: Whisper (openai-whisper), WhisperX, or ask the user to provide the transcript

**Rule 2: Script-First Workflow (when generating new audio)**
1. ✍️ Write script → Save to `script.txt`
2. 🎙️ Generate voice FROM `script.txt`
3. 📝 Create captions FROM `script.txt`
4. ✅ All three are identical by definition

**Rule 3: Transcription-First Workflow (when audio already exists)**
1. 🎧 Transcribe the audio (Whisper, WhisperX)  
2. 📝 Use transcription as captions
3. 🎨 Generate images to match the story in the transcription

**Rule 4: Caption density > Scene density**
- More captions than images is not just "OK" — it is often REQUIRED for word-for-word coverage
- A 48s video might have 8 visual scenes but 12-15 caption segments
- Each caption segment = one continuous text overlay that changes when narration changes
- Visual scene changes every 4-6s for engagement; captions change when words change

**Rule 5: If user says "captions don't match voiceover"**
- Stop guessing. Transcribe the audio.
- Compare transcription to your captions.
- Fix by regenerating from the correct transcript OR by adjusting captions to match.

**Real example from this session:**

I **thought** the audio said:
> "I started recording my sleep to catch my snoring..."

The **actual** audio said:
> "I've always been a heavy snore. My girlfriend convinced me to record my sleep..."

I wasted 5+ iterations fixing other issues when the root cause was an entirely wrong transcript.

### Text Readability (High Contrast)

User had to ask multiple times before I got this right. Do it right the first time:

- **Stroke width**: 4-5px depending on text color
- **White text**: `stroke_color='black', stroke_width=4`
- **Red text (#ff3333)**: `stroke_color='black', stroke_width=5` (needs thicker stroke)
- **Red on black bg**: `stroke_color='white', stroke_width=4`
- **Font**: Use 'DejaVuSans' (system font, always on Linux) not 'Arial'
- **Position**: y=1300 (not 1400-1600) to avoid bottom cutoff on mobile

### ElevenLabs API Details
- API endpoint: `POST /v1/text-to-speech/{voice_id}`
- Key format: `sk_...` (must include `sk-` prefix)
- Valid voice IDs: `EXAVITQu4vr4xnSDxMaL` (Adam), `21m00Tcm4TlvDq8ikWAM` (Rachel)
- Models: `eleven_monolingual_v1` or `eleven_multilingual_v2`
- Returns: `audio/mpeg` binary

See `references/voice-text-sync-workflow.md` for complete workflow.

### General
- **Async timeouts**: Some tasks take 60-300s. Set generous timeouts.
- **File cleanup**: Downloaded temp files accumulate. Clean up.
- **Rate limits**: Batch submits, don't parallelize polling.
- **FFmpeg filter complexity**: Test filter graphs incrementally.
- **Provider model availability**: Poyo chat/voice models may not be available on all accounts. Test first.
- **Poyo key format**: Must include `sk-` prefix in the Authorization header value itself.
- **Cost efficiency**: Prefer `claude-sonnet-5` over `claude-fable-5-1` for chat - cheaper with similar quality.

## References

- `references/poyo-api-discovery.md` - Complete Poyo API reference with working models
- `references/fal-ai-integration.md` - Fal.ai image generation (faster fallback when Poyo fails)
- `references/poyo-client.py` - Full async client implementation
- `references/story-generator.py` - LLM story generation with scoring
- `references/video-assembler.py` - FFmpeg assembly code
- `references/voice-text-sync-workflow.md` - **Critical**: Voice-to-caption synchronization workflow (2025-09-14)
- `references/voice-text-sync-workflow.md` - **CRITICAL**: How to keep captions word-for-word synced with voiceover (script-first workflow)
- `references/voice-text-sync-workflow.md` - **CRITICAL**: Ensuring captions match voiceover exactly

## Caption Synchronization Workflow

**User requirement**: Captions must be word-for-word accurate with voiceover.

**Workflow**:
1. Write script → Save to `script.txt`
2. Generate voice FROM `script.txt`
3. Create captions FROM same `script.txt`
4. Result: Guaranteed sync

**See**: `references/voice-text-sync-workflow.md` for full details on script-first workflow, caption density vs scenes, and troubleshooting mismatches.

## Provider Selection (Updated 2026-09-13)

**Current recommendation for Tales Untold / similar projects:**

| Component | Provider | Model | Why |
|-----------|----------|-------|-----|
| **Stories** | You (Hermes) | — | Zero cost, creative control |
| **Voice** | Poyo | `elevenlabs-v3-tts` | Reliable, ~3 credits |
| **Images** | **Fal.ai** | `flux-pro/v1.1-ultra` | Faster, more reliable than Poyo |
| **Video** | MoviePy | — | Local assembly |

**When Poyo images fail:** Fal.ai `flux-pro/v1.1-ultra` is the validated fallback. ~2-5s generation, higher quality than Poyo's `gpt-4o-image`.

## Example: Tales Untold

Complete horror Shorts pipeline using Poyo:
- Stories: `claude-sonnet-5` with quality scoring
- Voice: `elevenlabs-v3-tts` (Adam voice)
- Images: `gpt-4o-image` (9:16 for Shorts)
- Assembly: FFmpeg with Ken Burns + text overlays
- Upload: YouTube Data API

See references/ for implementation details.
