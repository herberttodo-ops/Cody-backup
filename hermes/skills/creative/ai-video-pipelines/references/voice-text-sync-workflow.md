# Voice-to-Text Caption Synchronization

**Problem**: Captions don't match voiceover because audio generation doesn't preserve exact input text.

**Root Cause**: TTS providers (ElevenLabs, etc.) may merge lines, change pacing, or interpret text. Without the exact output transcript, captions become approximations.

## The Two Workflows

### A. Script-First (generating new content)
```
1. Write script → Save as `script.txt`
2. Generate voice from `script.txt`
3. Use `script.txt` for captions
4. All three match by design
```

### B. Transcription-First (audio already exists — CRITICAL)
```
1. Run Whisper on existing audio to get transcript
2. Use transcript for captions
3. Generate images matching the transcribed story
4. All three match by design
```

**I made this mistake repeatedly in one session:** I assumed the narration matched the script I had written. The actual audio said something completely different. I wasted 5+ iterations fixing "sync issues" when the root cause was simply: **I never verified the transcript**.

**Always** transcribe first if you don't have the original script.

## When captions don't match voiceover

**Stop and diagnose before fixing.**

1. **Do you have the original script?**
   - Yes: Compare captions to script
   - No: Transcribe the audio

2. **Transcribe the audio** (if needed):
   ```bash
   pip install openai-whisper
   whisper audio.mp3 --model tiny --output_format json
   ```
   
   If torch install times out:
   ```bash
   pip install openai-whisper --no-deps
   pip install torch more-itertools numba tiktoken triton
   ```

3. **Compare transcription to captions**

4. **Rebuild from the transcription, not from memory or guess**

## Caption Density vs Visual Scenes

For a 48-second video:
- **Visual scenes**: 8-9 (4-6s each for engagement)
- **Caption segments**: Can be MORE than scenes (12-15 segments for full word coverage)

Each caption segment is a text overlay that changes when narration changes. Visual scenes change every 4-6s for engagement; captions change when words change.

## Text Formatting for Readability

**Do it right the first time — user had to ask multiple times.**

- **Stroke width**: 4-5px depending on text color
- **White text**: `stroke_color='black', stroke_width=4`
- **Red (#ff3333)**: `stroke_color='black', stroke_width=5`
- **Red on black bg**: `stroke_color='white', stroke_width=4`
- **Font**: 'DejaVuSans' (always available on Linux), not 'Arial'
- **Position**: y=1300 (not 1400-1600) to avoid bottom cutoff

## Key Rules

| Rule | Detail |
|------|--------|
| **NEVER guess transcript** | Always source from script file or transcription |
| **More captions than images** | Required for word-for-word coverage |
| **Scene timing** | 4-6 seconds per visual scene |
| **Transcription tools** | openai-whisper, whisperx |
| **Font** | DejaVuSans (system font) |
| **Position** | y=1300 to avoid cutoff |
| **Stroke** | 4-5px, opposite color to text |

## Real Example From Session

I **thought** audio said: "I started recording my sleep to catch my snoring..."

**Actual** audio said: "I've always been a heavy snore. My girlfriend convinced me to record my sleep..."

Completely different story. Fixed only after running Whisper transcription.
