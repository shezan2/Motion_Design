#!/usr/bin/env bash
# Final master: picture (near-lossless intermediate) + grain + SFX track -> delivery H.264/AAC.
#   bash tools/master.sh <version>   -> out/nickrl-intro-16x9-v<N>.mp4 (+ preview, cover)
set -euo pipefail
cd "$(dirname "$0")/.."
V=${1:-1}
OUT=out/nickrl-intro-16x9-v$V.mp4
# the 10-bit float-rendered intermediate is dithered to 8-bit 4:2:0 with a whisper of grain (no banding);
# BT.709 tagged, constant 30 fps, 48 kHz AAC
ffmpeg -v error -y -i out/film-video10.mp4 -i audio/sfx.wav \
  -filter_complex "[0:v]noise=c0s=2:c0f=t+u,format=yuv420p[v]" -map "[v]" -map 1:a \
  -c:v libx264 -profile:v high -preset slow -crf 16 -r 30 -pix_fmt yuv420p \
  -colorspace bt709 -color_primaries bt709 -color_trc bt709 \
  -c:a aac -b:a 320k -ar 48000 -movflags +faststart -shortest "$OUT"
# WhatsApp-size preview
ffmpeg -v error -y -i "$OUT" -vf scale=1280:-2 -c:v libx264 -crf 26 -preset slow -c:a aac -b:a 128k -movflags +faststart \
  "out/nickrl-intro-16x9-v$V-preview.mp4"
ffprobe -v error -show_entries format=duration,size:stream=codec_name,width,height,r_frame_rate,sample_rate -of compact "$OUT"
