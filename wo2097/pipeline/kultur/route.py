"""WIPEOUT KULTURSTOCKHOLM · the route through the cultural landmarks (2026-10-02).
A hand-laid control polygon in big arcs, landmark by landmark (OSM positions). A first version followed the street
network (foot routing), but the city's zig-zags made the 120 m smoothing cut every landmark off (6.9 km, Gröna Lund
322 m away); the Stockholm lap is a skyway over the roofs too, so the line is laid for flow and the dump calibrates it to
the street and roof heights under it. Writes ../../assets/kultur/route_osm.json ([[lat, lon], ...], a closed lap from
Börshuset at Stortorget), which design_track.py smooths to the 120 m racing line:
    python3 route.py && python3 ../design_track.py kultur && python3 plot_route.py"""
import json, os, math
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, '..', '..', 'assets', 'kultur', 'route_osm.json')
WP = [  # lat, lon; the comment is what the line passes
    (59.32515, 18.07060),  # Börshuset, Stortorget: the start
    (59.32400, 18.07020), (59.32230, 18.07150), (59.32030, 18.07270),  # Gamla stan south, west of Tyska kyrkan's spire (96 m), Slussen
    (59.31910, 18.07450), (59.31870, 18.07900), (59.31830, 18.08300), (59.31810, 18.08600),  # Stadsgårdskajen, Fotografiska
    (59.31950, 18.08680), (59.32150, 18.08550), (59.32320, 18.08300), (59.32430, 18.08170),  # over Saltsjön to af Chapman
    (59.32560, 18.08300), (59.32630, 18.08520), (59.32580, 18.08800), (59.32480, 18.09000),  # Skeppsholmen, Moderna museet
    (59.32380, 18.09300), (59.32340, 18.09620),  # over the water to Gröna Lund
    (59.32400, 18.09950), (59.32530, 18.10250), (59.32650, 18.10350),  # up to Skansen
    (59.32800, 18.10100), (59.32900, 18.09750), (59.32950, 18.09400),  # Nordiska museet (Vasamuseet to the left)
    (59.33130, 18.09150), (59.33250, 18.08850), (59.33280, 18.08400), (59.33300, 18.08000),  # Djurgårdsbron, Strandvägen
    (59.33300, 18.07680),  # Nybroplan, Dramaten
    (59.33150, 18.07700), (59.32980, 18.07850), (59.32850, 18.07850),  # down Blasieholmen to Nationalmuseum
    (59.32830, 18.07550), (59.32900, 18.07280), (59.32970, 18.07080),  # Strömkajen to Kungliga Operan
    (59.33080, 18.06850), (59.33200, 18.06620), (59.33250, 18.06450),  # Kulturhuset, Sergels torg
    (59.33120, 18.06330), (59.33030, 18.06020),  # east of Klara kyrka's spire (116 m), Tegelbacken
    (59.32900, 18.05800), (59.32760, 18.05600), (59.32680, 18.05600),  # Stadshuset
    (59.32600, 18.05850), (59.32520, 18.06200), (59.32480, 18.06450), (59.32500, 18.06750),  # over the water to Riddarholmen
]
M_LON = 111320 * math.cos(math.radians(59.328))
pts = []
for a, b in zip(WP, WP[1:] + WP[:1]):   # straight legs every ~20 m (design_track.py resamples and relaxes them)
    n = max(1, int(math.hypot((b[0] - a[0]) * 111320, (b[1] - a[1]) * M_LON) / 20))
    pts += [(a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n) for k in range(n)]
L = sum(math.hypot((b[0] - a[0]) * 111320, (b[1] - a[1]) * M_LON) for a, b in zip(pts, pts[1:] + pts[:1]))
json.dump([[round(a, 6), round(b, 6)] for a, b in pts], open(OUT, 'w'))
print('route', len(pts), 'points,', round(L), 'm ->', os.path.relpath(OUT, H))
