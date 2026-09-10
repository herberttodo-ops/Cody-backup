# Vercel Dashboard Architecture for Content Research

## Pattern Established

When Andrew needs research integrated into the Master Control Dashboard, follow this exact architecture:

### File Structure
```
master-control-dashboard/
├── data/
│   └── first-watch-intelligence.json    # Research data store (source of truth)
└── app/
    └── first-watch-society/
        ├── page.tsx                      # Interactive dashboard tabs
        └── guide/
            └── page.tsx                  # Full markdown guide (rendered)
```

### Data Flow
1. **Research** → Update `data/*.json`
2. **Build** → `npm run build` (must succeed)
3. **Deploy** → `vercel deploy --prod --token [token] --yes`
4. **Access** → Live URL with new data

### Critical UI Patterns

#### Tabs Array Must Match State Type
```tsx
// The array must match the useState type EXACTLY
const [activeTab, setActiveTab] = useState<'overview' | 'intelligence'>('overview');

// Then map over the EXACT same array
{(['overview', 'intelligence'] as const).map((tab) => (
  <button key={tab} onClick={() => setActiveTab(tab)}>
    {tab}
  </button>
))}
```
**Pitfall:** Adding tab content without adding to navigation array = invisible tab.

#### Responsive Grid Pattern
```tsx
// Always use responsive breakpoints
<div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
```

#### Dark Mode Integration
```tsx
// ALWAYS use global theme - NEVER local state
import { useTheme } from '@/components/ThemeProvider';
const { theme } = useTheme();
const isDark = theme === 'dark';
```

### Build Success Checklist
- [ ] JSON data file syntax valid
- [ ] TypeScript types match JSON structure
- [ ] All imported JSON properties exist
- [ ] npm run build succeeds
- [ ] Vercel deploy succeeds
- [ ] Mobile layout verified

### Token Management
The Vercel token lives in the deployment command. Andrew manages token access.
```bash
vercel deploy --prod --token [token] --yes
```
