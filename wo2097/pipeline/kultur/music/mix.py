import numpy as np, soundfile as sf, json, subprocess, sys
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from lufs import lufs
SR=44100; P=json.load(open('mus/A_plan.json'))
DRUM_DB=float(sys.argv[1]) if len(sys.argv)>1 else -3.0
orch,_=sf.read('mus/orch_warp.wav',dtype='float32'); dr,_=sf.read('mus/drums_all.wav',dtype='float32'); kk,_=sf.read('mus/drums_kick.wav',dtype='float32')
N=int(round(P['fileEnd']*SR)); H0=int(round(P['H0']*SR))
O=np.zeros((N,2),np.float32); O[:min(N,len(orch))]+=orch[:N]
M=N-H0; O[H0:H0+M]+=orch[:M]                       # the head again after the bridge: the loop seam sits inside identical audio
Io,_,_=lufs('mus/orch_warp.wav'); go=10**((-18.0-Io)/20); O*=go
gd=10**(DRUM_DB/20); D=dr[:N]*gd; K=kk[:N]*gd
# sidechain: the kick pumps the strings a little (peak follower, 3 ms attack, 140 ms release, ~3 dB on a full kick)
x=np.abs(K).max(1); a=np.exp(-1/(0.003*SR)); r=np.exp(-1/(0.140*SR)); env=np.zeros(N,np.float32); e=0.0
for i in range(N):
    v=x[i]; e=v if v>e else e*r+(1-r)*v if False else (a*e+(1-a)*v if v>e else r*e); env[i]=e
T=-8.0; R=2.5; lev=20*np.log10(env+1e-9); gr=np.maximum(0,lev-T)*(1-1/R); gain=10**(-gr/20)
mix=O*gain[:,None]+D
sf.write('mus/A_mix_raw.wav',mix,SR,subtype='FLOAT')
print('max GR dB',gr.max().round(2),'orch gain',round(20*np.log10(go),2),'peak',np.abs(mix).max().round(3))
