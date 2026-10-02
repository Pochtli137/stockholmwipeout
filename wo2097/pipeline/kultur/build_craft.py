"""WIPEOUT KULTURSTOCKHOLM · the six craft of the cultural league, modelled in Blender. Exports
../../assets/kultur/craft_<i>.glb (i = the team's index in ../../assets/kultur/copy.json `teams`).

    python3 craft_textures.py && blender -b --factory-startup -P build_craft.py -- [--nobake] [--only 3] [--preview <dir>]

The game's conventions, as in neon/build_craft.py (whose helpers this reuses): nose on Blender +Y, up +Z (the glTF export
turns it into nose -z, up +y), the nodes flap_L / flap_R (airbrake hinges, the plate hangs behind the hinge, rotation.x < 0
lifts it) and eng_L / eng_R (nozzle exits, where the glow and trails attach). Engine cores are `core_<i>` and glow strips
`neon_craft_<i>` (the game lets both go over 1.0 for the bloom). Satire of types only, no real people, no real logos.
--preview renders each craft (three-quarter rear and side, Cycles) to <dir>/craft_<i>_<name>[_side].png."""
import bpy, bmesh, os, sys, math, time, json, random
import numpy as np
from mathutils import Matrix, Vector
HERE=os.path.dirname(os.path.abspath(__file__)); TEX=os.path.join(HERE,'tex'); OUT=os.path.abspath(os.path.join(HERE,'..','..','assets','kultur'))
COPY=json.load(open(os.path.join(OUT,'copy.json'),encoding='utf-8')); TEAMS=COPY['teams']
argv=sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
NOBAKE='--nobake' in argv; ONLY=int(argv[argv.index('--only')+1]) if '--only' in argv else None
PREVIEW=argv[argv.index('--preview')+1] if '--preview' in argv else None
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

# ------------------------------------------------------------------ geometry helpers (Blender's frame), as in neon/build_craft.py
def sgnpow(v,p): return math.copysign(abs(v)**p,v)
def loft(bm,stations,mi,n=32,e=2.0,tip_front=None,tip_back=None,cap_back=True,cap_front=True,xoff=0.0):
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
    for a,b in zip(rings,rings[1:]):
        for k in range(n): f=bm.faces.new((a[k],a[(k+1)%n],b[(k+1)%n],b[k])); f.material_index=mi; faces.append(f)
    if tip_front:
        t=bm.verts.new((xoff,tip_front[0],tip_front[1])); r=rings[0]
        for k in range(n): f=bm.faces.new((t,r[(k+1)%n],r[k])); f.material_index=mi; faces.append(f)
    elif cap_front: f=bm.faces.new(rings[0]); f.material_index=mi; faces.append(f)
    if tip_back:
        t=bm.verts.new((xoff,tip_back[0],tip_back[1])); r=rings[-1]
        for k in range(n): f=bm.faces.new((t,r[k],r[(k+1)%n])); f.material_index=mi; faces.append(f)
    elif cap_back: f=bm.faces.new(list(reversed(rings[-1]))); f.material_index=mi; faces.append(f)
    return faces
def plate(bm,pts,fn,mi):
    """A slab from a 2D outline: fn(u,v,side) -> 3D point, side = -1 (bottom/inner) or +1 (top/outer)."""
    A=[bm.verts.new(fn(u,v,1)) for u,v in pts]; B=[bm.verts.new(fn(u,v,-1)) for u,v in pts]; n=len(pts)
    fs=[bm.faces.new(A),bm.faces.new(list(reversed(B)))]
    for k in range(n): fs.append(bm.faces.new((B[k],B[(k+1)%n],A[(k+1)%n],A[k])))
    for f in fs: f.material_index=mi
    return fs
def fin(bm,pts,x,t,mi,cant=0.0,mirror=True):
    for s in ((-1,1) if mirror else (1,)):
        plate(bm,pts,lambda u,v,side:(s*(x+(v-pts[0][1])*math.tan(math.radians(cant)))+side*0.5*t,u,v),mi)
def box(bm,c,size,mi,rot=0.0):
    x,y,z=c; w,d,h=size; cr,sr=math.cos(rot),math.sin(rot)
    R=lambda u,v:(x+(u-x)*cr-(v-y)*sr, y+(u-x)*sr+(v-y)*cr)
    plate(bm,[(x-w/2,y-d/2),(x+w/2,y-d/2),(x+w/2,y+d/2),(x-w/2,y+d/2)],lambda u,v,side:(*R(u,v),z+side*h/2),mi)
def tube(bm,p0,p1,r0,r1,mi,seg=12,caps=True):
    p0,p1=Vector(p0),Vector(p1); d=p1-p0; L=d.length
    q=Vector((0,0,1)).rotation_difference(d.normalized()).to_matrix().to_4x4()
    M=Matrix.Translation((p0+p1)/2)@q
    res=bmesh.ops.create_cone(bm,cap_ends=caps,cap_tris=False,segments=seg,radius1=r0,radius2=r1,depth=L,matrix=M)
    fs=set(f for v in res['verts'] for f in v.link_faces)
    for f in fs: f.material_index=mi
    return res['verts']
def pipe(bm,pts,r,mi,seg=10,closed=False):
    """a wire along a polyline: tubes between the points and a ball at every joint"""
    P=pts+([pts[0]] if closed else [])
    for a,b in zip(P,P[1:]): tube(bm,a,b,r,r,mi,seg,caps=False)
    for p in P: ball(bm,p,r,mi,sub=1)
def ball(bm,c,r,mi,sub=2):
    res=bmesh.ops.create_icosphere(bm,subdivisions=sub,radius=r,matrix=Matrix.Translation(c))
    for f in set(f for v in res['verts'] for f in v.link_faces): f.material_index=mi
def disc(bm,c,r,axis,mi,seg=20):
    q=Vector((0,0,1)).rotation_difference(Vector(axis)).to_matrix().to_4x4()
    res=bmesh.ops.create_circle(bm,cap_ends=True,segments=seg,radius=r,matrix=Matrix.Translation(c)@q)
    for f in set(f for v in res['verts'] for f in v.link_faces): f.material_index=mi
def nozzle(bm,c,r,depth,mi_shell,mi_ring,mi_core,seg=20):
    """A round engine bell on -Y: shell, a lip and a glowing core set back inside."""
    x,y,z=c
    tube(bm,(x,y+depth,z),(x,y,z),r*0.92,r,mi_shell,seg,caps=False)
    tube(bm,(x,y+0.02,z),(x,y-0.06,z),r*1.02,r*1.06,mi_ring,seg,caps=False)
    disc(bm,(x,y+0.16,z),r*0.84,(0,-1,0),mi_core,seg)
def hover_pads(bm,pads,mi_dark,mi_glow):
    for x,y,w,d,z in pads:
        box(bm,(x,y,z),(w,d,0.06),mi_dark); box(bm,(x,y,z-0.035),(w*0.84,d*0.84,0.02),mi_glow)
def finish(ob,bevel=0.035,seg=3,angle=32,subsurf=0,wn=True):
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active=ob
    if subsurf: m=ob.modifiers.new('ss','SUBSURF'); m.levels=subsurf; m.render_levels=subsurf
    if bevel:
        b=ob.modifiers.new('bv','BEVEL'); b.width=bevel; b.segments=seg; b.limit_method='ANGLE'
        b.angle_limit=math.radians(angle); b.harden_normals=True
    if wn: w=ob.modifiers.new('wn','WEIGHTED_NORMAL'); w.keep_sharp=True
    for m in list(ob.modifiers): bpy.ops.object.modifier_apply(modifier=m.name)
def mk(name,bm,mats,coll,closed=True,smooth=True,**fin_kw):
    if closed:
        try: bmesh.ops.recalc_face_normals(bm,faces=bm.faces[:])
        except Exception: pass
    for f in bm.faces: f.smooth=smooth
    me=bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    for m in mats: me.materials.append(m)
    ob=bpy.data.objects.new(name,me); coll.objects.link(ob); finish(ob,**fin_kw); return ob
def decal(name,corners,m,coll,uv=((0,0),(1,0),(1,1),(0,1))):
    me=bpy.data.meshes.new(name); me.from_pydata([tuple(c) for c in corners],[],[(0,1,2,3)]); me.update()
    ul=me.uv_layers.new(name='UVMap')
    for li,loop in enumerate(me.loops): ul.data[li].uv=uv[loop.vertex_index]
    me.materials.append(m); ob=bpy.data.objects.new(name,me); coll.objects.link(ob); return ob
def side_band(name,x,y0,y1,z0,z1,m,coll):
    """Text band on both flanks, reading nose-to-tail on each side seen from outside (y0 > y1)."""
    return [decal(name+'_L',[(-x,y0,z0),(-x,y1,z0),(-x,y1,z1),(-x,y0,z1)],m,coll),
            decal(name+'_R',[(x,y1,z0),(x,y0,z0),(x,y0,z1),(x,y1,z1)],m,coll)]
def top_decal(name,x0,x1,y0,y1,z,m,coll):   # reads from behind and above: text along +x, its top toward the nose
    return decal(name,[(x0,y0,z),(x1,y0,z),(x1,y1,z),(x0,y1,z)],m,coll)
def stern_decal(name,x0,x1,z0,z1,y,m,coll):  # on a face looking backwards (-Y): seen from behind, +x is to the right
    return decal(name,[(x0,y,z0),(x1,y,z0),(x1,y,z1),(x0,y,z1)],m,coll)
def bow_decal(name,x0,x1,z0,z1,y,m,coll):    # on a face looking forwards (+Y): seen from in front, -x is to the right
    return decal(name,[(x1,y,z0),(x0,y,z0),(x0,y,z1),(x1,y,z1)],m,coll)
def empty(name,loc,coll):
    e=bpy.data.objects.new(name,None); e.location=loc; coll.objects.link(e); return e
def flaps(coll,hinges,size,mA,thick=0.06):
    out=[]
    for sd,(x,y,z) in hinges:
        h=empty(f'flap_{sd}',(x,y,z),coll); bm=bmesh.new(); w,d=size
        plate(bm,[(-w/2,0),(w/2,0),(w/2*0.86,-d),(-w/2*0.86,-d)],lambda u,v,side:(u,v,side*thick/2),0)
        o=mk(f'flap_{sd}_plate',bm,[mA],coll,bevel=0.012,seg=1); o.parent=h; out.append(o)
    return out
def set_uv(ob,fn):
    """UVs from the final vertex positions: fn(co, normal) -> (u, v)"""
    me=ob.data; ul=me.uv_layers.active or me.uv_layers.new(name='UVMap')
    for p in me.polygons:
        for li in p.loop_indices: ul.data[li].uv=fn(me.vertices[me.loops[li].vertex_index].co,p.normal)
def box_uv(ob,scale):   # world-scale planar projection along each face's dominant axis (wood grain, paper fibre)
    def fn(co,n):
        a=max(range(3),key=lambda k:abs(n[k]))
        if a==0: return (co.y*scale,co.z*scale)
        if a==1: return (co.x*scale,co.z*scale)
        return (co.y*scale,co.x*scale)
    set_uv(ob,fn)

def materials(i):
    T=TEAMS[i]
    return dict(A=mat(f'paintA_{i}',col=srgb(T['a']),rough=0.38,metal=0.1,coat=0.6),
                B=mat(f'paintB_{i}',col=srgb(T['b']),rough=0.4,metal=0.2,coat=0.4),
                K=mat('k_dark',col=(0.02,0.02,0.024),rough=0.5,metal=0.4),
                M=mat('k_metal',col=(0.55,0.56,0.58),rough=0.28,metal=1.0),
                Gd=mat('k_gold',col=(0.83,0.6,0.2),rough=0.22,metal=1.0),
                E=mat(f'core_{i}',col=(0,0,0),emit_col=srgb(T['eng']),emit=7.0),
                N=mat(f'neon_craft_{i}',col=(0,0,0),emit_col=srgb(T['eng']),emit=3.0),
                R=mat('neon_tail_k',col=(0,0,0),emit_col=srgb('#ff3030'),emit=3.5),
                S=mat(f'stern_{i}',tex=f'craft_stern_{i}.jpg',rough=0.45))
ORDER=['A','B','K','M','Gd','E','N','R']   # material slots of the body meshes
def S(k): return ORDER.index(k)
def slots(m): return [m[k] for k in ORDER]

# ================================================================== 0 · DE ADERTON
def craft_aderton(i,coll,m):
    """The boss: a flying mahogany chamber, eighteen numbered velvet chairs in two tiered rows of nine (facing forward,
    the backs and their numbers toward the chasing pack), gold trim, a gilded crown on the bow, two gold nozzles."""
    W=mat('mahogany',tex='craft_mahogany.jpg',rough=0.3,metal=0.0,coat=0.9); VEL=mat('velvet',col=srgb('#6e1220'),rough=0.85)
    bm=bmesh.new(); A,K,Gd,E,N=S('A'),S('K'),S('Gd'),S('E'),S('N')
    loft(bm,[(3.95,1.45,0.15,0.36,0.34,6),(3.6,1.85,0.15,0.45,0.42,7),(-3.3,1.85,0.15,0.45,0.42,7),(-3.6,1.72,0.15,0.4,0.38,6)],0,n=36)
    body=mk(f'craft_{i}_chamber',bm,[W],coll,bevel=0.05,seg=2,angle=40); box_uv(body,0.35)
    bm=bmesh.new()
    for s in (-1,1):   # gold trim: top and bottom edges, the corners
        box(bm,(s*1.87,0.15,0.6),(0.07,7.0,0.07),Gd); box(bm,(s*1.87,0.15,-0.27),(0.07,7.0,0.07),Gd)
        for yy in (3.55,-3.25): box(bm,(s*1.87,yy,0.165),(0.09,0.09,0.86),Gd)
        loft(bm,[(3.3,0.2,-0.12,0.16,0.14),(2.6,0.3,-0.1,0.2,0.18),(-3.0,0.3,-0.1,0.2,0.18),(-3.5,0.26,-0.1,0.18,0.16)],A,e=3.0,n=16,xoff=s*2.15)   # runners
        box(bm,(s*2.15,-0.2,0.12),(0.62,6.0,0.05),Gd); box(bm,(s*2.46,-0.2,-0.12),(0.05,5.8,0.05),N)
        for yy in (1.6,-1.8): box(bm,(s*2.0,yy,0.1),(0.4,0.3,0.12),Gd)   # brackets to the chamber
    box(bm,(0,3.62,0.6),(3.7,0.07,0.07),Gd); box(bm,(0,-3.32,0.6),(3.7,0.07,0.07),Gd)
    for s in (-1,1): nozzle(bm,(s*1.2,-3.62,0.08),0.34,0.5,K,Gd,E)
    # the crown on the bow: a gold band, five points with pearls, two arches
    cy,cz=3.32,0.62; box(bm,(0,cy,cz+0.06),(0.7,0.5,0.12),Gd)
    tube(bm,(0,cy,cz+0.12),(0,cy,cz+0.42),0.42,0.44,Gd,seg=24,caps=False)
    for k in range(5):
        a=k*2*math.pi/5+math.pi/2; x,y=0.43*math.cos(a),cy+0.43*math.sin(a)
        tube(bm,(x,y,cz+0.42),(x,y,cz+0.74),0.1,0.0,Gd,seg=8,caps=True); ball(bm,(x,y,cz+0.78),0.065,Gd)
    for a in (0,math.pi/2):
        pts=[(0.4*math.cos(a)*math.cos(t),cy+0.4*math.sin(a)*math.cos(t),cz+0.42+0.38*math.sin(t)) for t in np.linspace(0,math.pi,9)]
        pipe(bm,pts,0.04,Gd,seg=8)
    ball(bm,(0,cy,cz+0.86),0.09,Gd); tube(bm,(0,cy,cz+0.92),(0,cy,cz+1.08),0.025,0.025,Gd,seg=6); box(bm,(0,cy,cz+1.04),(0.16,0.03,0.04),Gd)
    hover_pads(bm,[(0,2.2,1.6,1.6,-0.31),(0,-1.4,1.8,2.6,-0.31),(-2.15,-0.2,0.4,5.0,-0.28),(2.15,-0.2,0.4,5.0,-0.28)],K,N)
    mk(f'craft_{i}_trim',bm,slots(m),coll,bevel=0.015,seg=1)
    # the eighteen chairs: two blocks (left, right of the aisle), nine tiers stepping up toward the stern
    bm=bmesh.new(); bmg=bmesh.new(); backs=[]
    for row in range(9):
        y=2.75-row*0.71; zr=0.6+0.03*row
        box(bmg,(0,y,zr+0.0225),(3.3,0.71,0.045),0)   # the tier
        for s,blk in ((-1,0),(1,1)):
            x=s*0.82; z0=zr+0.045
            box(bm,(x,y+0.04,z0+0.15),(0.18,0.18,0.3),1)                    # pedestal
            box(bm,(x,y+0.04,z0+0.34),(0.6,0.52,0.1),0)                      # seat (velvet)
            box(bm,(x,y-0.24,z0+0.6),(0.6,0.08,0.5),0)                       # back (velvet)
            box(bm,(x,y-0.24,z0+0.87),(0.66,0.1,0.06),1); box(bm,(x-0.32,y-0.24,z0+0.6),(0.05,0.1,0.54),1); box(bm,(x+0.32,y-0.24,z0+0.6),(0.05,0.1,0.54),1)
            for sx in (-1,1): box(bm,(x+sx*0.3,y+0.06,z0+0.46),(0.06,0.42,0.06),1)   # arms
            backs.append((row*2+blk,x,y-0.285,z0+0.37,z0+0.83))
    mk(f'craft_{i}_chairs',bm,[VEL,m['Gd']],coll,bevel=0.02,seg=1)
    tiers=mk(f'craft_{i}_tiers',bmg,[W],coll,bevel=0.01,seg=1); box_uv(tiers,0.35)
    CH=mat('chairs',tex='craft_chairs.jpg',rough=0.6)
    for k,x,y,z0,z1 in backs:   # cell k of the 9 x 2 atlas, chair number k+1, on the back's rear face
        u0,u1=(k%9)/9,(k%9+1)/9; v1=1-(k//9)/2; v0=v1-0.5
        decal(f'craft_{i}_no{k+1}',[(x-0.28,y,z0),(x+0.28,y,z0),(x+0.28,y,z1),(x-0.28,y,z1)],CH,coll,uv=((u0,v0),(u1,v0),(u1,v1),(u0,v1)))
    PL=mat('plaque_0',tex='craft_plaque_0.jpg',rough=0.35,coat=0.6)
    stern_decal(f'craft_{i}_plaque_stern',-1.1,1.1,-0.18,0.52,-3.62,PL,coll); bow_decal(f'craft_{i}_plaque_bow',-0.95,0.95,-0.12,0.48,3.97,PL,coll)
    side_band(f'craft_{i}_side',1.865,2.8,-2.8,-0.12,0.5,m['S'],coll)
    flaps(coll,[('L',(-1.55,-3.0,0.64)),('R',(1.55,-3.0,0.64))],(0.58,0.5),m['Gd'])
    return (-1.2,-3.69,0.08),(1.2,-3.69,0.08)

# ================================================================== 1 · SOMMARPRATARNA
def craft_radio(i,coll,m):
    """A cathedral valve radio in walnut, its face (speaker cloth, tuning dial, two knobs) toward the pack behind it, a
    second grille on the bow, a carry handle, a telescopic antenna, and two speaker cones for nozzles."""
    WN=mat('walnut',tex='craft_walnut.jpg',rough=0.32,coat=0.85); BK=mat('bakelite',col=srgb('#3a2414'),rough=0.3,coat=0.6)
    bm=bmesh.new()
    loft(bm,[(4.25,0.95,0.05,0.62,0.26,2.8),(3.1,1.7,0.05,1.18,0.3,3.2),(1.0,1.98,0.05,1.45,0.32,3.6),(-2.6,1.98,0.05,1.52,0.32,3.6),(-3.25,1.94,0.05,1.48,0.3,3.6)],0,n=40)
    body=mk(f'craft_{i}_cabinet',bm,[WN],coll,bevel=0.04,seg=2,angle=40); box_uv(body,0.4)
    bm=bmesh.new(); A,B,K,Mt,Gd,E,N=S('A'),S('B'),S('K'),S('M'),S('Gd'),S('E'),S('N')
    ys=-3.27
    for s in (-1,1):   # brass bezel around the grille, the two knobs, side rails, the speaker-cone nozzles
        box(bm,(s*1.22,ys-0.03,0.88),(0.08,0.08,1.1),Gd)
        tube(bm,(s*0.98,ys,0.17),(s*0.98,ys-0.16,0.17),0.14,0.13,B,seg=20); tube(bm,(s*0.98,ys-0.16,0.17),(s*0.98,ys-0.2,0.17),0.13,0.1,Gd,seg=20)
        loft(bm,[(3.4,0.16,-0.14,0.12,0.12),(-3.1,0.16,-0.14,0.12,0.12)],B,e=3,n=12,xoff=s*2.12); box(bm,(s*2.12,0.1,-0.3),(0.05,6.2,0.05),N)
        for yy in (2.2,-1.6): box(bm,(s*2.04,yy,-0.08),(0.25,0.3,0.1),B)
        x,z=s*1.62,0.86
        tube(bm,(x,ys+0.55,z),(x,ys-0.02,z),0.16,0.42,len(ORDER),seg=28,caps=False)   # the paper cone (two-sided)
        tube(bm,(x,ys-0.0,z),(x,ys-0.07,z),0.43,0.46,Gd,seg=28,caps=False)             # its brass rim
        disc(bm,(x,ys+0.38,z),0.2,(0,-1,0),E,seg=24); ball(bm,(x,ys+0.3,z),0.09,K)     # the glowing voice coil and the dust cap
    box(bm,(0,ys-0.03,1.45),(2.52,0.08,0.08),Gd); box(bm,(0,ys-0.03,0.32),(2.52,0.08,0.08),Gd)
    # carry handle on top and the telescopic antenna, leaning back
    hp=[(-0.55,-0.6,1.55),(-0.5,-0.6,1.72),(0.5,-0.6,1.72),(0.55,-0.6,1.55)]; pipe(bm,hp,0.05,B,seg=10)
    a0=Vector((1.25,-2.55,1.52)); a1=Vector((1.4,-2.95,1.94)); seg3=[a0,a0+(a1-a0)*0.4,a0+(a1-a0)*0.72,a1]
    for k,(p,q) in enumerate(zip(seg3,seg3[1:])): tube(bm,p,q,0.035-k*0.008,0.035-k*0.008,Mt,seg=8)
    ball(bm,tuple(a1),0.05,Mt); box(bm,(1.25,-2.55,1.5),(0.16,0.16,0.08),Mt)
    hover_pads(bm,[(0,2.0,1.8,2.0,-0.3),(0,-1.4,2.2,2.6,-0.3),(-2.12,0.1,0.34,5.6,-0.27),(2.12,0.1,0.34,5.6,-0.27)],K,N)
    CONE=mat('cone_paper',col=srgb('#2a2018'),rough=0.9); CONE.use_backface_culling=False
    mk(f'craft_{i}_fittings',bm,slots(m)+[CONE],coll,bevel=0.012,seg=1)
    GR=mat('grille_1',tex='craft_grille_1.jpg',rough=0.9); DL=mat('dial_1',col=(0,0,0),tex='craft_dial_1.jpg',rough=0.2)
    stern_decal(f'craft_{i}_grille',-1.18,1.18,0.36,1.42,ys-0.012,GR,coll)
    stern_decal(f'craft_{i}_dial',-0.72,0.72,0.04,0.3,ys-0.012,DL,coll)
    bow_decal(f'craft_{i}_grille_bow',-0.62,0.62,0.06,0.58,4.252,GR,coll)
    side_band(f'craft_{i}_side',1.985,1.6,-2.2,0.1,0.74,m['S'],coll)
    flaps(coll,[('L',(-1.45,-3.05,1.25)),('R',(1.45,-3.05,1.25))],(0.6,0.45),WN)
    return (-1.62,-3.32,0.86),(1.62,-3.32,0.86)

# ================================================================== 2 · KULTURSIDAN
def craft_broadsheet(i,coll,m):
    """A broadsheet folded into a paper dart: two layered delta wings of newsprint on a V keel, the critic's red pencil
    along the right wing, red ink on the keel, two nozzles under the tail."""
    PAPER=mat('newsprint_edge',col=srgb('#e9e1cf'),rough=0.85)
    NA=mat('news_2a',tex='craft_news_2a.jpg',rough=0.85); NB=mat('news_2b',tex='craft_news_2b.jpg',rough=0.85)
    X0,X1,Y0,Y1=-2.7,2.7,-4.05,4.85
    page=lambda co,n:((co.x-X0)/(X1-X0),(co.y-Y0)/(Y1-Y0))   # one page over the whole plane, read from behind: top toward the nose
    for lay,(mm,z,sc) in enumerate(((NA,0.56,1.0),(NB,0.62,0.86))):
        bm=bmesh.new()
        for s in (-1,1):
            P=[(0.0,4.85*sc+(1-sc)*0.6),(s*2.65*sc,-3.95*sc+(1-sc)*-0.5),(s*0.14,-4.0*sc+(1-sc)*-0.5)]
            if s<0: P=P[::-1]
            plate(bm,P,lambda u,v,side,s=s:(u,v,z+abs(u)*math.tan(math.radians(7))+side*0.022),0)
        ob=mk(f'craft_{i}_sheet{lay}',bm,[mm],coll,bevel=0,smooth=False); set_uv(ob,page)
    bm=bmesh.new(); A,B,K,Mt,Gd,E,N,R=S('A'),S('B'),S('K'),S('M'),S('Gd'),S('E'),S('N'),S('R')
    kb=bmesh.new(); fin(kb,[(4.7,0.55),(-4.0,0.55),(-4.0,-0.26),(0.6,-0.26)],0.13,0.04,0,cant=-10)   # the keel, a V under the fold
    keel=mk(f'craft_{i}_keel_flanks',kb,[NB],coll,bevel=0,smooth=False)
    set_uv(keel,lambda co,n:(((co.y+4.0)/8.7) if n.x>0 else ((4.7-co.y)/8.7),0.38+(co.z+0.26)/0.81*0.3))
    box(bm,(0,0.3,-0.27),(0.32,8.0,0.05),N)                                           # red ink along the keel
    box(bm,(0,0.5,0.58),(0.06,8.2,0.03),B)                                            # the fold's crease
    for s in (-1,1): nozzle(bm,(s*0.42,-4.0,0.0),0.26,0.45,K,Mt,E); loft(bm,[(-1.8,0.22,0.0,0.24,0.24),(-3.6,0.27,0.0,0.27,0.27)],B,e=2.2,n=16,xoff=s*0.42)
    hover_pads(bm,[(0,1.8,0.5,4.0,-0.3),(-1.3,-2.6,0.7,1.6,0.38),(1.3,-2.6,0.7,1.6,0.38)],K,N)
    mk(f'craft_{i}_keel',bm,slots(m),coll,bevel=0.01,seg=1)
    # the red pencil lying along the right wing's leading edge
    PR=mat('pencil_red',col=srgb('#c4161e'),rough=0.35,coat=0.5); PW=mat('pencil_wood',col=srgb('#e3c08a'),rough=0.8); PE=mat('pencil_eraser',col=srgb('#e88a8a'),rough=0.9)
    bm=bmesh.new(); a=Vector((2.05,-3.2,0.95)); b=Vector((0.55,2.4,0.73)); d=(b-a).normalized()
    tube(bm,a,b,0.15,0.15,0,seg=6); tube(bm,b,b+d*0.55,0.15,0.035,1,seg=6); tube(bm,b+d*0.55,b+d*0.7,0.035,0.0,3,seg=6)
    tube(bm,a,a-d*0.22,0.155,0.155,3,seg=12); tube(bm,a-d*0.22,a-d*0.45,0.15,0.15,2,seg=12)
    for k in (-1,1): tube(bm,a+Vector((0,0,0.0))-d*0.05+Vector((0,0,-0.0)),a+Vector((k*0.0,0,-0.62)),0.03,0.03,3,seg=6)   # a strut down to the wing
    mk(f'craft_{i}_pencil',bm,[PR,PW,PE,m['K']],coll,bevel=0.01,seg=1,smooth=False)
    stern_decal(f'craft_{i}_stern',-0.7,0.7,-0.24,0.5,-4.02,m['S'],coll)
    flaps(coll,[('L',(-1.85,-3.62,0.8)),('R',(1.85,-3.62,0.8))],(0.9,0.42),PAPER,thick=0.04)
    return (-0.42,-4.06,0.0),(0.42,-4.06,0.0)

# ================================================================== 3 · NATURVINSBAREN
def craft_amphora(i,coll,m):
    """A terracotta amphora on its side, neck and cork forward, handles on the shoulders, a black-figure meander round
    the belly and the bar's own label on top; two small amphorae as engine pods on a wooden yoke, glowing orange."""
    TC=mat('terracotta',col=srgb(TEAMS[i]['a']),rough=0.75,coat=0.15); TD=mat('terracotta_dark',col=srgb('#8a3a1a'),rough=0.8)
    CORK=mat('cork',col=srgb('#a8865a'),rough=0.95); OAK=mat('oak',tex='craft_walnut.jpg',rough=0.5,coat=0.4)
    zc=0.64; prof=[(3.95,0.48),(3.75,0.48),(3.62,0.34),(2.7,0.33),(2.35,0.5),(1.7,0.86),(0.7,1.0),(-0.5,1.02),(-1.9,0.88),(-3.0,0.56),(-3.7,0.24)]
    bm=bmesh.new(); loft(bm,[(y,r,zc,r,r) for y,r in prof],0,n=36,e=2.0,tip_back=(-4.3,zc),cap_front=True)
    for s in (-1,1):   # the handles, from the shoulder over to the neck
        pts=[(s*0.72,1.55,zc+0.5),(s*0.98,1.9,zc+0.82),(s*0.82,2.45,zc+0.95),(s*0.5,2.85,zc+0.62),(s*0.36,2.95,zc+0.3)]
        pipe(bm,pts,0.085,0,seg=12)
    mk(f'craft_{i}_amphora',bm,[TC],coll,bevel=0,subsurf=0)
    # the meander band round the belly: a ring just proud of it, cylindrical UVs
    bm=bmesh.new(); loft(bm,[(-0.15,1.035,zc,1.035,1.035),(-0.55,1.03,zc,1.03,1.03)],0,n=48,e=2.0,cap_back=False,cap_front=False)
    band=mk(f'craft_{i}_band',bm,[mat('meander_3',tex='craft_meander_3.jpg',rough=0.7)],coll,closed=False,bevel=0,wn=False)
    set_uv(band,lambda co,n:((math.atan2(co.z-zc,co.x)/(2*math.pi)+0.5)*2,(co.y+0.55)/0.4))
    bm=bmesh.new(); A,B,K,Mt,Gd,E,N=S('A'),S('B'),S('K'),S('M'),S('Gd'),S('E'),S('N')
    tube(bm,(0,3.92,zc),(0,4.42,zc),0.32,0.3,0,seg=24)   # the cork (slot 0 of its own mesh below)
    mk(f'craft_{i}_cork',bm,[CORK],coll,bevel=0.02,seg=1)
    bm=bmesh.new()
    for s in (-1,1):
        x=s*2.05; loft(bm,[(2.4,0.18,0.15,0.18,0.18),(2.0,0.2,0.15,0.2,0.2),(1.5,0.38,0.15,0.38,0.38),(0.3,0.46,0.15,0.46,0.46),(-2.4,0.42,0.15,0.42,0.42),(-3.3,0.3,0.15,0.3,0.3)],0,n=24,xoff=x,tip_front=(2.55,0.15))
        nozzle(bm,(x,-3.32,0.15),0.29,0.45,K,Mt,E); box(bm,(x,-0.6,0.6),(0.05,4.0,0.05),N)
    mk(f'craft_{i}_pods',bm,[TD]+slots(m)[1:],coll,bevel=0,subsurf=0)
    bm=bmesh.new()
    for yy in (1.1,-1.7): box(bm,(0,yy,0.2),(4.5,0.36,0.16),0); box(bm,(0,yy,0.32),(4.5,0.1,0.08),1)
    yoke=mk(f'craft_{i}_yoke',bm,[OAK,m['Gd']],coll,bevel=0.02,seg=1); box_uv(yoke,0.4)
    bm=bmesh.new(); hover_pads(bm,[(0,1.4,1.0,2.4,-0.4),(0,-1.4,0.9,2.0,-0.38),(-2.05,-0.6,0.36,4.2,-0.33),(2.05,-0.6,0.36,4.2,-0.33)],0,1)
    mk(f'craft_{i}_hover',bm,[m['K'],m['N']],coll,bevel=0)
    LB=mat('label_3',tex='craft_label_3.jpg',rough=0.8)
    top_decal(f'craft_{i}_label',-0.62,0.62,-0.85,0.05,zc+1.04,LB,coll)
    flaps(coll,[('L',(-2.05,-2.9,0.6)),('R',(2.05,-2.9,0.6))],(0.6,0.5),TD)
    return (-2.05,-3.38,0.15),(2.05,-3.38,0.15)

# ================================================================== 4 · VERNISSAGEN
def craft_cube(i,coll,m):
    """The white cube: a crisp white gallery box with a ceiling track of spotlights, a framed abstract on each side and on
    the stern (with its wall label and the red dot), engines on two white plinths."""
    WH=mat('gallery_white',col=(0.86,0.86,0.84),rough=0.55); BL=mat('gallery_black',col=(0.03,0.03,0.035),rough=0.4,metal=0.3)
    OAKF=mat('frame_oak',col=srgb('#c9a676'),rough=0.55)
    bm=bmesh.new(); box(bm,(0,0.6,0.55),(3.6,7.8,1.6),0); mk(f'craft_{i}_cube',bm,[WH],coll,bevel=0.03,seg=2)
    bm=bmesh.new(); A,B,K,Mt,Gd,E,N=S('A'),S('B'),S('K'),S('M'),S('Gd'),S('E'),S('N')
    for s in (-1,1):
        box(bm,(s*0.8,0.6,1.47),(0.08,7.2,0.06),K)
        for yy in (3.6,-2.4): box(bm,(s*0.8,yy,1.41),(0.03,0.03,0.08),K)
        for k in range(5):   # the spotlights, tipped out toward the paintings
            y=3.2-k*1.35; p0=Vector((s*0.8,y,1.44)); d=Vector((s*0.55,0.0,-0.4)).normalized()
            tube(bm,p0,p0+d*0.32,0.07,0.1,K,seg=12); disc(bm,tuple(p0+d*0.325),0.085,tuple(d),N,seg=12)
        x=s*2.3; box(bm,(x,0.0,0.12),(0.66,6.4,0.72),A)                                     # the plinths
        nozzle(bm,(x,-3.22,0.12),0.27,0.4,K,Mt,E); box(bm,(x,0.0,-0.26),(0.5,6.0,0.04),N)
        for yy in (1.2,-2.0): box(bm,(s*1.95,yy,0.12),(0.3,0.5,0.3),A)
    hover_pads(bm,[(0,2.2,2.4,2.4,-0.29),(0,-1.4,2.4,2.4,-0.29),(-2.3,0.0,0.5,5.8,-0.27),(2.3,0.0,0.5,5.8,-0.27)],K,N)
    mk(f'craft_{i}_rig',bm,slots(m),coll,bevel=0.01,seg=1)
    bm=bmesh.new()
    for s in (-1,1):   # frames on the sides
        for (cy,cz,w,h) in ((0.4,0.9,2.3,0.76),):
            for (dy,dz,sw,sh) in ((0,h/2,w+0.12,0.07),(0,-h/2,w+0.12,0.07),(w/2,0,0.07,h),(-w/2,0,0.07,h)):
                box(bm,(s*1.83,cy+dy,cz+dz),(0.07,sw if sh==0.07 else 0.07,sh if sh!=0.07 else 0.07),0)
    for (dx,dz,sw,sh) in ((0,0.52,2.18,0.07),(0,-0.52,2.18,0.07),(1.06,0,0.07,1.1),(-1.06,0,0.07,1.1)):   # the stern frame
        box(bm,(dx-0.3,-3.33,0.62+dz),(sw,0.07,sh),0)
    mk(f'craft_{i}_frames',bm,[OAKF],coll,bevel=0.01,seg=1)
    PA=mat('paint_4a',tex='craft_paint_4a.jpg',rough=0.7); PB=mat('paint_4b',tex='craft_paint_4b.jpg',rough=0.7)
    CA=mat('card_4',tex='craft_card_4.jpg',rough=0.6); RR=mat('rear_4',tex='craft_rear_4.jpg',rough=0.6)
    side_band(f'craft_{i}_paint',1.815,1.55,-0.75,0.52,1.28,PB,coll)
    stern_decal(f'craft_{i}_paint_stern',-1.33,0.73,0.12,1.12,-3.312,PA,coll)
    stern_decal(f'craft_{i}_card',1.0,1.6,0.35,0.65,-3.312,CA,coll)
    top_decal(f'craft_{i}_rear',-1.45,1.45,-3.2,-2.48,1.356,RR,coll)
    flaps(coll,[('L',(-2.3,-2.95,0.5)),('R',(2.3,-2.95,0.5))],(0.6,0.45),m['A'])
    return (-2.3,-3.28,0.12),(2.3,-3.28,0.12)

# ================================================================== 5 · STIPENDIATERNA
def craft_stack(i,coll,m):
    """A slightly messy stack of grant applications: white sheets and blue folders, the top sheet stamped AVSLAG twice,
    a giant paperclip over the bow, a rubber band round the middle, engines in two blue binders alongside."""
    r=random.Random(41); PAPER=mat('sheet_white',col=(0.86,0.85,0.81),rough=0.85); FOLD=mat('folder_blue',col=srgb(TEAMS[i]['b']),rough=0.55,coat=0.3)
    AV=mat('avslag_5',tex='craft_avslag_5.jpg',rough=0.85); FS=mat('folder_5',tex='craft_folder_5.jpg',rough=0.6)
    bm=bmesh.new(); z=-0.18; L,W=6.8,4.24; YC=0.6
    for k in range(13):
        folder=k%4==1; th=0.13 if folder else 0.06; dx,dy,rot=r.uniform(-0.1,0.1),r.uniform(-0.14,0.14),math.radians(r.uniform(-2.6,2.6))
        box(bm,(dx,YC+dy,z+th/2),(W+(0.14 if folder else 0),L+(0.14 if folder else 0),th),1 if folder else 0,rot=rot); z+=th+0.008
    top_z=z; mk(f'craft_{i}_stack',bm,[PAPER,FOLD],coll,bevel=0.008,seg=1,smooth=False)
    top_decal(f'craft_{i}_avslag',-W/2+0.02,W/2-0.02,YC-L/2+0.02,YC+L/2-0.02,top_z+0.004,AV,coll)
    side_band(f'craft_{i}_spine',W/2+0.08,2.6,-1.6,-0.12,0.18,FS,coll)
    bm=bmesh.new(); A,B,K,Mt,Gd,E,N=S('A'),S('B'),S('K'),S('M'),S('Gd'),S('E'),S('N')
    # the paperclip (a Gem: three nested U-turns) over the bow, at the right
    cx,yb,zt=1.0,YC+L/2-0.45,top_z+0.05
    clip=[(cx-0.28,yb-0.9),(cx-0.28,yb+0.55),(cx+0.3,yb+0.55),(cx+0.3,yb-1.25),(cx-0.42,yb-1.25),(cx-0.42,yb+0.9),(cx+0.42,yb+0.9),(cx+0.42,yb-0.5)]
    pipe(bm,[(x,y,zt) for x,y in clip],0.05,Mt,seg=10)
    pipe(bm,[(cx-0.42,yb+0.9,zt),(cx-0.42,yb+0.9,-0.26),(cx-0.42,yb-0.6,-0.26),(cx+0.42,yb-0.6,-0.26),(cx+0.42,yb+0.9,-0.26),(cx+0.42,yb+0.9,zt)],0.05,Mt)
    # the rubber band round the stack
    zb=-0.22; band=[(-W/2-0.06,-0.9,zb),(-W/2-0.06,-0.9,top_z+0.04),(W/2+0.06,-0.9,top_z+0.04),(W/2+0.06,-0.9,zb)]
    RB=len(slots(m)); pipe(bm,band,0.05,RB,seg=8,closed=True)
    for s in (-1,1):   # the binders with the engines
        x=s*2.62; loft(bm,[(3.4,0.32,0.05,0.3,0.3,4.5),(-3.0,0.32,0.05,0.3,0.3,4.5)],B,n=24,xoff=x)
        nozzle(bm,(x,-3.02,0.05),0.24,0.4,K,Mt,E); box(bm,(x,-0.2,-0.27),(0.4,5.2,0.04),N)
        for yy in (1.6,-1.9): box(bm,(s*2.32,yy,0.0),(0.3,0.4,0.16),Mt)
    hover_pads(bm,[(0,1.8,2.6,2.4,-0.25),(0,-1.6,2.6,2.4,-0.25),(-2.62,-0.2,0.45,5.0,-0.27),(2.62,-0.2,0.45,5.0,-0.27)],K,N)
    mk(f'craft_{i}_kit',bm,slots(m)+[mat('rubber',col=srgb('#b5523a'),rough=0.7)],coll,bevel=0.01,seg=1)
    stern_decal(f'craft_{i}_stern',-1.2,1.2,-0.15,0.45,YC-L/2-0.09,m['S'],coll)
    flaps(coll,[('L',(-2.62,-2.75,0.36)),('R',(2.62,-2.75,0.36))],(0.55,0.5),FOLD)
    return (-2.62,-3.08,0.05),(2.62,-3.08,0.05)

BUILDERS=[craft_aderton,craft_radio,craft_broadsheet,craft_amphora,craft_cube,craft_stack]
crafts=[]
for i,fn in enumerate(BUILDERS):
    if ONLY is not None and i!=ONLY: continue
    cc=bpy.data.collections.new(f'craft_{i}'); scene.collection.children.link(cc)
    m=materials(i); eL,eR=fn(i,cc,m)
    empty('eng_L',eL,cc); empty('eng_R',eR,cc)
    meshes=[o for o in cc.objects if o.type=='MESH']; bpy.context.view_layer.update()
    pts=np.array([tuple(o.matrix_world@v.co) for o in meshes for v in o.data.vertices]); mn,mx=pts.min(0),pts.max(0)
    tris=sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)
    crafts.append((i,cc)); log('craft',i,TEAMS[i]['team'],f'{mx[0]-mn[0]:.2f} x {mx[1]-mn[1]:.2f} x {mx[2]-mn[2]:.2f} m (z {mn[2]:.2f}..{mx[2]:.2f})',tris,'tris')

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
        for j,c2 in crafts: c2.hide_render=(j!=i)
        bake([o for o in cc.objects if o.type=='MESH'])
    for j,c2 in crafts: c2.hide_render=False
    log('baked')

def export(coll,path,vc):
    bpy.ops.object.select_all(action='DESELECT')
    for o in coll.all_objects: o.select_set(True)
    bpy.ops.export_scene.gltf(filepath=path,export_format='GLB',use_selection=True,export_yup=True,export_apply=False,
        export_vertex_color='NAME' if vc else 'NONE',export_vertex_color_name='Col',export_all_vertex_colors=False,
        export_image_format='JPEG',export_jpeg_quality=82,export_materials='EXPORT',export_draco_mesh_compression_enable=True,export_draco_mesh_compression_level=7,
        export_draco_position_quantization=16,export_draco_texcoord_quantization=12,export_draco_color_quantization=8,export_draco_normal_quantization=10)
    log('exported',os.path.basename(path),round(os.path.getsize(path)/1e6,2),'MB')
# the game looks the nodes up by their exact names (eng_L, flap_R, ...), but Blender names are global and the second craft's
# came out as eng_L.001: before each export every craft's nodes get a parking name, then this craft's get the real ones
NODE_KEYS=('eng_L','eng_R','flap_L','flap_R','flap_L_plate','flap_R_plate')
for i,cc in crafts:
    for j,c2 in crafts:
        for o in c2.objects:
            b=o.get('base') or o.name.split('.')[0]
            if b in NODE_KEYS: o['base']=b; o.name=f'x{j}_{b}'
    for o in cc.objects:
        if o.get('base'): o.name=o['base']
    export(cc,os.path.join(OUT,f'craft_{i}.glb'),not NOBAKE)

# ------------------------------------------------------------------ preview stills (Cycles): three-quarter rear and side
if PREVIEW:
    os.makedirs(PREVIEW,exist_ok=True); scene.render.engine='CYCLES'; scene.cycles.samples=48
    try: scene.cycles.use_denoising=True
    except Exception: pass
    scene.render.resolution_x,scene.render.resolution_y=1280,720
    w=bpy.data.worlds.new('pv'); w.use_nodes=True; w.node_tree.nodes['Background'].inputs[0].default_value=(0.62,0.66,0.72,1); w.node_tree.nodes['Background'].inputs[1].default_value=0.9; scene.world=w
    fl=bpy.data.meshes.new('floor'); fl.from_pydata([(-40,-40,-0.9),(40,-40,-0.9),(40,40,-0.9),(-40,40,-0.9)],[],[(0,1,2,3)]); fo=bpy.data.objects.new('floor',fl); scene.collection.objects.link(fo)
    fl.materials.append(mat('pv_floor',col=(0.5,0.5,0.5),rough=0.8))
    sd=bpy.data.lights.new('sun','SUN'); sd.energy=3.2; sd.angle=math.radians(4); so=bpy.data.objects.new('sun',sd); so.rotation_euler=(math.radians(48),0,math.radians(205)); scene.collection.objects.link(so)
    cam=bpy.data.cameras.new('cam'); cam.lens=50; co=bpy.data.objects.new('cam',cam); scene.collection.objects.link(co); scene.camera=co
    def look(pos,tgt):
        co.location=pos; d=Vector(tgt)-Vector(pos); co.rotation_euler=d.to_track_quat('-Z','Y').to_euler()
    for i,cc in crafts:
        for j,c2 in crafts: c2.hide_render=(j!=i)
        name=TEAMS[i]['team'].lower().replace(' ','_')
        for tag,pos in (('',(7.5,-14.5,5.6)),('_side',(-15.5,0.6,2.2))):
            look(pos,(0,-0.3,0.45)); scene.render.filepath=os.path.join(PREVIEW,f'craft_{i}_{name}{tag}.png'); bpy.ops.render.render(write_still=True)
        log('preview',i,name)
log('done')
