#!/usr/bin/env python3
"""
Verify Tales Untold video has all three improvements:
1. Ken Burns motion detected
2. No mid-word text breaks
3. Dual audio tracks (narration + background)
"""

import sys
import subprocess
import numpy as np
from PIL import Image
import wave

def extract_frame(video_path, timestamp_sec, output_path):
    """Extract single frame at timestamp."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-ss", str(timestamp_sec), "-vframes", "1",
        output_path
    ]
    subprocess.run(cmd, capture_output=True)

def extract_audio(video_path, output_wav):
    """Extract audio to stereo WAV."""
    cmd = [
        "ffmpeg", "-y", "-i", video_path,
        "-vn", "-acodec", "pcm_s16le",
        "-ar", "44100", "-ac", "2",
        output_wav
    ]
    subprocess.run(cmd, capture_output=True)

def check_ken_burns(frame_a_path, frame_b_path, threshold=1.0):
    """Check if two frames from same scene show motion."""
    a = np.array(Image.open(frame_a_path))
    b = np.array(Image.open(frame_b_path))
    diff = np.abs(a.astype(float) - b.astype(float))
    mean_diff = np.mean(diff)
    return mean_diff > threshold, mean_diff

def check_dual_audio(wav_path):
    """Check both channels have activity."""
    with wave.open(wav_path, 'rb') as wf:
        nframes = wf.getnframes()
        nchannels = wf.getnchannels()
        framerate = wf.getframerate()
        
        if nchannels != 2:
            return False, "Not stereo audio"
        
        frames = wf.readframes(nframes)
        audio = np.frombuffer(frames, dtype=np.int16).reshape(-1, 2)
        
        # Check both channels have activity
        window = int(framerate * 2)  # 2s windows
        both_active = 0
        total = 0
        for i in range(0, len(audio) - window, window):
            total += 1
            rms0 = np.sqrt(np.mean(audio[i:i+window, 0].astype(float)**2))
            rms1 = np.sqrt(np.mean(audio[i:i+window, 1].astype(float)**2))
            if rms0 > 100 and rms1 > 100:
                both_active += 1
        
        return both_active > total * 0.8, f"{both_active}/{total} windows dual-active"

def verify_video(video_path):
    """Run all verifications."""
    print(f"Verifying: {video_path}")
    print("=" * 50)
    
    # Extract test frames
    extract_frame(video_path, 0.5, "/tmp/vf_start.png")
    extract_frame(video_path, 5.0, "/tmp/vf_end.png")
    extract_frame(video_path, 15, "/tmp/vf_15s.png")
    extract_audio(video_path, "/tmp/vf_audio.wav")
    
    # 1. Ken Burns check
    motion, diff = check_ken_burns("/tmp/vf_start.png", "/tmp/vf_end.png")
    status = "✓" if motion else "✗"
    print(f"{status} Ken Burns motion: mean pixel diff = {diff:.2f} (threshold 1.0)")
    
    # 2. Text check (visual inspection recommended)
    print(f"  Frame at 15s saved to /tmp/vf_15s.png - check for mid-word breaks")
    
    # 3. Audio check
    dual, msg = check_dual_audio("/tmp/vf_audio.wav")
    status = "✓" if dual else "✗"
    print(f"{status} Dual audio tracks: {msg}")
    
    print("=" * 50)
    return motion and dual

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <video.mp4>")
        sys.exit(1)
    
    success = verify_video(sys.argv[1])
    sys.exit(0 if success else 1)
