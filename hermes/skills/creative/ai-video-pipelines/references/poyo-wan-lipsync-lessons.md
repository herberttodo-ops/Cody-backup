# POYO Wan 3.0 + lip sync lessons (Nov 2026)

- Wan IDs: wan3.0-prime-{text,image,reference}-to-video. Guessed slugs 404. Docs index: https://docs.poyo.ai/llms.txt
- gpt-image-2 size must be "9:16" (not "1024x1536"); image_urls keeps characters consistent.
- Balance: GET https://api.poyo.ai/api/user/balance (1 credit = $0.005). Check before batches. 402/503 = credits, not content.
- Content filter blocks broken-anatomy beats (backward feet, bent ankle) even when framed as a deliberate effect. Use face beats instead.
- i2v from a locked character keyframe keeps faces consistent; text-to-video invents new faces. Add "static locked-off camera, subject frozen" to stop Wan undoing planted wrongness.
- Lip sync: Wan has no speech mode. kling-avatar-2.0/standard ($0.035/s, audio 2-60s) and omnihuman-2.0 ($0.105/s, audio >=4s) take image_urls[0] + audio_url. Pad short lines with silence. audio_url must be public: POYO upload takes images/video only; Google Drive anyone-with-link (uc?export=download&id=) worked.
- Story: confusing without a narrator. Add first-person VO in shots 1-2, two-shots between dialogue, show entrances, match VO to picture.
- Review your own cut with 3 frames per shot at readable size plus Whisper on the audio; say what you could not judge.
