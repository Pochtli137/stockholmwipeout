"""DISTRICT ENTRIES (Kim, 2026-09-29: "Entering Kungsholmen roll osv, ta med alla stadsdelar").
One cached Overpass query for Stockholm's stadsdelar (boundary=administrative, admin_level=10, inside the lap's bbox),
the calibrated centreline from assets/track.json tested against the polygons, and every district change written back
to track.json as `districts: [{t, name}]` (t = lap fraction where the racing line enters it). Pure python, no deps.
    python3 districts.py            (osm/districts_overpass.json is fetched once and never again)"""
import json, os, math, urllib.request, urllib.parse
import sys
BANA=sys.argv[1] if len(sys.argv)>1 else 'stockholm'   # 'kultur': WIPEOUT KULTURSTOCKHOLM (its own track.json and Overpass cache)
H=os.path.dirname(os.path.abspath(__file__)); TJ=os.path.join(H,'..','assets','kultur' if BANA=='kultur' else '','track.json'); CACHE=os.path.join(H,'osm','districts_overpass_kultur.json' if BANA=='kultur' else 'districts_overpass.json')
LAT0,LON0=59.328,18.06; M_LAT=111320; M_LON=111320*math.cos(math.radians(LAT0))
D=json.load(open(TJ)); F=D['frames']; N=len(F)
ll=[(LAT0+f[2]/M_LAT, LON0-f[0]/M_LON) for f in F]
s,w,n,e=min(a for a,_ in ll)-0.004,min(b for _,b in ll)-0.006,max(a for a,_ in ll)+0.004,max(b for _,b in ll)+0.006
if not os.path.exists(CACHE):
    q=f'[out:json][timeout:60];relation["boundary"="administrative"]["admin_level"="10"]({s},{w},{n},{e});out geom;'
    req=urllib.request.Request('https://overpass-api.de/api/interpreter',data=urllib.parse.urlencode({'data':q}).encode(),headers={'User-Agent':'stockholmwipeout-districts/1 (hobby game, one cached query)'})
    open(CACHE,'wb').write(urllib.request.urlopen(req,timeout=90).read())
R=json.load(open(CACHE))
def rings(rel):   # join the outer member ways into closed rings
    segs=[[(p['lat'],p['lon']) for p in m['geometry']] for m in rel['members'] if m.get('type')=='way' and m.get('role','outer') in ('outer','') and m.get('geometry')]
    out=[]
    while segs:
        ring=segs.pop(0)
        while ring[0]!=ring[-1] and segs:
            for i,sg in enumerate(segs):
                if sg[0]==ring[-1]: ring+=sg[1:]; segs.pop(i); break
                if sg[-1]==ring[-1]: ring+=sg[::-1][1:]; segs.pop(i); break
            else: break
        out.append(ring)
    return out
def inside(pt,ring):
    y,x=pt; c=False
    for (y1,x1),(y2,x2) in zip(ring,ring[1:]+ring[:1]):
        if (y1>y)!=(y2>y) and x < (x2-x1)*(y-y1)/(y2-y1)+x1: c=not c
    return c
polys=[(r['tags'].get('name','?'),rings(r)) for r in R['elements'] if r.get('type')=='relation']
def where(pt):
    for name,rs in polys:
        if sum(inside(pt,rg) for rg in rs)%2==1: return name
    return None
seq=[where(p) for p in ll]
# smooth out flicker along borders: a district must hold for 40 frames (~190 m) to count
entries=[]; cur=None; i=0
while i<N:
    nm=seq[i]
    if nm and nm!=cur:
        j=i
        while j<N and seq[j]==nm: j+=1
        if j-i>=40 or not entries: entries.append(dict(t=round(i/N,4),name=nm)); cur=nm
        i=j; continue
    i+=1
from runes import runes
for e in entries: e['rn']=runes(e['name'].upper())   # the runic subtitle under the title
D['districts']=entries; json.dump(D,open(TJ,'w'),separators=(',',':'))
print('districts:',[(e['name'],e['t']) for e in entries]); print('polygons in bbox:',sorted(set(n for n,_ in polys)))
