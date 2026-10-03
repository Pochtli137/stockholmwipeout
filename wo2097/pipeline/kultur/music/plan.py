# Variant A: the warp map (Harrison's live Presto onto a straight q=160 grid) and the drum score on that grid.
import numpy as np, json
Q=160.0; Tb=180.0/Q; G0=0.05; SR=44100; RHO=0.97
d=json.load(open('mus/harrison_q160.json')); s=np.array(d['bars']); beats=np.array(d['beats']).reshape(-1,3)
NB=130; FC=152.721; SRC_END=156.2
# target bar starts and lengths
tb=np.zeros(NB+1); T=np.full(NB,Tb)
T[118]=(s[119]-s[118])*RHO            # bar 119: the climb before the last tutti keeps its breath
for k in range(NB):
    if k>0: tb[k]=tb[k-1]+T[k-1]
    else: tb[0]=G0
# time map: beat markers for bars 1..128, then bar 129 to the end at RHO
src=[s[0]-G0]; dst=[0.0]
for k in range(128):
    for j in range(3): src.append(beats[k,j]); dst.append(tb[k]+j*T[k]/3)
src.append(s[128]); dst.append(tb[128])
src.append(SRC_END); dst.append(tb[128]+(SRC_END-s[128])*RHO)
src=np.array(src); dst=np.array(dst); assert np.all(np.diff(src)>0) and np.all(np.diff(dst)>0)
seg0=src[0]
with open('mus/A_map.txt','w') as f:
    for a,b in zip(src,dst): f.write(f'{int(round((a-seg0)*SR))} {int(round(b*SR))}\n')
ORCH_LEN=dst[-1]
T_FC=tb[128]+(FC-s[128])*RHO
B0=T_FC+2*Tb; H0=B0+2*Tb
LS=G0+0.30; LE=H0+LS; FILE_END=LE+0.5
# ---- arrangement
db=np.array(json.load(open('mus/harrison_bar_db.json'))['db'])
TUTTI=[(1,39),(55,73),(85,96),(101,108),(113,115),(120,130)]
def tutti(b): return any(a<=b<=e for a,e in TUTTI)
ENTRIES=[6,55,85,101,113,120]           # the orchestra comes back: impact on the downbeat, fill + riser the bar before
SOLO_IN=[40,74,97,109,116]
ev=[]
def E(t,k,v=1.0): ev.append({'t':round(float(t),5),'k':k,'v':round(float(v),3)})
def step(b,i): return tb[b-1]+i*T[b-1]/12
HAT8=[(0,.10),(2,.16),(4,.10),(6,.16),(8,.10),(10,.16)]
def hats(b,lv=1.0,sixteen=True):
    for i,v in HAT8: E(step(b,i),'hat',v*lv)
    if sixteen:
        for i in (1,3,5,7,9,11): E(step(b,i),'hat',0.05*lv)
def full(b,var):
    if var==0:
        for i,v in ((0,1.0),(7,0.6),(10,0.85)): E(step(b,i),'kick',v)
        E(step(b,4),'snare',1.0); E(step(b,9),'snare',0.2)
    else:
        for i,v in ((0,1.0),(6,0.7),(8,0.85)): E(step(b,i),'kick',v)
        E(step(b,4),'snare',1.0); E(step(b,11),'snare',0.35)
    hats(b)
def light(b):
    E(step(b,0),'kick',0.9); E(step(b,8),'kick',0.55); E(step(b,4),'snare',0.5); hats(b,0.85,False)
def fill(b,big):
    for i,v in ((0,1.0),(7,0.6)): E(step(b,i),'kick',v)
    E(step(b,4),'snare',1.0); E(step(b,8),'kick',0.8)
    rng=range(6,12) if big else range(8,12)
    n=len(rng)
    for j,i in enumerate(rng): E(step(b,i),'snare',0.35+0.65*(j+1)/n)
    for i,v in HAT8[:3]: E(step(b,i),'hat',v)
def riser_into(t_next): E(t_next-1.7,'riser',1.0)
sec_start=1
for b in range(1,NB+1):
    if b in ENTRIES or b in SOLO_IN or b==1: sec_start=b
    nxt=b+1
    if b<=4:                       # RIDÅ: the storm alone with a three-on-the-floor pulse
        for i in (0,4,8): E(step(b,i),'kick',0.95)
        continue
    if b==5:                       # the fermata: the orchestra holds its breath, the drums fill it
        for j,i in enumerate(range(5,12)): E(step(b,i),'snare',0.3+0.7*(j+1)/7)
        riser_into(tb[5]); continue
    if b==119:                     # the climb before the last tutti: a downbeat and a riser, no grid
        E(step(b,0),'kick',0.9); riser_into(tb[119]); continue
    if b==129:                     # the last ritardando: the drums stop on the downbeat, the final chord gets the impact
        E(step(b,0),'kick',1.0); E(step(b,0),'snare',1.0); E(step(b,0),'impact',0.8)
        E(T_FC,'kick',1.0); E(T_FC,'impact',1.0); continue
    if b==130: continue
    if b in ENTRIES: E(step(b,0),'impact',0.8)
    if nxt in ENTRIES:
        fill(b,True); riser_into(tb[nxt-1]); continue
    if b==54: E(step(b,0),'kick',0.9); continue
    loud=tutti(b) and db[b-1]>=-3.5
    pos=b-sec_start
    if loud and pos%8==7: fill(b,True); continue
    if loud and pos%4==3: fill(b,False); continue
    if loud: full(b,pos%2)
    else: light(b)
# the bridge: two bars of break while the last chord dies, then the storm again
tbr=lambda i,j: B0+i*Tb+j*Tb/12
for i,v in ((0,1.0),(7,0.6),(10,0.85)): E(tbr(0,i),'kick',v)
E(tbr(0,4),'snare',1.0)
for i,v in HAT8: E(tbr(0,i),'hat',v)
for i in (1,3,5,7,9,11): E(tbr(0,i),'hat',0.05)
E(tbr(1,0),'kick',1.0); E(tbr(1,4),'snare',1.0)
for j,i in enumerate(range(6,12)): E(tbr(1,i),'snare',0.35+0.65*(j+1)/6)
E(H0+G0-1.7,'riser',1.0)
# the head again (same drums as bars 1-2) so the loop seam sits inside identical audio
for e in list(ev):
    if e['t']<G0+2*Tb and e['k']=='kick' and e['t']<tb[2]: E(e['t']+H0,'kick',e['v'])
ev.sort(key=lambda e:e['t'])
plan={'Q':Q,'Tb':Tb,'G0':G0,'seg0':float(seg0),'srcEnd':SRC_END,'orchLen':float(ORCH_LEN),'T_FC':float(T_FC),'B0':float(B0),'H0':float(H0),
      'loopStart':float(LS),'loopEnd':float(LE),'fileEnd':float(FILE_END),'events':ev,'tb':tb.tolist()}
json.dump(plan,open('mus/A_plan.json','w'))
from collections import Counter
print('orch len',round(ORCH_LEN,3),'final chord',round(T_FC,3),'B0',round(B0,3),'H0',round(H0,3),'loop',round(LS,3),'->',round(LE,3),'file',round(FILE_END,3))
print('events',len(ev),Counter(e['k'] for e in ev))
