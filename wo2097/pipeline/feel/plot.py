"""Before/after profile from the real track files: out/track_before.json (pre-FEEL) vs assets/track.json.
Deck height, street, highest tile inside the track width, drop windows, tubes, and the crests where the craft
lifts off (v^2 * -y'' > g + 0.5) at 100 m/s. Run: python3 plot.py -> out/profile_track.png"""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '..', '..', 'assets'); OUT = os.path.join(H, 'out')
T = json.load(open(os.path.join(A, 'track.json'))); B = json.load(open(os.path.join(OUT, 'track_before.json')))
from prof import top, n as sn, ds as sds
L = T['trackLen']
import re
AIR_AT = [int(v) for v in re.search(r'airAt:\[([^\]]*)\]', open(os.path.join(H, '..', '..', '..', 'index.html')).read()).group(1).split(',')]
def arr(J, k): return np.array([f[k] for f in J['frames']])
yA, yB, gr = arr(T, 1), arr(B, 1), arr(T, 12); N = len(yA); ds = L / N; x = np.arange(N) * ds
topx = np.interp(x, np.arange(sn) * sds, top)
def grade(y): return np.gradient(np.concatenate([y[-3:], y, y[:3]]), ds)[3:-3]
def curv(y): g = np.concatenate([y[-3:], y, y[:3]]); return np.gradient(np.gradient(g, ds), ds)[3:-3]
def crests(y, v):
    a = v * v * -curv(y); m = a > 9.81 + 0.5; runs = []; i = 0
    while i < N:
        if m[i]:
            j = i
            while j < N and m[j]: j += 1
            runs.append((i, j)); i = j
        else: i += 1
    return runs
if __name__ == '__main__':
    for v in (80, 100, 120):
        print('v %d m/s (%d km/h): lift-off crests before %d, after %d' % (v, v * 3.6, len(crests(yB, v)), len(crests(yA, v))),
              [int(a * ds) for a, b in crests(yA, v)])
    print('airtime crests (gated in the game):', AIR_AT)
    for J, lab in ((B, 'before'), (T, 'after')):
        y = arr(J, 1); g = grade(y); print('%-6s max grade %.1f%%  range %.1f..%.1f m  max 400 m fall %.1f m' % (
            lab, 100 * abs(g).max(), y.min(), y.max(), max(y[i] - y[(i + k) % N] for i in range(0, N, 4) for k in range(0, int(400 / ds), 4))))
    import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
    fig, ax = plt.subplots(3, 1, figsize=(20, 10), sharex=True, gridspec_kw={'height_ratios': [3, 3, 1.4]})
    for a_, y, t, c in ((ax[0], yB, 'BEFORE (96d2217)', '#00b4d8'), (ax[1], yA, 'AFTER (FEEL pass)', '#ff2e9a')):
        a_.fill_between(x, gr.min() - 5, gr, color='#6b7a8f', alpha=.45, label='street / water')
        a_.plot(x, topx, color='#999', lw=.5, label='highest tile inside track width')
        a_.plot(x, y, color=c, lw=2, label='track deck')
        a_.set_title(t, loc='left'); a_.set_ylabel('height (m)'); a_.grid(alpha=.3); a_.set_ylim(gr.min() - 5, max(yA.max(), yB.max()) + 8)
    for d in T['drops']:
        ax[1].axvspan(d['t0'] * L, d['t1'] * L, color='#ffe600', alpha=.13)
        ax[1].annotate('%s  -%.0f m' % (d['n'], d['drop']), (d['crest'] * L, yA[int(d['crest'] * N) % N] + 3), fontsize=8)
    for a, b in T['tubes']: ax[1].axvspan(a * L, b * L, color='#00e5ff', alpha=.25, label='tube' if a == T['tubes'][0][0] else None)
    seen = set()
    for a, b in crests(yA, 100):
        k = a + np.argmax(-curv(yA)[a:b]); on = any(abs(k * ds - c) < 70 for c in AIR_AT)
        lab = 'airtime crest (lifts off)' if on else 'crest held to the deck'
        ax[1].plot(k * ds, yA[k], 'v', color='#ffe600' if on else '#bbb', mec='k', ms=11 if on else 6, label=None if lab in seen else lab); seen.add(lab)
    ax[1].legend(loc='upper right', fontsize=8); ax[0].legend(loc='upper right', fontsize=8)
    ax[2].plot(x, 100 * grade(yB), color='#00b4d8', lw=1, label='grade before'); ax[2].plot(x, 100 * grade(yA), color='#ff2e9a', lw=1.2, label='grade after')
    ax[2].set_ylabel('%'); ax[2].grid(alpha=.3); ax[2].legend(loc='upper right', fontsize=8); ax[2].set_xlabel('distance along the lap (m), start at Slussen')
    plt.tight_layout(); plt.savefig(os.path.join(OUT, 'profile_track.png'), dpi=90); print('out/profile_track.png')
