"""Look test (2026-10-02): two simple hero landmarks for Wipeout Österlen, in Blender, from landmarks.json.
   blender -b --factory-startup -P build_landmarks.py
-> test_assets/ales_stenar.glb: 59 stones (stone_00..58), each its own node standing on its own footing at y 0, so the
   test page can sit every stone on Google's terrain. Ship outline, 65 x 18 m on its NW-SE axis, from OSM.
-> test_assets/glimmingehus.glb: the keep, 32 x 13 m (OSM footprint), walls to 17 m, a slate roof to 24 m and two
   stepped gables to 26 m on the short ends, rows of small deep windows. Origin at the footprint centre, ground level.
Blender (x, y, z) exports as glTF (x, z, -y); the game frame is x = west, y = up, z = north, so Blender y = -north."""
import bpy, bmesh, json, math, os, random
from mathutils import Vector, Matrix
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(HERE, 'test_assets'); os.makedirs(OUT, exist_ok=True)
L = json.load(open(os.path.join(HERE, 'landmarks.json')))
random.seed(7)

def clear():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, col, rough=0.8, metal=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes['Principled BSDF']; b.inputs['Base Color'].default_value = (*col, 1)
    b.inputs['Roughness'].default_value = rough; b.inputs['Metallic'].default_value = metal
    return m

def obj_from_bm(name, bm, m):
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free(); me.materials.append(m)
    o = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(o); return o

def export(path):
    bpy.ops.export_scene.gltf(filepath=path, export_format='GLB', export_apply=True, export_yup=True)

def G(x_west, z_north, y_up=0.0):   # game frame -> Blender
    return Vector((x_west, -z_north, y_up))

# ---------------------------------------------------------------- Ales stenar
clear()
granite = [mat('stone_a', (0.22, 0.21, 0.19), 0.92), mat('stone_b', (0.27, 0.26, 0.23), 0.9), mat('stone_c', (0.18, 0.18, 0.17), 0.95)]
st = L['ales']['stones']
for i, s in enumerate(st):
    p = Vector((s['x'], s['z'])); q = Vector((st[(i + 1) % len(st)]['x'], st[(i + 1) % len(st)]['z'])); r = Vector((st[i - 1]['x'], st[i - 1]['z']))
    tan = (q - r).normalized()                                  # the outline's direction: the stone's broad face follows it
    h = s['h']; w = 0.9 + 0.35 * h + random.uniform(-0.15, 0.2); t = 0.55 + 0.15 * h
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:                                          # a rough slab: narrower at the top, lumpy
        x, y, z = v.co.x, v.co.y, v.co.z + 0.5
        k = 1.0 - 0.35 * z
        v.co = Vector((x * w * k + random.uniform(-0.08, 0.08), y * t * (1 - 0.2 * z) + random.uniform(-0.06, 0.06), z * h + (random.uniform(-0.12, 0.05) if z > 0.9 else -0.4 * (1 - z))))
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=1, use_grid_fill=True)
    for v in bm.verts: v.co += Vector((random.uniform(-0.04, 0.04), random.uniform(-0.04, 0.04), random.uniform(-0.03, 0.03) if v.co.z > 0.1 else 0))
    o = obj_from_bm(f'stone_{i:02d}', bm, random.choice(granite))
    yaw = math.atan2(-tan.y, tan.x)                             # broad face along the outline (Blender y = -north)
    o.rotation_euler = (random.uniform(-0.05, 0.05), random.uniform(-0.05, 0.05), yaw)
    o.location = G(s['x'], s['z'], 0.0)
export(os.path.join(OUT, 'ales_stenar.glb'))
print('ales_stenar', len(st), 'stones')

# ---------------------------------------------------------------- Glimmingehus
clear()
GL = L['glimmingehus']; LEN, WID = GL['lengthM'], GL['widthM']; EAVE, RIDGE, TOP = 17.0, 24.0, 26.0
wall = mat('glim_wall', (0.42, 0.39, 0.33), 0.85); lime = mat('glim_lime', (0.55, 0.53, 0.49), 0.8)
roof = mat('glim_roof', (0.13, 0.13, 0.14), 0.7); win = mat('glim_window', (0.03, 0.03, 0.035), 0.4)
parts = []
def box(name, cx, cy, cz, sx, sy, sz, m):
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector((sx, sy, sz)), verts=bm.verts); bmesh.ops.translate(bm, vec=Vector((cx, cy, cz)), verts=bm.verts)
    o = obj_from_bm(name, bm, m); parts.append(o); return o
# the keep: long axis along Blender x, rotated to the OSM bearing at the end
box('keep', 0, 0, EAVE / 2, LEN, WID, EAVE, wall)
# roof: a prism along x from the eaves to the ridge, a little overhang
bm = bmesh.new(); hw = WID / 2 + 0.4; hl = LEN / 2 - 0.6
vs = [bm.verts.new(v) for v in [(-hl, -hw, EAVE), (hl, -hw, EAVE), (hl, hw, EAVE), (-hl, hw, EAVE), (-hl, 0, RIDGE), (hl, 0, RIDGE)]]
for f in [(0, 1, 5, 4), (2, 3, 4, 5), (0, 4, 3), (1, 2, 5), (0, 3, 2, 1)]: bm.faces.new([vs[i] for i in f])
parts.append(obj_from_bm('roof', bm, roof))
# stepped gables on both short ends: 1.4 m thick walls rising above the roof line in steps
NST = 6
for sx in (-1, 1):
    x = sx * (LEN / 2 - 0.7)
    for k in range(NST):
        y0 = -WID / 2 + k * (WID / 2) / NST; y1 = WID / 2 - k * (WID / 2) / NST
        z0 = EAVE + k * (TOP - EAVE) / NST; z1 = EAVE + (k + 1) * (TOP - EAVE) / NST
        box(f'gable_{sx}_{k}', x, 0, (z0 + z1) / 2, 1.4, y1 - y0, z1 - z0, lime)
    box(f'gable_top_{sx}', x, 0, TOP + 0.6, 1.4, 1.4, 1.2, lime)
# windows: small, deep, in rows on all four faces
for z in (3.5, 7.5, 11.0, 14.5):
    for i in range(-3, 4):
        if random.random() < 0.25: continue
        for sy in (-1, 1): box(f'w_{z}_{i}_{sy}', i * LEN / 8, sy * (WID / 2 + 0.02), z, 0.9, 0.1, 1.5 if z > 4 else 0.9, win)
    for j in (-1, 1):
        for sx in (-1, 1): box(f'we_{z}_{j}_{sx}', sx * (LEN / 2 + 0.02), j * WID / 5, z, 0.1, 0.9, 1.4, win)
# the plinth: a band of darker stone at the foot
box('plinth', 0, 0, 0.6, LEN + 0.6, WID + 0.6, 2.2, mat('glim_plinth', (0.45, 0.42, 0.38), 0.95))
# join, rotate to the OSM long axis (axisAngleRad: angle of the axis from game +x = west toward +z = north)
bpy.ops.object.select_all(action='DESELECT')
for o in parts: o.select_set(True)
bpy.context.view_layer.objects.active = parts[0]; bpy.ops.object.join(); keep = bpy.context.active_object; keep.name = 'glimmingehus'
a = GL['axisAngleRad']   # in the game frame the axis is (cos a, sin a) in (west, north); Blender (x, y) = (west, -north)
keep.rotation_euler = (0, 0, -a)
export(os.path.join(OUT, 'glimmingehus.glb'))
print('glimmingehus', LEN, 'x', WID, 'm, to', TOP, 'm')
