"""STOCKHOLM WIPEOUT 2097 · the racing line.
The OSM street route has near-right-angle corners (min radius ~3 m). This smooths it to a minimum turn radius of
R_MIN metres with continuous curvature, and writes ../assets/route_smooth.json (x,z in the game frame, every STEP m),
which the game's ?dump mode uses instead of ROUTE. The track is allowed to leave the street at corners; the dump
lifts it over whatever it crosses.

Why 120 m: the game's grip limit is v = sqrt(70 * R) (index.html, curvAhead grip). Top speed is 66 m/s plus up to
~24 m/s of pad boost, so R = 120 m holds ~92 m/s: every corner can be taken flat out, boosted, without being pulled
into the wall. At 66 m/s that is a yaw rate of 0.55 rad/s (31 deg/s) for the chase camera.

    python3 design_track.py            # writes ../assets/route_smooth.json and route_smooth.png"""
import os, re, json, math
import numpy as np
H = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.abspath(os.path.join(H, '..', '..'))
OUT = os.path.join(H, '..', 'assets')
R_MIN = 120.0          # metres, minimum turn radius of the racing line
TARGET = R_MIN * 1.08  # smooth to a little more than the limit so the final light filter never undershoots
STEP = 8.0             # spacing of the control points handed to the game (its centripetal Catmull-Rom goes through them)

src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
o = re.search(r'const ORIGIN=\{ lat:([\d.]+), lon:([\d.]+)', src); OLAT, OLON = float(o.group(1)), float(o.group(2))
block = src[src.index('const ROUTE=['):]; block = block[:block.index('];')]
ROUTE = [(float(a), float(b)) for a, b in re.findall(r'\[([\d.]+),([\d.]+)\]', block)]
M_LAT = 111320.0; M_LON = 111320.0 * math.cos(math.radians(OLAT))
P = np.array([[-(lo - OLON) * M_LON, (la - OLAT) * M_LAT] for la, lo in ROUTE])   # (x = west, z = north)
# the same trims the game does: tail points that sit on the start, near-duplicates
while len(P) > 8 and np.hypot(*(P[-1] - P[0])) < 35: P = P[:-1]
keep = [0]
for i in range(1, len(P)):
    if np.hypot(*(P[i] - P[keep[-1]])) >= 8: keep.append(i)
P = P[keep]; ORIG = P.copy()

def resample(Q, ds):
    """closed polyline -> points every ds metres along it"""
    Q2 = np.vstack([Q, Q[:1]]); seg = np.hypot(*(np.diff(Q2, axis=0).T)); s = np.concatenate([[0], np.cumsum(seg)])
    n = max(16, int(round(s[-1] / ds))); t = np.linspace(0, s[-1], n, endpoint=False)
    return np.stack([np.interp(t, s, Q2[:, 0]), np.interp(t, s, Q2[:, 1])], 1), s[-1]

def curvature(Q, m):
    """signed curvature from the circle through points i-m, i, i+m (robust against point noise)"""
    a, b, c = np.roll(Q, m, 0), Q, np.roll(Q, -m, 0)
    ab, bc, ca = b - a, c - b, a - c
    cross = ab[:, 0] * bc[:, 1] - ab[:, 1] * bc[:, 0]
    la, lb, lc = np.hypot(*ab.T), np.hypot(*bc.T), np.hypot(*ca.T)
    return 2 * cross / np.maximum(la * lb * lc, 1e-9)

def gauss_closed(Q, sigma_pts):
    r = int(3 * sigma_pts); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma_pts) ** 2); k /= k.sum()
    out = np.zeros_like(Q)
    for j, w in zip(range(-r, r + 1), k): out += w * np.roll(Q, j, 0)
    return out

DS = 3.0
Q, L0 = resample(P, DS)
m = 4                      # curvature measured over +-12 m
kmax = 1.0 / TARGET
it = 0
while True:
    k = np.abs(curvature(Q, m)); worst = k.max()
    if worst <= kmax or it > 40000: break
    # relax only where the line is too tight (and a margin around it), towards the neighbours' midpoint:
    # a local elastic band. The corner moves inward until its radius reaches the target.
    bad = k > kmax * 0.97
    bad = np.convolve(np.concatenate([bad[-8:], bad, bad[:8]]).astype(float), np.ones(17), 'same')[8:-8] > 0
    mid = 0.5 * (np.roll(Q, 1, 0) + np.roll(Q, -1, 0))
    Q = np.where(bad[:, None], Q + 0.5 * (mid - Q), Q)
    it += 1
    if it % 400 == 0: Q, _ = resample(Q, DS)   # keep the spacing even while points slide inward
Q, L1 = resample(Q, DS)
Q = gauss_closed(Q, sigma_pts=4)                 # curvature continuity: no kinks where a relaxed zone meets a straight
Q, L2 = resample(Q, DS)
k = curvature(Q, m); kabs = np.abs(k)
Rmin = 1 / kabs.max()
dk = np.abs(np.diff(np.concatenate([k, k[:1]]))) / DS    # curvature change per metre
# never let the lap cross itself
def segs_intersect(Q):
    n = len(Q); A = Q; B = np.roll(Q, -1, 0); hits = 0
    for i in range(0, n, 2):
        for j in range(i + 3, n - 1 if i == 0 else n, 3):
            p, r = A[i], B[i] - A[i]; q, s = A[j], B[j] - A[j]; rxs = r[0] * s[1] - r[1] * s[0]
            if abs(rxs) < 1e-9: continue
            t = ((q - p)[0] * s[1] - (q - p)[1] * s[0]) / rxs; u = ((q - p)[0] * r[1] - (q - p)[1] * r[0]) / rxs
            if 0 <= t <= 1 and 0 <= u <= 1: hits += 1
    return hits
X = segs_intersect(resample(Q, 12)[0])
# how far the racing line leaves the street route
from itertools import islice
def dist_to_poly(pts, poly):
    a = poly; b = np.roll(poly, -1, 0); ab = b - a; ll = (ab ** 2).sum(1) + 1e-9; out = []
    for p in pts:
        t = np.clip(((p - a) * ab).sum(1) / ll, 0, 1); d = np.hypot(*(a + ab * t[:, None] - p).T); out.append(d.min())
    return np.array(out)
dev = dist_to_poly(Q[::4], ORIG)
CP, Lf = resample(Q, STEP)
json.dump({'rMin': R_MIN, 'step': STEP, 'len': Lf, 'xz': [[round(float(x), 3), round(float(z), 3)] for x, z in CP]},
          open(os.path.join(OUT, 'route_smooth.json'), 'w'))
print(f'route {L0:.0f} m -> racing line {Lf:.0f} m, {len(CP)} control points every {STEP} m')
print(f'min radius {Rmin:.1f} m (target >= {R_MIN}), max dk/ds {dk.max():.5f} 1/m^2, relax iterations {it}, self-crossings {X}')
print(f'leaves the street route: median {np.median(dev):.1f} m, 95th {np.percentile(dev,95):.1f} m, max {dev.max():.1f} m')
try:
    from PIL import Image, ImageDraw
    S = 0.18; allp = np.vstack([ORIG, Q]); mn = allp.min(0) - 60; W_, H_ = ((allp.max(0) - mn + 60) * S).astype(int)
    im = Image.new('RGB', (int(W_), int(H_)), (12, 14, 20)); d = ImageDraw.Draw(im)
    tr = lambda p: ((W_ - (p[0] - mn[0]) * S), (H_ - (p[1] - mn[1]) * S))   # x is west: flip so east is right
    d.line([tr(p) for p in np.vstack([ORIG, ORIG[:1]])], fill=(120, 120, 130), width=2)
    for i in range(len(Q)):
        a, b = Q[i], Q[(i + 1) % len(Q)]; c = min(1, kabs[i] * R_MIN)
        d.line([tr(a), tr(b)], fill=(int(255 * c), int(230 * (1 - c) + 30), int(255 * (1 - c))), width=3)
    im.save(os.path.join(H, 'route_smooth.png')); print('overlay -> route_smooth.png (grey = OSM streets, colour = racing line, red = at the radius limit)')
except Exception as ex: print('no overlay', ex)
