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

No standalone reports. Everything lives in dashboard JSON:

```json
{
  "trending": [
    {
      "title": "Superman (2025) Final Trailer",
      "type": "trailer",
      "views": "8.2M",
      "age": "6 hours ago",
      "priority": "high",
      "angle": "DC newcomer perspective",
      "status": "not-reacted"
    }
  ],
  "gaps": [
    {
      "title": "Low competition on older Tom Cruise",
      "opportunity": "Mission: Impossible retrospective",
      "potential": "200-500 subs"
    }
  ],
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

**On-Demand Research:**
"Find trending 90s movies on TikTok"
"What's #1 at box office this weekend?"
"Analyze competitor reactions to [title]"

## Tools Available

- Browser (check YouTube, Reddit, news sites)
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
