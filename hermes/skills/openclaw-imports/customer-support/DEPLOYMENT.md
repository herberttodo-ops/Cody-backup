# Kelly - Customer Support Deployment Guide

## Pre-Deployment Checklist

- [ ] All business knowledge bases created and reviewed
- [ ] Escalation contacts verified and active
- [ ] Response templates customized for each business
- [ ] Test inquiries run for each business
- [ ] Logging directory created: `memory/customer-support/`
- [ ] Human review process documented
- [ ] Cost estimates approved

## Deployment Steps

### 1. File Verification

Verify all files are in place:

```bash
cd /home/herby/.openclaw/workspace/skills/customer-support

# Check structure
ls -la
ls -la knowledge/*/FAQ.md
ls -la templates/

# Verify configs
cat agent-config.json | jq .
```

### 2. Test Each Business

Run test inquiries for each business:

```javascript
// Cozie Homes
sessions_spawn({
  runtime: "subagent",
  task: `BUSINESS: cozie_homes
CUSTOMER_MESSAGE: "Can I bring my dog?"
CUSTOMER_INFO: { name: "Test", email: "test@test.com" }`,
  mode: "run"
})

// OptiRFP
sessions_spawn({
  runtime: "subagent",
  task: `BUSINESS: optirfp
CUSTOMER_MESSAGE: "How do I reset my password?"
CUSTOMER_INFO: { name: "Test", email: "test@test.com" }`,
  mode: "run"
})

// TLC Rescue
sessions_spawn({
  runtime: "subagent",
  task: `BUSINESS: tlc_rescue
CUSTOMER_MESSAGE: "How do I volunteer?"
CUSTOMER_INFO: { name: "Test", email: "test@test.com" }`,
  mode: "run"
})

// Rival Productions
sessions_spawn({
  runtime: "subagent",
  task: `BUSINESS: rival_productions
CUSTOMER_MESSAGE: "I need a quote for a 5-minute video"
CUSTOMER_INFO: { name: "Test", email: "test@test.com" }`,
  mode: "run"
})
```

### 3. Integration Options

#### Option A: Email-Based Support

Set up email monitoring that spawns the agent:

```javascript
// Cron job runs every 5 minutes
cron.add({
  name: "support-email-check",
  schedule: { kind: "every", everyMs: 300000 },
  payload: {
    kind: "agentTurn",
    message: "Check support@coziehomes.com, support@optirfp.ai, etc. for new emails. For each email, spawn customer support subagent with the email content."
  },
  sessionTarget: "isolated"
})
```

#### Option B: Webhook Integration

For platforms with webhooks (Zendesk, Intercom, etc.):

```javascript
// Webhook handler
app.post('/support-webhook', async (req, res) => {
  const { message, customer, business } = req.body;
  
  const result = await sessions_spawn({
    runtime: "subagent",
    task: buildSupportTask({ business, customerMessage: message, customerInfo: customer }),
    mode: "run"
  });
  
  // Send response back to platform
  res.json({ response: result.response_draft });
});
```

#### Option C: Manual Spawn (Current)

Human reviews inquiry, spawns agent, reviews response before sending.

Best for: Initial rollout, quality assurance period

### 4. Escalation Setup

Ensure escalation contacts are configured:

| Business | Contact | Method |
|----------|---------|--------|
| Cozie Homes | andrew@coziehomes.com | Email |
| OptiRFP | herberttodo@gmail.com | Email |
| TLC Rescue | fundraising@tlcrescue.org | Email |
| Rival Productions | andrew@rivalproductions.com | Email |

Consider adding:
- SMS alerts for critical escalations
- Slack notifications
- Dashboard alerts

### 5. Logging Setup

Create logging directory:

```bash
mkdir -p /home/herby/.openclaw/workspace/memory/customer-support/$(date +%Y-%m-%d)
```

Log format:
```json
{
  "timestamp": "2026-02-28T12:00:00Z",
  "business": "cozie_homes",
  "customer": "customer@example.com",
  "inquiry_summary": "Late check-in question",
  "triage": { "category": "booking", "urgency": "low", "sentiment": "neutral" },
  "escalation_required": false,
  "response_sent": true,
  "response_text": "...",
  "handled_by": "subagent",
  "reviewed_by": null
}
```

### 6. Monitoring & Alerts

Set up health checks:

```javascript
// Daily report cron
cron.add({
  name: "support-daily-summary",
  schedule: { kind: "cron", expr: "0 9 * * *", tz: "America/New_York" },
  payload: {
    kind: "agentTurn",
    message: "Generate daily support summary: total inquiries, escalations, average response time, any issues."
  },
  sessionTarget: "isolated",
  delivery: { mode: "announce", channel: "telegram" }
})
```

### 7. Gradual Rollout

**Phase 1: Shadow Mode (Week 1-2)**
- Agent drafts responses
- Human reviews and edits before sending
- No customer-facing automation

**Phase 2: Limited Auto-Response (Week 3-4)**
- Auto-respond to FAQ questions only
- All other inquiries human-reviewed
- Monitor quality metrics

**Phase 3: Full Automation (Week 5+)**
- Auto-respond to all non-escalated inquiries
- Escalations still go to humans
- Continuous monitoring

## Post-Deployment

### Daily
- [ ] Review escalated inquiries
- [ ] Check error logs
- [ ] Monitor response quality

### Weekly
- [ ] Review metrics (volume, escalation rate, sentiment)
- [ ] Tune response templates based on feedback
- [ ] Update knowledge bases with new FAQs

### Monthly
- [ ] Full quality audit (sample 10% of responses)
- [ ] Cost analysis
- [ ] Add new businesses if needed

## Troubleshooting

### Issue: Agent not loading knowledge base
**Check**: File path is correct
**Fix**: Verify path in task: `/home/herby/.openclaw/workspace/skills/customer-support/knowledge/[business]/FAQ.md`

### Issue: Responses not matching business tone
**Check**: agent-config.json tone settings
**Fix**: Update response_tone in config, regenerate templates

### Issue: Missing escalations
**Check**: Escalation rules in AGENT_SPEC.md
**Fix**: Verify sentiment detection is working, adjust thresholds

### Issue: High costs
**Check**: Number of inquiries, model being used
**Fix**: Consider caching common responses, using lighter model for simple queries

## Security Checklist

- [ ] Customer data never logged to external systems
- [ ] API keys secured in config only
- [ ] No PII in response templates
- [ ] Escalation contacts verified
- [ ] Access controls on memory/customer-support/ directory

## Support & Maintenance

**Owner**: [Your name]
**Last Review**: [Date]
**Next Review**: [Date + 30 days]

For updates or issues:
1. Check README.md for usage
2. Review AGENT_SPEC.md for behavior
3. Update knowledge bases as needed
4. Test changes before deploying

---

**Deployment Date**: ___________
**Deployed By**: ___________
