#!/usr/bin/env bash
# Full export: build scenes -> SFX -> render scenes in parallel with Skottie -> concat + audio.
#   bash tools/export.sh                 portrait  -> out/outtakes-launch-lottie-9x16.mp4
#   OT_FORMAT=landscape bash tools/export.sh   landscape -> out/outtakes-launch-lottie-16x9.mp4
# Both formats share one timeline, so they share one sound-effects track.
set -euo pipefail
cd "$(dirname "$0")/.."
export OT_FORMAT=${OT_FORMAT:-portrait}
if [ "$OT_FORMAT" = "landscape" ]; then
  PROJECT=public/projects/outtakes-launch-16x9; OUTFILE=out/outtakes-launch-lottie-16x9.mp4
else
  PROJECT=public/projects/outtakes-launch; OUTFILE=out/outtakes-launch-lottie-9x16.mp4
fi
JOBS=${JOBS:-4}
SEG=out/segments-$OT_FORMAT
python3 tools/build_film.py
python3 tools/sfx.py
mkdir -p "$SEG"
rm -f "$SEG"/*.mp4
ls -d $PROJECT/scene-* | sort -V | xargs -P "$JOBS" -I{} sh -c 'node tools/render.mjs scene "$1" "$2/$(basename "$1").mp4" 2>&1 | grep -v "as a font" || true' _ {} "$SEG"
: > "$SEG/list.txt"
for d in $(ls -d $PROJECT/scene-* | sort -V); do echo "file '$(basename $d).mp4'" >> "$SEG/list.txt"; done
ffmpeg -v error -y -f concat -safe 0 -i "$SEG/list.txt" -i audio/sfx.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 320k -shortest -movflags +faststart "$OUTFILE"
ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 "$OUTFILE"
