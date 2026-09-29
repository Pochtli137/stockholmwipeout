"""FAUX PARTY LOGOS, 2097 (Kim, 2026-09-29: "lägg till faux loggor på alla partiannonser").
New marks that EVOKE each Riksdag party's visual identity with a dystopian twist. They never reproduce a real logo,
carry no text and no people other than faceless pictograms, and satirise power and rhetoric only. All eight are drawn
at the same size, in the same one-colour-plus-accent style, so no party gets a sharper or kinder mark than another.
logo(i, px, fg, ac) -> RGBA square, supersampled 4x for crisp edges at race-speed sizes."""
import math
from PIL import Image, ImageDraw
SS=4
def _pt(c,r,a): return (c[0]+math.cos(a)*r, c[1]+math.sin(a)*r)
def _ring(d,c,r,w,col): d.ellipse([c[0]-r,c[1]-r,c[0]+r,c[1]+r],outline=col,width=int(w))
def _disc(d,c,r,col): d.ellipse([c[0]-r,c[1]-r,c[0]+r,c[1]+r],fill=col)
def _line(d,pts,w,col): d.line(pts,fill=col,width=int(w),joint='curve')
def _drone(d,c,s,col):   # a tiny quadcopter: an X and four rotor discs
    for a in (math.pi/4,3*math.pi/4): _line(d,[_pt(c,s,a),_pt(c,s,a+math.pi)],s*0.35,col)
    for k in range(4): _disc(d,_pt(c,s,math.pi/4+k*math.pi/2),s*0.42,col)

def s_rose(d,S,fg,ac):      # S: a rose seen through a surveillance camera's iris, the stem is barbed wire
    c=(S*0.5,S*0.42); R=S*0.36
    _ring(d,c,R,S*0.05,fg)
    for k in range(7):      # aperture blades
        a=k*2*math.pi/7; _line(d,[_pt(c,R*0.97,a),_pt(c,R*0.42,a+1.05)],S*0.028,fg)
    for k,rr in enumerate((0.26,0.19,0.12)):   # the rose: three spiralling petal arcs
        r=R*rr/0.36*0.95; d.arc([c[0]-r,c[1]-r,c[0]+r,c[1]+r],start=k*110,end=k*110+290,fill=ac,width=int(S*0.045))
    _disc(d,c,S*0.025,ac)
    x=S*0.5; _line(d,[(x,c[1]+R),(x,S*0.96)],S*0.03,fg)          # stem: barbed wire
    for y in (S*0.85,S*0.93):
        _line(d,[(x-S*0.05,y-S*0.03),(x+S*0.05,y+S*0.03)],S*0.02,fg); _line(d,[(x-S*0.05,y+S*0.03),(x+S*0.05,y-S*0.03)],S*0.02,fg)
def m_lock(d,S,fg,ac):      # M: a padlock whose shackle is the letter-shape of an M
    bx0,by0,bx1,by1=S*0.2,S*0.46,S*0.8,S*0.92
    d.rounded_rectangle([bx0,by0,bx1,by1],radius=S*0.06,fill=fg)
    _line(d,[(S*0.3,by0),(S*0.3,S*0.12),(S*0.5,S*0.34),(S*0.7,S*0.12),(S*0.7,by0)],S*0.075,fg)
    kc=(S*0.5,S*0.64); _disc(d,kc,S*0.055,ac); d.polygon([(S*0.47,S*0.66),(S*0.53,S*0.66),(S*0.55,S*0.82),(S*0.45,S*0.82)],fill=ac)
def sd_globe(d,S,fg,ac):    # SD: a flower sealed in a snow globe, forever 1952 (nostalgia rhetoric, never people)
    c=(S*0.5,S*0.42); R=S*0.34
    _ring(d,c,R,S*0.04,fg)
    d.polygon([(S*0.22,S*0.8),(S*0.78,S*0.8),(S*0.7,S*0.95),(S*0.3,S*0.95)],fill=fg)   # the base
    fc=(S*0.5,S*0.38)
    for k in range(6): _disc(d,_pt(fc,S*0.085,k*math.pi/3),S*0.06,ac)                 # a generic six-petal flower
    _disc(d,fc,S*0.045,fg); _line(d,[(fc[0],fc[1]+S*0.07),(fc[0],S*0.7)],S*0.025,fg)
    for (u,v) in ((0.3,0.3),(0.66,0.24),(0.72,0.5),(0.3,0.56),(0.58,0.62),(0.4,0.18)): _disc(d,(S*u,S*v),S*0.016,fg)   # snow
def c_clover(d,S,fg,ac):    # C: a four-leaf clover with a barcode across it and a smokestack for a stem
    c=(S*0.5,S*0.38)
    for k in range(4):          # four separate heart-shaped leaves, a clear gap between them
        a=k*math.pi/2+math.pi/4; lc=_pt(c,S*0.165,a); r=S*0.06
        for side in (-1,1): _disc(d,_pt(lc,r*0.55,a+side*math.pi/2),r,fg)
        d.polygon([_pt(lc,r*1.25,a+math.pi*0.72),_pt(lc,r*1.25,a-math.pi*0.72),_pt(c,S*0.02,a)],fill=fg)
    for k in range(11):         # barcode over the clover
        x=S*0.29+k*S*0.038; w=S*(0.011 if k%3 else 0.02); d.rectangle([x,S*0.35,x+w,S*0.43],fill=ac)
    d.polygon([(S*0.47,S*0.56),(S*0.53,S*0.56),(S*0.56,S*0.94),(S*0.44,S*0.94)],fill=fg)   # the stack
    for k,(u,v) in enumerate(((0.62,0.62),(0.72,0.53),(0.81,0.42))): _disc(d,(S*u,S*v),S*(0.028+k*0.012),ac)   # its smoke
def v_fist(d,S,fg,ac):      # V: a raised fist, and what it grips is the remote control (held across, never pointing up)
    d.rectangle([S*0.4,S*0.6,S*0.6,S*0.96],fill=fg)                                       # forearm
    d.rounded_rectangle([S*0.14,S*0.32,S*0.86,S*0.44],radius=S*0.03,fill=ac)              # the remote, across the grip
    for k in range(4): _disc(d,(S*0.2+k*S*0.05,S*0.38),S*0.016,fg)                          # its buttons
    _disc(d,(S*0.8,S*0.38),S*0.024,(220,30,30))
    d.rounded_rectangle([S*0.3,S*0.28,S*0.7,S*0.64],radius=S*0.08,fill=fg)                # the fist over it
    for k in range(3): x=S*0.4+k*S*0.1; _line(d,[(x,S*0.3),(x,S*0.44)],S*0.02,ac)          # finger creases
    _line(d,[(S*0.32,S*0.5),(S*0.52,S*0.5)],S*0.03,ac)                                    # the thumb
def kd_cam(d,S,fg,ac):      # KD: the family, kept safe inside a CCTV housing
    d.polygon([(S*0.1,S*0.2),(S*0.78,S*0.2),(S*0.86,S*0.3),(S*0.86,S*0.6),(S*0.1,S*0.6)],fill=fg)   # housing
    d.rectangle([S*0.8,S*0.33,S*0.95,S*0.47],fill=fg)                                     # lens hood
    _line(d,[(S*0.3,S*0.6),(S*0.3,S*0.8),(S*0.18,S*0.95)],S*0.05,fg)                     # the mount
    d.rectangle([S*0.16,S*0.26,S*0.74,S*0.54],fill=ac)                                    # the window
    for (x,h) in ((0.3,1.0),(0.45,1.0),(0.6,0.7)):                                        # two adults and a child, faceless
        hx=S*x; top=S*0.54-S*0.24*h; _disc(d,(hx,top+S*0.035),S*0.03,fg); d.rectangle([hx-S*0.035,top+S*0.075,hx+S*0.035,S*0.54],fill=fg)
    _disc(d,(S*0.7,S*0.3),S*0.022,(220,30,30))                                            # the recording light
def l_torch(d,S,fg,ac):     # L: the torch of liberty, with a subscription tag on a string
    d.polygon([(S*0.38,S*0.42),(S*0.62,S*0.42),(S*0.54,S*0.95),(S*0.46,S*0.95)],fill=fg)   # handle
    d.rectangle([S*0.34,S*0.38,S*0.66,S*0.45],fill=fg)
    d.polygon([(S*0.5,S*0.04),(S*0.64,S*0.22),(S*0.6,S*0.36),(S*0.4,S*0.36),(S*0.36,S*0.22)],fill=ac)   # flame
    _line(d,[(S*0.64,S*0.44),(S*0.76,S*0.58)],S*0.012,fg)                                 # the string
    d.polygon([(S*0.72,S*0.58),(S*0.94,S*0.58),(S*0.94,S*0.82),(S*0.72,S*0.82),(S*0.66,S*0.7)],fill=ac)   # the tag
    c=(S*0.84,S*0.7); _ring(d,c,S*0.045,S*0.014,fg)                                        # ¤, the generic currency sign
    for k in range(4): _line(d,[_pt(c,S*0.05,math.pi/4+k*math.pi/2),_pt(c,S*0.075,math.pi/4+k*math.pi/2)],S*0.014,fg)
def mp_dandelion(d,S,fg,ac):# MP: a dandelion clock whose seeds are drones, some already airborne
    c=(S*0.42,S*0.44); _line(d,[(c[0],c[1]),(S*0.46,S*0.96)],S*0.03,fg)
    for k in range(11):
        a=-math.pi*0.95+k*math.pi*1.9/10; tip=_pt(c,S*0.26,a); _line(d,[c,tip],S*0.012,fg); _drone(d,tip,S*0.03,ac)
    _disc(d,c,S*0.04,fg)
    for (u,v) in ((0.78,0.2),(0.88,0.36),(0.74,0.06)): _drone(d,(S*u,S*v),S*0.035,ac)
MARKS=[s_rose,m_lock,sd_globe,c_clover,v_fist,kd_cam,l_torch,mp_dandelion]
def logo(i,px,fg,ac):
    S=px*SS; im=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(im); MARKS[i](d,S,fg+(255,) if len(fg)==3 else fg, ac+(255,) if len(ac)==3 else ac)
    return im.resize((px,px),Image.LANCZOS)
