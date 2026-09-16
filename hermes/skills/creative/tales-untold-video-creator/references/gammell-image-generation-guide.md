# Stephen Gammell Style Image Generation Guide for Tales Untold

## Overview

Images for Tales Untold should look like they belong in **Scary Stories to Tell in the Dark** by Alvin Schwartz, illustrated by Stephen Gammell.

**CRITICAL:** Post-processing color images to look Gammell-style does NOT work. Images must be generated **natively** with Gammell-style prompts.

---

## Why Post-Processing Fails

| Approach | Result |
|----------|--------|
| Generate color → filter to grayscale | Looks like a filtered photo, not ink wash art |
| CSS filters (contrast, saturate) | Destroys detail, looks artificial |
| Grain overlays | Looks like digital noise, not textured paper |

**Gammell's aesthetic** comes from the generation process — ink bleeds, shadow pools, textured paper — not post-processing.

---

## Core Style Elements

### Medium
- India ink wash
- Charcoal and ink
- Pen and ink crosshatching
- Textured paper (cold press watercolor)
- Aged book page aesthetic

### Visual Characteristics

| Feature | Description |
|---------|-------------|
| **Lighting** | Deep black shadows, stark contrast, chiaroscuro |
| **Shadows** | Pool like liquid ink, bleed into edges, organic shapes |
| **Highlights** | Stark white, minimal midtones |
| **Texture** | Visible paper grain, ink bleeds, rough edges |
| **Line work** | Loose, expressive, sometimes sketchy |
| **Details** | Sparse but unsettling — suggestion over definition |

### Mood
- Grotesque but not gory
- Surreal, dreamlike quality
- Uncanny — familiar but wrong
- Nightmare logic
- 1980s children's horror nostalgia

---

## Complete Scene Prompts (10 Scenes)

### Scene 1: Introduction (Safe World)
```
A person sleeping peacefully in bed, moonlight through window, 
Stephen Gammell ink wash illustration style, deep black shadows 
pooling like liquid ink in corners, face calm in sleep, textured 
aged book paper, gentle but ominous mood, surreal horror aesthetic, 
monochrome grayscale, high contrast --ar 9:16
```

**Negative:** color, bright lighting, digital art, smooth shading, 3D render, photograph, cartoon, anime, CGI, vibrant colors, saturated

---

### Scene 2: First Unease
```
A smartphone face down on a nightstand in darkness, Stephen Gammell 
style, red recording light glowing like an eye, deep ink shadows 
pooling around it, textured aged book paper, uncanny atmosphere, 
monochrome ink wash --ar 9:16
```

---

### Scene 3: The Turn (Horror Begins)
```
A pale figure sitting up in bed in darkness, Stephen Gammell ink 
wash illustration, face illuminated by phone glow, hollow eyes, 
mouth open in silent speech, deep black shadows, ink texture, 
grotesque surreal horror, monochrome, high contrast --ar 9:16
```

---

### Scene 4: Escalation
```
A shadowy figure standing at the foot of the bed, Stephen Gammell 
illustration style, indistinct human shape, darkness bleeding from 
form, textured aged paper, uncanny atmosphere, monochrome ink wash 
--ar 9:16
```

---

### Scene 5: Technological Dread
```
A phone screen glowing in darkness showing audio waveforms, Stephen 
Gammell style, shadowy reflection in screen, something behind viewer, 
textured paper, surreal horror, monochrome --ar 9:16
```

---

### Scene 6: Corner Horror
```
A corner of the room where shadows collect, Stephen Gammell ink wash, 
something emerging from the darkness, form barely visible, textured 
aged paper, surreal nightmare quality, monochrome --ar 9:16
```

---

### Scene 7: Absence
```
A bed with rumpled sheets, empty, Stephen Gammell style, impression 
of where someone lay, shadow hand reaching from under bed, textured 
paper, grotesque horror, monochrome --ar 9:16
```

---

### Scene 8: Threshold
```
A doorway with darkness beyond, Stephen Gammell illustration, 
silhouette in door, shadow bleeding into room, textured aged paper, 
threshold horror, monochrome --ar 9:16
```

---

### Scene 9: Being Watched
```
A ceiling viewed from below in bed, Stephen Gammell style, shadow 
pooling above, impression of face in plaster, textured paper, 
being watched from above, monochrome --ar 9:16
```

---

### Scene 10: Climax
```
An empty bed in moonlit room, Stephen Gammell ink wash, shadow 
standing beside bed watching, almost invisible, textured aged 
paper, the watcher revealed, monochrome --ar 9:16
```

---

## Universal Negative Prompt

Always include with generation:

```
color, colorful, bright lighting, clean lines, digital art, smooth 
shading, 3D render, photograph, realistic, modern, clean, cheerful, 
cute, cartoon, CGI, anime, manga, vibrant colors, saturated, photographic, 
hyperrealistic
```

---

## Post-Render Treatment (HyperFrames)

Once native Gammell images are generated, apply these in HyperFrames:

### Vignette
```css
.vignette {
  background: radial-gradient(
    ellipse at 50% 38%,
    transparent 0%,
    transparent 10%,
    rgba(10,10,10,0.4) 30%,
    rgba(10,10,10,0.85) 70%,
    rgba(5,5,5,0.98) 100%
  );
}
```

### Typography
```css
.caption {
  font-family: Georgia, 'Times New Roman', serif;
  font-style: italic;
  color: #e8e6e3; /* Off-white, not pure white */
}
```

### Ken Burns
- Slower motion: 8.13s per scene
- Smaller scale range: 1.05× → 1.18× (not 1.24×)
- More deliberate, ominous feel

---

## Image Generation Services

| Service | Status | Notes |
|---------|--------|-------|
| **FAL/Flux** | ⚠️ Requires auth | Best adherence to complex prompts |
| **OpenAI GPT-Image** | ⚠️ Rate limited | May hit 429 errors |
| **POYO/ElevenLabs** | ❌ No image gen | TTS only |
| **Midjourney** | ✅ Web only | Generate manually, download |
| **DALL-E (web)** | ✅ Web only | Generate manually, download |

**Fallback:** If API generation fails, user must generate images manually via Midjourney/DALL-E web interface using the prompts above.

---

## Verification Checklist

After generating images, verify:
- [ ] Grayscale/monochrome (no color tints)
- [ ] High contrast (deep blacks, bright whites)
- [ ] Textured appearance (not smooth digital)
- [ ] Shadow pools like liquid ink
- [ ] Uncanny, surreal quality
- [ ] Looks like book illustration, not photo

If any check fails, the image is NOT Gammell-style — regenerate with stronger prompt emphasis.
