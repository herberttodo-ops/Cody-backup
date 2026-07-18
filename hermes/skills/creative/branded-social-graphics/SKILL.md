---
name: branded-social-graphics
description: Create professional social media graphics using exact brand logos (not AI-generated) with dynamic, on-brand backgrounds
triggers:
  - user needs branded graphics for social media
  - user has exact logo file that must be used faithfully
  - creating automated content systems with consistent branding
  - logo compositing with AI-generated backgrounds
---

# Branded Social Media Graphics with Logo Compositing

Create professional social media graphics that use an exact brand logo (not AI-generated) with dynamic, on-brand backgrounds.

## When to Use

- Need consistent brand graphics for social media
- Have an exact logo file that must be used faithfully
- Want AI-generated backgrounds that match brand colors and topic
- Creating automated content systems (cron jobs, pipelines)

## Approach

### Two-Step Process

1. **AI generates background** — Prompt explicitly excludes logos/text, focuses on visual elements
2. **Python composites exact logo** — PIL/Pillow handles logo placement, text overlay, effects

### Why Not Pure AI?

AI image generators cannot faithfully reproduce a specific logo from text descriptions. They always interpret and change it. Solution: Generate background only, composite exact logo separately.

## Implementation Pattern

### 1. Logo Preprocessing

```python
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
```

### 2. Background Generation

**API Strategy**: OpenRouter primary, OpenAI fallback

OpenRouter avoids OpenAI billing limits and returns base64 data:

```python
import requests
import base64

or_key = os.getenv("OPENROUTER_API_KEY")
oai_key = os.getenv("OPENAI_API_KEY")

# Try OpenRouter first
if or_key:
    try:
        url = "https://openrouter.ai/api/v1/images/generations"
        headers = {
            "Authorization": f"Bearer {or_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://{brand}.com",  # Required
            "X-Title": "{Brand}"  # Required
        }
        
        size_map = {"square": "1024x1024", "landscape": "1792x1024", "portrait": "1024x1792"}
        
        payload = {
            "model": "openai/gpt-image-1",
            "prompt": prompt,
            "n": 1,
            "size": size_map.get(aspect_ratio, "1024x1024")
        }
        
        response = requests.post(url, headers=headers, json=payload, timeout=120)
        response.raise_for_status()
        data = response.json()
        
        if "data" in data and len(data["data"]) > 0 and "b64_json" in data["data"][0]:
            image_bytes = base64.b64decode(data["data"][0]["b64_json"])
            # Save to file
            with open(filepath, "wb") as f:
                f.write(image_bytes)
            return str(filepath)
    except Exception as e:
        print(f"OpenRouter failed: {e}, trying OpenAI...")

# Fall back to OpenAI direct
if oai_key:
    # Use openai library or direct API call
    pass
else:
    raise ValueError("Neither OPENROUTER_API_KEY nor OPENAI_API_KEY is set")
```

Prompt structure:
```
Professional social media background for [BRAND].
[SPECIFIC VISUAL DESCRIPTION]

LAYOUT:
- Top 25%: Clean area for headline text
- Middle 50%: Main visual elements
- Bottom 25%: Clean area for logo

STRICT EXCLUSIONS:
- NO logos, NO brand names, NO company names
- NO "{brand}" text or any text whatsoever
- NO watermarks or signatures
- NO UI elements, buttons, interface components
- Brand colors: [HEX CODES]
- NO people, NO faces
- Abstract/conceptual style
```

### 3. Text Positioning & Layout Zones (Critical)

**Final Working Layout (Zone-Based) - LOCKED:**

```
Top 0-35%:     Headline text (clean background, centered vertically in this zone)
Middle 35-75%: Visual elements (graphics, circuits, glow effects)
Bottom 75-100%: Logo placement (clean, no overlap)
```

**Code Implementation:**
```python
# Text positioned at 12% from top (within 0-35% zone)
start_y = int(height * 0.12)

# Visuals generated in 35-75% zone via prompt
# Logo placed at bottom center (75-100% zone)
logo_y = int(height * 0.85)
```

**Why this works:**
- Text 0-35%: Dedicated clean zone prevents overlap with visuals
- Visuals 35-75%: Lowered from original 25% to avoid text encroachment
- Logo 75-100%: Guaranteed clean space, no duplication issues

**In Prompt:** Explicitly tell AI the zone structure with FORCEFUL exclusions:
```
COMPOSITION REQUIREMENTS:
- Top 35% of image: Keep CLEAN with only subtle gradient/pattern (NO visual elements, NO documents, NO circuits here)
- Middle 40% (35-75%): Place ALL visual elements here (documents, circuits, glow effects)
- Bottom 25% (75-100%): Clean dark navy for logo
```

**Failed Approaches:**
- Centered text (45%): Overlaps central visual elements → Grade: C+
- Top 25% only: Visuals sometimes encroached into text area
- Text at 12% with visuals at 25%: Still occasional overlap

**Styling:**
- **Readability**: Semi-transparent dark navy gradient bar behind text
- **Effects**: Brand color glow + drop shadow for depth
- **Font**: Bold sans-serif (Inter, Helvetica, etc.)
- **Position**: Centered horizontally, 12% from top vertically

### 4. Logo Placement

- **Size**: 15-25% of image width
- **Position**: Bottom center or corner
- **Integration**: Remove white background first
- **Margin**: 4-5% padding from edges

## Visual Concepts by Topic

Map content topics to visual styles for variety. This prevents boring/repetitive backgrounds:

| Topic | Visual Style | Use For |
|-------|-------------|---------|
| `copy-paste` | Overlapping documents, duplication glow effects | Content recycling, templates |
| `mirror-language` | Matching highlights, aligned documents, parallel streams | Client alignment, mirroring |
| `specificity` | Detail focus, magnifying effects, clarity visualization | Precision, details matter |
| `page-one` | Spotlight on first document, book concepts, timeline | First impressions, priority |
| `workflow` | Circuit lines, node connections, automation flows | Processes, efficiency |
| `ai-automation` | Neural networks, data flows, processing visualization | AI, technology, automation |
| `winning` | Upward trends, achievement metrics, success visuals | Success stories, results |
| `so-what` | Value chain, transformation visualization, before/after | Value proposition, outcomes |

**Implementation:**
```python
TOPIC_VISUALS = {
    "copy-paste": "overlapping documents showing duplication and repetition",
    "mirror-language": "matching text highlights, perfectly aligned documents",
    "specificity": "sharp detail focus, magnifying glass on fine print",
    "page-one": "spotlight illuminating the first page of a document",
    # ... etc
}

visual_description = TOPIC_VISUALS.get(topic, "abstract professional pattern")
```

## Common Pitfalls

1. **Text overlapping visuals** → Use zone-based layout (Text 0-35%, Visuals 35-75%)
2. **Logo looks like a sticker** → Remove white background before compositing
3. **Boring backgrounds** → Use topic-mapped visual concepts with circuit patterns, glows
4. **Poor readability** → Semi-transparent dark bar + brand color glow + drop shadow
5. **Off-brand colors** → Explicit hex codes in every prompt
6. **Background contamination** → AI puts logos/text in background → Use MULTIPLE "NO logos"/"NO text" statements in prompt
7. **Logo duplication** → AI generates brand name as text → Add "NO [Brand] text", "NO watermarks", "NO signatures"
8. **API billing limits** → OpenRouter as primary (`openai/gpt-image-1`), OpenAI as fallback
9. **Layout imbalance** → Test multiple variations, use vision analysis to evaluate
10. **Missing API keys in subprocess/execute_code** → When running outside main Hermes context, `.env` files aren't auto-loaded. Use `load_env_file()` helper (see API Keys section)
11. **Text clipped at edges** → Font size too large for headline with padding. Use `font_size = int(height * 0.07)` max (not 0.09). Add boundary constraints: `bar_x1 = max(0, x - padding)` and `bar_x2 = min(width, x + text_width + padding)`

## Iteration Learnings (OptiRFP Case Study)

**V1 (Basic)**: Text at top 25%, visuals middle 50% → Visuals encroached on text area
**V2 (Centered)**: Text centered at 45% → Overlapped central visual element (glowing document icon) → Grade: C+
**V3 (Zone-Based - FINAL)**: Text 0-35%, Visuals 35-75%, Logo 75-100% → Clean separation, no overlap → Grade: A ✓

**Key insights:**
1. Just saying "top area" in prompt wasn't enough - AI still placed visuals at 25%
2. Had to specify exact percentages (35%, 75%) and be FORCEFUL: "NO visual elements in top 35%"
3. Multiple negative constraints needed: "NO logos", "NO text", "NO watermarks", "NO [Brand] name"
4. Zone-based layout (0-35/35-75/75-100) is the only reliable approach tested

**Testing methodology:**
- Generate graphic
- Use vision analysis to evaluate positioning
- Check for: text/visual overlap, logo duplication, background contamination
- Iterate prompt if issues found

## Example Workflow

```python
# 1. Generate background (no text/logos)
bg_prompt = """Dark navy background with circuit patterns...
NO text, NO logos..."""
background_path = generate_image(bg_prompt)

# 2. Open and prepare
image = Image.open(background_path).convert('RGBA')
logo = remove_white_background(Image.open(logo_path))

# 3. Add headline with effects
image = add_text_with_glow(image, headline)

# 4. Composite logo
image.paste(logo, (x, y), logo)

# 5. Save
image.convert('RGB').save(output_path)
```

## Complete Working Implementation

```python
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def add_text_with_effects(image, text, y_percent=0.14):
    """Add headline text with glow and shadow effects - PRODUCTION VERSION.
    
    FIXED: Uses smaller font size (0.07 vs 0.09) to prevent edge clipping.
    FIXED: Adds boundary constraints to keep bar within image bounds.
    """
    width, height = image.size
    draw = ImageDraw.Draw(image)
    
    # Font size: 0.07 of height prevents edge clipping (was 0.09)
    try:
        font_size = int(height * 0.07)
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = int(height * y_percent)
    
    # Semi-transparent dark bar with BOUNDARY CONSTRAINTS
    padding = int(height * 0.025)
    bar_x1 = max(0, x - padding * 2)  # Prevent negative
    bar_y1 = y - padding
    bar_x2 = min(width, x + text_width + padding * 2)  # Prevent exceeding width
    bar_y2 = y + text_height + padding
    
    overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([bar_x1, bar_y1, bar_x2, bar_y2], fill=(15, 23, 42, 200))
    image = Image.alpha_composite(image, overlay)
    
    # Glow effect
    draw = ImageDraw.Draw(image)
    glow_color = (64, 211, 149, 80)  # Brand mint with alpha
    for offset in range(6, 0, -2):
        glow_overlay = Image.new('RGBA', image.size, (0, 0, 0, 0))
        glow_draw = ImageDraw.Draw(glow_overlay)
        glow_draw.text((x, y), text, font=font, fill=glow_color)
        glow_blur = glow_overlay.filter(ImageFilter.GaussianBlur(radius=offset))
        image = Image.alpha_composite(image, glow_blur)
    
    # Main text
    draw = ImageDraw.Draw(image)
    draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    
    return image
```

## Tools in this Repo

- `create_branded_social_graphic` — Dynamic backgrounds, topic-mapped visuals
- `create_professional_graphic` — Cleaner, simpler backgrounds
- `create_branded_graphic` — Basic compositing (legacy)

## Brand Color Reference

OptiRFP example:
- Logo mint: `#40D395`
- Background navy: `#0F172A`
- Card dark: `#1E293B`
- Text white: `#FFFFFF`

## Files

- Logo: `~/.hermes/assets/optirfp_logo.jpg`
- Output: `~/.hermes/generated_images/`
- Tool: `tools/logo_compositor_v3.py`
- Tool: `tools/openrouter_image_tool.py`

## API Keys & Implementation

**Loading API Keys from .env**

When running scripts via `execute_code` or subprocess, environment variables from `~/.hermes/.env` aren't automatically loaded. Add this helper:

```python
def load_env_file(path):
    """Load environment variables from .env file."""
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            key, val = line.split('=', 1)
            if key not in os.environ:
                os.environ[key] = val

# Load from .env files before accessing API keys
load_env_file(Path.home() / ".hermes/.env")
load_env_file(Path.home() / ".env")
```

**OpenRouter (Recommended)**
- Returns base64 JSON (not URL)
- Avoids OpenAI billing limits
- Uses `openai/gpt-image-1` model

```python
url = "https://openrouter.ai/api/v1/images/generations"
headers = {
    "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
    "HTTP-Referer": "https://{brand}.com",  # Required
    "X-Title": "{Brand}"
}
payload = {
    "model": "openai/gpt-image-1",
    "prompt": prompt,
    "size": "1024x1024"
}
response = requests.post(url, headers=headers, json=payload)
data = response.json()
image_bytes = base64.b64decode(data["data"][0]["b64_json"])
```

**OpenAI Direct (Fallback)**
- Same base64 response format
- Same `gpt-image-1` model

**Check:**
```python
if not (os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY")):
    raise Error("No image generation API key set")
```

## Version History

- V1: Basic compositing — logo had white box, text overlapped elements
- V2: Text-safe zones, logo background removal — cleaner but boring backgrounds  
- V3: Dynamic topic-based backgrounds, brand color glows — professional, engaging

## Success Metrics

Graphics should score 9/10 on:
- Visual interest (dynamic backgrounds)
- Brand consistency (exact logo, brand colors)
- Readability (clear text, proper contrast)
- Professionalism (suitable for LinkedIn)