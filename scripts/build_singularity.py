#!/usr/bin/env python3
"""Render the profile's film once, so readers never run a particle renderer.

Deterministic original motion design. Pillow + NumPy, bundled open fonts,
no browser, network, GPU, JavaScript, live filters or remote image services.
The same pieces form the profile, fracture, orbit and return. WebP carries
only the finished frames. Run --preview for the storyboard without encoding.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from random import Random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
FONTS = ASSETS / 'fonts'
DURATION = 18
FPS = 30
PALETTE = {'paper': '#ede9e0', 'muted': '#87909c', 'dim': '#566270',
           'gold': '#d9af7a', 'cold': '#a6c3dc', 'surface': '#10151c'}


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def smooth(x):
    x = clamp(x)
    return x * x * (3 - 2 * x)


def smoother(x):
    x = clamp(x)
    return x * x * x * (x * (6 * x - 15) + 10)


def rgb(col):
    return tuple(bytes.fromhex(col.lstrip('#')))


@lru_cache(maxsize=128)
def font(size, face='regular'):
    name = {'bold': 'DejaVuSans-Bold.ttf', 'regular': 'DejaVuSans-ExtraLight.ttf',
            'mono': 'DejaVuSansMono.ttf'}[face]
    return ImageFont.truetype(str(FONTS / name), round(size))


def label_sprite(text, size, color, face='regular', spacing=0):
    """Typeset at 2x, keeping text antialiased through rotation and compression."""
    f = font(size * 2, face)
    boxes = [f.getbbox(c) for c in text] if spacing else [f.getbbox(text)]
    if spacing:
        width = sum(f.getlength(c) + spacing * 2 for c in text) - spacing * 2
    else:
        width = f.getlength(text)
    top = min(b[1] for b in boxes)
    bottom = max(b[3] for b in boxes)
    im = Image.new('RGBA', (math.ceil(width) + 8, bottom - top + 8))
    d = ImageDraw.Draw(im)
    if spacing:
        x = 4
        for c in text:
            d.text((x, 4 - top), c, fill=color, font=f)
            x += f.getlength(c) + spacing * 2
    else:
        d.text((4, 4 - top), text, fill=color, font=f)
    return im.resize((math.ceil(im.width / 2), math.ceil(im.height / 2)), Image.Resampling.LANCZOS)


@dataclass
class Piece:
    sprite: Image.Image
    x: float
    y: float
    kind: str
    keep: bool
    phase: float
    start: float
    end: float
    radius: float
    flatten: float
    omega: float
    spin: float
    orbit_scale: float


class Film:
    def __init__(self, mobile=False):
        self.mobile = mobile
        self.W, self.H = (640, 860) if mobile else (1120, 700)
        self.cx, self.cy = (320, 426) if mobile else (560, 358)
        self.unit = .86 if mobile else 1.0
        self.rng = Random(20261110 + int(mobile))
        self.pieces = []
        self.build_profile()
        self.background = self.make_background()
        self.stars = self.make_stars()
        self.intact = self.background.copy()
        for p in self.pieces:
            self.intact.alpha_composite(p.sprite, (round(p.x - p.sprite.width/2), round(p.y - p.sprite.height/2)))
        self.footer = self.make_footer()
        # Half-resolution radiance is smooth by construction. Crisp text/shards
        # and the shadow silhouette are composited at the full output size.
        yy, xx = np.mgrid[0:self.H:2, 0:self.W:2].astype(np.float32)
        self.X = xx - self.cx
        self.Y = yy - self.cy
        a = -.19
        self.U = self.X * math.cos(a) + self.Y * math.sin(a)
        self.V = -self.X * math.sin(a) + self.Y * math.cos(a)
        self.R = np.sqrt(self.X**2 + self.Y**2)
        self.theta = np.arctan2(self.Y, self.X)
        self.spark_data = [(self.rng.uniform(0, math.tau), self.rng.uniform(155, 530) * self.unit,
                            self.rng.uniform(.25, .95), self.rng.uniform(.35, .68),
                            self.rng.choice([.6, .8, 1.0, 1.4])) for _ in range(110 if not mobile else 76)]

    def add(self, sprite, x, y, kind='text', keep=None):
        r = self.rng
        pcx, pcy = x + sprite.width/2, y + sprite.height/2
        if keep is None:
            keep = kind == 'text' and r.random() < .50
        distance = math.hypot(pcx-self.cx, pcy-self.cy)
        release = 1.6 + distance / self.W * 1.3 + r.uniform(0, .45)
        radius = r.uniform(170, 260) if self.mobile else r.uniform(195, 440)
        radius = min(radius, (self.W/2 - 40 - sprite.width*.46)/1.08)
        self.pieces.append(Piece(sprite, pcx, pcy, kind, keep, r.uniform(0, math.tau),
            release, release + r.uniform(3.1, 4.6), radius, r.uniform(.85, 1.20) if self.mobile else r.uniform(.37, .68),
            r.uniform(.30, .55) * (300*self.unit / radius)**.7,
            r.uniform(-1, 1), r.uniform(.58, .86) if kind == 'text' else r.uniform(.16, .35)))

    def text(self, value, x, y, size, color='paper', face='regular', spacing=0,
             split=False, keep=None):
        col = PALETTE.get(color, color)
        if split:
            for word in value.split(' '):
                sprite = label_sprite(word, size, col, face, spacing)
                self.add(sprite, x, y, keep=keep)
                x += font(size, face).getlength(word + ' ')
        else:
            self.add(label_sprite(value, size, col, face, spacing), x, y, keep=keep)
            titles = ('Psi', 'Shohin', 'GPU / MoE', 'Frameworks')
            if value in titles:
                i=titles.index(value);p=self.pieces[-1]
                p.phase=i*math.pi/2
                p.omega=.40
                p.radius=([175,205,185,190] if self.mobile else [310,360,300,335])[i]
                p.flatten=1.02 if self.mobile else .68

    def rule(self, x, y, width, color='dim', height=1):
        col = rgb(PALETTE.get(color, color))
        # Segments are genuine pieces of the original rule, not filler particles.
        for i in range(4):
            lo, hi = round(i*width/4), round((i+1)*width/4)
            sprite = Image.new('RGBA', (hi-lo, height), col+(150,))
            self.add(sprite, x+lo, y, 'rule', keep=i == 1)

    def headline(self, x, y, size):
        whole = label_sprite('SAI', size, PALETTE['paper'], 'bold', -size*.060)
        # Horizontal shear strips split the actual glyph image. No duplicated
        # cards, browser clip paths or replacement labels exist in the film.
        widths = [0, .29, .58, .82, 1.0]
        rows = [0, .32, .56, .78, 1.0]
        for j in range(len(rows)-1):
            for i in range(len(widths)-1):
                a,b = round(widths[i]*whole.width), round(widths[i+1]*whole.width)
                c,d = round(rows[j]*whole.height), round(rows[j+1]*whole.height)
                p = whole.crop((a,c,b,d))
                if p.getbbox():
                    self.add(p, x+a,y+c,'headline', keep=(i+j)%5==0)

    def card(self, x, y, w, h, n, title, line1, line2, accent):
        # Thin open editorial rules instead of UI badges and rounded cards.
        self.rule(x,y,w,'dim')
        self.text(n, x, y+18, 10 if not self.mobile else 11, accent, 'mono', spacing=1, keep=False)
        self.text(title,x,y+47,30 if not self.mobile else 31,'paper','bold',keep=True)
        self.text(line1,x,y+98,12 if not self.mobile else 14,'muted',split=True)
        self.text(line2,x,y+119,11 if not self.mobile else 12,'dim',split=True)
        self.rule(x,y+h,w,'dim')
        # Two small solid edges are part of the original card structure.
        self.add(Image.new('RGBA',(2,16),rgb(PALETTE[accent])+(170,)),x+w-2,y+17,'rule',False)

    def build_profile(self):
        if self.mobile:
            self.text('SAICHARAN RAMINENI',35,40,12,'muted','mono',spacing=1.35,keep=False)
            self.text('01',574,41,11,'gold','mono',keep=False)
            self.rule(35,70,570)
            self.headline(26,111,197)
            self.text('I build things to understand them.',36,293,22,'paper',keep=False)
            self.text('GPU KERNELS  /  SMALL MODELS  /  SYSTEMS',36,335,10,'gold','mono',spacing=.35,keep=False)
            self.card(36,393,270,158,'01 / AUTOGRAD','Psi','C++ · Metal · CUDA','From scratch. To the metal.','gold')
            self.card(334,393,270,158,'02 / RESEARCH','Shohin','Models that revise','Experiments + negative results','cold')
            self.card(36,593,270,158,'03 / COMPUTE','GPU / MoE','Routing + memory','Measure. Optimize. Repeat.','cold')
            self.card(334,593,270,158,'04 / UPSTREAM','Frameworks','PyTorch · TF · JAX','Numerical + runtime fixes','gold')
        else:
            self.text('SAICHARAN RAMINENI',52,35,11,'muted','mono',spacing=1.6,keep=False)
            self.text('CODE / RESEARCH / SYSTEMS',811,36,10,'gold','mono',spacing=.65,keep=False)
            self.rule(52,63,1016)
            self.headline(36,105,250)
            self.text('I build things',590,153,31,'paper',split=True,keep=False)
            self.text('to understand them.',590,199,31,'paper',split=True,keep=False)
            self.text('GPU kernels. Small models.',593,268,13,'muted',split=True)
            self.text('The systems beneath them.',593,291,13,'muted',split=True)
            self.card(52,411,238,159,'01 / AUTOGRAD','Psi','C++ · Metal · CUDA','From scratch. To the metal.','gold')
            self.card(312,411,238,159,'02 / RESEARCH','Shohin','Models that revise','Controls + negative results','cold')
            self.card(572,411,238,159,'03 / COMPUTE','GPU / MoE','Routing + memory','Measure. Optimize. Repeat.','cold')
            self.card(832,411,236,159,'04 / UPSTREAM','Frameworks','PyTorch · TF · JAX','Numerical + runtime fixes','gold')

    def make_background(self):
        yy, xx = np.mgrid[0:self.H, 0:self.W].astype(np.float32)
        d=((xx-self.cx)/(self.W*.65))**2+((yy-self.cy)/(self.H*.68))**2
        c=np.empty((self.H,self.W,3),dtype=np.float32)
        for i,col in enumerate([7,10,15]): c[:,:,i]=col+np.exp(-d*2.8)*[2,3,4][i]
        return Image.fromarray(c.astype('uint8')).convert('RGBA')

    def make_stars(self):
        im=Image.new('RGBA',(self.W,self.H))
        d=ImageDraw.Draw(im)
        for i in range(130 if not self.mobile else 85):
            x,y=self.rng.randrange(self.W),self.rng.randrange(80,self.H-70)
            alpha=self.rng.randint(30,95)
            rad=.5 if i%7 else 1
            d.ellipse((x-rad,y-rad,x+rad,y+rad),fill=(150,170,195,alpha))
        return im

    def make_footer(self):
        im=Image.new('RGBA',(self.W,self.H))
        left=label_sprite('S I N G U L A R I T Y',10, '#7b8590','mono')
        right=label_sprite('SAI / 001',10,'#7b8590','mono')
        margin=36 if self.mobile else 52
        im.alpha_composite(left,(margin,self.H-43))
        im.alpha_composite(right,(self.W-margin-right.width,self.H-43))
        return im

    def clock(self,t):
        # Return along the same continuous trajectories. The opening and final
        # half-second are pixel-identical: no abrupt cut or randomized reset.
        if t<=11.5:return t
        if t<=12.5:
            u=t-11.5
            return 11.5+u-.5*u*u
        return 12.0*(1-smoother((t-12.5)/5.0))

    def position(self,p,t):
        u=clamp((t-p.start)/(p.end-p.start))
        if u==0:return p.x,p.y,1.0,0.0,1.0,0.0
        pull=smooth(u)
        a0=math.atan2(p.y-self.cy,p.x-self.cx)
        r0=math.hypot(p.x-self.cx,p.y-self.cy)
        # An accelerating infall blends continuously into Kepler-like orbits.
        omega=p.omega
        turn=2.8*smooth(u)*smooth((u-.15)/.85)+omega*(t-p.start)*smooth(u)
        offset=(p.phase-(a0+2.8-omega*p.start)+math.pi)%math.tau-math.pi
        a=a0+turn+offset*smooth((u-.50)/.50)
        target=p.radius if p.keep else 7*self.unit
        rad=(r0*(1-pull)+target*pull)*(1-.22*math.sin(math.pi*u))
        flatten=1-(1-p.flatten)*smooth(u)
        x=rad*math.cos(a)
        y=rad*math.sin(a)*flatten
        tilt=-.19*smooth(u)
        px=self.cx+x*math.cos(tilt)-y*math.sin(tilt)
        py=self.cy+x*math.sin(tilt)+y*math.cos(tilt)
        # Perspective breathes naturally as fragments cross the orbital plane.
        depth=math.sin(a)
        scale=(1-smooth(u))+p.orbit_scale*smooth(u)
        scale*=1+.16*depth*smooth(u)
        if not p.keep:scale*=1-.96*pull
        # Smooth tilt has no modulo wrap: a 180-degree angle discontinuity
        # would create a visible jump even in a perfectly timed 30fps movie.
        rotation=-(math.sin(a)*25+p.spin*10)*smooth(u)
        if p.kind=='headline':rotation=-(math.degrees(turn)*.65+p.spin*65)*smooth(u)
        if p.kind=='rule':rotation=-math.degrees(turn)*.8*smooth(u)
        opacity=1.0
        if not p.keep:opacity=1-smooth((u-.68)/.32)
        else:opacity=(.62+.38*(depth+1)/2)*smooth(u)+1-smooth(u)
        return px,py,max(.015,scale),rotation,opacity,depth

    def piece_sprite(self,p,scale,rotation,opacity):
        stretch=1+.7*(1-scale) if p.kind=='headline' else 1.0
        w=max(1,round(p.sprite.width*scale*stretch));h=max(1,round(p.sprite.height*scale/math.sqrt(stretch)))
        im=p.sprite if (w,h)==p.sprite.size else p.sprite.resize((w,h),Image.Resampling.LANCZOS)
        if p.kind=='headline' and scale<.98:
            warm=Image.new('RGBA',im.size,(238,192,131));warm.putalpha(im.getchannel('A'))
            im=Image.blend(im,warm,min(.42,(1-scale)*.6))
        elif p.kind=='text' and scale<.98:
            im=ImageEnhance.Brightness(im).enhance(1+.6*(1-scale))
        if abs(rotation)>.03:im=im.rotate(rotation,resample=Image.Resampling.BICUBIC,expand=True)
        if opacity<.999:
            im=im.copy();im.putalpha(im.getchannel('A').point(lambda a:round(a*opacity)))
        return im

    def draw_pieces(self,t):
        back=Image.new('RGBA',(self.W,self.H));front=Image.new('RGBA',(self.W,self.H))
        for p in self.pieces:
            x,y,s,a,op,depth=self.position(p,t)
            if op<.012:continue
            target=back if depth<0 else front
            # Short exposure trails only on fast actual shards. These are baked
            # into the frame, never live SVG filters or extra browser nodes.
            past=self.position(p,max(0,t-.045))
            speed=math.hypot(x-past[0],y-past[1])
            if speed>4 and s>.04:
                for lag,alpha in ((.055,.14),(.028,.23)):
                    tx,ty,ts,ta,to,_=self.position(p,max(0,t-lag))
                    ghost=self.piece_sprite(p,ts,ta,to*alpha)
                    target.alpha_composite(ghost,(round(tx-ghost.width/2),round(ty-ghost.height/2)))
            sprite=self.piece_sprite(p,s,a,op)
            target.alpha_composite(sprite,(round(x-sprite.width/2),round(y-sprite.height/2)))
        return back,front

    def field(self,t,mass):
        if mass<.005:return Image.new('RGBA',(self.W,self.H))
        radius=84*self.unit*mass
        U,V,R=self.U,self.V,self.R
        theta=self.theta
        # Brightness and color are integrated into a single immutable image.
        # Disk streaks advect coherently; there is no frame-random grain.
        rho=np.sqrt(U*U+(V/.245)**2)+.01
        ang=np.arctan2(V/.245,U)
        disk=np.exp(-((rho-radius*1.9)/(radius*.90+1))**2)
        disk*=np.clip((rho-radius*1.12)/(radius*.35+1),0,1)
        texture=(.55+.20*np.sin(rho*.14-ang*4+t*1.9)
                 +.14*np.sin(rho*.36+ang*9-t*2.8)+.08*np.sin(rho*.71-ang*13+t))
        disk*=np.clip(texture,.10,1.0)*(1+.5*np.cos(ang+.5))
        ring=np.exp(-((R-radius)/(1.1+mass*.9))**2)
        subring=np.exp(-((R-radius*1.07)/(1.5+mass*1.1))**2)*.22
        ringlight=(ring+subring)*(.72+.28*np.cos(theta+.65))
        halo=np.exp(-((R-radius)/(radius*.30+1))**2)*.09
        wide=np.exp(-((R-radius)/(radius*1.4+1))**2)*.018
        # A long anamorphic flare grows out of the disk, not the whole page.
        flare=np.exp(-np.abs(U)/(radius*4+1))*np.exp(-(V/(.8+mass*.8))**2)*.22
        heat=np.clip((np.cos(ang+.7)+1)*.5,0,1)
        radiance=np.zeros((*R.shape,3),dtype=np.float32)
        warm=(1.0,.48,.19);cool=(.70,.83,1.0)
        for c in range(3):
            diskcolor=warm[c]*(.75+.25*heat)+cool[c]*.16*(1-heat)
            radiance[:,:,c]=disk*diskcolor*.83+(ringlight*1.05+halo)*[1,.80,.52][c]+wide*[.42,.53,.78][c]+flare*[1,.75,.43][c]
        # Nothing can shine from inside the shadow. Bloom is applied afterwards.
        radiance[R<radius*.935]=0
        radiance*=smooth(mass)*mass
        linear=np.clip(radiance*240,0,255).astype('uint8')
        source=Image.fromarray(linear).resize((self.W,self.H),Image.Resampling.BILINEAR)
        tight=source.filter(ImageFilter.GaussianBlur(3*self.unit))
        wideglow=source.filter(ImageFilter.GaussianBlur(15*self.unit))
        source=ImageChops.add(source,ImageEnhance.Brightness(tight).enhance(.48))
        source=ImageChops.add(source,ImageEnhance.Brightness(wideglow).enhance(.75))
        return source

    def sparks(self,t,mass):
        im=Image.new('RGBA',(self.W,self.H));d=ImageDraw.Draw(im)
        if mass<.02:return im
        for i,(phase,rad,omega,flat,weight) in enumerate(self.spark_data):
            points=[]
            for j in range(8):
                a=phase+(t-j*.034)*omega
                rr=rad*(.97+.03*math.cos(a*2+phase))
                x=rr*math.cos(a);y=rr*math.sin(a)*flat
                points.append((self.cx+x*.982+y*.189,self.cy-x*.189+y*.982))
            alpha=round((38+65*(math.sin(phase)+1)/2)*mass)
            color=(216,173,122) if i%3 else (155,188,217)
            for j in range(7):
                d.line([points[j],points[j+1]],fill=color+(round(alpha*(1-j/8)),),width=1)
            if i%5==0:
                x,y=points[0]
                d.ellipse((x-1,y-1,x+1,y+1),fill=(246,223,191,round(alpha*1.5)))
        return im

    def render(self,time):
        t=self.clock(time)
        mass=smooth((t-1.2)/3.2)
        if t<1.4:
            result=self.intact.copy();result.alpha_composite(self.footer)
            return result.convert('RGB')
        base=self.background.copy()
        star=self.stars.copy();star.putalpha(star.getchannel('A').point(lambda a:round(a*mass)))
        base.alpha_composite(star)
        back,front=self.draw_pieces(t)
        base.alpha_composite(back)
        base.alpha_composite(self.sparks(t,mass))
        radius=84*self.unit*mass
        # Occlude the rear layer with a full-resolution event-horizon silhouette.
        d=ImageDraw.Draw(base)
        d.ellipse((self.cx-radius*.97,self.cy-radius*.97,self.cx+radius*.97,self.cy+radius*.97),fill=(1,2,4,255))
        glow=self.field(t,mass)
        if glow.mode=='RGB':base=ImageChops.add(base.convert('RGB'),glow).convert('RGBA')
        ImageDraw.Draw(front).ellipse((self.cx-radius*.94,self.cy-radius*.94,self.cx+radius*.94,self.cy+radius*.94),fill=(0,0,0,0))
        base.alpha_composite(front)
        # Modest camera push; all profile geometry and lighting share the camera.
        zoom=1+.07*mass+.01*smooth((t-5.5)/4)
        if zoom>1.0001:
            w,h=round(self.W*zoom),round(self.H*zoom)
            base=base.resize((w,h),Image.Resampling.BICUBIC)
            dx,dy=(w-self.W)//2,(h-self.H)//2
            base=base.crop((dx,dy,dx+self.W,dy+self.H))
        base.alpha_composite(self.footer)
        return base.convert('RGB')


_WORKER_FILM=None

def init_worker(mobile):
    global _WORKER_FILM
    _WORKER_FILM=Film(mobile)


def render_frame(args):
    i,fps,directory=args
    path=Path(directory)/f'{i:04d}.png'
    _WORKER_FILM.render(i/fps).save(path,compress_level=1)
    return i


def storyboard(film,output):
    times=[0,2.8,4.4,6.0,8.5,11.7,14.5,17.5]
    thumbw=560 if not film.mobile else 320
    thumbh=round(film.H*thumbw/film.W)
    cols=2 if not film.mobile else 4
    rows=math.ceil(len(times)/cols)
    sheet=Image.new('RGB',(cols*thumbw,rows*(thumbh+28)),(13,17,23))
    d=ImageDraw.Draw(sheet)
    for i,t in enumerate(times):
        frame=film.render(t).resize((thumbw,thumbh),Image.Resampling.LANCZOS)
        x=(i%cols)*thumbw;y=(i//cols)*(thumbh+28)
        sheet.paste(frame,(x,y))
        d.text((x+12,y+thumbh+6),f'{t:04.1f} s',font=font(12,'mono'),fill='#c6cbd2')
    sheet.save(output)


def encode(framesdir,output,fps,quality):
    files=sorted(Path(framesdir).glob('*.png'))
    # Pillow retains loaded source frames until encoding completes. Allow about
    # 2 GiB for desktop encoding; PNGs are an ignored cache, not repo assets.
    # Frame durations sum to exactly 18 s.
    frames=[Image.open(p) for p in files]
    durations=[round((i+1)*1000/fps)-round(i*1000/fps) for i in range(len(frames))]
    frames[0].save(output,format='WEBP',save_all=True,append_images=frames[1:],
                   duration=durations,loop=0,quality=quality,method=4,
                   lossless=False,minimize_size=True,allow_mixed=False)
    for frame in frames:frame.close()


def build_singularity(variant='all',preview=False,output_dir=ASSETS,workers=4,quality=64):
    output_dir=Path(output_dir);output_dir.mkdir(parents=True,exist_ok=True)
    cache=ROOT/'previews';cache.mkdir(exist_ok=True)
    variants=[False,True] if variant=='all' else [variant=='mobile']
    metadata={}
    for mobile in variants:
        name='singularity-mobile' if mobile else 'singularity'
        film=Film(mobile)
        film.render(0).save(output_dir/f'{name}-poster.png',optimize=True)
        storyboard(film,cache/f'{name}-storyboard.png')
        print(f'{name}: {len(film.pieces)} actual profile pieces, {film.W}x{film.H}',flush=True)
        if preview:continue
        source_hash=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()[:10]
        framesdir=cache/f'{name}-frames-{source_hash}';framesdir.mkdir(exist_ok=True)
        count=DURATION*FPS
        jobs=[(i,FPS,str(framesdir)) for i in range(count)]
        with ProcessPoolExecutor(max_workers=workers,initializer=init_worker,initargs=(mobile,)) as pool:
            for i in pool.map(render_frame,jobs,chunksize=6):
                if i%90==0:print(f'{name}: rendered {i}/{count}',flush=True)
        print(f'{name}: encoding {count} source frames',flush=True)
        dest=output_dir/f'{name}.webp'
        encode(framesdir,dest,FPS,quality)
        metadata[name]={'dimensions':[film.W,film.H],'fps':FPS,'source_frames':count,
                        'duration_ms':DURATION*1000,'bytes':dest.stat().st_size,
                        'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}
        print(f'{name}: {dest.stat().st_size:,} bytes',flush=True)
    if not preview:
        (cache/'render-metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--variant',choices=['all','desktop','mobile'],default='all')
    ap.add_argument('--preview',action='store_true',help='Render posters and storyboard only')
    ap.add_argument('--output-dir',type=Path,default=ASSETS)
    ap.add_argument('--workers',type=int,default=min(4,os.cpu_count() or 1))
    ap.add_argument('--quality',type=int,default=64)
    args=ap.parse_args()
    build_singularity(args.variant,args.preview,args.output_dir,args.workers,args.quality)
