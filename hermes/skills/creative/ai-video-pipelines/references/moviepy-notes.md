# MoviePy Video Assembly Notes

Session: 2026-09-13 (Tales Untold video rebuild)

## TextClip API Syntax

**Newer MoviePy versions use different parameter names:**

```python
# ❌ Old syntax (may not work)
txt = TextClip(
    txt="Hello",           # Wrong param name
    fontsize=56,           # Wrong param name
    font='Arial',
    color='white'
)

# ✅ Correct syntax
from moviepy import TextClip
txt = TextClip(
    text="Hello",          # Use 'text' not 'txt'
    font_size=56,          # Use 'font_size' not 'fontsize'
    font='Arial',
    color='white'
)
```

## Font Discovery

**System fonts may not be available by name:**

```bash
# List available fonts
fc-list | grep -i sans | head -10

# Common system fonts (use absolute paths)
/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
/usr/share/fonts/truetype/freefont/FreeSans.ttf
/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf
```

## Image Cropping for 9:16 Shorts

```python
from PIL import Image

def crop_to_9x16(img_path, output_path, target_w=1080, target_h=1920):
    """Crop and resize image to 9:16 aspect ratio."""
    img = Image.open(img_path)
    w, h = img.size
    
    if w/h > target_w/target_h:  # Too wide
        new_w = int(h * target_w / target_h)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:  # Too tall
        new_h = int(w * target_h / target_w)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    
    img = img.resize((target_w, target_h), Image.LANCZOS)
    img.save(output_path)
```

## Scene Timing for Text Sync

Always calculate text timing from the narration script, not estimated durations.

## Pitfalls

- **Font not found:** System fonts vary. Check with `fc-list` or use absolute paths.
- **API changed:** `txt` → `text`, `fontsize` → `font_size` in newer versions.
- **Text cut off:** Position text higher on screen (y=1400 for 1920px height).
- **Text sync:** Match text appearance to actual narration timing.
- **Black gaps:** Ensure image durations sum to total audio duration.
