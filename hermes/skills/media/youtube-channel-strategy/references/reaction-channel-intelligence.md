# Reaction Channel Content Intelligence System

From First Watch Society session. How to build a real-time content research dashboard for YouTube reaction channels.

## Architecture

The intelligence system has two layers:
1. **Dashboard (static JSON)** - Container for data
2. **Conversation (dynamic research)** - Engine that populates it

### Why Not Automated Scraping?

Attempted approaches that FAILED:
- YouTube Trending API: blocked without auth
- Reddit API: requires OAuth, returns "blocked by network security"  
- Box Office Mojo: heavy JavaScript, curl returns unreadable output
- TMDB API: requires API key

**Lesson: Be honest about what cannot be automated. Position the system as "conversation-driven research with structured output."**

## Dashboard Implementation

### JSON Data Structure

```json
{
  "lastUpdated": "YYYY-MM-DD",
  "trending": [
    {
      "id": "1",
      "title": "Content name",
      "type": "movie|tv|trailer",
      "views": "View count or 'Research needed'",
      "age": "How old",
      "priority": "high|medium|low",
      "angle": "Suggested reaction angle",
      "status": "not-reacted|done"
    }
  ],
  "gaps": [
    {
      "title": "Gap description",
      "opportunity": "What to create",
      "potential": "X-Y subs"
    }
  ],
  "upcoming": [
    {
      "date": "Month Year",
      "title": "Event name",
      "action": "What to do",
      "priority": "high|medium"
    }
  ],
  "competitors": [
    {
      "channel": "Name",
      "subs": "Sub count",
      "strengths": "What works",
      "lesson": "Your takeaway"
    }
  ],
  "ideas": ["String array"],
  "keywords": ["String array"]
}
```

### React Page Tabs

```
Overview | Calendar | Titles | Thumbnails | Series | Tools | Intelligence
```

Intelligence tab is LAST, marked with emoji (e.g. "🔥 Intelligence").

### Key UI Sections in Intelligence Tab

1. **Research Request Box**
   - Yellow border, prominent placement
   - Textarea with placeholder examples
   - Submit button that alerts "Research request submitted"
   - Example prompts below box

2. **Trending Now**
   - Cards with priority badges (HIGH = red border)
   - Type, views, age metadata
   - Suggested angle
   - Status badge (Not Reacted / Done)

3. **Content Gaps**
   - Green cards showing low-competition opportunities
   - Estimated sub gain

4. **Upcoming Releases**
   - Date, title, action, priority

5. **Competitor Intel**
   - Channel name, sub count
   - Strengths and lessons

6. **SEO Keywords**
   - Tag cloud display

## Research Workflow

### User Requests Research

User: "Research what's trending this week"

### Agent Actions

1. **Attempt automated sources** (knowing many will fail):
   - YouTube Trending (usually blocked)
   - Reddit r/movies (usually blocked)
   - Box Office Mojo (JS-heavy, unreliable)

2. **Fall back to guided research**:
   - Ask user to check specific URLs
   - Provide checklist of sources to monitor
   - Give template for what to look for

3. **Update dashboard** with:
   - Generic trending placeholders (labeled as "Research needed")
   - Content gaps based on calendar (Halloween prep, Award season)
   - Competitor lessons from known channels

4. **Deploy updated JSON**

### What to Put in "Trending" When Real Data Unavailable

Instead of fake specific movies, use:

```json
{
  "title": "Weekend Box Office Winner",
  "views": "Research needed",
  "angle": "Real-time reaction to whatever won Friday-Sunday",
  "researchAction": "Check boxofficemojo.com for #1 film"
}
```

This is honest, actionable, and doesn't age out.

## Mobile UX Checklist

- Horizontal scroll for tabs (overflow-x-auto)
- 2-column grids on mobile, 3-4 on desktop
- Stack layouts vertically
- Touch-friendly buttons (min 44px)
- Font scaling (text-sm on mobile, text-base on desktop)
- Responsive padding (px-4 on mobile, px-6 on desktop)

## Common Pitfalls

1. **Don't hardcode movie examples** - Use evergreen classics (Pulp Fiction) or generic placeholders
2. **Don't present template data as research** - Clearly label "Research needed" vs actual findings
3. **Don't promise automated updates** - System is conversation-driven
4. **Always include status badges** - "Not Reacted" / "Done" for tracking
5. **Tab navigation must match state array** - If tabs include 'intelligence', the array must too
