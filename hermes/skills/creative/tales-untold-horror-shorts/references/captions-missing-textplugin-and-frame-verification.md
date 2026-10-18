# Captions silently missing: GSAP TextPlugin (found Oct 2026)

## Symptom
Published Shorts have no on-screen captions even though the pipeline log says PIPELINE COMPLETE and the
composition HTML contains a caption element and timeline code.

## Cause
The caption code uses `tl.to(captionEl, {text: cap.text, ...})`. The `text` property is provided by GSAP
**TextPlugin**. pipeline_v3.py `build_html()` loaded only gsap.min.js, so the tween ran but wrote nothing.
scripts/auto_producer.py already loaded it, but the live cron path is tales_v3_producer_v3.1.sh -> pipeline_v3.py.

## Fix
In the `<head>` after gsap.min.js add:
`<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/TextPlugin.min.js"></script>`
`<script>gsap.registerPlugin(TextPlugin);</script>`
Quick check: `grep -c TextPlugin hyperframes-test/composition_<name>.html` must be >= 1.

## Verify with real frames (do this after any pipeline change)
1. `ffmpeg -ss T -i output/FINAL_x.mp4 -frames:v 1 -vf "crop=iw:ih*0.35:0:ih*0.55,scale=300:-1" out_T.png` for
   several T inside narration.
2. Tile with PIL into one grid image, then view it. White all-caps text in the bottom third = OK.
3. A test render of the composition at `--quality draft` is enough to prove the fix without a full run.
Oct 2026 finding: Oct 14-16 renders (banshee, dracula, siguanaba, skinwalker, taniwha) had no TextPlugin; the
older 33_mothman_bridge render did and showed captions. Whether Oct 1-13 and the Jan batch had captions was not
checked.

## Tooling note
Very large inline shell heredocs get blocked by the command guard; split into short commands or write a script file.
