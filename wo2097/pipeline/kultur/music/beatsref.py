# beat-level markers inside the tracked bars, then the rubberband time map to a straight grid
import librosa, numpy as np, json, sys, scipy.ndimage as nd
tag=sys.argv[1]; wav=sys.argv[2]; Q=float(sys.argv[3]); G0=0.05
sr=22050; Ho=64; y,_=librosa.load(wav,sr=sr,mono=True)
O=librosa.onset.onset_strength(y=y,sr=sr,hop_length=Ho,lag=1,max_size=3); O=nd.gaussian_filter1d(O,1.5)
w=int(2*sr/Ho); mu=nd.uniform_filter1d(O,w); sd=np.sqrt(nd.uniform_filter1d((O-mu)**2,w))+1e-6; On=((O-mu)/sd).clip(-1,6); fps=sr/Ho
def Oat(t):
    t=np.asarray(t); i=t*fps; i0=np.floor(i).astype(int).clip(0,len(On)-2); f=i-i0; return On[i0]*(1-f)+On[i0+1]*f
s=np.array(json.load(open(f'mus/{tag}_bars.json'))['bars'])
NB=len(s); Lmed=np.median(np.diff(s))
s[4]=s[3]+Lmed*1.0   # bar 5 (fermata) starts one ordinary bar after bar 4: bar 4 ends in an eighth rest, the silence is the fermata
beats=[]
Wb=np.array([2,1,1.5,1.]); sh=np.arange(-0.03,0.0301,0.002)
for k in range(NB):
    a=s[k]; L=(s[k+1]-a) if k<NB-1 else Lmed
    bb=[a]
    for j in (1,2):
        t0=a+j*L/3; best=None
        if k==4: bb.append(t0); continue
        sc=[(Wb*Oat(t0+x+np.arange(4)*L/12)).sum()-0.4*(x/0.02)**2 for x in sh]; bb.append(t0+sh[int(np.argmax(sc))])
    beats+=bb
beats=np.array(beats)
# residuals on the beat grid: best shift of a 4-tooth comb, per beat
res=[]
for i in range(len(beats)-1):
    if 12<=i<=14: continue
    L=beats[i+1]-beats[i]; sc=[(Wb*Oat(beats[i]+x+np.arange(4)*L/4)).sum() for x in np.arange(-0.04,0.0401,0.002)]; res.append(np.arange(-0.04,0.0401,0.002)[int(np.argmax(sc))]*1000)
res=np.array(res); print('beat residual |<8ms|',(abs(res)<8).mean().round(2),'|<15ms|',(abs(res)<15).mean().round(2),'p90',np.percentile(abs(res),90).round(1))
Tb=180.0/Q
# end of the final chord's decay in the source
rms=librosa.feature.rms(y=y,hop_length=512)[0]; tr=np.arange(len(rms))*512/sr; thr=rms.max()*10**(-50/20)
last=tr[np.where(rms>thr)[0][-1]]; print('decay ends at',round(last,2),'last bar start',round(s[-1],2))
SR=44100
src=[max(0.0,s[0]-G0)]; dst=[0.0]
for i,b in enumerate(beats): src.append(b); dst.append(G0+i*Tb/3)
src.append(last); dst.append(G0+(NB-1)*Tb+(last-s[-1]))
src=np.array(src); dst=np.array(dst)
assert np.all(np.diff(src)>0) and np.all(np.diff(dst)>0)
r=np.diff(dst)/np.diff(src); print('stretch ratio min',r.min().round(3),'max',r.max().round(3),'median',np.median(r).round(3))
with open(f'mus/{tag}_q{int(Q)}.map','w') as f:
    for a,b in zip(src-src[0],dst): f.write(f'{int(round(a*SR))} {int(round(b*SR))}\n')
json.dump({'Q':Q,'Tb':Tb,'G0':G0,'srcStart':float(src[0]),'srcEnd':float(src[-1]),'dstEnd':float(dst[-1]),'beats':beats.tolist(),'bars':s.tolist()},open(f'mus/{tag}_q{int(Q)}.json','w'))
print('target length',round(dst[-1],3),'s; bars',NB)
