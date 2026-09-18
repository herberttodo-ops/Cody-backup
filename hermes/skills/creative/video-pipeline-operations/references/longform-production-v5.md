# Long-Form Video Production V5 Reference

Supersedes V4. V4 shipped duration-estimation and caption-truncation bugs that
were severe enough to make the output unwatchable; both are fixed here. This
reference documents the fixes and the working architecture as of 2026-09-17.

## Why V4 failed

1. **Wrong words-per-minute constant.** V4 assumed 130 wpm without measuring
   the actual TTS voice. Measured against the real voice output: 155-169 wpm
   depending on prose density. Every downstream scene count and caption
   timestamp in V4 was derived from the wrong number, so scenes ran out before
   the narration finished and `-shortest` on the final ffmpeg pass silently cut
   the story short (verified: only 27% of one script's audio survived to the
   final render).
2. **Caption truncation (critical, user-visible).** V4's caption writer wrapped
   text into <=2 display lines per Whisper segment and kept only the first two
   with `rows[:2]`, discarding any line beyond that with no time-range split.
   On a 3,643-word video, **136 of 256 segments (53%) needed 3+ lines and had
   their last words silently dropped** — the user experienced this as "the
   voiceover kept going past where the captions stopped."

## V5 fixes

### Duration: measure, never estimate
Generate narration audio FIRST, before planning scenes or captions. Measure
its real duration with ffprobe. Derive scene count as
`ceil(audio_duration / scene_hold_seconds)`, and never truncate the final
video to the video track's length — pad or extend to the narration's length,
add a hard assertion that final duration >= narration duration.

Rate varies by prose density even for the same TTS voice: a 953-word sample
measured 169 wpm on one voice and a 3,643-word script measured 155 wpm on a
different voice. Always measure the actual configured voice on ~1000+ words of
real prose before planning a duration; a generic industry-average wpm figure
will be wrong.

### Captions: word-level timestamps, never a line cap that drops text
```python
# Request word-level timestamps from Whisper
result = model.transcribe(audio_path, word_timestamps=True, language="en")

# Split into captions by WORD, ending a caption when its char budget is full
# and starting a NEW caption with the correct timestamp for the next words.
# Never do `"\n".join(rows[:2])` on a wrapped text block — that is a silent
# truncation with no time-range split, and the dropped lines vanish with no
# warning.
```
After generating, verify caption word count against the raw transcript word
count. If captured words < 98% of transcript words, warn loudly — this is the
signal that a truncation bug has reappeared.

### Story intake: queue-driven, never hardcoded
Hardcoded story text baked into the producer script means every rerun risks
re-uploading the same content. Use a `queue/*.txt` directory with a simple
`key: value` header block, a `---` separator, then the story body. Move
consumed files to `queue_done/` and track produced filenames in a small JSON
state file so nothing repeats.

Minimum viable queue header:
```
title: <hook-first title, no brand suffix, no em dash>
desc: <1-2 sentence teaser>
chapters: A | B | C | D | E
thumbnail: <single-subject, tight-crop description>
thumb_text: TWO TO FOUR WORDS
scenes: <beat 1 image prompt>
scenes: <beat 2 image prompt>
tags: horror, creepypasta, ...
---
<story body>
```

### Music bed: multi-track crossfade, loudness-matched
A bed built from only 1-2 tracks loops audibly (`T1 > T2 > T1 > T2...`).
Loudness-normalize every source track to a common LUFS target FIRST (two-pass
ffmpeg `loudnorm`), then crossfade between them (`acrossfade`, 5-6s, triangular
curve), picking a random non-repeating order. This absorbed a 35dB spread
across test tracks down to +-3dB with zero audible seams. More source tracks
directly reduces perceived repetition — 10 tracks covering more than 2x the
video's runtime produced a bed with only one repeated track across 23.5
minutes, versus 16 repeats with 2 tracks.

### Thumbnail: model selection changes the outcome
Compared image models on an identical prompt at real feed size (320x180) —
results are model-specific and will need re-checking if models change, but the
METHOD generalizes: generate the same prompt across every available model,
downscale each to actual feed dimensions, and judge legibility there, not on
the full-resolution image. A thumbnail that reads clearly at 1280x720 can be a
muddy smudge at 320x180.

**Native text-in-thumbnail models are usable but need a review gate.** When a
model is asked to render an explicit headline overlay ("...text overlay
reading exactly 'X'..."), that instructed text comes out correct with high
reliability. The SAME model, in the SAME generation, may also paint unrelated
incidental scene text (signage, name tags, prop labels) that nobody asked for,
and that incidental text is unreliable — garbled/misspelled in roughly half of
test generations. This is not a reason to avoid native text for the headline;
it is a reason to always visually check the delivered thumbnail for garbled
background text before upload, since the model cannot self-verify it.

If native text-in-image proves unreliable for a given headline, a PIL text
compositor is the deterministic fallback: draw the exact string with a real
font, guaranteed correct every time, at the cost of a flatter "overlay bar"
look instead of text integrated into the composition. Auto-placement should
score candidate regions by edge energy / brightness variance and choose the
calmest, so text never lands on the subject. When measuring text width for
placement/centering, measure it the SAME WAY it will be drawn (e.g. per-word
cursor advance when one word gets different styling) — measuring with a
different method than the draw path is what causes glyphs to clip at the
frame edge.

### Parchment / decorative border artifacts
Some ink-wash-style image generations add a light decorative border/frame
around the artwork that the prompt did not ask for. Per-image auto-detection
of the border is unreliable (borders appear on only some generations and a
naive dark-content bounding box will instead crop into real artwork on
asymmetric compositions). A uniform inset crop (e.g. 7% from every edge,
applied identically to every image before the Ken Burns pass) is more robust
than trying to detect and crop each border individually.

### Shot-composition modifiers must not contradict the subject
When cycling through a list of "shot type" modifiers (wide/close/low-angle/
etc.) to add variety across many generated images, verify by enumeration that
no modifier can combine with a subject to produce a logical contradiction
(e.g. an "interior, single lamp" modifier applied to an outdoor dock subject
rendered an indoor boathouse instead of the intended dock). Prefer modifiers
that are purely compositional (angle, crop, framing) over modifiers that
assert a location or lighting condition, since those can conflict with the
scene description. Also add an explicit tone instruction (e.g. "predominantly
dark, deep blacks dominant") on every image prompt for a dark-themed channel,
and a post-generation brightness check that rejects and regenerates outliers
rather than shipping one visibly mismatched frame in an otherwise-dark set.

### Safe rebuild pattern: cache every expensive stage
Cache narration audio (keyed on hash of voice+model+script text) and each
generated image (keyed on hash of model+prompt) to local content-addressed
files. A failure or restart downstream of a cached stage costs zero API spend
— only the stage that actually changed needs to regenerate. This is what makes
it practical to fix a bug (e.g. the caption truncation above) and re-render a
finished video without re-paying for TTS or image generation.

### Concurrency: lock the shared workspace
If an old pipeline version and a new one can both write into the same
directories (e.g. via separate cron schedules), they will corrupt each other's
output — confirmed: an old version's cron fired mid-run and overwrote a new
version's in-progress illustrations with unrelated images from a different
story. Give each pipeline version its own build subdirectory, and add a PID
lockfile with stale-lock detection so two runs of the same version cannot
overlap either.

## Benchmark data (verified by scraping live channel listings, 2026-09-17)
Long-form horror narration channels performing well run 26-28+ minutes, not
the 12-17 minute range an earlier version of this pipeline targeted:
- Mr Nightmare (7M+ subs): median ~27 min, tight anthology format
- CreepsMcPasta (2M+ subs): median ~62 min, single continuous story
- Let's Read (1.4M+ subs): median ~55 min, themed compilations
- MrCreepyPasta (1.7M+ subs): median ~41 min

Title convention across all of them: first-person, specific, unresolved-threat
hook ("I'm a Paramedic in Chicago. Some Calls Don't Make It Into Our Reports"),
not a brand-name-first title.
