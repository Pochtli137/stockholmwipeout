"""Fold a play-through's tile heights back into the survey. The survey (dump_track.cjs) looks down from 150 m and gets
coarser tiles than the chase camera does at race height, so tree crowns can come out a metre or two taller in the sweep.
    python3 merge_sweep.py <check outdir>      then: node dump_track.cjs rebuild && blender -b --factory-startup -P build.py"""
import json, sys, os
A = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
S = json.load(open(os.path.join(A, 'survey.json'))); tops = json.load(open(os.path.join(sys.argv[1], 'sweep_tops.json')))
n, ds, raised = S['n'], S['ds'], 0
for m, y in tops:
    if y is None: continue
    c = round(m / ds)
    for k in range(c - 2, c + 3):   # the sweep samples every 8 m, the survey every 4 m: cover the gap
        i = k % n
        if S['top'][i] is None or y > S['top'][i] + 0.05: S['top'][i] = y; raised += 1
json.dump(S, open(os.path.join(A, 'survey.json'), 'w')); print('survey samples raised:', raised)
