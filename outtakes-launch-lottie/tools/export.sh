#!/usr/bin/env bash
# Full export: build scenes -> SFX -> render scenes in parallel with Skottie -> concat + audio.
#   bash tools/export.sh            (writes out/outtakes-launch-lottie-9x16.mp4)
set -euo pipefail
cd "$(dirname "$0")/.."
PROJECT=public/projects/outtakes-launch
JOBS=${JOBS:-4}
python3 tools/build_film.py
python3 tools/sfx.py
mkdir -p out/segments
rm -f out/segments/*.mp4
ls -d $PROJECT/scene-* | sort -V | xargs -P "$JOBS" -I{} sh -c 'node tools/render.mjs scene "{}" "out/segments/$(basename {}).mp4" 2>&1 | grep -v "as a font" || true'
: > out/segments/list.txt
for d in $(ls -d $PROJECT/scene-* | sort -V); do echo "file '$(basename $d).mp4'" >> out/segments/list.txt; done
ffmpeg -v error -y -f concat -safe 0 -i out/segments/list.txt -i audio/sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart out/outtakes-launch-lottie-9x16.mp4
ffprobe -v error -show_entries format=duration -of csv=p=0 out/outtakes-launch-lottie-9x16.mp4
