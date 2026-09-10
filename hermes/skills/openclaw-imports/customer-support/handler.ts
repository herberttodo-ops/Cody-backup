/**
 * Kelly - Customer Support Agent Handler
 * 
 * Usage Example:
 * 
 * const result = await handleCustomerSupport({
 *   business: 'cozie_homes',
 *   customerMessage: 'Hi, can I check in late?',
 *   customerInfo: { name: 'John', email: 'john@example.com' }
 * });
 * 
 * Returns: JSON response with draft response, triage info, escalation flags
 */

export async function handleCustomerSupport({
  business,
  customerMessage,
  customerInfo = {},
  context = {}
}) {
  const task = buildSupportTask({
    business,
    customerMessage,
    customerInfo,
    context
  });

  // This would be called via sessions_spawn in actual implementation
  // For now, returns the task specification
  return {
    runtime: "subagent",
    task,
    mode: "run",
    expectedOutput: "json"
  };
}

function buildSupportTask({ business, customerMessage, customerInfo, context }) {
  return `
# CUSTOMER SUPPORT TASK

## Business Context
Business: ${business}

## Customer Information
${Object.entries(customerInfo).map(([k, v]) => `- ${k}: ${v}`).join('\n')}

## Customer Message
"""
${customerMessage}
"""

## Additional Context
${JSON.stringify(context, null, 2)}

## Instructions

You are a customer support specialist for ${business}. 

1. **Load Knowledge Base**
   Read: /home/herby/.openclaw/workspace/skills/customer-support/knowledge/${business}/FAQ.md

2. **Analyze the Inquiry**
   - Summarize what they're asking
   - Identify category (booking/technical/billing/general/urgent)
   - Assess urgency (low/medium/high/critical)
   - Gauge sentiment (positive/neutral/negative/angry)

3. **Check Escalation Rules**
   - Immediate: legal threats, safety issues, data breach
   - Priority: refunds >$500, VIP customers, angry tone
   - Standard: complex issues, custom pricing

4. **Draft Response**
   - Match business tone (see agent-config.json)
   - Address all their questions
   - Be helpful and professional
   - Include next steps if applicable

5. **Output JSON**
   Return ONLY valid JSON in this format:
   
   {
     "business": "${business}",
     "customer": {
       "name": "${customerInfo.name || 'Unknown'}",
       "email": "${customerInfo.email || ''}"
     },
     "inquiry_summary": "Brief summary",
     "triage": {
       "category": "category_name",
       "urgency": "low|medium|high|critical",
       "sentiment": "positive|neutral|negative|angry"
     },
     "escalation": {
       "required": false,
       "reason": null,
       "contact": null
     },
     "response_draft": "Full response text",
     "suggested_actions": ["action1", "action2"],
     "follow_up_needed": false,
     "follow_up_date": null,
     "internal_notes": "Notes for human review"
   }

## Response Templates
Reference these for tone and structure:
/home/herby/.openclaw/workspace/skills/customer-support/templates/response_templates.md
`;
}

// Business detection helper
export function detectBusiness(message) {
  const message_lower = message.toLowerCase();
  
  const keywords = {
    cozie_homes: ['booking', 'check-in', 'property', 'rental', 'cabin', 'airbnb', 'poconos', 'stay', 'reservation'],
    optirfp: ['rfp', 'proposal', 'platform', 'login', 'api', 'subscription', 'billing', 'software', 'account'],
    tlc_rescue: ['donation', 'volunteer', 'adopt', 'dog', 'rescue', 'fundraiser', 'bingo', 'foster', 'donate'],
    rival_productions: ['video', 'production', 'filming', 'edit', 'webinar', 'quote', 'project', 'shoot']
  };
  
  const scores = {};
  
  for (const [business, words] of Object.entries(keywords)) {
    scores[business] = words.filter(word => message_lower.includes(word)).length;
  }
  
  const detected = Object.entries(scores)
    .sort((a, b) => b[1] - a[1])
    .filter(([_, score]) => score > 0)[0];
  
  return detected ? detected[0] : null;
}

// Main entry point for handling incoming messages
export async function processSupportInquiry(message, customerInfo = {}) {
  // Detect business if not specified
  const business = customerInfo.business || detectBusiness(message);
  
  if (!business) {
    return {
      error: "Could not detect business. Please specify: cozie_homes, optirfp, tlc_rescue, or rival_productions"
    };
  }
  
  return handleCustomerSupport({
    business,
    customerMessage: message,
    customerInfo
  });
}

// Example usage:
// const result = await processSupportInquiry(
//   "Hi, I need to cancel my booking for next week",
//   { name: "Jane Doe", email: "jane@example.com" }
// );
