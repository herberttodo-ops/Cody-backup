---
name: web-platform-process-audit
description: "Audit web platforms and recommend automation tools."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [audit, automation, workflow, web, process, integration]
    related_skills: [dogfood, content-performance-analysis]
---

# Web Platform Process Audit

## Overview

This skill guides systematic auditing of websites, portals, and web platforms to identify manual business processes that should be automated. The output is a prioritized set of recommendations with specific tools, cost estimates, and an implementation roadmap.

Typical audit targets:
- HOA/resident portals (HOASpace, etc.) with PDF/email workflows
- E-commerce sites with manual order processing
- Service business sites with phone/email intake
- Membership platforms with paper-based renewals
- Any site where users download PDFs, email forms, or call for tasks that could be self-service

## Prerequisites

- `curl` available for HTML scraping
- Browser tools (`browser_exec`, etc.) available as primary reconnaissance method
- Basic understanding of common SaaS integration patterns (forms, databases, email, payments)

## Inputs

The user provides:
1. **Target URL** — the website or portal to audit
2. **Known pain points** (optional) — e.g., "PDFs are emailed to the Welcome Center for registration"
3. **Budget constraints or preferred tools** (optional)
4. **Output format preference** — structured report, bullet list, markdown file

## Workflow

### Phase 1: Reconnaissance / Site Mapping

**Goal:** Understand the site's structure, technology, and visible workflows without needing full access.

**Primary method — Browser tools:**
```
browser_exec: new_tab("https://TARGET_SITE")
```
Navigate the site, capture screenshots, and note navigation structure.

**Fallback method — curl-based HTML scraping** (use when browser tools fail due to missing Chrome, network issues, or the site blocks automation):

```bash
# Fetch homepage and extract all links
curl -s -L "https://TARGET_SITE" | grep -o -E '<a[^>]*href="[^"]*"[^>]*>[^<]*</a>'

# Check for forms
curl -s -L "https://TARGET_SITE" | grep -o -E '<(form|input|select|textarea)[^>]*>'

# Check for email addresses (reveal manual communication paths)
curl -s -L "https://TARGET_SITE" | grep -o -E '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# Check for PDF/doc downloads
curl -s -L "https://TARGET_SITE" | grep -o -E 'href="[^"]*\.(pdf|docx?|xlsx?)"'

# Identify platform/CMS
curl -s -L "https://TARGET_SITE" | grep -i -E "(generator|powered by|wp-content|drupal|joomla|hoaspace)"
```

**What to catalog:**
- All navigation sections and sub-pages
- Any forms (login, registration, contact, application)
- PDF/document download links
- Email addresses embedded in pages
- Phone numbers for manual tasks
- "Grayed out" or inactive menu items (often reveal missing features)
- Payment processing presence or absence
- Calendar / event system
- FAQ/help content

**Key signal:** Any workflow where a user must:
- Download a PDF, fill it out, and email it back
- Call a phone number to complete a task
- Visit a physical location for something that could be online
- Re-enter information already captured elsewhere
- Wait for manual confirmation/approval without status visibility

### Phase 2: Process Identification

For each manual workflow found, document:

| Field | Description |
|-------|-------------|
| **Process Name** | Short label, e.g., "Annual Owner Registration" |
| **Current Flow** | Step-by-step of the manual process |
| **Pain Points** | What's broken, slow, or frustrating |
| **Data Inputs** | What information is collected |
| **Data Outputs** | What happens to the data (stored, emailed, printed) |
| **Actors** | Who initiates, who processes, who approves |
| **Frequency** | How often this happens (per day/week/year) |
| **Volume** | Estimated number of transactions |

### Phase 3: Solution Design

For each process, map to a modern automation stack:

| If the current process involves... | Then recommend... |
|-----------------------------------|---------------------|
| PDF forms emailed in | Online form builder (JotForm, Fillout, Tally, Google Forms) → database |
| Manual data re-entry | Direct API integration or webhook-based data flow |
| Email-based communication | Transactional email (Resend, SendGrid) + newsletter (Mailchimp, Mailerlite) |
| Phone call for status checks | Self-service status portal or automated status emails |
| Paper check/cash payments | Online payment (Stripe, Square, PayPal) |
| Static document repository | Versioned document library with "acknowledge receipt" tracking |
| Manual calendar/event management | Shared calendar (Google Calendar, TeamUp) with RSVP |
| No notification system | Email/SMS automation (Twilio for SMS, Mailchimp for newsletters) |
| Committee/application signups | Form → database → lead routing → notification |

**Recommended tool stack by budget tier:**

**Free Tier (< $10/mo):**
- Forms: Google Forms, Tally, Fillout free
- Database: Google Sheets, Airtable free tier
- Email: Resend (3k/mo free), Mailchimp (<500 contacts free)
- Payments: Stripe (pay-per-transaction only)
- SMS: Twilio (pay-per-message)

**Pro Tier ($50-150/mo):**
- Forms: JotForm Gold ($39/mo), Typeform Pro
- Database: Airtable Plus ($20/user/mo)
- Email: Resend + Mailchimp Essentials ($13/mo)
- Payments: Stripe Standard
- Internal dashboard: Airtable or Notion

**Enterprise Tier ($200+/mo):**
- Full CRM integration (HubSpot, Salesforce)
- SSO/SAML authentication
- Custom web portal development
- Dedicated automation platform (Zapier/Make with Premium apps)

### Phase 4: Report Generation

Produce a structured report with these sections:

1. **Executive Summary** — Platform identified, tech stack, most critical gaps
2. **Current State Assessment** — Site map, processes catalogued, manual vs digital breakdown
3. **Process Deep-Dives** — For each identified manual process:
   - Current flow diagram/description
   - Pain points
   - Recommended automation flow
   - Tools needed
   - Estimated cost
4. **Prioritization Matrix** — Rank by impact vs. effort (Quick Wins vs. Strategic)
5. **Implementation Roadmap** — Phased plan:
   - Phase 1: Foundation (online forms, database, basic notifications) — Weeks 1-2
   - Phase 2: Communication layer (newsletters, alerts, reminders) — Weeks 3-4
   - Phase 3: Enhanced automation (payments, advanced workflows) — Weeks 5-8
   - Phase 4: Advanced integrations (APIs, custom portal) — Months 3-6
6. **Quick Wins** — Actions implementable within one week
7. **Budget Estimate** — Tool costs, setup effort, ongoing maintenance

**Report format:** Save as markdown. Include specific page URLs, form field inventories, and exact tool recommendations.

### Phase 5: Follow-up (Optional)

If the user wants to implement:
1. Create detailed specs for online forms (field mapping from current PDFs)
2. Set up the recommended tools
3. Build proof-of-concept forms
4. Configure email automation
5. Test end-to-end flow
6. Train staff on new dashboard/process

## Pitfalls & Lessons Learned

1. **Browser tool failures are common.** Always have the curl-based fallback ready. The browser harness may fail due to missing Chrome, snap-based Chrome path issues, or headless mode problems. Curl works for static site reconnaissance and can extract links, forms, emails, and page text.

2. **Don't assume you need credentials.** Many process workflows are visible publicly (PDF downloads, form pages, FAQ content). Login may only be needed for protected member data. Do public reconnaissance first.

3. **"Grayed out" menu items are signals.** In HOASpace and similar legacy platforms, inactive menu entries like "Administration/Welcome Center" often indicate a feature the organization knows they need but hasn't enabled. Flag these as automation opportunities.

4. **Look for email addresses in page source.** Manual workflows often leave email addresses like `tenants@apcppoa.com` or `forms@company.com` embedded in HTML — these reveal the actual communication paths staff use.

5. **Legacy HOA platforms (HOASpace) are constrained.** You cannot rewrite the platform. Recommendations must be:
   - Embedded within existing pages (link to external forms)
   - Parallel systems (external form → database)
   - Or require a platform migration (note the cost)

6. **Always check for mobile friendliness.** Many community portals are desktop-optimized. Mobile-friendly workflows (forms, payments, alerts) significantly improve resident adoption.

7. **Account for staff training.** The cheapest technical solution may require the most behavior change. Balance tool cost with change management effort.

## References

- `references/manual-workflow-patterns.md` — Common patterns found in web platforms and their automation mappings
- `references/tool-comparison-matrix.md` — Side-by-side comparison of form builders, databases, email platforms, and payment processors
