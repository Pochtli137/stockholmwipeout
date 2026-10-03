import subprocess, re, sys
def lufs(path, ss=None, to=None):
    cmd=['ffmpeg','-hide_banner','-nostats']+(['-ss',str(ss)] if ss is not None else [])+(['-to',str(to)] if to is not None else [])+['-i',path,'-af','ebur128=peak=true','-f','null','-']
    out=subprocess.run(cmd,capture_output=True,text=True).stderr
    s=out[out.rfind('Summary:'):]
    I=float(re.search(r'I:\s+(-?[\d.]+) LUFS',s).group(1)); LRA=float(re.search(r'LRA:\s+(-?[\d.]+) LU',s).group(1))
    pk=re.search(r'True peak:\s+Peak:\s+(-?[\d.inf]+) dBFS',s)
    return I, LRA, (float(pk.group(1)) if pk else None)
if __name__=='__main__':
    for p in sys.argv[1:]: print(p, lufs(p))
