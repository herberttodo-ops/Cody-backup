# Wan 3.0 Prime on POYO: production lessons (Nov 2026)

- Model IDs: wan3.0-prime-text-to-video / -image-to-video / -reference-to-video. Guessed slugs 404; take IDs from the docs page.
- Keyframes: gpt-image-2 with size "9:16" (1024x1536 is rejected); image_urls=[ref] conditions on a character reference.
- Text-to-video gives a new face every shot; use one reference portrait per character, then i2v from conditioned keyframes.
- i2v normalizes anatomy; hold wrong poses with "static locked-off camera, very slow push in, subject frozen, no walking".
- POYO content filter rejects explicit body horror (twisted feet, bent ankle) even when labelled a deliberate effect; imply via tracks, reactions, silhouettes.
- 402/503 "insufficient credits" = top up; "does not comply with platform regulations" = content filter. Do not conflate them in logs/fallbacks.
- Download cdn.doculator.org files with curl (urllib gets 403).
- execute_code caps at 300s: run long builds with terminal(background=true, notify_on_complete=true); make polling tolerate transient read timeouts; make builds resumable.
- Dialogue-only scripts confuse viewers: add first-person VO, set up relationships in shot 1, show entrances/exits, match each line to its picture.
- State honestly when review was from stills only (motion/audio unreviewed).
