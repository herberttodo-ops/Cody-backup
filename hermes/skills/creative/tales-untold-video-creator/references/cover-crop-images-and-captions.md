## Image Sizing: Cover-Crop (Prevent Vertical Stretch)

### Problem
MoviePy `ImageClip.resized(new_size=RESOLUTION)` force-stretches images to exactly 1080×1920. A 1024×768 source becomes visibly tall/squished — faces and objects lose proper proportions.

### Solution: Cover-Crop with Pillow
```python
from PIL import Image

def cover_crop(image_path, target_size=(1080, 1920)):
    tw, th = target_size
    img = Image.open(image_path)
    iw, ih = img.size
    
    scale = max(th / ih, tw / iw)   # scale to cover both dims
    new_w, new_h = int(iw * scale), int(ih * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    
    left = (new_w - tw) // 2        # center crop
    top  = (new_h - th) // 2
    return resized.crop((left, top, left + tw, top + th))

# Generate cover-cropped images, then pass to ImageClip
for i in range(1, 11):
    cover_crop(f"scene{i}.png", (1080, 1920)).save(f"scene{i}_cover.png")
```

### Result
- Original aspect ratio preserved within crop region
- No vertical/horizontal stretch distortion
- Center of frame retained as default focal point

## Caption Layout: Auto-Height + Sentence Splitting

### Problem 1: Sentences Breaking Across Lines
MoviePy `TextClip` with `method="caption"` wraps at a width boundary, splitting sentences. A period can end up alone on the next line.

### Fix: Sentence-Split Timing
```python
import re

def split_into_sentences(segments):
    captions = []
    for seg in segments:
        start, end, text = seg["start"], seg["end"], seg["text"].strip()
        if not text:
            continue
        parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', text) if p.strip()]
        total_chars = sum(len(p) for p in parts) or 1
        seg_dur = end - start
        t = start
        for p in parts:
            p_dur = seg_dur * (len(p) / total_chars)
            captions.append({"start": t, "end": t + p_dur, "text": p})
            t += p_dur
    return captions
```
Each complete sentence renders as one timed caption unit.

### Problem 2: Text Clipped at Bottom
Fixing height with `size=(width, 200)` clips multi-line captions. Auto-height via `size=(width, None)` lets captions grow but still risks bottom-edge cutoff if anchored at a fixed y.

### Fix: Bottom-Anchored Position + Auto-Height
```python
txt = TextClip(
    text=c["text"],
    font="DejaVuSans-Bold",
    font_size=58,
    color="white",
    stroke_color="black",
    stroke_width=5,
    size=(1000, None),          # auto-height: never clips vertically
    method="caption",
    text_align="center",
)
# Anchor to bottom of frame with safe margin:
txt = txt.with_position(("center", 1920 - 250))  # 250px from bottom
```
