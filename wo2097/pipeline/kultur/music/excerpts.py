import sys, subprocess; import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from lufs import lufs; from master import mp3
def excerpt(src,ss,dur,out,target=-16.0):
    tmp=f'mus/_ex.wav'
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(ss),'-t',str(dur),'-i',src,'-ar','44100','-ac','2','-c:a','pcm_f32le',tmp],check=True)
    for it in range(3):   # the limiter shaves a little: iterate the gain until the mp3 sits on target
        I,_,_=lufs(tmp) if it==0 else (I,None,None)
        g=target-I+(0 if it==0 else corr)
        subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',tmp,'-af',f'volume={g:.3f}dB,alimiter=limit=0.76:attack=3:release=60:level=0:latency=1,afade=t=in:d=0.02,afade=t=out:st={dur-2.5}:d=2.5','-c:a','pcm_f32le','mus/_ex2.wav'],check=True)
        mp3('mus/_ex2.wav',out); Io,_,tp=lufs(out)
        corr=(0 if it==0 else corr)+(target-Io)
        if abs(target-Io)<0.15: break
    print(out, 'I',Io,'TP',tp)
excerpt('mus/A_full.wav',0.0,60,'mus/prov_a.mp3')
excerpt('mus/harrison_presto.wav',1.0,60,'mus/prov_b.mp3')
excerpt('mus/advent_brand3_1.wav',0.85,60,'mus/prov_c.mp3')
