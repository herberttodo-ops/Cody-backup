# RFP Weekly Brief - Setup & Testing

## Quick Start

### Step 1: Get SAM.gov API Key

1. Go to https://open.sam.gov/
2. Sign up (free)
3. Create API key in Account Settings
4. Copy the key

### Step 2: Add to OpenClaw Config

Edit `~/.openclaw/openclaw.json`:

```json
{
  "skills": {
    "entries": {
      "rfp-weekly": {
        "enabled": true,
        "env": {
          "SAM_API_KEY": "your-actual-key-here"
        }
      }
    }
  }
}
```

Save and the gateway will hot-reload.

### Step 3: Test Manually

Run the skill:

```bash
openclaw invoke rfp-weekly --action fetch
```

Or via web chat:

```
/rfp-weekly fetch
```

You should see a formatted digest like:

```
📋 Rival Productions Weekly RFP Brief
📅 Friday, February 13, 2026
🔍 Source: SAM.gov (Federal Opportunities)

Top 5 Opportunities:

1. Video Production Services...
🏛️ Department of Veterans Affairs
📍 Virginia
⏰ Due: 2026-02-28
Fit: 🟢🟢🟢⚪⚪ 60/100
🔗 https://sam.gov/opp/...
```

### Step 4: Schedule Weekly Delivery

Use cron to deliver every Monday at 8 AM to Telegram:

```bash
openclaw cron add \
  --name "Weekly RFP Brief" \
  --schedule "cron:0 8 * * 1 America/New_York" \
  --payload '{"kind":"agentTurn","message":"Invoke the RFP weekly brief skill and deliver to Telegram"}' \
  --delivery '{"channel":"telegram"}' \
  --sessionTarget isolated
```

Or edit the cron job in the Control UI at http://127.0.0.1:18789

## Files

- **SKILL.md** — Full documentation
- **handler.ts** — OpenClaw skill implementation (TypeScript)
- **../sam_gov_fetcher.py** — Standalone Python script (for testing/reference)

## Troubleshooting

**"SAM_API_KEY not set"**
→ Make sure you added it to the config and reloaded the gateway

**"SAM.gov API returned 401"**
→ API key is invalid. Double-check at https://open.sam.gov/

**"No opportunities found"**
→ Normal some weeks. SAM.gov may have gaps or your keywords aren't matching current RFPs.

**Telegram not receiving**
→ Check that your Telegram account is allowlisted in `channels.telegram.allowFrom` in the config

## Next Steps

1. **Test the skill** manually first (see Step 3)
2. **Confirm Telegram delivery** works
3. **Set up the cron job** (see Step 4)
4. **Monitor** the first few runs
5. **Expand** to state portals (PA, NJ, DE) later
