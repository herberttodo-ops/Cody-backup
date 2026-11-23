---
name: poyo-ai-video-production
description: "Use for AI video on POYO: Wan 3.0, lip sync, keyframes."
---

# POYO AI Video Production

Class-level notes for building short vertical dramas/horror shorts on POYO (api.poyo.ai). Complements `wan-short-drama-studio` (user-owned; its Wan 2.1 section is outdated, recommend `hermes curator adopt wan-short-drama-studio` then merge this in).

## API basics (verified Nov 2026)
- Submit `POST https://api.poyo.ai/api/generate/submit` body `{"model":..., "input":{...}}`; poll `GET /api/generate/status/{task_id}`; `data.status` finished/failed, files at `data.files[0].file_url`. Check body `code == 200`, not just HTTP.
- Key: `POYO_API_KEY` in `~/.openclaw/workspace/tales-untold/.env`. Never print it.
- Balance: `GET /api/user/balance` -> `data.credits_amount`. 1 credit = $0.005. Check before any batch and diff after.
- Model slugs cannot be guessed (`wan-3-0-*`, `wan-2-1-*` all 404). Read https://docs.poyo.ai/llms.txt and https://poyo.ai/models/<slug>.
- Ready client: `~/.openclaw/workspace/tales-untold/poyo_wan_client.py` (`submit_wan_video`, `poll_wan_task`, `generate_wan_video`); polling must tolerate transient timeouts (patched).

## Models
- Wan 3.0 Prime: `wan3.0-prime-text-to-video`, `wan3.0-prime-image-to-video` (`image_urls`), `wan3.0-prime-reference-to-video`. Params resolution 480p/720p/1080p, duration 2-30 int, aspect_ratio incl 9:16, audio bool. Sale (to 2026-11-30): 480p $0.048/s, 720p $0.098/s, 1080p $0.196/s. A 3s 480p clip finishes in ~30-60s.
- Keyframes: `gpt-image-2`, input `{"prompt","size":"9:16","image_urls":[refs]}`. `1024x1536` is rejected (needs 2K/4K). ~1-2 min per image; run in parallel.
- TTS: `elevenlabs-tts-turbo-2-5` input `{"voice":<id>,"text"}`. Female: Rachel `21m00Tcm4TlvDq8ikWAM`, Bella `EXAVITQu4vr4xnSDxMaL`. Cedric `BQOei2tk6QCBMHQWPhbj` is male (Tales Untold narrator only).
- Lip sync: `kling-avatar-2.0/standard` ($0.035/s; input `image_urls`[1], `audio_url` 2-60s <=5MB, `prompt`). `omnihuman-2.0` $0.105/s, audio >=4s. Kling chosen by user as better. HeyGen Avatar 6 Turbo also exists (~$0.05/s), untested.
- POYO file upload accepts images/video only. For `audio_url`, host the mp3 on Google Drive (permission anyone/reader, `https://drive.google.com/uc?export=download&id=<id>`); works. Tales Untold Bunny zone gave 401.

## Consistency and filters
- Text-to-video re-invents faces each shot. Make one reference portrait per character plus the set piece, then every keyframe uses `image_urls=[refs]`; animate with i2v. Put full wardrobe in every keyframe prompt (outfits drift otherwise). Add "Full-frame image, no letterbox, no black bars".
- POYO content filter rejects explicit body horror (backward feet, bent ankle) even when called a deliberate effect; Wan also normalizes odd anatomy once moving. Use faces, held unblinking stares, head tilts, fog, doorways.
- HTTP 402/503 "insufficient credits" is not a content rejection; never auto-fallback on it (a build script once logged it as "filtered").

## Story/edit lessons (user found v1/v2 confusing)
- No narrator + sparse lines = confusing. Add first-person VO that sets who/where/why; keep VO consistent with picture.
- Keep both characters in shared frames; show entrances/exits; no line over a contradicting shot.
- Keep the user's exact style words (Cinematic = live-action film grammar, not illustration).

## Build/review method
- Long runs: write a resumable script (cache per-shot files), launch with terminal background=true + notify_on_complete. execute_code dies at 300s; foreground terminal caps 600s. Large inline heredoc commands can be blocked by the parser: write the script with write_file first.
- Assemble: concat clips, scale 720x1280, mix per-line audio with `adelay`, burn ASS captions (VO italic), mux.
- Self-review before sending: 3 frames per shot (15/50/85%) at ~240px, two shots per contact sheet, plus Whisper on the final audio to confirm every line. Single thumbnails hid real defects. State what you could not judge (voices, motion).
- Report cost honestly from balance diff; deliver via Telegram MEDIA: path and upload to Drive folder "Wan Tests - The Chicken Legs" when asked.
