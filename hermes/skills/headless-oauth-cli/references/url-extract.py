#!/usr/bin/env python3
"""Extract a wrapped URL from tmux pane output.

OAuth URLs printed by CLI tools often wrap across multiple terminal lines.
This script reconstructs the full URL from tmux capture-pane output.
"""
import subprocess
import re
import sys

SESSION = sys.argv[1] if len(sys.argv) > 1 else "oauth-auth"

def extract_url(session):
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session, "-p", "-S", "-15"],
        capture_output=True, text=True
    )
    lines = result.stdout.split("\n")
    text = "".join(lines)
    
    markers = [
        "https://platform.claude.com/oauth/authorize",
        "https://claude.com/cai/oauth/authorize",
    ]
    start = -1
    for m in markers:
        start = text.find(m)
        if start != -1:
            break
    
    end = text.find("Paste code here", start)
    if start == -1 or end == -1:
        return None
    
    url = text[start:end].strip()
    url = re.sub(r"\s+", "", url)
    return url

if __name__ == "__main__":
    url = extract_url(SESSION)
    print(url if url else "URL_NOT_FOUND")
