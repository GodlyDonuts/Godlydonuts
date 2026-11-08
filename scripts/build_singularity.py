#!/usr/bin/env python3
"""Generate GitHub-safe, self-contained, animated profile-collapse SVGs.

Pure Python, no external rendering services or dependencies. Motion is SMIL,
not JavaScript. The whole "shattered README" is an optical illusion INSIDE
one image. GitHub HTML outside the image cannot be manipulated by an SVG.
"""
from __future__ import annotations

from html import escape
from math import cos, sin, pi, hypot
from pathlib import Path
from random import Random

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets"
DURATION = 32
COLORS = ["#F5F0E8", "#FF8565", "#A3ACFF", "#E3BD9E", "#7D9EBC"]


def e(t):
    return escape(str(t), quote=True)


def opacity_timing(start: float, end: float, fade=0.35):
    # One looping animation timeline, restoring the clean state before restart.
    times = [0, max(0,start-.02)/DURATION, start/DURATION,
             min(DURATION,end)/DURATION, min(DURATION,end+fade)/DURATION,
             1]
    return (';'.join(f'{v:.5f}' for v in times), '0;0;1;1;0;0')


def animate_opacity(start, end, fade=.35):
    kt, values = opacity_timing(start, end, fade)
    return f'<animate attributeName="opacity" values="{values}" keyTimes="{kt}" dur="{DURATION}s" calcMode="linear" repeatCount="indefinite"/>'


def profile_card(key,x,y,w,h,accent,number,title,line1,line2,foot):
    # The information is real; only the simulated UI is subject to gravity.
    return f'''<g id="card-{key}">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#111724" stroke="#394258" stroke-width="1.1"/>
      <rect x="{x}" y="{y}" width="{w}" height="5" rx="2" fill="{accent}"/>
      <text x="{x+22}" y="{y+32}" fill="{accent}" font-size="12" font-weight="760" letter-spacing="1.7">{number}</text>
      <text x="{x+22}" y="{y+84}" fill="#F5F0E8" font-size="47" font-weight="850" letter-spacing="-2.1">{e(title)}</text>
      <text x="{x+22}" y="{y+112}" fill="#B2B7C5" font-size="15">{e(line1)}</text>
      <text x="{x+22}" y="{y+135}" fill="#8B93A5" font-size="14">{e(line2)}</text>
      <text x="{x+22}" y="{y+h-14}" fill="{accent}" opacity=".75" font-size="10" font-weight="650" letter-spacing="1.25">{e(foot)}</text>
      <path d="M{x+w-34} {y+26}h13v13m0 -13l-13 13" fill="none" stroke="{accent}" stroke-width="1.8" opacity=".8"/>
    </g>'''


def mobile_card(key,x,y,w,h,accent,number,title,line1,line2,foot):
    return f'''<g id="card-{key}">
      <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="7" fill="#111724" stroke="#394258" stroke-width="1"/>
      <rect x="{x}" y="{y}" width="{w}" height="4" rx="2" fill="{accent}"/>
      <text x="{x+16}" y="{y+24}" fill="{accent}" font-size="10" font-weight="750" letter-spacing="1.4">{number}</text>
      <text x="{x+16}" y="{y+65}" fill="#F5F0E8" font-size="35" font-weight="850" letter-spacing="-1.5">{e(title)}</text>
      <text x="{x+16}" y="{y+88}" fill="#B2B7C5" font-size="12">{e(line1)}</text>
      <text x="{x+16}" y="{y+104}" fill="#8B93A5" font-size="12">{e(line2)}</text>
      <text x="{x+w-16}" y="{y+h-14}" text-anchor="end" fill="{accent}" font-size="9" letter-spacing="1">{e(foot)}</text>
    </g>'''


def profile_header(mobile):
    if mobile:
        return '''<g id="profile-header">
          <text x="20" y="39" fill="#A4A7BA" font-size="10.5" letter-spacing="1.6" font-weight="760">SAICHARAN RAMINENI</text>
          <path d="M20 54H412" stroke="#586275" stroke-width="1"/>
          <text x="14" y="166" fill="#F5F0E8" font-size="133" font-weight="900" letter-spacing="-13">SAI</text>
          <rect x="23" y="180" width="64" height="4" fill="#FF7452"/>
          <text x="23" y="211" fill="#F5F0E8" font-size="17" font-weight="720">I build things to understand them.</text>
          <text x="23" y="228" fill="#97A0B5" font-size="11.5">GPU kernels · small models · ML runtimes</text>
          </g>'''
    return '''<g id="profile-header">
      <text x="54" y="48" fill="#A4A7BA" font-size="12" letter-spacing="2.1" font-weight="760">SAICHARAN RAMINENI / GITHUB</text>
      <text x="970" y="48" text-anchor="end" fill="#A4A7BA" font-size="11" letter-spacing="1.7" font-weight="700">BUILD · MEASURE · REBUILD</text>
      <path d="M52 63H972" stroke="#374155" stroke-width="1"/>
      <text x="34" y="219" fill="#F5F0E8" font-size="173" font-weight="900" letter-spacing="-17">SAI</text>
      <rect x="54" y="229" width="142" height="5" fill="#FF7452"/>
      <text x="455" y="158" fill="#F5F0E8" font-size="30" font-weight="710" letter-spacing="-.8">I build things to understand them.</text>
      <text x="457" y="188" fill="#A4ADBD" font-size="16">GPU kernels, small models, and the systems beneath them.</text>
      <text x="457" y="220" fill="#FF8D6E" font-size="12" font-weight="700" letter-spacing="1.8">EXPERIMENTS / SOURCE / UPSTREAM</text>
      </g>'''


def card_setup(mobile):
    if mobile:
        boxes = [
            ("psi",20,248,392,132,"#667BFF","01 / CODE + EXPERIMENTS","Psi","Custom autograd and training stack","C++ · Metal · CUDA","OPEN SOURCE"),
            ("shohin",20,392,392,132,"#F48B65","02 / RESEARCH","Shohin","Models that revise their drafts","Controls · tests · negative results","RESEARCH LOG"),
            ("systems",20,536,392,132,"#9BA7C8","03 / SYSTEMS","GPU / MoE","Routing, memory movement, queues","Measure first, optimize next","ACTIVE RESEARCH"),
            ("upstream",20,680,392,132,"#E5C19E","04 / UPSTREAM","Frameworks","PyTorch · TensorFlow · JAX","Actual fixes merged upstream","CONTRIBUTIONS"),
        ]
        maker=mobile_card
    else:
        boxes = [
            ("psi",52,275,435,168,"#667BFF","01 / CODE + EXPERIMENTS","Psi","Custom autograd and training stack","C++ · Metal · CUDA","SOURCE / BENCHMARKS"),
            ("shohin",505,275,467,168,"#F48B65","02 / RESEARCH","Shohin","Small models learning to revise","Matched controls / negative experiments","RESEARCH + RESULTS"),
            ("systems",52,464,435,168,"#9BA7C8","03 / SYSTEMS","GPU / MoE","Expert routing + queueing","GPU memory movement and runtimes","ACTIVE RESEARCH"),
            ("upstream",505,464,467,168,"#E5C19E","04 / UPSTREAM","Frameworks","PyTorch · TensorFlow · JAX","Numerical correctness and GPU runtime","MERGED / UPSTREAM"),
        ]
        maker=profile_card
    return [(box, maker(*box)) for box in boxes]


def fracture_piece(tag, cid, x,y, w,h, cx,cy, rng, i, total):
    # Clip an ACTUAL copy of the original panel. It is that panel, not a fake tag,
    # that is physically shredded and pulled into the center.
    pcx=x+w/2; pcy=y+h/2
    dx=cx-pcx+rng.uniform(-12,12)
    dy=cy-pcy+rng.uniform(-12,12)
    angle=rng.uniform(-200,210)
    start=3.25+rng.random()*1.25+0.20*(i%3)
    end=7.2+rng.random()*1.5
    # An inward corkscrew path: initial repulsion, then shearing capture.
    tw=1 if i%2 else -1
    perp=(-dy/(hypot(dx,dy)+1), dx/(hypot(dx,dy)+1))
    bend= (30+rng.random()*80)*tw
    c1x=dx*.10+perp[0]*bend
    c1y=dy*.10+perp[1]*bend
    c2x=dx*.74+perp[0]*bend*1.4
    c2y=dy*.74+perp[1]*bend*1.4
    path=f'M0 0 C{c1x:.1f} {c1y:.1f},{c2x:.1f} {c2y:.1f},{dx:.1f} {dy:.1f}'
    t0=max(0,start-.05)/DURATION;t1=start/DURATION;t2=end/DURATION;t3=min(DURATION,end+.3)/DURATION
    k=f'0;{t0:.5f};{t1:.5f};{t2:.5f};{t3:.5f};1'
    visible=f'<animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{k}" dur="{DURATION}s" repeatCount="indefinite"/>'
    # SMIL keyPoints repeat the beginning and end of the path to match the global loop.
    # Geometry resides in user-space clip paths, transformed in unison with its copy.
    move=f'<animateMotion path="{path}" keyPoints="0;0;0;1;1;1" keyTimes="{k}" calcMode="linear" dur="{DURATION}s" repeatCount="indefinite"/>'
    sk=f'0;{t0:.5f};{t1:.5f};{t2:.5f};{t3:.5f};1'
    # Distortion around the tile center, rather than the top-left corner of the document.
    squash=f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;1 1;2.3 .19;.01 .01;1 1" keyTimes="{sk}" dur="{DURATION}s" repeatCount="indefinite"/>'
    twist=f'<animateTransform attributeName="transform" type="rotate" values="0;0;0;{angle:.1f};{angle*2:.1f};0" keyTimes="{sk}" dur="{DURATION}s" repeatCount="indefinite"/>'
    return f'''<g class="shard" opacity="0">{visible}{move}
       <g transform="translate({pcx:.2f} {pcy:.2f})"><g>{twist}<g>{squash}
       <g transform="translate({-pcx:.2f} {-pcy:.2f})" clip-path="url(#{tag})"><use href="#card-{cid}"/></g>
       </g></g></g></g>'''


def fracture_markup(mobile, boxes, rng):
    # Textures are clipped from the pristine project cards themselves, 96-144 pieces.
    cx,cy=(214,522) if mobile else (514,466)
    clips=[];pieces=[]
    for (key,x,y,w,h,*_),card in boxes:
        nx,ny=(5,4) if mobile else (7,4)
        for j in range(ny):
            for i in range(nx):
                dx=w/nx;dy=h/ny
                xx=x+i*dx;yy=y+j*dy
                tag=f'clip-{key}-{i}-{j}'
                clips.append(f'<clipPath id="{tag}" clipPathUnits="userSpaceOnUse"><rect x="{xx:.2f}" y="{yy:.2f}" width="{dx+.4:.2f}" height="{dy+.4:.2f}"/></clipPath>')
                pieces.append(fracture_piece(tag,key,xx,yy,dx,dy,cx,cy,rng,i+j*nx,nx*ny))
    return ''.join(clips), ''.join(pieces)


def header_shatter(mobile, rng):
    # Headlines are also chopped into offset text strips, so it's visibly the
    # README heading being disassembled rather than unrelated floating blocks.
    cx,cy=(214,522) if mobile else (514,466)
    x,y,w,h=(15,67,335,115) if mobile else (36,86,390,148)
    strips=[];defs=[]
    n=13
    for i in range(n):
        xx=x;yy=y+i*(h/n);ww=w;hh=h/n+.35
        tag=f'headline-{i}'
        defs.append(f'<clipPath id="{tag}" clipPathUnits="userSpaceOnUse"><rect x="{xx}" y="{yy:.2f}" width="{ww}" height="{hh:.2f}"/></clipPath>')
        pcx=xx+w/2;pcy=yy+hh/2
        dx=cx-pcx;dy=cy-pcy
        perp=(-dy/(hypot(dx,dy)+1),dx/(hypot(dx,dy)+1))
        sway=(i-6)*6
        path=f'M0 0 C{dx*.2+perp[0]*sway:.1f} {dy*.2+perp[1]*sway:.1f},{dx*.7+perp[0]*sway*2:.1f} {dy*.7+perp[1]*sway*2:.1f},{dx:.1f} {dy:.1f}'
        begin=3.30+i*.065;end=7.3+i*.09
        k=f'0;{(begin-.04)/DURATION:.5f};{begin/DURATION:.5f};{end/DURATION:.5f};{(end+.28)/DURATION:.5f};1'
        strips.append(f'''<g opacity="0">
         <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="{k}" dur="{DURATION}s" repeatCount="indefinite"/>
         <animateMotion path="{path}" keyPoints="0;0;0;1;1;1" keyTimes="{k}" dur="{DURATION}s" calcMode="linear" repeatCount="indefinite"/>
         <g transform="translate({pcx:.1f} {pcy:.1f})"><g><animateTransform attributeName="transform" type="rotate" values="0;0;0;{(i-6)*25:.1f};0;0" keyTimes="{k}" dur="{DURATION}s" repeatCount="indefinite"/>
         <g transform="translate({-pcx:.1f} {-pcy:.1f})" clip-path="url(#{tag})"><use href="#profile-header"/></g>
         </g></g></g>''')
    return ''.join(defs),''.join(strips)


def orbital_words(mobile,rng):
    cx,cy=(214,522) if mobile else (514,466)
    orbits=([(174,275,39),(146,219,29),(102,157,20)] if mobile else [(404,205,46),(323,157,33),(234,112,23),(157,69,14)])
    words=[
       'auto','grad','CUDA','CUDA::','GPU','tensor','kernel','MoE','expert','routing',
       'scratch','PyTorch','Triton','Psi','Shohin','JAX','ML','C++','Metal',
       'research','GPU / CPU','ABI','backward()','bf16','SGLang','checks','weights',
       'systems','DFT','OC20','TensorFlow','source','test','fail','rebuild','//',
       '{}','[ ]','->','0x7F','matrix','memory','ops','fork','push',
       'small models','evidence','speedup?','latency','dispatch'
    ]
    parts=[]
    for i,word in enumerate(words):
        rx,ry,speed=orbits[i%len(orbits)]
        # Negative begin shifts each token to a distinct location on its orbit.
        offset=-(i*3.73+float(i%7)*.51)
        initial=8.2+(i%9)*.18
        end=30.35
        col=COLORS[i%len(COLORS)]
        fs=(9.6 if mobile else 11.7)
        if len(word)>11:fs-=1
        span=max(30,len(word)*fs*.63+16)
        rot=f'<animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="{speed}s" repeatCount="indefinite"/>'
        path=(f'M {cx-rx:.1f} {cy:.1f} '
              f'a {rx:.1f} {ry:.1f} 0 1 0 {rx*2:.1f} 0 '
              f'a {rx:.1f} {ry:.1f} 0 1 0 {-rx*2:.1f} 0')
        # Text stays horizontal while moving on the orbit; no unreadable spinning badges.
        parts.append(f'''<g class="orbit-word" opacity="0">{animate_opacity(initial,end,.6)}
        <animateMotion path="{path}" begin="{offset:.2f}s" dur="{speed}s" rotate="0" repeatCount="indefinite"/>
        <rect x="{-span/2:.1f}" y="-11" width="{span:.1f}" height="22" rx="4" fill="#101827" stroke="{col}" stroke-opacity=".52"/>
        <text text-anchor="middle" y="4" fill="{col}" font-size="{fs}" font-weight="760" letter-spacing=".55">{e(word)}</text>
        </g>''')
    return ''.join(parts)


def event_field(mobile,rng):
    cx,cy=(214,522) if mobile else (514,466)
    # The shadow uses graphic-design rules rather than pretending to be the
    # actual physical Gargantua WebGL lensing solver.
    out=[];add=out.append
    add(f'''<g id="event-field" opacity="0">{animate_opacity(2.85,30.5,.6)}
      <circle cx="{cx}" cy="{cy}" r="{112 if mobile else 155}" fill="url(#outer-well)" opacity=".74"/>
      <ellipse cx="{cx}" cy="{cy}" rx="{95 if mobile else 147}" ry="{33 if mobile else 51}" fill="none" stroke="url(#plasma)" stroke-width="20" opacity=".40" filter="url(#glow)"/>
      <ellipse cx="{cx}" cy="{cy}" rx="{102 if mobile else 152}" ry="{38 if mobile else 53}" fill="none" stroke="url(#plasma)" stroke-width="8" opacity=".90"/>
      <g opacity=".72"><animateTransform attributeName="transform" type="rotate" values="0 {cx} {cy};11 {cx} {cy};0 {cx} {cy}" dur="12s" repeatCount="indefinite"/>
       <ellipse cx="{cx}" cy="{cy}" rx="{58 if mobile else 82}" ry="{83 if mobile else 115}" fill="none" stroke="url(#plasma)" stroke-width="5" opacity=".40"/>
      </g>
      <circle cx="{cx}" cy="{cy}" r="{65 if mobile else 85}" fill="#000003" stroke="#FFE0BB" stroke-opacity=".54" stroke-width="1.1"/>
      <circle cx="{cx}" cy="{cy}" r="{53 if mobile else 70}" fill="url(#inner-well)"/>
      <ellipse cx="{cx}" cy="{cy+13}" rx="{104 if mobile else 170}" ry="{16 if mobile else 24}" fill="none" stroke="url(#plasma)" stroke-width="4" opacity=".55"/>
    </g>''')
    # Multiple curling gravitational field lines, enough to imply warped space.
    add(f'<g class="lens-field" opacity="0">{animate_opacity(3.0,30.2,.75)}')
    for i in range(24 if mobile else 32):
        phase=i*2*pi/(24 if mobile else 32)
        rad1=(105 if mobile else 155)+rng.uniform(-20,20)
        rad2=(187 if mobile else 290)+rng.uniform(-22,22)
        x1=cx+rad1*cos(phase);y1=cy+rad1*sin(phase)*(.78 if mobile else .65)
        x2=cx+rad2*cos(phase+.34);y2=cy+rad2*sin(phase+.34)*(.88 if mobile else .68)
        xm=cx+((rad1+rad2)/2)*cos(phase+.54)
        ym=cy+((rad1+rad2)/2)*sin(phase+.54)*(.83 if mobile else .68)
        add(f'<path d="M{x1:.1f} {y1:.1f} Q{xm:.1f} {ym:.1f},{x2:.1f} {y2:.1f}" fill="none" stroke="{COLORS[i%len(COLORS)]}" stroke-width="{1.4 if i%5 else 2.2}" opacity="{.12 + rng.random()*.19:.2f}"/>')
    add('</g>')
    # Accretion sparks drifting into the singularity, with staggered phases.
    add(f'<g opacity="0">{animate_opacity(3.5,30.4,.6)}')
    for i in range(58 if mobile else 80):
        a=rng.random()*2*pi
        radius=rng.uniform(230,400) if not mobile else rng.uniform(175,300)
        x=cx+cos(a)*radius; y=cy+sin(a)*radius*(.75 if not mobile else 1.05)
        r=rng.choice([.7,.9,1.3,2.1])
        ex=cx+cos(a+2)*rng.uniform(20,58); ey=cy+sin(a+2)*rng.uniform(12,44)
        cpx=cx+cos(a+.8)*radius*.65; cpy=cy+sin(a+.8)*radius*.35
        path=f'M{x:.1f} {y:.1f} Q{cpx:.1f} {cpy:.1f} {ex:.1f} {ey:.1f}'
        add(f'<circle r="{r}" fill="{COLORS[i%len(COLORS)]}" opacity="{rng.uniform(.34,.8):.2f}"><animateMotion path="{path}" dur="{rng.uniform(3.1,8.2):.2f}s" begin="{-rng.uniform(.0,7.8):.2f}s" repeatCount="indefinite"/></circle>')
    add('</g>')
    return ''.join(out)


def stars(mobile,rng):
    W,H=(432,920) if mobile else (1024,720)
    out=[]
    for _ in range(105 if mobile else 170):
        x=rng.randint(0,W);y=rng.randint(0,H);r=rng.choice([.38,.54,.65,.9,1.2]);op=rng.uniform(.1,.45)
        out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#B4BFE3" opacity="{op:.2f}"/>')
    return ''.join(out)


def scriptless_svg(mobile: bool):
    rng=Random(25095 if mobile else 180921)
    W,H=(432,920) if mobile else (1024,720)
    cx,cy=(214,522) if mobile else (514,466)
    boxes=card_setup(mobile)
    carddefs=''.join(markup for _,markup in boxes)
    panel_frags,frags=fracture_markup(mobile,boxes,rng)
    header_clips,head_shards=header_shatter(mobile,rng)
    pristine=f'''<g class="pristine-profile"><use href="#profile-header"/>'''+''.join(f'<use href="#card-{box[0]}"/>' for box,_ in boxes)+'</g>'
    # Fallback remains unmoving even on systems that ask us to reduce motion.
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">
<title id="title">SAI — the GitHub singularity</title>
<desc id="desc">An animated GitHub profile collapses into a central singularity: real project cards and a giant SAI headline shred into fragments, then orbit with words from my work in kernels, CUDA, model revision, GPU serving, and open source.</desc>
<defs>
<style>
text{{font-family:-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif}}
.reduced-only{{display:none}}
@media(prefers-reduced-motion:reduce){{.motion-only{{display:none}} .reduced-only{{display:inline}}}}
</style>
<linearGradient id="plasma" x1="0" y1="0.5" x2="1" y2="0.5" gradientUnits="objectBoundingBox"><stop offset="0" stop-color="#A7C0FF"/><stop offset=".18" stop-color="#6D85FF"/><stop offset=".40" stop-color="#E0E9FF"/><stop offset=".64" stop-color="#F2B08B"/><stop offset=".81" stop-color="#FF674A"/><stop offset="1" stop-color="#FF674A" stop-opacity="0"/></linearGradient>
<radialGradient id="outer-well"><stop offset="0" stop-color="#525DD8" stop-opacity=".65"/><stop offset=".58" stop-color="#4E5584" stop-opacity=".13"/><stop offset="1" stop-color="#0B101C" stop-opacity="0"/></radialGradient>
<radialGradient id="inner-well"><stop offset="0" stop-color="#000000"/><stop offset=".7" stop-color="#000000"/><stop offset="1" stop-color="#080B14"/></radialGradient>
<filter id="glow" x="-90%" y="-90%" width="280%" height="280%"><feGaussianBlur stdDeviation="8"/></filter>
{carddefs}
{profile_header(mobile)}
{panel_frags}{header_clips}
</defs>
<rect width="100%" height="100%" fill="#080B13"/>
<g opacity=".75">{stars(mobile,rng)}</g>
<!-- an intact, finished GitHub-profile composition before the collapse -->
<g class="reduced-only">{pristine}</g>
<g class="motion-only">
  <g opacity="1"><animate attributeName="opacity" values="1;1;0;0;1;1" keyTimes="0;.105;.150;.918;.973;1" dur="{DURATION}s" repeatCount="indefinite"/>
   {pristine}
  </g>
  <g id="shredding">{frags}{head_shards}</g>
  {event_field(mobile,rng)}
  <g id="orbiting-remnants">{orbital_words(mobile,rng)}</g>
  <g opacity="0">{animate_opacity(4.7,30.0,.7)}
    <text x="{18 if mobile else 50}" y="{868 if mobile else 669}" fill="#FCB394" font-size="{10 if mobile else 12}" font-weight="750" letter-spacing="2">PROFILE INTEGRITY // LOST</text>
    <text x="{18 if mobile else 50}" y="{891 if mobile else 691}" fill="#8C9DB8" font-size="{10 if mobile else 12}" letter-spacing="1.0">THE WORK DIDN'T DISAPPEAR. IT CHANGED ORBIT.</text>
  </g>
</g>
<text x="{W-17}" y="{H-16}" text-anchor="end" fill="#67758F" font-size="{9 if mobile else 10}" letter-spacing="1.2">SINGULARITY / GITHUB NATIVE SVG</text>
</svg>\n'''
    return svg


def build_singularity():
    ASSETS.mkdir(parents=True, exist_ok=True)
    for mobile,name in ((False,'singularity.svg'),(True,'singularity-mobile.svg')):
        content=scriptless_svg(mobile)
        (ASSETS/name).write_text(content,encoding='utf-8')
        print(f'{name}: {len(content.encode()):,} bytes')


if __name__ == '__main__':
    build_singularity()
