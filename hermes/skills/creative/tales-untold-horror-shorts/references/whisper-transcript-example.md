# Whisper Transcript Example - Tales Untold

## Official Whisper Output

```
[00:00.000 --> 00:02.720]  I've always been a heavy snore.
[00:02.720 --> 00:07.600]  My girlfriend convinced me to record my sleep, hoping a doctor could help.
[00:07.600 --> 00:11.200]  I placed my phone on the nightstand and fell asleep.
[00:11.200 --> 00:14.320]  The next morning, I checked the recording.
[00:14.320 --> 00:16.560]  Six hours of audio.
[00:16.560 --> 00:19.360]  But something was wrong with the waveform.
[00:19.360 --> 00:22.640]  I isolated a section from 3am.
[00:22.640 --> 00:27.200]  When I played it back, I heard myself speaking in full sentences.
[00:27.200 --> 00:29.440]  Clear conversations.
[00:29.440 --> 00:32.160]  But I was alone in the apartment.
[00:32.160 --> 00:34.400]  And the words weren't English.
[00:34.400 --> 00:37.840]  I sent the audio to a linguistics professor.
[00:37.840 --> 00:40.640]  His email back still haunts me.
[00:40.640 --> 00:44.320]  He said this language died 600 years ago.
[00:44.320 --> 00:47.440]  And whoever is speaking it is asking when they can come through.
```

## Scene Mapping (10 scenes, 48s total)

| Time | Whisper Segment | Scene Key | Image File | Text Color | Caption Text |
|------|-----------------|-----------|------------|------------|--------------|
| 0-4.8s | 0-2.7s, 2.7-4.8s | snorer | scene1_heavy_sleeper.png | white | "I've always been a heavy snorer." / "My girlfriend convinced me to record my sleep." |
| 4.8-9.6s | 4.8-7.6s, 7.6-9.6s | phone | scene2_nightstand.png | white | "Hoping a doctor could help." / "I placed my phone on the nightstand." |
| 9.6-14.4s | 9.6-11.2s, 11.2-14.3s | asleep | scene1_setup.png | white | "I fell asleep." / "The next morning, I checked the recording." |
| 14.4-19.2s | 14.3-16.6s, 16.6-19.4s | waveform | scene5_weird_waveform.png | white→red | "Six hours of audio." / "But something was wrong with the waveform." |
| 19.2-24s | 19.4-22.6s, 22.6-24s | playback | scene6_playback.png | red | "I isolated a section from 3am." / "When I played it back..." |
| 24-28.8s | 24-27.2s, 27.2-28.8s | speaking | scene3_possession.png | red | "I heard myself speaking in full sentences." / "Clear conversations." |
| 28.8-33.6s | 28.8-32.2s, 32.2-33.6s | alone | scene7_alone.png | red | "But I was alone in the apartment." / "And the words weren't English." |
| 33.6-38.4s | 33.6-37.8s, 37.8-38.4s | professor | scene8_email.png | red | "I sent the audio to a linguistics professor." / "His email back still haunts me." |
| 38.4-44.3s | 38.4-42s, 42-44.3s | ancient | scene8_ancient.png | red | "He said this language died 600 years ago." / "And whoever is speaking it is asking when they can come through." |
| 44.3-48s | - | subscribe | (dark bg) | red | "SUBSCRIBE for more nightmares" |

## Image Inventory

Available images (check before mapping):
- scene1_heavy_sleeper.png - Person sleeping/snoring
- scene2_nightstand.png - Phone on nightstand
- scene1_setup.png - Dark bedroom
- scene3_morning_check.png - Morning check
- scene5_weird_waveform.png - Waveform problem
- scene6_playback.png - 3AM playback
- scene3_possession.png - Speaking/unnatural
- scene7_alone.png - Alone realization
- scene6_language.png - Ancient language
- scene8_email.png - Email screen
- scene8_ancient.png - Ancient/doorway

## Critical Fixes from This Session

1. **Caption position:** y=1420 (not 1250 - was cutting off bottoms)
2. **No base layer:** Don't add ColorClip base - causes black gaps
3. **Check images exist:** Verify `ls output/shorts/*.png` before mapping
4. **Exact timestamps:** Use Whisper output, never approximate
