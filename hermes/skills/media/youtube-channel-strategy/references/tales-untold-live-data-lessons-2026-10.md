# Tales Untold: live-data lessons (Oct 2026)

Method: yt-dlp flat pull of /shorts, then per-video `yt-dlp --skip-download -j` (flat gives only title/id/views). 187 Shorts, 257 subs.

## Findings
- Only strong period: Jan-Feb 2026, 61 videos, mean 491 views. Named folklore, one entity per video, 46-55s, median 11-word "Entity: angle" titles, 37/61 with hashtags.
- Sep-Oct 2026: mean ~115. Oct "compliant" videos (35s cap, short titles) aged 5+ days: mean 88.
- Duration buckets (all time): 31-40s mean 59 (n=16); 41-50s mean 328 (n=48); 51-60s mean 250; 61-90s mean 180. Under-40s is worst.
- Sep 1-Oct 11: named folklore median 87 (n=47) vs original no-entity stories median 31 (n=27). Age confound: best original stories were the oldest.
- Defects: 15/187 videos share titles; 6 uploads/day on Oct 15-16 from refill + cron; 25/40 pool stories under 90 words; full-frame end CTA overlay; whole-segment captions; likes/view 4.5%, comments/view 0.08%.
- Big narrated-story channels do poorly on Shorts (MrCreepyPasta 1.7M subs median ~4k; CreepsMcPasta 2M ~19k; DarknessPrevails 882k ~10k). Shorts winners with personality/hook: MrBallen (median ~134k), Mr Nightmare (~286k). Small reddit/nosleep shorts channels: 1-42 views.

## Lessons
- Never declare a fix "working" without live per-video views; earlier advice (35s cap, short titles) was contradicted by data.
- Treat duration/title rules as hypotheses; run an arm-rotated test, compare medians, require 1.5x gap.
- Missing input that matters most: YouTube Studio export (viewed-vs-swiped, avg view %, traffic source).
