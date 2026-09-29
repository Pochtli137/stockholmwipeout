"""STOCKHOLM WIPEOUT 2097 · the six anti-grav craft, modelled in Blender as bevelled hard-surface.
Rebuilds only the craft (the track lives in build.py). Exports ../assets/craft_<i>.glb.

    blender -b --factory-startup -P build_craft.py -- [--nobake] [--only 3]

Modelled in Blender's frame with the nose on +Y, up +Z (glTF export turns it into the game's frame: nose on -z, up +y).
Each file has the nodes the game drives: flap_L / flap_R (airbrake hinges, the plate hangs behind the hinge and
rotation.x < 0 lifts it) and eng_L / eng_R (nozzle exit centres, where the glow, heat and trails attach).
Six original designs for invented teams; no real craft, teams or logos."""
import bpy, bmesh, os, sys, math, time
import numpy as np
from mathutils import Matrix, Vector
HERE=os.path.dirname(os.path.abspath(__file__)); TEX=os.path.join(HERE,'tex'); OUT=os.path.abspath(os.path.join(HERE,'..','..','assets','neon'))   # NEON theme snapshot
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
NOBAKE='--nobake' in argv; ONLY=int(argv[argv.index('--only')+1]) if '--only' in argv else None
T0=time.time()
def log(*a): print(f'[{time.time()-T0:6.1f}s]',*a,flush=True)
bpy.ops.wm.read_factory_settings(use_empty=True); scene=bpy.context.scene

# ------------------------------------------------------------------ materials
def srgb(h): h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]; return tuple((x/12.92 if x<=0.04045 else ((x+0.055)/1.055)**2.4) for x in c)
MATS={}
def mat(name,col=(1,1,1),rough=0.5,metal=0.0,coat=0.0,tex=None,emit_col=None,emit=0.0):
    if name in MATS: return MATS[name]
    m=bpy.data.materials.new(name); m.use_nodes=True; nt=m.node_tree; bs=nt.nodes['Principled BSDF']
    bs.inputs['Roughness'].default_value=rough; bs.inputs['Metallic'].default_value=metal
    if coat:
        for k,v in (('Coat Weight',coat),('Coat Roughness',0.08)):
            if k in bs.inputs: bs.inputs[k].default_value=v
    if tex:
        t=nt.nodes.new('ShaderNodeTexImage'); t.image=bpy.data.images.load(os.path.join(TEX,tex),check_existing=True)
        nt.links.new(t.outputs['Color'],bs.inputs['Base Color'])
    else: bs.inputs['Base Color'].default_value=(*col,1)
    if emit_col: bs.inputs['Emission Color'].default_value=(*emit_col,1); bs.inputs['Emission Strength'].default_value=emit
    m.use_backface_culling=True
    MATS[name]=m; return m

TEAMS=[  # same order and colours as index.html TEAMS and make_textures.py
  dict(team='VOLVÖ SECURITY', a='#d6deeb',b='#0c1830',eng='#9fd8ff',acc='#ffcd00'),
  dict(team='SAAPH DEFENCE',  a='#c81020',b='#0c0d12',eng='#ff3b3b',acc='#8a8f98'),
  dict(team='SPOTIFAI NEURAL',a='#1ed760',b='#07090d',eng='#35ff8b',acc='#1ed760'),
  dict(team='IKÖA FLATPACK',  a='#ffcd00',b='#004aad',eng='#ffcd00',acc='#004aad'),
  dict(team='KLARNÅ DEBT',    a='#ffb3c7',b='#07090d',eng='#ff5fa2',acc='#ff5fa2'),
  dict(team='ERIXON SIGNAL',  a='#f2f6ff',b='#00a8e0',eng='#00e1ff',acc='#00a8e0') ]

# ------------------------------------------------------------------ geometry helpers (all in Blender's frame)
def sgnpow(v,p): return math.copysign(abs(v)**p,v)
def loft(bm,stations,mi,n=32,e=2.0,tip_front=None,tip_back=None,cap_back=True,xoff=0.0,panel_every=0):
    """Superellipse sections along Y. stations: (y, halfwidth, zc, top, bottom[, e]) from nose to tail.
    tip_front/back: (y, z) closes the end on a point; otherwise the end is capped flat. Returns the faces."""
    rings=[]
    for st in stations:
        y,hw,zc,ht,hb=st[:5]; ee=st[5] if len(st)>5 else e; ring=[]
        for k in range(n):
            th=2*math.pi*k/n; c,s=math.cos(th),math.sin(th)
            ring.append(bm.verts.new((xoff+hw*sgnpow(c,2/ee), y, zc+(ht if s>=0 else hb)*sgnpow(s,2/ee))))
        rings.append(ring)
    faces=[]
    for j,(a,b) in enumerate(zip(rings,rings[1:])):
        for k in range(n): f=bm.faces.new((a[k],a[(k+1)%n],b[(k+1)%n],b[k])); f.material_index=mi; faces.append(f)
    if tip_front:
        t=bm.verts.new((xoff,tip_front[0],tip_front[1])); r=rings[0]
        for k in range(n): f=bm.faces.new((t,r[(k+1)%n],r[k])); f.material_index=mi; faces.append(f)
    if tip_back:
        t=bm.verts.new((xoff,tip_back[0],tip_back[1])); r=rings[-1]
        for k in range(n): f=bm.faces.new((t,r[k],r[(k+1)%n])); f.material_index=mi; faces.append(f)
    elif cap_back: f=bm.faces.new(list(reversed(rings[-1]))); f.material_index=mi; faces.append(f)
    if panel_every:   # panel seams: inset every nth band of quads into a shallow groove
        sel=[f for f in faces if len(f.verts)==4 and (int(round(abs(f.calc_center_median().y)*10))//panel_every)%2==0]
        if sel: bmesh.ops.inset_individual(bm,faces=sel,thickness=0.018,depth=-0.006)
    return faces
def plate(bm,pts,fn,mi):
    """A slab from a 2D outline: fn(u,v,side) -> 3D point, side = -1 (bottom/inner) or +1 (top/outer)."""
    A=[bm.verts.new(fn(u,v,1)) for u,v in pts]; B=[bm.verts.new(fn(u,v,-1)) for u,v in pts]; n=len(pts)
    fs=[bm.faces.new(A),bm.faces.new(list(reversed(B)))]
    for k in range(n): fs.append(bm.faces.new((B[k],B[(k+1)%n],A[(k+1)%n],A[k])))
    for f in fs: f.material_index=mi
    return fs
def wing(bm,pts,z0,t,mi,dihedral=0.0,taper=0.5,x0=0.0,mirror=True):
    """Flat wing in XY from an outline (x>=0, y); thickness tapers to taper*t at the tip; dihedral in degrees."""
    xmax=max(p[0] for p in pts) or 1
    for s in ((-1,1) if mirror else (1,)):
        P=[(s*x,y) for x,y in pts] if s>0 else [(s*x,y) for x,y in reversed(pts)]
        plate(bm,P,lambda u,v,side:(u,v,z0+(abs(u)-x0)*math.tan(math.radians(dihedral))+side*0.5*t*(1-(1-taper)*abs(u)/xmax)),mi)
def fin(bm,pts,x,t,mi,cant=0.0,mirror=True):
    """A fin in the YZ plane at +-x, outline (y,z); cant tilts it outwards (degrees)."""
    for s in ((-1,1) if mirror else (1,)):
        plate(bm,pts,lambda u,v,side:(s*(x+(v-pts[0][1])*math.tan(math.radians(cant)))+side*0.5*t,u,v),mi)
def box(bm,c,size,mi):
    x,y,z=c; w,d,h=size
    plate(bm,[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],lambda u,v,side:(u,v,z+side*h/2),mi)
def tube(bm,p0,p1,r0,r1,mi,seg=12,caps=True):
    p0,p1=Vector(p0),Vector(p1); d=p1-p0; L=d.length
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    M=Matrix.Translation((p0+p1)/2)@q
    res=bmesh.ops.create_cone(bm,cap_ends=caps,cap_tris=False,segments=seg,radius1=r0,radius2=r1,depth=L,matrix=M)
    fs=set(f for v in res['verts'] for f in v.link_faces)
    for f in fs: f.material_index=mi
    return res['verts']
def disc(bm,c,r,axis,mi,seg=20):
    q=Vector((0,0,1)).rotation_difference(Vector(axis)).to_matrix().to_4x4()
    res=bmesh.ops.create_circle(bm,cap_ends=True,segments=seg,radius=r,matrix=Matrix.Translation(c)@q)
    fs=set(f for v in res['verts'] for f in v.link_faces)
    for f in fs: f.material_index=mi
def nozzle(bm,c,r,depth,mi_shell,mi_ring,mi_core,seg=20):
    """A round engine bell on -Y: shell, a metal lip and a glowing core set back inside."""
    x,y,z=c
    tube(bm,(x,y+depth,z),(x,y,z),r*0.92,r,mi_shell,seg,caps=False)
    tube(bm,(x,y+0.02,z),(x,y-0.06,z),r*1.02,r*1.06,mi_ring,seg,caps=True)
    disc(bm,(x,y+0.16,z),r*0.84,(0,-1,0),mi_core,seg)
def hexbolt(bm,c,r,mi,axis=(0,0,1)):
    c=Vector(c); a=Vector(axis).normalized(); tube(bm,c,c+a*0.05,r,r,mi,seg=6)

def hover_pads(bm,pads,mi_dark,mi_glow):
    """Anti-grav emitters under the hull: a dark plate with a glowing rim, facing the track."""
    for x,y,w,d,z in pads:
        box(bm,(x,y,z),(w,d,0.06),mi_dark); box(bm,(x,y,z-0.035),(w*0.84,d*0.84,0.02),mi_glow)
def tail_lights(bm,pts,mi):
    for x,y,z in pts: box(bm,(x,y,z),(0.22,0.04,0.07),mi)
def intake(bm,x,y,z,w,h,mi_dark,mi_lip,depth=0.5):
    box(bm,(x,y-depth/2,z),(w,depth,h),mi_dark); box(bm,(x,y+0.01,z+h/2+0.02),(w+0.06,0.06,0.04),mi_lip)
def finish(ob,bevel=0.035,seg=3,angle=32,subsurf=0,wn=True):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    if subsurf: m=ob.modifiers.new('ss','SUBSURF'); m.levels=subsurf; m.render_levels=subsurf
    if bevel:
        b=ob.modifiers.new('bv','BEVEL'); b.width=bevel; b.segments=seg; b.limit_method='ANGLE'
        b.angle_limit=math.radians(angle); b.harden_normals=True
    if wn: w=ob.modifiers.new('wn','WEIGHTED_NORMAL'); w.keep_sharp=True
    for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
def mk(name,bm,mats,coll,closed=True,**fin_kw):
    if closed:
        try: bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
        except Exception: pass
    for f in bm.faces: f.smooth=True
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); finish(ob,**fin_kw); return ob
def decal(name,corners,m,coll,uv=((0,0),(1,0),(1,1),(0,1))):
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(c) for c in corners],[],[(0,1,2,3)]); me.update()
    ul=me.uv_layers.new(name='UVMap')
    for li,loop in enumerate(me.loops): ul.data[li].uv=uv[loop.vertex_index]
    me.materials.append(m); ob=bpy.data.objects.new(name,me); coll.objects.link(ob); return ob
def side_band(name,x,y0,y1,z0,z1,m,coll):
    """Text band on both flanks, reading nose-to-tail on each side seen from outside."""
    obs=[decal(name+'_L',[(-x,y0,z0),(-x,y1,z0),(-x,y1,z1),(-x,y0,z1)],m,coll),
         decal(name+'_R',[(x,y1,z0),(x,y0,z0),(x,y0,z1),(x,y1,z1)],m,coll)]
    return obs
def top_decal(name,x0,x1,y0,y1,z,m,coll):   # reads from behind and above: text runs along +x, its top points to the nose
    return decal(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],m,coll)
def empty(name,loc,coll):
    e=bpy.data.objects.new(name,None); e.location=loc; coll.objects.link(e); return e
def flaps(coll,hinges,size,mA,thick=0.06):
    """Airbrake plates: each hangs behind its hinge (towards -Y); rotation.x < 0 in the game lifts the trailing edge."""
    out=[]
    for sd,(x,y,z) in hinges:
        h=empty(f'flap_{sd}',(x,y,z),coll); bm=bmesh.new(); w,d=size
        plate(bm,[(-w/2,0),(w/2,0),(w/2*0.86,-d),(-w/2*0.86,-d)],lambda u,v,side:(u,v,side*thick/2),0)
        o=mk(f'flap_{sd}_plate',bm,[mA],coll,bevel=0.012,seg=1); o.parent=h; out.append(o)
    return out

# ------------------------------------------------------------------ the six craft
def materials(i):
    T=TEAMS[i]
    return dict(A=mat(f'paintA_{i}',col=srgb(T['a']),rough=0.32,metal=0.25,coat=0.7),
                B=mat(f'paintB_{i}',col=srgb(T['b']),rough=0.38,metal=0.35,coat=0.5),
                K=mat('carbon',col=(0.018,0.02,0.026),rough=0.42,metal=0.55),
                M=mat('metal',col=(0.52,0.54,0.58),rough=0.28,metal=1.0),
                G=mat('canopy',col=(0.01,0.025,0.06),rough=0.06,metal=0.85,coat=1.0),
                E=mat(f'core_{i}',col=(0,0,0),emit_col=srgb(T['eng']),emit=7.0),
                N=mat(f'neon_craft_{i}',col=(0,0,0),emit_col=srgb(T['eng']),emit=3.5),
                R=mat('neon_tail',col=(0,0,0),emit_col=srgb('#ff2030'),emit=4.0),
                C=mat(f'accent_{i}',col=srgb(T['acc']),rough=0.35,metal=0.3,coat=0.6),
                L=mat(f'livery_{i}',tex=f'livery_{i}.jpg',rough=0.4,metal=0.1),
                H=mat(f'hull_{i}',tex=f'hull_{i}.jpg',rough=0.4,metal=0.1),
                Z=mat('hazard',tex='hazard.jpg',rough=0.5))
ORDER=['A','B','K','M','G','E','N','C','R']   # material slots of the body meshes
def S(k): return ORDER.index(k)
def slots(m): return [m[k] for k in ORDER]

def canopy(bm,y0,y1,zc,hw,h,mi):
    L=y0-y1
    loft(bm,[(y0-L*0.18,hw*0.62,zc,h*0.55,0.02,2.2),(y0-L*0.45,hw,zc,h,0.02,2.2),(y1+L*0.2,hw*0.8,zc,h*0.7,0.02,2.2)],mi,
         n=20,tip_front=(y0,zc+0.02),tip_back=(y1,zc+0.02))

def craft_volvo(i,coll,m):
    """VOLVÖ SECURITY · boxy, armoured, safe: a wide flat-topped hull, armoured side pods with bolt rows,
    a bumper bar across the nose, a roll cage over a tall canopy, twin armoured nozzles."""
    bm=bmesh.new(); A,B,K,Mt,E,N,C=S('A'),S('B'),S('K'),S('M'),S('E'),S('N'),S('C')
    loft(bm,[(4.2,0.5,0.02,0.2,0.24),(3.6,0.95,0.06,0.34,0.3),(2.2,1.22,0.1,0.5,0.38),(0.0,1.32,0.12,0.56,0.42),
             (-2.2,1.28,0.1,0.5,0.4),(-3.3,1.1,0.08,0.42,0.38)],A,e=4.2,panel_every=7)
    for s in (-1,1):
        loft(bm,[(2.5,0.3,-0.02,0.18,0.2),(1.8,0.5,0.0,0.3,0.28),(-2.8,0.56,0.02,0.32,0.3),(-3.5,0.52,0.0,0.3,0.28)],B,e=5.0,xoff=s*2.12)
        for k in range(6): hexbolt(bm,(s*(2.12+0.57),1.2-k*0.7,0.08),0.05,Mt,axis=(s,0,0))
        box(bm,(s*2.12,-0.6,0.36),(0.62,3.8,0.08),C)                              # armour cap on the pod
        box(bm,(s*2.7,-0.4,-0.12),(0.05,3.6,0.07),N)                              # neon rail along the skirt
    wing(bm,[(1.15,1.4),(1.62,1.1),(1.62,-2.5),(1.15,-2.7)],0.05,0.18,K,taper=1.0,x0=1.15)
    plate(bm,[(-2.55,3.05),(2.55,3.05),(2.3,3.55),(-2.3,3.55)],lambda u,v,side:(u,v,-0.05+side*0.14),K)   # the bumper
    fin(bm,[(-1.7,0.3),(-3.35,0.3),(-3.62,1.18),(-2.95,1.24)],2.12,0.12,A)
    for s in (-1,1): tube(bm,(s*0.62,1.5,0.62),(s*0.62,1.35,1.2),0.06,0.06,Mt,seg=8); tube(bm,(s*0.62,-0.6,0.62),(s*0.62,-0.45,1.2),0.06,0.06,Mt,seg=8)
    for yy in (1.35,-0.45): tube(bm,(-0.62,yy,1.2),(0.62,yy,1.2),0.06,0.06,Mt,seg=8)
    for s in (-1,1): tube(bm,(s*0.62,1.35,1.2),(s*0.62,-0.45,1.2),0.06,0.06,Mt,seg=8)
    for s in (-1,1): nozzle(bm,(s*2.12,-3.5,0.02),0.36,0.5,K,Mt,E)
    hover_pads(bm,[(0,1.8,0.9,1.6,-0.33),(0,-1.4,1.0,2.0,-0.33),(-2.12,-0.6,0.5,3.4,-0.33),(2.12,-0.6,0.5,3.4,-0.33)],K,N)
    tail_lights(bm,[(-0.7,-3.31,0.3),(0.7,-3.31,0.3)],S('R'))
    for s in (-1,1): intake(bm,s*2.12,2.52,0.02,0.44,0.22,K,Mt)
    mk(f'craft_{i}_body',bm,slots(m),coll,bevel=0.04,seg=2)
    bm=bmesh.new(); canopy(bm,2.9,-1.1,0.62,0.52,0.36,0); mk(f'craft_{i}_canopy',bm,[m['G']],coll,bevel=0)
    top_decal(f'craft_{i}_livery',-1.0,1.0,-3.1,-1.5,0.64,m['L'],coll)
    side_band(f'craft_{i}_hull',2.685,1.6,-2.6,-0.2,0.16,m['H'],coll)
    top_decal(f'craft_{i}_hazard',-2.3,2.3,3.2,3.5,0.1,m['Z'],coll)
    flaps(coll,[('L',(-1.4,-2.65,0.16)),('R',(1.4,-2.65,0.16))],(0.5,0.8),m['A'])
    return (-2.12,-3.62,0.02),(2.12,-3.62,0.02)

def craft_saaph(i,coll,m):
    """SAAPH DEFENCE · military stealth: faceted diamond-section hull with chines, twin intake booms,
    forward canards, canted twin tails, missile rails under the wings and a nose cannon."""
    bm=bmesh.new(); A,B,K,Mt,E,N,C=S('A'),S('B'),S('K'),S('M'),S('E'),S('N'),S('C')
    loft(bm,[(3.9,0.28,0.0,0.14,0.12),(2.6,0.78,0.05,0.4,0.24),(0.8,1.0,0.08,0.52,0.3),(-1.4,0.92,0.08,0.48,0.3),(-3.0,0.6,0.06,0.36,0.26)],
         A,e=1.35,n=16,tip_front=(4.7,0.0),panel_every=5)
    for s in (-1,1):
        loft(bm,[(1.6,0.34,-0.04,0.26,0.24,1.6),(0.8,0.46,-0.02,0.34,0.3,1.6),(-2.6,0.46,-0.02,0.34,0.3,1.6),(-3.3,0.4,-0.02,0.3,0.28,1.6)],
             B,n=16,xoff=s*1.75)
        plate(bm,[(s*1.42,1.62),(s*2.08,1.62),(s*2.0,1.52),(s*1.5,1.52)],lambda u,v,side:(u,v,-0.04+side*0.26),K)   # intake mouth
        tube(bm,(s*2.95,1.2,-0.3),(s*2.95,-1.4,-0.3),0.1,0.1,Mt,seg=8)          # missile rail
        tube(bm,(s*2.95,1.5,-0.3),(s*2.95,1.2,-0.3),0.0,0.1,C,seg=8)
    wing(bm,[(0.9,0.6),(3.2,-1.4),(3.3,-2.2),(0.9,-2.4)],0.0,0.14,A,dihedral=-4,taper=0.4,x0=0.9)
    wing(bm,[(0.6,3.0),(1.5,2.3),(1.5,2.05),(0.6,2.2)],0.18,0.07,K,dihedral=8,taper=0.5,x0=0.6)              # canards
    fin(bm,[(-1.9,0.3),(-3.2,0.3),(-3.55,1.45),(-2.95,1.5)],1.75,0.1,B,cant=22)
    tube(bm,(0,4.5,-0.02),(0,5.3,-0.02),0.06,0.05,Mt,seg=8)                              # nose cannon
    for s in (-1,1): box(bm,(s*1.2,0.0,0.46),(0.05,2.6,0.05),N)
    for s in (-1,1): nozzle(bm,(s*1.75,-3.3,-0.02),0.34,0.45,K,Mt,E)
    hover_pads(bm,[(0,1.4,0.8,2.0,-0.24),(-1.75,-0.8,0.44,3.2,-0.34),(1.75,-0.8,0.44,3.2,-0.34)],K,N)
    tail_lights(bm,[(-0.4,-3.02,0.22),(0.4,-3.02,0.22)],S('R'))
    mk(f'craft_{i}_body',bm,slots(m),coll,bevel=0.025,angle=28)
    bm=bmesh.new(); canopy(bm,3.1,0.6,0.5,0.4,0.28,0); mk(f'craft_{i}_canopy',bm,[m['G']],coll,bevel=0)
    top_decal(f'craft_{i}_livery_L',-3.0,-1.3,-2.2,-1.05,0.03,m['L'],coll); top_decal(f'craft_{i}_livery_R',1.3,3.0,-2.2,-1.05,0.03,m['L'],coll)
    side_band(f'craft_{i}_hull',2.215,0.6,-2.4,-0.16,0.14,m['H'],coll)
    flaps(coll,[('L',(-2.3,-2.3,0.08)),('R',(2.3,-2.3,0.08))],(0.9,0.6),m['B'])
    return (-1.75,-3.36,-0.02),(1.75,-3.36,-0.02)

def craft_spotifai(i,coll,m):
    """SPOTIFAI NEURAL · organic: a smooth teardrop hull flowing into bulbous nacelles, a curved wing,
    'waveform' ribs down the spine and one swept dorsal fin; subdivided for soft surfaces."""
    bm=bmesh.new(); A,B,K,Mt,E,N,C=S('A'),S('B'),S('K'),S('M'),S('E'),S('N'),S('C')
    loft(bm,[(3.8,0.42,0.04,0.24,0.2),(2.6,0.9,0.08,0.44,0.3),(0.9,1.2,0.1,0.56,0.36),(-1.0,1.1,0.1,0.5,0.36),(-2.6,0.75,0.08,0.38,0.3)],
         A,e=2.2,n=20,tip_front=(4.6,0.02),tip_back=(-3.3,0.08))
    for s in (-1,1):
        loft(bm,[(1.4,0.28,-0.04,0.24,0.22),(0.4,0.5,-0.02,0.4,0.34),(-1.9,0.52,-0.02,0.42,0.36),(-3.0,0.44,-0.02,0.34,0.3)],
             B,e=2.1,n=18,xoff=s*1.55,tip_front=(2.0,-0.04),cap_back=True)
    pts=[(0.8,1.2)]+[(0.8+2.2*math.sin(a),1.2-3.4*(1-math.cos(a))) for a in np.linspace(0.2,1.35,7)]+[(2.4,-2.1),(0.8,-1.9)]
    wing(bm,pts,0.0,0.16,A,dihedral=6,taper=0.35,x0=0.8)
    for k in range(7):   # the waveform: ribs of varying height down the spine
        h=0.12+0.22*abs(math.sin(k*1.1)); box(bm,(0,0.6-k*0.42,0.66+h/2),(0.12,0.16,h),K)
    fin(bm,[(-0.9,0.5),(-2.8,0.45),(-3.3,1.55),(-2.6,1.6),(-1.8,1.0)],0.0,0.12,B,mirror=False)
    for s in (-1,1): box(bm,(s*1.55,-1.0,0.43),(0.05,2.2,0.05),N)
    for s in (-1,1): nozzle(bm,(s*1.55,-3.05,-0.02),0.3,0.4,K,Mt,E)
    for s in (-1,1): tube(bm,(s*1.55,1.62,-0.03),(s*1.55,1.4,-0.03),0.3,0.36,Mt,seg=24,caps=False)
    for k in range(7): box(bm,(0,0.6-k*0.42,0.67),(0.16,0.2,0.03),N)
    hover_pads(bm,[(0,1.2,0.9,2.4,-0.28),(-1.55,-0.9,0.5,2.6,-0.36),(1.55,-0.9,0.5,2.6,-0.36)],K,N)
    mk(f'craft_{i}_body',bm,slots(m),coll,bevel=0,subsurf=1)
    bm=bmesh.new(); canopy(bm,3.4,0.9,0.52,0.46,0.32,0); mk(f'craft_{i}_canopy',bm,[m['G']],coll,bevel=0,subsurf=1)
    top_decal(f'craft_{i}_livery_L',-2.5,-0.95,-1.7,-0.9,0.12,m['L'],coll); top_decal(f'craft_{i}_livery_R',0.95,2.5,-1.7,-0.9,0.12,m['L'],coll)
    flaps(coll,[('L',(-1.9,-1.85,0.12)),('R',(1.9,-1.85,0.12))],(0.8,0.55),m['A'])
    return (-1.55,-3.1,-0.02),(1.55,-3.1,-0.02)

def craft_ikoa(i,coll,m):
    """IKÖA FLATPACK · flat-pack: every part is a flat board with chamfered edges, held by hex bolts;
    a slotted tail, a stacked-slab nose, square nozzles in plywood-coloured blocks, assembly stickers."""
    bm=bmesh.new(); A,B,K,Mt,E,N,C=S('A'),S('B'),S('K'),S('M'),S('E'),S('N'),S('C')
    slabs=[((0,1.2,0.05),(2.4,5.4,0.3),A),((0,0.9,0.38),(1.7,4.2,0.36),B),((0,3.9,0.05),(1.4,1.2,0.26),A),((0,-2.0,0.5),(1.9,2.4,0.2),A)]
    for c,sz,mi in slabs: box(bm,c,sz,mi)
    plate(bm,[(-0.7,4.5),(0.7,4.5),(0.35,5.0),(-0.35,5.0)],lambda u,v,side:(u,v,0.05+side*0.13),A)
    for s in (-1,1):
        box(bm,(s*2.15,-0.6,0.0),(0.9,5.2,0.5),B)
        box(bm,(s*1.35,-0.3,0.02),(0.9,3.2,0.14),A)
        for k in range(5): hexbolt(bm,(s*2.15,1.5-k*1.0,0.26),0.07,Mt)
        box(bm,(s*2.15,-3.25,0.0),(0.72,0.3,0.5),K)
        disc(bm,(s*2.15,-3.36,0.0),0.26,(0,-1,0),E,seg=4)
        box(bm,(s*2.62,-0.6,-0.12),(0.05,4.6,0.06),N)
    for k in range(3):   # the slotted tail: three boards slid into a cross-board
        plate(bm,[(-1.6+k*0.4,0.62),(-3.1+k*0.25,0.62),(-3.3+k*0.25,1.35-k*0.1),(-2.4+k*0.3,1.35-k*0.1)],lambda u,v,side,xx=(k-1)*0.55:(xx+side*0.05,u,v),A)
    box(bm,(0,-2.6,0.66),(1.9,0.9,0.08),B)
    for c in ((0.6,3.6),(-0.6,3.6),(0.7,-1.2),(-0.7,-1.2),(0.7,-2.9),(-0.7,-2.9)): hexbolt(bm,(c[0],c[1],0.6 if c[1]<0 else 0.18),0.06,Mt)
    for s in (-1,1):
        plate(bm,[(s*2.6,0.6),(s*3.3,0.2),(s*3.3,-1.6),(s*2.6,-2.0)],lambda u,v,side:(u,v,0.05+side*0.05),A)   # outrigger boards
        for yy in (0.1,-0.7,-1.5): hexbolt(bm,(s*2.95,yy,0.1),0.05,Mt)
        box(bm,(s*3.3,-0.7,0.05),(0.06,1.8,0.3),B)
    tube(bm,(0.5,-2.0,0.6),(0.5,-2.0,1.6),0.045,0.045,Mt,seg=6); tube(bm,(0.5,-2.0,1.6),(0.5,-2.6,1.6),0.045,0.045,Mt,seg=6)   # the allen key
    for k in range(5): box(bm,(0,2.8-k*1.4,-0.2),(2.2,0.35,0.1),B)
    hover_pads(bm,[(-2.15,-0.6,0.6,4.4,-0.3),(2.15,-0.6,0.6,4.4,-0.3)],K,N)
    tail_lights(bm,[(-0.6,-3.21,0.5),(0.6,-3.21,0.5)],S('R'))
    mk(f'craft_{i}_body',bm,slots(m),coll,bevel=0.03,seg=2,angle=40)
    bm=bmesh.new(); box(bm,(0,2.5,0.72),(1.0,1.4,0.32),0); mk(f'craft_{i}_canopy',bm,[m['G']],coll,bevel=0.08,seg=2)
    top_decal(f'craft_{i}_livery',-0.95,0.95,-3.05,-1.2,0.61,m['L'],coll)
    side_band(f'craft_{i}_hull',2.605,1.8,-3.0,-0.2,0.2,m['H'],coll)
    flaps(coll,[('L',(-1.35,-1.9,0.1)),('R',(1.35,-1.9,0.1))],(0.8,0.7),m['B'])
    return (-2.15,-3.42,0.0),(2.15,-3.42,0.0)

def craft_klarna(i,coll,m):
    """KLARNÅ DEBT · sleek and pink: a needle nose on a low glossy hull, a smooth swept delta,
    a single wide nozzle with two cores, small tip winglets; everything flows, nothing is paid for."""
    bm=bmesh.new(); A,B,K,Mt,E,N,C=S('A'),S('B'),S('K'),S('M'),S('E'),S('N'),S('C')
    loft(bm,[(4.4,0.16,0.0,0.08,0.07),(3.0,0.55,0.03,0.26,0.18),(1.0,0.95,0.06,0.42,0.26),(-1.2,1.05,0.06,0.44,0.28),(-2.9,0.9,0.04,0.36,0.26),(-3.4,0.82,0.02,0.32,0.24)],
         A,e=2.4,n=22,tip_front=(5.6,0.0))
    wing(bm,[(0.8,1.4),(2.9,-2.3),(2.9,-2.9),(0.8,-3.0)],-0.02,0.14,A,dihedral=-3,taper=0.3,x0=0.8)
    fin(bm,[(-2.2,0.0),(-2.9,0.0),(-3.1,0.55),(-2.75,0.6)],2.9,0.07,B,cant=-18)
    loft(bm,[(-2.3,0.72,0.1,0.34,0.26),(-3.3,0.8,0.1,0.36,0.28)],K,e=3.0,n=20,cap_back=False)
    loft(bm,[(-3.3,0.8,0.1,0.36,0.28),(-3.62,0.86,0.1,0.38,0.3)],S('M'),e=3.0,n=20,cap_back=False)
    for s in (-1,1): disc(bm,(s*0.4,-3.42,0.1),0.3,(0,-1,0),E,seg=24)
    for s in (-1,1): box(bm,(s*0.98,-0.6,0.28),(0.05,3.6,0.05),N)
    loft(bm,[(3.6,0.08,0.3,0.03,0.03),(1.0,0.2,0.46,0.04,0.04),(-2.6,0.22,0.42,0.04,0.04)],B,e=2.0,n=12,tip_front=(4.3,0.2))   # the black spine
    wing(bm,[(0.3,4.2),(0.9,1.6),(1.05,0.9),(0.55,1.3)],0.0,0.05,B,taper=0.6,x0=0.3)                 # black blade chines along the nose
    wing(bm,[(2.4,-1.9),(2.9,-2.3),(2.9,-2.9),(2.5,-2.95)],0.0,0.16,B,taper=1.0,x0=2.4)                 # black wingtips
    loft(bm,[(0.6,0.26,0.62,0.18,0.02),(-1.4,0.3,0.6,0.2,0.02),(-2.6,0.16,0.5,0.1,0.02)],A,e=2.2,n=20,tip_front=(1.4,0.56))   # head fairing
    intake(bm,0,0.8,-0.22,0.7,0.14,K,Mt,depth=0.8)
    hover_pads(bm,[(0,1.6,0.7,2.0,-0.24),(-1.5,-1.9,0.9,1.2,-0.1),(1.5,-1.9,0.9,1.2,-0.1)],K,N)
    tail_lights(bm,[(-0.95,-3.45,0.3),(0.95,-3.45,0.3)],S('R'))
    mk(f'craft_{i}_body',bm,slots(m),coll,bevel=0.02,angle=30)
    bm=bmesh.new(); canopy(bm,3.2,0.2,0.34,0.4,0.28,0); mk(f'craft_{i}_canopy',bm,[m['G']],coll,bevel=0)
    top_decal(f'craft_{i}_livery_L',-2.7,-1.1,-2.75,-1.85,0.06,m['L'],coll); top_decal(f'craft_{i}_livery_R',1.1,2.7,-2.75,-1.85,0.06,m['L'],coll)
    flaps(coll,[('L',(-1.8,-2.95,0.06)),('R',(1.8,-2.95,0.06))],(1.0,0.6),m['B'])
    return (-0.4,-3.5,0.1),(0.4,-3.5,0.1)

def craft_erixon(i,coll,m):
    """ERIXON SIGNAL · a catamaran of two booms around a slim centre pod, tall stepped 'signal bar' fins,
    a dish on the spine and antenna masts with beacons."""
    bm=bmesh.new(); A,B,K,Mt,E,N,C=S('A'),S('B'),S('K'),S('M'),S('E'),S('N'),S('C')
    loft(bm,[(3.4,0.34,0.08,0.24,0.2),(2.0,0.62,0.1,0.42,0.26),(-0.6,0.66,0.1,0.44,0.28),(-2.4,0.46,0.08,0.34,0.24)],A,e=2.6,n=18,
         tip_front=(4.5,0.06),tip_back=(-3.1,0.1))
    for s in (-1,1):
        loft(bm,[(3.0,0.26,-0.02,0.2,0.2),(2.0,0.44,0.0,0.3,0.28),(-2.6,0.46,0.0,0.32,0.28),(-3.3,0.42,0.0,0.3,0.26)],B,e=3.0,n=18,xoff=s*2.0,
             tip_front=(3.8,-0.02))
    for k,(h,yy) in enumerate(((0.55,-1.3),(0.85,-2.0),(1.25,-2.7))):   # signal bars: three rising fins on each boom
        fin(bm,[(yy+0.26,0.28),(yy-0.26,0.28),(yy-0.3,0.28+h),(yy+0.14,0.28+h)],2.0,0.08,A)
    wing(bm,[(0.62,1.2),(1.6,0.9),(1.6,-1.6),(0.62,-1.9)],0.06,0.14,K,taper=1.0,x0=0.62)
    tube(bm,(0,-0.4,0.52),(0,-0.4,0.78),0.05,0.05,Mt,seg=8)                      # the dish
    tube(bm,(0,-0.4,0.78),(0,-0.4,0.9),0.05,0.5,C,seg=20,caps=True)
    for s in (-1,1):
        tube(bm,(s*2.0,1.2,0.3),(s*2.0,1.0,1.4),0.035,0.02,Mt,seg=6)              # antenna masts
        tube(bm,(s*2.0,1.0,1.4),(s*2.0,1.0,1.5),0.08,0.08,N,seg=10)
        box(bm,(s*2.46,-0.4,-0.1),(0.05,4.0,0.05),N)
    for s in (-1,1): nozzle(bm,(s*2.0,-3.3,0.0),0.34,0.45,K,Mt,E)
    hover_pads(bm,[(-2.0,-0.3,0.5,4.4,-0.3),(2.0,-0.3,0.5,4.4,-0.3),(0,1.0,0.7,2.4,-0.2)],K,N)
    tail_lights(bm,[(-0.3,-2.6,0.38),(0.3,-2.6,0.38)],S('R'))
    for s in (-1,1): intake(bm,s*2.0,3.2,0.12,0.3,0.14,K,Mt,depth=0.4)
    mk(f'craft_{i}_body',bm,slots(m),coll,bevel=0.03)
    bm=bmesh.new(); canopy(bm,3.0,0.9,0.52,0.4,0.28,0); mk(f'craft_{i}_canopy',bm,[m['G']],coll,bevel=0)
    top_decal(f'craft_{i}_livery',-0.62,0.62,-2.3,-1.0,0.55,m['L'],coll)
    side_band(f'craft_{i}_hull',2.465,2.2,-2.6,-0.2,0.18,m['H'],coll)
    flaps(coll,[('L',(-1.1,-1.95,0.14)),('R',(1.1,-1.95,0.14))],(0.8,0.7),m['A'])
    return (-2.0,-3.36,0.0),(2.0,-3.36,0.0)

BUILDERS=[craft_volvo,craft_saaph,craft_spotifai,craft_ikoa,craft_klarna,craft_erixon]
crafts=[]
for i,fn in enumerate(BUILDERS):
    if ONLY is not None and i!=ONLY: continue
    cc=bpy.data.collections.new(f'craft_{i}'); scene.collection.children.link(cc)
    m=materials(i); eL,eR=fn(i,cc,m)
    empty('eng_L',eL,cc); empty('eng_R',eR,cc)
    tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in cc.objects if o.type=='MESH')
    crafts.append((i,cc)); log('craft',i,TEAMS[i]['team'],tris,'tris')

# ------------------------------------------------------------------ AO into vertex colours
def bake(obs):
    scene.render.engine='CYCLES'
    prefs=bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type='METAL'; prefs.get_devices()
        for dv in prefs.devices: dv.use=True
        scene.cycles.device='GPU'
    except Exception as ex: log('gpu unavailable',ex)
    scene.cycles.samples=64; w=bpy.data.worlds.new('w'); scene.world=w; w.light_settings.distance=1.2
    for o in obs:
        me=o.data; ca=me.color_attributes.new('Col','BYTE_COLOR','CORNER'); me.color_attributes.active_color=ca
        bpy.ops.object.select_all(action='DESELECT'); o.select_set(True); bpy.context.view_layer.objects.active=o
        bpy.ops.object.bake(type='AO',target='VERTEX_COLORS')
        n=len(me.loops); c=np.ones(n*4,np.float32); ca.data.foreach_get('color',c); c=c.reshape(-1,4); c[:,:3]=0.42+0.58*np.clip(c[:,:3],0,1)**1.2
        ca.data.foreach_set('color',c.ravel())
if not NOBAKE:
    for i,cc in crafts:
        # hide the other craft so one team's hull never shadows another's
        for j,c2 in crafts: c2.hide_render=(j!=i)
        bake([o for o in cc.objects if o.type=='MESH'])
    for j,c2 in crafts: c2.hide_render=False
    log('baked')

def export(coll,path,vc):
    bpy.ops.object.select_all(action='DESELECT')
    for o in coll.all_objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_yup=True,export_apply=False,
        export_vertex_color='NAME' if vc else 'NONE',export_vertex_color_name='Col',export_all_vertex_colors=False,
        export_image_format='JPEG',export_materials='EXPORT',export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=7,
        export_draco_position_quantization=16,export_draco_texcoord_quantization=12,export_draco_color_quantization=8,export_draco_normal_quantization=10)
    log('exported',os.path.basename(path),round(os.path.getsize(path)/1e6,2),'MB')
for i,cc in crafts: export(cc,os.path.join(OUT,f'craft_{i}.glb'),not NOBAKE)
log('done')
