"""Look test (2026-10-02): the two Blender hero landmarks, from OpenStreetMap, into landmarks.json for build_landmarks.py.
   python3 landmarks.py <overpass.json>
Ales stenar: OSM has 57 of the 59 stones as nodes (historic=stone). They are ordered round the ship's outline and the two
widest gaps get one stone each, so there are 59. Glimmingehus: the OSM footprint (way 456871043), centre, length, width and
the bearing of its long axis. Metres are in the game frame: x = west, z = north, round each landmark's own centre."""
import json, math, sys
d = json.load(open(sys.argv[1]))
stones = [(e['lat'], e['lon']) for e in d['elements'] if e['type'] == 'node' and e.get('tags', {}).get('historic') == 'stone']
glim = next(e for e in d['elements'] if e['type'] == 'way' and e.get('tags', {}).get('name') == 'Glimmingehus')

def local(pts, lat0, lon0):
    ml = 111320 * math.cos(math.radians(lat0))
    return [(-(lo - lon0) * ml, (la - lat0) * 111320) for la, lo in pts]   # x west, z north

lat0 = sum(p[0] for p in stones) / len(stones); lon0 = sum(p[1] for p in stones) / len(stones)
P = local(stones, lat0, lon0)
P.sort(key=lambda q: math.atan2(q[1], q[0]))
while len(P) < 59:
    gaps = [(math.dist(P[i], P[(i + 1) % len(P)]), i) for i in range(len(P))]
    g, i = max(gaps); a, b = P[i], P[(i + 1) % len(P)]
    P.insert(i + 1, ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
# the long axis (PCA) and the stems: the two stones furthest along it
sxx = sum(x * x for x, z in P); szz = sum(z * z for x, z in P); sxz = sum(x * z for x, z in P)
ang = 0.5 * math.atan2(2 * sxz, sxx - szz); ux, uz = math.cos(ang), math.sin(ang)
along = [x * ux + z * uz for x, z in P]; half = max(abs(a) for a in along)
L = max(along) - min(along); W = max(-x * uz + z * ux for x, z in P) - min(-x * uz + z * ux for x, z in P)
out_st = []
for (x, z), a in zip(P, along):
    k = abs(a) / half
    h = 3.3 if k > 0.97 else 1.0 + 1.5 * k ** 3   # the stems are the tallest (about 3.3 m), the sides rise toward them
    out_st.append({'x': round(x, 2), 'z': round(z, 2), 'h': round(h, 2)})
# bearing of the long axis, from north clockwise (x is west, so east = -x)
bear = math.degrees(math.atan2(-ux, uz)) % 180
g = [(p['lat'], p['lon']) for p in glim['geometry']][:-1]
glat = sum(p[0] for p in g) / len(g); glon = sum(p[1] for p in g) / len(g)
G = local(g, glat, glon)
gxx = sum(x * x for x, z in G); gzz = sum(z * z for x, z in G); gxz = sum(x * z for x, z in G)
ga = 0.5 * math.atan2(2 * gxz, gxx - gzz); gux, guz = math.cos(ga), math.sin(ga)
gl = [x * gux + z * guz for x, z in G]; gw = [-x * guz + z * gux for x, z in G]
res = {'ales': {'lat': lat0, 'lon': lon0, 'stones': out_st, 'lengthM': round(L, 1), 'widthM': round(W, 1), 'axisBearing': round(bear, 1)},
       'glimmingehus': {'lat': glat, 'lon': glon, 'lengthM': round(max(gl) - min(gl), 1), 'widthM': round(max(gw) - min(gw), 1),
                        'axisAngleRad': round(ga, 4), 'axisBearing': round(math.degrees(math.atan2(-gux, guz)) % 180, 1), 'heightM': 26}}
json.dump(res, open(__file__.replace('landmarks.py', 'landmarks.json'), 'w'), indent=1)
print('ales', len(out_st), 'stones', res['ales']['lengthM'], 'x', res['ales']['widthM'], 'm, axis', res['ales']['axisBearing'], 'deg')
print('glimmingehus', res['glimmingehus'])
