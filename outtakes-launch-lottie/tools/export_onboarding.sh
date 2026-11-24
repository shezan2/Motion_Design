#!/usr/bin/env bash
# Outtakes onboarding film (Ozen Flow): build -> sound -> render the three acts in parallel chunks -> concat + audio.
#   bash tools/export_onboarding.sh                       portrait  -> out/outtakes-onboarding-9x16-$VER.mp4
#   OT_FORMAT=landscape bash tools/export_onboarding.sh   landscape -> out/outtakes-onboarding-16x9-$VER.mp4
#   ONLY="2 3" bash tools/export_onboarding.sh          re-render only acts 2 and 3, then re-join
set -euo pipefail
cd "$(dirname "$0")/.."
export OT_FORMAT=${OT_FORMAT:-portrait}
VER=${VER:-v1}
if [ "$OT_FORMAT" = landscape ]; then P=public/projects/outtakes-onboarding-16x9; F=16x9; else P=public/projects/outtakes-onboarding; F=9x16; fi
OUTFILE=out/outtakes-onboarding-$F-$VER.mp4
JOBS=${JOBS:-4}
CHUNK=${CHUNK:-120}
SEG=out/segments-onboarding-$F
python3 tools/build_onboarding.py
# sound: synthesised SFX on the cue frames, crowd under the hook, a soft pad under the Studio and the payoff,
# then two-pass loudness to -14 LUFS with a -1.5 dBTP ceiling
OT_PROJECT=$(basename $P) OT_BED=studio OT_SFX_OUT=sfx_onboarding_raw_$F.wav python3 tools/sfx.py
IN=audio/sfx_onboarding_raw_$F.wav
M=$(ffmpeg -hide_banner -i $IN -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
g() { echo "$M" | python3 -c "import json,sys; print(json.load(sys.stdin)['$1'])"; }
ffmpeg -v error -y -i $IN -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(g input_i):measured_TP=$(g input_tp):measured_LRA=$(g input_lra):measured_thresh=$(g input_thresh):offset=$(g target_offset):linear=true,aresample=192000,alimiter=limit=0.80:attack=1:release=60:level=disabled,aresample=48000" audio/sfx_onboarding_$F.wav
mkdir -p $SEG
: > $SEG/list.txt
JOBF=$(mktemp)
for d in $(ls -d $P/scene-* | sort -V); do
  sn=$(basename $d)
  n=$(python3 -c "import json;d=json.load(open('$d/lottie.json'));print(int(d['op']-d['ip']))")
  for ((s=0; s<n; s+=CHUNK)); do
    e=$(( s + CHUNK < n ? s + CHUNK : n ))
    name=$sn-$(printf %04d $s)
    echo "file '$name.mp4'" >> $SEG/list.txt
    if [ -z "${ONLY:-}" ] || [[ " ${ONLY} " == *" ${sn#scene-} "* ]]; then echo "$d $SEG/$name.mp4 $s $e" >> $JOBF; fi
  done
done
xargs -P "$JOBS" -L 1 sh -c 'node tools/render.mjs scene "$0" "$1" "$2" "$3" 2>&1 | grep -v "as a font" || true' < $JOBF
rm -f $JOBF
ffmpeg -v error -y -f concat -safe 0 -i $SEG/list.txt -i audio/sfx_onboarding_$F.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 320k -shortest -movflags +faststart "$OUTFILE"
ffprobe -v error -show_entries format=duration:stream=width,height -of csv=p=0 "$OUTFILE"
echo "$OUTFILE"
