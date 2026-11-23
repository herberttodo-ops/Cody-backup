# POYO Wan 3.0 Prime lessons (Nov 2026)

- Model IDs: wan3.0-prime-text-to-video / -image-to-video / -reference-to-video. Guessed slugs 404.
- gpt-image-2: input.size must be an aspect string like "9:16"; "1024x1536" is rejected. It accepts input.image_urls as character references, which keeps faces consistent. Text-to-video alone invents a new face per clip.
- Wan normalizes wrong anatomy in motion. Keep a frozen subject: "feet stay exactly as they are, no walking, locked-off camera, very slow push in". A prompt describing a limb bending was rejected by the content filter.
- Download POYO CDN files with curl -sL (urllib gets 403).
- Long batches: terminal(background=true, notify_on_complete=true), resumable per-file caching; execute_code dies at 300s.
- Catch transient poll timeouts and keep polling. Treat HTTP 402/503 insufficient credits as a hard stop, not a content rejection.
- Female leads: Cedric voice is male; Rachel 21m00Tcm4TlvDq8ikWAM, Bella EXAVITQu4vr4xnSDxMaL work via elevenlabs-tts-turbo-2-5.
