#!/usr/bin/env python3
"""
OptiRFP Content Generator v2 - Expanded Content Library
Picks random headline/topic from expanded content pool with diverse angles.
"""

import random
import subprocess
import json
import re
import sys
from pathlib import Path
from datetime import datetime

# ============================================================
# EXPANDED CONTENT LIBRARY - Multiple Content Pillars
# ============================================================

# --- PILLAR 1: The Problem Framework (Pain Points) ---
PROBLEM_HEADLINES = [
    ("80% of losing RFPs are copy-pasted", "copy-paste"),
    ("Copy-paste RFPs copy-paste losses", "copy-paste"),
    ("Generic proposals get generic results", "specificity"),
    ("Recycled language signals low effort", "copy-paste"),
    ("Templates that everyone uses... everyone ignores", "specificity"),
    ("When your RFP sounds like ChatGPT", "ai-automation"),
    ("The features-first trap loses deals", "so-what"),
    ("Bid on everything. Win nothing.", "workflow"),
    ("The illusion of productivity: hitting send", "workflow"),
]

# --- PILLAR 2: The Solution Framework (Winning Strategies) ---
SOLUTION_HEADLINES = [
    ("Win the RFP before page two", "page-one"),
    ("Your first page determines everything", "page-one"),
    ("Specificity beats generic claims", "specificity"),
    ("Winning proposals mirror the source", "winning"),
    ("Mirror their language. Win their trust.", "mirror-language"),
    ("Answer the questions they forgot to ask", "winning"),
    ("Stop recycling. Start winning.", "workflow"),
    ("Lead with outcomes. Lead with proof.", "so-what"),
]

# --- PILLAR 3: The Psychology Framework (Evaluator Mindset) ---
PSYCHOLOGY_HEADLINES = [
    ("Readers scan. Evaluators decide.", "page-one"),
    ("Cognitive load kills credibility", "specificity"),
    ("Familiarity breeds confidence", "mirror-language"),
    ("The halo effect works both ways", "winning"),
    ("Trust is earned in specifics", "specificity"),
    ("Pattern matching: they see bad RFPs daily", "winning"),
]

# --- PILLAR 4: The Metrics Framework (Data/Proof) ---
METRICS_HEADLINES = [
    ("3.2x higher win rate with specificity", "winning"),
    ("Top 20% responses get 80% of wins", "winning"),
    ("Average evaluator spends 90 seconds", "workflow"),
    ("Page one impressions: you get one", "page-one"),
    ("70% of decisions happen on section one", "page-one"),
]

# --- PILLAR 5: The Contrarian Framework (Challenging Assumptions) ---
CONTRARIAN_HEADLINES = [
    ("Your process is the product", "workflow"),
    ("Ignore the scoring rubric. Read between lines.", "winning"),
    ("Longer proposals score worse", "specificity"),
    ("Compliance without distinction loses", "copy-paste"),
    ("The best response might not win", "winning"),
]

# --- PILLAR 6: Action/Punchy (Quick Impact) ---
ACTION_HEADLINES = [
    ("Remove three buzzwords today", "specificity"),
    ("Replace features with outcomes", "so-what"),
    ("Find three claims needing proof", "winning"),
    ("Mirror the first paragraph", "mirror-language"),
    ("Kill your cover letter boilerplate", "page-one"),
]

# --- PILLAR 7: Question-Framed (Engagement) ---
QUESTION_HEADLINES = [
    ("Is your RFP response actually answering them?", "winning"),
    ("How many buzzwords are in your first paragraph?", "specificity"),
    ("What questions did they forget to ask?", "winning"),
    ("Does page one make them want page two?", "page-one"),
    ("Are you writing for procurement or outcomes?", "so-what"),
]

# Combine all buckets
ALL_HEADLINES = (
    PROBLEM_HEADLINES + 
    SOLUTION_HEADLINES + 
    PSYCHOLOGY_HEADLINES + 
    METRICS_HEADLINES + 
    CONTRARIAN_HEADLINES + 
    ACTION_HEADLINES + 
    QUESTION_HEADLINES
)

# ============================================================
# EXPANDED BODY TEMPLATES - More angles and voices
# ============================================================

BODY_TEMPLATES = [
    # --- Angle 1: The Evaluator's Perspective ---
    "#RFP evaluators have seen it all. Generic claims, recycled language, obvious templates.\n\nThe winners? They prove every claim. Specific metrics. Real outcomes. Names you can verify.\n\nStand out by standing up to scrutiny.",

    # --- Angle 2: The So-What Framework ---
    "Most RFP responses bury the value under features.\n\nFlip it. Lead with outcomes. Lead with proof. Lead with the transformation they actually care about.\n\nThe 'so what' is what wins.",

    # --- Angle 3: The Hook ---
    "The evaluators made their decision on page one. Whether they knew it or not.\n\nYour first impression is your only impression. Make it count.\n\nLead with impact. Mirror their priorities. Make them want page two.",

    # --- Angle 4: The Mirror Strategy ---
    "People trust what looks familiar. It's cognitive bias, and it's your advantage.\n\nMirror their terminology. Reflect their priorities. Use their language like it was your first.\n\nThe closer you match their mental model, the easier you are to select.",

    # --- Angle 5: The Anti-Template ---
    "Templates save time. They also scream 'bulk send.'\n\nEvery boilerplate paragraph is a signal: This wasn't written for you.\n\nCut the generic. Add the specific. One custom detail outweighs ten recycled features.",

    # --- Angle 6: The Specificity Principle ---
    "'Best-in-class' means nothing. '20% faster' means something. '20% faster validated by ClientCo' means everything.\n\nSpecificity builds credibility. Numbers build trust. Names build confidence.\n\nGeneric claims don't win competitive RFPs.",

    # --- Angle 7: The Process Insights ---
    "Winning RFP responses aren't written. They're engineered.\n\nEach section answers a specific question. Each paragraph moves the evaluator forward. Each sentence earns the next.\n\nStructure is strategy.",

    # --- Angle 8: The Time Reality ---
    "Your evaluator has 20 proposals and 2 hours.\n\nThey're not reading. They're scanning. They're pattern-matching. They're deciding.\n\nMake the decision easy. Put the win where they'll see it first.",

    # --- Angle 9: The AI Warning ---
    "AI-generated responses all sound the same. Confident, polished, and hollow.\n\nEvaluators feel it. They can't quite say why, but they know.\n\nHuman insight beats algorithmic fluency every time.",

    # --- Angle 10: The Questioning Mindset ---
    "Good RFP responses answer the questions asked.\n\nWinning RFP responses answer the questions behind the questions. The unspoken concerns. The hidden priorities. The real decision criteria.\n\nRead between the lines.",

    # --- Angle 11: The Confidence Play ---
    "Every hedging phrase weakens your position.\n\n'May help' → 'Reduces'\n'Can potentially' → 'Delivers'\n'We believe' → 'Proven by'\n\nConfidence builds credibility. Tentativeness telegraphs uncertainty.",

    # --- Angle 12: The Curation Principle ---
    "Not every RFP is worth your time. Not every bid deserves a response.\n\nThe best teams say no more often than yes. They know their win rates by industry, by size, by deadline.\n\nStrategy starts with selection.",
]

# ============================================================
# HASHTAG ROTATION
# ============================================================

HASHTAG_SETS = [
    "#RFP #B2BSales #ProposalWriting #SalesTips #WinRate",
    "#RFPResponse #GovTech #B2B #SalesStrategy #ProposalTips",
    "#RFP #ProposalManagement #SalesEnablement #B2BSales #WinMore",
    "#RFPWriting #BusinessDevelopment #SalesProcess #ProposalTips #B2B",
    "#RFPResponse #SalesTips #WinningProposals #B2BSales #GovCon",
]

# ============================================================
# CONTENT SELECTION STRATEGY
# ============================================================

def select_diverse_headline():
    """Pick a headline, ensuring variety by rotating through pillars."""
    # In production, we'd track recently used pillars
    # For now, random selection from expanded pool
    return random.choice(ALL_HEADLINES)

def generate_post():
    """Generate a complete post with diverse elements."""
    headline, topic = select_diverse_headline()
    body = random.choice(BODY_TEMPLATES)
    hashtags = random.choice(HASHTAG_SETS)
    
    return {
        "headline": headline,
        "topic": topic,
        "body": body,
        "hashtags": hashtags,
    }

def main():
    post = generate_post()
    
    # Output structured data for next step in pipeline
    output = {
        "headline": post["headline"],
        "topic": post["topic"],
        "body": post["body"],
        "hashtags": post["hashtags"],
        "generated_at": datetime.now().isoformat(),
        "content_stats": {
            "total_headlines": len(ALL_HEADLINES),
            "total_bodies": len(BODY_TEMPLATES),
            "hashtag_sets": len(HASHTAG_SETS),
        }
    }
    
    print("=== OPTIRFP POST DATA ===")
    print(json.dumps(output, indent=2))
    print("=== END ===")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
