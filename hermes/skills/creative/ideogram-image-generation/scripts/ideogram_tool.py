#!/usr/bin/env python3
"""
Ideogram Image Generation Tool
Generates social media graphics with AI-rendered text.
"""

import requests
import os
import json
from pathlib import Path
from datetime import datetime

# API Configuration
IDEOGRAM_API_KEY = os.getenv(
    "IDEOGRAM_API_KEY",
    "___LONG_STRING___"
)

# Visual themes mapped to topics
TOPIC_VISUALS = {
    "copy-paste": "overlapping documents showing copy-paste repetition, dashed lines connecting duplicated content",
    "mirror-language": "matching text highlights, perfectly aligned documents, parallel flowing streams",
    "specificity": "magnifying glass on fine print, sharp detail focus, clarity visualization",
    "page-one": "spotlight illuminating the first page, book concepts, priority visualization",
    "workflow": "circuit lines, node connections, automation flows, process visualization",
    "ai-automation": "neural networks, data flows, AI processing visualization",
    "winning": "upward trends, achievement metrics, success celebration",
    "so-what": "value chain transformation, before/after comparison",
    "general": "professional abstract pattern with subtle tech elements"
}

ASPECT_RATIOS = {
    "square": "ASPECT_1_1",
    "landscape": "ASPECT_16_9",
    "portrait": "ASPECT_9_16",
    "4_3": "ASPECT_4_3",
    "3_2": "ASPECT_3_2"
}


def build_optirfp_prompt(
    headline: str,
    topic: str = "general",
    include_logo_hint: bool = False
) -> str:
    """Build a prompt optimized for OptiRFP branded graphics."""
    
    visual = TOPIC_VISUALS.get(topic, TOPIC_VISUALS["general"])
    
    logo_hint = ""
    if include_logo_hint:
        logo_hint = """
OPTIONAL: Include a subtle 'OptiRFP' text watermark in mint green at bottom corner, small and unobtrusive."""
    
    prompt = f"""Professional LinkedIn graphic for OptiRFP (AI-powered RFP response platform).

HEADLINE TEXT (render this prominently in large, bold, highly readable text):
"{headline}"

VISUAL STYLE:
- Dark navy blue background (#0F172A)
- Mint green accent colors (#40D395) for highlights, glows, and accents
- {visual}
- Clean, modern, minimalist professional design
- High contrast for maximum readability
- No clutter, focused composition
- Premium quality, suitable for professional social media

LAYOUT:
- Headline text should be the FOCAL POINT, large and centered or top-aligned
- Visual elements should SUPPORT, not compete with, the text
- Ample negative space around text
- Professional composition with good visual hierarchy

RENDERING REQUIREMENTS:
- Crystal clear text readability - this is CRITICAL
- Sharp, professional typography
- Modern sans-serif font
- Text must be crisp and easily readable at small sizes (mobile feed)
- High contrast between text and background
- No distortion, blurring, or artifacts on text{logo_hint}"""

    return prompt


def generate_ideogram_image(
    prompt: str,
    aspect_ratio: str = "square",
    model: str = "V_2A",
    output_filename: str = None
) -> dict:
    """
    Generate an image using Ideogram API.
    
    Args:
        prompt: Text description including headline text to render
        aspect_ratio: square, landscape, portrait, 4_3, 3_2
        model: V_2A (latest), V_2, V_1
        output_filename: Optional custom filename
    
    Returns:
        dict with 'url', 'local_path', 'resolution', 'prompt_used', 'seed'
    """
    # Map friendly aspect ratio names to API values
    aspect_api = ASPECT_RATIOS.get(aspect_ratio, "ASPECT_1_1")
    
    url = "https://api.ideogram.ai/generate"
    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": aspect_api,
            "model": model,
            "magic_prompt_option": "AUTO"
        }
    }
    
    print(f"Generating image with Ideogram...")
    print(f"Aspect ratio: {aspect_ratio} ({aspect_api})")
    print(f"Model: {model}")
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
    
    data = response.json()
    
    # Extract image URL
    image_url = data["data"][0]["url"]
    
    # Download the image
    print(f"Downloading from: {image_url[:60]}...")
    image_response = requests.get(image_url, timeout=60)
    image_response.raise_for_status()
    
    # Save locally
    output_dir = Path.home() / ".hermes" / "generated_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if output_filename:
        local_path = output_dir / output_filename
    else:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        local_path = output_dir / f"ideogram_{timestamp}.png"
    
    with open(local_path, "wb") as f:
        f.write(image_response.content)
    
    print(f"Saved to: {local_path}")
    
    return {
        "url": image_url,
        "local_path": str(local_path),
        "resolution": data["data"][0].get("resolution"),
        "prompt_used": data["data"][0].get("prompt"),
        "seed": data["data"][0].get("seed"),
        "is_image_safe": data["data"][0].get("is_image_safe", True)
    }


def generate_optirfp_post(
    headline: str,
    topic: str = "general",
    aspect_ratio: str = "square",
    include_logo_hint: bool = False
) -> dict:
    """
    Generate an OptiRFP social media post with Ideogram.
    
    Args:
        headline: The main text to display
        topic: visual theme (copy-paste, workflow, ai-automation, etc.)
        aspect_ratio: square, landscape, portrait
        include_logo_hint: Whether to mention OptiRFP branding
    
    Returns:
        dict with generation results and file path
    """
    prompt = build_optirfp_prompt(headline, topic, include_logo_hint)
    
    print("=" * 60)
    print(f"Generating OptiRFP post with Ideogram")
    print(f"Headline: {headline}")
    print(f"Topic: {topic}")
    print("=" * 60)
    
    result = generate_ideogram_image(
        prompt=prompt,
        aspect_ratio=aspect_ratio,
        model="V_2A"
    )
    
    return {
        "success": True,
        "headline": headline,
        "topic": topic,
        "local_path": result["local_path"],
        "url": result["url"],
        "resolution": result["resolution"],
        "prompt_used": result["prompt_used"],
        "seed": result["seed"]
    }


if __name__ == "__main__":
    # Test generation
    test_headlines = [
        ("80% of losing RFPs are copy-pasted", "copy-paste"),
        ("Your first page determines everything", "page-one"),
        ("Stop recycling. Start winning.", "workflow"),
    ]
    
    for headline, topic in test_headlines:
        print("\n" + "=" * 60)
        result = generate_optirfp_post(
            headline=headline,
            topic=topic,
            aspect_ratio="square"
        )
        print(f"\nResult: {result['local_path']}")
        print(f"Resolution: {result['resolution']}")
