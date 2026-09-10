# API Limitations & Workarounds for Content Research

## What Works Now (Firecrawl)

### Firecrawl API
**Status:** ✅ WORKS — Bypasses bot detection
**How:** Cloud-based scraping, no browser binary needed
**Best for:** Entertainment sites that normally block automated access

**Working Sites:**
1. **TrailerAddict** - Full trailer data, poster images, release info
2. **Rotten Tomatoes** - "What to Watch" section, weekend picks, reviews
3. **IMDb MovieMeter** - Popular films, ratings data
4. **TMDB** - Movie catalog, streaming availability
5. **YouTube trending** - Partial data (requires login for personalized)

**API Endpoint:**
```
curl -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "SITE_URL", "formats": ["markdown"]}'
```

**Result:** Clean markdown, no CAPTCHAs, no bot blocks

### What Still Requires Manual

| Source | Why | Action |
|--------|-----|--------|
| **Netflix** | Login-walled, no public API | Andrew checks app manually |
| **YouTube personalized trending** | Requires Google login | Search with date filters instead |
| **Studio Twitter/X** | Rate limits, API key needed | Browser + screenshot |
| **Google Trends** | CAPTCHA on automated requests | Manual check acceptable |

## What Failed Before (FIXED)

### Reddit API (r/movies)
**Error:** "You've been blocked by network security"
**Status:** Still blocked, but NOT NEEDED — use Firecrawl on entertainment sites instead

### Browser Tool
**Error:** "No such file or directory: agent-browser"
**Status:** ✅ FIXED — Install agent-browser in hermes-agent directory
```bash
cd /home/herby/.hermes/hermes-agent && npm install agent-browser
```

### Direct Curl Scraping
**Error:** JavaScript blobs, no parseable data
**Status:** REPLACED by Firecrawl — don't use curl for entertainment sites

## Key Learning: Firecrawl is the Solution

**Old approach (failed):**
- Try browser tool → blocked
- Try curl → returns JS
- Fall back to manual research

**New approach (works):**
- Use Firecrawl API → clean data
- Target specific entertainment sites
- Build automated content scouts

## Site-Specific Firecrawl Patterns

### TrailerAddict
**Best for:** New trailer drops, release announcements
**Data extracted:** Trailer titles, poster URLs, studio info
**Rate:** Check daily for fresh content

```bash
curl -X POST "https://api.firecrawl.dev/v1/scrape" \
  -d '{"url": "https://www.traileraddict.com", "formats": ["markdown"]}'
```

### Rotten Tomatoes
**Best for:** Weekend watchlists, critic consensus
**Data extracted:** "What to Watch This Weekend", Top Movies
**Rate:** Check Thursdays/Fridays for weekend previews

### IMDb MovieMeter
**Best for:** Popular films by search volume
**Data extracted:** Rankings, ratings, vote counts
**Parser needed:** Extract ratings like "8.5 (453K)"

### TMDB
**Best for:** Comprehensive movie database
**Data extracted:** Movie info, streaming platforms, release dates

## Automation Now Possible

With Firecrawl, you can now:

✅ **Automated daily briefs** - Scrape 4 sources, compile trending
✅ **Trailer drop alerts** - Check TrailerAddict every 6 hours  
✅ **Weekend watch research** - Auto-extract RT "What to Watch"
✅ **Competitor tracking** - Monitor other reaction channels
✅ **Keyword research** - Extract trending search terms

## Data Integrity Rule

**CRITICAL:** Always label data source type

```json
{
  "lastUpdated": "2026-08-28T19:01:00Z",
  "researchSources": [
    {
      "source": "TrailerAddict",
      "status": "✅ Scraped successfully via Firecrawl",
      "findings": "5 new trailers identified"
    }
  ]
}
```

**Never present template/example data as scraped findings.**

## Recommended Research Workflow (Updated)

1. **Firecrawl primary sites** (TrailerAddict, RT, IMDb, TMDB)
2. **Parse structured data** from markdown output
3. **Manual check Netflix** (app required)
4. **Compile JSON** for dashboard
5. **Update dashboard** with real research timestamp
6. **Deploy** so Andrew sees live data

**Cycle:** Can run fully automated now, or on-demand when Andrew requests research.
