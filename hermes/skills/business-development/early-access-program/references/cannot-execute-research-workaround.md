# When the Agent Cannot Execute Target Research Directly

## Problem

LinkedIn Sales Navigator, ZoomInfo, Apollo, and similar research tools require:
- User account credentials (which the agent should not have)
- API keys that may not be configured
- Access to paid tools the user owns but the agent cannot access

## Solution: Hybrid Research Pattern

### What the Agent CAN Do

1. **Build the Research Framework**
   - Create structured target lists with placeholders
   - Define search queries and filters
   - Set up scoring criteria
   - Write message templates with variable insertion

2. **Prepare Execution Templates**
   - Provide exact LinkedIn search queries
   - List specific search filters to apply
   - Create copy-paste message sequences
   - Build tracking spreadsheets

3. **Create Support Dashboards** (Vercel/Notion/etc)
   - Build UI for tracking outreach status
   - Embed message templates with one-click copy
   - Show research instructions
   - Track conversion metrics

### What the User MUST Do

1. **Execute the Research**
   - Log into LinkedIn Sales Navigator
   - Run the search queries provided by agent
   - Make judgment calls on which contacts fit ICP
   - Fill in names/emails/LinkedIn URLs

2. **Personalize at Point of Send**
   - Copy message templates from dashboard
   - Replace `[Name]` with actual first name
   - Reference specific pain signals found in research
   - Send via their own LinkedIn account

### Communication Pattern

**When user asks: "Research targets for me"**

Agent should respond with:
```
I can prepare everything you need, but I'll need you to execute 
the LinkedIn research using your Sales Navigator account.

Here's what I'll create:
1. Target list template with search queries
2. 4-message sequences for each segment
3. Research criteria checklist
4. [Optional] Vercel dashboard to track everything

Then you'll:
1. Run the searches I specify
2. Fill in the names I found
3. Copy the messages I wrote
4. Track in the dashboard I built

Ready to proceed?
```

## Tools for Bridging the Gap

### 1. Vercel Dashboard (Used in LotSignal Project)
- **Pros:** Always available, mobile-friendly, free hosting
- **Cons:** Requires deployment step
- **Best for:** Ongoing tracking, multiple team members

### 2. Notion Database
- **Pros:** Easy to update, collaborative, built-in templates
- **Cons:** Less structured than custom UI
- **Best for:** Simple tracking, non-technical users

### 3. Google Sheets + Apps Script
- **Pros:** Familiar interface, easy sharing
- **Cons:** Limited interactivity
- **Best for:** Quick setups, temporary projects

### 4. Airtable
- **Pros:** Database + UI in one, automations
- **Cons:** Paid for advanced features
- **Best for:** Complex workflows, integrations

## Message Template Strategy

When writing messages for user to send:

**DO:**
- Use `[FirstName]` placeholders for personalization
- Write market-specific hooks (heat in Phoenix, competition in Atlanta)
- Include fallback text if research doesn't find a name
- Provide 4-message sequence so user can progress conversation

**DON'T:**
- Assume agent will know the contact's name
- Write overly specific references that require deep research
- Create single messages (need full sequence)

**Example Template:**
```
Hi [FirstName],

Saw you run [Company] in [Location]. Quick question: 
with [market-specific challenge], how do you decide which 
[problem area] gets priority?

Not selling - just researching how [segment] handles this.
- [Your name]
```

## Research Instructions Template

Provide the user with:

```markdown
## LinkedIn Search for [Segment]

**Search Query:**
"[Company name pattern]" [Location] [Title]

**Filters:**
- Location: [City/State]
- Current company: [Contains/Is]
- Title: Owner OR General Manager OR Dealer Principal
- Company size: [range]

**What to Look For:**
- [ ] Recent posts about [pain topic]
- [ ] Active in [relevant groups]
- [ ] Under 65 (tech adoption indicator)
- [ ] Posts within last 30 days

**Red Flags (Skip These):**
- Corporate mega-structure (Autonation HQ vs single location)
- No LinkedIn activity in 6+ months
- Clearly not decision maker

**Priority Score:**
- Pain signals visible (1-5)
+ Accessibility (1-5)  
+ Brand fit (1-3)
= Total (target 9-13 for first outreach)
```

## Success Metrics for Hybrid Approach

**Agent Deliverables:**
- [ ] Target list framework created
- [ ] Message sequences written for all segments
- [ ] Research instructions documented
- [ ] Tracking system deployed (if applicable)

**User Execution:**
- [ ] 10-20 targets researched and populated
- [ ] 5 connection requests sent (Week 1)
- [ ] 3 follow-up messages sent (Week 2)
- [ ] 1 meeting scheduled (Week 3)

## Lessons from LotSignal Project

**What Worked:**
- Creating full 4-message sequences upfront
- Building Vercel dashboard with copy-to-clipboard
- Market-specific hooks (Phoenix heat, DFW trucks, Colorado seasons)
- Clear separation: agent builds framework, user executes research

**What to Improve:**
- Set clearer expectations upfront about who does what
- Provide explicit "handoff checklist" for research phase
- Include estimated time for user tasks ("20 min of LinkedIn research")

## When to Use Full-Service vs Hybrid

**Full-Service (Agent Does Everything):**
- User provides existing contact list
- Database/API access available (e.g., Apollo API key)
- Email-based outreach (can send via user's email API)
- Warm intros (user makes connection, agent writes message)

**Hybrid (Agent Builds, User Executes):**
- LinkedIn required (no API access)
- Judgment-heavy research (need human assessment)
- Voice/phone outreach
- High-touch sales requiring personal credibility
