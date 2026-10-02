"""WIPEOUT KULTURSTOCKHOLM · textures for the six craft, drawn with PIL into tex/craft_*.jpg (build_craft.py reads them).
Team names, numbers, colours and Latin mottos come from ../../assets/kultur/copy.json (`teams`), so a rename there only
needs this and build_craft.py re-run. Fonts are the OFL ones the game embeds (../../fonts). Satire of types, no real
people, no real logos or producers.     python3 craft_textures.py"""
import os, json, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(H, 'tex'); os.makedirs(OUT, exist_ok=True)
FD = os.path.join(H, '..', '..', 'fonts')
COPY = json.load(open(os.path.join(H, '..', '..', 'assets', 'kultur', 'copy.json'), encoding='utf-8')); TEAMS = COPY['teams']

def _var(path, sz, wght):
    f = ImageFont.truetype(os.path.join(FD, path), sz)
    try:
        axes = f.get_variation_axes(); vals = []
        for a in axes:
            nm = a.get('name', b'');
            nm = nm.decode() if isinstance(nm, bytes) else str(nm)
            vals.append(wght if 'eight' in nm or nm == 'wght' else (min(max(sz * 0.75, a['minimum']), a['maximum']) if 'ptical' in nm or nm == 'opsz' else a['default']))
        f.set_variation_by_axes(vals)
    except Exception: pass
    return f
def play(sz, w=900): return _var('PlayfairDisplay.ttf', sz, w)
def playi(sz, w=700): return _var('PlayfairDisplay-Italic.ttf', sz, w)
def dms(sz): return ImageFont.truetype(os.path.join(FD, 'DMSerifDisplay-Regular.ttf'), sz)
def inter(sz, w=600): return _var('Inter.ttf', sz, w)
def hx(h): h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))
def fit(d, s, ff, start, maxw, minsz=10):
    sz = start
    while sz > minsz and d.textlength(s, font=ff(sz)) > maxw: sz -= 2
    return ff(sz)
def save(im, name, q=90):
    im.convert('RGB').save(os.path.join(OUT, name), quality=q); return name
GOLD = (212, 175, 55); GOLD_L = (240, 214, 120); INK = (24, 22, 20); RED = (196, 28, 36); CREAM = (242, 236, 222)
rnd = random.Random(18)

# ---- wood: mahogany (DE ADERTON) and walnut (SOMMARPRATARNA), lacquered grain, tiles along u
def wood(name, base, dark, w=1024, h=512, seed=1):
    r = random.Random(seed); im = Image.new('RGB', (w, h), base); px = im.load()
    ph = [r.uniform(0, 6.28) for _ in range(6)]
    for y in range(h):
        for x in range(w):
            g = math.sin(y * 0.06 + 3.0 * math.sin(x * 0.004 + ph[0]) + 1.2 * math.sin(x * 0.011 + ph[1]) + ph[2])
            g2 = math.sin(y * 0.21 + 2.0 * math.sin(x * 0.007 + ph[3]))
            k = 0.5 + 0.32 * g + 0.12 * g2
            px[x, y] = tuple(int(dark[c] + (base[c] - dark[c]) * max(0, min(1, k))) for c in range(3))
    im = im.filter(ImageFilter.GaussianBlur(0.6)); return save(im, name)
wood('craft_mahogany.jpg', (122, 46, 26), (58, 18, 10), seed=3)
wood('craft_walnut.jpg', (128, 84, 48), (62, 38, 20), seed=7)

# ---- DE ADERTON: the eighteen chair backs (a 9 x 2 atlas, cell k = chair k+1), and the gilded plaque on the stern
T0 = TEAMS[0]
w, h = 1152, 256; im = Image.new('RGB', (w, h), (92, 16, 26)); d = ImageDraw.Draw(im)
for k in range(18):
    cx, cy = (k % 9) * 128, (k // 9) * 128
    d.rectangle([cx, cy, cx + 127, cy + 127], fill=(104, 18, 30)); d.rectangle([cx + 6, cy + 6, cx + 121, cy + 121], outline=GOLD, width=5)
    for j in range(5): d.line([(cx + 14, cy + 20 + j * 22), (cx + 114, cy + 20 + j * 22)], fill=(90, 14, 24), width=2)   # velvet tufting
    d.text((cx + 64, cy + 68), str(k + 1), font=play(76), fill=GOLD_L, anchor='mm')
save(im, 'craft_chairs.jpg')
w, h = 1024, 384; im = Image.open(os.path.join(OUT, 'craft_mahogany.jpg')).resize((w, h)); d = ImageDraw.Draw(im)
d.rectangle([14, 14, w - 15, h - 15], outline=GOLD, width=10); d.rectangle([34, 34, w - 35, h - 35], outline=GOLD_L, width=3)
d.text((w // 2, int(h * .36)), T0['team'], font=fit(d, T0['team'], play, 150, w - 140), fill=GOLD_L, anchor='mm')
d.text((w // 2, int(h * .68)), T0['latin'].upper() + '  ·  ' + T0['n'], font=playi(54), fill=GOLD, anchor='mm')
save(im, 'craft_plaque_0.jpg')

# ---- SOMMARPRATARNA: the tuning dial (stations as on an old set, all invented or plain place names) and the speaker cloth
T1 = TEAMS[1]
w, h = 1024, 192; im = Image.new('RGB', (w, h), (238, 222, 178)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, w - 1, h - 1], outline=(150, 112, 50), width=10)
for i in range(0, 61):
    x = 40 + i * (w - 80) / 60; d.line([(x, 132), (x, 132 + (26 if i % 5 == 0 else 13))], fill=INK, width=3 if i % 5 == 0 else 1)
STATIONS = ['STOCKHOLM', 'MOTALA', 'HÖRBY', 'ÖSTERLEN', 'KULTURARVET', 'SOMMAR 90']
for i, s_ in enumerate(STATIONS):
    x = 120 + i * (w - 240) / (len(STATIONS) - 1); d.text((x, 62 if i % 2 == 0 else 96), s_, font=inter(24, 700), fill=INK, anchor='mm')   # staggered, as on the old sets
d.line([(int(w * .64), 18), (int(w * .64), h - 18)], fill=RED, width=7)   # the needle
save(im, 'craft_dial_1.jpg')
w, h = 768, 512; im = Image.new('RGB', (w, h), (196, 168, 112)); d = ImageDraw.Draw(im)
for x in range(0, w, 6): d.line([(x, 0), (x, h)], fill=(176, 146, 92), width=2)
for y in range(0, h, 6): d.line([(0, y), (w, y)], fill=(210, 184, 130), width=1)
for x in range(60, w, 120): d.rectangle([x, 0, x + 22, h], fill=(122, 86, 48))   # the dark vertical bars of the cloth
d.rounded_rectangle([w // 2 - 150, h - 112, w // 2 + 150, h - 30], radius=18, fill=(170, 130, 60), outline=(110, 78, 30), width=6)
d.text((w // 2, h - 71), T1['team'], font=fit(d, T1['team'], playi, 44, 270), fill=(52, 34, 18), anchor='mm')
d.text((w // 2, 92), T1['n'], font=play(120), fill=(96, 64, 30), anchor='mm')
save(im, 'craft_grille_1.jpg')

# ---- KULTURSIDAN: a broadsheet page (masthead, headlines, columns of text lines, a halftone photo) with red-pen marks
T2 = TEAMS[2]
def page(name, seed, head, sub):
    r = random.Random(seed); w, h = 1024, 1024; im = Image.new('RGB', (w, h), (239, 232, 216)); d = ImageDraw.Draw(im)
    d.text((w // 2, 92), T2['team'], font=fit(d, T2['team'], play, 150, w - 80), fill=INK, anchor='mm')
    d.line([(36, 168), (w - 36, 168)], fill=INK, width=5); d.line([(36, 178), (w - 36, 178)], fill=INK, width=2)
    d.text((40, 198), f"LÖRDAG · 2097 · NR {T2['n']}", font=inter(26, 600), fill=INK, anchor='lm')
    d.text((w - 40, 198), T2['latin'].upper(), font=playi(28), fill=INK, anchor='rm')
    d.text((40, 268), head, font=fit(d, head, dms, 92, w - 80), fill=INK, anchor='lm')
    d.text((40, 342), sub, font=fit(d, sub, playi, 46, w - 80), fill=(60, 56, 50), anchor='lm')
    cols = 4; cw = (w - 80 - (cols - 1) * 24) / cols
    for c in range(cols):
        x0 = 40 + c * (cw + 24); y = 400
        if c == 1:   # a halftone photo block
            for yy in range(400, 640, 8):
                for xx in range(int(x0), int(x0 + cw), 8):
                    v = 0.5 + 0.5 * math.sin(xx * 0.03 + yy * 0.02) * math.cos(yy * 0.025); rr = 1 + 3.2 * v
                    d.ellipse([xx + 4 - rr, yy + 4 - rr, xx + 4 + rr, yy + 4 + rr], fill=(70, 66, 60))
            y = 660
        while y < h - 40:
            ln = cw * r.uniform(0.55, 1.0) if r.random() < 0.15 else cw
            d.line([(x0, y), (x0 + ln, y)], fill=(120, 114, 104), width=5); y += 15
            if r.random() < 0.06: y += 18
    # the critic's red pen: a circle, two crosses and a verdict in the margin
    d.ellipse([560, 230, 1000, 320], outline=RED, width=7)
    for cx, cy in ((180, 720), (720, 860)): d.line([(cx - 40, cy - 40), (cx + 40, cy + 40)], fill=RED, width=9); d.line([(cx - 40, cy + 40), (cx + 40, cy - 40)], fill=RED, width=9)
    d.text((820, 700), 'NEJ.', font=playi(90), fill=RED, anchor='mm')
    return save(im, name)
page('craft_news_2a.jpg', 4, 'DENNA SOMMAR ÄR PROBLEMATISK', 'Recensenten har sett allt. Det räckte inte.')
page('craft_news_2b.jpg', 9, 'RECENSION: DU', 'En stjärna av fem. Den femte var nåd.')

# ---- NATURVINSBAREN: the wine label (own design, no producer) and a black-figure meander band for the belly
T3 = TEAMS[3]
w, h = 768, 512; im = Image.new('RGB', (w, h), (240, 228, 200)); d = ImageDraw.Draw(im)
d.rectangle([18, 18, w - 19, h - 19], outline=(120, 60, 30), width=6)
d.text((w // 2, 96), T3['team'], font=fit(d, T3['team'], play, 96, w - 90), fill=(90, 36, 18), anchor='mm')
d.text((w // 2, 186), f"AMFORA NR {T3['n']} · ORANGE 2097", font=inter(34, 700), fill=(120, 60, 30), anchor='mm')
for k in range(9):   # a hand-drawn grape bunch
    gx, gy = w // 2 + (k % 3 - 1) * 34 + (k // 3) * 0, 250 + (k // 3) * 34; d.ellipse([gx - 18 + (k // 3) * 10 - 10, gy - 18, gx + 18 + (k // 3) * 10 - 10, gy + 18], outline=(120, 60, 30), width=4)
d.text((w // 2, 398), T3['slogan'], font=fit(d, T3['slogan'], playi, 54, w - 90), fill=(90, 36, 18), anchor='mm')
d.text((w // 2, 452), T3['latin'].upper(), font=inter(26, 600), fill=(150, 90, 50), anchor='mm')
save(im, 'craft_label_3.jpg')
w, h = 1024, 128; im = Image.new('RGB', (w, h), (176, 84, 40)); d = ImageDraw.Draw(im)
d.rectangle([0, 0, w, 14], fill=(28, 18, 14)); d.rectangle([0, h - 14, w, h], fill=(28, 18, 14))
for x in range(0, w, 96):   # the meander (Greek key), black on terracotta
    pts = [(x + 8, 100), (x + 8, 28), (x + 80, 28), (x + 80, 84), (x + 32, 84), (x + 32, 52), (x + 56, 52)]
    d.line(pts, fill=(28, 18, 14), width=10, joint='curve')
save(im, 'craft_meander_3.jpg')

# ---- VERNISSAGEN: two abstract paintings (pastel Scandinavian blocks) and the wall label
T4 = TEAMS[4]
def painting(name, seed):
    r = random.Random(seed); w, h = 768, 512; im = Image.new('RGB', (w, h), (244, 240, 230)); d = ImageDraw.Draw(im)
    pal = [(232, 176, 170), (176, 196, 170), (226, 196, 120), (150, 178, 206), (40, 40, 44), (214, 120, 90)]
    for _ in range(6):
        x0, y0 = r.randrange(-80, w - 120), r.randrange(-60, h - 100); d.rectangle([x0, y0, x0 + r.randrange(160, 420), y0 + r.randrange(120, 300)], fill=r.choice(pal))
    d.ellipse([w * .55, h * .18, w * .55 + 190, h * .18 + 190], fill=r.choice(pal[:4]))
    d.line([(40, h * .82), (w - 60, h * .3)], fill=(30, 30, 34), width=10)
    return save(im, name)
painting('craft_paint_4a.jpg', 21); painting('craft_paint_4b.jpg', 33)
w, h = 512, 256; im = Image.new('RGB', (w, h), (250, 250, 248)); d = ImageDraw.Draw(im)
d.text((30, 52), 'OBETITLAD, 2097', font=inter(40, 700), fill=INK, anchor='lm')
d.text((30, 112), 'Blandteknik på förväntan', font=playi(34), fill=(70, 70, 70), anchor='lm')
d.text((30, 170), 'PRIS PÅ BEGÄRAN', font=inter(32, 600), fill=INK, anchor='lm')
d.ellipse([w - 70, 150, w - 30, 190], fill=RED)   # the red dot: sold, to someone else
save(im, 'craft_card_4.jpg')
w, h = 1024, 256; im = Image.new('RGB', (w, h), (246, 245, 241)); d = ImageDraw.Draw(im)
d.text((48, h // 2), T4['team'], font=inter(96, 300), fill=INK, anchor='lm'); d.text((w - 48, h // 2), T4['n'], font=inter(120, 200), fill=INK, anchor='rm')
save(im, 'craft_rear_4.jpg')

# ---- STIPENDIATERNA: the top sheet with its rejection stamps, and the folder spine
T5 = TEAMS[5]
w, h = 724, 1024; im = Image.new('RGB', (w, h), (250, 248, 240)); d = ImageDraw.Draw(im)
d.text((50, 80), 'ANSÖKAN OM ARBETSSTIPENDIUM', font=fit(d, 'ANSÖKAN OM ARBETSSTIPENDIUM', inter, 44, w - 100, 20), fill=INK, anchor='lm')
d.text((50, 130), f"Sökande nr {T5['n']} · omgång {T5['n']} av {T5['n']}", font=playi(30), fill=(80, 80, 80), anchor='lm')
for y in range(190, h - 60, 30): d.line([(50, y), (w - 50 - (rnd.randrange(0, 200) if rnd.random() < 0.2 else 0), y)], fill=(150, 150, 160), width=4)
stamp = Image.new('RGBA', (560, 200), (0, 0, 0, 0)); sd = ImageDraw.Draw(stamp)
sd.rectangle([8, 8, 551, 191], outline=(200, 30, 40, 235), width=12); sd.text((280, 102), 'AVSLAG', font=inter(130, 900), fill=(200, 30, 40, 235), anchor='mm')
for ang, (x, y) in ((-14, (70, 260)), (9, (110, 620))):
    s2 = stamp.rotate(ang, expand=True, resample=Image.BICUBIC); im.paste(s2, (x, y), s2)
d.text((w // 2, h - 40), T5['latin'].upper(), font=playi(30), fill=(80, 80, 80), anchor='mm')
save(im, 'craft_avslag_5.jpg')
w, h = 1024, 160; im = Image.new('RGB', (w, h), hx(T5['b'])); d = ImageDraw.Draw(im)
d.rectangle([24, 24, w - 24, h - 24], fill=(236, 232, 218)); d.text((w // 2, h // 2), f"{T5['team']} · ANSÖKNINGAR 1 TILL {T5['n']}", font=fit(d, f"{T5['team']} · ANSÖKNINGAR 1 TILL {T5['n']}", inter, 64, w - 90), fill=INK, anchor='mm')
save(im, 'craft_folder_5.jpg')

# ---- a stern plate per team (number and name) where the design has a flat stern
for i, T in enumerate(TEAMS):
    w, h = 1024, 256; a, b = hx(T['a']), hx(T['b']); im = Image.new('RGB', (w, h), b); d = ImageDraw.Draw(im)
    lum = 0.3 * b[0] + 0.59 * b[1] + 0.11 * b[2]; fg = INK if lum > 140 else (246, 240, 226)
    d.rectangle([0, 0, w - 1, h - 1], outline=a, width=14)
    d.text((70, h // 2 + 4), T['n'], font=play(170), fill=a if a != b else fg, anchor='lm')
    d.text((330, h // 2 - 26), T['team'], font=fit(d, T['team'], play, 84, w - 380), fill=fg, anchor='lm')
    d.text((332, h // 2 + 56), T['latin'].upper(), font=playi(40), fill=fg, anchor='lm')
    save(im, f'craft_stern_{i}.jpg')
print('craft textures ->', OUT, len([f for f in os.listdir(OUT) if f.startswith('craft_')]))
