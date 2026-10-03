# DP bar tracker: 130 bars of 3/4, each bar = 12 sixteenths. DTW gives the prior; a 16th comb on the onset envelope decides.
import librosa, numpy as np, json, sys, scipy.ndimage as nd
tag=sys.argv[1]; wav=sys.argv[2]
d=json.load(open(f'mus/{tag}_align.json')); bd=np.array(d['beats_dtw'])
sr=22050; Ho=64; y,_=librosa.load(wav,sr=sr,mono=True)
O=librosa.onset.onset_strength(y=y,sr=sr,hop_length=Ho,lag=1,max_size=3)
O=nd.gaussian_filter1d(O,1.5)
# local normalisation over ~2 s
w=int(2*sr/Ho); mu=nd.uniform_filter1d(O,w); sd=np.sqrt(nd.uniform_filter1d((O-mu)**2,w))+1e-6
On=((O-mu)/sd).clip(-1,6)
fps=sr/Ho
def Oat(t):
    i=t*fps; i0=np.floor(i).astype(int).clip(0,len(On)-2); f=i-i0; return On[i0]*(1-f)+On[i0+1]*f
NB=130
s_dtw=bd[0::3][:NB]               # bar starts (beat 0 of each bar)
L_dtw=np.diff(np.append(s_dtw, bd[-1]+np.median(np.diff(bd))))  # rough
Ls=nd.median_filter(L_dtw,5)
W=np.array([3,1,1.5,1, 2,1,1.5,1, 2,1,1.5,1.]); W/=W.sum()
step=0.003; R=0.13; offs=np.arange(-R,R+1e-9,step)
REST={4}          # bar 5 is the fermata (silence)
cand=[s_dtw[k]+offs for k in range(NB)]
prior=lambda o: 0.5*(o/0.07)**2
lam=60.0
# score for bar k given start a and next start b
def comb(a,b):
    L=b-a; j=np.arange(12)[None,None,:]
    return (W[None,None,:]*Oat(a[:,:,None]+j*L[:,:,None]/12)).sum(-1)
cost=[prior(offs)]; back=[]
for k in range(1,NB):
    a=cand[k-1][:,None]; b=cand[k][None,:]
    A=np.broadcast_to(a,(len(offs),len(offs))); B=np.broadcast_to(b,(len(offs),len(offs)))
    if (k-1) in REST: obs=np.zeros(A.shape); pen=np.zeros(A.shape)
    else:
        obs=-4.0*comb(A,B); L=B-A; pen=lam*np.log(np.maximum(L,1e-3)/Ls[k-1])**2
        pen[L<=0.3]=1e9
    tot=cost[-1][:,None]+obs+pen
    bi=np.argmin(tot,axis=0); back.append(bi); cost.append(tot[bi,np.arange(len(offs))]+prior(offs))
# last bar: score with its prior length
i=int(np.argmin(cost[-1])); path=[i]
for k in range(NB-2,-1,-1): i=back[k][i]; path.append(i)
path=path[::-1]
s=np.array([cand[k][path[k]] for k in range(NB)])
Lb=np.diff(s)
print('bar starts first 8',s[:8].round(3)); print('last 4',s[-4:].round(3))
print('offset vs dtw ms: median',np.median((s-s_dtw)*1000).round(1),'p90 abs',np.percentile(abs(s-s_dtw)*1000,90).round(1),'at edge',(abs(s-s_dtw)>R-0.004).sum())
q=180/Lb; print('q per bar: median',np.median(q).round(1),'min',q.min().round(1),'max',q.max().round(1))
print('bars with q outside 135-185:',[(k+1,round(q[k],1)) for k in range(len(q)) if (q[k]<135 or q[k]>185) and k not in REST])
# per-bar residual: best local shift of the comb (+-60 ms) given the tracked bar
res=[]
for k in range(NB-1):
    if k in REST: continue
    sh=np.arange(-0.06,0.0601,0.002); sc=[(W*Oat(s[k]+sh_+np.arange(12)*Lb[k]/12)).sum() for sh_ in sh]; res.append(sh[int(np.argmax(sc))]*1000)
res=np.array(res); print('residual best-shift ms: |res|<10',(abs(res)<10).mean().round(2),'<20',(abs(res)<20).mean().round(2),'p90',np.percentile(abs(res),90).round(1))
json.dump({'bars':s.tolist()},open(f'mus/{tag}_bars.json','w'))
