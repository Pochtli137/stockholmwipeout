"""Distance along the lap -> lat/lon and the nearest named place, for picking where the drops go."""
import json, os, math, sys
H = os.path.dirname(os.path.abspath(__file__)); A = os.path.join(H, '..', '..', 'assets')
T = json.load(open(os.path.join(A, 'track.json')))
O_LAT, O_LON = 59.32800, 18.06000
M_LAT = 111320; M_LON = 111320 * math.cos(O_LAT * math.pi / 180)
PLACES = {
    'Medborgarplatsen': (59.3143, 18.0730), 'Slussen': (59.3197, 18.0722), 'Skeppsbron': (59.3238, 18.0760),
    'Strömmen/Slottet': (59.3268, 18.0730), 'Norrmalmstorg': (59.3337, 18.0733), 'Kungsträdgården': (59.3310, 18.0715),
    'Nybroplan': (59.3330, 18.0780), 'Strandvägen': (59.3322, 18.0850), 'Stureplan': (59.3355, 18.0740),
    'Östermalmstorg': (59.3350, 18.0790), 'Karlavägen': (59.3395, 18.0800), 'Sveavägen': (59.3400, 18.0590),
    'Tegelbacken': (59.3302, 18.0620), 'Stadshuset': (59.3275, 18.0545), 'Fleminggatan': (59.3330, 18.0350),
    'Västerbron': (59.3230, 18.0270), 'Riddarfjärden N': (59.3265, 18.0480), 'Hornsgatan': (59.3170, 18.0500),
    'Götgatan': (59.3150, 18.0710), 'Söder Mälarstrand': (59.3205, 18.0550), 'Gamla stan': (59.3250, 18.0710),
    'Riddarholmen': (59.3250, 18.0640), 'Kungsholmen strand': (59.3290, 18.0400), 'Hantverkargatan': (59.3310, 18.0450)}
fr = T['frames']; L = T['trackLen']

def at(dist):
    i = int(dist / L * len(fr)) % len(fr); x, y, z = fr[i][0], fr[i][1], fr[i][2]
    lat = O_LAT + z / M_LAT; lon = O_LON - x / M_LON
    best = min(PLACES.items(), key=lambda kv: math.hypot((kv[1][0] - lat) * M_LAT, (kv[1][1] - lon) * M_LON))
    d = math.hypot((best[1][0] - lat) * M_LAT, (best[1][1] - lon) * M_LON)
    return lat, lon, y, best[0], d

if __name__ == '__main__':
    for a in sys.argv[1:] or [str(k) for k in range(0, 11400, 400)]:
        lat, lon, y, pl, d = at(float(a))
        print('%6s m  %.5f %.5f  y %5.1f  near %s (%d m)' % (a, lat, lon, y, pl, d))
