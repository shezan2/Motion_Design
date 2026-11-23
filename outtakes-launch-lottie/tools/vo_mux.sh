#!/usr/bin/env bash
# Voiceover versions of both cuts. Per format: synthesise the effects without the crowd bed, lay the voice lines
# on their beats with the effects ducked (tools/vo_mix.py), loudness-normalise (two-pass, -14 LUFS, true-peak
# limited) and mux onto that format's film.
#   bash tools/vo_mux.sh   ->  out/outtakes-launch-lottie-9x16-vo.mp4, out/outtakes-launch-lottie-16x9-vo.mp4
set -euo pipefail
cd "$(dirname "$0")/.."
for FMT in portrait landscape; do
  if [ "$FMT" = landscape ]; then F=16x9; else F=9x16; fi
  OT_FORMAT=$FMT OT_NO_BED=1 python3 tools/sfx.py > /dev/null
  OT_FORMAT=$FMT python3 tools/vo_mix.py > /dev/null
  IN=audio/mix_vo_raw.wav
  M=$(ffmpeg -hide_banner -i $IN -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  g() { echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
  ffmpeg -v error -y -i $IN -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=192000,alimiter=limit=0.78:attack=1:release=60:level=disabled,aresample=48000" audio/mix_vo-$F.wav
  ffmpeg -v error -y -i out/outtakes-launch-lottie-$F.mp4 -i audio/mix_vo-$F.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 256k -shortest -movflags +faststart out/outtakes-launch-lottie-$F-vo.mp4
  echo "out/outtakes-launch-lottie-$F-vo.mp4"
done
