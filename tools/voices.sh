#!/usr/bin/env bash
# Génère voices/sceneXX.mp3 avec Piper (voix fr locale) + ffmpeg.
# Usage : tools/voices.sh /chemin/fr-siwis-medium.onnx
set -euo pipefail
MODEL="$1"; cd "$(dirname "$0")/.."; TMP=$(mktemp -d)
line(){ # n perso texte
  local n=$1 who=$2 txt=$3 raw="$TMP/$1.wav"
  if [ "$who" = goku ]; then
    echo "$txt" | python3 -m piper -m "$MODEL" --length-scale 0.88 --noise-scale 0.75 -f "$raw" >/dev/null 2>&1
    ffmpeg -loglevel error -y -i "$raw" -af "rubberband=pitch=1.12:formant=preserved,acompressor=threshold=-18dB:ratio=3,volume=2.5,aresample=44100" -b:a 160k "voices/scene$n.mp3"
  else
    echo "$txt" | python3 -m piper -m "$MODEL" --length-scale 0.95 --noise-scale 0.5 -f "$raw" >/dev/null 2>&1
    ffmpeg -loglevel error -y -i "$raw" -af "asetrate=22050*0.74,aresample=22050,atempo=1.18,bass=g=6:f=140,acompressor=threshold=-18dB:ratio=4,aecho=0.8:0.6:40:0.15,volume=2.5,aresample=44100" -b:a 160k "voices/scene$n.mp3"
  fi
  echo "scene$n $who $(ffprobe -v error -show_entries format=duration -of csv=p=0 voices/scene$n.mp3)s"
}
line 01 vegeta "Pourquoi je déteste perdre ?"
line 02 goku   "Végéta... c'était juste Mario Kart !"
line 03 vegeta "Je ne perds pas. Jamais."
line 04 goku   "En fait, c'est ton cerveau qui fait ça."
line 05 goku   "Perdre fait environ deux fois plus mal, que gagner fait plaisir."
line 06 vegeta "Deux fois ? Seulement ?"
line 07 goku   "Des chercheurs ont appelé ça, l'aversion à la perte."
line 08 goku   "Avant, perdre de la nourriture, ça pouvait te coûter la vie !"
line 09 goku   "Alors ton cerveau traite une défaite, comme un danger."
line 10 vegeta "Donc, c'est pas ma faute."
line 11 goku   "Hé hé... Si, un peu quand même !"
line 12 goku   "Et toi, t'as un truc en plus : l'égo."
line 13 vegeta "Le prince des Saïyens n'a pas d'égo. Il a de la fierté."
line 14 goku   "C'est pareil."
line 15 vegeta "Et toi, pourquoi ça te fait rien de perdre ?"
line 16 goku   "Parce que moi, je vois la défaite comme un entraînement !"
rm -rf "$TMP"
