"""Kulturstockholm's height profile: the survey's street (ground), the highest tile hit across the deck (top), the deck
(track.json frames) and the drop windows, against m along the lap.   python3 plot_profile.py [out.png]"""
import json, os, sys
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '..', '..', 'assets', 'kultur')
S = json.load(open(os.path.join(A, 'survey.json'))); D = json.load(open(os.path.join(A, 'track.json')))
n, ds = S['n'], S['ds']; L = n * ds
deck = [f[1] for f in D['frames']]; NF = len(deck)
vals = [v for v in S['top'] + S['ground'] + deck if v is not None]
y0, y1 = max(min(vals), -40), min(max(vals), 140); W, Hh = 2400, 700; sx = W / L; sy = (Hh - 40) / (y1 - y0)
im = Image.new('RGB', (W, Hh), (12, 14, 20)); d = ImageDraw.Draw(im)
Y = lambda y: Hh - 20 - (min(max(y, y0), y1) - y0) * sy
for name, a, b in D.get('drops', []) and [(x['n'], x['t0'] * L, x['t1'] * L) for x in D['drops']]:
    d.rectangle([a * sx, 0, b * sx, Hh], fill=(30, 40, 60)); d.text((a * sx + 4, 4), name, fill=(150, 180, 220))
for m in range(0, int(L), 500): d.line([(m * sx, 0), (m * sx, Hh)], fill=(40, 44, 54)); d.text((m * sx + 2, Hh - 16), str(m), fill=(120, 120, 130))
for arr, col in ((S['ground'], (120, 90, 60)), (S['top'], (200, 200, 210))):
    pts = [(i * ds * sx, Y(v)) for i, v in enumerate(arr) if v is not None]
    for p in pts: d.point(p, fill=col)
d.line([(i / NF * L * sx, Y(v)) for i, v in enumerate(deck)], fill=(0, 220, 255), width=2)
for k, y in enumerate(range(int(y0) // 10 * 10, int(y1), 10)): d.text((2, Y(y) - 6), str(y), fill=(90, 90, 100))
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, 'profile.png'); im.save(out); print(out, 'range', round(min(vals), 1), round(max(vals), 1))
