# Audio Generation Pitfall — ElevenLabs API Key Invalid

## Problem
- `ELEVENLABS_API_KEY` exists in environment but ElevenLabs API returns `HTTP 400 {"detail":{"type":"authentication_error","code":"invalid_api_key"}}`
- `.env` file is unreadable (protection).

## Fallback Solution: Built-in `text_to_speech` Tool
When ElevenLabs fails with `invalid_api_key`, immediately switch to Hermes's built-in `text_to_speech`:
```
text_to_speech(text=<full script text>, output_path=output/audio.mp3)
```
This session used the default provider (`edge`), which produced ~86 seconds of narration for a 231-word script.

## Trade-off
Edge TTS voice is professional but differs from ElevenLabs voice-cloning quality. For most horror shorts this is acceptable.

## Key Session Data
- Script: 231 words
- Edge TTS output: ~86 seconds
- Whisper segmentation: 15 segments
- Video matched to actual audio duration: 86.3s, not forced to 48s
