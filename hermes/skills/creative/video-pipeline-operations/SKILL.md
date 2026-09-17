---
name: video-pipeline-operations
description: Video pipelines with Buffer scheduling, cost tracking, and full long-form (12-17 min) production with Ken Burns, captions, and YouTube OAuth direct upload.
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

**Cron Pattern:** `0 8 * * 1,4` — Monday + Thursday mornings minimum for 3/day pace.

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

For 12-17 minute 16:9 videos with Ken Burns, captions, direct YouTube OAuth upload, see:
- `references/longform-production.md` — original long-form reference
- `references/longform-production-v4.md` — **updated V4: Ken Burns, captions, YouTube device OAuth, full automation**

## State Tracking
- User may ask "Where does X stand?" — check `project-state.md` / Obsidian first
- Report: produced count, queue depth, buffer fill, next run
