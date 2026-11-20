#!/usr/bin/env bash
# Loudness-normalise the voiceover mix (two-pass, -14 LUFS / -1.5 dBTP) and put it on both cuts.
#   python3 tools/vo_mix.py && bash tools/vo_mux.sh
set -euo pipefail
cd "$(dirname "$0")/.."
IN=audio/mix_vo_raw.wav
M=$(ffmpeg -hide_banner -i $IN -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i $IN -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=192000,alimiter=limit=0.8:attack=1:release=60:level=disabled,aresample=48000" audio/mix_vo.wav
for f in 9x16 16x9; do
  ffmpeg -v error -y -i out/outtakes-launch-lottie-$f.mp4 -i audio/mix_vo.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest out/outtakes-launch-lottie-$f-vo.mp4
  echo "out/outtakes-launch-lottie-$f-vo.mp4"
done
