# Video Analysis for Clip Selection

## Finding Engaging Moments

### Transcript Analysis

Look for these patterns in the transcript:

1. **Hook indicators**
   - Questions: "Did you know...", "What if...", "Why is..."
   - Contrarian statements: "Everyone thinks X, but actually..."
   - Numbers/stats: "80% of people...", "In just 3 years..."

2. **Emotional markers**
   - Capitalized words (excitement)
   - Exclamation points
   - Repeated words (stress/emphasis)
   - Pauses (transcript shows "..." or [pause])

3. **Reaction moments**
   - "Oh my god"
   - "Wow"
   - "That's crazy"
   - "I can't believe"

### FFmpeg Commands for Clips

**Extract multiple clips:**
```bash
# Clip 1: 0:30-1:00
ffmpeg -ss 00:00:30 -t 30 -i input.mp4 -c copy clip1.mp4

# Clip 2: 2:15-2:45
ffmpeg -ss 00:02:15 -t 30 -i input.mp4 -c copy clip2.mp4
```

**Vertical conversion:**
```bash
# Center crop to 9:16
ffmpeg -i input.mp4 -vf "crop=in_h*9/16:in_h,scale=1080:1920" output.mp4
```

**Add captions:**
```bash
ffmpeg -i input.mp4 -vf "subtitles=captions.srt" output.mp4
```

## Platform-Specific Formats

| Platform | Resolution | Aspect Ratio | Max Duration |
|----------|-----------|--------------|--------------|
| TikTok | 1080x1920 | 9:16 | 10 min |
| Instagram Reels | 1080x1920 | 9:16 | 90 sec |
| YouTube Shorts | 1080x1920 | 9:16 | 60 sec |