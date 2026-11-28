#!/usr/bin/env bash
# Render the one-take film in parallel frame ranges into a 32-bit float surface, then join them
# (video only, 10-bit 4:4:4 BT.709 intermediate; tools/master.sh dithers it to 8-bit).
#   bash tools/render_film.sh [jobs]   -> out/film-video10.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
SCENE=public/projects/nickrl-intro-16x9/scene-1
FRAMES=$(python3 -c "import json;print(json.load(open('$SCENE/lottie.json'))['op'])")
JOBS=${1:-4}
SEG=out/segments
mkdir -p "$SEG"; rm -f "$SEG"/*.mp4
step=$(( (FRAMES + JOBS - 1) / JOBS ))
pids=()
for ((i=0; i<JOBS; i++)); do
  a=$(( i * step )); z=$(( a + step )); (( z > FRAMES )) && z=$FRAMES
  node tools/render.mjs range16 "$SCENE" "$a" "$z" "$SEG/part-$i.mp4" 2>&1 | grep -v "as a font" &
  pids+=($!)
done
for p in "${pids[@]}"; do wait "$p"; done
: > "$SEG/list.txt"
for ((i=0; i<JOBS; i++)); do echo "file 'part-$i.mp4'" >> "$SEG/list.txt"; done
ffmpeg -v error -y -f concat -safe 0 -i "$SEG/list.txt" -c copy out/film-video10.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height -of csv=p=0 out/film-video10.mp4
