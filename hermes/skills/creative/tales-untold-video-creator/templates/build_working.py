#!/usr/bin/env python3
"""
Tales Untold — Complete Working Build vFinal
Reusable template: Adam voice (POYO) + cover-crop images + sentence captions + music mix
"""
import json, re, sys
from pathlib import Path
from PIL import Image
from moviepy import (
    AudioFileClip, CompositeAudioClip, concatenate_audioclips,
    ImageClip, concatenate_videoclips, CompositeVideoClip, TextClip, vfx, afx
)

OUTDIR   = Path.home() / ".openclaw/workspace/tales-untold/output/shorts"
ADAM_MP3 = Path.home() / ".openclaw/workspace/tales-untold/output/narration_adam_poyo.mp3"
MUSIC    = Path.home() / ".openclaw/workspace/tales-untold/output/background_music.wav"
TRANSCR  = OUTDIR / "transcript_adam.json"
FONT     = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
RES      = (1080, 1920)
FPS      = 30
FADE     = 0.15

def cover_crop(image_path: Path, target_size: tuple = RES) -> Image:
    tw, th = target_size
    img = Image.open(image_path)
    iw, ih = img.size
    scale = max(th / ih, tw / iw)
    new_w, new_h = int(iw * scale), int(ih * scale)
    resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    left = (new_w - tw) // 2
    top  = (new_h - th) // 2
    return resized.crop((left, top, left + tw, top + th))

def preprocess_images(scene_count: int, out_dir: Path) -> list[Path]:
    paths = []
    for i in range(1, scene_count + 1):
        src = out_dir / f"scene{i}.png"
        dst = out_dir / f"scene{i}_cover.png"
        if src.exists():
            cover_crop(src).save(dst)
        paths.append(dst)
    return paths

def split_into_sentences(transcript_path: Path) -> list[dict]:
    data = json.loads(transcript_path.read_text())
    captions = []
    for seg in data.get("segments", []):
        start, end, text = seg["start"], seg["end"], seg["text"].strip()
        if not text: continue
        parts = [p.strip() for p in re.split(r'(?<=[.!?])\s+', text) if p.strip()]
        total_chars = sum(len(p) for p in parts) or 1
        seg_dur = end - start
        t = start
        for p in parts:
            p_dur = seg_dur * (len(p) / total_chars)
            captions.append({"start": t, "end": t + p_dur, "text": p})
            t += p_dur
    return captions

def build():
    narration = AudioFileClip(str(ADAM_MP3))
    audio_dur = narration.duration

    # Music: measure source first, then scale conservatively
    music = AudioFileClip(str(MUSIC))
    loops = int(audio_dur / music.duration) + 1
    music = concatenate_audioclips([music] * loops).subclipped(0, audio_dur)
    # Start conservative (0.5-0.7x for -15dB source music), adjust per user
    music = music.with_volume_scaled(0.6)
    music = music.with_effects([afx.AudioFadeOut(3.0)])
    final_audio = CompositeAudioClip([narration, music])

    scene_count = 10
    scene_dur   = audio_dur / scene_count
    img_paths   = preprocess_images(scene_count, OUTDIR)

    scenes = []
    for p in img_paths:
        clip = ImageClip(str(p), duration=scene_dur + FADE)
        clip = clip.with_effects([vfx.CrossFadeIn(FADE), vfx.CrossFadeOut(FADE)])
        scenes.append(clip)

    video = concatenate_videoclips(scenes, method="compose").subclipped(0, audio_dur)

    captions = split_into_sentences(TRANSCR)
    text_clips = []
    for c in captions:
        color = "#ff4444" if c["start"] >= 19.0 else "white"
        txt = TextClip(
            text=c["text"], font=FONT, font_size=58, color=color,
            stroke_color="black", stroke_width=5,
            size=(1000, None), method="caption", text_align="center",
        )
        txt = txt.with_position(("center", 1420))
        txt = txt.with_start(c["start"]).with_end(c["end"])
        text_clips.append(txt)

    final = CompositeVideoClip([video] + text_clips, size=RES)
    final = final.with_audio(final_audio)

    out_path = OUTDIR / "FINAL_TALES_UNTOLD_vFinal.mp4"
    final.write_videofile(
        str(out_path), fps=FPS, codec="libx264", audio_codec="aac",
        temp_audiofile=str(OUTDIR / "temp_final.m4a"),
        remove_temp=True, preset="medium", threads=4, logger=None,
    )
    print(f"Done: {out_path}")

if __name__ == "__main__":
    build()
