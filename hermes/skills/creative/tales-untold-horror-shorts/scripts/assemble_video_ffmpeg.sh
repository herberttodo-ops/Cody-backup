#!/bin/bash
# Tales Untold Video Assembler (ffmpeg)
# Builds final vertical video from native Gammell images + Ken Burns + audio

set -e

OUTPUT_DIR="${OUTPUT_DIR:-output}"
SCENES_DIR="${SCENES_DIR:-output/shorts/gammell_native}"
TEMP_DIR="/tmp/tales_build_$$"
FINAL_OUTPUT="${OUTPUT_DIR}/FINAL_TALES_GAMMELL.mp4"

# Scene durations in seconds (matches narration timing)
DURATIONS=(14 9 17 10 10 10 6)

mkdir -p "$TEMP_DIR"

# Build each scene with Ken Burns zoom
for i in {1..7}; do
    DUR="${DURATIONS[$((i-1))]}"
    INPUT="${SCENES_DIR}/scene${i}.png"
    SCENE_OUT="${TEMP_DIR}/scene${i}.mp4"
    
    echo "Building scene ${i} (${DUR}s)..."
    
    # Slow zoom from 1.0 to 1.08 (Ken Burns effect)
    ffmpeg -y \
        -loop 1 \
        -i "$INPUT" \
        -vf "zoompan=z='min(zoom+0.0004,1.08)':d=$((DUR*30)):s=1080x1920:fps=30" \
        -c:v libx264 \
        -t "$DUR" \
        -pix_fmt yuv420p \
        -r 30 \
        "$SCENE_OUT" 2>/dev/null
        
    echo "  Scene ${i} done"
done

# Concatenate all scenes
echo "Concatenating scenes..."
for i in {1..7}; do
    echo "file '${TEMP_DIR}/scene${i}.mp4'" >> "$TEMP_DIR/concat_list.txt"
done

ffmpeg -y \
    -f concat \
    -safe 0 \
    -i "$TEMP_DIR/concat_list.txt" \
    -c:v libx264 \
    -r 30 \
    -pix_fmt yuv420p \
    "${TEMP_DIR}/visual.mp4" 2>/dev/null

# Mix audio: narration + background music
echo "Mixing audio..."
ffmpeg -y \
    -i "${TEMP_DIR}/visual.mp4" \
    -i "${OUTPUT_DIR}/narration_adam_poyo.mp3" \
    -i "${OUTPUT_DIR}/background_music.wav" \
    -filter_complex "
        [1:a]volume=1.0[narr];
        [2:a]volume=0.3,aloop=loop=-1:size=2e+09[mus];
        [narr][mus]amix=inputs=2:duration=first:dropout_transition=3[aout]
    " \
    -map 0:v:0 \
    -map "[aout]" \
    -c:v copy \
    -c:a aac \
    -b:a 192k \
    -t 76 \
    "${TEMP_DIR}/with_audio.mp4" 2>/dev/null

# Add title card (first 2s)
echo "Adding title..."
ffmpeg -y \
    -f lavfi \
    -i "color=c=black:s=1080x1920:d=2" \
    -i "${TEMP_DIR}/with_audio.mp4" \
    -filter_complex "
        [0:v]drawtext=text='TALES UNTOLD':fontsize=96:fontcolor=#dc2626:x=(w-text_w)/2:y=(h-text_h)/2-40:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf[title];
        [title][1:v]concat=n=2:v=1:a=0[vid];
        [1:a]atrim=start=2[a1]
    " \
    -map "[vid]" \
    -map "[a1]" \
    -c:v libx264 \
    -c:a aac \
    -b:a 192k \
    -r 30 \
    "${TEMP_DIR}/with_title.mp4" 2>/dev/null

# Add CTA at end (last 4s)
echo "Adding CTA..."
DURATION=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "${TEMP_DIR}/with_title.mp4" 2>/dev/null | cut -d. -f1)
CTA_START=$((DURATION - 4))

ffmpeg -y \
    -i "${TEMP_DIR}/with_title.mp4" \
    -vf "drawtext=text='LIKE & SUBSCRIBE':fontsize=64:fontcolor=white:x=(w-text_w)/2:y=(h-text_h)/2-100:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:enable='between(t,${CTA_START},${DURATION})',
         drawtext=text='@TalesUntold':fontsize=32:fontcolor=#9ca3af:x=(w-text_w)/2:y=(h-text_h)/2:fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf:enable='between(t,${CTA_START},${DURATION})'" \
    -c:v libx264 \
    -c:a copy \
    -r 30 \
    "$FINAL_OUTPUT" 2>/dev/null

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo "========================================"
echo "FINAL VIDEO: $FINAL_OUTPUT"
ls -lh "$FINAL_OUTPUT"
echo "========================================"
