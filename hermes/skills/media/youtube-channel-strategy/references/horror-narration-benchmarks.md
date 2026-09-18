# Horror Narration Channels — Competitive Benchmark

Scraped live 2026-09-17 via `yt-dlp --flat-playlist --playlist-end 15 -J`, last 15 uploads
per channel. Refresh before relying on the numbers; the *structural* conclusions are stable.

## Method that works

HTML scraping of `youtube.com/@channel/videos` is unreliable — `ytInitialData` parses but the
video renderer keys shift and regex/walker extraction returned 0 rows across 6 channels.
Subscriber count is extractable from HTML; durations and view counts are not.

**Use yt-dlp instead.** It returns clean JSON with `duration`, `view_count`, `title`,
`channel_follower_count`:

```bash
yt-dlp --flat-playlist --playlist-end 15 -J "https://www.youtube.com/@MrNightmare/videos" > ch.json
```

```python
d = json.load(open("ch.json"))
for e in d["entries"]:
    print(e["duration"], e.get("view_count"), e["title"])
```

Note: some entries have `view_count: None` (recent/limited uploads) — filter before computing
medians. A channel handle that 404s returns a near-empty JSON file; check size before parsing.

## The data

| Channel | Subs | Median length | Views/video | Format |
|---------|------|---------------|-------------|--------|
| Mr Nightmare | 7.14M | **26.8 min** | 700K-1.5M | 3-story anthology, tight 25-30 min band |
| CreepsMcPasta | 2.08M | 61.9 min | 39-125K | Single long first-person story |
| MrCreepyPasta | 1.72M | 40.9 min | 8-61K | Single story + 3-5 hr compilations |
| Let's Read | 1.38M | 55.1 min | 160-300K | 4-5 story themed compilations |

## Conclusions

**The floor for "long-form" in this niche is ~20 minutes.** Nobody successful publishes
12-minute horror narration. A pipeline targeting 12-17 min is targeting below the floor.

**Best views-per-sub is the disciplined anthology**, not the marathon. Mr Nightmare has 3.4x
CreepsMcPasta's subs and 10x the per-video views on a rigid 25-30 min / 3-story format.
Consistency of length and structure appears to matter more than raw duration.

**Two viable targets:**
- 26-28 min (~4,400-4,700 words at ~169 wpm) — 3 loosely themed stories, ~1,500 words each
- 50-60 min — single sustained first-person story, or 4-5 story themed compilation

## Title patterns that win

First-person + specific occupation or place + unresolved threat. Observed:

- "I'm a Paramedic in Chicago. Some Calls Don't Make It Into Our Reports"
- "A Whiteout Trapped Us in an Unmarked Cabin. One Door Was Nailed Shut"
- "I'm a Flood Operator in the California Delta. There's a Reason We Stay"
- "3 Terrifying TRUE Night Walk Horror Stories"

Two-sentence structure recurs: **situation, then the specific wrong detail.** The second
sentence is the curiosity gap.

### Anti-pattern

`"The Road Home | Tales Untold — Full Narrated Horror"`

Fails on four counts: brand-first (burns the front of the title box, which is the only part
visible in feeds), no hook, no specificity, no curiosity gap. Also uses an em dash, which
Andrew avoids in all written content.

Rewrite: *"I Took a Highway That's Been Closed Since 1989. Twelve Chairs Were Waiting"*

Drop the `| Channel Name — Category` suffix entirely. Viewers already see the channel name.

## Thumbnail requirements

Every benchmark channel: high contrast, single subject, often a face or silhouette, plus
2-5 words of text.

**Common AI-art failure mode:** a genuinely beautiful wide illustration that dies at feed
size. A reviewed Gammell-style factory interior was near-monochrome sepia, no face, no text,
no focal subject — at 320x180 it read as a brown smudge.

Spec: single subject, tight crop, one strong light source, 3-4 words of high-contrast text,
silhouetted figure where possible. Generate 1280x720 and **verify legibility by downscaling
to 320x180 and looking at it** before upload.

## Retention mechanics for this niche

- **Cold open 0:00-0:15.** No title card, no channel intro. Open on the most disturbing
  sentence, then back up. Benchmark channels have narration running inside 3 seconds.
- **Chapters in the description.** YouTube surfaces them on the scrubber; measurable
  long-form retention help, trivial to generate from story beats.
- **Scene variety.** 12s holds across 27 min needs ~135 scenes. Generating 135 unique images
  is expensive — use 40-50 unique illustrations with varied Ken Burns paths and 20-25s holds
  plus occasional cross-dissolves. Selecting a zoom path via `hash(path) % 5` produces
  visible repetition; vary direction and easing per scene.
- **Music bed continuous**, ducked to about -22dB under narration. Never cut it at CTA.
- **Playlist per series** with auto-advance; end screen points at the next episode, not a
  generic subscribe card.
- **Shorts as funnel.** Cut 3 vertical clips from each long-form's best beats, CTA to the
  full story. Free reach when a shorts pipeline already exists.
- **Publish 6-8 PM ET** for horror. Production can run any time; publishing should land in
  the evening window.
