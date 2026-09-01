---
title: Web Scraping for Content Intelligence
description: Patterns for scraping entertainment/content sites to extract trending data, with focus on title cleaning, deduplication, and data enrichment.
name: web-scraping-content-intelligence
triggers:
  - scraping movie trailers
  - extracting trending content
  - parsing entertainment sites
  - building content dashboards
  - automated content discovery
---

# Web Scraping for Content Intelligence

## Overview

Scraping entertainment sites (TrailerAddict, IMDb, Rotten Tomatoes) to extract trending movies, trailers, and content opportunities for reaction channels, content creators, and trend tracking.

## Core Patterns

### 1. Title Extraction & Cleaning

**Order Matters for String Replacement**

When cleaning scraped titles, replace MORE SPECIFIC patterns before LESS SPECIFIC ones:

```python
# WRONG - leaves trailing numbers
"Minions & Monsters Trailer 2".replace("Trailer", "").strip()
# Result: "Minions & Monsters 2" ❌

# CORRECT - removes the full pattern first
clean_title = title.replace(' Trailer 2', '').replace(' trailer 2', '')
clean_title = clean_title.replace(' Trailer', '').replace(' trailer', '')
clean_title = clean_title.strip()
# Result: "Minions & Monsters" ✓
```

**Pitfall:** Always replace numbered variants ("Trailer 2", "Trailer 3") before unnumbered variants ("Trailer") or you'll leave orphaned numbers in titles.

### 2. Deduplication Logic

```python
seen_titles = set()
for title, url in scraped_matches:
    clean_title = clean_title(title)
    if clean_title in seen_titles:
        continue
    seen_titles.add(clean_title)
```

### 3. Source Detection from URLs

```python
source = "Various"
if 'netflix' in url.lower():
    source = "Netflix"
elif 'amazon' in url.lower() or 'prime' in title.lower():
    source = "Amazon MGM"
elif 'universal' in url.lower():
    source = "Universal"
elif 'focus' in url.lower():
    source = "Focus Features"
elif 'ketchup' in url.lower():
    source = "Ketchup Entertainment"
```

### 4. Known Movie Database Fallback

Maintain a dictionary of known movies with enriched data (talking points, title options, thumbnail concepts) so newly scraped items get auto-enriched.

### 5. Generic Fallback for Unknown Movies

For movies not in the known database, provide a generic structure with placeholders:

```python
{
    "genre": "TBD",
    "whatIsIt": f"Recently trending: {title}",
    "whyTrending": "Appearing on TrailerAddict trending page",
    "reactionHook": "Fresh trailer = first-mover opportunity",
    "titleOptions": [...],
    "talkingPoints": [...]
}
```

## Firecrawl API Pattern

```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://www.traileraddict.com", "formats": ["markdown"]}'
```

Extract pattern for markdown links:
```regex
\[([^\]]+)\]\((https://traileraddict\.com/[^)]+)\)
```

## Skip List for Non-Movie Items

```python
skip_terms = ['prev', 'next', 'page', 'home', 'archive', 'featured']
if any(x in clean_title.lower() for x in skip_terms):
    continue
```

## Automation Cron Pattern

```cron
0 8 * * *  source ~/.profile; /path/to/script.sh >> /path/to/log 2>&1
0 18 * * * source ~/.profile; /path/to/script.sh >> /path/to/log 2>&1
```

## Deployment via Cron

Use `npx` not bare `vercel` command:

```python
subprocess.run(
    ["npx", "vercel", "deploy", "--prod", "--yes", "--token", token],
    capture_output=True, text=True, timeout=120
)
```

## References

- `references/title-cleaning-patterns.md` - Session-specific extraction lessons
