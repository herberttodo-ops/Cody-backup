---
name: dashboard-content-intelligence
description: Build automated content intelligence dashboards for YouTube channels, newsletters, or content creators. Scrapes trending topics, generates briefs, auto-updates Next.js dashboards, and delivers notifications. Includes Firecrawl integration, cron scheduling, and Telegram alerts.
---

# Dashboard Content Intelligence System

## Overview

Build fully automated content scouting systems that:
1. Scrape trending topics from entertainment/media sources
2. Generate actionable briefs with research depth
3. Auto-update Next.js dashboards
4. Deliver notifications via Telegram

## Architecture

```
Scraper (Firecrawl) → Parser → JSON Update → Build → Deploy → Notify
```

## Core Components

### 1. Python Scraper Script

Location: `~/.hermes/scripts/{project}-auto-intel.py`

Key pattern:
```python
def scrape_source(self) -> List[Dict]:
    try:
        result = subprocess.run(
            ["curl", "-s", "-X", "POST", 
             "https://api.firecrawl.dev/v1/scrape",
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"url": SOURCE_URL, "formats": ["markdown"]}),
            capture_output=True, text=True, timeout=30
        )
        data = json.loads(result.stdout)
        # Parse and extract trending items
        return extracted_data
    except Exception as e:
        print(f"Scrape error: {e}", file=sys.stderr)
        return []
```

### 2. Cron Automation

```bash
# Install cron jobs
crontab -l > /tmp/current_crons
echo "0 8 * * * /home/user/.hermes/scripts/project-auto-intel.sh >> /home/user/.hermes/logs/project-intel.log 2>&1" >> /tmp/current_crons
echo "0 18 * * * /home/user/.hermes/scripts/project-auto-intel.sh >> /home/user/.hermes/logs/project-intel.log 2>&1" >> /tmp/current_crons
crontab /tmp/current_crons
```

Runs twice daily: 8 AM and 6 PM.

### 3. Data Structure Pattern

```json
{
  "lastUpdated": "2026-08-29T00:00:00Z",
  "researchSources": [
    {"name": "Source", "url": "https://source.com", "status": "Active"}
  ],
  "trending": [{
    "id": "1",
    "title": "Trending Item",
    "type": "movie",
    "genre": "Genre",
    "source": "Studio/Distributor",
    "priority": "high|medium|low",
    "whatIsIt": "Full description",
    "whyTrending": "Why this is trending now",
    "reactionHook": "Your angle for the reaction",
    "talkingPoints": ["Point 1", "Point 2", "Point 3"],
    "titleOptions": ["Title 1", "Title 2"],
    "thumbnailConcept": "Visual description",
    "sources": [{"site": "Name", "url": "https://..."}]
  }],
  "gaps": [{
    "title": "Content Gap",
    "opportunity": "Why this is underserved",
    "potential": "Expected reach",
    "whyLowCompetition": "Reasoning"
  }],
  "upcoming": [{
    "date": "When",
    "title": "Event",
    "action": "What to do",
    "priority": "high|medium",
    "why": "Why this matters"
  }]
}
```

## Next.js Dashboard Integration

### TypeScript Type Assertion

When handling dynamic scraped data in Next.js:

```typescript
import rawData from '@/data/intel.json';
const data = rawData as any; // Bypass strict type checking for dynamic data
```

Then add type annotations to map functions:

```typescript
{data.trending.map((item: any, i: number) => (
  item.sources?.map((source: {site: string, url: string}, i: number) => ...)
))}
```

### Dashboard Update Flow

```bash
cd ~/.openclaw/workspace/project-dashboard
npm run build
vercel deploy --prod --token $TOKEN --yes
```

Auto-deploy happens after JSON update.

## Telegram Integration

Add to Python scraper:

```python
def send_telegram(self, message: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        return
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        'chat_id': CHAT_ID,
        'text': message,
        'parse_mode': 'HTML'
    }).encode()
    
    req = urllib.request.Request(url, data=data, method='POST')
    urllib.request.urlopen(req, timeout=10)
```

## Pitfalls

1. **TypeScript Errors**: Always use `as any` or explicit type annotations for dynamic JSON
2. **Build Failures**: Fix ALL TypeScript errors before deployment
3. **Telegram Auth**: 401 errors mean TELEGRAM_BOT_TOKEN isn't set
4. **Rate Limits**: Firecrawl free tier = 500 credits/month
5. **Vercel Token**: Must be passed to deploy command or set in env

## Research Command Pattern

When user says "research [topic]":

1. Scrape relevant sources (IMDb, RT, Google, etc.)
2. Extract detailed findings
3. Update JSON data with researchComplete: true
4. Rebuild and deploy
5. Show results with source links

## References

- Firecrawl skill: `skills/openclaw-imports/firecrawl-search/`
- Example scripts: `~/.hermes/scripts/fws-auto-intel.*`
- Title cleaning: `skills/research/web-scraping-content-intelligence/` — critical pitfall when scraping movie titles with trailer numbers

## B2B Building in Public Pattern

For B2B SaaS products (like OptiRFP, LotSignal), combine professional business authority with authentic personal storytelling:

**Business Page**: Industry stats, customer wins, product features
**Personal Profile**: Dealer conversations, feature failures, honest struggles

See `skills/social-media/linkedin-content-system/references/building-in-public-b2b-pattern.md` for full implementation.