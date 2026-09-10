#!/usr/bin/env python3
"""
OpenAI Image Generation Tool using gpt-image-1

This module provides image generation using OpenAI's gpt-image-1 model.

Available tools:
- openai_image_generate: Generate images from text prompts using gpt-image-1

Features:
- High-quality image generation using OpenAI's gpt-image-1
- Support for various aspect ratios and sizes
- Automatic retry on rate limits
- Saves generated images locally and returns file path
- Proper error handling and validation

Usage:
    from openai_image_generation_tool import openai_image_generate_tool
    
    result = openai_image_generate_tool(
        prompt="A serene mountain landscape with cherry blossoms",
        aspect_ratio="landscape"
    )
"""

import json
import logging
import os
import time
from typing import Dict, Any, Optional
from urllib.parse import urlencode
import requests

from tools.debug_helpers import DebugSession

logger = logging.getLogger(__name__)

# Configuration
# Note: Using gpt-image-1 which is the current OpenAI image generation model
DEFAULT_MODEL = "gpt-image-1"
DEFAULT_QUALITY = "high"  # "high" or "medium" for gpt-image-1
DEFAULT_OUTPUT_FORMAT = "png"

# Aspect ratio mapping to dimensions
ASPECT_RATIO_DIMENSIONS = {
    "landscape": (1792, 1024),  # 16:9 wide
    "landscape_4_3": (1792, 1024),  # Maps to landscape
    "square": (1024, 1024),  # 1:1
    "square_hd": (1024, 1024),  # 1:1
    "portrait": (1024, 1792),  # 9:16 tall
    "portrait_4_3": (1024, 1792),  # Maps to portrait
}

VALID_ASPECT_RATIOS = list(ASPECT_RATIO_DIMENSIONS.keys())

_debug = DebugSession("openai_image_tools", env_var="OPENAI_IMAGE_TOOLS_DEBUG")


def check_openai_image_requirements() -> bool:
    """Check if OpenAI API key is available for image generation."""
    return bool(os.getenv("OPENAI_API_KEY"))


def _get_openai_api_key() -> str:
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
    return api_key


def _make_openai_request(
    prompt: str,
    width: int,
    height: int,
    quality: str = DEFAULT_QUALITY,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    max_retries: int = 3
) -> Dict[str, Any]:
    """Make request to OpenAI Images API for gpt-image-1."""
    api_key = _get_openai_api_key()
    base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    url = f"{base_url}/images/generations"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": DEFAULT_MODEL,
        "prompt": prompt,
        "size": f"{width}x{height}",
        "quality": quality,
        "n": 1
    }
    
    if _debug.active:
        _debug.log_call("openai_image_generate_request", {
            "url": url,
            "method": "POST",
            "headers": {k: v for k, v in headers.items() if k.lower() != "authorization"},
            "payload": payload
        })
    
    # Retry logic for rate limits
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=120)
            
            if _debug.active:
                _debug.log_call("openai_image_generate_response", {
                    "status_code": response.status_code,
                    "headers": dict(response.headers),
                    "body": response.text[:1000] if len(response.text) > 1000 else response.text
                })
            
            if response.status_code == 429:  # Rate limited
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # Exponential backoff
                    logger.warning(f"Rate limited, waiting {wait_time}s before retry...")
                    time.sleep(wait_time)
                    continue
            
            response.raise_for_status()
            
            data = response.json()
            
            if "data" in data and len(data["data"]) > 0:
                image_data = data["data"][0]
                
                # Handle base64 response (gpt-image-1 returns b64_json)
                if "b64_json" in image_data:
                    import base64
                    from pathlib import Path
                    
                    # Decode base64 and save to file
                    image_bytes = base64.b64decode(image_data["b64_json"])
                    
                    # Save to hermes home directory
                    hermes_home = os.path.expanduser("~/.hermes")
                    image_dir = Path(hermes_home) / "generated_images"
                    image_dir.mkdir(parents=True, exist_ok=True)
                    
                    filename = f"openai_image_{int(time.time())}.{output_format}"
                    filepath = image_dir / filename
                    
                    with open(filepath, "wb") as f:
                        f.write(image_bytes)
                    
                    # Return file:// URL
                    file_url = f"file://{filepath}"
                    
                    return {
                        "url": file_url,
                        "local_path": str(filepath),
                        "revised_prompt": image_data.get("revised_prompt", prompt),
                        "width": width,
                        "height": height,
                        "model": DEFAULT_MODEL,
                        "format": output_format
                    }
                elif "url" in image_data:
                    return {
                        "url": image_data.get("url"),
                        "revised_prompt": image_data.get("revised_prompt", prompt),
                        "width": width,
                        "height": height,
                        "model": DEFAULT_MODEL,
                        "format": output_format
                    }
                else:
                    raise ValueError(f"Unexpected image data format: {image_data}")
            else:
                raise ValueError(f"Unexpected response format: {data}")
                
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                logger.warning(f"Request failed (attempt {attempt + 1}), retrying: {e}")
                time.sleep(2 ** attempt)
                continue
            raise
    
    raise RuntimeError("Max retries exceeded")


def openai_image_generate_tool(
    prompt: str,
    aspect_ratio: str = "landscape",
    quality: str = DEFAULT_QUALITY,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    seed: Optional[int] = None
) -> str:
    """
    Generate an image using OpenAI's gpt-image-1 model.
    
    Args:
        prompt: The text prompt describing the desired image
        aspect_ratio: Aspect ratio ("landscape", "square", "portrait", etc.)
        quality: Image quality ("high" or "medium")
        output_format: Output format ("png", "jpeg", "webp")
        seed: Optional seed for reproducibility (not supported by gpt-image-1, ignored)
    
    Returns:
        JSON string with image file path and metadata
    """
    try:
        # Validate API key
        if not check_openai_image_requirements():
            return json.dumps({
                "error": "OPENAI_API_KEY not set. Set your OpenAI API key to use image generation."
            })
        
        # Validate aspect ratio
        if aspect_ratio not in VALID_ASPECT_RATIOS:
            return json.dumps({
                "error": f"Invalid aspect_ratio '{aspect_ratio}'. Must be one of: {VALID_ASPECT_RATIOS}"
            })
        
        # Get dimensions
        width, height = ASPECT_RATIO_DIMENSIONS[aspect_ratio]
        
        # Validate quality
        if quality not in ["high", "medium"]:
            return json.dumps({
                "error": "quality must be 'high' or 'medium'"
            })
        
        # Validate output format
        if output_format not in ["png", "jpeg", "webp"]:
            return json.dumps({
                "error": "output_format must be 'png', 'jpeg', or 'webp'"
            })
        
        logger.info(f"Generating image with {DEFAULT_MODEL}: {width}x{height}, quality={quality}")
        
        # Make request
        result = _make_openai_request(
            prompt=prompt,
            width=width,
            height=height,
            quality=quality,
            output_format=output_format
        )
        
        response = {
            "success": True,
            "image_url": result["url"],
            "revised_prompt": result["revised_prompt"],
            "width": result["width"],
            "height": result["height"],
            "model": result["model"],
            "format": result["format"],
            "aspect_ratio": aspect_ratio
        }
        
        if _debug.active:
            _debug.log_call("openai_image_generate_result", {"processed_result": response})
        
        return json.dumps(response, indent=2)
        
    except Exception as e:
        logger.error(f"Error generating image: {e}", exc_info=True)
        if _debug.active:
            _debug.log_call("openai_image_generate_error", {"error": str(e)})
        return json.dumps({
            "error": f"Image generation failed: {str(e)}"
        })


# ___LONG_STRING___
# Registry
# ___LONG_STRING___
from tools.registry import registry

OPENAI_IMAGE_GENERATE_SCHEMA = {
    "name": "openai_image_generate",
    "description": "Generate high-quality images from text prompts using OpenAI's gpt-image-1 model. Creates detailed, artistic images with excellent prompt adherence. Saves images locally to ~/.hermes/generated_images/ and returns the file path. Use this for social media visuals, marketing materials, or any image generation needs.",
    "parameters": {
        "type": "object",
        "properties": {
            "prompt": {
                "type": "string",
                "description": "The text prompt describing the desired image. Be detailed and descriptive for best results."
            },
            "aspect_ratio": {
                "type": "string",
                "enum": ["landscape", "landscape_4_3", "square", "square_hd", "portrait", "portrait_4_3"],
                "description": "The aspect ratio of the generated image. 'landscape' is 16:9 (1792x1024), 'square'/'square_hd' is 1:1 (1024x1024), 'portrait' is 9:16 (1024x1792).",
                "default": "landscape"
            },
            "quality": {
                "type": "string",
                "enum": ["high", "medium"],
                "description": "Image quality level. 'high' produces the best quality images with finer details. 'medium' is faster and cheaper.",
                "default": "high"
            },
            "output_format": {
                "type": "string",
                "enum": ["png", "jpeg", "webp"],
                "description": "Output image format. PNG is best for quality, JPEG for smaller files, WebP for modern web use.",
                "default": "png"
            }
        },
        "required": ["prompt"]
    }
}


def _handle_openai_image_generate(args, **kw):
    prompt = args.get("prompt", "")
    if not prompt:
        return json.dumps({"error": "prompt is required for image generation"})
    
    return openai_image_generate_tool(
        prompt=prompt,
        aspect_ratio=args.get("aspect_ratio", "landscape"),
        quality=args.get("quality", "high"),
        output_format=args.get("output_format", "png"),
        seed=None
    )


registry.register(
    name="openai_image_generate",
    toolset="image_gen",
    schema=OPENAI_IMAGE_GENERATE_SCHEMA,
    handler=_handle_openai_image_generate,
    check_fn=check_openai_image_requirements,
    requires_env=["OPENAI_API_KEY"],
    is_async=False,
    emoji="🎨",
)


if __name__ == "__main__":
    print("🎨 OpenAI gpt-image-1 Image Generation Tool")
    print()
    
    if not check_openai_image_requirements():
        print("❌ OPENAI_API_KEY not set")
        print("   Set your OpenAI API key: export OPENAI_API_KEY='sk-...'")
        exit(1)
    
    print("✅ OpenAI API key found")
    print(f"🤖 Using model: {DEFAULT_MODEL}")
    print()
    print("Supported aspect ratios:")
    for ratio, (w, h) in ASPECT_RATIO_DIMENSIONS.items():
        print(f"  - {ratio}: {w}x{h}")
    print()
    print("Usage:")
    print("  from openai_image_generation_tool import openai_image_generate_tool")
    print()
    print("  result = openai_image_generate_tool(")
    print("      prompt='A serene mountain landscape with cherry blossoms',")
    print("      aspect_ratio='landscape',")
    print("      quality='high'")
    print("  )")
