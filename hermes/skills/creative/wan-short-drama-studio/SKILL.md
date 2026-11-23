---
name: wan-short-drama-studio
description: Make short drama scripts for Wan video via POYO.
version: 1.0.0
category: creative
tags:
  - video
  - drama
  - wan
  - poyo
---

# Wan Short Drama Studio

Guide users from zero to a finished short drama script, then produce it using Wan 2.1 video generation via POYO. Replaces Higgsfield.ai workflow with Wan/POYO.

## When to Use

Load when someone wants:
- A short drama or micro-drama idea
- A season plan (4, 8, or 12 episodes)
- An episode script for AI video production
- Help adapting their script for Wan/POYO production

## Workflow

```
Script → Keyframes (Fal/POYO) → Wan Video (POYO) → Voice (POYO) → Assembly
```

## 1. Conversation Style

- Plain words in user's language. No jargon: "opening" not "hook".
- One question at a time, numbered options, one "recommended".
- Short messages. Long content: stories, plan, script only.
- You decide: hook, characters, location, stakes.
- Steer gently: "Keeping your idea, changing two things: ..."
- Dialogue in English unless asked otherwise.

## 2. Three Paths

### First Question
```
Do you have an idea, or should I help you come up with one?
1. Help me come up with one
2. I have an idea (one line)
3. I have a finished script (attach it)
```

### Path A: Help me come up with one
1. **Taste:** "Name 2–3 favorite films/series." Take mood only.
2. **Five stories:** Title + "→" chain ending with dialogue. Five different types/locations/stakes. Recommend one.
3. **Episodes:** 4 (recommended), 8, or 12.
4. **Episode plan:** Section 5.
5. **Length:** 60s (recommended), 90s, or 120s.
6. **Style:** Cinematic, K-Drama, Anime, Noir, RomCom, Thriller.
7. **Script Episode 1:** Sections 6–8.
8. **Next:** "Tell me to change. Write 'next' for episode 2."

### Path B: I have an idea
Return as "→" chain. Say what changed. Continue from Path A step 3.

### Path C: I have a finished script
1. Confirm in 2–3 sentences.
2. Adapt silently: format, word count, ages, names, English dialogue, actions not feelings, no camera words.
3. Note changes made.
4. Flag issues, suggest fixes.
5. Ask style, deliver file.

## 3. Story Principles (Check Silently)

- **Surface level:** No flashbacks, no "it turns out".
- **Opening:** Visible action or unmissable line. No greetings.
- **Unfair treatment:** By 3rd second, see who was wronged.
- **Stakes:** Physical/filmable: thrown out, locked in, amount said aloud. Not "reputation".
- **Goal + deadline:** "By noon", "before doors close".
- **"And so" chain:** Each forces the next. Retell with "→".
- **Hero acts:** No savior from nowhere.
- **Twist:** Seed on screen earlier. Cuts before answer.
- **No crying:** Anger, shock, resolve.

## 4. Story Types

| Type | Viewer waits for |
|---|---|
| Hidden status | Bullies learn who she really is |
| Forced deal | Deal turns to real feeling |
| Payback | Enemies fall one by one |
| Second chance | Hero uses what they know |
| Wrong person | Mask comes off |
| Love with enemy | Who betrays their side first |
| Secret on timer | One who mustn't know finds out |
| Underdog on stage | Faces of non-believers |
| Family war | Outcast takes head's place |
| Trap | The way out |
| Dark deal | Price comes due |
| Snowball lie | Lie blows up |

**Variety:** Five stories = five different types, locations, objects.

**Locations:** Office, hospital, restaurant, wedding, courtroom, store, gym, airport, elevator.

## 5. Episode Plan

**You decide:**
- Heroine's goal + deadline (season-long)
- Main enemy, presses harder
- Second line: relationship/alliance growing
- New person per 4-episode block, makes things worse

**Season Frame:**

| Part | Episodes | What happens |
|---|---|---|
| Opening | 1 (or 1–2 for 12ep) | Injustice, goal, deadline, new position |
| Rise | 2–3 (or 2–5) | Enemy strikes → answers → new threat |
| Midpoint | 4 (or 6) | False victory, someone stronger enters |
| Three quarters | — (or 7–9) | Loses everything |
| Finale | 4 (or 10–12) | Enemies fall, goal resolved, last shot mirrors first, future twist |

**Format:** Goal + who is who. Each episode: title + 3–5 sentence story. Last sentence = cut point.

**Episode Rules:**
- Understandable alone
- Starts at previous cliffhanger, answers in 10s
- One twist, one small win
- New cliffhanger type each time
- Always something happening

## 6. Numbers

| Length | Words | Ceiling |
|---|---|---|
| 60s | 70–90 | 100 |
| 90s | 110–135 | 150 |
| 120s | 145–180 | 200 |

**Check:** speech = words÷2.7 + 0.3×lines; silence = 3s + 2s/action + 4s final; total within 10% target.

- Lines: 3–8 words. One 15-word line at key moment.
- 2–4 speakers. 1 location, 2 max.

## 7. Wan Production (POYO, Wan 3.0 Video Prime)

Client: `scripts/poyo_wan_client.py` (copy of `~/.openclaw/workspace/tales-untold/poyo_wan_client.py`).
Key: `POYO_API_KEY` env var, or load from `~/.openclaw/workspace/tales-untold/.env`. Never hard-code.

### Model IDs (verified live Nov 22 2026)
- `wan3.0-prime-text-to-video`
- `wan3.0-prime-image-to-video` (`image_urls[0]` start frame, optional `[1]` end frame)
- `wan3.0-prime-reference-to-video` (`reference_image_urls` up to 10, refer as Image1, Video1, Audio1)
Old IDs like `wan-2-1-*`, `wan-3-0-*` return 404. Do not guess slugs.

### Specs
- resolution 480p/720p/1080p, duration 2-30s integer, aspect_ratio adaptive/16:9/4:3/1:1/3:4/9:16, audio true/false
- Black Friday price to 2026-11-30 23:59 UTC: 480p $0.048/s, 720p $0.098/s, 1080p $0.196/s
- Async: submit -> poll status 3-5s -> `data.files[0].file_url`. Check body `code == 200`, not only HTTP status.
- Observed: 480p 2s clip finishes in about 30-55s. Timeout default 1800s.
- Wan can generate clips up to 30s, so ~20x3s is no longer required; use 5-8s shots for fewer seams.

### Usage
```python
import sys; sys.path.insert(0, "<skill_dir>/scripts")
from poyo_wan_client import generate_wan_video
url = generate_wan_video(model="wan3.0-prime-image-to-video",
    prompt="Slow push in, mist drifts", image_urls=[keyframe_url],
    resolution="720p", duration=5, aspect_ratio="9:16", audio=False)
```
Batch: call `submit_wan_video` for all shots first, then `poll_wan_task` each (see `ep01/generate_test_wan.py`).

### Workflow
1. Keyframes (POYO `gpt-image-2` or `nano-banana-2-lite`), 9:16, one per shot.
2. i2v per shot with a motion prompt (keyframe keeps character/style consistent; text-to-video does not).
3. Voice: POYO `elevenlabs-v3-tts`. Captions from same script file.
4. Assemble:
```bash
ffmpeg -f concat -safe 0 -i clips.txt -c copy raw.mp4
ffmpeg -i raw.mp4 -i voice.mp3 -c:v copy -c:a aac final.mp4
```
Captions: y=1400-1500, 40-50px, 4-5px stroke.

### Style rule
Use the style written in the script's PRODUCTION block. "Cinematic" means live-action film language (35mm anamorphic, desaturated grade), NOT Gammell illustration. Gammell is only for Tales Untold.

## 8. File Format

```
THE RUSTY KEY
EPISODE 1
Vertical 9:16. About 60s. Cinematic. United States.
No establishing shot. Opens on: suitcase thrown across office.

--- PRODUCTION ---
Style: Cinematic
Wan clips: ~20
Keyframes: Confrontation, safe reveal, key close-up, deed reveal
Voice: Female, 30s, determined

CHARACTERS
NORA CROSS, 27. Daughter of hotel's late owner. Black dress, hair tied.
VICTOR CROSS, 34. Her brother. Dark suit, gold watch.
HALE, 60. Family lawyer. Grey suit, glasses, leather folder.
TWO MAIDS, 40s. Hotel uniforms. Silent.

SCENE 1. OWNER'S OFFICE IN OLD HOTEL. DAY.

Victor throws suitcase across office. Bursts at Nora's feet. Maids watch.

VICTOR: Out by six, Nora.

NORA: This is my home.

VICTOR: It was.

[Continue scene...]

HALE: Miss Cross. Does he stay?

--- END ---
Words: 124 | Est: 58s
```

## 9. Deliverables

1. Script block + .txt file
2. Check line: words + estimated seconds
3. Retelling: 2–3 sentences in user's language
4. Production briefing: ready for Wan, ~20 clips, keyframe→animate workflow
5. Next steps prompt

## 10. Checklist

### Stories/Plan
- [ ] Could happen; visible decision reasons
- [ ] Fits length; no time jumps
- [ ] Not a copy
- [ ] Simple stakes; goal + deadline
- [ ] Variety in types, locations, objects
- [ ] Unambiguous names
- [ ] Episodes: mini-story, cliffhanger
- [ ] No flashbacks
- [ ] Twist planted

### Script
- [ ] Opening is event; "No establishing shot"
- [ ] By 3s: who wronged by whom
- [ ] Word count in limits
- [ ] Lines 3–8 words; 2–4 speakers; 1–2 locations
- [ ] Entrances/exits/handovers written
- [ ] Nothing to read; no VO; no camera words; no tears
- [ ] Ages for all; leads adults; no real people/brands
- [ ] Mid twist; cuts on clear event
- [ ] Ep 2+: starts at cliffhanger, answers in 10s

### Wan Ready
- [ ] Keyframes described
- [ ] Motion per 3s clip
- [ ] Script in ~3s beats
- [ ] ~20 clips estimated for 60s

## Pitfalls

**Wan-specific:**
- 3s clips: ~20 for 60s episode
- Motion drift: same seed for consistency
- ~200 credits per 60s episode
- Keyframe quality drives output

**General:**
- Script-first workflow for voice/caption sync
- Include "cinematic lighting" in prompts
- Wan takes ~30-120s per clip

## References

- `ai-video-pipelines` skill
- `references/poyo-api-discovery.md`
- POYO docs: https://docs.poyo.ai/api-manual/video-series/wan-3-0-video-prime
