---
name: content-performance-analysis
description: Scrape YouTube and produce content pivot plans.
triggers:
  - user asks to analyze YouTube channel performance
  - user wants to know what content is performing best
  - user requests a content strategy pivot
  - scrape channel analytics to guide production
---

# Content Performance Analysis

Scrape a YouTube channel's live performance data via yt-dlp, segment by
topic/category, and produce actionable pivot recommendations backed by
actual numbers.

## Workflow

### 1. Find the Channel
- Check project metadata (ab_test_log.json, queue files)
- Check Obsidian vault
- Ask user for handle/URL if needed

### 2. Scrape All Content
```bash
# Videos tab
yt-dlp -j --flat-playlist "https://www.youtube.com/channel/CHANNEL_ID/videos"

# Shorts tab (separate — critical for short-form channels)
yt-dlp -j --flat-playlist "https://www.youtube.com/channel/CHANNEL_ID/shorts"
```

**Important:** Videos and Shorts are separate feeds on YouTube. Scraping
only /videos will miss all Shorts.

Extract: id, title, view_count, duration, upload_date, like_count.

### 3. Segment by Category
Manually categorize every video by topic:

| Category | Examples |
|----------|----------|
| Folklore/Cryptid | Skinwalkers, Wendigo, Dracula, Bell Witch |
| Creature/Entity | Generic creatures, shadow people |
| Place-Based | Haunted locations, abandoned buildings |
| Compilation/Meta | Top 5, analysis, behind-the-scenes |
| Contamination | AI slop, wrong-topic uploads, tests |

### 4. Compute Averages
Calculate average views per category. Sort descending.

### 5. Identify Issues
- Contamination (wrong-topic videos)
- Duplicates
- Inconsistent branding
- Broken format

### 6. Recommendations
Structure: summary, current state, table, issues, pivot, titles, cleanup,
verification plan.

## Verified Patterns

- Named folklore entities outperform generics by 3x+
- Retrospective/reveal titles outperform direct hooks
- Shorts are the discovery engine; long-form rides the wave
- Non-content contamination kills topical authority
- Top performers use zero hashtags, minimal descriptions

## Pitfalls

1. Scraping only /videos misses /shorts — always check both feeds
2. Ignoring subscriber context — ratio matters more than raw count
3. Small sample bias — require 5+ videos per category before calling trend
4. Cross-time comparison — compare within same window or use 48h velocity
5. Missing contamination — non-topic videos drag down averages
