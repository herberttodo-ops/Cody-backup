#!/usr/bin/env python3
"""
Logo Compositor Template — Social Media Automation Pipeline
Generate branded social media images with logo placement at bottom right.

Usage:
    python logo_compositor.py "Headline text" topic
    
Environment:
    LOGO_PATH — path to logo image (jpg/png with white background)
    IDEOGRAM_API_KEY — Ideogram API key for base image generation
    OUTPUT_DIR — where to save final images (default: ~/.hermes/generated_images)
"""

import os
import sys
import requests
from pathlib import Path
from PIL import Image
import io

# Configuration
IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY")
LOGO_PATH = os.getenv("LOGO_PATH", str(Path.home() / ".hermes" / "assets" / "logo.jpg"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(Path.home() / ".hermes" / "generated_images")))


def build_prompt(headline: str, topic: str, brand: str) -> str:
    """Build Ideogram prompt. Override this for brand-specific styling."""
    
    topic_visuals = {
        "stat": "bold statistic display, data visualization, professional metrics",
        "insight": "minimalist infographic, key points, checkmark icons",
        "tip": "before/after split, action-oriented, instructional",
        "general": "professional abstract, clean design, modern",
    }
    
    visual = topic_visuals.get(topic, topic_visuals["general"])
    
    prompt = f"""Professional LinkedIn graphic for {brand}.

HEADLINE TEXT:
"{headline}"
- Positioned in upper portion (top 40%)
- Large, bold, highly readable
- Text is primary focal point

VISUAL STYLE:
- Dark background (#0A0A0A)
- {visual}
- Clean, modern, professional
- High contrast for readability
- Minimal clutter

LAYOUT (CRITICAL):
- Headline in upper portion
- Bottom 25% completely clean dark space
- No text, elements, or graphics in bottom 25%
- Solid dark color only

ABSOLUTELY FORBIDDEN:
- NO logos except what I provide
- NO watermarks
- NO additional text beyond headline
- NO timestamps or counters
"""
    return prompt


def generate_base_image(prompt: str, aspect_ratio: str = "ASPECT_4_3") -> bytes:
    """Generate base image via Ideogram."""
    
    url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
    headers = {"Api-Key": IDEOGRAM_API_KEY}
    files = {
        "text_prompt": (None, prompt),
        "aspect_ratio": (None, aspect_ratio),
        "model": (None, "V_4"),
        "magic_prompt_option": (None, "OFF"),
    }

    response = requests.post(url, headers=headers, files=files, timeout=120)
    response.raise_for_status()
    data = response.json()

    image_url = data["data"][0]["url"]
    image_response = requests.get(image_url, timeout=60)
    image_response.raise_for_status()

    return image_response.content


def composite_logo(image_data: bytes, 
                   logo_path: str = LOGO_PATH,
                   target_width_pct: float = 0.28,
                   margin_bottom: int = 150,
                   margin_right: int = 150) -> Image.Image:
    """
    Composite logo onto image at bottom right.
    
    Args:
        image_data: Raw image bytes
        logo_path: Path to logo file (white background will be made transparent)
        target_width_pct: Logo width as % of image width (0.25-0.35 typical)
        margin_bottom: Pixels from bottom edge (150 recommended for LinkedIn)
        margin_right: Pixels from right edge (150 recommended)
    """
    
    # Load images
    img = Image.open(io.BytesIO(image_data)).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")

    # Make white background transparent
    data = logo.getdata()
    newData = []
    for item in data:
        # White pixels (>240 RGB) become transparent
        if item[0] > 240 and item[1] > 240 and item[2] > 240:
            newData.append((255, 255, 255, 0))
        else:
            newData.append(item)
    logo.putdata(newData)

    # Resize logo
    target_width = int(img.width * target_width_pct)
    aspect = logo.width / logo.height
    target_height = int(target_width / aspect)
    
    # Clamp to reasonable size
    target_height = max(target_height, 50)   # Minimum 50px
    target_height = min(target_height, 120)  # Maximum 120px
    target_width = int(target_height * aspect)
    
    logo = logo.resize((target_width, target_height), Image.Resampling.LANCZOS)

    # Position at bottom right
    position = (img.width - logo.width - margin_right, 
                img.height - logo.height - margin_bottom)
    
    img.paste(logo, position, logo)
    return img


def generate_branded_post(headline: str, topic: str, brand: str) -> str:
    """Generate complete branded post with logo."""
    
    # Build prompt
    prompt = build_prompt(headline, topic, brand)
    
    # Generate base image
    image_data = generate_base_image(prompt)
    
    # Composite logo
    final_img = composite_logo(image_data)
    
    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    timestamp = int(__import__("time").time())
    final_path = OUTPUT_DIR / f"{brand.lower().replace(' ', '_')}_social_{timestamp}.png"
    final_img.save(final_path)

    return str(final_path)


if __name__ == "__main__":
    headline = sys.argv[1] if len(sys.argv) > 1 else "Your headline here"
    topic = sys.argv[2] if len(sys.argv) > 2 else "general"
    brand = sys.argv[3] if len(sys.argv) > 3 else "BrandName"
    
    result = generate_branded_post(headline, topic, brand)
    print(result)
