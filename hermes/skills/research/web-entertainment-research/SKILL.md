---
name: web-entertainment-research
description: Research trending movies, trailers, and streaming content using Firecrawl API to bypass bot detection. Integrates with Vercel dashboards for real-time content intelligence.
---

# Web Entertainment Research with Firecrawl

Research trending movies, trailers, and streaming content without bot detection using Firecrawl API.

## Prerequisites

Set your API key:
```bash
export FIRECRAWL_API_KEY=fc-xxxxxxxxxx
```

## When to Use

- Daily content briefing for YouTube channels
- Trailer drop detection
- Weekend watchlist research
- Competitor content tracking
- Trending movie analysis

## Research Sources That Work

| Site | Content | Status |
|------|---------|--------|
| **TrailerAddict** | New trailers, posters | ✅ Working |
| **Rotten Tomatoes** | Weekend picks, reviews | ✅ Working |
| **IMDb MovieMeter** | Popular films, ratings | ✅ Working |
| **TMDB** | Catalog, streaming info | ✅ Working |
| **Netflix** | No API, login required | ❌ Manual only |

## Quick Commands (Tested & Working)

### Full Research Cycle (All Sources)
```bash
# TrailerAddict - New trailers with posters
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.traileraddict.com", "formats": ["markdown"]}' \
  2>&1 | jq -r '.data.markdown' | grep -E "trailer|Trailer|202[5-6]" | head -25

# Rotten Tomatoes - Weekend picks
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.rottentomatoes.com", "formats": ["markdown"]}' \
  2>&1 | jq -r '.data.markdown' | grep -E "\*\*|#[0-9]|[0-9]\s+\%|What to Watch" | head -30

# IMDb MovieMeter - Popularity ratings
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.imdb.com/chart/moviemeter/", "formats": ["markdown"]}' \
  2>&1 | jq -r '.data.markdown' | grep -E "^[0-9]+\.|Rate|Popularity" | head -40

# TMDB - Catalog & streaming info
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.themoviedb.org/movie", "formats": ["markdown"]}' \
  2>&1 | jq -r '.data.markdown' | grep -E "[A-Z][a-z].*\(|New|Trending|202[5-6]" | head -30
```

## Dashboard Integration

Place findings in JSON:
```json
{
  "lastUpdated": "2026-08-28T19:01:00Z",
  "researchSources": [{"source": "TrailerAddict", "status": "✅ Scraped"}],
  "trending": [...],
  "gaps": [...]
}
```

Update: `~/.openclaw/workspace/master-control-dashboard/data/first-watch-intelligence.json`

## Research Workflow Patterns

### Pattern A: Daily Automated Scout (Recommended)
**For:** YouTube channels needing regular content briefs

**Cron Schedule:**
```bash
# 8 AM and 6 PM EST daily
0 8,18 * * * /home/herby/.hermes/scripts/fws-auto-intel.sh
```

**Script Location:** `~/.hermes/scripts/fws-daily-content-scout.py`

**Actions:**
1. Scrapes 4 sources (TrailerAddict, RT, IMDb, TMDB)
2. Parses markdown for titles, sources, angles
3. Updates `data/first-watch-intelligence.json`
4. Generates Telegram brief
5. Rebuilds & deploys Vercel dashboard
6. Sends notification

### Pattern B: On-Demand Research
**For:** User requests like `research Coyote vs Acme`

**Commands:**
```bash
# General entertainment release info
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.google.com/search?q=TITLE+streaming+release+2026", "formats": ["markdown"]}'

# Specific movie details
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.imdb.com/title/tt16047866/", "formats": ["markdown"]}'

# RT scores
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.rottentomatoes.com/m/MOVIE_SLUG", "formats": ["markdown"]}'
```

**Research Output Format:**
```json
{
  "researchDate": "2026-08-29T00:12:00Z",
  "title": "Movie Name",
  "releaseStatus": {
    "status": "Now Playing - Theatrical Only",
    "theatricalDate": "August 28, 2026",
    "streaming": "No confirmed date",
    "distributor": "Studio Name"
  },
  "availability": {
    "theaters": "✅ Yes",
    "streaming": "❌ No",
    "digital": "❌ No"
  },
  "rtStatus": {
    "verified": true,
    "critics": "250+ Verified Ratings"
  },
  "reactionStrategy": {
    "option1": "Go to theater",
    "option2": "Wait for streaming",
    "contentAngle": "Specific hook"
  }
}
```

### Pattern C: Dashboard Live Update
**For:** Immediate visibility on trending content

**Update Steps:**
1. Scrape sources (Pattern B)
2. Parse findings into structured JSON
3. Update `data/first-watch-intelligence.json`:
   - `trending[]` array with research fields
   - `researchDetails` object for deep dives
4. `npm run build` in dashboard directory
5. `vercel deploy --prod`
6. Verify at `https://[dash].vercel.app/first-watch-society`

## Key Pattern (Legacy - See Pattern A/B Above)

1. Firecrawl scrape (gets clean markdown)
2. Parse/extract structured data
3. Compile dashboard JSON
4. Deploy to Vercel
5. Deliver brief to user

## Scripts

- `scripts/daily-content-scout.py` - Automated research script
- `scripts/parse-entertainment.py` - Markdown parser
