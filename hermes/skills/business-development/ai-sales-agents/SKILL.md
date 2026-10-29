---
name: ai-sales-agents
description: "Set up Harvey AI sales agent for cold email automation."
version: 1.0.0
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [sales, cold-email, outbound, prospecting, automation, claude-code]
    related_skills: [claude-code]
---

# AI Sales Agents — Setup Guide

Autonomous sales agents that find prospects, write personalized cold emails, handle replies, and book meetings. These tools typically embed Claude Code as their AI backend and run locally with subscription-based pricing (no per-token API billing).

## Supported Agents

### Harvey (https://github.com/ethanplusai/harvey)

The reference implementation for autonomous sales agents.

**What Harvey Does:**
- Crawls company websites to find prospects
- Writes personalized cold email sequences using Claude Code
- Sends campaigns via Gmail/Workspace, SMTP, or Instantly
- Handles replies and works toward meetings
- Web dashboard for monitoring and approvals
- SQLite database for prospect tracking

**Prerequisites:**
- Python 3.11+
- Claude Pro or Max subscription
- Dedicated secondary domain for sending (not your main domain)
- OPTIONAL: Email verification service (Reoon, ZeroBounce, Hunter)

## Installation Pattern

```bash
git clone <repo-url>
cd <agent-directory>
python3.11 -m venv .venv && source .venv/bin/activate
pip install -e .
python -m playwright install chromium
```

Note: Playwright browser automation is typically needed for LinkedIn or JS-heavy sites.

## Configuration Workflow

All AI sales agents follow a similar setup pattern:

### 1. Environment Configuration
Copy `.env.example` to `.env` and configure at minimum:
- **Email provider** (required): Gmail OAuth, SMTP/IMAP, or Instantly API
- **Email verification** (strongly recommended): Reoon (600 free/mo), ZeroBounce (100 free/mo)
- **Optional**: LinkedIn credentials, Cloudflare for JS crawling, etc.

### 2. Product Training
```bash
harvey train https://your-company.com
```

Training typically runs a Claude-powered 6-step analysis:
1. **Crawl** — scrapes product website
2. **Analyze** — extracts product info
3. **ICP** — identifies ideal customer profile
4. **Competitors** — finds and analyzes competitors
5. **Objections** — generates objection responses
6. **Config** — writes `harvey.local.yaml`, `skills/product_knowledge.md`

**Pitfall:** Training makes Claude calls sequentially — it takes 30-120 seconds and may timeout if impatient. Run with generous timeout or in background.

### 3. Review Generated Config
Always review `harvey.local.yaml` or similar agent config:
- **Persona name/email** — default is often generic (e.g., harvey@yourdomain)
- **Tone** — adjust to match your brand (e.g., "Blunt, operator-savvy, plainspoken")
- **ICP titles** — verify titles match your actual targets
- **Pricing** — review for accuracy
- **Objection responses** — customize as needed

### 4. Set Prospecting Signals
```bash
harvey signals --confirm free
```

Signals = criteria the agent uses to identify good prospects. Review and confirm before running discovery.

### 5. Discovery & Run
```bash
harvey discover        # Find prospects matching ICP
harvey dashboard       # Open monitoring UI (typically localhost:5555)
harvey run             # Start autonomous loop
```

## Email Provider Setup

### Gmail/Workspace [Recommended for <50/day]
1. Google Cloud Console → new project → enable Gmail API
2. Credentials → OAuth client ID → Desktop app
3. Paste client ID/secret into `.env`
4. Run `harvey gmail auth` for browser login
5. Set `channels.email.provider: gmail` in config

### SMTP/IMAP [Any provider]
- AgentMail, Fastmail, Workspace app password
- Set `channels.email.provider: smtp` in config

### Microsoft 365
- Azure App registration with redirect URI
- Run `harvey microsoft auth` then `harvey microsoft test`

### Instantly [Legacy cold email platform]
- Requires Instantly Growth plan+
- Set `channels.email.provider: instantly` in config

## Email Verification

**Without verification:** All addresses marked "guess" — never sent

| Service | Free Tier | Best For |
|---------|-----------|----------|
| Reoon | 600/month | Best free tier, good catch-all flagging |
| ZeroBounce | 100/month | M365/Workspace catch-all domains |
| Hunter.io | 50/month + 25 searches | Domain pattern lookup (used first to reduce guesses) |

## Domain Strategy

**CRITICAL:** Use a DEDICATED SECONDARY DOMAIN, never your main domain.

**Good:** harvey@lotsignal.ai (if lotsignal.ai is separate from main site)
**Bad:** sales@main-company.com (main domain reputation at risk)

For cold email deliverability, you need:
- Dedicated domain (never use for transactional/business email)
- SPF, DKIM, DMARC configured
- 14+ days warmup period via TrulyInbox or similar

## Daily Operations

### Monitor Dashboard
```bash
harvey dashboard
```
Opens private link to monitoring UI (e.g., `http://127.0.0.1:5555/#token=...`)

**Key Tabs:**
- **Today** — pending decisions, pipeline status
- **Signals** — confirmed prospecting criteria
- **Companies** — discovered prospects
- **Contacts** — email addresses found
- **Outbox** — emails awaiting approval
- **Conversations** — active reply threads

### Check Warmup Status
```bash
harvey warmup
harvey trulyinbox connect  # If using TrulyInbox for warmup
```

Don't start sending until inbox rate >90% and warmup period complete.

### Usage Quotas
```bash
harvey usage  # Shows Claude/Codex quota consumption
```

Agents budget themselves: read subscription quota and throttle to leave headroom.

## Troubleshooting

### "Nothing sends"
- Check `.env` — did you add email provider credentials?
- Check email verification — addresses marked "guess" never send
- Check warmup status — new domains need warmup period
- Check outbox — review `harvey outbox` for pending approvals

### "Low deliverability"
- Verify SPF/DKIM/DMARC on sending domain
- Check warmup completion (TrulyInbox inbox rate >90%)
- Review bounce rates in dashboard
- Send only to "verified" addresses, not "catch-all" or "guess"

### "Training fails/times out"
- Training uses Claude Code — ensure `claude auth status` shows logged in
- Cloudflare credentials needed for JS-rendered sites
- Timeout is normal for 6-step analysis — use background process

### Database Locks
Harvey uses SQLite. If interrupted during writes:
```bash
# Kill stale Python processes
tmux ls  # or pgrep -f harvey
# Delete lock file if it exists
rm -f data/harvey.db-journal
```

## References

- [Harvey Repository](https://github.com/ethanplusai/harvey) — The reference implementation
- [Harvey Docs](https://github.com/ethanplusai/harvey/tree/main/docs) — Provider-specific setups

## Pitfalls

1. **Never use your main domain** — dedicate a secondary domain for cold email
2. **Don't skip email verification** — sending to bad addresses destroys sender reputation
3. **Don't rush warmup** — 14 days minimum for new domains
4. **Review generated configs** — tone, ICP, pricing may need refinement
5. **Approval gates are on by default** — nothing sends without human approval (good!)
6. **Training times out** — it's making Claude calls; run with generous timeout or background
