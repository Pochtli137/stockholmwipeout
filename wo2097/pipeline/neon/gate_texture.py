"""THE GATE AT VÄSTERBRON (Kim 2026-10-02: "lägg också en gate vid hoppet vid västerbron där det står 'Du har mycket att
leva för'"). Not an ad: no brand, no hazard stripes, no flicker. Warm white Gill Sans on a deep warm dark, a soft
steady glow, a thin warm rule. Two lines, so the letters stand ~2.4 m tall on the 6.5 m banner and read from the approach.
    python3 gate_texture.py   ->  tex/gate_vb.jpg (neon/build.py hangs it over the take-off)"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
H=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.join(H,'tex')
W_,H_=3072,1060; BG=(15,13,19); INK=(255,243,226); GLOW=(255,214,170)   # the banner's own aspect, ~19 x 6.5 m
def gill(sz): return ImageFont.truetype('/System/Library/Fonts/Supplemental/GillSans.ttc',sz,index=4)   # SemiBold
LINES=['DU HAR MYCKET','ATT LEVA FÖR']
im=Image.new('RGB',(W_,H_),BG); d=ImageDraw.Draw(im)
sz=470
while sz>120 and max(d.textlength(s,font=gill(sz)) for s in LINES)>W_-300: sz-=8
f=gill(sz); ys=[int(H_*0.31),int(H_*0.71)]
glow=Image.new('L',(W_,H_),0); gd=ImageDraw.Draw(glow)
for s,y in zip(LINES,ys): gd.text((W_//2,y),s,font=f,fill=255,anchor='mm')
glow=glow.filter(ImageFilter.GaussianBlur(26))
im=Image.composite(Image.new('RGB',(W_,H_),GLOW),im,glow.point(lambda v:int(v*0.32)))   # the soft halo, steady
d=ImageDraw.Draw(im)
for s,y in zip(LINES,ys): d.text((W_//2,y),s,font=f,fill=INK,anchor='mm',spacing=0)
for y in (40,H_-40): d.line([(150,y),(W_-150,y)],fill=(200,170,140),width=5)   # a thin warm rule, top and bottom
im.save(os.path.join(OUT,'gate_vb.jpg'),quality=92); print('gate_vb.jpg',sz,'px letters')
