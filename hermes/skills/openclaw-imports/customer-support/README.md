# Kelly - Customer Support Agent

A production-ready, multi-tenant AI customer support system named **Kelly** for handling inquiries across multiple businesses.

## Overview

This subagent can handle customer support for:
- **Cozie Homes** - Short-term rentals (Poconos)
- **OptiRFP** - RFP automation SaaS platform
- **TLC Rescue** - Dog rescue nonprofit
- **Rival Productions** - Video production services

## Quick Start

### 1. Spawn for a Specific Inquiry

```javascript
sessions_spawn({
  runtime: "subagent",
  task: `
BUSINESS: cozie_homes
CUSTOMER_MESSAGE: "Can I check in late on Friday? Also, is there WiFi?"
CUSTOMER_INFO:
  name: "Sarah Johnson"
  email: "sarah@email.com"
  booking_id: "CH-2024-01234"

Please handle this inquiry following the customer support specification.
Load knowledge from: /home/herby/.openclaw/workspace/skills/customer-support/knowledge/cozie_homes/
`,
  mode: "run"
})
```

### 2. Auto-Detect Business

```javascript
const message = "I want to donate $500 to help the dogs";
const detected = detectBusiness(message);
// Returns: "tlc_rescue"
```

### 3. Full Handoff Example

```javascript
// Incoming support request
const inquiry = {
  message: "Your platform is broken! I can't log in and my deadline is tomorrow!",
  from: "angry.customer@company.com",
  name: "Frustrated User"
};

// Spawn support agent
const result = await sessions_spawn({
  runtime: "subagent", 
  task: buildSupportTask({
    business: "optirfp",
    customerMessage: inquiry.message,
    customerInfo: {
      name: inquiry.name,
      email: inquiry.from,
      plan: "Professional"
    }
  }),
  mode: "run"
});

// Result will include:
// - response_draft (ready to send)
// - escalation flag (likely true for angry tone)
// - suggested actions
// - internal notes
```

## File Structure

```
customer-support/
├── SKILL.md                    # Overview and architecture
├── AGENT_SPEC.md               # Detailed agent behavior
├── QUICKSTART.md              # Usage guide with examples
├── agent-config.json          # Business configurations
├── handler.ts                 # Implementation reference
├── knowledge/
│   ├── cozie_homes/
│   │   └── FAQ.md
│   ├── optirfp/
│   │   └── FAQ.md
│   ├── tlc_rescue/
│   │   └── FAQ.md
│   └── rival_productions/
│       └── FAQ.md
└── templates/
    └── response_templates.md  # Response templates by business
```

## Features

### Multi-Tenant Support
- Automatic business detection from keywords
- Business-specific knowledge bases
- Custom tone/voice per business
- Separate escalation contacts

### Issue Triage
- **Categories**: Booking, Technical, Billing, General, Urgent
- **Urgency Levels**: Low, Medium, High, Critical
- **Sentiment Analysis**: Positive, Neutral, Negative, Angry

### Escalation Detection
Automatically escalates when:
- Angry/upset customer tone
- Legal threats or compliance issues
- Refund requests > $500
- Data security concerns
- VIP customer flag
- Safety emergencies

### Response Generation
- Drafts professional, contextual responses
- Matches business tone and voice
- Includes relevant links/resources
- Provides clear next steps

## Business Configurations

| Business | Tone | Auto-Response | Escalation Contact |
|----------|------|---------------|-------------------|
| Cozie Homes | Warm, hospitable | Yes | andrew@coziehomes.com |
| OptiRFP | Professional, technical | Yes | herberttodo@gmail.com |
| TLC Rescue | Heartfelt, mission-driven | Yes | fundraising@tlcrescue.org |
| Rival Productions | Creative, professional | No | andrew@rivalproductions.com |

## Response Format

All responses follow this JSON structure:

```json
{
  "business": "cozie_homes",
  "customer": {
    "name": "Customer Name",
    "email": "customer@example.com"
  },
  "inquiry_summary": "Brief summary of inquiry",
  "triage": {
    "category": "booking",
    "urgency": "medium",
    "sentiment": "neutral"
  },
  "escalation": {
    "required": false,
    "reason": null,
    "contact": null
  },
  "response_draft": "Full response to send",
  "suggested_actions": ["Check reservation", "Send confirmation"],
  "follow_up_needed": false,
  "follow_up_date": null,
  "internal_notes": "Notes for human review"
}
```

## Escalation Rules

### Immediate Escalation
- Legal threats (lawsuit, lawyer)
- Safety/security issues
- Data breach reports
- Platform outages

### Priority Escalation  
- Refund requests > $500
- VIP/Priority customers
- Angry/upset tone
- Negative review threats

### Standard Escalation
- Complex technical issues
- Custom pricing requests
- Contract negotiations
- Feature development requests

## Adding a New Business

1. Create directory: `knowledge/[business_id]/`
2. Add FAQ.md with common questions
3. Update `agent-config.json`:
   ```json
   "new_business": {
     "name": "Business Name",
     "industry": "industry_type",
     "priority": "high|medium|low",
     "auto_response": true|false,
     "escalation_contacts": ["email@example.com"],
     "categories": ["category1", "category2"]
   }
   ```
4. Add tone to `response_tone` section
5. Add keywords to `detectBusiness()` function

## Logging

All support interactions should be logged to:
```
memory/customer-support/YYYY-MM-DD/[business]_[timestamp].json
```

This enables:
- Quality review by human team
- Pattern analysis
- Performance tracking
- Training data for improvements

## Testing

### Test Cozie Homes Inquiry
```javascript
sessions_spawn({
  runtime: "subagent",
  task: `BUSINESS: cozie_homes
CUSTOMER_MESSAGE: "Is there a fireplace at the Poconos cabin? We're celebrating our anniversary!"
CUSTOMER_INFO:
  name: "Mike and Lisa"
  email: "mike@example.com"`,
  mode: "run"
})
```

### Test OptiRFP Technical Issue
```javascript
sessions_spawn({
  runtime: "subagent", 
  task: `BUSINESS: optirfp
CUSTOMER_MESSAGE: "The AI keeps giving me errors when I upload my document. This is URGENT!"
CUSTOMER_INFO:
  name: "CTO Frustrated"
  email: "cto@bigcompany.com"
  plan: "Enterprise"`,
  mode: "run"
})
```

### Test TLC Rescue Donation
```javascript
sessions_spawn({
  runtime: "subagent",
  task: `BUSINESS: tlc_rescue
CUSTOMER_MESSAGE: "I'd like to donate $1,500 in memory of my childhood dog"
CUSTOMER_INFO:
  name: "Robert Williams"
  email: "rwilliams@example.com"`,
  mode: "run"
})
```

## Integration Options

### Option 1: Direct Spawn (One-shot)
Best for: Individual inquiries
- Spawn agent per message
- Gets response immediately
- Agent exits after response

### Option 2: Persistent Session
Best for: Ongoing conversation threads
- Spawn with `mode: "session"`
- Agent maintains context
- Can handle back-and-forth

### Option 3: Cron/Automated
Best for: Monitoring support channels
- Cron job checks email/support channels
- Spawns agent for each new inquiry
- Logs all responses

## Quality Assurance

### Human Review Triggers
- All escalated inquiries
- Random sample (10%) of non-escalated
- Negative sentiment responses
- New business first 30 days

### Metrics to Track
- Response time
- Escalation rate
- Customer satisfaction
- Resolution rate
- Tone appropriateness

## Cost Estimation

Per inquiry cost: ~$0.01-0.03
- Model: Kimi k2.5 (default)
- Includes: Analysis + Response generation
- Knowledge base: Local file read (no API cost)

Monthly cost estimate:
- 100 inquiries/month: ~$2-3
- 500 inquiries/month: ~$10-15
- 1000 inquiries/month: ~$20-30

## Security & Privacy

- Customer data never leaves local environment
- No training on customer conversations
- Logs stored locally only
- API keys secured in config

## Support

For questions or issues:
- Check `AGENT_SPEC.md` for behavior details
- Review `knowledge/[business]/FAQ.md` for business info
- See `templates/response_templates.md` for examples

---

**Status**: Ready for deployment
**Last Updated**: 2026-02-28
**Version**: 1.0.0
