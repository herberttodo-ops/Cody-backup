# $0 Research Stack for Early Access Programs

## The Challenge

User needs to research decision makers and emails for beta outreach but has **$0 budget** and **no LinkedIn Sales Navigator** access. Agent cannot log into private accounts.

## The Solution: Hybrid Research + Centralized Dashboard

### Step 1: Build the Research Framework (Agent)

The agent creates:
- Target list with LinkedIn search queries per dealer
- Regional pain-angle messaging (auto-customized by location)
- Status tracking fields (Not Contacted → Connection Requested → Message Sent → etc.)

### Step 2: User Executes Research (Human)

User uses free tools directly:

| Tool | Free Tier | Best For | How to Use |
|------|-----------|----------|------------|
| **LinkedIn** | Unlimited search | Finding decision makers | Search: `"Dealer Name" Location owner OR GM` |
| **Hunter.io** | 25 searches/month | Email addresses | Enter domain, get pattern |
| **Apollo.io** | 50 contacts/month | Contact info + emails | Filter by title, company, location |
| **Lusha Extension** | 5 searches/month | Phone + email | Browser extension on LinkedIn profiles |
| **Dealer Websites** | Free | Staff pages | /about-us, /team, /staff |
| **State Dealer Associations** | Free-$50/yr | Member directories | Owner/GM names |

### Step 3: Centralize Everything in Dashboard

**Pattern:** Build an interactive Next.js dashboard deployed to Vercel:

```
┌─────────────────────────────────────────┐
│  DASHBOARD (accessible from anywhere)    │
├─────────────────────────────────────────┤
│  • 25 dealers with priority ranking      │
│  • Status tracking dropdown              │
│  • "Search LinkedIn" button per dealer   │
│  • LinkedIn DM + Email message templates  │
│  • Regional pain angles (auto by city)   │
│  • Task management for outreach          │
│  • Tools tab (links to Hunter, Apollo)   │
└─────────────────────────────────────────┘
```

**Key Features:**
- **Copy-to-clipboard buttons** for message templates
- **LinkedIn search button** opens search in new tab with pre-filled query
- **Status tracking** with color-coded badges
- **Mobile responsive** for on-the-go access
- **Dark mode** support

### Step 4: Outreach Workflow

```
1. Open dashboard on phone/desktop
2. Find dealer with "Needs Research" badge
3. Click "Search LinkedIn" → opens LinkedIn search
4. Find GM/Owner name on LinkedIn
5. Return to dashboard → update name field
6. Click "Get Messages" → choose LinkedIn or Email
7. Select message type (Day 1, 2, 4, 7)
8. Copy message → paste into LinkedIn/Gmail
9. Update status → track progress
```

## Regional Pain-Angle Messaging Pattern

When the agent cannot personalize for each dealer individually, use **location-based pain angles**:

| Region | Pain Angle | Example |
|--------|-----------|---------|
| Arizona | "110°+ heat aging inventory 2x faster than northern dealers" | Desert heat damage |
| Texas | "Desert heat + volatile oil economy putting pressure on truck inventory" | Oil boom-bust cycles |
| Pennsylvania | "Seasonal Northeast cycles creating pre-snow inventory rush" | Winter prep |
| Missouri/Kansas | "Agricultural buying cycles affecting truck demand" | Ag economy |
| Colorado | "Mountain weather + seasonal 4WD demand fluctuations" | Seasonal shifts |
| Georgia | "Atlanta metro hyper-competition making aged inventory bleed money" | Urban competition |

**Implementation:**
```typescript
const getRegionPain = (location: string) => {
  if (location.includes('AZ')) return '110°+ heat aging inventory 2x faster';
  if (location.includes('TX')) return 'desert heat + volatile oil economy';
  // ... etc
};
```

## The Commitment: "Everything Goes in the Dashboard"

**Critical workflow rule:** When user says "make sure this is accessible in the dashboard," they mean:
- All research data
- All task tracking
- All strategy documents
- All messaging templates
- All project notes

**Action:** Always create a JSON data file + interactive page + sidebar navigation entry. Deploy to Vercel immediately.

## Dashboard Sections to Include

| Section | Purpose |
|---------|---------|
| **Dealer Pipeline** | All targets, searchable/filterable |
| **Outreach Templates** | Copy-paste messages by channel |
| **Tools Tab** | Links to free research tools |
| **Task Management** | Research, outreach, setup tasks |
| **Notes/Strategy** | Research instructions, green/red flags |
| **Full Guide** | Complete markdown document rendered |

## Technical Stack

- **Frontend:** Next.js + Tailwind CSS + shadcn/ui
- **Data:** Static JSON files in `/data/`
- **State:** React useState (no backend needed for MVP)
- **Deployment:** Vercel CLI with token
- **Theme:** Dark mode via ThemeProvider context
