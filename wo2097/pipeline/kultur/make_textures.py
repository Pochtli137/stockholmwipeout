"""WIPEOUT KULTURSTOCKHOLM · the track set's textures, drawn with PIL from ../../assets/kultur/copy.json (every word on them
lives there). No neon corporate: cream paper and linen, gallery wall labels, festival banners, pastels, gold leaf and ink, in
Playfair Display, DM Serif Display and Inter (OFL, ../../fonts). Invented league, parody brands, real places and restaurants by
name only, never a logo. Output: tex/*.jpg|png for build.py (the craft textures are craft_textures.py's, same folder).
READABLE AT SPEED IN SUN (the Österlen look test): two short lines, letters about 1 m tall on a 14 x 7 m board (>= 104 px of
1024), dark on light or light on dark, nothing thinner than a stroke of ~6 px. A slogan that cannot be that big fails the build."""
import os, json, math, random
from PIL import Image, ImageDraw, ImageFont
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'tex'); os.makedirs(OUT, exist_ok=True)
FD = os.path.join(H, '..', '..', 'fonts'); C = json.load(open(os.path.join(H, '..', '..', 'assets', 'kultur', 'copy.json')))
def var(name, sz, w):
    f = ImageFont.truetype(os.path.join(FD, name), sz)
    try: f.set_variation_by_axes([w] if 'Playfair' in name else [14, w])   # Inter: opsz, wght
    except Exception:
        try: f.set_variation_by_axes([w])
        except Exception: pass
    return f
SERIF = lambda z, w=900: var('PlayfairDisplay.ttf', z, w)
SERIFI = lambda z, w=800: var('PlayfairDisplay-Italic.ttf', z, w)
DISP = lambda z: ImageFont.truetype(os.path.join(FD, 'DMSerifDisplay-Regular.ttf'), z)
SANS = lambda z, w=700: var('Inter.ttf', z, w)
INK = (29, 26, 22); CREAM = (247, 242, 231); LINEN = (234, 226, 210); GOLD = (184, 144, 28); GOLDL = (232, 196, 96)
BORD = (142, 42, 54); NAVY = (29, 43, 79); FOREST = (31, 75, 58); SAGE = (183, 201, 176); BLUSH = (232, 196, 188); SKY = (188, 211, 227); OCHRE = (196, 140, 54)
def save(im, name, q=90):
    p = os.path.join(OUT, name); (im.convert('RGB').save(p, quality=q) if name.endswith('.jpg') else im.save(p)); return p
def fit(d, lines, font, maxw, start, minsz, what):
    sz = start
    while sz > minsz and max(d.textlength(l, font=font(sz)) for l in lines) > maxw: sz -= 2
    if max(d.textlength(l, font=font(sz)) for l in lines) > maxw: raise SystemExit(f'TOO LONG for {what}: {lines} (min {minsz}px): shorten it in copy.json')
    return font(sz)
def linen(w, h, base=LINEN, seed=1):
    im = Image.new('RGB', (w, h), base); d = ImageDraw.Draw(im); r = random.Random(seed)
    for y in range(0, h, 3): d.line([(0, y), (w, y)], fill=tuple(max(0, c - r.randrange(0, 7)) for c in base))
    for x in range(0, w, 4): d.line([(x, 0), (x, h)], fill=tuple(max(0, c - r.randrange(0, 5)) for c in base))
    return im
PALETTE = {'label': (CREAM, INK, GOLD), 'poster': (None, INK, BORD), 'festival': (None, CREAM, GOLDL)}
PASTELS = [SAGE, BLUSH, SKY, (226, 214, 170), (205, 190, 220)]; DEEP = [BORD, NAVY, FOREST, (110, 72, 40)]

# ---- billboards: 1024 x 512 on 14 x 7 m. The brand on top in serif, the two lines below as big as they go.
NB = len(C['brands'])
for i, B in enumerate(C['brands']):
    w, h = 1024, 512; st = B.get('style', 'label')
    if st == 'label':      # a gallery wall label: cream card, ink type, a thin gold rule
        im = linen(w, h, CREAM, i); d = ImageDraw.Draw(im); fg = INK; ac = GOLD
        d.rectangle([14, 14, w - 15, h - 15], outline=INK, width=4)
        d.text((44, 74), B['n'], font=fit(d, [B['n']], lambda z: SANS(z, 800), w - 100, 66, 40, 'brand ' + B['n']), fill=BORD, anchor='lm')
        d.rectangle([44, 128, w - 44, 133], fill=ac)
        sf = fit(d, B['s'], DISP, w - 88, 156, 104, 'billboard ' + B['n'])
        for ln, y in zip(B['s'], (int(h * .47), int(h * .78))): d.text((44, y), ln, font=sf, fill=fg, anchor='lm')
        d.text((w - 44, h - 36), 'SAKL 2097 · AKRYL PÅ STATSBIDRAG', font=SANS(20, 600), fill=(110, 100, 84), anchor='rm')
    elif st == 'poster':   # an exhibition poster: a pastel field, the name in display serif, the lines in black serif
        bg = PASTELS[i % len(PASTELS)]; im = Image.new('RGB', (w, h), bg); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, w, 150], fill=CREAM); d.rectangle([0, 150, w, 158], fill=INK)
        d.text((40, 78), B['n'], font=fit(d, [B['n']], DISP, w - 80, 104, 52, 'brand ' + B['n']), fill=INK, anchor='lm')
        sf = fit(d, B['s'], DISP, w - 80, 156, 104, 'billboard ' + B['n'])
        for ln, y in zip(B['s'], (int(h * .50), int(h * .80))): d.text((40, y), ln, font=sf, fill=INK, anchor='lm')
    else:                  # a festival banner: a deep colour, cream italic serif, a gold border
        bg = DEEP[i % len(DEEP)]; im = Image.new('RGB', (w, h), bg); d = ImageDraw.Draw(im)
        d.rectangle([10, 10, w - 11, h - 11], outline=GOLDL, width=8)
        d.text((44, 80), B['n'], font=fit(d, [B['n']], lambda z: SANS(z, 800), w - 100, 64, 40, 'brand ' + B['n']), fill=GOLDL, anchor='lm')
        sf = fit(d, B['s'], DISP, w - 88, 156, 104, 'billboard ' + B['n'])
        for ln, y in zip(B['s'], (int(h * .47), int(h * .78))): d.text((44, y), ln, font=sf, fill=CREAM, anchor='lm')
    save(im, f'bill_{i}.jpg')

# ---- the restaurants along the line: their real names in our own type (never their signage), the joke on the guests
for i, R in enumerate(C['restaurants']):
    w, h = 1024, 512; im = Image.new('RGB', (w, h), (24, 30, 26)); d = ImageDraw.Draw(im)
    d.rectangle([12, 12, w - 13, h - 13], outline=GOLDL, width=6); d.rectangle([28, 28, w - 29, h - 29], outline=(120, 100, 50), width=2)
    d.text((w // 2, 92), R['name'], font=fit(d, [R['name']], lambda z: SERIF(z, 900), w - 120, 104, 56, 'restaurant ' + R['name']), fill=GOLDL, anchor='mm')
    d.text((w // 2, 160), 'BORDSBOKNING SEDAN 1786', font=SANS(22, 600), fill=(200, 180, 120), anchor='mm')
    sf = fit(d, R['s'], DISP, w - 100, 130, 96, 'restaurant ' + R['name'])
    for ln, y in zip(R['s'], (int(h * .56), int(h * .82))): d.text((w // 2, y), ln, font=sf, fill=CREAM, anchor='mm')
    save(im, f'rest_{i}.jpg')

# ---- the pit lanes: Riche's awning sign and Den Gyldene Freden's private one; the lane paint on the deck
for k, P in C['pits'].items():
    w, h = 2048, 384; im = linen(w, h, CREAM if k == 'riche' else (36, 30, 24), 7); d = ImageDraw.Draw(im)
    fg = INK if k == 'riche' else GOLDL; ac = BORD if k == 'riche' else GOLDL
    d.rectangle([0, 0, w, 16], fill=ac); d.rectangle([0, h - 16, w, h], fill=ac)
    d.text((w // 2, int(h * .38)), P['sign'], font=fit(d, [P['sign']], lambda z: SERIF(z, 900), w - 160, 200, 120, 'pit ' + k), fill=fg, anchor='mm')
    d.text((w // 2, int(h * .76)), P['sub'], font=fit(d, [P['sub']], lambda z: SANS(z, 700), w - 300, 76, 48, 'pit sub ' + k), fill=fg, anchor='mm')
    save(im, f'pit_{k}.jpg')
w, h = 256, 512; im = Image.new('RGB', (w, h), (0, 0, 0)); d = ImageDraw.Draw(im)   # additive on the deck: black is clear
for y in range(0, h, 64): d.polygon([(0, y), (w, y + 32), (w, y + 52), (0, y + 20)], fill=(150, 112, 24))
d.rectangle([0, 0, 10, h], fill=(220, 190, 110)); d.rectangle([w - 10, 0, w, h], fill=(220, 190, 110))
d.text((w // 2, h // 2), 'PIT', font=SERIF(96, 900), fill=(230, 200, 120), anchor='mm'); save(im, 'pit_lane.png')

# ---- the gantry over the start at Börshuset: cream, the Academy's motto, ink and gold
G = C['gantry']; w, h = 2048, 320; im = linen(w, h, CREAM, 3); d = ImageDraw.Draw(im)
d.rectangle([0, 0, w, 14], fill=GOLD); d.rectangle([0, h - 14, w, h], fill=GOLD)
d.text((w // 2, int(h * .27)), G['title'], font=fit(d, [G['title']], lambda z: SERIF(z, 900), w - 300, 100, 70, 'gantry'), fill=INK, anchor='mm')
d.text((w // 2, int(h * .49)), G['latin'], font=SERIFI(34, 600), fill=BORD, anchor='mm')
d.text((w // 2, int(h * .76)), G['line'], font=fit(d, [G['line']], DISP, w - 320, 104, 80, 'gantry line'), fill=INK, anchor='mm')
for x in (110, w - 110):   # a laurel of two arcs and a crown dot either side
    d.arc([x - 60, int(h * .5) - 70, x + 60, int(h * .5) + 70], 200, 340, fill=GOLD, width=10); d.ellipse([x - 14, int(h * .5) - 90, x + 14, int(h * .5) - 62], fill=GOLD)
save(im, 'gantry.jpg')

# ---- festival banners over the track (the arches): 2048 x 256 on 24 x 2.6 m, name left, the two lines right
for i, A in enumerate(C['arches']):
    w, h = 2048, 256; bg = DEEP[i % len(DEEP)]; im = Image.new('RGB', (w, h), bg); d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, 10], fill=GOLDL); d.rectangle([0, h - 10, w, h], fill=GOLDL)
    d.text((70, h // 2 + 4), A['n'], font=fit(d, [A['n']], lambda z: SERIF(z, 900), 820, 150, 70, 'arch ' + A['n']), fill=GOLDL, anchor='lm')
    d.rectangle([950, 0, w, h], fill=CREAM); d.rectangle([950, 0, 962, h], fill=GOLDL)
    af = fit(d, A['s'], DISP, w - 1010, 124, 96, 'arch ' + A['n'])
    for ln, y in zip(A['s'], (int(h * .30), int(h * .74))): d.text((1000, y), ln, font=af, fill=INK, anchor='lm')
    save(im, f'arch_{i}.jpg')

# ---- the barrier walls: gallery labels on linen, 8192 x 128 px over 104 m of a 1.7 m wall (the title ~0.9 m tall)
def barrier(name, order, acc):
    w, h = 8192, 128; im = linen(w, h, LINEN, len(name)); d = ImageDraw.Draw(im); x = 30; k = 0
    while True:
        t, cap = C['barrier'][order[k % len(order)]]
        tf = SERIFI(84, 800); cf = SANS(30, 600); tw = int(max(d.textlength(t, font=tf), d.textlength(cap, font=cf))) + 90
        if x + tw + 140 > w - 30: break
        d.rectangle([x, 8, x + tw, h - 8], fill=CREAM); d.rectangle([x, 8, x + 8, h - 8], fill=acc)
        d.text((x + 40, 50), t, font=tf, fill=INK, anchor='lm'); d.text((x + 42, 104), cap, font=cf, fill=(96, 88, 74), anchor='lm')
        x += tw + 50
        for j in range(3): cx = x + j * 30; d.ellipse([cx, h // 2 - 7, cx + 14, h // 2 + 7], fill=acc)
        x += 120; k += 1
    d.rectangle([0, 0, w, 6], fill=GOLD); d.rectangle([0, h - 6, w, h], fill=GOLD)
    save(im, name); return k
nL = barrier('barrier_L.jpg', list(range(0, len(C['barrier']), 2)) + list(range(1, len(C['barrier']), 2)), BORD)
nR = barrier('barrier_R.jpg', list(range(1, len(C['barrier']), 2)) + list(range(0, len(C['barrier']), 2)), NAVY)
print('barrier labels per 104 m:', nL, nR)

# ---- the deck: pale limestone slabs, brass inlays at the edges, an ink centre line; u across, v along (32 m a tile)
w, h = 512, 1024; im = Image.new('RGB', (w, h), (122, 117, 108)); d = ImageDraw.Draw(im); r = random.Random(5)
for i in range(8): d.rectangle([0, i * h // 8, w, (i + 1) * h // 8], fill=(124, 119, 110) if i % 2 else (116, 111, 103))
for _ in range(2400): x, y = r.randrange(w), r.randrange(h); c = 100 + r.randrange(36); d.point((x, y), fill=(c, c - 4, c - 10))
for i in range(9): d.line([(0, i * h // 8), (w, i * h // 8)], fill=(92, 88, 80), width=3)
for x in (w // 3, 2 * w // 3): d.line([(x, 0), (x, h)], fill=(100, 96, 88), width=2)
d.rectangle([0, 0, int(w * .05), h], fill=(60, 52, 44)); d.rectangle([int(w * .95), 0, w, h], fill=(60, 52, 44))
d.rectangle([int(w * .06), 0, int(w * .06) + 8, h], fill=(196, 160, 70)); d.rectangle([int(w * .94) - 8, 0, int(w * .94), h], fill=(196, 160, 70))
for y in range(0, h, 128): d.rectangle([w // 2 - 5, y + 20, w // 2 + 5, y + 90], fill=(44, 40, 34))
st = Image.new('RGBA', (700, 140), (0, 0, 0, 0)); sd = ImageDraw.Draw(st); sd.text((350, 70), 'SAKL · MMXCVII', font=SERIF(60, 900), fill=(60, 52, 44, 60), anchor='mm')
st = st.rotate(90, expand=True); im.paste(st, (int(w * .28) - st.width // 2, h // 2 - st.height // 2), st)
save(im, 'track.jpg')
em = Image.new('RGB', (w, h), (0, 0, 0)); e = ImageDraw.Draw(em)
e.rectangle([int(w * .06), 0, int(w * .06) + 8, h], fill=(120, 96, 40)); e.rectangle([int(w * .94) - 8, 0, int(w * .94), h], fill=(120, 96, 40))
save(em, 'track_e.jpg')

# ---- pads: the speed pad (gold chevrons, KULTURBIDRAG) and the pickup pad (a wax seal: FÖRMÅN); black = clear under additive blending
w, h = 256, 512; im = Image.new('RGB', (w, h), (0, 0, 0)); d = ImageDraw.Draw(im); d.rectangle([8, 8, w - 8, h - 8], outline=(200, 160, 60), width=8)
for k in range(3):
    y = h * .78 - k * h * .24; col = (230 - k * 10, 180 + k * 15, 70 + k * 20)
    d.polygon([(w * .12, y), (w * .5, y - h * .14), (w * .88, y), (w * .88, y + 34), (w * .5, y - h * .14 + 34), (w * .12, y + 34)], fill=col)
d.text((w / 2, h * .93), C['pads']['speed'], font=fit(d, [C['pads']['speed']], lambda z: SANS(z, 700), w - 16, 26, 7, 'pad'), fill=(240, 220, 160), anchor='mm'); save(im, 'pad_speed.png')
w = h = 512; im = Image.new('RGB', (w, h), (0, 0, 0)); d = ImageDraw.Draw(im)
d.ellipse([60, 60, w - 60, h - 60], fill=(170, 30, 40)); d.ellipse([100, 100, w - 100, h - 100], outline=(240, 200, 120), width=10)
for k in range(12):
    a = k * math.pi / 6; d.ellipse([w / 2 + math.cos(a) * 205 - 26, h / 2 + math.sin(a) * 205 - 26, w / 2 + math.cos(a) * 205 + 26, h / 2 + math.sin(a) * 205 + 26], fill=(150, 24, 34))
d.text((w / 2, h / 2 - 10), 'F', font=SERIF(170, 900), fill=(245, 215, 140), anchor='mm')
d.text((w / 2, h - 34), C['pads']['weapon'], font=fit(d, [C['pads']['weapon']], lambda z: SANS(z, 700), w - 40, 30, 14, 'wpad'), fill=(245, 215, 140), anchor='mm'); save(im, 'pad_weapon.png')
print('textures ->', OUT, 'billboards', NB, 'restaurants', len(C['restaurants']), 'arches', len(C['arches']))
