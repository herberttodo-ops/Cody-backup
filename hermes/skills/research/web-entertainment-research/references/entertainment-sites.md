# Entertainment Content Research with Firecrawl

Research trending movies, trailers, and streaming content without bot detection.

## Overview

Firecrawl bypasses bot detection by using cloud-based scraping, making it ideal for entertainment sites that aggressively block automated access (YouTube, IMDb, Rotten Tomatoes, etc.).

## Working Sites for Movie/TV Research

| Site | Content Type | Endpoint | Notes |
|------|--------------|----------|-------|
| **TrailerAddict** | New trailers, posters | `https://www.traileraddict.com` | ✅ Full data, daily checks recommended |
| **Rotten Tomatoes** | Weekend watchlists, reviews | `https://www.rottentomatoes.com` | ✅ "What to Watch This Weekend" section |
| **IMDb MovieMeter** | Popular films, ratings | `https://www.imdb.com/chart/moviemeter/` | ✅ Ratings like "8.5 (453K)" extractable |
| **TMDB** | Movie catalog, streaming | `https://www.themoviedb.org/movie` | ✅ Streaming availability data |

## Quick Research Commands

### Daily Trailer Check
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.traileraddict.com", "formats": ["markdown"]}' \
  | jq -r '.data.markdown' | grep -i "trailer"
```

### Weekend Watch List
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.rottentomatoes.com", "formats": ["markdown"]}' \
  | jq -r '.data.markdown' | grep -i "what to watch"
```

### Trending Movies with Ratings
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.imdb.com/chart/moviemeter/", "formats": ["markdown"]}' \
  | jq -r '.data.markdown' | grep -E '\([0-9]+K\)'
```

## Response Parsing

### Extract Movie Titles
From TrailerAddict markdown:
```bash
grep -oP '\[.*?Trailer' | sed 's/\[//;s/ Trailer//'
```

### Extract Ratings
From IMDb markdown:
```bash
grep -oP '\d+\.\d+\s+\([0-9.]+K\)'
```

### Extract "What to Watch"
From Rotten Tomatoes:
```bash
grep -A5 "What to Watch This Weekend"
```

## Research Schedule

| Day | Action | Target |
|-----|--------|--------|
| **Daily (morning)** | Check TrailerAddict | New trailer drops |
| **Daily (evening)** | Check IMDb MovieMeter | Trending shifts |
| **Thursday/Friday** | Check Rotten Tomatoes | Weekend watchlist |
| **Sunday** | Research weekend box office | Monday reaction content |

## Data Structure for Dashboard

```json
{
  "lastUpdated": "2026-08-28T19:01:00Z",
  "trending": [
    {
      "id": "1",
      "title": "Movie Title",
      "type": "trailer|movie",
      "source": "TrailerAddict",
      "views": "Optional view data",
      "age": "New release | This week",
      "priority": "high|medium|low",
      "angle": "Suggested reaction angle",
      "status": "not-reacted|done"
    }
  ],
  "gaps": [
    {
      "title": "Content Gap Name",
      "opportunity": "Why this is underserved",
      "potential": "Estimated subscriber gain"
    }
  ],
  "upcoming": [
    {
      "date": "2026-09-01",
      "title": "Upcoming Release",
      "action": "What to do",
      "priority": "high|medium|low"
    }
  ],
  "researchSources": [
    {
      "source": "TrailerAddict",
      "status": "✅ Scraped",
      "findings": "5 new trailers"
    }
  ]
}
```

## Automation Pattern

For automated daily research:

1. **Scrape** 4 sources (TrailerAddict, RT, IMDb, TMDB)
2. **Parse** markdown output to extract structured data
3. **Compile** into dashboard JSON format
4. **Update** `first-watch-intelligence.json`
5. **Deploy** to Vercel for live access
6. **Deliver** brief to user via Telegram

## Data Integrity Rules

**CRITICAL:**
- Always timestamp findings: `"lastUpdated": "2026-08-28T19:01:00Z"`
- Label source of every data point
- Never present template data as scraped findings
- Include "researchSources" array with status for transparency

## Limitations

Still requires manual check:
- **Netflix** - No public API, login required
- **YouTube personalized trending** - Requires Google auth
- **Studio Twitter/X** - API rate limits, separate creds needed

## Related

- `first-watch-content-research` skill - Dashboard integration pattern
- Firecrawl API documentation at https://docs.firecrawl.dev
