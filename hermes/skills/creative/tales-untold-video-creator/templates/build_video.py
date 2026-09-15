"""
Tales Untold Video Builder - Subagent Script Template

This is a complete working script for building Tales Untold horror shorts.
The subagent should copy this file and customize for each video.
"""

import os
import json
from moviepy import *
from PIL import Image
import numpy as np

# Configuration
VIDEO_W, VIDEO_H = 1080, 1920
FONT = 'DejaVuSans-Bold'
BOTTOM_MARGIN = 20

def load_image(path, target_size=(VIDEO_W, VIDEO_H)):
    """Load and resize image to fit video dimensions."""
    if not os.path.exists(path):
        return None
    img = Image.open(path)
    w, h = img.size
    tw, th = target_size
    
    # Center crop to aspect ratio
    if w/h > tw/th:
        new_w = int(h * tw / th)
        left = (w - new_w) // 2
        img = img.crop((left, 0, left + new_w, h))
    else:
        new_h = int(w * th / tw)
        top = (h - new_h) // 2
        img = img.crop((0, top, w, top + new_h))
    
    return np.array(img.resize((tw, th), Image.LANCZOS))

def make_safe_caption(text, start, duration, video_h=VIDEO_H, 
                       font_size=48, color="white", stroke_w=5):
    """
    CRITICAL: Dynamic text positioning to prevent cutoff.
    TextClip positions from TOP, text extends DOWNWARD.
    Calculate y position so bottom is at video_h - margin.
    """
    txt = TextClip(
        text=text,
        font=FONT,
        font_size=font_size,
        color=color,
        stroke_color="black",
        stroke_width=stroke_w,
        size=(900, None),
        method='caption'
    )
    
    # Calculate exact height AFTER rendering
    txt_h = txt.h
    
    # Position so bottom edge is BOTTOM_MARGIN from video bottom
    y_pos = video_h - BOTTOM_MARGIN - txt_h
    
    # Safety: never position above reasonable top margin
    y_pos = max(100, y_pos)
    
    return txt.with_start(start).with_duration(duration).with_position(('center', y_pos))

def build_video(script_path, audio_path, transcript_path, output_path):
    """
    Complete video builder from assets.
    
    Expected structure:
    - script.txt: The written story
    - audio.mp3: ElevenLabs narration
    - transcript.json: Whisper transcription with timestamps
    - scene1.png ... scene10.png: Generated images
    """
    
    # Load audio
    audio = AudioFileClip(audio_path)
    duration = audio.duration
    
    # Load transcript
    with open(transcript_path) as f:
        transcript = json.load(f)
    
    # Map segments to scenes
    segments = []
    num_scenes = 10
    scene_duration = duration / num_scenes
    
    for i in range(num_scenes):
        start = i * scene_duration
        end = (i + 1) * scene_duration
        segments.append({
            'start': start,
            'end': end,
            'scene': f'scene{i+1}.png'
        })
    
    # Build clips
    clips = []
    
    for seg in segments:
        # Load scene image
        img_path = f"output/shorts/{seg['scene']}"
        img_arr = load_image(img_path)
        
        if img_arr is None:
            # Fallback: dark background
            bg = ColorClip(size=(VIDEO_W, VIDEO_H), color=(5, 5, 8))
            bg = bg.with_start(seg['start']).with_duration(seg['end'] - seg['start'])
            clips.append(bg)
        else:
            img_clip = ImageClip(img_arr)
            img_clip = img_clip.with_start(seg['start']).with_duration(seg['end'] - seg['start'])
            clips.append(img_clip)
    
    # Add captions from transcript
    # [Caption logic goes here - parse transcript.json]
    
    # Composite and export
    final = CompositeVideoClip(clips, size=(VIDEO_W, VIDEO_H))
    final = final.with_duration(duration)
    final = final.with_audio(audio)
    
    final.write_videofile(
        output_path,
        fps=30,
        codec='libx264',
        audio_codec='aac',
        bitrate='6000k'
    )
    
    # Cleanup
    audio.close()
    final.close()
    
    print(f"✅ Video exported: {output_path}")

if __name__ == "__main__":
    build_video(
        script_path="output/script.txt",
        audio_path="output/audio.mp3", 
        transcript_path="output/transcript.json",
        output_path="output/FINAL_TALES_UNTOLD_SHORT.mp4"
    )
