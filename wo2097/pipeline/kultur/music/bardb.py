# loudness of every bar relative to the median (decides full kit or light kit in plan.py)
import librosa, numpy as np, json
y,sr=librosa.load('mus/harrison_presto.wav',sr=22050,mono=True)
s=np.array(json.load(open('mus/harrison_q160.json'))['bars']); e=np.append(s[1:],s[-1]+1.2)
db=np.array([20*np.log10(np.sqrt(np.mean(y[int(a*sr):int(b*sr)]**2))+1e-9) for a,b in zip(s,e)])
json.dump({'db':(db-np.median(db)).tolist()},open('mus/harrison_bar_db.json','w'))
