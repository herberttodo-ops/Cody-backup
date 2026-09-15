#!/usr/bin/env python3
"""
OptiRFP Random Content + Auto-Post Generator
Picks random headline/topic from content pool, generates image, uploads, outputs Buffer data.
For cron jobs: run this script directly in the cron prompt for fully automated posting.
"""

import random
import subprocess
import json
import re
import sys
from pathlib import Path

HEADLINES = [
    ("80% of losing RFPs are copy-pasted", "copy-paste"),
    ("Your first page determines everything", "page-one"),
    ("Stop recycling. Start winning.", "workflow"),
    ("Winning proposals mirror the source", "winning"),
    ("Specificity beats generic claims", "specificity"),
    ("The so-what is what wins", "so-what"),
    ("Answer the questions they forgot to ask", "winning"),
    ("Mirror their language. Win their trust.", "mirror-language"),
    ("Copy-paste RFPs copy-paste losses", "copy-paste"),
    ("Your first page decides everything", "page-one"),
    ("Winning proposals answer unasked questions", "winning"),
]

BODY_TEMPLATES = [
    "#RFP evaluators have seen it all. Generic claims, recycled language, obvious templates.\n\nThe winners? They prove every claim. Specific metrics. Real outcomes. Names you can verify.\n\nStand out by standing up to scrutiny.",
    "Most RFP responses bury the value under features.\n\nFlip it. Lead with outcomes. Lead with proof. Lead with the transformation they actually care about.\n\nThe 'so what' is what wins.",
    "The evaluators made their decision on page one. Whether they knew it or not.\n\nYour first impression is your only impression. Make it count.\n\nLead with impact. Mirror their priorities. Make them want page two.",
]

def main():
    headline, topic = random.choice(HEADLINES)
    body = random.choice(BODY_TEMPLATES)

    cmd = f"python3 ~/.hermes/scripts/optirfp_autopost.py '{headline}' {topic}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    # Extract catbox URL from autostpost output
    url_match = re.search(r'https://litter\.catbox\.moe/[^\s]+', result.stdout)
    image_url = url_match.group(0) if url_match else None

    post = {
        "channelId": "6a7f74bcb2d9d577437af9a4",
        "text": f"{headline}\n\n{body}\n\n#RFP #B2BSales #ProposalWriting #SalesTips #WinRate",
        "image_url": image_url,
        "schedulingType": "automatic",
        "mode": "addToQueue"
    }

    print("=== OPTIRFP AUTO-POST DATA ===")
    print(json.dumps(post, indent=2))
    print("=== END ===")

    return 0 if image_url else 1

if __name__ == "__main__":
    sys.exit(main())
