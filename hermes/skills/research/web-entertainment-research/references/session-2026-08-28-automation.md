# Session 2026-08-28: Automated Content Intelligence for YouTube

## Key Lessons Learned

### 1. Firecrawl API vs Browser Tools

**Lesson:** Firecrawl API was the working solution when browser tools failed.

**What Failed:**
- `browser_navigate` to YouTube/IMDb/RT = bot detection or bot blocks
- Standard Playwright browsers couldn't bypass entertainment site protections
- Google Search via browser = captcha redirect

**What Worked:**
- `curl` to `api.firecrawl.dev/v1/scrape` = clean markdown, no blocks
- Returned structured data ready for parsing
- Works even on JavaScript-heavy sites

**Pattern:**
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://site.com", "formats": ["markdown"]}' \
  2>&1 | jq -r '.data.markdown'
```

### 2. Cron Automation Key Steps

**Found Deployment Blocker:**
- Auto-cron via `hermes_tools.cronjob()` failed
- Cron script using browser tools fails because it can't prompt user

**Working Solution:**
1. Write Python script using `subprocess.run(curl...)` instead of browser tools
2. `chmod +x` set on script
3. `crontab -e` to add entry
4. `source ~/.profile` ensures env vars loaded

**Cron Schedule:**
```bash
0 8,18 * * * source ~/.profile; /home/herby/.hermes/scripts/fws-auto-intel.sh
```

### 3. Vercel Dashboard Auto-Deploy

**Working Pattern:**
1. Update JSON data file first
2. `npm run build` (from dashboard directory)
3. `vercel deploy --prod --yes`

### 4. Research Output Structure

**Dashboard JSON Schema:**
```json
{
  "lastUpdated": "ISO timestamp",
  "trending": [{
    "title": "...",
    "priority": "high" | "medium",
    "angle": "...",
    "researchComplete": true,
    "watchStatus": "..."
  }]
}
```

## Files Created

- `~/.hermes/scripts/fws-auto-intel.py` - Main research script
- `~/.hermes/scripts/fws-auto-intel.sh` - Cron wrapper
- Cron entry added for automatic execution
