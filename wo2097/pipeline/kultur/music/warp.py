import json, subprocess
d=json.load(open('A_plan.json')); s0=d['seg0']; e=d['srcEnd']; L=d['orchLen']
subprocess.run(['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(s0),'-to',str(e),'-i','harrison_presto.wav','-af',f'afade=t=out:st={155.4-s0}:d=0.8','-c:a','pcm_f32le','seg.wav'],check=True)
r=subprocess.run(['rubberband','--fine','-M','A_map.txt','-D',str(L),'seg.wav','orch_warp.wav'],capture_output=True,text=True); print(r.stdout[-600:],r.stderr[-600:])
