"""The racing line over the landmarks, for choosing the route: route_smooth.json (colour by radius), route_osm.json (grey),
the landmarks (green) and the distance from each landmark to the line.   python3 plot_route.py"""
import json, math, os
from PIL import Image, ImageDraw
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '..', '..', 'assets', 'kultur')
LAT0, LON0 = 59.328, 18.06; M_LAT = 111320; M_LON = 111320 * math.cos(math.radians(LAT0))
LM = json.load(open(os.path.join(H, 'landmarks.json')))
S = json.load(open(os.path.join(A, 'route_smooth.json'))); R = json.load(open(os.path.join(A, 'route_osm.json')))
xz = [tuple(p) for p in S['xz']]; osm = [(-(lo - LON0) * M_LON, (la - LAT0) * M_LAT) for la, lo in R]
lm = {k: (-(v[1] - LON0) * M_LON, (v[0] - LAT0) * M_LAT) for k, v in LM.items()}
allp = xz + osm + list(lm.values()); x0 = min(p[0] for p in allp) - 150; x1 = max(p[0] for p in allp) + 150
z0 = min(p[1] for p in allp) - 150; z1 = max(p[1] for p in allp) + 150; sc = 0.28
W, Hh = int((x1 - x0) * sc), int((z1 - z0) * sc)
im = Image.new('RGB', (W, Hh), (12, 14, 20)); d = ImageDraw.Draw(im)
T = lambda p: ((x1 - p[0]) * sc, (z1 - p[1]) * sc)   # x is west: east to the right
d.line([T(p) for p in osm + osm[:1]], fill=(90, 90, 100), width=2)
d.line([T(p) for p in xz + xz[:1]], fill=(0, 220, 255), width=4)
d.ellipse([T(xz[0])[0] - 6, T(xz[0])[1] - 6, T(xz[0])[0] + 6, T(xz[0])[1] + 6], fill=(255, 230, 0))
cum = [0.0]
for a, b in zip(xz, xz[1:]): cum.append(cum[-1] + math.dist(a, b))
for k, p in lm.items():
    i = min(range(len(xz)), key=lambda j: math.dist(xz[j], p)); dd = math.dist(xz[i], p)
    x, y = T(p); d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(60, 255, 120) if dd < 150 else (255, 90, 60))
    d.text((x + 6, y - 6), f'{k} {dd:.0f}m @{cum[i]:.0f}', fill=(220, 230, 240))
d.text((10, 10), f'racing line {S["len"]:.0f} m', fill=(255, 255, 255))
im.save(os.path.join(H, 'route_plot.png')); print('route_plot.png', W, Hh)
