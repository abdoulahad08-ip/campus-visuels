#!/bin/bash
# Usage : outils/video_build.sh videos/<dossier>   (original.mp4 + fond.png -> tiktok.mp4 + reel.mp4 de 88 s)
set -e
d=$1
ffmpeg -v error -y -loop 1 -i "$d/fond.png" -i "$d/original.mp4" -filter_complex "[1:v]scale=1080:608,fps=25[v];[0:v][v]overlay=0:760:shortest=1,format=yuv420p" -map 1:a -c:v libx264 -preset veryfast -crf 28 -tune stillimage -c:a aac -b:a 128k -movflags +faststart "$d/tiktok.mp4"
ffmpeg -v error -y -i "$d/tiktok.mp4" -t 88 -c:v libx264 -preset veryfast -crf 23 -c:a aac -b:a 128k -movflags +faststart -af "afade=t=out:st=86:d=2" -vf "fade=t=out:st=86.5:d=1.5" "$d/reel.mp4"
echo "ok $d"
