# Audio Mix Verification

## User Preference
User wants background music **clearly audible**, not whisper-level. Default `0.1` (~-20 dB) was too quiet; user preferred `0.3` (~-15 dB).

## Verification Steps
After mixing narration + music in MoviePy, NEVER assume levels are correct.

### 1. Extract and Analyze
```bash
ffmpeg -i FINAL_VIDEO.mp4 -vn -af "volumedetect" -f null - 2>&1 | grep -E "mean_volume|max_volume"
```

### Expected Readings
| Mix Quality | mean_volume | Interpretation |
|-------------|-------------|----------------|
| Voice only, no music | ~-15 to -12 dB | Narration at good level |
| Voice + music at 0.1 | ~-24 to -20 dB | Music barely perceptible (TOO QUIET) |
| Voice + music at 0.3 | ~-18 to -15 dB | Music clearly audible (GOOD) |
| Clipping risk | > -6 dB max_volume | Reduce master or individual tracks |

### Typical Final Readings (Good Mix)
```
mean_volume: -17.2 dB
max_volume: -5.1 dB
```

## Music Generation Notes
Existing `background_music.wav` is procedural dark ambient (~25s loop). To match longer narration (~80s), loop it:
```python
from moviepy import concatenate_audioclips
loops = int(narration.duration / music.duration) + 1
music = concatenate_audioclips([music] * loops).subclipped(0, narration.duration)
```

## Key Lesson from Sept 15 2026 Session
User said: "Boost the background music." Initial build had music at `0.1` scale (-20 dB). Rebuild boosted to `0.3` and verified with `volumedetect`. User confirmed satisfaction. **Always verify audibility, never assume -20 dB is correct.**
