"""Where does the city leave room for drops? Reads the tile survey (assets/survey.json) and the current profile
(assets/track.json) and lists the open stretches (nothing inside the track's width above the street)."""
import json, os, numpy as np
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '..', '..', 'assets')
S = json.load(open(os.path.join(A, 'survey.json'))); T = json.load(open(os.path.join(A, 'track.json')))
n = S['n']; ds = S['ds']

def cfill(a):
    out = list(a)
    for i in range(n):
        if out[i] is not None: continue
        p = q = i; dp = dq = 0
        while a[p] is None and dp < n: p = (p - 1) % n; dp += 1
        while a[q] is None and dq < n: q = (q + 1) % n; dq += 1
        if a[p] is not None and a[q] is not None: out[i] = (a[p] * dq + a[q] * dp) / (dp + dq)
        else: out[i] = a[p] if a[p] is not None else (a[q] or 0)
    return np.array(out, float)

ground = cfill(S['ground'])
top = cfill([None if v is None else max(v, ground[i]) for i, v in enumerate(S['top'])])
fr = np.array([f[1] for f in T['frames']])
cur = np.interp(np.arange(n) / n * len(fr), np.arange(len(fr)), fr)
if __name__ == '__main__':
    os.makedirs(os.path.join(H, 'out'), exist_ok=True)
    np.save(os.path.join(H, 'out', 'ground.npy'), ground); np.save(os.path.join(H, 'out', 'top.npy'), top); np.save(os.path.join(H, 'out', 'cur.npy'), cur)
    print('n', n, 'ds', round(ds, 3), 'len', round(S['len']))
    print('ground', round(ground.min(), 1), round(ground.max(), 1), ' top-ground median', round(float(np.median(top - ground)), 1))
    openm = (top - ground) < 3.0
    runs = []; i = 0
    while i < n:
        if openm[i]:
            j = i
            while j < n and openm[j]: j += 1
            runs.append((i * ds, (j - i) * ds, float(cur[i:j].mean() - ground[i:j].mean()), float(ground[i:j].mean())))
            i = j
        else: i += 1
    for r in sorted(runs, key=lambda r: -r[1])[:20]:
        print('open at %5.0f m, %4.0f m long, track %.1f m above ground (ground %.1f)' % r)
