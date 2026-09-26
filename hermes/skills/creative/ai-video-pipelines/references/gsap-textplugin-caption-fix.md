# GSAP TextPlugin for HyperFrames Captions

## Problem
When using GSAP to animate text captions with `tl.to(el, {text: "..."})`, the caption text never appears on screen if `gsap/TextPlugin` is not loaded and registered.

**Symptom in render logs:**
```
[Browser:WARN] Invalid property text set to "My caption text here" Missing plugin? gsap.registerPlugin()
```

The video renders successfully and the audio plays, but the on-screen text overlay is completely absent. This is a silent failure.

## Fix
Add after the GSAP core script:
```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/TextPlugin.min.js"></script>
<script>gsap.registerPlugin(TextPlugin);</script>
```

## Production Discovery (Tales Untold, 2026-09-24)
Pipeline scripts (`run_folklore_spielberg.py`, `batch_folklore_producer.py`, etc.) only loaded `gsap.min.js`. TextPlugin was never loaded, so all caption text animations silently failed. Videos rendered but had no on-screen text. Discovered when subagent render logs showed the `Missing plugin? gsap.registerPlugin()` warning.

## Verification
Check render output for `Loaded plugins: [TextPlugin]`. Do NOT rely on "render succeeded" as a signal captions work.
