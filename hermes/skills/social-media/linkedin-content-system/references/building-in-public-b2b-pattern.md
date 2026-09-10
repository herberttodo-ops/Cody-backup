# Building in Public + Business Authority Pattern (B2B)

## Overview

A dual-content strategy for B2B SaaS companies where you simultaneously establish:
1. **Business Page**: Professional authority, product features, customer wins
2. **Personal Profile**: Authentic founder journey, problem-solving process, behind-the-scenes

This pattern works for B2B products where trust comes from seeing the human process, not just polished marketing.

## Content Split

### Business Page (The Solution)
**Goal**: Position as authoritative tool for industry
**Audience**: Decision makers, buyers, industry peers
**Tone**: Professional, data-driven, helpful

**Content Pillars**:
- Industry insights and statistics
- Customer success stories
- Product features and benefits
- Best practices and how-tos

**Example Topics**:
- "Aged inventory costs $100/day per unit"
- "How [Dealer] moved 12 units in 8 days"
- "73% of dealership marketing spend is wasted"

### Personal Profile (The Journey)
**Goal**: Document authentic problem-solving process
**Audience**: Fellow entrepreneurs, early adopters, potential beta testers
**Tone**: Authentic, humble, learning in public

**Content Pillars**:
- Solving real customer problems
- Product evolution and mistakes
- Industry observations from conversations
- Personal wins and learnings

**Example Topics**:
- "Spent 30 min on phone with Ford GM today..."
- "I built the wrong thing. Twice."
- "Three months ago I thought this was a tracking problem"

## Weekly Schedule Template

| Day | Business | Personal |
|-----|----------|----------|
| **Monday** | Industry stat/data | - |
| **Tuesday** | Marketing tip | Building in public reflection |
| **Wednesday** | Customer story | - |
| **Thursday** | Product feature | Dealer conversation insight |
| **Friday** | Quick win/result | - |
| **Saturday** | - | Weekend reflection/learning |

**Optimal Times**:
- Business: 8:00 AM EST (professionals start day)
- Personal: 7:00 PM EST (evening scroll time)

## Content Templates

### Business: Aged Inventory Cost
```
❌ Not a slow leak
🚨 A hemorrhage

Daily carrying cost per unit aged 60+ days:
• Floorplan interest: $12-25
• Lot depreciation: $15-40
• Insurance/maintenance: $8-15
• Opportunity cost: $50-80

= $85-160 PER DAY

A dealer with 25 aged units is losing $2,125-$4,000 weekly.

In silence.

While marketing focuses on new arrivals.

#DealershipMarketing #AgedInventory
```

### Personal: Dealer Conversation
```
🚗 Spent 30 minutes on the phone with a Ford GM in Arizona today.

He told me something that shocked me:

"Andrew, every aged unit on my lot is a $100/day loan I'm not paying off. And nobody's marketing them."

Think about that.

$100/day.
Per unit.
25 units = $2,500/day in silent carrying cost.

That's not theory.
That's his reality.

This is why I'm doing this.

#BuildingInPublic #CustomerDiscovery
```

### Personal: Product Evolution
```
🔧 Built this feature wrong the first time.

LotSignal's first campaign generator:
• Pick vehicles manually
• Choose channels
• Write custom copy
• Schedule timing
• Review before posting

Dealers used it once. Then stopped.

V2 (what I thought was solution):
Pre-drafted campaigns dealers could edit.

Result: Still too slow.

V3 (shipping now):
1. Scan inventory (automated)
2. Click "Generate"
3. Approve or modify
4. Auto-post

From 4 steps → 1 click.

The lesson: Speed beats features.

#BuildingInPublic #ProductDesign
```

## Dashboard Integration

Track both content streams in a unified dashboard:

**Data Files**:
- `channel.json` — Brand config, posting schedule
- `content-bank.json` — Pre-written posts with metadata
- `outreach.json` — Prospects/CRM tracking

**UI Pattern**:
- Split view: Business vs Personal content
- Status tracking: ready/posted/scheduled
- Scheduling calendar with timezone awareness
- "Next post in" countdown timer

## Engagement Strategy

### Daily (10 min)
1. Comment on 3 industry posts — add value, not pitch
2. Reply to all comments on your posts
3. Share 1 insight from dealer conversations

### Weekly (30 min)
1. DM 5 new connections — personalized, no pitch
2. Engage with industry association content
3. Comment on 10 dealer/GM posts

## Key Lessons from Implementation

### Lesson 1: Title Cleaning Bug
When scraping content from sources like TrailerAddict:
- Input: "Minions & Monsters Trailer 2"
- Bad cleaning: → "Minions & Monsters 2" (kept "2" from "Trailer 2")
- Good cleaning: → "Minions & Monsters"

**Fix**: Remove numbered suffixes BEFORE generic suffixes:
```python
title = title.replace(' Trailer 2', '').replace(' trailer 2', '')
title = title.replace(' Trailer', '').replace(' trailer', '')
```

### Lesson 2: Fallback Data Preservation
When scraper fails, don't lose rich context:
- Load existing JSON before scraping
- Merge new findings with detailed existing entries
- Preserve talking points, title options, sources

### Lesson 3: Dealer CRM Integration
Social strategy connects to sales outreach:
- Track dealer pain points from conversations
- Document GM names and next actions
- Link content themes to actual customer problems

## Hashtag Strategy

### Business
- Primary: #DealershipMarketing #AgedInventory #CarDealer
- Secondary: #AutoRetail #LotSignal #InventoryManagement

### Personal
- Primary: #BuildingInPublic #StartupLife #SaaS
- Secondary: #CustomerDiscovery #DealershipTech #FounderJourney

**Rule**: 3-5 hashtags max per post. Quality over quantity.

## Success Metrics

### Month 1
- [ ] LinkedIn followers: 500 (business), 300 (personal)
- [ ] Weekly posts: 5 business + 3 personal
- [ ] Engagement rate: 3%+
- [ ] Inbound inquiries: 10+ combined

### Month 3
- [ ] LinkedIn followers: 2,000+ (business), 1,000+ (personal)
- [ ] Established as "aged inventory marketing guy"
- [ ] 3+ customer case studies published
- [ ] 25+ beta signups from social

## Related Patterns

- `dashboard-content-intelligence` — Automated scraping and brief generation
- `social-media-workflow` — Buffer MCP scheduling patterns
- `linkedin-content-system` — Quality scoring and dual-version output

---

*Pattern extracted from LotSignal social media strategy build*
