#!/bin/zsh
# WIPEOUT KULTURSTOCKHOLM, the race music (2026-10-03): Vivaldi's Summer Presto (John Harrison, Wikimedia Commons, CC BY-SA) on a
# straight q=160 grid with the game's own big-beat drums under it, plus the three 60 s audition files. Sources and licences:
# wo2097/assets/kultur/music/sources.json. Needs ffmpeg, rubberband (brew), python3, node + the Playwright install check_lap uses.
#   zsh wo2097/pipeline/kultur/music/build.sh [workdir]     (default /tmp/kmusic; the repo is never written until the last step)
# Steps: download -> score alignment (DTW against Mutopia's MIDI) -> bar tracker (16th comb, DP) -> beat markers + time map ->
# per-bar loudness -> plan (warp map, drum score, loop points) -> rubberband warp -> drums rendered in Chrome with the voices
# lifted from index.html -> mix (sidechain) -> master (-16 LUFS over a loop, limiter) -> MP3 160k -> audition excerpts at -16 LUFS.
# Change the groove in plan.py (full/light/fill, ENTRIES, TUTTI), the balance with mix.py's argument (drums dB, default -3).
set -e
HERE=${0:A:h}; REPO=${HERE:h:h:h:h}; WORK=${1:-/tmp/kmusic}; mkdir -p $WORK/mus $WORK/score; cd $WORK
UA="stockholmwipeout-build/1.0"
[ -f mus/harrison_presto.oga ] || curl -sfA "$UA" -o mus/harrison_presto.oga "https://upload.wikimedia.org/wikipedia/commons/f/fa/Vivaldi_-_Four_Seasons_2_Summer_mvt_3_Presto_-_John_Harrison_violin.oga"
[ -f mus/advent_brand3_1.ogg ] || curl -sfA "$UA" -o mus/advent_brand3_1.ogg "https://upload.wikimedia.org/wikipedia/commons/b/b0/Bach_-_Brandenburg_Concerto_No._3_-_1._Allegro.ogg"
[ -f score/summer-score-2.mid ] || { curl -sfo score/m.zip "https://www.mutopiaproject.org/ftp/VivaldiA/O8/summer/summer-mids.zip" && (cd score && unzip -oq m.zip); }
for f in harrison_presto advent_brand3_1; do [ -f mus/$f.wav ] || ffmpeg -hide_banner -loglevel error -y -i mus/$f.og* -ar 44100 -ac 2 mus/$f.wav; done
[ -x venv/bin/python ] || { python3 -m venv venv && venv/bin/pip install -q librosa soundfile pretty_midi matplotlib; }
PY=venv/bin/python
$PY $HERE/align.py mus/harrison_presto.wav harrison
$PY $HERE/bars.py harrison mus/harrison_presto.wav
$PY $HERE/beatsref.py harrison mus/harrison_presto.wav 160
$PY $HERE/bardb.py
$PY $HERE/plan.py
(cd mus && ../$PY $HERE/warp.py)
node $HERE/drums_render.cjs $REPO/index.html mus/A_plan.json mus/drums_all.wav
node $HERE/drums_render.cjs $REPO/index.html mus/A_plan.json mus/drums_kick.wav kick
$PY $HERE/mix.py -3
$PY $HERE/master.py
$PY $HERE/excerpts.py
cp mus/kulturstockholm_vivaldi_presto_breakbeat.mp3 $REPO/wo2097/assets/kultur/music/vivaldi_sommaren_presto.mp3
mkdir -p $REPO/kultur/musikprov && for v in a b c; do cp mus/prov_$v.mp3 $REPO/kultur/musikprov/$v.mp3; done
$PY -c "import json; d=json.load(open('mus/A_plan.json')); print('loopStart',round(d['loopStart'],4),'loopEnd',round(d['loopEnd'],4),'(KREC in index.html and sources.json must match)')"
