# Harvey Continuation Checklist

Quick reference for picking up Harvey setup from a partial state.

## Check Current Status

```bash
cd ~/.openclaw/workspace/harvey  # or your install path
source .venv/bin/activate
harvey status
```

## Verify Config State

| Check | Command/Location | Done When |
|-------|------------------|-----------|
| Product trained | `ls skills/product_knowledge.md` | File exists with content |
| Booking URL set | `grep booking_url harvey.local.yaml` | Shows actual URL, not `''` |
| Postal address real | `grep postal_address harvey.local.yaml` | Real street address, not placeholder |
| Sending domain correct | Check `channels.email.provider` and persona email | Secondary domain, NOT primary business domain |

## API Key Setup (Exact Steps)

### Gmail OAuth
1. https://console.cloud.google.com → New project "Harvey Mail"
2. APIs & Services → Enable "Gmail API"
3. Credentials → Create OAuth client ID → Application type: Desktop app
4. Copy Client ID and Secret to `.env`:
   ```
   GMAIL_CLIENT_ID=***.apps.googleusercontent.com
   GMAIL_CLIENT_SECRET=***
   ```
5. Run authorization:
   ```bash
   harvey gmail auth
   ```

### Reoon Email Verification (600 free/month)
1. https://reoon.com/email-verifier → Sign up
2. Account → API Key → Copy
3. `.env`:
   ```
   REOON_API_KEY=***
   ```

### Hunter.io Pattern Lookup (50 free/month)
1. https://hunter.io → Sign up
2. API page → Copy key
3. `.env`:
   ```
   HUNTER_API_KEY=***
   HUNTER_MONTHLY_SEARCHES=25
   ```

## Domain Red Flag Check

**If `harvey.local.yaml` shows:**
```yaml
persona:
  email: harvey@PRIMARY_DOMAIN.com  # e.g., harvey@lotsignal.ai
channels:
  email:
    provider: gmail
```

**STOP.** This will destroy your primary domain's deliverability. Fix:
1. Register secondary domain (e.g., `lotsignalmail.com`)
2. Set up Workspace on that domain
3. Update `persona.email` to mailbox on secondary domain
4. Re-run warmup

## Ready to Launch Checklist

- [ ] Gmail OAuth authorized (`harvey gmail auth` completed)
- [ ] Reoon API key in `.env`
- [ ] Hunter API key in `.env`
- [ ] Sending domain is secondary (not primary business domain)
- [ ] Booking URL is real calendar link
- [ ] Postal address is CAN-SPAM compliant
- [ ] Warmup period complete or TrulyInbox connected
- [ ] `harvey status` shows pipeline ready

## Commands Reference

```bash
harvey discover      # Find prospects (requires confirmed signals)
harvey dashboard     # Open monitoring UI at localhost:5555
harvey run           # Start autonomous loop
harvey outbox        # Review emails awaiting approval
harvey signals --confirm free   # Confirm free prospecting criteria
```
