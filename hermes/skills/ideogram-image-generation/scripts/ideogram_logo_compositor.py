#!/usr/bin/env python3
"""
Ideogram + Logo Compositor for OptiRFP LinkedIn Posts
Generates images with Ideogram V4 and composites the exact OptiRFP logo.
"""

import requests
import os
from pathlib import Path
from PIL import Image, ImageDraw
import io

IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY", "___LONG_STRING___")
LOGO_PATH = os.getenv("OPTIRFP_LOGO_PATH", "/home/herby/.hermes/assets/optirfp_logo.jpg")

# Brand colors
DARK_NAVY = "#0F172A"
MINT_GREEN = "#40D395"

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


def build_optirfp_prompt(headline: str, topic: str = "general") -> str:
    """Build a prompt optimized for OptiRFP branded graphics."""
    
    visual = TOPIC_VISUALS.get(topic, TOPIC_VISUALS["general"])
    
    prompt = f"""Professional LinkedIn graphic for OptiRFP (AI-powered RFP response platform).

HEADLINE TEXT (render this prominently in large, bold text, crystal clear):
"{headline}"

VISUAL STYLE:
- Dark navy blue background (#0F172A)
- Mint green accent colors (#40D395) for highlights and glows
- {visual}
- Clean, modern, minimalist professional design
- High contrast for readability
- No clutter, focused composition

LAYOUT:
- Headline text should be the focal point, large and centered
- Visual elements should support, not compete with, the text
- Bottom 20% should be solid dark navy with absolutely NOTHING else (clean space for logo)
- Ample negative space
- Premium quality, suitable for professional social media

RENDERING INSTRUCTIONS:
- Crystal clear text readability - text must be PERFECTLY legible
- Sharp, professional typography
- Modern sans-serif font
- Text should be crisp and easily readable at small sizes

ABSOLUTELY FORBIDDEN - NO EXCEPTIONS:
- NO watermarks of any kind
- NO "LinkedIFP", "Thekecs", "Cxeottics", or any similar text
- NO numbers in corners or edges
- NO fake logos or branding
- NO additional text beyond the exact headline provided
- NO decorative text, UI elements, or icons
- NO timestamps, NO counters, NO progress indicators
- The bottom area must be completely clean dark navy ONLY"""

    return prompt


def generate_ideogram_image(prompt: str, aspect_ratio: str = "ASPECT_1_1", model: str = "V_4") -> dict:
    """Generate an image using Ideogram V4 API."""
    
    url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
    headers = {"Api-Key": IDEOGRAM_API_KEY}
    
    files = {
        "text_prompt": (None, prompt),
        "aspect_ratio": (None, aspect_ratio),
        "model": (None, model),
        "magic_prompt_option": (None, "OFF")  # Disable auto-enhance for more control
    }
    
    response = requests.post(url, headers=headers, files=files, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    image_url = data["data"][0]["url"]
    
    # Download the image
    image_response = requests.get(image_url, timeout=60)
    image_response.raise_for_status()
    
    return {
        "url": image_url,
        "image_data": image_response.content,
        "resolution": data["data"][0].get("resolution"),
        "prompt_used": data["data"][0].get("prompt"),
        "seed": data["data"][0].get("seed")
    }


def composite_logo(image_data: bytes, logo_path: str = None, logo_height: int = 60) -> Image.Image:
    """Composite the OptiRFP logo at the bottom of the image."""
    
    # Load the generated image
    img = Image.open(io.BytesIO(image_data))
    
    # Try to load logo
    logo_full_path = logo_path or LOGO_PATH
    if not os.path.exists(logo_full_path):
        # Return image without logo if logo not found
        return img
    
    try:
        logo = Image.open(logo_full_path)
        
        # Convert logo to RGBA if needed
        if logo.mode != 'RGBA':
            logo = logo.convert('RGBA')
        
        # Calculate logo size
        aspect_ratio = logo.width / logo.height
        new_height = logo_height
        new_width = int(new_height * aspect_ratio)
        
        # Resize logo
        logo = logo.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Calculate position (bottom center with padding)
        padding = 40
        logo_x = (img.width - new_width) // 2
        logo_y = img.height - new_height - padding
        
        # Paste logo onto image
        img.paste(logo, (logo_x, logo_y), logo)
        
    except Exception as e:
        print(f"Warning: Could not composite logo: {e}")
    
    return img


def save_image(img: Image.Image, prefix: str = "optirfp") -> str:
    """Save the image to the output directory."""
    
    output_dir = Path.home() / ".hermes" / "generated_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(os.time()) if hasattr(os, 'time') else 0
    from datetime import datetime
    timestamp = int(datetime.now().timestamp())
    
    local_path = output_dir / f"{prefix}_{timestamp}.png"
    img.save(local_path, "PNG", quality=95)
    
    return str(local_path)


def generate_optirfp_post_with_logo(
    headline: str,
    topic: str = "general",
    aspect_ratio: str = "ASPECT_1_1",
    logo_height: int = 60
) -> dict:
    """
    Generate a complete OptiRFP LinkedIn post image with logo composited.
    
    Args:
        headline: The main text to display (5-8 words max recommended)
        topic: Visual theme from TOPIC_VISUALS
        aspect_ratio: ASPECT_1_1, ASPECT_16_9, etc.
        logo_height: Height of logo in pixels
    
    Returns:
        dict with local_path, headline, topic, quality_check
    """
    
    # Build the prompt
    prompt = build_optirfp_prompt(headline, topic)
    
    # Generate with Ideogram
    result = generate_ideogram_image(prompt, aspect_ratio, model="V_4")
    
    # Composite the logo
    final_img = composite_logo(result["image_data"], logo_height=logo_height)
    
    # Save the result
    local_path = save_image(final_img, prefix="optirfp_ideogram")
    
    # Basic quality assessment
    quality_score = 8.5  # Base score, would need manual review for actual score
    
    return {
        "local_path": local_path,
        "headline": headline,
        "topic": topic,
        "url": result["url"],
        "resolution": result["resolution"],
        "prompt_used": result["prompt_used"],
        "seed": result["seed"],
        "quality_score": quality_score,
        "ready_for_post": quality_score >= 9.0
    }


if __name__ == "__main__":
    # Generate with winning headline
    test = generate_optirfp_post_with_logo(
        headline="Winning RFPs answer 'so what?' first",
        topic="winning"
    )
    print(f"Generated: {test['local_path']}")
    print(f"Resolution: {test['resolution']}")
    print(f"Ready for post: {test['ready_for_post']}")
