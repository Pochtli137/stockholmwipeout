"""Room for the wide sections and the tube: the highest tile hit at the arch posts (+-11.5 m) and further out (+-18 m),
relative to the new deck (design.py). A wide section needs nothing above the deck at +-11.5 m; the tube (half width
~10.5 m, top ~9.5 m over the deck) needs nothing between the deck and its top inside +-11.5 m."""
import sys, numpy as np
from prof import S, n, ds
from design import design
h = design()[0]
def rel(key): return np.array([np.nan if v is None else v for v in S[key]], float) - h
pL, pR, oL, oR = rel('postL'), rel('postR'), rel('outL'), rel('outR')
def report(a, b, label):
    i0, i1 = int(a / ds), int(b / ds); sl = slice(i0, i1)
    worst = np.nanmax(np.maximum(pL[sl], pR[sl])); worst_out = np.nanmax(np.maximum(oL[sl], oR[sl]))
    bad = np.where(np.maximum(pL[sl], pR[sl]) > -0.5)[0]
    print('%-10s %5d-%5d m  posts max %+6.1f m  out max %+6.1f m  post hits above deck: %d of %d (first at %s m)' % (
        label, a, b, worst, worst_out, len(bad), i1 - i0, None if not len(bad) else int((i0 + bad[0]) * ds)))
for arg in sys.argv[1:]:
    a, b = arg.split('-'); report(int(a), int(b), 'window')
