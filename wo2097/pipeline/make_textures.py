"""WipEout 2097 textures for the Blender track set and craft, drawn with PIL. Original designs only:
invented league, invented brands and teams, no real logos. Fonts: Orbitron + Rajdhani (OFL, in fonts/),
katakana from the system's Hiragino. Output: tex/*.png|jpg, read by build.py."""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(H,'tex'); os.makedirs(OUT,exist_ok=True)
FD=os.path.join(H,'fonts')
def orb(sz,w=900):
    f=ImageFont.truetype(os.path.join(FD,'Orbitron.ttf'),sz)
    try: f.set_variation_by_axes([w])
    except Exception: pass
    return f
def fit(d,s,fontf,start,maxw,minsz=24):   # the biggest size that keeps the words inside maxw
    sz=start
    while sz>minsz and d.textlength(s,font=fontf(sz))>maxw: sz-=4
    return fontf(sz)
def raj(sz): return ImageFont.truetype(os.path.join(FD,'Rajdhani-Bold.ttf'),sz)
JP='/System/Library/Fonts/ヒラギノ丸ゴ ProN W4.ttc'
def jp(sz): return ImageFont.truetype(JP,sz)
Y=(255,230,0); K=(7,9,13); C=(0,225,255); M=(255,46,154); W=(242,246,255); G=(53,255,139); R=(255,59,59)
def hx(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def hazard(d,x,y,w,h,a=Y,b=K,s=22):   # diagonal hazard stripes, clipped to their box
    w,h=int(w),int(h); tile=Image.new('RGB',(max(1,w),max(1,h)),b); td=ImageDraw.Draw(tile)
    for k in range(-h,w+h,s*2): td.polygon([(k,h),(k+s,h),(k+s+h,0),(k+h,0)],fill=a)
    d._image.paste(tile,(int(x),int(y)))
def clipbox(im,x,y,w,h,fn):
    sub=Image.new('RGB',(int(w),int(h))); fn(ImageDraw.Draw(sub),sub.size); im.paste(sub,(int(x),int(y)))
def text_c(d,xy,s,font,fill,anchor='mm'): d.text(xy,s,font=font,fill=fill,anchor=anchor)
def icon(d,kind,x,y,r,col):
    if kind=='bolt': d.polygon([(x-r*.2,y-r),(x+r*.45,y-r*.1),(x,y-r*.05),(x+r*.25,y+r),(x-r*.45,y+r*.05),(x,y)],fill=col)
    elif kind=='sun':
        d.ellipse([x-r*.45,y-r*.45,x+r*.45,y+r*.45],fill=col)
        for i in range(12):
            a=i*math.pi/6; d.line([(x+math.cos(a)*r*.6,y+math.sin(a)*r*.6),(x+math.cos(a)*r*.95,y+math.sin(a)*r*.95)],fill=col,width=max(2,int(r*.1)))
    elif kind=='crown': d.polygon([(x-r,y+r*.6),(x-r,y-r*.4),(x-r*.5,y+r*.05),(x,y-r*.8),(x+r*.5,y+r*.05),(x+r,y-r*.4),(x+r,y+r*.6)],fill=col)
    elif kind=='wave':
        for k in range(3):
            pts=[(x+(i/20*2-1)*r, y+(k-1)*r*.55+math.sin((i/20*2-1)*6)*r*.15) for i in range(21)]; d.line(pts,fill=col,width=max(2,int(r*.14)))
    elif kind=='rings':
        for k in (1,2,3): rr=r*k/3; d.ellipse([x-rr,y-rr,x+rr,y+rr],outline=col,width=max(2,int(r*.13)))
    elif kind=='grid':
        for i in range(-2,3):
            for j in range(-2,3):
                if (i+j)%2==0: d.rectangle([x+i*r*.36-r*.15,y+j*r*.36-r*.15,x+i*r*.36+r*.15,y+j*r*.36+r*.15],fill=col)
    elif kind=='tri':
        d.polygon([(x,y-r),(x+r*.9,y+r*.7),(x-r*.9,y+r*.7)],outline=col,width=max(2,int(r*.14))); d.ellipse([x-r*.22,y-r*.07,x+r*.22,y+r*.37],fill=col)
    else: d.ellipse([x-r*.7,y-r*.7,x+r*.7,y+r*.7],fill=col)
BRANDS=[ # invented, 2097
  dict(n='VOLTA',t='ENERGY FOR THE FAST',k='ボルタ',bg=Y,fg=K,ac=M,icon='bolt'),
  dict(n='SYNTHOLM',t='SYNTHETIC SUMMER',k='シンソルム',bg=M,fg=W,ac=K,icon='sun'),
  dict(n='KRONA AG',t='FLY THE CROWN',k='クローナ',bg=(10,44,255),fg=W,ac=Y,icon='crown'),
  dict(n='HYPERFJORD',t='COLD FUSION WATER',k='ハイパーフィヨルド',bg=C,fg=(4,18,28),ac=W,icon='wave'),
  dict(n='NORDSONIC',t='HEAR THE SPEED',k='ノルドソニック',bg=(255,106,0),fg=K,ac=W,icon='rings'),
  dict(n='ÖRE-X',t='MONEY MOVES AT 600',k='オーレ',bg=K,fg=G,ac=G,icon='grid'),
  dict(n='MÄLARVÄRME',t='2097 °C · HEAT THE CITY',k='マラーヴェルメ',bg=R,fg=W,ac=K,icon='tri'),
  dict(n='PSY-NUDEL',t='EAT AT MACH 2',k='ヌードル',bg=W,fg=K,ac=R,icon='dot') ]
TEAMS=[
  dict(team='KRONA AG',a='#f2f6ff',b='#0a2cff',n='01',glyph='crown'),
  dict(team='VALKYR SYSTEMS',a='#e01020',b='#0c0d12',n='07',glyph='tri'),
  dict(team='AURORA-X',a='#00c8c8',b='#ffe600',n='12',glyph='wave'),
  dict(team='MÄLAR FANG',a='#ff6a00',b='#2a2e36',n='23',glyph='bolt'),
  dict(team='NORRSKEN DYNAMICS',a='#6a2cff',b='#9dff3a',n='31',glyph='rings'),
  dict(team='ICEBREAKER',a='#f2f6ff',b='#ff2e9a',n='44',glyph='grid') ]
def save(im,name,q=90):
    p=os.path.join(OUT,name); (im.convert('RGB').save(p,quality=q) if name.endswith('.jpg') else im.save(p)); return p

# ---- track surface (u across the track, v along it, one tile = 32 m) and its glow map
w,h=512,1024; im=Image.new('RGB',(w,h),(11,14,21)); d=ImageDraw.Draw(im); rnd=random.Random(3)
for i in range(8): d.rectangle([0,i*h//8,w,(i+1)*h//8],fill=(16,19,28) if i%2 else (12,15,23))
for i in range(9): d.line([(0,i*h//8),(w,i*h//8)],fill=(46,54,70),width=2)
for x in (w//3,2*w//3): d.line([(x,0),(x,h)],fill=(40,48,62),width=2)
for _ in range(900): x,y=rnd.randrange(w),rnd.randrange(h); d.point((x,y),fill=(22+rnd.randrange(12),)*3)
hazard(d,0,0,int(w*.055),h,s=18); hazard(d,int(w*.945),0,int(w*.055),h,s=18)
d.rectangle([int(w*.065),0,int(w*.065)+6,h],fill=(233,238,248)); d.rectangle([int(w*.935)-6,0,int(w*.935),h],fill=(233,238,248))
for y in range(0,h,128): d.rectangle([w//2-4,y+20,w//2+4,y+90],fill=(233,238,248))
st=Image.new('RGBA',(700,160),(0,0,0,0)); sd=ImageDraw.Draw(st); sd.text((350,55),'SAGL · 2097',font=orb(52),fill=(255,255,255,26),anchor='mm'); sd.text((350,120),'ストックホルム',font=jp(34),fill=(255,255,255,26),anchor='mm')
st=st.rotate(90,expand=True); im.paste(st,(int(w*.28)-st.width//2,h//2-st.height//2),st)
for k in range(3):
    y0=int(h*.18)+k*46; d.polygon([(w*.72-40,y0+30),(w*.72,y0),(w*.72+40,y0+30),(w*.72+40,y0+44),(w*.72,y0+14),(w*.72-40,y0+44)],fill=(0,70,86))
save(im,'track.jpg')
em=Image.new('RGB',(w,h),(0,0,0)); e=ImageDraw.Draw(em)
e.rectangle([int(w*.065),0,int(w*.065)+6,h],fill=(150,160,180)); e.rectangle([int(w*.935)-6,0,int(w*.935),h],fill=(150,160,180))
for y in range(0,h,128): e.rectangle([w//2-4,y+20,w//2+4,y+90],fill=(150,160,180))
for k in range(3):
    y0=int(h*.18)+k*46; e.polygon([(w*.72-40,y0+30),(w*.72,y0),(w*.72+40,y0+30),(w*.72+40,y0+44),(w*.72,y0+14),(w*.72-40,y0+44)],fill=(0,120,150))
save(em,'track_e.jpg')

# ---- barrier panels, one per side: colour blocks, brand words, arrows, hazard slabs
def barrier(acc,name):
    w,h=2048,128; im=Image.new('RGB',(w,h),(13,17,25)); d=ImageDraw.Draw(im); x=0; i=0
    while x<w:
        B=BRANDS[i%len(BRANDS)]; bw=300+((i*97)%120)
        if i%3==2: hazard(d,x,18,bw,h-36,s=14)
        else:
            d.rectangle([x,18,x+bw,h-18],fill=B['bg'] if i%2 else (20,26,38))
            if i%2: d.text((x+18,h//2+2),B['n'],font=fit(d,B['n'],orb,46,bw-30),fill=B['fg'],anchor='lm')
            else:
                for k in range(3): ax=x+30+k*60; d.polygon([(ax,h*.3),(ax+36,h*.5),(ax,h*.7)],fill=acc)
        x+=bw+14; i+=1
    d.rectangle([0,0,w,8],fill=acc); d.rectangle([0,h-8,w,h],fill=acc)
    save(im,name)
barrier(M,'barrier_L.jpg'); barrier(C,'barrier_R.jpg')

# ---- speed pad (three chevrons) and weapon pad (a three-blade glyph), black = transparent under additive blending
w,h=256,512; im=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(im); d.rectangle([8,8,w-8,h-8],outline=(40,220,120),width=10)
for k in range(3):
    y=h*.78-k*h*.24; col=(int(53+k*60),255,int(139-k*30))
    d.polygon([(w*.12,y),(w*.5,y-h*.14),(w*.88,y),(w*.88,y+34),(w*.5,y-h*.14+34),(w*.12,y+34)],fill=col)
save(im,'pad_speed.png')
w=h=512; im=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(im); d.rectangle([14,14,w-14,h-14],outline=(255,106,0),width=14); d.rectangle([40,40,w-40,h-40],outline=Y,width=6)
for k in range(3):
    a=k*2*math.pi/3; rot=lambda px,py:(w/2+px*math.cos(a)-py*math.sin(a), h/2+px*math.sin(a)+py*math.cos(a))
    d.polygon([rot(0,-20),rot(120,-150),rot(160,-40)],fill=R)
d.ellipse([w/2-34,h/2-34,w/2+34,h/2+34],fill=Y); save(im,'pad_weapon.png')

# ---- gantry sign, billboards, arch faces, hazard tile
w,h=2048,320; im=Image.new('RGB',(w,h),K); d=ImageDraw.Draw(im); hazard(d,0,h-46,w,46,s=26); hazard(d,0,0,w,22,s=16)
d.text((w//2,int(h*.44)),'STOCKHOLM GRAND PRIX',font=orb(112),fill=W,anchor='mm')
d.text((w//2,int(h*.75)),'ストックホルム グランプリ',font=jp(40),fill=M,anchor='rm'); d.text((w//2+30,int(h*.75)),'SAGL ANTI-GRAVITY LEAGUE · 2097',font=raj(44),fill=M,anchor='lm')
icon(d,'crown',120,int(h*.45),70,C); icon(d,'rings',w-120,int(h*.45),70,C); save(im,'gantry.jpg')
for i,B in enumerate(BRANDS):
    w,h=1024,512; im=Image.new('RGB',(w,h),B['bg']); d=ImageDraw.Draw(im)
    d.rectangle([0,int(h*.78),w,h],fill=B['ac']); d.rectangle([int(w*.66),0,int(w*.66)+10,int(h*.78)],fill=B['ac'])
    icon(d,B['icon'],int(w*.83),int(h*.39),int(h*.25),B['fg'])
    d.text((40,int(h*.46)),B['n'],font=fit(d,B['n'],orb,128,w*.66-70),fill=B['fg'],anchor='ls')
    d.text((44,int(h*.62)),B['t'],font=raj(46),fill=B['fg'],anchor='ls')
    d.text((44,int(h*.93)),B['k'],font=jp(48),fill=B['bg'],anchor='ls'); d.text((w-40,int(h*.94)),'2097',font=orb(50),fill=B['bg'],anchor='rs')
    save(im,f'bill_{i}.jpg')
    w,h=2048,256; im=Image.new('RGB',(w,h),B['bg']); d=ImageDraw.Draw(im); hazard(d,0,0,160,h,B['ac'],B['bg'],18); hazard(d,w-160,0,160,h,B['ac'],B['bg'],18)
    d.text((w//2,int(h*.44)),B['n'],font=fit(d,B['n'],orb,140,w-420),fill=B['fg'],anchor='mm'); d.text((w//2,int(h*.85)),B['k']+'  ·  '+B['t'],font=jp(34),fill=B['fg'],anchor='mm')
    save(im,f'arch_{i}.jpg')
im=Image.new('RGB',(256,256),K); hazard(ImageDraw.Draw(im),0,0,256,256,s=32); save(im,'hazard.jpg')

# ---- team liveries: the wing top (number, glyph, name) and the hull decal band
for i,T in enumerate(TEAMS):
    a,b=hx(T['a']),hx(T['b']); w,h=512,256; im=Image.new('RGB',(w,h),b); d=ImageDraw.Draw(im)
    d.polygon([(0,0),(w*.42,0),(w*.3,h),(0,h)],fill=a); hazard(d,int(w*.86),0,int(w*.14),h,s=16)
    fg=K if T['a']=='#f2f6ff' else W
    d.text((int(w*.36),int(h*.5)),T['n'],font=orb(140),fill=fg,anchor='lm'); icon(d,T['glyph'],int(w*.16),int(h*.5),int(h*.3),b if T['a']=='#f2f6ff' else K)
    d.text((int(w*.36),int(h*.9)),T['team'],font=fit(d,T['team'],raj,28,w*.48),fill=W,anchor='ls'); save(im,f'livery_{i}.jpg')
    w,h=1024,128; im=Image.new('RGB',(w,h),a); d=ImageDraw.Draw(im); d.rectangle([0,int(h*.62),w,h],fill=b)
    for k in range(4): d.polygon([(w*.55+k*70,0),(w*.55+k*70+40,0),(w*.55+k*70+10,h*.62),(w*.55+k*70-30,h*.62)],fill=b)
    d.text((24,int(h*.33)),T['team']+'  '+T['n'],font=orb(40),fill=K if T['a']=='#f2f6ff' else W,anchor='lm'); save(im,f'hull_{i}.jpg')
print('textures ->',OUT, len(os.listdir(OUT)))
