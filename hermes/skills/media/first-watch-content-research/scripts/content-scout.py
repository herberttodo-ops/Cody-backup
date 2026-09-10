#!/usr/bin/env python3
"""
First Watch Society - Content Intelligence Scout
Generates daily/weekly content briefs with suggestions.
Run manually or via cron (cron setup requires user configuration).
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# Configuration
DASHBOARD_DATA_PATH = os.path.expanduser("~/.openclaw/workspace/master-control-dashboard/data/first-watch-intelligence.json")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")

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
    hour = datetime.now().hour
    return {
        "title": "Search YouTube for 'trailer' in last 24 hours",
        "action": "YouTube search: filter by upload date 'today' → 'trailer'",
        "priority": "HIGH" if hour < 12 else "MEDIUM"
    }

def generate_report():
    """Generate the daily content intelligence report"""
    hour = datetime.now().hour
    is_morning = hour < 12
    
    report = []
    
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
    
    # Day-of-week suggestions
    weekday = datetime.now().weekday()
    report.append("📝 SUGGESTED CONTENT FOR TODAY")
    report.append("-" * 30)
    
    if weekday == 0:  # Monday
        report.append("Type: Classic Movie Reaction")
        report.append("Title: '[Movie] REACTION | First Time Watching a Classic'")
    elif weekday == 2:  # Wednesday
        report.append("Type: Trailer Reaction (URGENT)")
        report.append("Title: '[Trailer] REACTION | This looks INSANE'")
    elif weekday == 4:  # Friday
        report.append("Type: New Release Reaction")
        report.append("Title: '[New Movie] REACTION | Opening Weekend'")
    else:
        report.append("Type: Flexible - catch up on backlog")
        report.append("Title: '[Movie] REACTION | Hidden Gem or Overrated?'")
    
    report.append("")
    report.append("-" * 40)
    report.append("💡 Want me to research something specific?")
    report.append("Reply with: 'Research [topic]' and I'll investigate")
    report.append("-" * 40)
    
    return "\n".join(report)

def main():
    report = generate_report()
    print(report)

if __name__ == "__main__":
    main()
