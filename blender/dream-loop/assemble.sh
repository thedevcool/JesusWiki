#!/usr/bin/env bash
# Turn rendered frame folders into captioned episode clips + one seamless looping video.
# Usage: ./assemble.sh <frames_dir> <out_dir>
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
FR="${1:-$HERE/frames}"; OUT="${2:-$HERE/out}"
mkdir -p "$OUT/episodes" "$OUT/.txt"
BOLD=/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf
SEMI=/usr/share/fonts/opentype/inter/Inter-SemiBold.otf
[ -f "$BOLD" ] || BOLD=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
[ -f "$SEMI" ] || SEMI=/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf

TITLES=(
  "THE DREAM"
  "PLOT TWIST"
  "FRIENDLY TERROR"
  "HELP DESK"
  "THE GRIND"
  "BACKEND BOSS"
  "STILL STUDYING"
  "SUNDAYS"
  "ALMOST THERE"
  "THE LEAD"
)
CAPTIONS=(
  "Three friends. Three dreams: game dev, mechanical engineer... and lawyer."
  "\"Lawyer? Nah. I'll be a HACKER!\"  (he just liked the fun)"
  "...so he could friendly-terrorize his game dev friend."
  "And whenever the game dev got stuck, he knew exactly who to call."
  "6 years of grinding. Day. Night. Coffee. Repeat."
  "He became a great backend developer."
  "Game dev went into Computer Science. The engineer kept engineering."
  "3 years on, they always meet at church."
  "Both almost done... and still learning."
  "Now a lead software engineer. Still not a hacker... yet. The dream loops on."
)

list="$OUT/.txt/concat.txt"; : > "$list"
for i in $(seq 1 10); do
  n=$(printf %02d "$i")
  printf '%s' "EP $n  ·  ${TITLES[$((i-1))]}" > "$OUT/.txt/t$n.txt"
  printf '%s' "${CAPTIONS[$((i-1))]}" > "$OUT/.txt/c$n.txt"
  fx=""
  # loop seam: ep01 fades in from white, ep10 dives into the white thought bubble
  [ "$i" = 1 ] && fx=",fade=t=in:st=0:d=0.5:color=white"
  [ "$i" = 10 ] && fx=",fade=t=out:st=3.55:d=0.45:color=white"
  ffmpeg -y -loglevel error -framerate 24 -i "$FR/ep$n/f_%04d.png" -vf "\
drawbox=x=24:y=22:w=iw*0.42:h=46:color=black@0.55:t=fill,\
drawtext=fontfile=$BOLD:textfile=$OUT/.txt/t$n.txt:x=40:y=34:fontsize=24:fontcolor=white,\
drawbox=x=0:y=ih-78:w=iw:h=78:color=black@0.5:t=fill,\
drawtext=fontfile=$SEMI:textfile=$OUT/.txt/c$n.txt:x=(w-tw)/2:y=h-52:fontsize=22:fontcolor=white:\
alpha='if(lt(t,0.25),t/0.25,1)'$fx" \
    -c:v libx264 -pix_fmt yuv420p -crf 20 -preset slow -movflags +faststart "$OUT/episodes/ep$n.mp4"
  echo "file '$OUT/episodes/ep$n.mp4'" >> "$list"
  echo "ep$n done"
done
ffmpeg -y -loglevel error -f concat -safe 0 -i "$list" -c copy -movflags +faststart "$OUT/dream_loop.mp4"
# 3 loops back-to-back, for players/platforms that don't loop automatically
ffmpeg -y -loglevel error -stream_loop 2 -i "$OUT/dream_loop.mp4" -c copy -movflags +faststart "$OUT/dream_loop_x3.mp4"
rm -rf "$OUT/.txt"
echo "-> $OUT/dream_loop.mp4"
