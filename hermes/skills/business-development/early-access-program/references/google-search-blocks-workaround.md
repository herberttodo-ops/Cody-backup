# Google/LinkedIn Search Blocks — Agent Workaround Pattern

## Problem

When researching contacts or leads, the agent may encounter:
- **Google CAPTCHA blocks** (`https://www.google.com/sorry/index`)
- **LinkedIn login walls** (requires user credentials)
- **Rate limiting** on search engines
- **Bot detection** by modern websites

These blockers prevent the agent from directly executing research lookups.

## Solution: Multi-Channel Research Fallback

When a search channel is blocked, immediately pivot through this fallback stack:

### 1. DuckDuckGo (Anonymous Search)
```
https://duckduckgo.com/?q=%22[Name]%22+%22[Company]%22+[Location]
```
- No CAPTCHA
- No login required
- Good for finding public pages

### 2. Direct Website Scraping
Check these common pages on the target's domain:
- `/meetourstaff` — Staff listings with titles
- `/aboutus` or `/about` — Owner/team info
- `/team` — Team page
- `/staff` — Staff directory
- Footer — Business registration name

Command pattern:
```bash
curl -s -A "Mozilla/5.0" "https://[domain]/meetourstaff" | grep -i "owner\|manager\|director"
```

### 3. Email Pattern Analysis
When an email like `jrosser@company.com` is found:
- **Rosser** is likely the owner/founder
- Search: "Rosser [Company] [Location]"
- Verify by checking if email appears on About page

### 4. Testimonial/Review Mining
- Google Reviews: Owners often respond to reviews
- Yelp: Sometimes identifies business owner
- DealerRater: Automotive-specific
- BBB: Lists principal contact

### 5. State Business Registries
| State | URL | What You Get |
|-------|-----|--------------|
| TX | mycpa.cpa.state.tx.us/coa/ | Registered agent, officers |
| FL | search.sunbiz.org/ | Officers, registered agent |
| GA | ecorp.sos.ga.gov/ | Officers, principal |
| NC | www.sosnc.gov/search/index/corp | Officers |
| AZ | azsos.gov/business | Officers |
| CA | bizfileportal.sos.ca.gov/ | Officers |
| TN | tnbear.tn.gov/ | Officers |
| MI | cofs.lara.state.mi.us/ | Officers |
| OH | businesssearch.ohiosos.gov/ | Officers |
| PA | file.dos.pa.gov/ | Officers |
| WA | ccfs.sos.wa.gov/ | Officers |

### 6. Apollo.io / Hunter.io (Free Tiers)
- **Apollo**: 50 free credits/month for email finding
- **Hunter**: 25 free searches/month for email verification
- Upload company domain, find decision-makers

## Example: LotSignal Dealer Research

**Blocked:** Google search for "Brian Kahn Len's Auto Brokerage" → CAPTCHA

**Fallback sequence:**
1. ✅ DuckDuckGo — Found kellersauto.com (wrong Keller, but technique worked)
2. ✅ Direct scrape — `franklinmotorstn.com/meetourstaff` → Found "Jessica Shortt - General Manager"
3. ✅ Email analysis — `jrosser@abcautostar.com` → Rosser = likely owner
4. ✅ Testimonial mining — Oso Grande reviews mention "Mike Farmer"
5. ⏭️ State registry — Not needed, enough info found

## What to Document for User

When research is blocked, provide the user with:
1. **Direct LinkedIn search URLs** (they can click and search manually)
2. **Known contact info** found via alternative channels
3. **Specific search queries** to run on LinkedIn Sales Navigator
4. **State registry links** for manual lookup

## Key Insight

The agent's value is NOT in executing the lookup, but in:
- **Building the target list** (200 dealers categorized)
- **Creating search URLs** (LinkedIn search links for each dealer)
- **Identifying patterns** (email clues, testimonial names)
- **Organizing findings** (spreadsheet with research status)
- **Drafting outreach** (personalized emails ready to send)

The user executes the final LinkedIn lookups. The agent does everything else.
