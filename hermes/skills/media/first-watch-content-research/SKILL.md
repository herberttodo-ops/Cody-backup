---
name: first-watch-content-research
version: 1.0.1
description: "Research trending trailers, movies, and content ideas for First Watch Society YouTube channel. Provides daily/weekly intel reports with titles, thumbnails, and upload timing. INTEGRATES INTO VERCEL DASHBOARD for persistent access."
author: Hermes Agent
---

# First Watch Society - Content Research Workflow

## When to Use
Use when Andrew needs:
- Daily trailer drop alerts
- Trending movie/TV research
- Weekly content intel reports
- Competitor analysis
- Title/thumbnail suggestions
- Real-time content ideas

**Critical:** All research OUTPUT should be integrated into the Vercel Master Control Dashboard under `/first-watch-society`. Andrew expects a unified location for all channel operations, not scattered files.

## User Context
- **Channel:** First Watch Society (@FirstWatchSociety)
- **Host:** Nick Vergara
- **Niche:** Movie/TV/Trailer reactions
- **Goal:** YouTube Partner Program (1K subs, 4K hours)
- **Budget:** $0/low-cost tools
- **Upload schedule:** 3-4x/week
- **Preferred output:** Dashboard-integrated, structured data
- **Key preference:** Everything must be accessible via Vercel Master Control

## Research Sources

### Primary Sources (Check Daily)
1. **YouTube Trending** - youtube.com/feed/trending
2. **r/movies** - reddit.com/r/movies hot posts
3. **Studio Twitter/X:** @MarvelStudios, @DCOfficial, @Netflix, @PrimeVideo, @DisneyPlus
4. **Entertainment News:** Deadline.com, Variety.com
5. **Box Office:** BoxOfficeMojo.com

### Secondary Sources
- Google Trends
- TikTok trending sounds/movies
- Letterboxd popular
- IMDb Top 10

## Research Workflow

### Step 1: Research
Use browser tools to check:
- YouTube trending page
- Studio social media accounts
- Reddit hot posts
- Entertainment news sites

### Step 2: Structure Data
Create JSON file with findings:
```json
{
  "lastUpdated": "2026-08-28",
  "trending": [...],
  "gaps": [...],
  "upcoming": [...],
  "competitors": [...]
}
```

### Step 3: Dashboard Integration (CRITICAL)
Place data in: `~/.openclaw/workspace/master-control-dashboard/data/first-watch-intelligence.json`

Update dashboard page: `app/first-watch-society/page.tsx`

**Must include these sections:**
- **Research Request Box** - Text input for Andrew to request new research
- **Trending Now** - Currently hot content with suggested angles
- **Content Gaps** - Low competition opportunities
- **Upcoming Releases** - Calendar of must-react content
- **Competitor Intel** - What other channels are doing
- **Content Ideas Bank** - Evergreen series ideas
- **SEO Keywords** - Trending search terms

### Step 4: Deploy
Build and deploy so updates go live immediately.

## Dashboard UI Pattern

The Intelligence tab should have:

**Header with Research Request:**
```tsx
<div className="border-2 border-yellow-500 p-6">
  <h2>🔍 Research Request</h2>
  <textarea placeholder="Ask me to research trending topics..." />
  <button>Submit Research Request</button>
</div>
```

**Trending Cards:**
- Title + Priority badge (HIGH/MEDIUM)
- View count + age
- Suggested angle
- Status (Not Reacted / Done)

**Content Gap Cards:**
- Title
- Opportunity description
- Potential sub gain

## Output Format (Dashboard-Integrated)

No standalone reports. Everything lives in dashboard JSON. Use **expanded detail structure** for maximum value:

### Full Trending Item Structure (Recommended)

```json
{
  "lastUpdated": "2026-08-29T15:30:00Z",
  "researchSources": [...],
  "trending": [
    {
      "id": "1",
      "title": "Finding Emily",
      "type": "movie",
      "genre": "Thriller/Drama",
      "source": "Focus Features/Netflix",
      "views": "1M+ views on trailer",
      "age": "New trailer",
      "priority": "high",
      "angle": "Netflix partnership - trending on TrailerAddict #1",
      "status": "not-reacted",
      "researchComplete": true,
      "watchStatus": "Theatrical only - streaming TBA",
      "releaseDate": "August 28, 2026",
      "availableOn": ["theaters"],
      "notAvailableOn": ["Netflix", "Max", "VOD"],
      "whatIsIt": "Psychological thriller where a woman searches for her missing sister in a remote town",
      "whyTrending": "Trailer 2 currently #1 on TrailerAddict; Netflix distribution announced",
      "reactionHook": "First-mover on Netflix thriller with 'first time watching' angle",
      "titleOptions": [
        "FINDING EMILY Trailer 2 REACTION | Netflix's New Thriller?",
        "FINDING EMILY - First Time Watching | This Looks CRAZY"
      ],
      "thumbnailConcept": "Dark thriller imagery + confused expression + Netflix logo",
      "talkingPoints": [
        "Focus Features + Netflix partnership = guaranteed distribution",
        "Similar narrative structure to Gone Girl, Shutter Island",
        "Small town mystery has built-in suspense hooks",
        "1M+ trailer views indicate strong audience interest"
      ],
      "sources": [
        {"site": "TrailerAddict", "url": "https://traileraddict.com/finding-emily/trailer-2"},
        {"site": "RT", "url": "https://www.rottentomatoes.com/m/finding_emily"}
      ]
    }
  ],
  "gaps": [...],
  "upcoming": [...],
  "competitors": [...],
  "ideas": [...],
  "keywords": [...]
}
```

### Required Fields

**Every trending item should have:**
- `title` - Movie/show name
- `genre` - Helpful for positioning
- `source` - Studio/distributor
- `priority` - high/medium/low
- `angle` - Your unique reaction angle

**Recommended expanded fields:**
- `whatIsIt` - One-sentence description
- `whyTrending` - Why it's hot right now
- `reactionHook` - What makes this reaction-worthy
- `titleOptions` - 2-3 ready-to-use YouTube titles
- `thumbnailConcept` - Visual direction
- `talkingPoints` - 3-4 discussion points
- `sources` - Links to research sources with `site` and `url`
  "upcoming": [...],
  "competitors": [...],
  "ideas": [...],
  "keywords": [...]
}
```

## Research Request Examples

**Dashboard Input:**
- "Find trending trailers today"
- "What movies are viral on Reddit?"
- "Research Oscar buzz films"
- "Check what dropped on Netflix this week"

**My Process:**
1. Research via browser/web search
2. Compile structured data
3. Update dashboard JSON
4. Rebuild and deploy
5. Confirm new data visible in dashboard

## Automation Architecture

### Full Automation System (Implemented)

The automation now runs via **cron jobs** executing Python scripts that:

1. **Scrape** via FIRECRAWL API (bypasses bot detection)
2. **Parse** structured data from markdown output  
3. **Generate** JSON with full research structure
4. **Deploy** dashboard updates via `npm run build` + `vercel deploy`

### Data Flow

```
Cron Trigger (8AM / 6PM EST)
  → Execute ~/.hermes/scripts/fws-auto-intel.sh
    → Run Python scout (fws-auto-intel.py)
      → Firecrawl: TrailerAddict, RT, IMDb
        → Parse trending movies
          → Generate full structure with:
            - whatIsIt, whyTrending, reactionHook
            - titleOptions, talkingPoints
            - thumbnailConcept, sources
              → Write JSON to dashboard data
                → Build & deploy Vercel
                  → Live dashboard updates
```

### Cron Schedule

Installed crontab:
```
# First Watch Society - Automated Content Intelligence
# Runs daily at 8 AM and 6 PM EST
0 8 * * *  source ~/.profile; /home/herby/.hermes/scripts/fws-auto-intel.sh >> /home/herby/.hermes/logs/fws-intel.log 2>&1
0 18 * * * source ~/.profile; /home/herby/.hermes/scripts/fws-auto-intel.sh >> /home/herby/.hermes/logs/fws-intel.log 2>&1
```

### Key Technical Pattern: Firecrawl Integration

**Python Scout** uses subprocess to call Firecrawl API:
```python
result = subprocess.run(
    ["curl", "-s", "-X", "POST", "https://api.firecrawl.dev/v1/scrape",
     "-H", "Content-Type: application/json",
     "-d", '{"url": "https://www.traileraddict.com", "formats": ["markdown"]}'],
    capture_output=True, text=True, timeout=30
)
data = json.loads(result.stdout)
markdown = data.get("data", {}).get("markdown", "")
# Parse movie titles from markdown
```

**Why:** Firecrawl cloud infrastructure bypasses bot detection that blocks local scraping

### Dashboard JSON Structure (Live Standard)

```json
{
  "lastUpdated": "2026-08-29T22:00:02Z",
  "researchSources": [...],
  "trending": [...],      // Full detail items
  "gaps": [...],           // Low competition opportunities
  "upcoming": [...],       // Calendar with "why" context
  "competitors": [...],    // Upload freq, strengths, weaknesses
  "ideas": [...],          // Ready-to-use titles
  "keywords": [...]        // SEO trending terms
}
```

### Deployment Pattern

**After JSON update:**
1. `npm run build` - TypeScript compilation
2. `vercel deploy --prod --token TOKEN --yes` - Live push
3. Verify at `https://master-control-dashboard.vercel.app/first-watch-society`

### Notes

- **TELEGRAM_BOT_TOKEN** - Optional, falls back to dashboard-only
- **Firecrawl API key** - May need explicit setting in cron environment
- **Vercel CLI path** - May need full path in cron scripts
- **Log file location:** `~/.hermes/logs/fws-intel.log`

## Key Learnings

**Andrew's Preferences:**
- Everything accessible via Vercel Master Control
- Real-time updates (not static files that drift)
- Self-service (he can browse dashboard without asking)
- Mobile-friendly (responsive design)
- Research on-demand + proactive intelligence

**Pattern Established:**
Data file → Dashboard component → Live deployment → Available anywhere

## Commands

**Research & Update Dashboard:**
"Research trending trailers for today"
"Find content gaps in the reaction space"  
"Update dashboard with weekly intel"
"Research [specific movie title]"

**On-Demand Research:**
"Find trending 90s movies on TikTok"
"What's #1 at box office this weekend?"
"Analyze competitor reactions to [title]"
"Check availability for [movie]"

## Automation Commands

**Manual trigger automation:**
```bash
# Run the content scout script
python3 ~/.hermes/scripts/fws-auto-intel.py

# Or via wrapper
bash ~/.hermes/scripts/fws-auto-intel.sh
```

**Scheduled automation (already installed):**
```bash
# View cron jobs
crontab -l | grep fws-auto-intel

# Runs daily at:
# 8:00 AM EST - Morning brief
# 6:00 PM EST - Evening brief
```

## Automation Architecture

### Python Scout (`~/.hermes/scripts/fws-auto-intel.py`)

**Components:**
1. **ContentScout class** - Scrapes websites via Firecrawl API
2. **update_dashboard()** - Generates JSON structure
3. **generate_brief()** - Creates formatted Telegram/message output
4. **deploy_dashboard()** - Rebuilds and deploys Vercel

**Data Flow:**
```
Scrape (TrailerAddict, RT, IMDb, TMDB) 
  → Process/Parse
    → Update JSON
      → Build/Deploy
        → Live dashboard
```

**Key Methods:**
- `scrape_traileraddict()` - Extract featured trailers
- `scrape_google_trends()` - Get trending search terms
- `generate_gaps()` - Identify low-competition opportunities
- `update_dashboard()` - Write JSON with full structure

### Environment Note

**Firecrawl API Key:** May need to check if available in cron environment. The automation falls back to curated data if Firecrawl unavailable.

**Vercel CLI:** Full path may be needed in cron scripts since PATH differs in cron vs interactive shell.

## Research Request Examples

**Dashboard Input:**
- Web search
- Dashboard JSON editing
- Vercel deployment

## Deployment Checklist

After each research update:
- [ ] JSON data file updated
- [ ] Dashboard component imports data
- [ ] npm run build succeeds
- [ ] vercel deploy succeeds
- [ ] Live URL accessible
- [ ] Data displays correctly on mobile
