# Tales Untold Pitfalls — 2026-09-28 Session

## 1. Buffer "Media Issue" Error Hides Duration Violation

**Symptom:** Buffer reports `error: "There appears to be an issue with the attached media or link attachment. This could be due to the file being too large or connection timing out."`

**Actual cause:** YouTube Shorts has a **hard 60-second limit**. The Beast of Gévaudan video was **139 seconds** (2:19) — Buffer accepted the post but YouTube rejected it on ingestion.

**Fix:** **Always ffprobe duration BEFORE scheduling.**
```bash
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 VIDEO.mp4
```
If > 60s, do NOT schedule. Either:
- Speed up (chipmunk audio, fast but degraded)
- Trim story and re-render (proper fix)
- Split into two Shorts

**Buffer error message is misleading** — it never says "too long," only "media issue." Duration must be checked client-side.

---

## 2. Gammell Monochrome: Technical Correctness ≠ Visual Correctness

**Symptom:** User reports "video only had 1 image."

**Actual state:** 6 scenes were rendered correctly with proper GSAP transitions.

**Root cause:** Frame extraction analysis showed average RGB values:
| Frame | Avg RGB | Perceived |
|-------|---------|-----------|
| 0s | (13, 13, 13) | Near-black |
| 7s | (59, 59, 59) | Dark gray |
| 14s | (53, 50, 46) | Brown-gray |
| 21s | (56, 53, 47) | Brown-gray |
| 28s | (64, 62, 58) | Warm gray |
| 35s | (37, 35, 32) | Dark gray |

Variance: 56.2 — low for a multi-scene composition. To a human viewer, all frames read as "dark monochrome with slight tone shift."

**Lesson:** Technical correctness (6 scenes, correct timestamps) does not guarantee visual distinctness. When scene color palettes are extremely similar, users perceive a single static image.

**Verification method:**
```bash
# Extract frames at scene boundaries and compare avg color
ffmpeg -i VIDEO.mp4 -vf "fps=1/7,scale=10:-1" /tmp/frames/frame_%03d.jpg
# Average color variance should exceed ~100 for noticeable scene changes
# In the wendigo case, ~56 variance = imperceptible transitions
```

**Fix options when this is detected:**
a) Accept the muted palette (genre-appropriate for Gammell)
b) Add per-scene contrast guidance in prompts: "Scene 1: darker shadows," "Scene 3: lighter midtones"
c) Use different color temperature per scene (cooler/warmer shifts)

---

## 3. Google Drive URL Formats in Buffer

Buffer posts show two URL formats in the wild:
- **Old:** `https://drive.google.com/uc?export=download&id=...`
- **New:** `https://drive.usercontent.google.com/download?id=...&export=download&confirm=t`

Both work but the newer format appears more reliable for Buffer ingestion. The `confirm=t` parameter may help with large file delivery. No action needed unless Buffer ingestion starts failing more widely — then migrate scheduling scripts to prefer the newer format.

---

## Action Items from Session

- [ ] Add `ffprobe duration < 60` gate to `publisher.sh` / `publish_queue.py` before any Buffer scheduling call
- [ ] Consider per-scene contrast variation in HyperFrames composition prompts for low-variance monochrome renders
