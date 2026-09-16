# Music Volume & Mixing for Tales Untold

## Core Lesson

User preference: **subtle background bed under narration**, not prominent audio. Music should support atmosphere without competing with Adam voice.

## Volume Calibration Reference

### Source Music Analysis (always run first)
```bash
ffmpeg -i music_file.wav -af "volumedetect" -f null - 2>&1 | grep mean_volume
```

### Starting Points by Source Level

| Source mean_volume | Recommended starting scale | Result in final mix |
|---|---|---|
| -25 dB or quieter | 1.5–2.0× | ~-10 to -12 dB |
| -18 to -22 dB | 0.8–1.2× | ~-12 to -15 dB |
| -14 to -15 dB (common) | **0.5–0.7×** | ~-15 to -18 dB |
| -10 dB or louder | 0.3–0.5× | ~-15 dB |

### User-Calibrated Sweet Spot
- User's track: -15.2 dB source → 0.6× scale → audible but subtle
- User's previous request: "humming" at too-low levels → raised; then "too loud" → lowered to 0.6×
- **Rule of thumb for this user:** Start at 0.6×, then ask

## Verification

Always verify the **final mixed video**, not just source files:
```bash
ffmpeg -i FINAL_VIDEO.mp4 -af "volumedetect" -f null - 2>&1 | grep mean_volume
```

Target for this user: **-15 to -20 dB mean on the final mix** (subtle but present)

## Anti-Pattern: "More Is Better"

- ❌ DO NOT boost music to 3.0× based on source dB alone
- ❌ DO NOT target -5 to -8 dB mean for final mix — user finds this too loud
- ✅ DO start conservative and iterate with user feedback
- ✅ DO explicitly ask "is this level right or should I adjust?" when unsure

## Music Track Management

When user says "music needs attention," get explicit clarification:
1. **Volume adjustment?** → Adjust scale, rebuild, upload
2. **Wrong track?** → Ask for correct file, replace, rebuild
3. **New track needed?** → Ask for genre/mood specs or file upload

Always confirm which before acting. The phrase "the music" has led to multiple wrong assumptions in past sessions.
