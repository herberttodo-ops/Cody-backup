---
name: video-pipeline-operations
description: Video pipelines with Buffer scheduling, cost tracking, and full long-form (26-28+ min) production with Ken Burns, captions, and YouTube OAuth direct upload.
---

# Video Pipeline Operations

## Buffer Rolling System

### Known Limits
| Platform | Scheduled Post Limit |
|----------|---------------------|
| YouTube (Buffer) | 10 posts |
| Instagram (Buffer) | 10 posts |
| LinkedIn (Buffer) | 10 posts |

At 3 videos/day: 10 posts = ~3 days runway.

### Refill Trigger
```
When scheduled < (daily_rate × 2), produce until limit - 1
```

**Cron Pattern: run the refill check DAILY, not just 2x/week.** A `0 8 * * 1,4`
(Mon+Thu only) cadence looks sufficient on paper for a 3/day pace but fails in
practice: it batches ~a week of posts twice weekly, and if the agent
overproduces or underproduces slightly on one run, the gap between Thu and
the next Mon goes uncovered with zero self-correction. Confirmed in production
2026-09-17: a Mon/Thu-only refill left a real 2.5+ day posting gap (nothing
scheduled from Fri evening through the whole weekend). Use `0 8 * * *`
(daily) and make the check itself cheap: query actual scheduled posts,
compute which of the next 3-4 days' target slots are still empty, and only
produce enough new videos to fill real gaps — do not blindly top up to a
fixed count every run.

**Always verify posts landed at the exact target time, not just that a post
exists.** Buffer's own default scheduling (`addToQueue` / no `dueAt`) puts a
post at an unpredictable slot that can drift outside the target window (seen:
a post intended for 7:00 PM landed at 7:31 PM because the scheduling call
omitted `dueAt`). Any post that must land in a specific window needs an
explicit `dueAt` and a post-schedule check confirming it. See
`references/buffer-scheduling-mechanics.md` for the exact API behavior.

**Dead-cron check:** if a publish/refill script's precondition folder (e.g.
"pull one video from `produced/`") is checked against a path the real
pipeline never actually writes to, the cron fires forever and silently
no-ops every single time with no error. When auditing a multi-cron pipeline,
trace each job's actual file dependency end to end rather than trusting the
job's name/description — three daily crons were found doing exactly this on
2026-09-17 and were removed.

## Cost Per Video

### Shorts (~60s, 9:16)
| Component | Est. Cost |
|-----------|-----------|
| Script (GPT-4o-mini via POYO) | $0.01-0.03 |
| Voice (ElevenLabs via POYO) | $0.05-0.10 |
| Images (5-7 scenes) | $0.10-0.25 |
| Rendering / Upload | $0 |
| **Total** | **$0.15-0.35** |

### Long-Form (12-17 min, 16:9)
| Component | Count | Est. Cost |
|-----------|-------|-----------|
| Scenes (~75 images) | 75 × nano-banana | ~$0.60 |
| Thumbnail | 1 × nano-banana | ~$0.05 |
| Adam TTS (~15 min) | elevenlabs-tts-turbo-2-5 | ~$0.18 |
| **Total** | | **~$0.83** |

Monthly (90 shorts at 3/day): ~$20-30. Always provide when user asks about scaling.

## Upload → Schedule Workflow

1. **Upload to Google Drive** → `uc?export=view&id=` URL
2. **Buffer create_post** with video asset URL (not local paths)
3. **Schedule at niche-optimized times** (verify with user)

## Scheduling by Niche (ET)
| Niche | Best Times |
|-------|-----------|
| Horror Shorts | 6-8 PM (evening scroll) |
| Comedy/Tech | 12-2 PM, 5-7 PM |
| Education | 9-11 AM, 2-4 PM |
| Fitness | 6-8 AM, 4-6 PM |

## Long-Form Production

For 26-28+ minute 16:9 videos with Ken Burns, captions, direct YouTube OAuth upload, see:
- `references/longform-production.md` — original long-form reference
- `references/longform-production-v4.md` — V4: Ken Burns, captions, YouTube device OAuth, full automation (superseded — had a wpm-estimation bug and a caption-truncation bug, both fixed in V5)
- `references/longform-production-v5.md` — **current: measured-duration pipeline, word-level caption timestamps, multi-track music crossfade, queue-driven story intake, thumbnail model selection method, safe-rebuild caching, and verified 26-28+ min benchmark data**

## State Tracking
- User may ask "Where does X stand?" — check `project-state.md` / Obsidian first
- Report: produced count, queue depth, buffer fill, next run
