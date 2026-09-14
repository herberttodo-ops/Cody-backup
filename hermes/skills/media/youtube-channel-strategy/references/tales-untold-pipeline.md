# Tales Untold — AI Video Pipeline Reference

Full automation pipeline for AI-generated YouTube Shorts (supernatural storytelling).
Built Sep 13, 2026 for Andrew's "Tales Untold" channel.

## Location
`~/.openclaw/workspace/tales-untold/`

## Pipeline Architecture

```
Orchestrator (pipeline.py)
  ├── Story Generator (generate_story.py) — GPT-4o-mini, quality gate 7.0
  ├── Voice Synthesizer (synthesize_voice.py) — ElevenLabs Adam + FFmpeg reverb
  ├── Image Generator (generate_image.py) — OpenRouter DALL-E / placeholder
  ├── Video Assembler (assemble_shorts.py) — FFmpeg Ken Burns + text overlays
  └── YouTube Uploader (upload_youtube.py) — Data API v3
```

## Three Operation Modes

| Mode | Uploads? | Use For |
|------|----------|---------|
| dryrun | No | Testing, debugging |
| semi | No (holds for review) | Daily production with human oversight |
| full | Yes | Fully hands-off |

## Key Configuration

Environment variables in `.env`:
- OPENAI_API_KEY — story generation
- ELEVENLABS_API_KEY — voice synthesis
- OPENROUTER_API_KEY — image generation (fallback)
- YOUTUBE_CLIENT_SECRETS — OAuth2 credentials file
- YOUTUBE_CREDENTIALS — saved OAuth tokens

## Daily Execution

```bash
cd ~/.openclaw/workspace/tales-untold
source venv/bin/activate
python scripts/pipeline.py --mode semi
```

Cron (daily 6 AM EST):
```
0 11 * * * cd ~/.openclaw/workspace/tales-untold && source venv/bin/activate && python scripts/pipeline.py --mode semi >> logs/daily.log 2>&1
```

## Quality Gate

Stories scored on coherence, atmosphere, originality, punch (1-10 each).
Minimum 7.0 average to pass. Auto-retry up to 3 batches of 15.

## ElevenLabs Voice Spec

- Voice: Adam (pNInz6obpgDQGcFmaJgB)
- Model: eleven_multilingual_v2
- Settings: stability=0.7, similarity_boost=0.85, style=0.3
- Post-processing: aecho reverb, highpass 80Hz, lowpass 8kHz, compression, loudnorm -16 LUFS

## Video Spec (Shorts)

- Format: 1080x1920, 9:16, 60s max
- Background: Ken Burns slow zoom (1.0 to 1.15 over 60s)
- Text overlays: Hook at 0s (4s), Twist at 30s (5s), Brand at 55s
- Audio: Voice + ambient music (ducked 12dB under voice)

## Next Extensions

1. Long-form track (10-18 min) — Claude story generation, multi-scene images
2. Auto-Shorts from long-form — extract best 60s clip automatically
3. Community post automation — polls for next story topic
4. Music library — replace silent placeholder with dark ambient loops

## Monthly Costs

~$12/mo: OpenAI (~$2), ElevenLabs (~$5), OpenRouter images (~$5)
