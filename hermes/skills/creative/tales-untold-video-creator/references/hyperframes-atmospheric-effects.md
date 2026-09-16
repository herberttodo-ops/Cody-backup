# HyperFrames Atmospheric Effects — Lessons Learned

## Grain Effects

### Static Grain (Basic)
```css
.grain {
  position: absolute; inset: 0;
  opacity: 0.22;  /* Start here — visible but not overwhelming */
  background-image: url("data:image/svg+xml,...feTurbulence...");
  z-index: 6;
  pointer-events: none;
}
```

**Opacity guidance:**
- 0.055 (5.5%) = Invisible — user couldn't see it
- 0.38 (38%) = Too heavy — user said "too much"
- 0.22 (22%) = Good balance — visible texture without distraction

### Animated Grain (Cinematic)
```javascript
// Rapid position shifts + opacity pulsing
const tl = gsap.timeline({ paused: true });

// Position jitter every 2 frames
for (let i = 0; i < duration * 15; i++) {
  const x = (Math.random() - 0.5) * 20;
  const y = (Math.random() - 0.5) * 20;
  tl.to('#grain', { x, y, duration: 0.067, ease: 'steps(1)' }, i * 0.067);
}

// Opacity pulsing
tl.fromTo('#grain', 
  { opacity: 0.18 }, 
  { opacity: 0.26, duration: 0.1, repeat: 810, yoyo: true, ease: 'steps(1)' }, 
  0
);
```

**Tradeoff:** Animated grain increases file size significantly (79MB → 241MB for 81s video).

---

## Vignette

### Standard (Subtle)
```css
.vignette {
  background: radial-gradient(
    ellipse at 50% 42%,
    transparent 30%,
    rgba(0,0,0,0.80) 100%
  );
}
```

### Heavy (Gammell/Horror)
```css
.vignette {
  background: radial-gradient(
    ellipse at 50% 40%,
    transparent 0%,
    transparent 8%,
    rgba(0,0,0,0.6) 35%,
    rgba(0,0,0,0.95) 70%,
    rgba(0,0,0,0.98) 100%
  );
}
```

**User preference:** Heavy vignette for horror — dark corners create unease.

---

## Gammell Style (Stephen Gammell / Scary Stories)

**User direction:** "Artwork should look like Scary Stories to Tell in the Dark — Stephen Gammell"

### Key Characteristics
- **NO grain** — clean ink wash aesthetic
- **Grayscale** — `filter: grayscale(100%)` on scenes
- **High contrast** — images get `contrast(1.4) brightness(0.85)`
- **Serif typography** — Georgia or Times, italic style
- **Ominous motion** — slower Ken Burns (scale 1.05→1.18 vs 1.08→1.24)

### CSS Implementation
```css
.scene {
  filter: grayscale(100%);
}
.scene img {
  filter: contrast(1.4) brightness(0.85) saturate(0);
}
.caption {
  font-family: Georgia, 'Times New Roman', serif;
  font-style: italic;
  font-size: 48px;
  color: #e8e6e3; /* warm off-white */
}
.caption.horror {
  color: #c9c7c4;
  font-weight: bold;
}
```

### Optional Enhancements
- **Ink texture overlay** — subtle fractal noise in multiply blend mode
- **Smudge marks** — corner shadows like aged paper
- **Paper texture** — subtle horizontal lines

---

## User Preference Summary

| Element | Current Preference |
|---------|-------------------|
| Grain | **None** — removed entirely for Gammell style |
| Vignette | **Heavy** — 98% black corners |
| Color | **Grayscale** |
| Font | **Serif, italic** (not bold sans-serif) |
| Motion | **Slower, more deliberate** Ken Burns |
| Style target | **Stephen Gammell ink illustrations** |
