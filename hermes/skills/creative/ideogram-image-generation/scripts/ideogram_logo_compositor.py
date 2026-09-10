#!/usr/bin/env python3
"""
Ideogram + Logo Compositor Tool
Generates graphics with Ideogram (text baked in) + composites exact logo.
"""

import requests
import os
import json
from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# API Configuration
IDEOGRAM_API_KEY = os.getenv(
    "IDEOGRAM_API_KEY",
    "___LONG_STRING___"
)

# Brand Configuration
BRAND_COLORS = {
    "mint": "#40D395",
    "navy": "#0F172A",
    "dark_card": "#1E293B",
    "white": "#FFFFFF"
}

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


def remove_white_background(image, tolerance=35):
    """Make logo background transparent."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    data = image.getdata()
    new_data = []
    
    for item in data:
        r, g, b, a = item
        # White pixels become transparent
        if r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance:
            new_data.append((r, g, b, 0))
        else:
            new_data.append((r, g, b, a))
    
    image.putdata(new_data)
    return image


def find_logo_path(brand_name="optirfp"):
    """Find logo file in standard locations."""
    extensions = [".png", ".jpg", ".jpeg", ".PNG", ".JPG"]
    base_paths = [
        Path.home() / ".hermes" / "assets",
        Path.home() / "assets",
    ]
    
    for base in base_paths:
        for ext in extensions:
            logo_path = base / f"{brand_name}_logo{ext}"
            if logo_path.exists():
                return str(logo_path)
            # Try without underscore
            logo_path = base / f"{brand_name}{ext}"
            if logo_path.exists():
                return str(logo_path)
    
    return None


def composite_logo_on_image(
    base_image_path: str,
    logo_path: str = None,
    logo_size_percent: float = 0.20,
    position: str = "bottom_center",
    margin_percent: float = 0.05
) -> str:
    """
    Composite exact logo onto an existing image.
    
    Args:
        base_image_path: Path to the base image (from Ideogram)
        logo_path: Path to logo file (auto-detected if None)
        logo_size_percent: Logo width as % of image width
        position: bottom_center, bottom_right, bottom_left
        margin_percent: Margin from edges
    
    Returns:
        Path to final composited image
    """
    # Auto-detect logo if not provided
    if logo_path is None:
        logo_path = find_logo_path()
        if logo_path is None:
            raise ValueError("Logo not found. Please provide logo_path or ensure logo exists in ~/.hermes/assets/")
    
    # Open images
    base = Image.open(base_image_path).convert("RGBA")
    logo = Image.open(logo_path).convert("RGBA")
    
    # Remove white background from logo
    logo = remove_white_background(logo)
    
    # Calculate logo size
    max_logo_width = int(base.width * logo_size_percent)
    logo_ratio = logo.height / logo.width
    new_width = min(max_logo_width, logo.width)
    new_height = int(new_width * logo_ratio)
    logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    # Calculate position
    margin = int(base.height * margin_percent)
    
    if position == "bottom_center":
        x = (base.width - new_width) // 2
        y = base.height - new_height - margin
    elif position == "bottom_right":
        x = base.width - new_width - margin
        y = base.height - new_height - margin
    elif position == "bottom_left":
        x = margin
        y = base.height - new_height - margin
    else:
        x = (base.width - new_width) // 2
        y = base.height - new_height - margin
    
    # Create composite
    base.paste(logo, (x, y), logo)
    
    # Save final
    output_dir = Path(base_image_path).parent
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_path = output_dir / f"ideogram_logo_{timestamp}.png"
    
    # Convert to RGB for final save (removes alpha)
    final_rgb = base.convert("RGB")
    final_rgb.save(final_path, quality=95)
    
    return str(final_path)


def build_ideogram_prompt(
    headline: str,
    topic: str = "general",
    brand_name: str = "OptiRFP"
) -> str:
    """
    Build a prompt for Ideogram that generates background + text,
    but NO logo (we'll composite that separately).
    """
    
    visual = TOPIC_VISUALS.get(topic, TOPIC_VISUALS["general"])
    
    prompt = f"""Professional LinkedIn graphic for {brand_name} (B2B SaaS platform).

HEADLINE TEXT - POSITIONING IS CRITICAL:
"{headline}"
- Place headline text in the UPPER CENTER of the image (top 40% of frame)
- Text must be CENTERED horizontally, not left-aligned or right-aligned
- Text should occupy the visual center of attention
- Large, bold, highly readable text
- Generous spacing around the text on all sides

LAYOUT ZONES - FOLLOW EXACTLY:
Zone 1 (Top 0-40%): Headline text, centered, prominent
Zone 2 (Middle 40-75%): Visual elements ({visual}), supporting the message
Zone 3 (Bottom 75-100%): Clean dark navy area with NO elements whatsoever

CRITICAL LAYOUT RULES:
- The headline text MUST be centered in the upper portion of the image
- Visual elements in the middle should frame and support the centered text
- The bottom area should naturally fade to solid navy - NO hard edges, NO rectangular blocks
- The overall composition should feel balanced with the text as the clear focal point
- NO navy-colored rectangles, blocks, or bars anywhere - smooth gradients only

VISUAL STYLE:
- Dark navy blue background (#0F172A) with smooth, subtle gradients
- Mint green accent colors (#40D395) for highlights, glows, and accents
- {visual}
- Clean, modern, minimalist professional design
- High contrast for maximum readability
- Premium quality, suitable for professional social media
- Centered, balanced composition

RENDERING REQUIREMENTS:
- Crystal clear text readability - this is CRITICAL
- Sharp, professional typography
- Modern sans-serif font
- Text must be crisp and easily readable at small sizes (mobile feed)
- High contrast between text and background
- Smooth, gradual transitions - NO hard edges or solid color blocks

ABSOLUTE PROHIBITIONS (NEVER INCLUDE THESE):
- NO "{brand_name}" text anywhere in the image
- NO "{brand_name}" watermark or signature
- NO company name text of any kind
- NO logos or brand marks
- NO additional text beyond the headline
- NO decorative text, filler text, or Lorem Ipsum
- NO social media icons (no LinkedIn icons, no social logos)
- NO UI elements, buttons, or interface components
- NO navy-colored rectangles, bars, or blocks (smooth gradients only)
- NO hard edges between visual areas - everything should blend smoothly"""

    return prompt


def generate_ideogram_image(
    prompt: str,
    aspect_ratio: str = "square",
    model: str = "V_4"
) -> dict:
    """
    Generate an image using Ideogram V4 API.
    
    Returns:
        dict with 'url', 'local_path', 'resolution', 'prompt_used', 'seed'
    """
    aspect_api = ASPECT_RATIOS.get(aspect_ratio, "ASPECT_1_1")
    
    # V4 uses multipart/form-data instead of JSON
    url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
    headers = {
        "Api-Key": IDEOGRAM_API_KEY
    }
    
    # V4 uses multipart form data
    files = {
        "text_prompt": (None, prompt),
        "aspect_ratio": (None, aspect_api),
        "model": (None, model),
        "magic_prompt_option": (None, "OFF")  # Disable auto-enhance for more control
    }
    
    print(f"Generating image with Ideogram V4...")
    print(f"Aspect ratio: {aspect_ratio} ({aspect_api})")
    
    response = requests.post(url, headers=headers, files=files, timeout=120)
    
    if response.status_code != 200:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        response.raise_for_status()
    
    data = response.json()
    image_url = data["data"][0]["url"]
    
    # Download
    print(f"Downloading...")
    image_response = requests.get(image_url, timeout=60)
    image_response.raise_for_status()
    
    # Save
    output_dir = Path.home() / ".hermes" / "generated_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    local_path = output_dir / f"ideogram_v4_raw_{timestamp}.png"
    
    with open(local_path, "wb") as f:
        f.write(image_response.content)
    
    return {
        "url": image_url,
        "local_path": str(local_path),
        "resolution": data["data"][0].get("resolution"),
        "prompt_used": data["data"][0].get("prompt"),
        "seed": data["data"][0].get("seed")
    }


def generate_optirfp_post_with_logo(
    headline: str,
    topic: str = "general",
    aspect_ratio: str = "square",
    logo_path: str = None,
    logo_size_percent: float = 0.18
) -> dict:
    """
    Complete workflow: Generate with Ideogram + composite exact logo.
    
    Args:
        headline: Main text to display (5-8 words recommended)
        topic: visual theme (copy-paste, workflow, etc.)
        aspect_ratio: square, landscape, portrait
        logo_path: Optional custom logo path
        logo_size_percent: Logo width as % of image
    
    Returns:
        dict with paths and metadata
    """
    print("=" * 60)
    print(f"Generating OptiRFP Post with Ideogram + Logo Composite")
    print(f"Headline: {headline}")
    print(f"Topic: {topic}")
    print("=" * 60)
    
    # Step 1: Generate with Ideogram (text + background, no logo)
    prompt = build_ideogram_prompt(headline, topic)
    ideogram_result = generate_ideogram_image(prompt, aspect_ratio)
    
    print(f"\nIdeogram image saved: {ideogram_result['local_path']}")
    
    # Step 2: Composite exact logo
    print(f"\nCompositing exact logo...")
    final_path = composite_logo_on_image(
        base_image_path=ideogram_result["local_path"],
        logo_path=logo_path,
        logo_size_percent=logo_size_percent,
        position="bottom_center"
    )
    
    print(f"Final image saved: {final_path}")
    
    return {
        "success": True,
        "headline": headline,
        "topic": topic,
        "ideogram_raw_path": ideogram_result["local_path"],
        "final_path": final_path,
        "resolution": ideogram_result["resolution"],
        "url": ideogram_result["url"]
    }


def verify_image_quality(image_path: str, headline: str) -> dict:
    """
    Verify image quality using vision analysis.
    This is a helper function - actual vision check is done via tool call.
    
    Returns quality criteria for manual/vision verification.
    """
    print("\n" + "=" * 60)
    print("QUALITY VERIFICATION CHECKLIST")
    print("=" * 60)
    print(f"\nImage: {image_path}")
    print(f"Expected headline: '{headline}'")
    print("\nCheck:")
    print("  [ ] 1. Headline text perfectly readable?")
    print("  [ ] 2. No watermarks or fake branding?")
    print("  [ ] 3. Dark navy (#0F172A) + mint (#40D395) colors present?")
    print("  [ ] 4. Logo cleanly at bottom?")
    print("  [ ] 5. No garbled text or AI artifacts?")
    print("\nScore: ___/10 (9+ = proceed, <9 = regenerate)")
    print("\nUse vision_analyze tool:")
    print(f'  vision_analyze(image_url="{image_path}", ')
    print(f'                 question="Rate 1-10: text clarity, watermarks, colors, logo, artifacts?")')
    print("=" * 60)
    
    return {
        "image_path": image_path,
        "headline": headline,
        "checks": [
            "Text perfectly readable",
            "No watermarks/fake branding", 
            "Brand colors (navy/mint)",
            "Logo cleanly placed",
            "No AI artifacts"
        ],
        "threshold": "9/10 to proceed"
    }


if __name__ == "__main__":
    # Test with the previous headlines
    test_posts = [
        ("80% of losing RFPs are copy-pasted", "copy-paste"),
        ("Your first page determines everything", "page-one"),
        ("Stop recycling. Start winning.", "workflow"),
    ]
    
    for headline, topic in test_posts:
        print("\n" + "=" * 60)
        result = generate_optirfp_post_with_logo(
            headline=headline,
            topic=topic,
            aspect_ratio="square"
        )
        print(f"\n✓ Final result: {result['final_path']}")
