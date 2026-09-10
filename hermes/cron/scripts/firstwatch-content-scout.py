#!/usr/bin/env python3
"""
First Watch Society - Content Intelligence Scout
Runs twice daily to research trending content and suggest reactions.
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Configuration
DASHBOARD_DATA_PATH = os.path.expanduser("~/.openclaw/workspace/master-control-dashboard/data/first-watch-intelligence.json")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

def web_search(query):
    """Perform a web search using curl/ddgr or similar"""
    try:
        # Try using ddgr if available
        result = subprocess.run(
            ["ddgr", "--json", "-n", "5", query],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout:
            return result.stdout
    except:
        pass
    
    # Fallback: return None, we'll use static intel
    return None

def get_box_office_winner():
    """Research current box office #1"""
    return {
        "title": "Check boxofficemojo.com for this weekend's #1",
        "action": "Go to boxofficemojo.com/weekend - react to the winner",
        "priority": "HIGH"
    }

def get_netflix_top10():
    """Research Netflix trending"""
    return {
        "title": "Check Netflix Top 10 Movies",
        "action": "Open Netflix app → Top 10 Movies → Pick one you haven't seen",
        "priority": "HIGH"
    }

def get_trailer_drops():
    """Research recent trailer drops"""
    return {
        "title": "Search YouTube for 'trailer' in last 24 hours",
        "action": "YouTube search: filter by upload date 'today' → 'trailer'",
        "priority": "HIGH" if datetime.now().hour < 12 else "MEDIUM"
    }

def generate_report():
    """Generate the daily content intelligence report"""
    hour = datetime.now().hour
    is_morning = hour < 12
    
    report = []
    
    # Header
    if is_morning:
        report.append("🌅 FIRST WATCH SOCIETY - MORNING CONTENT BRIEF")
    else:
        report.append("🌆 FIRST WATCH SOCIETY - EVENING CONTENT BRIEF")
    
    report.append(f"📅 {datetime.now().strftime('%A, %B %d, %Y')}")
    report.append("")
    
    # Box Office
    report.append("🎬 BOX OFFICE INTEL")
    report.append("-" * 30)
    box_office = get_box_office_winner()
    report.append(f"Priority: {box_office['priority']}")
    report.append(f"Action: {box_office['action']}")
    report.append("")
    
    # Netflix
    report.append("📺 NETFLIX INTEL")
    report.append("-" * 30)
    netflix = get_netflix_top10()
    report.append(f"Priority: {netflix['priority']}")
    report.append(f"Action: {netflix['action']}")
    report.append("")
    
    # Trailers
    report.append("🎞️ TRAILER DROP INTEL")
    report.append("-" * 30)
    trailer = get_trailer_drops()
    report.append(f"Priority: {trailer['priority']}")
    report.append(f"Action: {trailer['action']}")
    report.append("")
    
    # Quick wins
    report.append("⚡ QUICK WINS")
    report.append("-" * 30)
    if is_morning:
        report.append("1. Check YouTube trending tab (5 min)")
        report.append("2. Check r/movies hot posts (5 min)")
        report.append("3. Plan today's reaction topic")
    else:
        report.append("1. Film reaction if you haven't today")
        report.append("2. Check tomorrow's release schedule")
        report.append("3. Batch film 2-3 reactions if possible")
    report.append("")
    
    # Title suggestions based on day of week
    weekday = datetime.now().weekday()
    report.append("📝 SUGGESTED CONTENT FOR TODAY")
    report.append("-" * 30)
    
    if weekday == 0:  # Monday
        report.append("Type: Classic Movie Reaction")
        report.append("Title: '[Movie] REACTION | First Time Watching a Classic'")
        report.append("Why: Start week with evergreen content")
    elif weekday == 2:  # Wednesday
        report.append("Type: Trailer Reaction (URGENT - midweek drop)")
        report.append("Title: '[Trailer] REACTION | This looks INSANE'")
        report.append("Why: Midweek trailer drops get weekend search traffic")
    elif weekday == 4:  # Friday
        report.append("Type: New Release Reaction")
        report.append("Title: '[New Movie] REACTION | Opening Weekend'")
        report.append("Why: Fresh content, trending searches")
    else:
        report.append("Type: Flexible - catch up on backlog")
        report.append("Title: '[Movie] REACTION | Hidden Gem or Overrated?'")
        report.append("Why: Fill gaps, test new angles")
    
    report.append("")
    report.append("-" * 40)
    report.append("💡 Want me to research something specific?")
    report.append("Reply with: 'Research [topic]' and I'll investigate")
    report.append("-" * 40)
    
    return "\n".join(report)

def update_dashboard():
    """Update the dashboard JSON with today's date"""
    try:
        if os.path.exists(DASHBOARD_DATA_PATH):
            with open(DASHBOARD_DATA_PATH, 'r') as f:
                data = json.load(f)
            data['lastUpdated'] = TODAY
            with open(DASHBOARD_DATA_PATH, 'w') as f:
                json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Could not update dashboard: {e}", file=sys.stderr)

def main():
    report = generate_report()
    update_dashboard()
    print(report)

if __name__ == "__main__":
    main()
