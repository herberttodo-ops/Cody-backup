# Firecrawl CLI Reference for Entertainment Scraping

## Commands

### TrailerAddict
```bash
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" -H "Content-Type: application/json" -d '{"url": "https://www.traileraddict.com", "formats": ["markdown"]}' | jq -r '.data.markdown'
```

### Rotten Tomatoes
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" -H "Content-Type: application/json" -d '{"url": "https://www.rottentomatoes.com", "formats": ["markdown"]}' | jq -r '.data.markdown'

### IMDb MovieMeter
curl -s -X POST "https://api.firecrawl.dev/v1/scrape" -H "Content-Type: application/json" -d '{"url": "https://www.imdb.com/chart/moviemeter/", "formats": ["markdown"]}' | jq -r '.data.markdown'

## Notes
- Each scrape uses 1 credit
- Free tier: 500 credits/month
- Markdown format recommended for clean extraction