#!/usr/bin/env python3
"""
OptiRFP Auto-Post Pipeline
Full workflow: Ideogram image + logo composite + catbox upload → Buffer-ready JSON
Usage: python3 optirfp_autopost.py "Headline text" topic
Outputs: JSON with channelId, text, image_url, scheduling ready for mcp__buffer__create_post
"""

import subprocess
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path.home() / ".hermes" / "skills" / "creative" / "ideogram-image-generation" / "scripts"

def run(cmd, timeout=120):
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    return result.stdout.strip() if result.returncode == 0 else None

def generate(headline, topic):
    cmd = f"cd ~/.openclaw/workspace && python3 {SCRIPT_DIR}/ideogram_logo_compositor.py --headline '{headline}' --topic {topic} --aspect square"
    out = run(cmd, 180)
    if not out:
        return None
    for line in out.split('\n'):
        if 'Final image saved:' in line:
            return line.split('Final image saved:')[1].strip()
    return None

def upload_catbox(path):
    cmd = f'curl -s -F "reqtype=fileupload" -F "time=1h" -F "fileToUpload=@{path}" https://litterbox.catbox.moe/resources/internals/api.php'
    url = run(cmd, 60)
    return url if url and url.startswith('https://') else None

def main():
    if len(sys.argv) < 3:
        print("Usage: python3 optirfp_autopost.py 'Headline text' topic", file=sys.stderr)
        return 1

    headline = sys.argv[1]
    topic = sys.argv[2]

    print(f"[1/3] Generating image (Ideogram + logo)...")
    path = generate(headline, topic)
    if not path:
        print("ERROR: Image generation failed", file=sys.stderr)
        return 1

    print(f"[2/3] Uploading to catbox.moe...")
    url = upload_catbox(path)
    if not url:
        print("ERROR: catbox upload failed", file=sys.stderr)
        return 1

    post = {
        "channelId": "6a7f74bcb2d9d577437af9a4",
        "text": f"{headline}\n\n#RFP #B2BSales #WinRate",
        "image_url": url,
        "image_path": path,
        "schedulingType": "automatic",
        "mode": "addToQueue"
    }
    print("[3/3] Buffer post data:")
    print(json.dumps(post, indent=2))
    return 0

if __name__ == "__main__":
    sys.exit(main())
