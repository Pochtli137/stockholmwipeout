import librosa, numpy as np, pretty_midi, sys, json, scipy.signal as ss
import matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
wav=sys.argv[1]; tag=sys.argv[2]
sr=22050; H=256
y,_=librosa.load(wav,sr=sr,mono=True)
pm=pretty_midi.PrettyMIDI('score/summer-score-2.mid')
ym=pm.synthesize(fs=sr,wave=lambda x: ss.sawtooth(x)*0.5)
ym=ym/np.abs(ym).max()
def lead(sig):
    e=librosa.feature.rms(y=sig,hop_length=256)[0]; th=0.05*e.max(); i=np.argmax(e>th); return max(0,i*256-512)
la=lead(y); lm=lead(ym); print('lead audio',la/sr,'lead midi',lm/sr)
y=y[la:]; ym=ym[lm:]
def feats(sig):
    C=librosa.feature.chroma_cqt(y=sig,sr=sr,hop_length=H,bins_per_octave=36,n_octaves=6)
    C=librosa.util.normalize(np.log1p(20*C)+1e-4,axis=0)
    # onset novelty (spectral flux) per frame, normalized
    o=librosa.onset.onset_strength(y=sig,sr=sr,hop_length=H); o=o/(np.percentile(o,99)+1e-9)
    rms=librosa.feature.rms(y=sig,hop_length=H)[0]; rms=np.log1p(50*rms/rms.max())
    n=min(C.shape[1],len(o),len(rms))
    return np.vstack([C[:,:n], 0.6*o[None,:n].clip(0,1.5), 0.8*rms[None,:n]])
Fa=feats(y); Fm=feats(ym)
D,wp=librosa.sequence.dtw(X=Fm,Y=Fa,metric='euclidean',step_sizes_sigma=np.array([[1,1],[0,1],[1,0],[2,1],[1,2]]),weights_add=np.array([0,0.05,0.05,0,0]),weights_mul=np.array([1,1,1,2,2]))
wp=wp[::-1]; fs=sr/H
um=np.unique(wp[:,0]); amap=np.array([np.mean(wp[wp[:,0]==u,1]) for u in um])/fs; um=um/fs
beats_m=pm.get_beats()
beats_a=np.interp(beats_m-lm/sr,um,amap)+la/sr
json.dump({'beats_midi':beats_m.tolist(),'beats_dtw':beats_a.tolist(),'path':[um.tolist(),amap.tolist()]},open(f'mus/{tag}_align.json','w'))
ibi=np.diff(beats_a)
print(tag,'first beats',beats_a[:16].round(2)); print('around fermata (beats 12-18)',beats_a[12:19].round(2)); print('last',beats_a[-6:].round(2))
print('q median',round(60/np.median(ibi),1))
fig,ax=plt.subplots(1,1,figsize=(18,5)); ax.plot(beats_a[1:],60/ibi,'.',ms=3); ax.set_ylim(60,300); plt.savefig(f'mus/{tag}_tempo.png',dpi=60)
