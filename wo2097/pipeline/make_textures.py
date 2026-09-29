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
SUP='/System/Library/Fonts/Supplemental/'
def sysf(name,sz,index=0):
    try: return ImageFont.truetype(SUP+name,sz,index=index)
    except Exception: return orb(sz)
FONTS={ 'futura':lambda z:sysf('Futura.ttc',z,4), 'black':lambda z:sysf('Arial Black.ttf',z), 'din':lambda z:sysf('DIN Condensed Bold.ttf',z),
        'impact':lambda z:sysf('Impact.ttf',z), 'serif':lambda z:sysf('Georgia Bold.ttf',z), 'gill':lambda z:sysf('GillSans.ttc',z,1),
        'orb':lambda z:orb(z), 'raj':lambda z:raj(z) }
# SWEDEN, 2097. Parodies of well-known Swedish brands and institutions: altered names, our own typography and colours
# that only evoke the originals, never their logos. Satire of companies and institutions only, no real people.
BRANDS=[
  dict(n='IKÖA',       t='MONTERA DITT EGET MEDBORGARSKAP',   k='イケア',          bg=(0,74,173),  fg=(255,205,0), ac=(255,205,0), icon='grid',  f='futura'),
  dict(n='VOLVÖ',      t='SÄKERHET. FÖR AKTIEÄGARNA.',        k='ボルボ',          bg=(12,24,48),  fg=(214,222,235),ac=(214,222,235),icon='rings', f='serif'),
  dict(n='SAAPH',      t='WE ARM BOTH SIDES SINCE 1937',      k='サーブ',          bg=(200,16,32), fg=W, ac=K, icon='tri',   f='black'),
  dict(n='SPOTIFAI',   t='WE KNOW WHAT YOU WILL FEEL NEXT',   k='スポティファイ',  bg=K, fg=(30,215,96), ac=(30,215,96), icon='wave', f='black'),
  dict(n='H&N',        t='FAST FASHION. SLOW EXTINCTION.',    k='エイチアンドエヌ',bg=(226,0,26), fg=W, ac=W, icon='dot',   f='serif'),
  dict(n='ERIXON',     t='CONNECTING EVERY THOUGHT. RECORDING ALL OF THEM.', k='エリクソン', bg=(0,22,64), fg=W, ac=(0,168,224), icon='rings', f='gill'),
  dict(n='KLARNÅ',     t='KÖP NU. BETALA FÖR ALLTID.',        k='クラーナ',        bg=(255,179,199),fg=K, ac=K, icon='dot',   f='black'),
  dict(n='SYSTEMBÖLAGET',t='DIN KVOT: 0,3 L I MÅNADEN',       k='システムボラーゲット', bg=(0,92,62), fg=(255,210,0), ac=(255,210,0), icon='sun', f='din'),
  dict(n='SJ 2097',    t='FÖRSENAT SEDAN 1997',               k='エスイェー',      bg=(24,24,24),  fg=W, ac=(0,160,220), icon='bolt',  f='din'),
  dict(n='S/L',        t='PENDELTÅGET KOMMER. KANSKE.',       k='エスエル',        bg=(0,94,170),  fg=W, ac=(230,0,40), icon='rings', f='gill'),
  dict(n='IKÅ',        t='DINA MATDATA ÄR VÅRA',              k='イーカ',          bg=(226,0,26),  fg=W, ac=W, icon='dot',   f='futura'),
  dict(n='OATLÖ',      t='WOW NO COW. NO COW LEFT.',          k='オートリー',      bg=(238,236,225),fg=(0,40,110), ac=(0,40,110), icon='wave', f='black'),
  dict(n='ABSOLUTT',   t='ABSOLUT LYDNAD',                    k='アブソルート',    bg=(170,190,210),fg=(0,40,130), ac=(0,40,130), icon='dot', f='serif'),
  dict(n='SECURITAZ',  t='WE ARE ALWAYS WATCHING. YOU ARE WELCOME.', k='セキュリタス', bg=K, fg=W, ac=(230,0,40), icon='tri', f='black'),
  dict(n='ELECTROLUXX',t='WE CLEAN UP AFTER THE PROTESTS',    k='エレクトロラックス', bg=(0,30,80), fg=W, ac=W, icon='sun', f='gill'),
  dict(n='PRESSBYRÅ-N',t='KORV OCH ÖVERVAKNING · DYGNET RUNT', k='プレスビーロン', bg=(255,205,0), fg=(200,16,32), ac=(200,16,32), icon='bolt', f='impact'),
  dict(n='FÖRSÄKRINGSKASSÅN',t='DU ÄR FRISK. VI HAR BESTÄMT DET.', k='フォシェクリングスカッサン', bg=(0,62,106), fg=W, ac=(255,205,0), icon='crown', f='din'),
  dict(n='SKATTEVERK-X',t='VI VET VAD DU TÄNKER TJÄNA',       k='スカッテヴェルケット', bg=(0,50,90), fg=W, ac=(255,205,0), icon='crown', f='din'),
  dict(n='BANK-ID+',   t='LEGITIMERA DIG FÖR ATT ANDAS',      k='バンクアイディー', bg=(8,40,70),  fg=W, ac=(0,168,224), icon='grid', f='black') ]
# RACE-SPEED SLOGANS: at most two short lines (~16 characters), set big in heavy condensed type. A slogan must
# read for about a second from the racing line at 66-90 m/s, so it is seen from 60-90 m: that asks for letters about
# 1 m tall on the billboards and arches (legibility ~1:100), and the barrier text runs a full metre high.
# Too long to be big? Shorten it here. Never shrink it (make_textures fails if a line has to go under its minimum).
SLOGAN={ 'IKÖA':('MONTERA DITT','MEDBORGARSKAP'), 'VOLVÖ':('SÄKERHET.','FÖR ÄGARNA.'), 'SAAPH':('WE ARM','BOTH SIDES'),
  'SPOTIFAI':('WE KNOW WHAT','YOU FEEL NEXT'), 'H&N':('FAST FASHION.','SLOW EXTINCTION.'), 'ERIXON':('WE RECORD','EVERY THOUGHT'),
  'KLARNÅ':('KÖP NU.','BETALA FÖR ALLTID.'), 'SYSTEMBÖLAGET':('DIN KVOT:','0,3 L I MÅNADEN'), 'SJ 2097':('FÖRSENAT','SEDAN 1997'),
  'S/L':('TÅGET KOMMER.','KANSKE.'), 'IKÅ':('DINA MATDATA','ÄR VÅRA'), 'OATLÖ':('NO COW.','NO COW LEFT.'), 'ABSOLUTT':('ABSOLUT','LYDNAD'),
  'SECURITAZ':('WE ARE ALWAYS','WATCHING'), 'ELECTROLUXX':('WE CLEAN UP','AFTER PROTESTS'), 'PRESSBYRÅ-N':('KORV OCH','ÖVERVAKNING'),
  'FÖRSÄKRINGSKASSÅN':('DU ÄR FRISK.','VI BESTÄMDE DET.'), 'SKATTEVERK-X':('VI VET VAD DU','TÄNKER TJÄNA'), 'BANK-ID+':('LEGITIMERA DIG','FÖR ATT ANDAS') }
for B in BRANDS: B['s']=SLOGAN[B['n']]
def cond(z): return sysf('DIN Condensed Bold.ttf',z)
def big(d,lines,maxw,start,minsz,what):
    """the biggest condensed size that fits every line in maxw, or a hard stop: shorten the slogan, never shrink it"""
    sz=start
    while sz>minsz and max(d.textlength(l,font=cond(sz)) for l in lines)>maxw: sz-=2
    if max(d.textlength(l,font=cond(sz)) for l in lines)>maxw: raise SystemExit(f'SLOGAN TOO LONG for {what}: {lines} (min {minsz}px): shorten it in SLOGAN')
    return cond(sz)
# six teams on the same principle (index.html TEAMS and build.py TEAMS use the same colours, in the same order)
TEAMS=[
  dict(team='VOLVÖ SECURITY',  a='#d6deeb',b='#0c1830',n='01',glyph='rings', f='serif'),
  dict(team='SAAPH DEFENCE',   a='#c81020',b='#0c0d12',n='07',glyph='tri',   f='black'),
  dict(team='SPOTIFAI NEURAL', a='#1ed760',b='#07090d',n='12',glyph='wave',  f='black'),
  dict(team='IKÖA FLATPACK',   a='#ffcd00',b='#004aad',n='23',glyph='grid',  f='futura'),
  dict(team='KLARNÅ DEBT',     a='#ffb3c7',b='#07090d',n='31',glyph='dot',   f='black'),
  dict(team='ERIXON SIGNAL',   a='#f2f6ff',b='#00a8e0',n='44',glyph='rings', f='gill') ]
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
def barrier(acc,name,order):
    # 8192 x 128 px over 104 m of wall (build.py): 1.27 cm a pixel, the wall is 1.7 m high. Brand cell, then its slogan
    # as one line almost a metre tall in white on black, then chevrons; cells never cross the texture's wrap
    w,h=8192,128; im=Image.new('RGB',(w,h),(13,17,25)); d=ImageDraw.Draw(im); x=24; k=0
    while True:
        B=BRANDS[order[k%len(order)]]; nf=fit(d,B['n'],FONTS[B['f']],84,1100,minsz=60); nw=int(d.textlength(B['n'],font=nf))+60
        line=' '.join(B['s']); sf=big(d,[line],2600,100,84,'barrier'); sw=int(d.textlength(line,font=sf))+70
        if x+nw+sw+300>w-24: break
        d.rectangle([x,14,x+nw,h-14],fill=B['bg']); d.text((x+30,h//2+2),B['n'],font=nf,fill=B['fg'],anchor='lm'); x+=nw+10
        d.rectangle([x,14,x+sw,h-14],fill=K); d.text((x+35,h//2+6),line,font=sf,fill=W,anchor='lm'); x+=sw+10
        for j in range(3): ax=x+30+j*60; d.polygon([(ax,h*.3),(ax+36,h*.5),(ax,h*.7)],fill=acc)
        x+=220; k+=1
    hazard(d,x,14,w-24-x,h-28,s=14)
    d.rectangle([0,0,w,8],fill=acc); d.rectangle([0,h-8,w,h],fill=acc)
    save(im,name); return k
nL=barrier(M,'barrier_L.jpg',list(range(0,len(BRANDS),2))+list(range(1,len(BRANDS),2)))
nR=barrier(C,'barrier_R.jpg',list(range(1,len(BRANDS),2))+list(range(0,len(BRANDS),2)))
print('barrier brands per 104 m:',nL,nR)


# ---- speed pad (three chevrons) and weapon pad (a three-blade glyph), black = transparent under additive blending
w,h=256,512; im=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(im); d.rectangle([8,8,w-8,h-8],outline=(40,220,120),width=10)
for k in range(3):
    y=h*.78-k*h*.24; col=(int(53+k*60),255,int(139-k*30))
    d.polygon([(w*.12,y),(w*.5,y-h*.14),(w*.88,y),(w*.88,y+34),(w*.5,y-h*.14+34),(w*.12,y+34)],fill=col)
d.text((w/2,h*.93),'KLARNÅ BOOST · BETALA SENARE',font=fit(d,'KLARNÅ BOOST · BETALA SENARE',raj,30,w-30,minsz=14),fill=(255,179,199),anchor='mm'); save(im,'pad_speed.png')
w=h=512; im=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(im); d.rectangle([14,14,w-14,h-14],outline=(255,106,0),width=14); d.rectangle([40,40,w-40,h-40],outline=Y,width=6)
for k in range(3):
    a=k*2*math.pi/3; rot=lambda px,py:(w/2+px*math.cos(a)-py*math.sin(a), h/2+px*math.sin(a)+py*math.cos(a))
    d.polygon([rot(0,-20),rot(120,-150),rot(160,-40)],fill=R)
d.ellipse([w/2-34,h/2-34,w/2+34,h/2+34],fill=Y); d.text((w/2,h-62),'SAAPH · WE ARM BOTH SIDES',font=raj(34),fill=Y,anchor='mm'); save(im,'pad_weapon.png')

# ---- gantry sign, billboards, arch faces, hazard tile
w,h=2048,320; im=Image.new('RGB',(w,h),K); d=ImageDraw.Draw(im); hazard(d,0,h-18,w,18,s=16); hazard(d,0,0,w,14,s=14)
d.text((w//2,int(h*.30)),'STOCKHOLM GRAND PRIX',font=orb(96),fill=W,anchor='mm')
gl=['BANK-ID+ · LEGITIMERA DIG FÖR ATT TÄVLA']; d.text((w//2,int(h*.70)),gl[0],font=big(d,gl,w-360,120,96,'gantry'),fill=Y,anchor='mm')
icon(d,'crown',120,int(h*.45),70,C); icon(d,'rings',w-120,int(h*.45),70,C); save(im,'gantry.jpg')
for i,B in enumerate(BRANDS):
    # billboard: 1024 x 512 px on 14 x 7 m, seen from 60-90 m: 1.37 cm a pixel, so ~95 px caps = 1.3 m letters
    w,h=1024,512; im=Image.new('RGB',(w,h),B['bg']); d=ImageDraw.Draw(im)
    d.rectangle([0,int(h*.42),w,h],fill=K if B['bg']!=K else (28,30,36)); d.rectangle([0,int(h*.42)-8,w,int(h*.42)],fill=B['ac'])
    icon(d,B['icon'],int(w*.9),int(h*.21),int(h*.14),B['fg'])
    d.text((36,int(h*.21)),B['n'],font=fit(d,B['n'],FONTS[B['f']],150,w*.78,minsz=60),fill=B['fg'],anchor='lm')
    sf=big(d,B['s'],w-72,140,112,'billboard '+B['n']); sy=[int(h*.585),int(h*.84)]
    for ln,y in zip(B['s'],sy): d.text((36,y),ln,font=sf,fill=W,anchor='lm')
    save(im,f'bill_{i}.jpg')
    # arch face: 2048 x 256 px on 24 x 2.6 m, overhead, seen from ~100 m: brand left, slogan right in two ~1 m lines
    w,h=2048,256; im=Image.new('RGB',(w,h),B['bg']); d=ImageDraw.Draw(im); hazard(d,0,0,90,h,B['ac'],B['bg'],18); hazard(d,w-90,0,90,h,B['ac'],B['bg'],18)
    d.text((120,h//2+4),B['n'],font=fit(d,B['n'],FONTS[B['f']],190,800,minsz=80),fill=B['fg'],anchor='lm')
    d.rectangle([960,0,w-90,h],fill=K); d.rectangle([960,0,972,h],fill=B['ac'])
    af=big(d,B['s'],w-90-1010,124,104,'arch '+B['n'])
    for ln,y in zip(B['s'],(int(h*.30),int(h*.76))): d.text((1000,y),ln,font=af,fill=W,anchor='lm')
    save(im,f'arch_{i}.jpg')
im=Image.new('RGB',(256,256),K); hazard(ImageDraw.Draw(im),0,0,256,256,s=32); save(im,'hazard.jpg')

# ---- team liveries: the wing top (number, glyph, name) and the hull decal band
for i,T in enumerate(TEAMS):
    a,b=hx(T['a']),hx(T['b']); w,h=512,256; im=Image.new('RGB',(w,h),b); d=ImageDraw.Draw(im)
    d.polygon([(0,0),(w*.42,0),(w*.3,h),(0,h)],fill=a); hazard(d,int(w*.86),0,int(w*.14),h,s=16)
    fg=K if T['a'] in ('#f2f6ff','#d6deeb','#ffcd00','#ffb3c7','#1ed760') else W
    d.text((int(w*.36),int(h*.5)),T['n'],font=orb(140),fill=fg,anchor='lm'); icon(d,T['glyph'],int(w*.16),int(h*.5),int(h*.3),b if T['a']=='#f2f6ff' else K)
    d.text((int(w*.36),int(h*.9)),T['team'],font=fit(d,T['team'],FONTS[T['f']],30,w*.48,minsz=14),fill=W if T['b'] not in ('#f2f6ff','#ffcd00') else K,anchor='ls'); save(im,f'livery_{i}.jpg')
    w,h=1024,128; im=Image.new('RGB',(w,h),a); d=ImageDraw.Draw(im); d.rectangle([0,int(h*.62),w,h],fill=b)
    for k in range(4): d.polygon([(w*.55+k*70,0),(w*.55+k*70+40,0),(w*.55+k*70+10,h*.62),(w*.55+k*70-30,h*.62)],fill=b)
    d.text((24,int(h*.33)),T['team']+'  '+T['n'],font=fit(d,T['team']+'  '+T['n'],FONTS[T['f']],40,w*.52,minsz=16),fill=K if T['a'] in ('#f2f6ff','#d6deeb','#ffcd00','#ffb3c7','#1ed760') else W,anchor='lm'); save(im,f'hull_{i}.jpg')
print('textures ->',OUT, len(os.listdir(OUT)))
