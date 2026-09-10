# Dashboard Integration Pattern for Beta Outreach

## Overview

When building a Next.js dashboard to track beta outreach targets, follow this pattern for clean integration.

## Data Flow

```
1. Research targets → 2. Store in JSON → 3. Dashboard reads JSON → 4. User views/interacts
```

## JSON Schema

```json
{
  "lastUpdated": "2025-09-01",
  "strategy": "Focus on high-heat markets (Arizona, Texas, Florida) with acute aged inventory pain",
  "tiers": {
    "tier1": {
      "label": "Immediate Outreach",
      "criteria": "High aged inventory, single location, active on social, warm climate markets",
      "targets": [
        {
          "id": "T1-001",
          "dealership": "Camelback Ford Lincoln",
          "location": "Phoenix, AZ",
          "website": "camelbackford.com",
          "phone": "844-873-7964",
          "size": "Single location",
          "priority": "High",
          "estimatedInventory": 150,
          "tier": "Tier 1",
          "status": "Contact Found",
          "contactStrategy": "Call + LinkedIn outreach",
          "notes": "Extreme heat market"
        }
      ]
    }
  }
}
```

## Next.js Integration

### Import Pattern
```typescript
import betaTargets from '@/data/lotsignal-beta-targets.json';

// In component
const tier1Count = betaTargets.tiers.tier1.targets.length;
const targets = betaTargets.tiers.tier1.targets;
```

### Tab Addition Pattern
Add new tab to existing tabs array:
```typescript
const tabs = ['overview', 'content', 'dealers', 'schedule', 'beta'] as const;

// In tab navigation
{tabs.map((tab) => (
  <button key={tab} onClick={() => setActiveTab(tab)}>
    {tab === 'beta' ? 'Beta Targets' : tab.charAt(0).toUpperCase() + tab.slice(1)}
  </button>
))}
```

### Display Pattern
```typescript
{targets.map((target) => (
  <div key={target.id} className="...">
    <h4>{target.dealership}</h4>
    <p>{target.location}</p>
    <a href={`https://${target.website}`}>Website</a>
  </div>
))}
```

## Google Sheet Sync

### Two-Way Sync Pattern
```
Dashboard JSON ←→ Google Sheet
     ↓                    ↑
  Display              Research
```

### Sheet Structure
| Column | Purpose |
|--------|---------|
| ID | Target identifier |
| Dealership Name | Display name |
| Location | City, State |
| Contact Name | GM/Decision maker |
| Phone | Direct line |
| Tier | 1/2/3 |
| Status | Researching → Contact Found → Outreach → Demo → Signed |
| Next Action | Specific follow-up task |
| Notes | Context from research |

### Python Sync Script
```python
from google_api import build_service

# Read from sheet
service = build_service("sheets", "v4")
result = service.spreadsheets().values().get(
    spreadsheetId=SPREADSHEET_ID,
    range='Dealership Pipeline!A2:N20'
).execute()

# Convert to JSON for dashboard
import json
targets = []
for row in result.get('values', []):
    targets.append({
        'id': row[0],
        'dealership': row[1],
        # ... etc
    })

# Write to JSON file
with open('data/targets.json', 'w') as f:
    json.dump({'targets': targets}, f, indent=2)
```

## Build & Deploy

### Static Export
```javascript
// next.config.js
const nextConfig = {
  output: 'export',
  distDir: 'dist',
  images: { unoptimized: true }
}
```

### Deployment Options
1. **Vercel CLI:** `npx vercel --prod` (requires login)
2. **Git push:** Auto-deploy if connected to Git
3. **Manual upload:** Drag dist/ folder to Vercel dashboard

## Common Pitfalls

1. **JSON in static export:** Next.js `output: 'export'` inlines JSON imports at build time. Changes to JSON require rebuild.
2. **Browser vs server:** Don't use browser tools (navigate, click) in build step. Research happens before build.
3. **Token scope mismatch:** Vercel tokens may be scoped to wrong team. Always verify with `npx vercel login`.
4. **Git repo location:** Ensure `.git` is in project root, not parent directory.
