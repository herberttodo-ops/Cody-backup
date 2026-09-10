# First Watch Society - Dashboard Integration

Reference for integrating Firecrawl research into the Vercel dashboard.

## Dashboard Data File

**Location:** `~/.openclaw/workspace/master-control-dashboard/data/first-watch-intelligence.json`

**Purpose:** Real-time trending content for YouTube channel

## JSON Schema

```json
{
  "lastUpdated": "2026-08-28T19:01:00Z",
  "trending": [
    {
      "id": "1",
      "title": "Movie Title",
      "type": "movie",
      "source": "TrailerAddict",
      "views": "Just dropped",
      "age": "New trailer",
      "priority": "high",
      "angle": "Suggested reaction approach",
      "status": "not-reacted"
    }
  ],
  "gaps": [
    {
      "title": "Content Gap Name",
      "opportunity": "Why this is underserved",
      "potential": "500+ subs"
    }
  ],
  "upcoming": [
    {
      "date": "This Weekend",
      "title": "Upcoming Release",
      "action": "What to do",
      "priority": "high"
    }
  ],
  "competitors": [
    {
      "channel": "Competitor Name",
      "subs": "450K",
      "strengths": "What they do well",
      "lesson": "Takeaway for your channel"
    }
  ],
  "ideas": [
    "Title idea 1",
    "Title idea 2"
  ],
  "keywords": [
    "trending keyword 1",
    "trending keyword 2"
  ]
}
```

## Key Fields

| Field | Purpose | Example |
|-------|---------|---------|
| `lastUpdated` | ISO timestamp for data freshness | `"2026-08-28T19:01:00Z"` |
| `title` | Movie/show name | `"Coyote vs. Acme"` |
| `source` | Where found (TrailerAddict, RT, IMDb, TMDB) | `"Ketchup Entertainment"` |
| `priority` | HIGH = React ASAP, MEDIUM = Within week | `"high"` |
| `angle` | Your unique take/reaction hook | `"Shelved film controversy"` |
| `status` | `"not-reacted"` or `"done"` | `"not-reacted"` |

## Research Workflow

1. **Run scrapes** on 4 sources (TrailerAddict, Rotten Tomatoes, IMDb, TMDB)
2. **Parse findings** into trending, gaps, upcoming arrays
3. **Update JSON** file with new data
4. **Rebuild** Next.js app (`npm run build`)
5. **Deploy** to Vercel (`vercel deploy --prod`)
6. **Verify** dashboard shows fresh data
7. **Deliver brief** to user

## Validation Checklist

Before deploying:
- [ ] `lastUpdated` set to current time
- [ ] `trending` array has at least 3 items
- [ ] `gaps` array highlights low-competition opportunities
- [ ] All HIGH priority items have strong angles
- [ ] Keywords reflect actual trending search terms

## Real Example (August 28, 2026)

```json
{
  "trending": [
    {
      "id": "1",
      "title": "Coyote vs. Acme",
      "type": "movie",
      "source": "Ketchup Entertainment",
      "views": "Viral interest",
      "age": "Recently revived",
      "priority": "high",
      "angle": "Shelved film finally releasing - built-in controversy/fan interest",
      "status": "not-reacted"
    },
    {
      "id": "2",
      "title": "Finding Emily",
      "type": "movie",
      "source": "Focus Features",
      "views": "Just dropped",
      "age": "New trailer",
      "priority": "high",
      "angle": "New trailer just released - perfect for quick reaction",
      "status": "not-reacted"
    }
  ],
  "gaps": [
    {
      "title": "Coyote vs. Acme",
      "opportunity": "Shelved film getting release - unique angle, low competition",
      "potential": "500+ subs"
    }
  ]
}
```

## Dashboard UI Rules

When updating the dashboard:

1. **Make Intelligence tab FIRST** - users land on trending data
2. **Yellow highlighting** for Intelligence tab - stands out visually  
3. **Trending preview on Overview** - shows top 3 items briefly
4. **"Full Intel →" button** on preview card to jump to full data
5. **Updated timestamp visible** - users know data freshness

## Automation Target

Goal: Automated daily research that delivers to user:

```
Time: 8:00 AM daily
Trigger: Cron job or user command "/brief"
Action: Run 4 scrapes, compile JSON, display in dashboard, send Telegram summary
Output: Morning content briefing with 3-5 reaction opportunities
```

## Related Files

- Dashboard page: `app/first-watch-society/page.tsx`
- Data file: `data/first-watch-intelligence.json`
- Scout script: `~/.hermes/cron/scripts/firstwatch-content-scout.py`
