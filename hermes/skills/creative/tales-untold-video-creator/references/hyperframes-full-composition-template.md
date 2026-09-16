## HyperFrames — Full Tales Untold Production Composition

### What Changed in This Session

- Full 10-scene, 81.3s HTML composition rendered cleanly (2,439 frames, 79MB, no errors)
- Duration inferred from GSAP timeline — no `--duration` CLI flag exists
- All 20 captions from Whisper transcript mapped to timed GSAP animations

---

### Key Discovery: No `--duration` Flag

HyperFrames CLI **does not accept a `--duration` flag**. Duration is computed automatically from the end of the GSAP timeline. Make sure `window.__timelines[0]` covers the full desired duration.

### Complete Single-File Composition Template

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=1080, height=1920">
  <title>Tales Untold</title>
  <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      width: 1080px; height: 1920px;
      background: #030303; overflow: hidden;
      position: relative;
      font-family: 'DejaVu Sans', 'Arial Black', Arial, sans-serif;
    }
    .scene {
      position: absolute; inset: 0;
      display: flex; align-items: center; justify-content: center;
      opacity: 0; overflow: hidden;
    }
    .scene img {
      position: absolute;
      min-width: 125%; min-height: 125%;
      object-fit: cover; will-change: transform;
    }
    .caption {
      position: absolute; bottom: 220px; left: 50%;
      transform: translateX(-50%);
      width: 94%; text-align: center;
      color: #fff; font-size: 52px; font-weight: bold;
      line-height: 1.4;
      text-shadow:
        -4px -4px 0 #000, 4px -4px 0 #000,
        -4px 4px 0 #000, 4px 4px 0 #000,
        -2px 0 0 #000, 2px 0 0 #000,
        0 -2px 0 #000, 0 2px 0 #000,
        0 4px 18px rgba(0,0,0,0.85);
      z-index: 10; opacity: 0; pointer-events: none;
    }
    .caption.horror { color: #ff2a2a; }
    .vignette {
      position: absolute; inset: 0;
      background: radial-gradient(ellipse at 50% 42%, transparent 30%, rgba(0,0,0,0.80) 100%);
      z-index: 5; pointer-events: none;
    }
    .grain {
      position: absolute; inset: 0;
      opacity: 0.055;
      background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='256' height='256'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
      z-index: 6; pointer-events: none;
    }
  </style>
</head>
<body>
  <!-- 10 scenes -->
  <div class="scene" id="s1"><img src="./scene1.png"></div>
  <div class="scene" id="s2"><img src="./scene2.png"></div>
  <!-- ... s3-s10 -->

  <!-- 20 captions -->
  <div class="caption" id="c0">I've always been a heavy sleeper.</div>
  <div class="caption horror" id="c1">The voice on the recording was not mine.</div>
  <!-- ... c2-c19 -->

  <div class="vignette"></div>
  <div class="grain"></div>

  <script>
    const tl = gsap.timeline({ paused: true });
    window.__timelines = [tl];
    const SD = 8.13;  // scene duration = audio_dur / 10

    // Scene 1
    tl.to('#s1', { opacity: 1, duration: 0.4 }, 0);
    tl.fromTo('#s1 img', { scale: 1.08, x: 0 }, { scale: 1.24, x: -50, duration: SD, ease: 'none' }, 0);

    // Scene 2 (crossfade)
    tl.to('#s2', { opacity: 1, duration: 0.5 }, SD - 0.4);
    tl.fromTo('#s2 img', { scale: 1.20, x: 40 }, { scale: 1.00, x: -30, duration: SD, ease: 'none' }, SD);
    tl.to('#s1', { opacity: 0, duration: 0.5 }, SD + 0.3);

    // ... repeat for scenes 3-10

    // Captions (from Whisper transcript)
    tl.to('#c0', { opacity: 1, duration: 0.25 }, 0.8);
    tl.to('#c0', { opacity: 0, duration: 0.3 }, 7.0);
    // ... repeat for all segments
  </script>
</body>
</html>
```

### Render Command

```bash
npx hyperframes render --composition composition.html --format mp4 \
  --fps 30 --quality looks --output tales_visual_hf.mp4 --quiet
```

### Performance Reference

| Metric | Value |
|---|---|
| 81.3s, 30fps, 1080×1920 | ~2.5 min render time |
| Output size | ~79MB (quality=looks, CRF 16) |
| Workers | Auto (1 on this machine) |
| Memory | ~400MB peak |

### Hybrid Assembly

The HyperFrames output has **no audio**. Add in MoviePy:
1. Load `tales_visual_hf.mp4` as video track
2. Load Adam voice narration + background music
3. `CompositeAudioClip([voice, music_with_volume(0.6)])`
4. `video.with_audio(final_audio).write_videofile(...)`
