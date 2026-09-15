# Ken Burns Effect Implementation

## User Requirement
Every scene MUST have subtle motion - no static images. This creates visual interest and professional polish.

## Technique

```python
from moviepy import *
import numpy as np

def apply_ken_burns(image_array, duration, variation='zoom_in'):
    """
    Apply subtle motion to static images.
    
    Variations:
    - 'zoom_in': 1.0 -> 1.15 over duration
    - 'zoom_out': 1.15 -> 1.0 over duration  
    - 'pan_left': image moves right to left
    - 'pan_right': image moves left to right
    - 'pan_up': image moves down to up
    - 'pan_down': image moves up to down
    """
    img_clip = ImageClip(image_array).with_duration(duration)
    w, h = img_clip.size  # 1080, 1920
    
    def zoom_in(t):
        scale = 1.0 + 0.15 * (t / duration)
        return img_clip.resized(scale)
    
    def zoom_out(t):
        scale = 1.15 - 0.15 * (t / duration)
        return img_clip.resized(scale)
    
    def pan_left(t):
        # Start with image shifted right, end shifted left
        shift = int(50 * (1 - 2 * (t / duration)))
        return img_clip.with_position((shift, 'center'))
    
    def pan_right(t):
        shift = int(50 * (2 * (t / duration) - 1))
        return img_clip.with_position((shift, 'center'))
    
    # Create clip with effect
    if variation == 'zoom_in':
        return img_clip.resized(lambda t: 1 + 0.15 * (t / duration))
    elif variation == 'zoom_out':
        return img_clip.resized(lambda t: 1.15 - 0.15 * (t / duration))
    elif variation == 'pan_left':
        return img_clip.with_position(lambda t: (50 - 100 * (t / duration), 'center'))
    elif variation == 'pan_right':
        return img_clip.with_position(lambda t: (-50 + 100 * (t / duration), 'center'))
    else:
        return img_clip.resized(lambda t: 1 + 0.15 * (t / duration))

# Rotate through variations for visual interest
ken_burns_variations = [
    'zoom_in',      # Scene 1
    'pan_left',     # Scene 2
    'zoom_in',      # Scene 3
    'pan_right',    # Scene 4
    'zoom_in',      # Scene 5
    'pan_left',     # Scene 6
    'zoom_out',     # Scene 7
    'pan_right',    # Scene 8
    'zoom_in',      # Scene 9
    'pan_left',     # Scene 10
]
```

## Verification
Check that images are actually moving:
```bash
# Extract frames at different timestamps
ffmpeg -ss 0.5 -i video.mp4 -vframes 1 frame_start.jpg
ffmpeg -ss 5.0 -i video.mp4 -vframes 1 frame_end.jpg

# Calculate pixel difference (should be > 0 for motion)
# In Python:
from PIL import Image
import numpy as np

img1 = np.array(Image.open('frame_start.jpg'))
img2 = np.array(Image.open('frame_end.jpg'))
diff = np.mean(np.abs(img1.astype(float) - img2.astype(float)))
print(f"Pixel difference: {diff}")  # Should be > 5.0 for visible motion
```