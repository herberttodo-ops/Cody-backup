# RFP Weekly Brief Skill

Fetch and digest government RFP opportunities for Rival Productions, delivered to Telegram.

## What it does

- Fetches video/production RFPs from SAM.gov (federal opportunities)
- Scores by relevance to Rival Productions
- Formats as a Telegram-friendly digest
- Can be scheduled via cron or triggered manually

## Setup

### 1. Get a SAM.gov API Key

1. Visit https://open.sam.gov/
2. Register for a free account
3. Create an API key (in Account Settings)
4. Copy the key

### 2. Configure the skill

Set the environment variable in your OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "rfp-weekly": {
        "enabled": true,
        "env": {
          "SAM_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

### 3. Schedule it

Add a cron job to run every Monday at 8 AM:

```bash
openclaw cron add \
  --name "Weekly RFP Brief" \
  --schedule "cron:0 8 * * 1 America/New_York" \
  --payload '{"kind":"agentTurn","message":"Run the RFP weekly brief and send to Telegram"}' \
  --delivery '{"mode":"announce","channel":"telegram"}'
```

Or run manually:

```bash
openclaw invoke rfp-weekly --action fetch
```

## How it works

1. **Fetch**: Queries SAM.gov API for opportunities posted in the last 7 days
2. **Score**: Rates each opportunity (0-100) based on relevance to video/production
3. **Filter**: Keeps top 5 by score
4. **Format**: Converts to Telegram-friendly markdown with emojis
5. **Send**: Delivers via Telegram to your configured channel

## Output example

```
📋 Rival Productions Weekly RFP Brief
📅 Friday, February 13, 2026
🔍 Source: SAM.gov

Top 5 Opportunities:

1. Video Production Services for Department of Veterans Affairs
🏛️ Department of Veterans Affairs
📍 Virginia
⏰ Due: 2026-02-28
Fit: 🟢🟢🟢⚪⚪ 60/100
🔗 https://sam.gov/opp/...
```

## Notes

- SAM.gov API is public but requires an API key (free)
- Opportunities are fetched from the last 7 days (configurable)
- Fit score prioritizes: keyword matches (video, production, etc.), priority states (PA/NJ/DE), matching NAICS codes
- Response deadlines may have extended hours (check SAM.gov directly)

## Future expansions

- Add state-level RFP sources (PA, NJ, DE portals)
- Include local/municipal opportunities
- Add industry-specific filters (explainer videos, corporate comms, etc.)
- Track applied/won opportunities
- Integrate with project management system
