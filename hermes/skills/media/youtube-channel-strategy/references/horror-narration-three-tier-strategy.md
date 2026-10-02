# Three-Tier Horror Narration Strategy

Based on competitive analysis of Mr Nightmare, CreepsMcPasta, and Tales Untold channel optimization (2026-10-01).

## The Problem

Channels often split into two disconnected worlds:
- **Shorts (discovery):** High frequency, low engagement depth, doesn't count toward YPP watch hours
- **Long-form (community):** 60-90 min live streams, audience burnout on time commitment
- **The Gap:** No produced narrative content in the 20-30 minute sweet spot

## The Solution: Three-Tier Architecture

| Tier | Format | Frequency | Duration | Purpose |
|------|--------|-----------|----------|---------|
| **1. Shorts** | 9:16 vertical | 3x daily | ~60s | Discovery, subscriber acquisition |
| **2. Anthology** | 16:9 produced | 2x weekly | 26-28 min | Watch time, YPP qualification, monetization bridge |
| **3. Live Streams** | Live | 1x weekly | 60-90 min | Community building, Super Chat revenue |

## Why 26-28 Minutes Works

Competitive benchmark data (2026-09-17):

| Channel | Subs | Median Length | Views/Video | Format |
|---------|------|---------------|-------------|--------|
| Mr Nightmare | 7.14M | **26.8 min** | 700K-1.5M | 3-story anthology |
| CreepsMcPasta | 2.08M | 61.9 min | 39-125K | Single long story |
| MrCreepyPasta | 1.72M | 40.9 min | 8-61K | Single + compilations |

**Key Insight:** The disciplined 3-story anthology (25-30 min) outperforms marathon singles by 10x+ on views per video. Consistency of length matters more than raw duration.

## Anthology Structure

| Segment | Time | Content |
|---------|------|---------|
| Cold Open | 0:00-0:15 | Most disturbing sentence; no title card; narration in 3s |
| Story 1 | 0:15-9:00 | ~1,400 words, ~40 scenes |
| Transition | 9:00-9:30 | Musical interlude, visual reset |
| Story 2 | 9:30-18:30 | ~1,400 words, ~40 scenes |
| Transition | 18:30-19:00 | Musical interlude, visual reset |
| Story 3 | 19:00-27:30 | ~1,400 words, ~40 scenes |
| Outro | 27:30-28:00 | CTA to next episode + subscribe |

## Production Specs

**Visual:**
- 1920x1080 (16:9)
- 1 scene every 12-15 seconds (~120 scenes total)
- Ken Burns on every scene (slow zoom + pan, 5 directional variants)
- Crossfade transitions between scenes
- Gammell-style ink wash illustrations

**Audio:**
- Music bed continuous at -22dB under narration
- Never cut at CTA
- Whisper-transcribed captions burned in

**Publishing:**
- Thursday 6 PM ET, Sunday 6 PM ET
- 30 min before peak for indexing
- First 60 minutes: reply to ALL comments

## Funnel Strategy

1. **Shorts → Anthology:** End screens, pinned comments, description links
2. **Anthology → Live Stream:** Community posts, end screen cards
3. **Retention:** Chapter markers, playlist auto-advance, pattern interrupts

## YPP Math

At 2 anthology episodes/week:
- 104 episodes/year
- Target: 500 avg views × 27 min AVD = 225 watch hours per episode
- 104 × 225 = **23,400 watch hours/year** (exceeds 4,000 requirement by 5.8x)

## Title Formulas That Work

**First-person hook (Variant A):**
"I {action} in {location}. {wrong_detail}"

**Retrospective reveal (Variant B):**
"{Past action}. {Consequence}"

A/B test both. The retrospective reveal tends to outperform in horror niche.

## Thumbnail Requirements

- Single silhouetted figure
- Strong light source (moonlight, window, flashlight)
- 3-4 words high-contrast text
- Verified legible at 320x180 (feed size)
- Gammell aesthetic maintained

## Pitfalls

1. **Marathon singles** (60+ min) underperform anthologies
2. **No title card** — cold open required
3. **Static images** — Ken Burns mandatory
4. **Missing funnel** — every short needs CTA to anthology
5. **Inconsistent scheduling** — same day/time every week

## References

- Original research: `horror-narration-benchmarks.md` in this directory
- Tales Untold implementation: `tales-untold-pipeline.md` in this directory
