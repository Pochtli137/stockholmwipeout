"""Prototype of the FEEL profile against the tile survey, in Python so it can be plotted and tuned quickly.
The same algorithm is ported to designProfile() in index.html (the game and the dump use that one).

Base: the lowest smooth line 6 m over the street and 2.6 m over anything inside the track's width (as before).
Drops: in chosen windows the line may dive much steeper (up to ~16 %) and close shorter dips, so it falls toward the
water and the open squares and climbs back. The two lines are blended with a smooth weight, so both stay clear of the
envelope. Run:  python3 design.py  -> out/profile.png (before/after) and printed stats."""
import os, json, math, numpy as np
from prof import S, ground, top, cur, n, ds
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'out'); os.makedirs(OUT, exist_ok=True)

def winmax(a, w): return np.array([a[np.arange(i - w, i + w + 1) % n].max() for i in range(n)])
def winmin(a, w): return np.array([a[np.arange(i - w, i + w + 1) % n].min() for i in range(n)])
def gauss(a, sig):
    r = int(math.ceil(sig * 3)); k = np.exp(-0.5 * (np.arange(-r, r + 1) / sig) ** 2); k /= k.sum()
    ap = np.concatenate([a[-r:], a, a[:r]]); return np.convolve(ap, k, 'valid')

def profile(over_street=6, over_obst=2.6, slope=0.06, closeM=100, smoothM=25, buffer=2, finalM=40, slope_arr=None):
    req = np.maximum(ground + over_street, top + over_obst)
    w = max(1, round(closeM / ds)); env = winmin(winmax(req, w), w); env = np.maximum(env, req)
    SL = (slope_arr if slope_arr is not None else np.full(n, slope)) * 0.8
    for _ in range(3):
        for i in range(n): env[i] = max(env[i], env[i - 1] - SL[i] * ds)
        for i in range(n - 1, -1, -1): env[i] = max(env[i], env[(i + 1) % n] - SL[i] * ds)
    h = env + buffer; sg = smoothM / ds
    for _ in range(80): h = np.maximum(gauss(h, sg), env + buffer)
    h = gauss(h, finalM / ds)
    return h, req, env

# DROP WINDOWS (metres along the lap, from the survey: open space, nothing inside the track's width above the street)
DROPS = [  # name, start, end
    ('Slussen -> Strömmen', 250, 1000),
    ('Nybroviken', 1440, 1830),
    ('Norrmalm cut', 4380, 4680),
    ('Klara sjö', 5340, 5700),
    ('Norr Mälarstrand', 7340, 7560),
    ('Söder open', 9150, 9700),
]

def weight(ramp=90.0):
    x = np.arange(n) * ds; w = np.zeros(n)
    for _, a, b in DROPS:
        for i in range(n):
            d = min(x[i] - a, b - x[i])
            if d > -ramp: w[i] = max(w[i], 0.5 - 0.5 * math.cos(math.pi * min(1.0, (d + ramp) / ramp)) if d < 0 else 1.0)
    return w

DROP_SLOPE, DROP_CLOSE, DROP_BUF, DROP_SMOOTH, DROP_FINAL = 0.19, 16, 1.5, 10, 14

def design():
    """Outside the drop windows the old profile is the floor (unchanged track); inside, only the city's own
    requirement (+ a buffer) with short dips allowed. Ramps are limited per sample (steep in the windows), then
    the line relaxes onto that floor and gets one short final smoothing."""
    base, req, env0 = profile()
    x = np.arange(n) * ds
    inwin = np.zeros(n, bool)
    for _, a, b in DROPS: inwin |= (x >= a) & (x <= b)
    reqB = req + DROP_BUF
    w = max(1, round(DROP_CLOSE / ds)); envD = np.maximum(winmin(winmax(reqB, w), w), reqB)
    floor = np.where(inwin, envD, base)
    sl = np.where(inwin, DROP_SLOPE, DROP_SLOPE)          # ramps may start just outside a window, at the same grade
    for _ in range(3):
        for i in range(n): floor[i] = max(floor[i], floor[i - 1] - sl[i] * ds)
        for i in range(n - 1, -1, -1): floor[i] = max(floor[i], floor[(i + 1) % n] - sl[i] * ds)
    h = floor.copy()
    for _ in range(60): h = np.maximum(gauss(h, DROP_SMOOTH / ds), floor)
    h = gauss(h, DROP_FINAL / ds)
    return h, base, floor, req, inwin.astype(float)

def stats(h, req, label):
    g = np.gradient(h, ds); vc = np.gradient(g, ds)
    under = (h - req).min()
    print('%-6s maxgrade %.1f%%  min(h-req) %.2f m  lifted>12m %.0f%%  min crest R %.0f m  min sag R %.0f m' % (
        label, 100 * np.abs(g).max(), under, 100 * np.mean(h - ground > 12), 1 / max(1e-9, (-vc).max()), 1 / max(1e-9, vc.max())))
    return g, vc

if __name__ == '__main__':
    h, base, drop, req, w = design()
    stats(cur, req, 'before'); g, vc = stats(h, req, 'after')
    x = np.arange(n) * ds
    for name, a, b in DROPS:
        m = (x >= a - 200) & (x <= b + 100); seg = h[m]
        i_hi = np.argmax(seg[: max(1, len(seg) // 2)]); i_lo = np.argmin(seg)
        print('  %-20s drop %.1f m (from %.1f to %.1f), max grade in window %.1f%%' % (name, seg[:len(seg)//2].max() - seg.min(), seg[:len(seg)//2].max(), seg.min(), 100 * np.abs(g[m]).max()))
    np.save(os.path.join(OUT, 'h.npy'), h)
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 1, figsize=(18, 8), sharex=True)
    for a_, arr, t in ((ax[0], cur, 'BEFORE (b86ebbc profile)'), (ax[1], h, 'AFTER (feel pass)')):
        a_.fill_between(x, ground.min() - 5, ground, color='#6b7a8f', alpha=.5, label='street / water')
        a_.plot(x, top, color='#999', lw=.6, label='highest tile inside track width')
        a_.plot(x, arr, color='#ff2e9a' if arr is h else '#00b4d8', lw=2, label='track deck')
        for name, a, b in DROPS: a_.axvspan(a, b, color='#ffe600', alpha=.12)
        a_.set_title(t); a_.set_ylabel('m'); a_.grid(alpha=.3)
    ax[1].set_xlabel('distance along the lap (m), start at Slussen'); ax[0].legend(loc='upper right', fontsize=8)
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'profile.png'), dpi=90)
