"""USED UNIVERSE textures for the Blender track set and craft, drawn with PIL + numpy. Original designs only:
invented league, invented brands and teams, no real logos. Fonts: Orbitron + Rajdhani (OFL, in fonts/),
runes (Younger Futhark) in Noto Sans Runic from ../fonts. Output: tex/*.png|jpg, read by build.py.
The world is worn Stockholm (old Slussen concrete, tunnelbana tile, rust, sodium and fluorescent light). Every ad, corporate
and party alike, is a matte PRINTED PAPER poster in the neon version's layout and size, lit by the world's lamps and a worn
floodlight on each board: crisp print, the wear on the paper edges and the board, never across the letters."""
import os, math, random
sys_path_fix=__import__('sys').path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from faux_logos import logo as faux_logo   # the eight parties' faux logos (faux_logos.py)
import numpy as np
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
# the secondary script is Younger Futhark (runes.py), set in the same OFL font the game embeds, so bakes match the web
from runes import runes
RUNE=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','fonts','NotoSansRunic-Regular.ttf')
def rn(sz): return ImageFont.truetype(RUNE,sz)
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
  dict(n='IKÖA',       t='MONTERA DITT EGET MEDBORGARSKAP',   bg=(0,74,173),  fg=(255,205,0), ac=(255,205,0), icon='grid',  f='futura'),
  dict(n='VOLVÖ',      t='SÄKERHET. FÖR AKTIEÄGARNA.',        bg=(12,24,48),  fg=(214,222,235),ac=(214,222,235),icon='rings', f='serif'),
  dict(n='SAAPH',      t='WE ARM BOTH SIDES SINCE 1937',      bg=(200,16,32), fg=W, ac=K, icon='tri',   f='black'),
  dict(n='SPOTIFAI',   t='WE KNOW WHAT YOU WILL FEEL NEXT',   bg=K, fg=(30,215,96), ac=(30,215,96), icon='wave', f='black'),
  dict(n='H&N',        t='FAST FASHION. SLOW EXTINCTION.',    bg=(226,0,26), fg=W, ac=W, icon='dot',   f='serif'),
  dict(n='ERIXON',     t='CONNECTING EVERY THOUGHT. RECORDING ALL OF THEM.', bg=(0,22,64), fg=W, ac=(0,168,224), icon='rings', f='gill'),
  dict(n='KLARNÅ',     t='KÖP NU. BETALA FÖR ALLTID.',        bg=(255,179,199),fg=K, ac=K, icon='dot',   f='black'),
  dict(n='SYSTEMBÖLAGET',t='DIN KVOT: 0,3 L I MÅNADEN',       bg=(0,92,62), fg=(255,210,0), ac=(255,210,0), icon='sun', f='din'),
  dict(n='SJ 2097',    t='FÖRSENAT SEDAN 1997',               bg=(24,24,24),  fg=W, ac=(0,160,220), icon='bolt',  f='din'),
  dict(n='S/L',        t='PENDELTÅGET KOMMER. KANSKE.',       bg=(0,94,170),  fg=W, ac=(230,0,40), icon='rings', f='gill'),
  dict(n='IKÅ',        t='DINA MATDATA ÄR VÅRA',              bg=(226,0,26),  fg=W, ac=W, icon='dot',   f='futura'),
  dict(n='OATLÖ',      t='WOW NO COW. NO COW LEFT.',          bg=(238,236,225),fg=(0,40,110), ac=(0,40,110), icon='wave', f='black'),
  dict(n='ABSOLUTT',   t='ABSOLUT LYDNAD',                    bg=(170,190,210),fg=(0,40,130), ac=(0,40,130), icon='dot', f='serif'),
  dict(n='SECURITAZ',  t='WE ARE ALWAYS WATCHING. YOU ARE WELCOME.', bg=K, fg=W, ac=(230,0,40), icon='tri', f='black'),
  dict(n='ELECTROLUXX',t='WE CLEAN UP AFTER THE PROTESTS',    bg=(0,30,80), fg=W, ac=W, icon='sun', f='gill'),
  dict(n='PRESSBYRÅ-N',t='KORV OCH ÖVERVAKNING · DYGNET RUNT', bg=(255,205,0), fg=(200,16,32), ac=(200,16,32), icon='bolt', f='impact'),
  dict(n='FÖRSÄKRINGSKASSÅN',t='DU ÄR FRISK. VI HAR BESTÄMT DET.', bg=(0,62,106), fg=W, ac=(255,205,0), icon='crown', f='din'),
  dict(n='SKATTEVERK-X',t='VI VET VAD DU TÄNKER TJÄNA',       bg=(0,50,90), fg=W, ac=(255,205,0), icon='crown', f='din'),
  dict(n='BANK-ID+',   t='UTAN OSS FINNS DU INTE.',      bg=(8,40,70),  fg=W, ac=(0,168,224), icon='grid', f='black') ]
for B in BRANDS: B['k']=runes(B['n'])   # the brand name in runes: the small tag on its billboard
# RACE-SPEED SLOGANS: at most two short lines (~16 characters), set big in heavy condensed type. A slogan must
# read for about a second from the racing line at 66-90 m/s, so it is seen from 60-90 m: that asks for letters about
# 1 m tall on the billboards and arches (legibility ~1:100), and the barrier text runs a full metre high.
# Too long to be big? Shorten it here. Never shrink it (make_textures fails if a line has to go under its minimum).
SLOGAN={ 'IKÖA':('MONTERA DITT','MEDBORGARSKAP'), 'VOLVÖ':('SÄKERHET.','FÖR ÄGARNA.'), 'SAAPH':('WE ARM','BOTH SIDES'),
  'SPOTIFAI':('WE KNOW WHAT','YOU FEEL NEXT'), 'H&N':('FAST FASHION.','SLOW EXTINCTION.'), 'ERIXON':('WE RECORD','EVERY THOUGHT'),
  'KLARNÅ':('KÖP NU.','BETALA FÖR ALLTID.'), 'SYSTEMBÖLAGET':('DIN KVOT:','0,3 L I MÅNADEN'), 'SJ 2097':('FÖRSENAT','SEDAN 1997'),
  'S/L':('TÅGET KOMMER.','KANSKE.'), 'IKÅ':('DINA MATDATA','ÄR VÅRA'), 'OATLÖ':('NO COW.','NO COW LEFT.'), 'ABSOLUTT':('ABSOLUT','LYDNAD'),
  'SECURITAZ':('WE ARE ALWAYS','WATCHING'), 'ELECTROLUXX':('WE CLEAN UP','AFTER PROTESTS'), 'PRESSBYRÅ-N':('KORV OCH','ÖVERVAKNING'),
  'FÖRSÄKRINGSKASSÅN':('DU ÄR FRISK.','VI BESTÄMDE DET.'), 'SKATTEVERK-X':('VI VET VAD DU','TÄNKER TJÄNA'), 'BANK-ID+':('UTAN OSS','FINNS DU INTE.') }
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


# ============================================================ USED UNIVERSE · helpers
RNG=np.random.default_rng(97)
def vnoise(h,w,cell,seed):   # smooth value noise, h x w, 0..1
    r=np.random.default_rng(seed); gh,gw=h//cell+2,w//cell+2; g=r.random((gh,gw)).astype(np.float32)
    y=np.linspace(0,gh-2,h,endpoint=False); x=np.linspace(0,gw-2,w,endpoint=False)
    y0=y.astype(int); x0=x.astype(int); fy=(y-y0)[:,None]; fx=(x-x0)[None,:]; fy=fy*fy*(3-2*fy); fx=fx*fx*(3-2*fx)
    a=g[y0][:,x0]; b=g[y0][:,x0+1]; c=g[y0+1][:,x0]; d=g[y0+1][:,x0+1]
    return (a*(1-fx)+b*fx)*(1-fy)+(c*(1-fx)+d*fx)*fy
def fbm(h,w,cell,seed,oct=5):
    s=np.zeros((h,w),np.float32); a=0.5; t=0
    for k in range(oct): c=max(1,cell>>k); s+=a*vnoise(h,w,c,seed+k*31); t+=a; a*=0.5
    return s/t
def to_im(a): return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
def grime(im,amt=0.45,seed=1,cell=64,rust=0.0,runs=0.0):
    """darken the pores, water stains, rust runs from the top edge: the look of a surface left outside since 1997"""
    a=np.asarray(im.convert('RGB')).astype(np.float32); h,w=a.shape[:2]
    g=fbm(h,w,cell,seed); big=fbm(h,w,cell*4,seed+9,3)
    a*=(1-amt)+amt*(0.55+0.7*g)[...,None]
    stain=np.clip((big-0.55)/0.25,0,1)[...,None]*amt; a=a*(1-stain)+a*np.array([0.62,0.53,0.42])*stain
    if runs>0:
        cols=RNG.random(w)<runs/60; ln=(RNG.random(w)*0.8+0.2)*h
        yy=np.arange(h)[:,None]; m=(cols[None,:]&(yy<ln[None,:])).astype(np.float32)*(1-yy/h)
        m=np.clip(m*0.9,0,1)[...,None]
        rc=np.array([92,48,22],np.float32); a=a*(1-m*rust)+rc*(m*rust)
    return to_im(a)
def fade(im,k=0.25,warm=True):
    a=np.asarray(im.convert('RGB')).astype(np.float32); l=(a@np.array([0.299,0.587,0.114]))[...,None]
    a=a*(1-k)+l*k
    if warm: a+=np.array([10,5,-6])
    return to_im(a)
def dark_edge(d,x,y,w,h,col=(34,31,28),t=10):   # a steel frame round a box, rivets
    d.rectangle([x,y,x+w,y+h],outline=col,width=t)
    for k in range(0,int(w),60): d.ellipse([x+k+4,y+2,x+k+8,y+6],fill=(70,64,58)); d.ellipse([x+k+4,y+h-6,x+k+8,y+h-2],fill=(70,64,58))
def neon_text(size,text,font,col,xy,anchor='lm',halo=18,core=(255,255,255)):
    """a neon-tube word: coloured glow, hot white-ish core. Returns (colour layer RGBA, emission layer RGB)"""
    w,h=size; tube=Image.new('L',(w,h),0); td=ImageDraw.Draw(tube); td.text(xy,text,font=font,fill=255,anchor=anchor)
    blur=tube.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(halo))   # the halo hugs the tube, it never floods the word
    c=np.array(col,np.float32); core=np.array(core,np.float32)
    B=np.asarray(blur).astype(np.float32)[...,None]/255; T=np.asarray(tube).astype(np.float32)[...,None]/255
    em=c*np.clip(B*0.85,0,1)*(1-T) + (c*0.35+core*0.65)*T          # a crisp hot tube, a thin coloured bloom round it
    return np.clip(em,0,255), np.clip(B*0.85+T,0,1)
def comp(base,em,mask,k=1.0):   # the unlit colour under a neon word: the glass tube tinted by its colour
    a=np.asarray(base.convert('RGB')).astype(np.float32); a=a*(1-mask*k)+em*mask*k; return to_im(a)
def lednoise(im,pitch=6):   # LED panel: a pixel grid over the emission
    a=np.asarray(im.convert('RGB')).astype(np.float32); h,w=a.shape[:2]
    yy,xx=np.mgrid[0:h,0:w]; g=((xx%pitch)<pitch-1)&((yy%pitch)<pitch-1); a*=np.where(g,1.0,0.25)[...,None]; return to_im(a)

# ============================================================ POLITICS, 2097 · the eight Riksdag parties
# Satire of power only, treated alike: one neon billboard pair and one election poster each, the same bite for all.
# Parody names close to the real ones (the brand trick), party colours, NO party logos or symbols, NO politicians,
# never a word about any group of people. Direktdemokraterna and parties outside the Riksdag are not included.
PARTIES=[
  dict(n='SOCIÅLDEMOKRATERNA', s=('ALLA SKA MED.','FRIVILLIGT ELLER EJ.'), bg=(200,16,46),  fg=W, ac=(255,255,255)),
  dict(n='MODERÅTERNA',        s=('SÄNKT SKATT.','HÖJD KONTROLL.'),        bg=(20,70,170),  fg=W, ac=(120,200,255)),
  dict(n='SVERIGEDEMOKRÄTERNA',s=('SVERIGE TILLBAKA.','TILL 1952.'),       bg=(250,210,0),  fg=(0,50,130), ac=(0,50,130)),
  dict(n='CENTERPÅRTIET',      s=('GRÖN TILLVÄXT.','BARA TILLVÄXT.'),      bg=(0,120,60),   fg=W, ac=(160,230,120)),
  dict(n='VÄNSTERPÅRTIET',     s=('MAKTEN ÅT FOLKET.','FOLKET ÅT PARTIET.'),bg=(160,0,20),  fg=W, ac=(255,120,120)),
  dict(n='KRISTDEMOKRÄTERNA',  s=('TRYGGA FAMILJER.','ÖVERVAKADE FAMILJER.'),bg=(10,30,110),fg=W, ac=(120,170,255)),
  dict(n='LIBERÅLERNA',        s=('FRIHET.','MED PRENUMERATION.'),         bg=(0,100,180),  fg=W, ac=(255,210,0)),
  dict(n='MILJÖPÅRTIET',       s=('KLIMATNEUTRALT.','ENLIGT OSS.'),        bg=(90,160,40),  fg=W, ac=(220,255,160)) ]
for P in PARTIES: P['k']=runes(P['n']); P['neon']=tuple(min(255,int(c*1.15+30)) for c in (P['bg'] if P['bg']!=(10,30,110) else (60,110,255)))

# ============================================================ the deck: old Slussen concrete and asphalt
# u across the 17 m track, v along it, one tile = 32 m: 1024 x 2048 px, 1.7 cm a pixel
w,h=1024,2048
agg=fbm(h,w,48,3); fine=RNG.random((h,w)).astype(np.float32)
base=92+44*agg+18*(fine-0.5)
a=np.stack([base*1.03,base*0.99,base*0.92],-1)
im=to_im(a); d=ImageDraw.Draw(im,'RGBA'); r=random.Random(11)
for _ in range(34):   # patches: newer black asphalt and older grey concrete, cut square
    x=r.randrange(w); y=r.randrange(h); pw=r.randint(80,420); ph=r.randint(60,500)
    d.rectangle([x,y,x+pw,y+ph],fill=(38,36,34,150) if r.random()<0.55 else (150,146,136,95))
    d.rectangle([x,y,x+pw,y+ph],outline=(20,19,18,120),width=2)
for _ in range(110):  # cracks
    x,y=r.randrange(w),r.randrange(h); pts=[(x,y)]
    for k in range(r.randint(5,12)): x+=r.randint(-40,40); y+=r.randint(-60,60); pts.append((x,y))
    d.line(pts,fill=(18,16,15,170),width=r.choice((1,2,2,3)))
for _ in range(28):   # skid marks along the racing line
    x=r.randint(220,800); y=r.randrange(h); L=r.randint(200,900); cx=x+r.randint(-60,60)
    for o in (-22,22): d.line([(x+o,y),(cx+o,y+L//2),(x+o+r.randint(-40,40),y+L)],fill=(10,9,8,r.randint(60,120)),width=r.randint(14,22))
for _ in range(60):   # oil and water stains
    x,y=r.randrange(w),r.randrange(h); rr=r.randint(20,120)
    st=Image.new('L',(rr*2,rr*2),0); ImageDraw.Draw(st).ellipse([0,0,rr*2,rr*2],fill=r.randint(40,90)); st=st.filter(ImageFilter.GaussianBlur(rr/3))
    im.paste((22,20,18),(x-rr,y-rr),st)
# faded paint: kerb lines, the dashed centre line, a worn chevron group and the league stencil
for xx in (int(w*.065),int(w*.935)-12):
    for y in range(0,h,4):
        if r.random()<0.78: d.rectangle([xx,y,xx+12,y+4],fill=(214,206,188,r.randint(90,170)))
for y in range(0,h,256):
    for yy in range(y+40,y+180,4):
        if r.random()<0.7: d.rectangle([w//2-7,yy,w//2+7,yy+4],fill=(214,206,188,r.randint(70,150)))
for k in range(3):
    y0=int(h*.18)+k*90; d.polygon([(w*.72-80,y0+60),(w*.72,y0),(w*.72+80,y0+60),(w*.72+80,y0+88),(w*.72,y0+28),(w*.72-80,y0+88)],fill=(200,160,40,70))
st=Image.new('RGBA',(1100,240),(0,0,0,0)); sd=ImageDraw.Draw(st); sd.text((550,90),'SAGL · 2097',font=orb(96),fill=(220,214,200,46),anchor='mm'); sd.text((550,190),runes('STOCKHOLM'),font=rn(64),fill=(220,214,200,40),anchor='mm')
st=st.rotate(90,expand=True); im.paste(st,(int(w*.28)-st.width//2,h//2-st.height//2),st)
for y in range(64,h,h//6):   # drain grates by both kerbs
    for x in (int(w*.035),int(w*.965)-60):
        d.rectangle([x,y,x+60,y+34],fill=(26,24,22,255))
        for k in range(1,6): d.rectangle([x+k*10,y+3,x+k*10+3,y+31],fill=(70,66,60,255))
        d.rectangle([x,y,x+60,y+34],outline=(52,48,44,255),width=2)
im=grime(im,0.35,5,96)
save(im,'track.jpg',88)
save(Image.new('RGB',(64,64),(0,0,0)),'track_e.jpg')   # the deck is unlit now: no glow in the paint

# ============================================================ concrete (slab underside, footings) and rusty steel with tags
w=h=1024
c=fbm(h,w,40,21); a=np.stack([118+60*c]*3,-1)*np.array([1.0,0.98,0.93]); im=to_im(a); d=ImageDraw.Draw(im,'RGBA')
for y in range(0,h,256): d.line([(0,y),(w,y)],fill=(60,56,52,160),width=4)   # formwork lines
for _ in range(400): x,y=r.randrange(w),r.randrange(h); d.ellipse([x,y,x+3,y+3],fill=(50,48,45,140))   # blowholes
im=grime(im,0.6,23,48,rust=0.7,runs=2.0); save(im,'concrete.jpg',88)
TAGS=['SLSN','KRÅK','NOLL7','RÅTT','GRUS','MÖRK','ZON9','TUBE','BETONG','SÖDER']   # invented words, no real crews
TAGC=[(232,225,208),(194,59,42),(43,111,208),(224,181,42),(29,29,29),(88,168,74)]
c=fbm(h,w,32,41); a=np.stack([62+40*c,50+30*c,40+22*c],-1); im=to_im(a); d=ImageDraw.Draw(im,'RGBA')
for _ in range(900): x,y=r.randrange(w),r.randrange(h); rr=r.randint(2,9); d.ellipse([x,y,x+rr,y+rr],fill=(120,58,24,r.randint(60,160)))   # rust bloom
for y in range(0,h,128): d.line([(0,y),(w,y)],fill=(30,26,22,200),width=3)
for k in range(9):
    t=TAGS[k%len(TAGS)]; col=TAGC[k%len(TAGC)]; f=sysf('Arial Black.ttf',r.randint(60,96))
    cw,ch=w//3,h//3; lay=Image.new('RGBA',(cw,ch),(0,0,0,0)); ld=ImageDraw.Draw(lay)
    ld.text((cw//2,ch//2),t,font=f,fill=(*col,235),anchor='mm',stroke_width=7,stroke_fill=(20,20,20,235) if k%2 else (240,236,226,235))
    for q in range(3): dx=r.randint(cw//4,3*cw//4); ld.line([(dx,ch//2+36),(dx,ch//2+36+r.randint(20,70))],fill=(*col,150),width=4)   # drips
    lay=lay.rotate(r.uniform(-14,14),resample=Image.BICUBIC); im.paste(lay,((k%3)*cw+r.randint(-30,30),(k//3)*ch+r.randint(-30,30)),lay)
im=grime(im,0.5,43,40,rust=0.9,runs=3.0); save(im,'pylon.jpg',88)
im=Image.new('RGB',(256,256),K); hazard(ImageDraw.Draw(im),0,0,256,256,a=(196,160,40),b=(28,26,24),s=32); save(grime(im,0.6,7,24,rust=0.6,runs=2.0),'hazard.jpg')
m=fbm(512,512,32,61); save(to_im(np.stack([70+50*m,66+44*m,60+38*m],-1)).filter(ImageFilter.SMOOTH),'steel.jpg')   # dirty galvanised steel

# ============================================================ barrier walls: tunnelbana tile, light boxes, election posters
# 8192 x 128 px over 104 m of wall (build.py), the wall is 1.7 m high: 1.27 cm a pixel. Three variants per side
# alternate every 104 m: two brand walls (every ad a LIT light box) and one poster wall with all eight parties.
def tiles(w,h,seed):
    a=np.zeros((h,w,3),np.float32); rr=np.random.default_rng(seed); tw,th=24,11   # 30 x 15 cm tiles
    ny,nx=h//th+1,w//tw+1; tint=rr.random((ny,nx)).astype(np.float32)
    yy,xx=np.mgrid[0:h,0:w]; ti=tint[yy//th,xx//tw]
    base=np.stack([186+18*ti,190+16*ti,168+14*ti],-1)*0.82          # pale green-cream SL tile, each its own
    grout=((xx%tw)<2)|((yy%th)<2); base[grout]=np.array([70,68,60])
    return to_im(base)
def paper(im,box,seed):
    """printed paper on the wall: the paper yellows a touch and its edges lift and dirty; the print stays crisp"""
    x0,y0,x1,y1=box; d=ImageDraw.Draw(im); rr=random.Random(seed)
    for _ in range(3): tx=rr.randint(x0,x1-44); d.rectangle([tx,y0-4,tx+44,y0+4],fill=(214,206,180))     # tape on the top edge
    d.rectangle([x0,y0,x1,y1],outline=(160,150,128),width=2)                                            # the paper's own edge
    for _ in range(int((x1-x0)/90)):                                                                    # dirt only along the bottom edge
        tx=rr.randint(x0,x1); d.line([(tx,y1-rr.randint(2,7)),(tx+rr.randint(10,40),y1-1)],fill=(92,84,70),width=2)
def paper_cell(im,x,y,w,h,B,slogan_font_max=100):
    """a brand poster on the tile: brand cell + slogan cell, exactly the neon version's barrier sizes, printed matte"""
    d=ImageDraw.Draw(im)
    nf=fit(d,B['n'],FONTS[B['f']],84,1100,minsz=60); nw=int(d.textlength(B['n'],font=nf))+60
    line=' '.join(B['s']); sf=big(d,[line],2600,slogan_font_max,84,'barrier'); sw=int(d.textlength(line,font=sf))+70
    W_=nw+sw+30
    d.rectangle([x,y,x+nw,y+h],fill=B['bg']); d.text((x+30,y+h//2+2),B['n'],font=nf,fill=B['fg'],anchor='lm')
    d.rectangle([x+nw+10,y,x+nw+10+sw,y+h],fill=(16,16,18)); d.text((x+nw+45,y+h//2+6),line,font=sf,fill=(246,242,230),anchor='lm')
    paper(im,(x,y,x+W_-20,y+h),x)
    return W_+40
def barrier_variant(name,order,seed):
    w,h=8192,128; im=grime(tiles(w,h,seed),0.42,seed+3,48,rust=0.5,runs=1.2); x=40; k=0
    while True:
        B=BRANDS[order[k%len(order)]]
        tmp=ImageDraw.Draw(im); nf=fit(tmp,B['n'],FONTS[B['f']],84,1100,minsz=60)
        need=int(tmp.textlength(B['n'],font=nf))+60+int(tmp.textlength(' '.join(B['s']),font=big(tmp,[' '.join(B['s'])],2600,100,84,'barrier')))+70+120
        if x+need>w-40: break
        x+=paper_cell(im,x,16,0,h-32,B)+r.randint(160,420); k+=1
    save(im,name+'.jpg'); save(im,name+'_e.jpg'); return k      # the *_e map: the whole wall, for the tubes' light on it
def poster_wall(name,seed):
    """all eight parties as pasted-up election posters on the tile. The PAPER is faded, rained on and torn at the
    right-hand end; the INK is crisp: name and slogan set after the wear, big, dark-on-light or light-on-dark."""
    w,h=8192,128; im=grime(tiles(w,h,seed),0.42,seed+3,48,rust=0.5,runs=1.2); pw=(w-120)//8; x=60; boxes=[]
    for P in PARTIES:
        px=x+8; ww=pw-16; paper=Image.new('RGB',(ww,h-20),P['bg']); paper=grime(fade(paper,0.3),0.5,seed+len(boxes)*7,24,rust=0.3,runs=1.0)
        im.paste(paper,(px,10)); boxes.append((px,ww,P)); x+=pw
    d=ImageDraw.Draw(im)
    for px,ww,P in boxes:
        nf=fit(d,P['n'],cond,40,ww-150,minsz=26); tw=int(d.textlength(P['n'],font=nf))
        d.text((px+20,28),P['n'],font=nf,fill=P['fg'],anchor='lm')
        d.rectangle([px+14,50,px+ww-14,53],fill=P['ac'])
        line=' '.join(P['s']); sf=big(d,[line],ww-150,74,46,'poster '+P['n']); lw=int(d.textlength(line,font=sf))
        lg=faux_logo(PARTIES.index(P),92,P['fg'],P['ac']); im.paste(lg,(px+ww-112,8),lg)   # the faux logo, right, never over the ink
        d.text((px+20,88),line,font=sf,fill=P['fg'],anchor='lm')
        d.text((px+ww-16,114),P['k'],font=rn(14),fill=P['fg'],anchor='rm')
        for tx in (px+4,px+ww-48): d.rectangle([tx,6,tx+44,14],fill=(214,206,180))          # tape at the corners, never over the ink
        free=px+max(tw,lw)+60
        if free<px+ww-270:                                                                  # torn only where there is no text or logo
            tx=r.randint(free,px+ww-260); d.polygon([(tx,h-10),(tx+r.randint(60,120),h-10),(tx+r.randint(20,90),r.randint(30,80))],fill=(186,176,150))
    save(im,name+'.jpg'); save(im,name+'_e.jpg')      # the tubes light the poster wall like the others
half=list(range(0,len(BRANDS),2)), list(range(1,len(BRANDS),2))
nA=barrier_variant('barrier_A',half[0]+half[1],101); nB=barrier_variant('barrier_B',half[1]+half[0],202)
poster_wall('barrier_P',303)
print('light boxes per 104 m:',nA,nB,'· poster wall: 8 parties')

# ---- speed pad (three chevrons) and weapon pad: corporate (KLARNÅ, SAAPH) so they stay lit, black = transparent
w,h=256,512; im=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(im); d.rectangle([8,8,w-8,h-8],outline=(255,120,170),width=8)
for k in range(3):
    y=h*.78-k*h*.24; col=(255,int(120+k*30),int(170+k*20))
    d.polygon([(w*.12,y),(w*.5,y-h*.14),(w*.88,y),(w*.88,y+34),(w*.5,y-h*.14+34),(w*.12,y+34)],fill=col)
d.text((w/2,h*.93),'KLARNÅ BOOST · BETALA SENARE',font=fit(d,'KLARNÅ BOOST · BETALA SENARE',raj,30,w-30,minsz=14),fill=(255,179,199),anchor='mm'); save(im,'pad_speed.png')
w=h=512; im=Image.new('RGB',(w,h),(0,0,0)); d=ImageDraw.Draw(im); d.rectangle([14,14,w-14,h-14],outline=(255,40,50),width=14); d.rectangle([40,40,w-40,h-40],outline=(255,210,60),width=6)
for k in range(3):
    a=k*2*math.pi/3; rot=lambda px,py:(w/2+px*math.cos(a)-py*math.sin(a), h/2+px*math.sin(a)+py*math.cos(a))
    d.polygon([rot(0,-20),rot(120,-150),rot(160,-40)],fill=R)
d.ellipse([w/2-34,h/2-34,w/2+34,h/2+34],fill=(255,210,60)); d.text((w/2,h-62),'SAAPH · WE ARM BOTH SIDES',font=raj(34),fill=(255,210,60),anchor='mm'); save(im,'pad_weapon.png')

# ============================================================ the gantry: BANK-ID+ LED panel over a dirty steel box
w,h=2048,320; im=Image.new('RGB',(w,h),(14,14,16)); d=ImageDraw.Draw(im)
d.text((w//2,int(h*.25)),'STOCKHOLM GRAND PRIX',font=orb(96),fill=(236,232,220),anchor='mm')
d.text((w//2,int(h*.455)),runes('STOCKHOLMS STORA PRIS'),font=rn(34),fill=(0,168,224),anchor='mm')
gl=['BANK-ID+ · IDENTIFIERAD. GODKÄND. ÄGD.']; d.text((w//2,int(h*.745)),gl[0],font=big(d,gl,w-360,120,96,'gantry'),fill=(80,200,255),anchor='mm')
icon(d,'grid',120,int(h*.45),70,(0,168,224)); icon(d,'grid',w-120,int(h*.45),70,(0,168,224))
dark_edge(d,4,4,w-8,h-8,t=12); save(im,'gantry.jpg'); save(im,'gantry_e.jpg')   # a printed banner; *_e = the same print, for its floodlight

# ============================================================ billboards and arches: every brand lit, three kinds of light
# LIGHTBOX: the whole face backlit through dirty acrylic. NEON: a weathered dark panel with tube letters. LED: a pixel panel.
def edge_wear(im,seed,m=14):
    """dirt and rust on the outer rim only: the frame's business, never the face's"""
    w,h=im.size; worn=grime(im,0.7,seed,24,rust=0.8,runs=2.0); mask=Image.new('L',(w,h),255); ImageDraw.Draw(mask).rectangle([m,m,w-m,h-m],fill=0)
    return Image.composite(worn,im,mask)
def bill_face(B,runes_tag,mark=None):
    """the neon version's billboard, 1024 x 512 on 14 x 7 m: brand band on top, the slogan big in white on black
    (min 112 px = ~1.5 m letters). Returns (dim base, clean emission)."""
    w,h=1024,512; im=Image.new('RGB',(w,h),B['bg']); d=ImageDraw.Draw(im)
    d.rectangle([0,int(h*.42),w,h],fill=K if B['bg']!=K else (28,30,36)); d.rectangle([0,int(h*.42)-8,w,int(h*.42)],fill=B['ac'] if B['ac']!=K else B['fg'])
    if B.get('icon'): icon(d,B['icon'],int(w*.9),int(h*.19),int(h*.12),B['fg'])
    d.text((w-30,int(h*.365)),runes_tag,font=rn(26),fill=B['fg'],anchor='rm')
    d.text((36,int(h*.21)),B['n'],font=fit(d,B['n'],FONTS.get(B.get('f'),cond),150,w*(.7 if mark is not None else .78),minsz=60),fill=B['fg'],anchor='lm')
    if mark is not None:   # the party's faux logo in the band, right, the same size for all eight
        lg=faux_logo(mark,158,B['fg'],B['ac']); im.paste(lg,(w-214,12),lg)   # clear of the rune tag under it
    sf=big(d,B['s'],w-72,140,112,'billboard '+B['n'])
    for ln,y in zip(B['s'],(int(h*.585),int(h*.84))): d.text((36,y),ln,font=sf,fill=(255,250,236),anchor='lm')
    im=edge_wear(im,hash(B['n'])%997,12); d=ImageDraw.Draw(im)                    # paper pasted on the board: dirty rim, lifted corner
    d.polygon([(w-1,0),(w-70,0),(w-1,56)],fill=(196,188,166)); d.line([(w-70,0),(w-1,56)],fill=(120,110,92),width=2)
    return im,im
for i,B in enumerate(BRANDS):
    col,em=bill_face(B,B['k']); save(col,f'bill_{i}.jpg'); save(em,f'bill_{i}_e.jpg')
    # arch face 2048 x 256 on 24 x 2.6 m, overhead: brand left, slogan right in two ~1 m lines (the neon version's sizes)
    w,h=2048,256; im=Image.new('RGB',(w,h),B['bg']); d=ImageDraw.Draw(im)
    d.text((120,h//2+4),B['n'],font=fit(d,B['n'],FONTS[B['f']],190,800,minsz=80),fill=B['fg'],anchor='lm')
    d.rectangle([960,0,w-90,h],fill=K); d.rectangle([960,0,972,h],fill=B['ac'] if B['ac']!=K else (255,255,255))
    af=big(d,B['s'],w-90-1010,124,104,'arch '+B['n'])
    for ln,y in zip(B['s'],(int(h*.30),int(h*.76))): d.text((1000,y),ln,font=af,fill=(255,250,236),anchor='lm')
    im=edge_wear(im,i+300,10); save(im,f'arch_{i}.jpg'); save(im,f'arch_{i}_e.jpg')   # a printed vinyl banner
for i,P in enumerate(PARTIES):   # the parties' boards: the same layout and size as every brand, party colours
    col,em=bill_face(dict(P,f=None,icon=None),P['k'],mark=i); save(col,f'pbill_{i}.jpg'); save(em,f'pbill_{i}_e.jpg')
# a sodium light pool (additive decal under the lamp posts) and the tube sprite
w=h=256; yy,xx=np.mgrid[0:h,0:w]; rr=np.sqrt((xx-w/2)**2+(yy-h/2)**2)/(w/2); a=np.clip(1-rr,0,1)**2.2
save(to_im(np.stack([a*255,a*150,a*40],-1)),'pool.png')


def chips(im,seed):
    """chipped paint: flecks of primer and bare metal along the edges and at random, and scratches"""
    r=random.Random(seed); d=ImageDraw.Draw(im); w,h=im.size
    for _ in range(int(w*h/1800)):
        x,y=r.randrange(w),r.randrange(h); edge=min(x,y,w-x,h-y)<w*0.06
        if edge or r.random()<0.25: rr=r.randint(1,5); d.ellipse([x,y,x+rr,y+rr*0.7],fill=(150,150,146) if r.random()<0.6 else (96,92,88))
    for _ in range(9): x,y=r.randrange(w),r.randrange(h); d.line([(x,y),(x+r.randint(-60,60),y+r.randint(-6,6))],fill=(170,168,160),width=1)
    return im

# ---- team liveries: the wing top (number, glyph, name) and the hull decal band, then a season of racing on them
for i,T in enumerate(TEAMS):
    a,b=hx(T['a']),hx(T['b']); w,h=512,256; im=Image.new('RGB',(w,h),b); d=ImageDraw.Draw(im)
    d.polygon([(0,0),(w*.42,0),(w*.3,h),(0,h)],fill=a); hazard(d,int(w*.86),0,int(w*.14),h,s=16)
    fg=K if T['a'] in ('#f2f6ff','#d6deeb','#ffcd00','#ffb3c7','#1ed760') else W
    d.text((int(w*.36),int(h*.5)),T['n'],font=orb(140),fill=fg,anchor='lm'); icon(d,T['glyph'],int(w*.16),int(h*.5),int(h*.3),b if T['a']=='#f2f6ff' else K)
    d.text((int(w*.36),int(h*.9)),T['team'],font=fit(d,T['team'],FONTS[T['f']],30,w*.48,minsz=14),fill=W if T['b'] not in ('#f2f6ff','#ffcd00') else K,anchor='ls')
    im=chips(im,i); save(grime(im,0.35,500+i,24,rust=0.25,runs=1.0),f'livery_{i}.jpg')
    w,h=1024,128; im=Image.new('RGB',(w,h),a); d=ImageDraw.Draw(im); d.rectangle([0,int(h*.62),w,h],fill=b)
    for k in range(4): d.polygon([(w*.55+k*70,0),(w*.55+k*70+40,0),(w*.55+k*70+10,h*.62),(w*.55+k*70-30,h*.62)],fill=b)
    d.text((24,int(h*.33)),T['team']+'  '+T['n'],font=fit(d,T['team']+'  '+T['n'],FONTS[T['f']],40,w*.52,minsz=16),fill=K if T['a'] in ('#f2f6ff','#d6deeb','#ffcd00','#ffb3c7','#1ed760') else W,anchor='lm')
    im=chips(im,i+10); save(grime(im,0.35,600+i,24,rust=0.25,runs=1.0),f'hull_{i}.jpg')
print('textures ->',OUT, len(os.listdir(OUT)))
