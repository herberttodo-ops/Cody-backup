# Kelly - Customer Support Quick Start Guide

## How to Use

### Option 1: Spawn for Specific Business

```
sessions_spawn with:
- runtime: "subagent"
- task: "Handle customer support inquiry for [BUSINESS]"
- mode: "run" (one-shot) or "session" (persistent)
```

### Option 2: Full Context Spawn

```
sessions_spawn:
  runtime: "subagent"
  task: |
    BUSINESS: [cozie_homes|optirfp|tlc_rescue|rival_productions]
    CUSTOMER_MESSAGE: |
      [Paste customer inquiry here]
    CUSTOMER_INFO:
      name: [Customer Name]
      email: [email@example.com]
      tier: [vip|standard|new]
    
    Please:
    1. Load business knowledge from /home/herby/.openclaw/workspace/skills/customer-support/knowledge/[business]/
    2. Triage the inquiry (category, urgency, sentiment)
    3. Check if escalation is needed
    4. Draft a professional response
    5. Output JSON format with all fields
  mode: "run"
```

## Response Template Format

The subagent should output:

```json
{
  "business": "cozie_homes",
  "customer": {
    "name": "Customer Name",
    "email": "customer@example.com"
  },
  "inquiry_summary": "Brief summary of what they asked",
  "triage": {
    "category": "booking|technical|billing|general|urgent",
    "urgency": "low|medium|high|critical",
    "sentiment": "positive|neutral|negative|angry"
  },
  "escalation": {
    "required": false,
    "reason": null,
    "contact": null
  },
  "response_draft": "Full response text to send to customer",
  "suggested_actions": [
    "Check reservation system",
    "Process refund if approved"
  ],
  "follow_up_needed": false,
  "follow_up_date": null,
  "internal_notes": "Notes for human review"
}
```

## Example Usage

### Example 1: Cozie Homes Booking Question

```javascript
sessions_spawn({
  runtime: "subagent",
  task: `
BUSINESS: cozie_homes
CUSTOMER_MESSAGE: "Hi, I'm arriving at midnight on Friday. Will I be able to check in that late? Also, is there WiFi?"
CUSTOMER_INFO:
  name: "Sarah Johnson"
  email: "sarah.j@email.com"
  booking_id: "CH-2024-01234"

Please handle this inquiry following the customer support agent specification.
`,
  mode: "run"
})
```

### Example 2: OptiRFP Technical Issue

```javascript
sessions_spawn({
  runtime: "subagent",
  task: `
BUSINESS: optirfp
CUSTOMER_MESSAGE: "I uploaded my RFP document but the AI isn't generating any responses. It just spins forever. This is urgent - my deadline is tomorrow!"
CUSTOMER_INFO:
  name: "Michael Chen"
  email: "mchen@company.com"
  plan: "Professional"
  account_age: "3 months"

Please triage and respond.
`,
  mode: "run"
})
```

### Example 3: TLC Rescue Donation

```javascript
sessions_spawn({
  runtime: "subagent",
  task: `
BUSINESS: tlc_rescue
CUSTOMER_MESSAGE: "I want to donate $2,000 in memory of my dog who recently passed. Can you tell me how to do this and if I can specify how it's used?"
CUSTOMER_INFO:
  name: "Robert Williams"
  email: "rwilliams@email.com"

This is a large donation - handle with care and escalate to fundraising team.
`,
  mode: "run"
})
```

## Business Detection Rules

If business is not specified, detect from keywords:

| Business | Keywords |
|----------|----------|
| cozie_homes | booking, check-in, property, rental, cabin, stay, airbnb, poconos |
| optirfp | RFP, proposal, platform, login, API, subscription, billing, software |
| tlc_rescue | donation, volunteer, adopt, dog, rescue, fundraiser, bingo, foster |
| rival_productions | video, production, filming, edit, webinar, quote, project |

## Tone Guidelines by Business

### Cozie Homes
- Warm and welcoming
- Use hospitality language
- Be helpful and accommodating
- Example: "We'd love to host you!" "Let me help make your stay perfect."

### OptiRFP
- Professional and technical
- Solution-focused
- Clear and concise
- Example: "I'll help resolve this issue." "Here's the solution..."

### TLC Rescue
- Heartfelt and compassionate
- Mission-driven
- Express gratitude
- Example: "Thank you for caring about our dogs!" "Your support means the world."

### Rival Productions
- Creative and professional
- Detail-oriented
- Enthusiastic about projects
- Example: "Excited to bring your vision to life!" "Let's create something amazing."

## Escalation Decision Tree

```
Customer Message Received
        ↓
┌─────────────────┐
│ Check for angry │ → YES → Escalate (Priority)
│ tone, all caps, │
│ threatening     │
└─────────────────┘
        ↓ NO
┌─────────────────┐
│ Check for legal │ → YES → Escalate (Immediate)
│ words (lawsuit, │
│ lawyer, sue)    │
└─────────────────┘
        ↓ NO
┌─────────────────┐
│ Check for refund│ → YES → Escalate (Priority)
│ amount > $500   │
└─────────────────┘
        ↓ NO
┌─────────────────┐
│ Check for safety│ → YES → Escalate (Immediate)
│ or security     │
└─────────────────┘
        ↓ NO
┌─────────────────┐
│ Handle normally │
└─────────────────┘
```

## Files Reference

| File | Purpose |
|------|---------|
| `SKILL.md` | Overview and architecture |
| `AGENT_SPEC.md` | Detailed agent behavior spec |
| `agent-config.json` | Business configurations |
| `knowledge/[business]/FAQ.md` | Business-specific FAQs |
| `templates/response_templates.md` | Response templates (optional) |

## Storage

Support interactions should be logged to:
`memory/customer-support/YYYY-MM-DD/[business]_[timestamp].json`

For tracking and review by human team members.
