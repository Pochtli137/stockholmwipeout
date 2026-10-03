import subprocess, sys, json
import os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from lufs import lufs
def master(src,dst_wav,target=-16.0,ss=None,to=None,fade=None):
    I,_,_=lufs(src,ss,to); g=target-I
    af=f'volume={g:.3f}dB,alimiter=limit=0.76:attack=3:release=60:level=0:latency=1'
    if fade: af+=f',afade=t=out:st={fade[0]}:d={fade[1]}'
    cmd=['ffmpeg','-hide_banner','-loglevel','error','-y']+(['-ss',str(ss)] if ss is not None else [])+(['-to',str(to)] if to is not None else [])+['-i',src,'-af',af,'-ar','44100','-c:a','pcm_f32le',dst_wav]
    subprocess.run(cmd,check=True); return g
def mp3(wav,out,kbps=160):
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',wav,'-c:a','libmp3lame','-b:a',f'{kbps}k','-ar','44100',out],check=True)
if __name__=='__main__':
    P=json.load(open('mus/A_plan.json'))
    # loudness of one pass of the loop sets the gain for the whole file
    I,_,_=lufs('mus/A_mix_raw.wav',0,P['H0']); g=-16.0-I
    subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i','mus/A_mix_raw.wav','-af',f'volume={g:.3f}dB,alimiter=limit=0.76:attack=3:release=60:level=0:latency=1','-c:a','pcm_f32le','mus/A_full.wav'],check=True)
    mp3('mus/A_full.wav','mus/kulturstockholm_vivaldi_presto_breakbeat.mp3')
    print('A full: gain',round(g,2), lufs('mus/kulturstockholm_vivaldi_presto_breakbeat.mp3',0,P['H0']))
