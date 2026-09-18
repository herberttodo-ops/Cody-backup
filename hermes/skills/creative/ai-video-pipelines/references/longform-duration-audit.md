# Long-Form Duration & Sync Audit

How to verify a long-form narration pipeline actually produces the duration it claims.
Hardened 2026-09-17 auditing a pipeline whose header said "12-17 minutes" and which
shipped a **2:00** video with 4 scenes.

## Why this exists

Long-form generators accumulate silent duration bugs. Nothing errors. The script
prints "Est. duration: 9.1 min", ffmpeg exits 0, a file appears in `finals/`.
Only measurement catches it. **Never trust the script's own printed estimate —
always ffprobe the artifact.**

## The audit sequence

Run all of these against the newest file in `finals/` before believing any claim.

```bash
F=~/path/to/finals/NEWEST.mp4

# 1. Actual duration + dimensions + framerate
ffprobe -v error -show_entries format=duration,size \
  -show_entries stream=codec_type,width,height,r_frame_rate \
  -of default=noprint_wrappers=1 "$F"

# 2. Narration duration — must be <= video duration
ffprobe -v error -show_entries format=duration -of csv=p=0 assets/narration.mp3

# 3. Scene clip count and individual durations
for f in scenes/*.mp4; do
  echo -n "$(basename $f): "; ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"
done

# 4. Illustration count actually on disk (vs count the script claimed to request)
ls illustrations/*.png | wc -l
```

### Interpreting

| Symptom | Cause |
|---------|-------|
| video duration < narration duration | `-shortest` is cutting the story off |
| scene_count × scene_dur ≠ narration_dur | scene count derived from an estimate, not measured audio |
| video fps ≠ clip fps | container rate mismatch; set `-r` on final mux too |
| far fewer images than scenes needed | generation loop swallowed failures without aborting |

## Bug 1: hardcoded WPM constants are wrong

A pipeline assumed `NARRATION_WPM = 130`. Measured by direct API probe:
**169 wpm** for POYO `elevenlabs-tts-turbo-2-5` / Adam.

```
953 words  -> 338.3s  (169 wpm)   script predicted 7.3 min, actual 5.6 min
1316 words -> 408.1s  (193 wpm)
```

Rate varies with punctuation density, so a constant is never reliable.

**Fix: never derive structure from a word-count estimate.** Generate narration
FIRST, ffprobe its real duration, then derive scene count from that:

```python
audio_dur = get_audio_duration(narration_path)   # ffprobe, not an estimate
scene_count = math.ceil(audio_dur / SCENE_DURATION_SEC)
actual_scene_dur = audio_dur / scene_count       # even division, no remainder
```

Use WPM constants only to *plan script length before writing*, never to time assembly.

### Measuring a provider's real WPM

```python
text = ("The house at the end of the lane had been empty for years. " * 60)
# submit, poll, download -> probe.mp3
# wpm = len(text.split()) / (duration / 60)
```

## Bug 2: `-shortest` silently truncates the story

`-shortest` ends output at the shortest input. If video track (scene clips) is
shorter than narration, **the ending of the story never plays**. Measured case:
120s of scene clips against 161s of narration — 41s of story lost, no warning.

This is the worst class of bug in narration pipelines because the artifact looks
fine unless you watch the last minute.

**Fix:** guarantee the video track covers the audio, then drop `-shortest`:

```python
scene_count = math.ceil(audio_dur / SCENE_DURATION_SEC)   # ceil, so video >= audio
# render exactly scene_count clips
# then mux WITHOUT -shortest, or use -t audio_dur to trim video to audio precisely
```

Prefer `-t {audio_dur}` on the output: it trims the tail padding off the video
while guaranteeing the full narration is present.

## Bug 3: linear caption division drifts

Dividing the script's words evenly across the audio duration assumes constant
speech rate. It is not constant. Captions drift progressively and desync badly
by the end of a 20+ minute video.

**Fix:** use Whisper for forced alignment on the generated narration. If the
shorts path in the same project already uses Whisper, the long-form path has no
excuse not to.

## Bug 4: `rstrip(".  No text.")` is a character-set strip

`str.rstrip(chars)` strips **any** of those characters, not the suffix.

```python
p = "...receiver dangling, amber glow button. No text."
p.rstrip(". No text.")
# -> "...receiver dangling, amber glow button"   (fine here)

p2 = "...single white deck chair on muddy shore. Eerie fog. No text."
p2.rstrip(". No text.")
# -> "...Eerie fo"   <-- chewed real words
```

Verified 2 of 21 prompts silently corrupted this way. Fix:

```python
SUFFIX = ". No text."
base = p[:-len(SUFFIX)] if p.endswith(SUFFIX) else p
# or: p.removesuffix(". No text.")   # Python 3.9+
```

Audit any codebase for `rstrip("` followed by more than one character.

## Bug 5: unterminated quotes in the ffmpeg concat list

```python
f.write(f"file '{path.resolve()}\n")   # missing closing quote
```

Current ffmpeg tolerates this (verified: 4×30s clips concatenated to a correct
160s). It is a latent break on upgrade. Always close the quote.

## Bug 6: brown-noise "ambient music"

`anoisesrc=c=brown` at `volume=0.05` is a hiss, not a score. If the user supplied
real music tracks for the brand, use them — loop to length and duck under
narration (about -22dB) rather than generating noise. For a brand where the user
treats audio as a brand element, substituting synthetic noise is a silent
brand-quality regression; report it rather than shipping it.

## Bug 7: `day_of_year % N` story rotation re-uploads duplicates

With 3 hardcoded stories and a Mon/Thu schedule, projected 90 days yields 9/8/9
uploads of the same three scripts. Any content pipeline on a modulo rotation over
a small fixed pool WILL duplicate. Use a queue directory consumed and archived
per run, mirroring whatever the project's working shorts pipeline does.

## Verifying the artifact visually

ffprobe proves duration but not that captions rendered. Extract frames and look:

```bash
for t in 10 30 60 90; do
  ffmpeg -y -ss $t -i "$F" -frames:v 1 -vf scale=960:-1 /tmp/f_$t.jpg -loglevel error
done
```

Then inspect them with vision. Also check the subtitle stream: if `subtitles=`
was used as a burn-in filter there will be NO separate subtitle stream, so
`ffprobe -select_streams s` returning empty does not prove captions are missing —
you have to look at pixels.

## Cron that never fired

`last_run_at: null` on a scheduled producer job means it has never successfully
run. Check this before analyzing output quality: you may be reviewing a hand-run
artifact rather than anything the schedule produced.
