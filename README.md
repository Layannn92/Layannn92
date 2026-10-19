# Pourquoi tu perds ? — version Dragon Ball

**La vidéo finale : [`pourquoi-tu-perds.mp4`](pourquoi-tu-perds.mp4)** (63 s, 1080×1920, voix + bruitages + musique).

Motion design vertical (9:16, 1080×1920) en 17 scènes, dans le style fan-art Dragon Ball, avec Goku et Vegeta qui se donnent la réplique.

## Lancer
Ouvrir `index.html` dans Chrome ou Edge, puis cliquer sur **LANCER**.

- `←` / `→` : scène précédente / suivante, `Espace` : pause
- `index.html?scene=7` : ouvre directement une scène (aperçu sans son)

## Voix
1. **Par défaut** : la synthèse vocale du navigateur (fr-FR), avec une voix aiguë et rapide pour Goku et une voix grave et lente pour Vegeta.
2. **Meilleur rendu** : déposer des fichiers `voices/scene01.mp3` … `voices/scene16.mp3` (une réplique par fichier, voir `voices/README.md`). Ils remplacent automatiquement la synthèse vocale.

Les bruitages (sirène, explosion de ki, level-up…) sont générés en Web Audio : aucun fichier à télécharger.

## Refaire la vidéo
1. Voix : `tools/voices.sh fr-siwis-medium.onnx` (Piper, voix française locale ; Goku plus aigu, Vegeta plus grave).
2. Vidéo : `npm i playwright && node tools/render.mjs` → rendu image par image + mixage audio (`tools/audio.py`, besoin de numpy et ffmpeg).
