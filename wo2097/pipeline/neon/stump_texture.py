"""THE STUMPS' CONCRETE: a tiling 4.8 x 4.8 m patch of board-formed concrete for the abutments that close the cut ends
of Västerbron (neon/build.py). Dark cool grey (the low sun warms it) with slow mottle, formwork joints every 2.4 x 1.2 m, tie holes, and vertical
rain streaks; no text, no colour. Deterministic (seeded).
    python3 stump_texture.py   ->  tex/stump_conc.jpg"""
import os, random
from PIL import Image, ImageDraw, ImageFilter
H=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(H,'tex'); random.seed(2097)
N=1024; px=N/4.8   # pixels per metre
im=Image.new('L',(N,N),128)
noise=Image.effect_noise((N//8,N//8),40).resize((N,N),Image.BICUBIC).filter(ImageFilter.GaussianBlur(6))
im=Image.blend(im,noise,0.55)
fine=Image.effect_noise((N,N),18); im=Image.blend(im,fine,0.18)
d=ImageDraw.Draw(im)
for k in range(1,4): y=int(k*1.2*px); d.line([(0,y),(N,y)],fill=88,width=3)          # horizontal board joints
for k in (1,): x=int(k*2.4*px); d.line([(x,0),(x,N)],fill=92,width=3)                # vertical panel joint
for yy in (0.6,1.8,3.0,4.2):                                                          # tie holes
    for xx in (0.6,1.8,3.0,4.2):
        x,y=int(xx*px),int(yy*px); d.ellipse([x-5,y-5,x+5,y+5],fill=70)
for _ in range(70):                                                                   # rain streaks
    x=random.randint(0,N); y0=random.randint(0,N); ln=random.randint(60,400); w=random.randint(2,7)
    d.line([(x,y0),(x+random.randint(-6,6),y0+ln)],fill=random.randint(96,116),width=w)
im=im.filter(ImageFilter.GaussianBlur(1.2))
rgb=Image.merge('RGB',[im.point(lambda v:int(v*0.40)),im.point(lambda v:int(v*0.45)),im.point(lambda v:int(v*0.53))])   # dark and cool: the low sun warms everything
rgb.save(os.path.join(OUT,'stump_conc.jpg'),quality=90); print('stump_conc.jpg')
