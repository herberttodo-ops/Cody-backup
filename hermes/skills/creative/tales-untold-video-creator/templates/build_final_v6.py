#!/usr/bin/env python3
"""
Tales Untold — Final Short Video Builder (v6)
Fixed bottom text cutoff using dynamic positioning.

Usage:
    cd /home/herby/.openclaw/workspace/tales-untold
    source venv/bin/activate
    python3 build_final_v6.py
"""
import os
import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "venv" / "lib" / "python3.11" / "site-packages"))

from moviepy import (
    ImageClip, TextClip, CompositeVideoClip,
    AudioFileClip
)

VIDEO_W, VIDEO_H = 1080, 1920
FPS = 30
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def load_whisper_segments(json_path):
    """Load Whisper transcription with exact word-level timing."""
    with open(json_path) as f:
        data = json.load(f)
    return [(s["start"], s["end"], s["text"].strip()) for s in data["segments"]]


def build_caption_clip(text, start, end, is_horror=False):
    """
    Build a caption TextClip with SAFE vertical positioning.
    
    CRITICAL: MoviePy TextClip with method='caption' positions y at the TOP
    of the text box. Multi-line text extends DOWNWARD from that point.
    """
    duration = end - start
    color = "#ff4444" if is_horror else "white"
    
    txt = TextClip(
        text=text,
        font=FONT,
        font_size=55,
        color=color,
        stroke_color="black",
        stroke_width=4,
        method="caption",
        size=(VIDEO_W - 80, None),  # 1000px max width, auto height
        text_align="center",
        duration=duration,
    )
    
    # txt.size is (width, height) of rendered text
    txt_w, txt_h = txt.size
    
    # Position from BOTTOM of video, not top
    # This ensures text never extends beyond video bounds
    bottom_margin = 20  # px from bottom edge (accounts for stroke bleed)
    safe_bottom = VIDEO_H - bottom_margin
    
    # y = TOP of text box
    y_pos = safe_bottom - txt_h
    x_pos = (VIDEO_W - txt_w) // 2
    
    # Sanity floor - don't let text go too high
    if y_pos < 1100:
        print(f"  [!] Warning: text tall ({txt_h}px), using y=1100 as fallback")
        y_pos = 1100
    
    # Safety assert
    bottom_of_text = y_pos + txt_h
    if bottom_of_text > VIDEO_H:
        print(f"  [!] ERROR: text exceeds video bottom! adjusting...")
        y_pos = VIDEO_H - txt_h - 10
    
    txt = txt.with_position((x_pos, y_pos))
    txt = txt.with_start(start)
    
    print(f"  Caption: '{text[:40]}...' y={y_pos}, h={txt_h}, bottom={y_pos+txt_h}")
    return txt


def build_scene_clip(image_name, start, end):
    """Load scene image and set duration."""
    img_path = PROJECT_ROOT / "output" / "shorts" / image_name
    if not img_path.exists():
        print(f"  [!] Missing: {image_name}, using black placeholder")
        from moviepy import ColorClip
        clip = ColorClip(size=(VIDEO_W, VIDEO_H), color=(10, 10, 10), duration=end - start)
    else:
        clip = ImageClip(str(img_path), duration=end - start)
        # Resize preserving aspect, filling 1080x1920
        clip = clip.resized(height=VIDEO_H)
        # Center crop if too wide
        if clip.size[0] > VIDEO_W:
            x_crop = (clip.size[0] - VIDEO_W) // 2
            clip = clip.cropped(x1=x_crop, x2=x_crop + VIDEO_W)
    clip = clip.with_start(start)
    return clip


def main():
    print("=" * 60)
    print("Tales Untold — Building FINAL short (v6)")
    print("=" * 60)
    
    # Load whisper transcription
    json_path = PROJECT_ROOT / "output" / "shorts" / "story_extended_voice.json"
    segments = load_whisper_segments(json_path)
    print(f"Loaded {len(segments)} whisper segments")
    print()
    
    # Scene splits covering full 48s duration
    scene_splits = [
        ("scene1_heavy_sleeper.png", 0.0, 5.0),
        ("scene2_nightstand.png", 5.0, 11.0),
        ("scene3_morning_check.png", 11.0, 16.0),
        ("scene5_weird_waveform.png", 16.0, 20.0),
        ("scene6_playback.png", 20.0, 27.0),
        ("scene7_alone.png", 27.0, 33.0),
        ("scene3_possession.png", 33.0, 38.0),
        ("scene6_language.png", 38.0, 41.0),
        ("scene8_email.png", 41.0, 44.0),
        ("scene8_ancient.png", 44.0, 48.0),
    ]
    
    # Build scene clips
    print("Building scene clips...")
    scene_clips = []
    for img_name, start, end in scene_splits:
        clip = build_scene_clip(img_name, start, end)
        scene_clips.append(clip)
        print(f"  {img_name}: {start:.1f}s - {end:.1f}s")
    print()
    
    # Determine horror escalation point (~27s)
    horror_start = 27.0
    
    # Build caption clips with dynamic positioning
    print("Building captions with safe positioning...")
    caption_clips = []
    for start, end, text in segments:
        is_horror = start >= horror_start
        cap = build_caption_clip(text, start, end, is_horror)
        caption_clips.append(cap)
    print()
    
    # Load audio
    audio_path = PROJECT_ROOT / "output" / "shorts" / "story_extended_voice.mp3"
    audio = AudioFileClip(str(audio_path))
    print(f"Audio duration: {audio.duration:.2f}s")
    
    # Composite video
    print()
    print("Compositing final video...")
    all_clips = scene_clips + caption_clips
    final = CompositeVideoClip(all_clips, size=(VIDEO_W, VIDEO_H))
    final = final.with_audio(audio)
    final = final.with_duration(48.0)
    
    # Export
    output_path = PROJECT_ROOT / "output" / "shorts" / "story_FINAL_v6.mp4"
    print(f"Exporting to: {output_path}")
    print("This may take a few minutes...")
    
    final.write_videofile(
        str(output_path),
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        bitrate="6000k",
        threads=4,
        logger=None,
    )
    
    print()
    print("=" * 60)
    print(f"DONE: {output_path}")
    print(f"Size: {output_path.stat().st_size / (1024*1024):.1f} MB")
    print("=" * 60)


if __name__ == "__main__":
    main()
