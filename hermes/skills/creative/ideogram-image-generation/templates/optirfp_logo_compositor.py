#!/usr/bin/env python3
"""
Ideogram Image Generator + OptiRFP Logo Compositor
Generates branded social media graphics with AI-rendered text + exact logo.

Usage:
    python3 optirfp_logo_compositor.py --headline "Your headline here" --topic winning

Topics: copy-paste, mirror-language, specificity, page-one, workflow, ai-automation, winning, so-what, general
"""

import os
import sys
import time
import requests
from pathlib import Path
from PIL import Image
import io

# API Key - uses env var or falls back to default
IDEOGRAM_API_KEY = os.getenv(
    "IDEOGRAM_API_KEY",
    "___LONG_STRING___"
)

LOGO_PATH = os.getenv("OPTIRFP_LOGO", str(Path.home() / ".hermes" / "assets" / "optirfp_logo.jpg"))
OUTPUT_DIR = Path.home() / ".hermes" / "generated_images"

TOPIC_VISUALS = {
    "copy-paste": "overlapping documents showing copy-paste repetition, dashed lines connecting duplicated content",
    "mirror-language": "matching text highlights, perfectly aligned documents, parallel flowing streams",
    "specificity": "magnifying glass on fine print, sharp detail focus, clarity visualization",
    "page-one": "spotlight illuminating the first page, book concepts, priority visualization",
    "workflow": "circuit lines, node connections, automation flows, process visualization",
    "ai-automation": "neural networks, data flows, AI processing visualization",
    "winning": "upward trends, achievement metrics, success celebration, trophy vibes",
    "so-what": "value chain transformation, before/after comparison",
    "general": "professional abstract pattern with subtle tech elements"
}


def build_optirfp_prompt(headline: str, topic: str = "general") -> str:
    """Build prompt with aggressive exclusions to prevent fake watermarks."""
    visual = TOPIC_VISUALS.get(topic, TOPIC_VISUALS["general"])
    prompt = f"""Professional LinkedIn graphic for OptiRFP (AI-powered RFP response platform).

HEADLINE TEXT (render this prominently in large, bold text):
"{headline}"

VISUAL STYLE:
- Dark navy blue background (#0F172A)
- Mint green accent colors (#40D395) for highlights and glows
- {visual}
- Clean, modern, minimalist professional design
- High contrast for readability
- No clutter, focused composition

LAYOUT:
- Headline text should be the focal point, large and centered or top-aligned
- Visual elements should support, not compete with, the text
- Ample negative space
- Premium quality, suitable for professional social media

RENDERING:
- Crystal clear text readability
- Sharp, professional typography
- Modern sans-serif font
- Text should be crisp and easily readable at small sizes

ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:
- NO watermarks of any kind
- NO "LinkedIFP", "Thekecs", "Cxeottics", "OptiIFP", "IptiRFp" or similar fake branding
- NO LinkedIn icons, NO social media icons, NO "in" logos
- NO numbers in corners or edges
- NO fake logos or branding of any kind
- NO additional text beyond the exact headline provided
- NO small text in corners, NO bylines, NO attribution text
- NO decorative text, UI elements, or icons
- NO timestamps, NO counters, NO progress indicators
- Bottom 20% of image must be completely clean dark navy ONLY - solid color, no elements, no text, no graphics, completely empty for logo placement"""
    return prompt


def generate_ideogram_image(prompt: str, aspect_ratio: str = "ASPECT_1_1", model: str = "V_4") -> dict:
    """Generate image using Ideogram V4 API."""
    url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
    headers = {"Api-Key": IDEOGRAM_API_KEY}
    files = {
        "text_prompt": (None, prompt),
        "aspect_ratio": (None, aspect_ratio),
        "model": (None, model),
        "magic_prompt_option": (None, "OFF"),
    }

    print(f"[Ideogram] Generating image with model={model}, aspect={aspect_ratio}")
    response = requests.post(url, headers=headers, files=files, timeout=120)
    response.raise_for_status()
    data = response.json()

    image_url = data["data"][0]["url"]
    print(f"[Ideogram] Image URL: {image_url}")

    # Download
    img_response = requests.get(image_url, timeout=60)
    img_response.raise_for_status()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    local_path = OUTPUT_DIR / f"ideogram_v4_{ts}.png"
    with open(local_path, "wb") as f:
        f.write(img_response.content)

    print(f"[Ideogram] Saved to: {local_path}")
    return {
        "url": image_url,
        "local_path": str(local_path),
        "image_data": img_response.content,
        "resolution": data["data"][0].get("resolution"),
        "prompt_used": data["data"][0].get("prompt"),
        "seed": data["data"][0].get("seed"),
    }


def composite_logo(image_data: bytes, logo_path: str = LOGO_PATH) -> Image.Image:
    """Composite logo onto image with transparency handling for JPEG logos."""
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")

    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo not found: {logo_path}")

    logo = Image.open(logo_path).convert("RGBA")

    # Make near-white pixels transparent (for JPEG logos on dark backgrounds)
    data = logo.getdata()
    new_data = []
    for item in data:
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            new_data.append((255, 255, 255, 0))
        else:
            new_data.append(item)
    logo.putdata(new_data)

    # Resize logo
    logo_height = 55
    aspect = logo.width / logo.height
    logo = logo.resize((int(logo_height * aspect), logo_height), Image.Resampling.LANCZOS)

    # Paste centered at bottom
    position = ((img.width - logo.width) // 2, img.height - logo.height - 40)
    img.paste(logo, position, logo)

    return img


def generate_optirfp_post_with_logo(headline: str, topic: str = "general", aspect_ratio: str = "ASPECT_1_1") -> str:
    """
    Full pipeline: generate Ideogram image + composite logo.
    Returns path to final image.
    """
    prompt = build_optirfp_prompt(headline, topic)
    result = generate_ideogram_image(prompt, aspect_ratio=aspect_ratio, model="V_4")

    final_img = composite_logo(result["image_data"])
    ts = int(time.time())
    final_path = OUTPUT_DIR / f"optirfp_{topic}_{ts}.png"
    final_img.save(final_path, "PNG")
    print(f"[Compositor] Final image saved to: {final_path}")
    return str(final_path)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate OptiRFP branded social media graphics")
    parser.add_argument("--headline", required=True, help="Main headline text to display")
    parser.add_argument("--topic", default="general", 
                        choices=list(TOPIC_VISUALS.keys()),
                        help="Visual theme for the graphic")
    parser.add_argument("--aspect", default="ASPECT_1_1",
                        choices=["ASPECT_1_1", "ASPECT_16_9", "ASPECT_9_16", "ASPECT_4_3", "ASPECT_3_2"],
                        help="Aspect ratio for the output image")
    args = parser.parse_args()

    path = generate_optirfp_post_with_logo(args.headline, args.topic, args.aspect)
    print(path)
