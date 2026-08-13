---
name: ideogram-image-generation
description: Generate social media graphics using Ideogram AI with text baked into the image
version: 1.0.0
triggers:
  - generate images with Ideogram
  - test Ideogram API
  - create graphics with AI-rendered text
---

# Ideogram Image Generation Skill

Generate social media graphics using Ideogram's API, which excels at rendering text directly in images.

## API Details

- **Endpoint**: `POST https://api.ideogram.ai/v1/ideogram-v4/generate` (multipart/form-data)
- **Auth Header**: `Api-Key: <your_key>` (NOT Bearer token)
- **Models**: `V_4` (latest), `V_2A`, `V_2`, `V_1`
- **Pricing**: ~$0.04/image (50%+ cheaper than OpenAI)

## Request Format (V4)

```python
import requests

url = "https://api.ideogram.ai/v1/ideogram-v4/generate"
headers = {"Api-Key": IDEOGRAM_API_KEY}
files = {
    "text_prompt": (None, prompt),
    "aspect_ratio": (None, "ASPECT_1_1"),
    "model": (None, "V_4"),
    "magic_prompt_option": (None, "OFF")  # Disable auto-enhance
}

response = requests.post(url, headers=headers, files=files, timeout=120)
data = response.json()
image_url = data["data"][0]["url"]
```

## Cost Comparison

| Workflow | Cost per Image | Monthly (30 posts) |
|----------|----------------|-------------------|
| gpt-image-1 + composite | ~$0.08-0.12 | ~$2.40-3.60 |
| **Ideogram V4 + logo** | **~$0.04** | **~$1.20** |
| **Savings** | — | **50-67%** |

## Aspect Ratios

| Value | Dimensions | Use Case |
|-------|-----------|----------|
| `ASPECT_1_1` | 1024x1024 | Square (LinkedIn, Instagram) |
| `ASPECT_16_9` | 1024x576 | Landscape (Twitter/X, LinkedIn) |
| `ASPECT_9_16` | 576x1024 | Portrait (Stories, Reels) |
| `ASPECT_4_3` | 1024x768 | Classic photo ratio |
| `ASPECT_3_2` | 1024x682 | Landscape photo |

## Usage

### Basic Generation

```python
import requests
import os
from pathlib import Path

IDEOGRAM_API_KEY = os.getenv("IDEOGRAM_API_KEY", "___LONG_STRING___")

def generate_ideogram_image(
    prompt: str,
    aspect_ratio: str = "ASPECT_1_1",
    model: str = "V_2A"
) -> dict:
    """
    Generate an image using Ideogram API.
    
    Args:
        prompt: Text description including headline text to render
        aspect_ratio: ASPECT_1_1, ASPECT_16_9, ASPECT_9_16, etc.
        model: V_2A (latest), V_2, V_1
    
    Returns:
        dict with 'url', 'local_path', 'resolution'
    """
    url = "https://api.ideogram.ai/generate"
    headers = {
        "Api-Key": IDEOGRAM_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "image_request": {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "model": model,
            "magic_prompt_option": "AUTO"
        }
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()
    data = response.json()
    
    # Download the image
    image_url = data["data"][0]["url"]
    image_response = requests.get(image_url, timeout=60)
    image_response.raise_for_status()
    
    # Save locally
    output_dir = Path.home() / ".hermes" / "generated_images"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = int(os.path.getctime(__file__) if os.path.exists(__file__) else 0)
    local_path = output_dir / f"ideogram_{timestamp}.png"
    
    with open(local_path, "wb") as f:
        f.write(image_response.content)
    
    return {
        "url": image_url,
        "local_path": str(local_path),
        "resolution": data["data"][0].get("resolution"),
        "prompt_used": data["data"][0].get("prompt"),
        "seed": data["data"][0].get("seed")
    }
```

### OptiRFP-Specific Prompt Builder

```python
def build_optirfp_prompt(
    headline: str,
    topic: str = "general",
    include_logo_hint: bool = False
) -> str:
    """
    Build a prompt optimized for OptiRFP branded graphics.
    
    Args:
        headline: The main text to display prominently
        topic: visual theme (copy-paste, workflow, ai-automation, etc.)
        include_logo_hint: Whether to mention OptiRFP branding
    """
    
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
- Text should be crisp and easily readable at small sizes"""

    return prompt
```

## Example Usage

```python
# Generate a test graphic
prompt = build_optirfp_prompt(
    headline="80% of losing RFPs are copy-pasted",
    topic="copy-paste"
)

result = generate_ideogram_image(
    prompt=prompt,
    aspect_ratio="ASPECT_1_1"
)

print(f"Generated: {result['local_path']}")
print(f"Resolution: {result['resolution']}")
```

## Comparison with Current Workflow

| Aspect | Current (Composite) | Ideogram (Direct) |
|--------|---------------------|-------------------|
| Text rendering | PIL/Pillow (brand font) | AI-generated |
| Logo handling | Exact logo file composited | AI-approximated or omitted |
| Brand consistency | High (exact assets) | Variable (AI interpretation) |
| Visual creativity | Background only | Full image coherence |
| Text quality | Perfect typography | AI-dependent, sometimes stylized |
| Cost | ~$0.08/image | ~$0.04/image |
| Speed | 2 API calls + compositing | 1 API call |

## When to Use Ideogram vs Composite

**Use Ideogram when:**
- Visual creativity and text integration matter more than exact brand font
- You want faster generation (single API call)
- Cost savings are a priority
- Logo presence is optional or can be AI-interpreted

**Use Composite when:**
- Exact logo reproduction is required
- Brand font consistency is critical
- You need precise control over layout
- Compliance requires accurate brand representation

## Testing Checklist

- [ ] API key configured as `IDEOGRAM_API_KEY` env var
- [ ] Test generation with simple prompt
- [ ] Verify text readability in output
- [ ] Check brand color approximation
- [ ] Compare side-by-side with composite workflow
- [ ] Evaluate at small sizes (mobile feed view)

## Prompt Engineering for Clean Results

Ideogram often adds its own text/watermarks even when instructed not to. To minimize this:

1. **Aggressive exclusions in prompt:**
   - Use "NO logos", "NO watermarks", "NO additional text" multiple times
   - Specify "NO [BrandName] text anywhere"
   - Explicitly forbid UI elements, social icons, decorative text

2. **Reserve clean zones:**
   - "Bottom 25%: solid dark navy only, completely empty, ready for logo"
   - Separate visual elements from text areas explicitly

3. **Set magic_prompt_option to OFF** for more literal interpretation:
   ```json
   "magic_prompt_option": "OFF"
   ```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Invalid Bearer token" | Use `Api-Key` header, not `Authorization: Bearer` |
| "V3 model not supported" | V_3 requires different endpoint; use V_2A for now |
| Text garbled or misspelled | Simplify prompt, check spelling in headline |
| AI adds its own branding | Tighten prompt exclusions; still may occur with V_2A |
| Text too small | Add "large text" or "prominent headline" to prompt |
| Wrong colors | Be explicit with hex codes in prompt |
| Poor composition | Add layout instructions (centered, top-aligned) |

## Files

- Output: `~/.hermes/generated_images/ideogram_*.png`

## API Documentation

- Official docs: https://ideogram.ai/api
- Pricing: https://ideogram.ai/pricing