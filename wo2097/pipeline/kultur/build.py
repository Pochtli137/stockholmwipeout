"""WIPEOUT KULTURSTOCKHOLM · the track set, built in Blender over its calibrated centreline (a copy of neon/build.py, re-dressed).
Reads ../../assets/kultur/track.json (BANA=kultur node dump_track.cjs) and tex/ (make_textures.py, from copy.json). No neon
corporate, no party boards, no jump: limestone deck, gallery-label walls, gold leaf where Stockholm has neon, festival banners
over the track, the gantry at Börshuset, the restaurant boards and the two pit lanes (Riche, Den Gyldene Freden).
Everything is modelled in the game's own frame (+X west, +Y up, +Z north; Blender gets (x,-z,y), the glTF export
turns it back), so the glb lands exactly on the tiles. Exports ../assets/track.glb (the craft: build_craft.py).

    blender -b --factory-startup -P build.py -- [--nobake]"""
import bpy, bmesh, os, sys, json, math, time
import numpy as np
HERE=os.path.dirname(os.path.abspath(__file__)); TEX=os.path.join(HERE,'tex'); SHARED=os.path.abspath(os.path.join(HERE,'..','..','assets','kultur')); OUT=SHARED
COPY=json.load(open(os.path.join(SHARED,'copy.json')))
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []; NOBAKE='--nobake' in argv
PROBE=argv[argv.index('--probe')+1] if '--probe' in argv else None   # write the set pieces' boxes to this json and stop (setpieces_probe.cjs)
T0=time.time()
def log(*a): print(f'[{time.time()-T0:6.1f}s]',*a,flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene
D=json.load(open(os.path.join(SHARED,'track.json')))
FR=np.array([[np.nan if v is None else v for v in f] for f in D['frames']],np.float64); SEG=len(FR); L=D['trackLen']; HW=D['halfW']
# the survey, per frame and relative to the track surface: the highest tile hit at the arch posts (+-11.5 m) and at the
# billboards (+-18 m). Negative = below the deck. Set pieces only go where the tiles leave room for them.
CLR=np.array([[np.nan if v is None else v for v in c] for c in D.get('clear',[[None]*4]*SEG)],np.float64)
NB=len([f for f in os.listdir(TEX) if f.startswith('bill_')])
def clear_at(t): return CLR[int(round((t%1.0)*SEG))%SEG]
# FEEL (2026-09-30): per-frame half width (wide quiet sections) and the jump gaps, from the dump; the bank is already
# in the frames' right/up vectors. The tubes are gone (Kim: "remove the tunnel thingie bars").
HWA=np.array(D['hw'],np.float64) if 'hw' in D else np.full(SEG,HW)
def hw_at(t): x=(t%1.0)*SEG; i=int(x)%SEG; k=x-int(x); return HWA[i]*(1-k)+HWA[(i+1)%SEG]*k
GAPS=D.get('gaps',[])
START_T=D.get('start',{}).get('m',0.0)/L   # the start/finish line and the gantry: mid Guldbron since 2026-10-02 (FEEL.startM)
def in_gap(t,margin=0.0):   # THE JUMP: no deck, barrier, pylon or pad between the lip and the landing
    t=t%1.0; return any(a-margin<=t<=b+margin for a,b in GAPS)
BAR_H, SLAB = 1.7, 0.9
def G2B(v): return (v[0],-v[2],v[1])      # game frame -> Blender (glTF export maps it back)

# ------------------------------------------------------------------ materials
def img(n): return bpy.data.images.load(os.path.join(TEX,n),check_existing=True)
MATS={}
def mat(name,col=(1,1,1),rough=0.5,metal=0.0,tex=None,emit_tex=None,emit_col=None,emit=0.0,double=False):
    if name in MATS: return MATS[name]
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; bs=nt.nodes['Principled BSDF']
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if tex: t=nt.nodes.new('ShaderNodeTexImage'); t.image=img(tex); nt.links.new(t.outputs['Color'],bs.inputs['Base Color'])
    else: bs.inputs['Base Color'].default_value=(*col,1)
    if emit_tex: t=nt.nodes.new('ShaderNodeTexImage'); t.image=img(emit_tex); nt.links.new(t.outputs['Color'],bs.inputs['Emission Color'])
    elif emit_col: bs.inputs['Emission Color'].default_value=(*emit_col,1)
    if emit_tex or emit_col: bs.inputs['Emission Strength'].default_value=emit
    m.use_backface_culling=not double
    MATS[name]=m; return m
def srgb(h): h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]; return tuple((x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4) for x in c)

# ------------------------------------------------------------------ a small mesh builder in game coordinates
class MB:
    def __init__(s): s.v=[]; s.f=[]; s.uv=[]; s.mi=[]; s.mats=[]; s.boxes=[]
    def m(s,mat):
        if mat not in s.mats: s.mats.append(mat)
        return s.mats.index(mat)
    def quad(s,a,b,c,d,mat,uv=((0,0),(1,0),(1,1),(0,1))):
        i=len(s.v); s.v+= [a,b,c,d]; s.f.append((i,i+1,i+2,i+3)); s.uv.append(uv); s.mi.append(s.m(mat))
    def poly(s,pts,mat):
        i=len(s.v); s.v+=list(pts); s.f.append(tuple(range(i,i+len(pts)))); s.uv.append(tuple((0,0) for _ in pts)); s.mi.append(s.m(mat))
    def box(s,T,cx,cy,cz,w,h,d,mat,top_uv=False):   # T maps a local point to game coords
        x0,x1,y0,y1,z0,z1=cx-w/2,cx+w/2,cy-h/2,cy+h/2,cz-d/2,cz+d/2
        P=lambda x,y,z:T((x,y,z))
        s.boxes.append((PART,[tuple(float(c) for c in P(x,y,z)) for x in (x0,x1) for y in (y0,y1) for z in (z0,z1)]))
        s.quad(P(x0,y1,z1),P(x1,y1,z1),P(x1,y1,z0),P(x0,y1,z0),mat,((0,0),(1,0),(1,1),(0,1)) if top_uv else ((0,0),)*4)   # top
        for q in ((P(x0,y0,z0),P(x1,y0,z0),P(x1,y0,z1),P(x0,y0,z1)),(P(x0,y0,z1),P(x1,y0,z1),P(x1,y1,z1),P(x0,y1,z1)),
                  (P(x1,y0,z0),P(x0,y0,z0),P(x0,y1,z0),P(x1,y1,z0)),(P(x1,y0,z1),P(x1,y0,z0),P(x1,y1,z0),P(x1,y1,z1)),
                  (P(x0,y0,z0),P(x0,y0,z1),P(x0,y1,z1),P(x0,y1,z0))): s.quad(*q,mat,((0,0),)*4)
    def build(s,name,coll=None,recalc=False):
        me=bpy.data.meshes.new(name); me.from_pydata([G2B(v) for v in s.v],[],s.f); me.update()
        if recalc:   # closed solids: point every face outwards so backface culling never eats one
            bm=bmesh.new(); bm.from_mesh(me); bmesh.ops.recalc_face_normals(bm,faces=bm.faces); bm.to_mesh(me); bm.free()
        for mt in s.mats: me.materials.append(mt)
        me.polygons.foreach_set('material_index',np.array(s.mi,np.int32))
        uvl=me.uv_layers.new(name='UVMap'); flat=[c for fu in s.uv for uv in fu for c in uv]; uvl.data.foreach_set('uv',flat)
        me.validate(); ob=bpy.data.objects.new(name,me); (coll or scene.collection).objects.link(ob)
        if coll is not None and coll.name=='setpieces': SETBOXES.extend(dict(obj=name,part=pt,c=c) for pt,c in s.boxes)
        return ob

PART=''; SETBOXES=[]   # every set-piece box, tagged, for the tile-clipping probe
def frame(i):
    f=FR[i%SEG]; return f[0:3],f[3:6],f[6:9],f[9:12],f[12]
def at(t):   # interpolate the dumped frames at track parameter t
    x=(t%1.0)*SEG; i=int(x); k=x-i; a=FR[i%SEG]; b=FR[(i+1)%SEG]; f=a*(1-k)+b*k
    p,r,u,fw=f[0:3],f[3:6],f[6:9],f[9:12]; r=r/np.linalg.norm(r); u=u/np.linalg.norm(u); fw=fw/np.linalg.norm(fw)
    return p,r,u,fw,f[12]
def local(p,r,u,fw,rot=0.0,lat=0.0,lift=0.0):   # local frame: x right, y up, z = -forward (backwards)
    c,s_=math.cos(rot),math.sin(rot); base=p+r*lat+u*lift
    def T(q):
        x,y,z=q; x,z=x*c+z*s_, -x*s_+z*c
        return tuple(base+r*x+u*y-fw*z)
    return T

# ------------------------------------------------------------------ the track
trk=bpy.data.collections.new('track'); scene.collection.children.link(trk)
m_surf=mat('track_surface',tex='track.jpg',emit_tex='track_e.jpg',emit=0.6,rough=0.75,metal=0.05)   # honed limestone with brass inlays
m_under=mat('track_under',col=(0.42,0.39,0.34),rough=0.8,metal=0.0,double=True)
m_barL=mat('barrier_L',tex='barrier_L.jpg',emit_tex='barrier_L.jpg',emit=0.12,rough=0.7,metal=0.0,double=True)
m_barR=mat('barrier_R',tex='barrier_R.jpg',emit_tex='barrier_R.jpg',emit=0.12,rough=0.7,metal=0.0,double=True)
# no party sections on this track (Kim's brief: no political party ads in Kulturstockholm)
m_neonL=mat('neon_L',col=srgb('#b8901c'),emit_col=srgb('#f0c860'),emit=0.9,double=True,metal=0.8,rough=0.3); m_neonR=mat('neon_R',col=srgb('#d8d0bc'),emit_col=srgb('#fff4dc'),emit=0.8,double=True)
m_neonY=mat('neon_Y',col=srgb('#b8901c'),emit_col=srgb('#f4d77c'),emit=0.8,metal=0.9,rough=0.25)
m_pad=mat('pad_speed',col=(0,0,0),emit_tex='pad_speed.png',emit=1.6,double=True); m_wpad=mat('pad_weapon',col=(0,0,0),emit_tex='pad_weapon.png',emit=1.6,double=True)
m_metal=mat('frame_metal',col=(0.10,0.085,0.07),rough=0.38,metal=0.85); m_haz=mat('gold_band',col=srgb('#b8901c'),rough=0.3,metal=0.95)
m_stone=mat('pylon_stone',col=(0.56,0.52,0.46),rough=0.85,metal=0.0)

S=MB(); U=MB(); B=MB(); N=MB()
dist=0.0; dl=L/SEG
for i in range(SEG):
    if in_gap((i+0.5)/SEG): continue
    p0,r0,u0,f0,g0=frame(i); p1,r1,u1,f1,g1=frame(i+1); v0=i*dl/32; v1=(i+1)*dl/32
    HW0,HW1=HWA[i%SEG],HWA[(i+1)%SEG]
    Lp0,Rp0,Lp1,Rp1=p0-r0*HW0,p0+r0*HW0,p1-r1*HW1,p1+r1*HW1
    S.quad(tuple(Lp0),tuple(Rp0),tuple(Rp1),tuple(Lp1),m_surf,((0,v0),(1,v0),(1,v1),(0,v1)))
    # slab: bottom and both skirts
    e0,e1=HW0+0.4,HW1+0.4
    U.quad(tuple(p0+r0*e0-u0*SLAB),tuple(p0-r0*e0-u0*SLAB),tuple(p1-r1*e1-u1*SLAB),tuple(p1+r1*e1-u1*SLAB),m_under)
    for sd in (-1,1):
        a0=p0+r0*sd*e0; a1=p1+r1*sd*e1
        U.quad(tuple(a0-u0*SLAB),tuple(a1-u1*SLAB),tuple(a1),tuple(a0),m_under)
        # barrier wall (text runs forward on the left wall, backwards on the right so it reads from the track)
        w0=p0+r0*sd*(HW0+0.2); w1=p1+r1*sd*(HW1+0.2); ua,ub=(i*dl/104,(i+1)*dl/104) if sd<0 else (-(i*dl/104),-((i+1)*dl/104))   # one 8192 px barrier texture per 104 m
        B.quad(tuple(w0),tuple(w1),tuple(w1+u1*BAR_H),tuple(w0+u0*BAR_H),(m_barL if sd<0 else m_barR),((ua,0),(ub,0),(ub,1),(ua,1)))
        mn=m_neonL if sd<0 else m_neonR; n0=p0+r0*sd*(HW0+0.15); n1=p1+r1*sd*(HW1+0.15)
        for h0,h1 in ((BAR_H,BAR_H+0.22),(0.04,0.16)): N.quad(tuple(n0+u0*h0),tuple(n1+u1*h0),tuple(n1+u1*h1),tuple(n0+u0*h1),mn)
S.build('track_surface',trk); U.build('track_under',trk); B.build('track_barriers',trk); N.build('track_neon',trk)
log('track ribbons',SEG,'segments')

# ------------------------------------------------------------------ THE JUMP: the lip and the landing
# The deck just stops: a hazard-striped face and a bright yellow neon bar across the lip, the same on the landing edge,
# and a yellow chevron band on the last 30 m of the ramp so the launch reads from far off.
JB=MB()
for k,(a,b) in enumerate(GAPS):
    for t,sg in ((a,1),(b,-1)):   # sg: which way the gap lies (forward from the lip, backward from the landing)
        p,r,u,fw,_=at(t); w=hw_at(t)+0.4
        JB.quad(tuple(p-r*w),tuple(p+r*w),tuple(p+r*w-u*SLAB),tuple(p-r*w-u*SLAB),m_haz)                       # the cut face
        JB.quad(tuple(p-r*w+u*0.05),tuple(p+r*w+u*0.05),tuple(p+r*w+u*0.05-fw*sg*0.6),tuple(p-r*w+u*0.05-fw*sg*0.6),m_neonY)   # neon lip
        for sd in (-1,1):   # posts at the barrier ends
            q=p+r*sd*(w-0.2); T=local(q,r,u,fw); JB.box(T,0,1.4,0,0.7,2.8,0.7,m_neonY)
    for j in range(6):   # chevron band on the ramp run-up
        t=(a-(j+1)*5/L)%1.0; p,r,u,fw,_=at(t); w=hw_at(t)
        JB.quad(tuple(p-r*w+u*0.07),tuple(p+r*w+u*0.07),tuple(p+r*w+u*0.07+fw*1.2),tuple(p-r*w+u*0.07+fw*1.2),m_neonY if j%2==0 else m_haz)
if GAPS: JB.build('jump',trk); log('jump gaps',len(GAPS))

P_=MB()
def flat_pad(t,lat,w,l,m):
    p,r,u,fw,_=at(t); c=p+r*lat+u*0.06
    a=c-r*w/2-fw*l/2; b=c+r*w/2-fw*l/2; cc=c+r*w/2+fw*l/2; d=c-r*w/2+fw*l/2
    P_.quad(tuple(a),tuple(b),tuple(cc),tuple(d),m,((0,0),(1,0),(1,1),(0,1)))   # v runs forward: the chevrons point the way
for t,lat in D['pads']:
    if not in_gap(t,0.001): flat_pad(t,lat,5,9,m_pad)
for t,lat in D['wpads']:
    if not in_gap(t,0.001): flat_pad(t,lat,5.5,5.5,m_wpad)
P_.build('pads',trk)

WAT=D.get('water')   # Västerbron cut out of the tiles (water_profile.cjs, index.html WATER): its pylons stand in the water
def water_at(m):   # our water's height under the racing line at m, if m is inside the corridor
    if not WAT or 'hull' not in WAT: return None
    (m0,l0),(m1,l1),(m2,l2),(m3,l3)=WAT['hull']; k=(0-l0)/(l1-l0)
    return WAT['y'] if m0+(m1-m0)*k<=m<=m3+(m2-m3)*k else None
Y_=MB(); n=int(L/42)
for i in range(n):
    t=i/n; p,r,u,fw,g=at(t)
    if in_gap(t,0.002) or g is None or np.isnan(g): continue
    wy=water_at(t*L)
    if wy is not None: log('pylon down to the water',round(t*L),round(g,1),'->',round(wy,1)); g=wy
    top=p[1]-SLAB; hgt=top-g
    if hgt<1.2: continue
    # a vertical leg (world up, not track up) and a yoke under the slab, hazard band at the top of the leg
    fl=np.array([fw[0],0,fw[2]]); fl/=np.linalg.norm(fl); rl=np.array([-fl[2],0,fl[0]]) if False else np.cross(fl,[0,1,0]); rl/=np.linalg.norm(rl)
    def T(q,base=np.array([p[0],g,p[2]])): x,y,z=q; return tuple(base+rl*x+np.array([0,1,0])*y-fl*z)
    Y_.box(T,0,hgt/2,0,1.5,hgt,1.5,m_stone)                                         # a limestone column
    if hgt>3: Y_.box(T,0,hgt-1.2,0,1.46,1.0,1.46,m_haz)
    Y_.box(T,0,hgt-0.35,0,HW*1.5,0.7,1.2,m_metal)
Y_.build('pylons',trk); log('pylons')

# ------------------------------------------------------------------ set pieces: gantry, sponsor arches, billboards
SET=bpy.data.collections.new('setpieces'); scene.collection.children.link(SET); setobs=[]
def sign(M,T,w,h,y,z,front,back):
    for tex,zz,flip in ((front,z,False),(back,-z,True)):
        mm=mat('sign_'+tex.split('.')[0],tex=tex,emit_tex=tex,emit=0.4,rough=0.5)
        x0,x1=-w/2,w/2
        if not flip: M.quad(T((x0,y-h/2,zz)),T((x1,y-h/2,zz)),T((x1,y+h/2,zz)),T((x0,y+h/2,zz)),mm)
        else: M.quad(T((x1,y-h/2,zz)),T((x0,y-h/2,zz)),T((x0,y+h/2,zz)),T((x1,y+h/2,zz)),mm)
p,r,u,fw,_=at(START_T); T=local(p,r,u,fw); M=MB(); W2=HW+3.2
PART='post'
for sx in (-1,1):
    M.box(T,sx*W2,8,0,1.6,16,1.6,m_metal); M.box(T,sx*W2,8,0.85,0.5,14,0.5,m_neonY); M.box(T,sx*W2,2.2,0,1.7,1.4,1.7,m_haz)
PART='banner'; M.box(T,0,14.2,0,W2*2+2,3.4,2.2,m_metal); sign(M,T,W2*2+1.6,3.0,14.2,1.18,'gantry.jpg','gantry.jpg')
for i in range(5): M.box(T,(i-2)*2.2,11.8,1.25,1.1,1.1,0.4,mat(f'light_{i}',col=(0.02,0,0),emit_col=(0.3,0.0,0.0),emit=1.0))
setobs.append(M.build('gantry',SET)); META={'gantry':dict(t=START_T)}
def arch_free(t):   # both posts clear: nothing from the tiles above the slab bottom where they stand
    c=clear_at(t); return all(np.isnan(v) or v< -1.2 for v in c[:2])
ARCHES=[dict(n=A['n'],t=A['t'],b=A['b'],d=A['d']) for A in D['arches']]
for k in range(8):   # sponsor arches around the lap, away from the landmarks and the start
    t=(k+0.55)/8
    if all(min(abs(t-A['t']),1-abs(t-A['t']))*L>600 for A in ARCHES): ARCHES.append(dict(n=f'SPONSOR_{k}',t=t,b=k,d=0))
# CLEAR OF THE TILES (Kim 2026-10-02, the SJ 2097 arch on Skeppsbron had a post inside the facade): the survey above
# samples the posts coarsely, so setpieces_probe.cjs raycasts every set-piece box against the finest tiles. What it
# caught is fixed here: an arch narrows to the track (posts right outside the barriers) or moves along the lap (dm, m);
# a billboard moves along the lap or changes side. Re-run the probe after any change to the track or the layout.
NA=len(COPY['arches'])
ARCH_FIX={}     # Kulturstockholm: filled from setpieces_probe.cjs
BOARD_FIX={2:dict(dm=40), 7:dict(dm=-40), 11:dict(dm=40)}   # setpieces_probe.cjs 2026-10-02: masts through facades
placed=0
for A in ARCHES:
    if A['d']>260: log('arch skipped (landmark too far from the lap)',A['n'],round(A['d'])); continue
    t=None
    for dm in range(0,160,4):
        for sg in (1,-1):
            tt=(A['t']+sg*dm/L)%1.0
            if arch_free(tt): t=tt; break
        if t is not None: break
    if t is None: log('arch skipped (tiles at the posts)',A['n']); continue
    if in_gap(t,0.01): log('arch skipped (in the jump)',A['n']); continue
    fx=ARCH_FIX.get(A['n'],{}); t=(t+fx.get('dm',0)/L)%1.0
    p,r,u,fw,_=at(t); T=local(p,r,u,fw); M=MB(); W2=hw_at(t)+(0.9 if fx.get('narrow') else 3.5); b=A['b']   # narrow: the posts' inner face 5 cm outside the barrier
    PART='post'
    for sx in (-1,1): M.box(T,sx*W2,6,0,1.3,12,1.3,m_metal); M.box(T,sx*W2,1.6,0,1.4,1.0,1.4,m_haz)
    PART='banner'; M.box(T,0,11.4,0,W2*2+2,3.0,1.6,m_metal); sign(M,T,W2*2+1.4,2.6,11.4,0.88,f'arch_{b%NA}.jpg',f'arch_{(b+2)%NA}.jpg')
    M.box(T,0,9.8,0,W2*2+2,0.2,1.8,m_neonY); setobs.append(M.build('arch_'+A['n'].lower(),SET)); placed+=1
    META['arch_'+A['n'].lower()]=dict(t=t,brand=b)
log('arches placed',placed,'of',len(ARCHES))
# THE GATE AT VÄSTERBRON (Kim 2026-10-02: "lägg också en gate vid hoppet vid västerbron där det står 'Du har mycket att
# leva för'"). Over the take-off, 15 m before the lip. Not an ad: gate_texture.py's warm white on a deep dark, a soft
# steady glow (no flicker, no stripes, no brand), a thin warm light under it. sign_: the motion blur leaves its letters. The posts stand right outside the
# barriers, as the ramp runs 25 m over the water; the banner's foot is 10 m over the deck, clear of craft and camera.
if GAPS:
    t=(GAPS[0][0]-15/L)%1.0; p,r,u,fw,_=at(t); T=local(p,r,u,fw); M=MB(); W2=hw_at(t)+0.9; GW=W2*2+1.2
    m_gate=mat('sign_gate_vb',tex='gate_vb.jpg',emit_tex='gate_vb.jpg',emit=0.55,rough=0.8); m_warm=mat('gate_warm',col=(0,0,0),emit_col=(1.0,0.78,0.55),emit=1.4)
    PART='post'
    for sx in (-1,1): M.box(T,sx*W2,9.25,0,1.1,18.5,1.1,m_metal)
    PART='banner'; M.box(T,0,13.75,0,GW+0.4,6.9,1.2,m_metal)
    for zz,(a,b) in ((0.62,(-GW/2,GW/2)),(-0.62,(GW/2,-GW/2))):   # the face toward the racer, and the same words on the back
        M.quad(T((a,10.5,zz)),T((b,10.5,zz)),T((b,17.0,zz)),T((a,17.0,zz)),m_gate)
    M.box(T,0,10.18,0,GW+0.4,0.12,1.3,m_warm); setobs.append(M.build('gate_vasterbron',SET)); META['gate_vasterbron']=dict(t=t)
    log('gate at Västerbron',round(t*L),'m,',round(GW,1),'x 6.5 m')
PARTY_NEON=[(1,0.08,0.18),(0.3,0.6,1),(1,0.85,0.1),(0.4,1,0.4),(1,0.25,0.3),(0.4,0.55,1),(1,0.85,0.1),(0.6,1,0.3)]   # rim colours, S..MP
BOARD_AIM_M=200   # how far up the track each billboard looks for the racer (m)
nb=int(L/300); M=MB(); boards=0; slots=[]
for i in range(nb):
    t=(i+0.5)/nb
    if t<0.012 or t>0.988 or in_gap(t,0.004): continue   # the ad layout is fixed to the loop, not the line (IKÖA, board 0, moves 30 m on: framed by the gantry from the grid)
    fx=BOARD_FIX.get(i,{}); t=(t+fx.get('dm',0)/L)%1.0
    c=clear_at(t); free={-1:c[2],1:c[3]}; pref=fx.get('side',1 if i%2 else -1); sd=None
    for s_ in ((pref,) if 'side' in fx else (pref,-pref)):
        v=free[s_]
        if not np.isnan(v) and v<3.5: sd=s_; break   # the board spans +6.3..+13.7 m over the deck: the tiles must stay below
    if sd is not None: slots.append((i,t,sd,free[sd]))
pslot={}; PARTIES_SHORT=[]; bi=0
for si,(i,t,sd,fr) in enumerate(slots):
    p,r,u,fw,_=at(t); T=local(p,r,u,fw,rot=sd*0.42,lat=sd*(hw_at(t)+10),lift=10)
    leg=10-3.5-max(fr,-60.0)                               # mast from the board down to the roof or street under it
    PART=f'board{si}:mast'; M.box(T,0,-3.5-leg/2,0,0.8,leg,0.8,m_metal)            # the mast stays plumb
    META[f'board{si}']=dict(t=t,side=sd,i=i,party=PARTIES_SHORT[pslot[si]] if si in pslot else None,brand=None if si in pslot else bi%NB)
    # the board itself turns to face the racer coming at it: aimed at the racing line BOARD_AIM_M before it, which
    # also tips it a little down toward the deck, so the slogan reads square-on in the chase camera
    B=p+r*(sd*(hw_at(t)+10))+u*10; qp,_,qu,_,_=at((t-BOARD_AIM_M/L)%1.0); Q=qp+qu*1.5
    Zb=Q-B; Zb=Zb/np.linalg.norm(Zb); Xb=np.cross(u,Zb); Xb=Xb/np.linalg.norm(Xb)
    if np.dot(Xb,r)<0: Xb=-Xb
    hand=np.dot(np.cross(r,u),-fw)                        # keep the original frame's handedness: no mirrored print, no culled face
    Yb=np.cross(Zb,Xb) if hand>0 else np.cross(Xb,Zb); Yb=Yb/np.linalg.norm(Yb)
    assert np.dot(Yb,u)>0.5, 'billboard frame flipped'
    TB=lambda q,B=B,Xb=Xb,Yb=Yb,Zb=Zb: tuple(B+Xb*q[0]+Yb*q[1]+Zb*q[2])
    PART=f'board{si}:board'; M.box(TB,0,0,0,14.4,7.4,0.5,m_metal)
    if si in pslot:   # a party's lit election board, with a neon rim in the party colour
        k=pslot[si]; mm=mat(f'pboard_{k}',tex=f'pbill_{k}.jpg',emit_tex=f'pbill_{k}.jpg',emit=0.5,rough=0.5)
        rim=mat(f'prim_{k}',col=(0,0,0),emit_col=PARTY_NEON[k],emit=6.0)
        for (cx,cy,ww,hh) in ((0,3.72,14.6,0.16),(0,-3.72,14.6,0.16),(-7.22,0,0.16,7.6),(7.22,0,0.16,7.6)): M.box(TB,cx,cy,0.36,ww,hh,0.12,rim)
    else:
        mm=mat(f'board_{bi%NB}',tex=f'bill_{bi%NB}.jpg',emit_tex=f'bill_{bi%NB}.jpg',emit=0.4,rough=0.5); bi+=1
    M.quad(TB((-7,-3.5,0.33)),TB((7,-3.5,0.33)),TB((7,3.5,0.33)),TB((-7,3.5,0.33)),mm); boards+=1   # 8 cm proud of the frame
log('party boards',len(pslot),'of',len(slots),'placed boards, at t:',' '.join(f'{PARTIES_SHORT[k]}={slots[j][1]:.4f}' for j,k in sorted(pslot.items())))
log('billboards',boards,'of',nb)
# ------------------------------------------------------------------ the restaurants along the line (copy.json restaurants)
# Real names as place names, our own type, never their signage. A board stands on the restaurant's side of the line where
# the racing line passes closest, turned to the racer like the billboards; if the tiles are in the way it slides up to 80 m.
LAT0,LON0=59.328,18.06; M_LAT=111320.0; M_LON=111320.0*math.cos(math.radians(LAT0))
RPOS={'Slussen':(59.31955,18.07316),'Kungliga Operan':(59.32970,18.07127),'Dramaten':(59.33371,18.07636),'Berzelii park':(59.33218,18.07390),'Djurgården':(59.32521,18.09894)}
def nearest_t(la,lo):
    x=-(lo-LON0)*M_LON; z=(la-LAT0)*M_LAT; d=(FR[:,0]-x)**2+(FR[:,2]-z)**2; i=int(np.argmin(d))
    p,r,u,fw,_=at(i/SEG); side=1 if (x-p[0])*r[0]+(z-p[2])*r[2]>0 else -1
    return i/SEG, side, math.sqrt(d[i])
REST_FIX={0:dict(dm=30)}   # by restaurant index: dm (m along the lap) from setpieces_probe.cjs
rest=0
for k,Rs in enumerate(COPY['restaurants']):
    t0,sd,dd=nearest_t(*RPOS[Rs['at']]); t0=(t0+REST_FIX.get(k,{}).get('dm',0)/L)%1.0; t=None
    for dm in range(0,84,4):
        for sg in (-1,1):
            tt=(t0+sg*dm/L)%1.0; c=clear_at(tt); v=c[2] if sd<0 else c[3]
            if not np.isnan(v) and v<3.5 and not in_gap(tt,0.004) and all(min(abs(tt-q[1]),1-abs(tt-q[1]))*L>60 for q in slots): t=tt; break
        if t is not None: break
    if t is None: log('restaurant skipped (tiles)',Rs['name']); continue
    fr=clear_at(t)[2 if sd<0 else 3]; p,r,u,fw,_=at(t); T=local(p,r,u,fw,rot=sd*0.42,lat=sd*(hw_at(t)+10),lift=10)
    leg=10-3.5-max(fr,-60.0); PART=f'rest{k}:mast'; M.box(T,0,-3.5-leg/2,0,0.8,leg,0.8,m_metal)
    B=p+r*(sd*(hw_at(t)+10))+u*10; qp,_,qu,_,_=at((t-BOARD_AIM_M/L)%1.0); Q=qp+qu*1.5
    Zb=Q-B; Zb=Zb/np.linalg.norm(Zb); Xb=np.cross(u,Zb); Xb=Xb/np.linalg.norm(Xb)
    if np.dot(Xb,r)<0: Xb=-Xb
    hand=np.dot(np.cross(r,u),-fw); Yb=np.cross(Zb,Xb) if hand>0 else np.cross(Xb,Zb); Yb=Yb/np.linalg.norm(Yb)
    TB=lambda q,B=B,Xb=Xb,Yb=Yb,Zb=Zb: tuple(B+Xb*q[0]+Yb*q[1]+Zb*q[2])
    PART=f'rest{k}:board'; M.box(TB,0,0,0,14.4,7.4,0.5,m_metal)
    mm=mat(f'board_rest_{k}',tex=f'rest_{k}.jpg',emit_tex=f'rest_{k}.jpg',emit=0.35,rough=0.5)
    M.quad(TB((-7,-3.5,0.33)),TB((7,-3.5,0.33)),TB((7,3.5,0.33)),TB((-7,3.5,0.33)),mm); rest+=1
    META[f'rest{k}']=dict(t=t,side=sd,name=Rs['name'],d=round(dd))
    log('restaurant',Rs['name'],round(t*L),'m, side',sd,round(dd),'m from the line')
setobs.append(M.build('billboards',SET)); log('set pieces',len(setobs),'restaurants',rest)

# ------------------------------------------------------------------ THE PIT LANES (track.json pits; index.html PITS)
# The lane is the outer strip of the deck on the restaurant's side (|lat| >= 4.3 m, the deck is wide there where the tiles allow):
# gold chevron paint on the deck, and an awning on posts outside the barrier, its sign facing the racers coming in.
m_pit=mat('pool_pit',col=(0,0,0),emit_tex='pit_lane.png',emit=1.3,double=True)
m_cloth={'riche':mat('pit_cloth_riche',col=srgb('#8e2a36'),rough=0.9),'freden':mat('pit_cloth_freden',col=srgb('#1d1a16'),rough=0.9)}
PL=MB()
for P in D.get('pits',[]):
    k,t0,t1,sd=P['k'],P['t0'],P['t1'],P['side']; span=(t1-t0)%1.0; n=max(2,int(span*L/4))
    for j in range(n):   # the lane paint, 4 m strips, chevrons pointing on
        ta=(t0+span*j/n)%1.0; tb=(t0+span*(j+1)/n)%1.0; pa,ra,ua,fa,_=at(ta); pb,rb,ub,fb,_=at(tb); wa,wb=hw_at(ta),hw_at(tb)
        PL.quad(tuple(pa+ra*sd*4.3+ua*0.07),tuple(pa+ra*sd*(wa-0.3)+ua*0.07),tuple(pb+rb*sd*(wb-0.3)+ub*0.07),tuple(pb+rb*sd*4.3+ub*0.07),m_pit,((0,0),(1,0),(1,1),(0,1)) if sd>0 else ((1,0),(0,0),(0,1),(1,1)))
    M=MB(); m_sign=mat(f'sign_pit_{k}',tex=f'pit_{k}.jpg',emit_tex=f'pit_{k}.jpg',emit=0.45,rough=0.6)
    for j,tt in enumerate(((t0+span*(0.5-30/(span*L)))%1.0,(t0+span*0.5)%1.0,(t0+span*(0.5+30/(span*L)))%1.0)):   # posts outside the barrier, the awning over the pit box at 7.6 m
        p,r,u,fw,_=at(tt); w=hw_at(tt); T=local(p,r,u,fw)
        PART=f'pit_{k}:post'; M.box(T,sd*(w+1.0),3.9,0,0.5,7.8,0.5,m_metal)
    c0=0.5-30/(span*L); c1=0.5+30/(span*L)   # the awning: 60 m over the middle of the lane (the pit box), not the whole window
    for j in range(n):
        if not (c0<=j/n<=c1): continue
        ta=(t0+span*j/n)%1.0; tb=(t0+span*(j+1)/n)%1.0; pa,ra,ua,fa,_=at(ta); pb,rb,ub,fb,_=at(tb); wa,wb=hw_at(ta),hw_at(tb)
        PART=f'pit_{k}:canopy'
        M.quad(tuple(pa+ra*sd*3.6+ua*7.6),tuple(pa+ra*sd*(wa+1.2)+ua*7.9),tuple(pb+rb*sd*(wb+1.2)+ub*7.9),tuple(pb+rb*sd*3.6+ub*7.6),m_cloth[k])
        M.quad(tuple(pb+rb*sd*3.6+ub*7.6),tuple(pb+rb*sd*(wb+1.2)+ub*7.9),tuple(pa+ra*sd*(wa+1.2)+ua*7.9),tuple(pa+ra*sd*3.6+ua*7.6),m_cloth[k])
    p,r,u,fw,_=at(t0); w=hw_at(t0); T=local(p,r,u,fw); cx=sd*(w+1.2+3.6)/2; sw=(w+1.2-3.6)+3.0   # the sign over the lane's mouth
    PART=f'pit_{k}:sign'; M.box(T,cx,9.6,0,sw+0.4,2.6,0.4,m_metal)
    a,b=(cx-sw/2,cx+sw/2)
    M.quad(T((a,8.4,0.24)),T((b,8.4,0.24)),T((b,10.8,0.24)),T((a,10.8,0.24)),m_sign)          # faces the racers coming in
    M.quad(T((b,8.4,-0.24)),T((a,8.4,-0.24)),T((a,10.8,-0.24)),T((b,10.8,-0.24)),m_sign)
    setobs.append(M.build(f'pit_{k}',SET)); META[f'pit_{k}']=dict(t=t0,side=sd); log('pit lane',k,round(t0*L),'..',round(t1*L),'m, side',sd)
if PL.v: PL.build('pit_lanes',trk)
if PROBE:   # the set pieces' boxes for the tile-clipping probe (setpieces_probe.cjs), then stop: nothing is exported
    json.dump(dict(boxes=SETBOXES,meta=META,trackLen=L),open(PROBE,'w')); log('probe',len(SETBOXES),'boxes ->',PROBE); os._exit(0)

# the craft moved to build_craft.py (detailed hard-surface models); this script only builds the track set
crafts=[]

# ------------------------------------------------------------------ ambient occlusion into vertex colours (craft and set pieces)
def bake(obs):
    scene.render.engine='CYCLES'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='METAL'; prefs.get_devices()
        for dv in prefs.devices: dv.use=True
        scene.cycles.device='GPU'
    except Exception as ex: log('gpu unavailable',ex)
    scene.cycles.samples=48; w=bpy.data.worlds.new('w'); scene.world=w; w.light_settings.distance=3.0
    for o in obs:
        me=o.data; ca=me.color_attributes.new('Col','BYTE_COLOR','CORNER'); me.color_attributes.active_color=ca
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.bake(type='AO',target='VERTEX_COLORS')
        n=len(me.loops); c=np.ones(n*4,np.float32); ca.data.foreach_get('color',c); c=c.reshape(-1,4); c[:,:3]=0.35+0.65*np.clip(c[:,:3],0,1)**1.1
        ca.data.foreach_set('color',c.ravel())
    log('baked',len(obs))
if not NOBAKE: bake(setobs)

# ------------------------------------------------------------------ export
def export(coll,path,vc):
    bpy.ops.object.select_all(action='DESELECT')
    for o in coll.all_objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_yup=True,export_apply=False,
        export_vertex_color='NAME' if vc else 'NONE',export_vertex_color_name='Col',export_all_vertex_colors=False,
        export_image_format='AUTO',export_materials='EXPORT',export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=7,
        export_draco_position_quantization=20,export_draco_texcoord_quantization=12,export_draco_color_quantization=8,export_draco_normal_quantization=8)
    log('exported',os.path.basename(path),round(os.path.getsize(path)/1e6,2),'MB')
all_track=bpy.data.collections.new('all_track'); scene.collection.children.link(all_track)
for o in list(trk.objects)+list(SET.objects): all_track.objects.link(o)
export(all_track,os.path.join(OUT,'track.glb'),not NOBAKE)
log('done')
