#!/bin/bash
# Diapos TikTok (1080x1920 JPEG) -> vidéo verticale MP4 pour TikTok / Reel / Short.
# Usage : outils/slides_video.sh <sortie.mp4> <secondes_par_diapo> <img1.jpg> <img2.jpg> ...
# Fondu enchaîné de 0,5 s, léger zoom, piste audio silencieuse (compatibilité). Vise 20–90 s au total.
set -e
out=$1; d=$2; shift 2
n=$#; [ $n -ge 2 ] || { echo "au moins 2 images"; exit 1; }
inputs=(); filt=""; i=0
for img in "$@"; do
  inputs+=(-loop 1 -t "$d" -i "$img")
  filt+="[$i:v]scale=1188:2112,zoompan=z='min(zoom+0.0006,1.06)':d=$(awk "BEGIN{print int($d*25)}"):x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=25,setsar=1,format=yuv420p[v$i];"
  i=$((i+1))
done
prev="v0"; off=0
for ((k=1;k<n;k++)); do
  off=$(awk "BEGIN{print $off+$d-0.5}")
  filt+="[$prev][v$k]xfade=transition=fade:duration=0.5:offset=$off[x$k];"
  prev="x$k"
done
total=$(awk "BEGIN{print $n*$d-($n-1)*0.5}")
ffmpeg -v error -y "${inputs[@]}" -f lavfi -t "$total" -i anullsrc=r=44100:cl=stereo \
  -filter_complex "${filt%;}" -map "[$prev]" -map "$n:a" -c:v libx264 -preset veryfast -crf 24 -c:a aac -b:a 64k -shortest -movflags +faststart "$out"
echo "ok $out ${total}s"
