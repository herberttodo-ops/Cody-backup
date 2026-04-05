# Kelly - Customer Support Agent

A multi-tenant AI customer support agent named **Kelly** that handles inquiries for multiple businesses with business-specific knowledge, response templates, and escalation protocols.

## Supported Businesses

- **Cozie Homes** - Short-term rental property management
- **OptiRFP** - RFP automation platform
- **TLC Rescue** - Dog rescue fundraising
- **Rival Productions** - Video production services

## Capabilities

1. **Multi-Tenant Support** - Routes inquiries to correct business context
2. **Knowledge Base Integration** - Access to business-specific FAQs and policies
3. **Issue Triage** - Classifies and prioritizes support requests
4. **Response Generation** - Drafts professional, contextual responses
5. **Escalation Handling** - Identifies when human intervention is needed
6. **Handoff Logging** - Tracks all interactions for review

## Usage

```
Spawn customer support subagent for: [Business Name]
Customer inquiry: [Message or context]
```

## Architecture

```
Customer Inquiry
       ↓
[Business Detection] → Identify which business
       ↓
[Context Loading] → Load business config + knowledge
       ↓
[Issue Triage] → Classify urgency + category
       ↓
[Response Generation] → Draft response
       ↓
[Escalation Check] → Auto-escalate if needed
       ↓
[Response Output] → Deliver to customer
```

## Response Categories

- **General Inquiry** - Standard questions, FAQ responses
- **Technical Issue** - Platform/technical problems
- **Billing** - Payments, refunds, invoicing
- **Urgent** - Time-sensitive or critical issues
- **Escalation Required** - Needs human review

## Escalation Triggers

- Angry/upset customer tone
- Legal/compliance issues
- Refund requests over $500
- Data security concerns
- Complex technical issues
- VIP/Priority customers
