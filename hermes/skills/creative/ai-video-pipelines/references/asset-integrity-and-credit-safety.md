# Asset Integrity & Credit Safety for Long AI Pipelines

Hardened 2026-09-17 rebuilding a 26-minute narration pipeline. Covers four classes of
problem that only appear on LONG, EXPENSIVE, MULTI-STAGE jobs:

1. Verifying a provider actually honored your request (silent substitution)
2. QA gating generated images so one bad plate does not ship
3. Surviving mid-run interruption without re-billing
4. Preventing concurrent pipeline versions from corrupting each other

Companion to `longform-duration-audit.md` (duration/sync bugs).

---

## 1. Verify the provider honored your request

### Providers may not error on a wrong parameter

POYO accepts a raw ElevenLabs voice ID in the `voice` field:

```python
{"model": "elevenlabs-tts-turbo-2-5", "input": {"voice": "BQOei2tk6QCBMHQWPhbj", "text": ...}}
```

It returns **HTTP 200 and usable audio for a voice ID it does not recognize**. So a
successful response is NOT evidence the voice was applied. Never report a voice/model
swap as working on the basis of exit status alone.

### Three-signal verification for a voice/model swap

Generate the SAME text under old and new parameters, then compare:

```bash
# 1. Byte identity — identical MD5 means you got the same render twice
md5sum old.mp3 new.mp3

# 2. Duration — different voices pace differently
for f in old.mp3 new.mp3; do
  ffprobe -v error -show_entries format=duration -of csv=p=0 $f
done

# 3. Spectral tilt — the strongest signal, catches same-length different-timbre
for f in old.mp3 new.mp3; do
  for band in "80:160" "160:300" "300:600"; do
    lo=${band%%:*}; hi=${band##*:}
    ffmpeg -i $f -af "highpass=f=$lo,lowpass=f=$hi,astats=metadata=1:reset=0" \
      -f null - 2>&1 | grep "RMS level dB" | head -1
  done
done
```

Real measured example — two voices, identical input text:

| Signal | Adam | BQOei2tk6QCBMHQWPhbj |
|--------|------|----------------------|
| MD5 | `1f57d285...` | `57128ac9...` (differ) |
| Duration | 33.5s | 36.4s |
| 80-160Hz RMS | -22.8 dB | -28.3 dB |
| 160-300Hz | -21.8 dB | -31.0 dB |
| 300-600Hz | -22.9 dB | -32.3 dB |

The consistent downward tilt confirms a genuinely darker/drier voice, not a fallback.

### Verify no silent truncation at length

Long TTS requests may be truncated without error. Append a **unique sentinel sentence**
to the very end, generate, then transcribe only the tail:

```bash
ffmpeg -y -sseof -30 -i long.mp3 -c copy tail.mp3 -loglevel error
# then Whisper the tail and grep for the sentinel
```

Measured: POYO accepted a 12,454-char single request and returned 822s with the sentinel
present. Chunking is still worthwhile for retry economy, but the limit is high.

---

## 2. Measured speech rate is per-voice AND per-prose

WPM is not a property of the model alone. Same voice, different scripts:

| Voice | Words | Duration | WPM |
|-------|-------|----------|-----|
| Adam | 953 | 338.3s | 169 |
| BQOei2tk6QCBMHQWPhbj | 953 | 411.6s | 139 |
| BQOei2tk6QCBMHQWPhbj | 3,643 | 1407.4s | **155** |

Same voice measured 139 on a short dense sample and 155 on a long script. Short samples
over- or under-estimate. **Measure on a full-length script of the actual prose style,**
and use the constant only for pre-flight word-count planning — never for assembly timing
(see `longform-duration-audit.md` Bug 1).

Word targets at 155 wpm: 26 min = 4,030 words; 28 min = 4,340 words.

---

## 3. Image QA gates

Two defect classes that ffprobe cannot see. Both require measuring pixels or looking.

### Defect: model adds a decorative border

An illustration model asked for an "ink wash illustration" may return the artwork
**matted inside a light parchment/torn-paper frame**. Measured: edge mean brightness
**196** vs center **29**, frame 25-47px on a 1376x768 render.

On a dark video this reads as a rendering defect, and Ken Burns drifts the frame in and
out of shot so it pulses.

**Auto-detection was tried and rejected.** Two approaches, both unsafe:

| Approach | Failure |
|----------|---------|
| Dark-content bounding box | Asymmetric trims (L221/R20) on images whose real artwork is dark at one edge — it cut the picture, not the frame |
| Bright-edge inward scan | Correctly found `T30 B25 L37 R37` on some images, reported "no frame" on others that had one, because border opacity varies |

Borders appear on only SOME generations, so per-image auto-crop risks destroying
composition on the unframed ones.

**Fix: prompt + uniform inset, not detection.**

```python
# 1. Negative prompt language
"Full-bleed edge to edge composition. No border, no frame, no parchment edge, "
"no torn paper edge, no vignette margin, no matting. "
"No text, no watermarks, no lettering, no signature."

# 2. Uniform inset crop applied to EVERY scene, before the zoompan upscale
EDGE_INSET = 0.07
keep = 1.0 - (EDGE_INSET * 2)
vf = (f"crop=iw*{keep:.4f}:ih*{keep:.4f},"
      f"scale={w*2}:{h*2}:force_original_aspect_ratio=increase,crop={w*2}:{h*2},"
      f"zoompan=...")
```

Uniform means composition stays centered and no image is treated differently.
Verified: edge mean brightness 196 -> 32, artwork full-bleed, composition intact.
Prompt language reduced but did not eliminate frames, which is why the inset stays.

### Defect: one washed-out plate in a dark sequence

Measure post-inset mean brightness and reject outliers. On a dark-horror sequence one
pale plate out of 64 reads as a mistake.

```python
def image_is_too_bright(path, max_mean=110, inset=0.07):
    from PIL import Image
    import numpy as np
    im = Image.open(path).convert("L")
    w, h = im.size
    box = (int(w*inset), int(h*inset), int(w*(1-inset)), int(h*(1-inset)))
    a = np.asarray(im.crop(box), dtype=np.uint8)
    return float(a.mean()) > max_mean, float(a.mean())
```

On rejection, append a cumulative darkener to the prompt and regenerate (bounded
attempts, then accept with a logged WARNING rather than halting the whole build).

Validated against 10 real renders: flagged only the outlier (113.7), passed the other
nine (41.4 to 79.5). No false positives. After the prompt fix the same beats came back
at 19-48.

### Defect: shot modifier contradicts the subject

Pairing beat `i % len(beats)` with modifier `i % len(shots)` and stepping both by 1
**locks into a cycle** and produces impossible combinations. Enumerated on a real
14-beat / 8-shot list:

| # | Beat | Shot | Result |
|---|------|------|--------|
| 6 | collapsed boat dock | interior, single lamp | rendered a **boathouse interior** with a hanging lantern |
| 14 | flooded access road | interior, single lamp | same conflict |
| 4 | rusted call box | silhouette against pale light | forced a bright sky on a dark channel |

Two rules:

1. **Modifiers must be composition-only and tone-neutral.** Drop anything that asserts a
   location (`interior, single lamp`) or a brightness (`silhouette against pale light`).
   Prefer `off-center composition, negative space in darkness`,
   `framed through a dark foreground element`, `low angle, oppressive`.
2. **Step the modifier index by a coprime offset** so pairings do not cycle:
   `shots[(i * 3) % len(shots)]`.

Also append an explicit value instruction to every prompt when the brand is dark:
`"Overall value: predominantly dark, deep blacks dominant, light used sparingly as accent only."`

**Always spot-check generated images against their prompt with vision.** Brightness and
border metrics pass an image that shows entirely the wrong subject.

---

## 4. Credit safety: content-addressed caching

A long job that fails at stage 6 must not re-bill stages 1-5. Key each cache on the
inputs that determine the output, so a fix at one level invalidates only that level.

```python
import hashlib

# Narration: keyed on voice + model + full script text
tag = hashlib.sha256(f"{VOICE_ID}|{TTS_MODEL}|{text}".encode()).hexdigest()[:16]
cache = ASSETS / f"narration_{tag}.mp3"
if cache.exists():
    shutil.copy(cache, out_path)
    return probe_duration(cache)     # zero spend
# ... generate, verify, then: shutil.copy(out_path, cache)

# Images: keyed on model + full prompt string
tag = hashlib.sha256(f"{IMAGE_MODEL}|{prompt}".encode()).hexdigest()[:16]
```

This granularity is the point: prompt-level fixes (border, shot modifiers) correctly
invalidate the image cache while the narration cache survives untouched. Measured across
four restarts in one session, 23.5 minutes of TTS was reused every time at zero cost,
while images regenerated as intended.

**Design rule: cheap-to-fix stages should be cheap to retry.** Put the most expensive
artifact behind the most stable key.

### Partial completion with a coverage gate

If asset generation is interrupted partway, a complete video may still be buildable —
but only if nothing in the story is unrepresented. Gate on **semantic coverage**, not count:

```python
allow_partial = os.environ.get("ALLOW_PARTIAL_IMAGES") == "1"
covered_beats = set()
for i in range(target):
    try:
        generate_image(prompt, out)
    except ProductionError as e:
        if allow_partial and i > 0:
            log(f"stopping image generation early: {e}")
            break
        raise
    covered_beats.add(i % len(beats))

have = sorted(ILLUSTRATIONS.glob("*.png"))
if len(have) < target:
    missing = [beats[j] for j in range(len(beats)) if j not in covered_beats]
    if not allow_partial:
        raise ProductionError(
            f"only {len(have)}/{target} generated. Re-run with ALLOW_PARTIAL_IMAGES=1 "
            f"to build from these ({len(covered_beats)}/{len(beats)} beats covered).")
    if missing:
        raise ProductionError(
            f"{len(missing)} story beat(s) have no image: {missing}. Refusing to build "
            f"a video that never shows part of the story.")
```

Real case: generation stopped at 34/45 images. All 14 story beats were already covered —
the missing 11 were duplicate composition variants — so the full 26-minute video
completed from cache at zero additional spend.

Apply the same fallback to secondary assets (thumbnail): degrade to an existing
illustration and log `REGENERATE before upload` rather than blocking the build. Never
let a placeholder ship silently — surface it in the final report as an action item.

---

## 5. Concurrency: version collision

Two versions of a pipeline sharing a workspace will corrupt each other. Observed: a
scheduled V4 job fired mid-run of a hand-started V5 and overwrote its illustrations —
caught only by spot-checking an image and finding a subject from the OTHER story
(a rotary phone in a story with no phone).

Three defenses, apply all:

1. **Isolated build dirs per version.** `longform/v5/{assets,illustrations,scenes}`.
   Outputs (`finals/`, `thumbnails/`) can stay shared if filenames are unique.
2. **PID lockfile with stale detection.**

```python
if LOCK_FILE.exists():
    try:
        old = int(LOCK_FILE.read_text().strip())
        os.kill(old, 0)
        raise ProductionError(f"another run is active (pid {old}). "
                              f"If stale, delete {LOCK_FILE}")
    except (ValueError, ProcessLookupError):
        log("clearing stale lock")
LOCK_FILE.write_text(str(os.getpid()))
try:
    return _produce()
finally:
    if LOCK_FILE.exists():
        LOCK_FILE.unlink()
```

3. **Pause the old version's cron before running the new one.** Do not assume a
   superseded schedule is harmless. Check `hermes cronjob list` for anything pointing at
   the old script and pause it explicitly.

Detection tip: `ls -la --time-style=+%H:%M:%S` on the asset dir. Interleaved or
out-of-order mtimes across a supposedly sequential loop means a second writer.

---

## 6. Fail loudly, never substitute

For a project where the user treats voice, art style, and music as brand elements, a
silent substitution is a brand regression shipped without review. Structure the pipeline
so every core-component failure raises:

```python
class ProductionError(RuntimeError):
    """Raised when a core component fails. We stop rather than substitute."""

# and at the entry point:
except ProductionError as e:
    log(f"\nPRODUCTION HALTED: {e}")
    log("Nothing was substituted. Fix the cause and re-run.")
    sys.exit(1)
```

Also assert the invariant you actually care about before declaring success:

```python
coverage = final_dur / audio_dur * 100
if coverage < 98:
    raise ProductionError(f"final covers only {coverage:.0f}% of narration")
```
