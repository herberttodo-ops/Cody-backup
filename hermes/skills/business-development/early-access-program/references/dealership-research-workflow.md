# Dealership-Specific Research Workflow

## Overview

Step-by-step process for researching car dealerships (or similar local businesses with websites) as beta targets for early access programs.

## Step 1: Geographic Prioritization

### Heat Map Approach (for aged inventory)
States with extreme weather = faster inventory aging = higher urgency:
1. **Arizona** (110°F+ summers)
2. **Texas** (high volume, independent culture)
3. **Florida** (humidity + heat)
4. **Nevada** (desert heat)

### Volume Approach
States with highest dealership density:
1. **California** (volume, but saturated)
2. **Texas** (independent dealers)
3. **Florida** (year-round market)

## Step 2: Website Contact Extraction

### Browser Automation Pattern
```
1. Navigate to dealership.com
2. Click "About Us" in nav
3. Look for: GM name, Owner name, "Meet the Team"
4. Click "Contact" 
5. Extract: Phone, address, hours
6. Check footer for social links (LinkedIn, Facebook)
```

### Common Website Structures
| Page Section | What to Extract |
|--------------|----------------|
| Home page | Current promotions (pain signals: "We Buy Cars", "Aged Inventory") |
| About Us | GM name, ownership info, years in business |
| Contact | Phone, address, email form |
| Meet the Team | Decision maker names, titles |
| Sell Your Car | Trade-in offers (indicates inventory movement focus) |

### Red Flags (Skip These)
- No website (outdated operation)
- Only corporate contact form (no direct access)
- Part of massive group with no local autonomy
- Recently opened (no aged inventory yet)

## Step 3: Tier Classification

### Scoring Matrix
| Factor | Weight | Score |
|--------|--------|-------|
| Pain signals visible | 3x | 1-5 |
| Contact info found | 2x | 1-5 |
| Decision maker accessible | 2x | 1-5 |
| Inventory size (estimated) | 1x | 1-5 |
| Geographic priority | 1x | 1-5 |

**Tier 1:** Score 25-40 (immediate outreach)
**Tier 2:** Score 15-24 (nurture first)
**Tier 3:** Score <15 (strategic/long-term)

## Step 4: Dashboard Integration

### JSON Schema for Dashboard
```json
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
  "contactStrategy": "Call + LinkedIn",
  "notes": "Extreme heat market, large single-point"
}
```

### Status Progression
```
Researching → Contact Found → Outreach Sent → Demo Scheduled → Beta Signed → Active → Case Study
```

## Step 5: Outreach Preparation

### First Call Script (Dealerships)
```
"Hi [Name], this is Andrew. I'm building a tool specifically for 
aged inventory marketing automation. I know [Dealership] carries 
significant inventory in [Location] - every day a unit sits costs money.

I'm looking for 3-5 dealerships to beta test free for 60 days. 
No cost, just honest feedback on whether it saves time and moves metal.

Do you have 15 minutes this week?"
```

### LinkedIn Connection Message
```
Hi [Name], saw [Dealership]'s focus on [specific thing from research]. 
Quick question - how do you currently handle aged inventory marketing?

Not selling anything, just researching what works for [location] dealers.
- Andrew
```

## Tools & Resources

### Free Research Stack
| Tool | Purpose | Limit |
|------|---------|-------|
| Dealership website | Contact info, pain signals | Manual |
| LinkedIn (free) | GM profiles, connections | 100 connections/week |
| Google Maps | Location verification, reviews | Unlimited |
| State dealer associations | Member lists | Varies by state |

### Paid Alternatives
- Apollo.io: $0-50/month for contact data
- LinkedIn Sales Navigator: $80/month
- Hunter.io: $49/month for email finding
