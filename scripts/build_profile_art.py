#!/usr/bin/env python3
"""Build the SVG profile panels and the image-led README that links them.

The independent render_profile.py script continues to update the live now panel.
This script needs only Python's standard library; no images or web services.
"""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'assets'
STYLE = '''
text { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif; }
.bg { fill: #090B16; } .surface { fill: #12172A; }
.fg { fill: #F5F0E8; } .muted { fill: #A9A4B3; }
.line { stroke: #2B324D; } .blue { fill: #4D64FF; }
.orange { fill: #FF6845; } .on-blue { fill: #FBF7EF; }
.on-orange { fill: #15131B; } .fg-stroke { stroke: #F5F0E8; }
@media (prefers-color-scheme: light) {
 .bg { fill: #F5F0E7; } .surface { fill: #E9E2D7; }
 .fg { fill: #15131B; } .muted { fill: #6E6876; }
 .line { stroke: #D2C9BC; } .blue { fill: #2645FF; }
 .orange { fill: #ED512F; } .fg-stroke { stroke: #15131B; }
}
@media (prefers-reduced-motion: reduce) { .motion { display: none; } }
'''


def text(x, y, value, size=18, cls='fg', weight=400, extra=''):
    return (f'<text x="{x}" y="{y}" class="{cls}" font-size="{size}" '
            f'font-weight="{weight}" {extra}>{escape(value)}</text>')


def lines(x, y, values, size=18, cls='fg', gap=27, weight=400):
    return '\n'.join(text(x, y + i * gap, value, size, cls, weight)
                     for i, value in enumerate(values))


def arrow(x, y, color='currentColor', size=22):
    return (f'<path d="M{x} {y}h{size}v{size}m0 -{size}l-{size} {size}" '
            f'fill="none" stroke="{color}" stroke-width="2"/>')


def write(name, width, height, title, desc, body):
    (ASSETS / f'{name}.svg').write_text(f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
  <title id="title">{escape(title)}</title>
  <desc id="desc">{escape(desc)}</desc>
  <defs><style>{STYLE}</style></defs>
  <rect class="bg" width="{width}" height="{height}"/>
  {body}
</svg>
''')


CARDS = [
    dict(id='work-psi', title='Psi', theme='blue', label='CODE & EXPERIMENTS',
         href='https://github.com/GodlyDonuts/psi',
         desktop=['A language model and its training stack.', 'C++17 · autograd · Metal · CUDA'],
         detail=['Gradient checks, trained checkpoints,', 'and documented kernel benchmarks.'],
         mobile=['A language model and its', 'training stack in C++17.', 'Custom autograd, Metal and CUDA.', 'Gradient checks, checkpoints,', 'and kernel benchmarks.']),
    dict(id='work-shohin', title='Shohin', theme='surface', label='RESEARCH & RESULTS',
         href='https://github.com/GodlyDonuts/shohin-ettr',
         desktop=['Training models to revise their own drafts.', 'An ongoing research project.'],
         detail=['Matched controls, results, limitations,', 'and negative experiments.'],
         mobile=['Training models to revise', 'their own drafts.', 'An ongoing research project with', 'matched controls, results,', 'and negative experiments.']),
    dict(id='work-sai', title='Sai', theme='orange', label='PROTOTYPE & SOURCE',
         href='https://github.com/GodlyDonuts/sai',
         desktop=['A voice agent that operates a Mac.', 'Screenshots in. Verified actions out.'],
         detail=['Visual control, per-action verification,', 'and repeated-failure detection.'],
         mobile=['A voice agent that operates a Mac.', 'Screenshots in. Verified actions out.', 'A prototype with visual control,', 'per-action verification,', 'and repeated-failure detection.']),
    dict(id='work-gargantua', title='Gargantua', theme='surface', label='VIEW LIVE',
         href='https://saicharanramineni.com/',
         desktop=['The black hole behind my portfolio.', 'Real-time WebGL · procedural plasma'],
         detail=['Curved light paths, optical bloom,', 'and a camera driven by native scrolling.'],
         mobile=['The black hole behind my portfolio.', 'Real-time WebGL, procedural plasma,', 'curved light paths, and optical bloom.', 'A camera driven by native scrolling.', 'Open the live experience.']),
    dict(id='upstream-pytorch', title='PyTorch', theme='orange', label='ACCEPTED UPSTREAM',
         href='https://github.com/pytorch/pytorch/commit/42a70784390a343ebd90e9e84b1bf5a5df4901f3',
         desktop=['Global scratch in the static Triton launcher.', 'TorchInductor / GPU runtime'],
         detail=['Scratch allocation and metadata for', 'restoring kernels from the FX graph cache.'],
         mobile=['Global-scratch support in', 'the static Triton launcher.', 'Scratch allocation and metadata', 'for restoring kernels from', 'the FX graph cache.']),
    dict(id='upstream-tensorflow', title='TensorFlow', theme='surface', label='MERGED UPSTREAM',
         href='https://github.com/tensorflow/tensorflow/pull/125171',
         desktop=['SELU gradient precision for negative inputs.', 'Numerical correctness'],
         detail=['Float32 and float64 regression coverage', 'in both graph and eager execution.'],
         mobile=['SELU gradient precision', 'for negative inputs.', 'Float32 and float64 regressions', 'cover graph and eager execution.', 'Merged into TensorFlow.']),
]


def card(item, mobile):
    width, height = (420, 340) if mobile else (846, 204)
    panel_width, panel_height = (420, 134) if mobile else (302, height)
    theme = item['theme']
    fg = 'on-blue' if theme == 'blue' else 'on-orange' if theme == 'orange' else 'fg'
    color = '#FBF7EF' if theme == 'blue' else '#15131B' if theme == 'orange' else '#FF6845'
    title = item['title']
    size = (58 if len(title) > 8 else 68) if mobile else (44 if len(title) > 8 else 62)
    body = f'<rect class="{theme}" width="{panel_width}" height="{panel_height}"/>'
    body += text(24, 29, item['label'], 10.5, fg, 700, 'letter-spacing="1.2"')
    body += text(22, 102 if mobile else 117, title, size, fg, 880, 'letter-spacing="-2.5"')
    body += arrow(370 if mobile else 251, 24 if mobile else 159, color)
    if mobile:
        body += lines(24, 177, item['mobile'], 18, gap=29)
    else:
        body += lines(334, 55, item['desktop'], 20, gap=30, weight=600)
        body += lines(334, 139, item['detail'], 17, 'muted', gap=27)
        body += text(24, 181, 'saicharanramineni.com' if item['id']=='work-gargantua' else 'open project' if item['id'].startswith('work') else 'view contribution', 12, fg)
    if item['id']=='work-gargantua':
        # A restrained, code-drawn orbital mark; the card opens the live site.
        cx, cy = (330, 90) if mobile else (259, 66)
        body += f'<circle cx="{cx}" cy="{cy}" r="24" fill="none" stroke="#FF6845" stroke-width="2" opacity="0.42"/>'
        body += f'<ellipse cx="{cx}" cy="{cy}" rx="33" ry="7" transform="rotate(-18 {cx} {cy})" fill="none" stroke="#FFB45C" stroke-width="1.5" opacity="0.6"/>'
    elif item['id']=='work-sai':
        # Voice motif, kept separate from the readable name.
        x = 270 if mobile else 198
        for i, h in enumerate([12, 28, 43, 23, 34, 10]):
            body += f'<rect x="{x+i*10}" y="{82-h/2}" width="3" height="{h}" rx="1.5" fill="{color}" opacity="0.27"/>'
    alt = title + '. ' + ' '.join(item['desktop']+item['detail'])
    write(item['id']+('-mobile' if mobile else ''), width, height, title, alt, body)


def support_panels(mobile):
    width = 420 if mobile else 846
    suffix = '-mobile' if mobile else ''
    intro = (['I work through papers and source code', 'by building and testing implementations.', 'GPU kernels, small models, ML runtimes.'] if mobile else
             ['I work through papers and framework source by building and testing implementations.', 'GPU kernels, small models, and the runtimes beneath them.'])
    body = '<rect class="orange" x="22" y="26" width="4" height="75"/>'
    body += lines(42, 47, intro, 17 if mobile else 18, gap=29)
    write('profile-intro'+suffix, width, 132, 'How I work', ' '.join(intro), body)
    for name, title in [('heading-work','selected work'),('heading-upstream','upstream')]:
        write(name+suffix, width, 94, title, title,
              text(22, 70, title, 46 if mobile else 56, weight=880, extra='letter-spacing="-2.2"') +
              f'<line class="line" x1="{330 if mobile else 500}" y1="59" x2="{width-24}" y2="59"/>')
    for name, title, desc in [('fold-now','right now','Recent work & current questions'),('fold-offscreen','offscreen','Rockets, predictions, design & lifting')]:
        body = f'<rect class="surface" width="{width}" height="92"/>'
        body += text(22, 39, title, 25, weight=800, extra='letter-spacing="-0.6"')
        body += text(22, 68, desc, 13, 'muted')
        body += text(width-44, 55, '+', 30, 'orange', 400)
        write(name+suffix,width,92,title,desc,body)
    # Reuses the same split-row proportions as the original contact buttons.
    w = 205 if mobile else 410
    write('action-projects'+suffix,w,94,'All projects','Browse all projects',
          f'<rect class="blue" width="{w}" height="94"/>' +
          text(18 if mobile else 24,57,'all projects',20 if mobile else 24,'on-blue',820) +
          arrow(w-40 if mobile else w-56,35,'#FBF7EF',19 if mobile else 25))


def picture(name, alt, width="100%", align=None):
    alignment = f' align="{align}"' if align else ''
    return f'''<picture>
    <source media="(max-width: 760px)" srcset="assets/{name}-mobile.svg" />
    <img src="assets/{name}.svg" width="{width}"{alignment} alt="{escape(alt, quote=True)}" />
  </picture>'''


def linked(name, alt, href, width="100%"):
    return f'<a href="{escape(href, quote=True)}">{picture(name, alt, width)}</a>'


def build_readme():
    chunks = ['''<!-- SVG artwork and this README are maintained by scripts/build_profile_art.py. -->
<p align="center">
  <picture>
    <source media="(max-width: 760px) and (prefers-color-scheme: dark)" srcset="assets/hero-dark-mobile.svg" />
    <source media="(max-width: 760px) and (prefers-color-scheme: light)" srcset="assets/hero-light-mobile.svg" />
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg" />
    <img src="assets/hero-light.svg" width="100%" alt="Sai — Saicharan Ramineni. Computer Science at UCF, Orlando." />
  </picture>
</p>''',
        picture('profile-intro', 'I work through papers and framework source by building and testing implementations. GPU kernels, small models, and the runtimes beneath them.'),
        linked('heading-work', 'Selected work. Browse all projects.', 'https://saicharanramineni.com/projects'),
    ]
    for item in CARDS:
        if item['id'] == 'upstream-pytorch':
            chunks.append(linked('heading-upstream', 'Upstream contributions. Open the full record.', 'https://saicharanramineni.com/open-source'))
        alt = item['title'] + '. ' + ' '.join(item['desktop'] + item['detail'])
        chunks.append(linked(item['id'], alt, item['href']))
    for name, title, body, alt, href in [
        ('fold-now', 'Right now: recent public work and current questions', 'now', "Sai's latest public change and current research questions.", 'https://github.com/GodlyDonuts?tab=repositories&sort=updated'),
        ('fold-offscreen', 'Offscreen: rockets, predictions, design and lifting', 'offscreen', 'Reusable rockets, the AI race, design, predictions, project names, and lifting.', 'https://saicharanramineni.com/'),
    ]:
        chunks.append('<details>\n  <summary>' + picture(name, title, '92%', 'middle') + '</summary>\n\n' + linked(body, alt, href) + '\n\n</details>')
    for left, right in [
        (('action-email', 'Email Sai', 'mailto:csramineni@gmail.com'), ('action-portfolio', 'Open the live portfolio', 'https://saicharanramineni.com/')),
        (('action-linkedin', 'LinkedIn', 'https://www.linkedin.com/in/saicharan-ramineni/'), ('action-projects', 'All projects', 'https://saicharanramineni.com/projects')),
    ]:
        chunks.append('<p align="center">' + linked(*left, width='49%') + '<!--\n-->' + linked(*right, width='49%') + '</p>')
    (ROOT / 'README.md').write_text('\n\n'.join(chunks) + '\n')


if __name__ == '__main__':
    for mobile in [False, True]:
        for item in CARDS:
            card(item, mobile)
        support_panels(mobile)
    build_readme()
    print('Built the SVG panels and image-led README.')
