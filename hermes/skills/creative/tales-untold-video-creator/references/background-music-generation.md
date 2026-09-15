# Background Music Generation

## User Requirement
Dark ambient horror music mixed underneath narration at background level.

## Technique

### Option 1: Generate with AudioCraft/MusicGen (if available)
```python
from audiocraft.models import MusicGen
from audiocraft.data.audio import audio_write

model = MusicGen.get_pretrained('facebook/musicgen-small')
model.set_generation_params(duration=88)  # Match video duration

descriptions = ["dark ambient horror, tension, atmospheric drone, no melody"]
wav = model.generate(descriptions)

# Save at proper volume
import torch
wav = wav[0] * 0.12  # -20dB approx = 12% volume
audio_write('background_music', wav.cpu(), model.sample_rate)
```

### Option 2: Procedural Generation (reliable)
```python
import numpy as np
from scipy.io.wavfile import write

def generate_dark_ambient(duration=88, sample_rate=44100):
    """Generate procedural dark ambient drone."""
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Layer 1: Deep sub-bass drone (50-100 Hz)
    drone1 = np.sin(2 * np.pi * 60 * t) * 0.3
    drone2 = np.sin(2 * np.pi * 80 * t) * 0.2
    
    # Layer 2: Low frequency oscillation (LFO) for movement
    lfo = np.sin(2 * np.pi * 0.1 * t)  # 0.1 Hz = slow movement
    drone1 *= (0.8 + 0.2 * lfo)
    
    # Layer 3: Dark noise texture
    noise = np.random.randn(len(t)) * 0.05
    
    # Layer 4: Distant tension tones (200-400 Hz, sparse)
    tension = np.zeros_like(t)
    for freq in [220, 330, 440]:
        envelope = np.sin(2 * np.pi * 0.05 * t) ** 2  # Slow swell
        tension += np.sin(2 * np.pi * freq * t) * envelope * 0.1
    
    # Combine layers
    audio = drone1 + drone2 + noise + tension
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.12  # -20dB level
    
    # Convert to 16-bit PCM
    audio = (audio * 32767).astype(np.int16)
    
    write('background_music.wav', sample_rate, audio)
    return 'background_music.wav'

generate_dark_ambient(88)
```

### Option 3: Download from FreeSound (requires API key)
```bash
# Search for "dark ambient drone horror"
# Download and trim to video duration
# Mix at -20dB
```

## Mixing with MoviePy

```python
from moviepy import CompositeAudioClip, AudioFileClip

voice = AudioFileClip("audio.mp3")  # Narration
music = AudioFileClip("background_music.wav")

# Loop music to match voice duration if needed
if music.duration < voice.duration:
    music = music.loop(duration=voice.duration)
else:
    music = music.with_duration(voice.duration)

# Mix: voice at full, music at background level
final_audio = CompositeAudioClip([voice, music])

# Or use volume adjustment
final_audio = CompositeAudioClip([
    voice,
    music.with_volume(0.12)  # 12% = ~-20dB
])

# Apply to video
final_video = video.with_audio(final_audio)
```

## Volume Guidelines

| Element | Level | Notes |
|---------|-------|-------|
| Voice narration | -3dB (70%) | Primary, must be clear |
| Background music | -20dB (10-12%) | Atmosphere, not competing |
| Combined | -1dB peak | Prevent clipping |

## Verification
```bash
# Check audio has two distinct layers
ffprobe -i FINAL_TALES_UNTOLD_SHORT.mp4 -show_streams -select_streams a

# Extract audio and visualize
ffmpeg -i FINAL_TALES_UNTOLD_SHORT.mp4 -vn -acodec pcm_s16le audio.wav
# Open in audio editor - should see voice + low-level background
```