# Dashboard Integration Pattern

## Creating a Content Intelligence Dashboard

### Overview
When Andrew requests research for First Watch Society, the output must be integrated into the Vercel Master Control Dashboard, not delivered as files or lists.

### File Structure
```
master-control-dashboard/
├── data/
│   └── first-watch-intelligence.json     # Research data store
└── app/
    └── first-watch-society/
        ├── page.tsx                           # Main page with Intelligence tab
        └── guide/
            └── page.tsx                       # Full guide (optional)
```

### Data Schema
```json
{
  "lastUpdated": "2026-08-28",
  "trending": [...],
  "gaps": [...],
  "upcoming": [...],
  "competitors": [...],
  "ideas": [...],
  "keywords": [...]
}
```

### Key Requirements
- Use `useTheme()` from ThemeProvider (NEVER custom dark mode)
- Responsive layouts (grid-cols-1 sm:grid-cols-2 lg:grid-cols-3)
- Mobile-first touch targets
- Everything accessible via Vercel Master Control
