from __future__ import annotations

from typing import Any

from .copy import authored_copy
from .core import (
    PALETTES, PublicTrace, crop_marks, eclipse, esc, grain, info_box,
    observed, question_card, style, text, wrap,
)

def render_desktop(theme: str, trace: PublicTrace, config: dict[str, Any]) -> str:
    p = PALETTES[theme]
    c = authored_copy(theme)
    width, height = 1200, 3820
    rabbit = wrap(str(config["rabbit_hole"]), 32, 4)
    bet = wrap(str(config["current_bet"]), 38, 4)
    changed = wrap(str(config["changed_my_mind"]), 35, 4)
    commit = wrap(trace.message, 39, 3)

    cards = [
        ("01", "CURRENT", ["Can a model learn when its", "first answer is wrong—", "without being told?"], p["orange"], -0.7),
        ("02", "ARGUING WITH MYSELF", ["Does America's compute lead", "matter if Chinese labs keep", "finding better algorithms?"], p["blue"], 0.55),
        ("03", "AGENCY", ["What does a computer become", "when the interface", "disappears?"], p["blue"], -0.35),
        ("04", "PROBABLY TOO HARD", ["Can one ordinary camera turn", "a room into live", "geometry?"], p["orange"], 0.8),
        ("05", "TASTE IS TECHNICAL", ["Why do technically correct", "products still feel", "dead?"], p["orange"], 0.35),
        ("06", "KEEPS COMING BACK", ["How small can intelligence get", "before it stops feeling like", "intelligence?"], p["blue"], -0.65),
    ]
    positions = [(56, 1260), (618, 1260), (56, 1530), (618, 1530), (56, 1800), (618, 1800)]
    card_markup = "".join(
        question_card(x, y, 526, 232, i, tag, lines, accent, p, rot)
        for (i, tag, lines, accent, rot), (x, y) in zip(cards, positions)
    )

    aria = esc(
        "Sai's profile. A responsive editorial page about the questions he obsesses over, "
        "how he works, what he thinks about offscreen, and what he is doing right now."
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{aria}">
  <defs><style>{style(p)}</style></defs>
  <rect width="{width}" height="{height}" fill="{p['bg']}"/>
  {grain(width, height, theme, p['ink'], 260)}
  {crop_marks(width, height, p)}
  <rect class="motion" x="0" y="-8" width="{width}" height="6" fill="{p['blue']}" opacity="0.16"><animate attributeName="y" values="-8;{height + 8}" dur="21s" repeatCount="indefinite"/></rect>

  {text(58, 76, f"SAI / PROFILE ISSUE 05 / {c['copy_label']}", cls='mono muted', size=15, weight=800, letter_spacing=0.7)}
  {text(1142, 76, 'LAST EDITED BY A HUMAN. UPDATED BY A BOT.', cls='mono muted', size=13, weight=800, anchor='end', letter_spacing=0.25)}
  {eclipse(917, 290, 205, p, p['bg'])}
  {text(58, 180, ['I FOLLOW', 'QUESTIONS'], cls='serif ink', size=94, line_height=91, weight=700)}
  {text(58, 378, ['PAST THE POINT', 'WHERE THEY STAY'], cls='serif ink', size=74, line_height=77, weight=700)}
  {text(58, 555, 'REASONABLE.', cls='serif orange', size=104, weight=700)}
  {text(676, 570, c['top_note'], cls='sans blue', size=22, weight=650, rotate=-2.2)}
  <path d="M670 581c78-9 135 9 279-3" fill="none" stroke="{p['blue']}" stroke-width="3" stroke-linecap="round"/>
  {text(58, 642, 'SAICHARAN RAMINENI / CS @ UCF / BUILDS TOO MUCH', cls='mono muted', size=16, weight=800, letter_spacing=0.45)}
  <path d="M58 674H1142" stroke="{p['ink']}" stroke-width="3"/>

  {text(58, 755, 'NOT A BIO', cls='mono orange', size=17, weight=800, letter_spacing=0.6)}
  {text(58, 808, c['bio'], cls='serif ink', size=31, line_height=39, weight=700)}
  {text(58, 981, c['bio_sub'], cls='sans muted', size=20, line_height=29, weight=550)}
  <g transform="rotate(-1.1 923 894)">
    <rect x="718" y="748" width="424" height="292" fill="{p['inverse']}"/>
    {text(748, 790, 'BAD HABIT', cls='mono', size=13, weight=800, letter_spacing=0.55, fill=p['inverse_ink'])}
    {text(748, 842, ['I start with the version', 'I actually want.', 'Then I learn whatever I need', 'to make it exist.'], cls='serif', size=27, line_height=36, weight=700, fill=p['inverse_ink'])}
    <path d="M748 1000h202" stroke="{p['orange']}" stroke-width="9"/>
  </g>
  {text(697, 1063, c['habit_note'], cls='sans blue', size=18, weight=650, rotate=1.2)}

  <path d="M58 1136H1142" stroke="{p['line']}" stroke-width="2"/>
  {text(58, 1195, 'THINGS I THINK ABOUT TOO MUCH', cls='serif ink', size=51, weight=700)}
  {card_markup}
  {text(58, 2081, c['list_note'], cls='sans blue', size=20, weight=650, rotate=-1.2)}
  <path d="M56 2093c96-9 170 11 322-2" fill="none" stroke="{p['blue']}" stroke-width="3" stroke-linecap="round"/>

  <path d="M58 2144H1142" stroke="{p['ink']}" stroke-width="3"/>
  {text(58, 2218, 'HOW I ACTUALLY WORK', cls='serif ink', size=55, weight=700)}
  {text(58, 2264, 'THE ACTUAL LOOP', cls='mono orange', size=14, weight=800, letter_spacing=0.55)}
  <g transform="translate(58 2323)">
    <path d="M0 58H1084" stroke="{p['line']}" stroke-width="3"/>
    <g fill="{p['bg']}" stroke="{p['ink']}" stroke-width="3">
      <circle cx="30" cy="58" r="27"/><circle cx="235" cy="58" r="27"/><circle cx="440" cy="58" r="27"/>
      <circle cx="645" cy="58" r="27"/><circle cx="850" cy="58" r="27"/><circle cx="1054" cy="58" r="27"/>
    </g>
    {text(30, 64, '1', cls='mono ink', size=18, weight=800, anchor='middle')}{text(235, 64, '2', cls='mono ink', size=18, weight=800, anchor='middle')}{text(440, 64, '3', cls='mono ink', size=18, weight=800, anchor='middle')}{text(645, 64, '4', cls='mono ink', size=18, weight=800, anchor='middle')}{text(850, 64, '5', cls='mono ink', size=18, weight=800, anchor='middle')}{text(1054, 64, '6', cls='mono ink', size=18, weight=800, anchor='middle')}
    {text(30, 129, 'OBSESS', cls='mono orange', size=15, weight=800, anchor='middle')}{text(235, 129, 'BUILD', cls='mono blue', size=15, weight=800, anchor='middle')}{text(440, 129, 'MEASURE', cls='mono orange', size=15, weight=800, anchor='middle')}{text(645, 129, 'BREAK', cls='mono blue', size=15, weight=800, anchor='middle')}{text(850, 129, 'DELETE', cls='mono orange', size=15, weight=800, anchor='middle')}{text(1054, 129, 'REBUILD', cls='mono blue', size=15, weight=800, anchor='middle')}
    {text(30, 164, ['question refuses', 'to leave'], cls='sans muted', size=14, line_height=20, anchor='middle')}{text(235, 164, ['make it', 'concrete'], cls='sans muted', size=14, line_height=20, anchor='middle')}{text(440, 164, ['find the', 'control'], cls='sans muted', size=14, line_height=20, anchor='middle')}{text(645, 164, ['look for the', 'embarrassing failure'], cls='sans muted', size=14, line_height=20, anchor='middle')}{text(850, 164, ['even if', 'I loved it'], cls='sans muted', size=14, line_height=20, anchor='middle')}{text(1054, 164, ['now I know', 'more'], cls='sans muted', size=14, line_height=20, anchor='middle')}
  </g>
  <g transform="translate(58 2594)">
    <rect width="1084" height="263" fill="{p['paper']}" stroke="{p['line']}" stroke-width="2"/>
    <path d="M542 0V263" stroke="{p['line']}" stroke-width="2"/>
    {text(31, 49, c['candid_left'], cls='sans ink', size=27, line_height=52, weight=600)}
    {text(575, 49, c['candid_right'], cls='sans ink', size=27, line_height=52, weight=600)}
    <path d="M31 222h158" stroke="{p['orange']}" stroke-width="8"/><path d="M575 222h211" stroke="{p['blue']}" stroke-width="8"/>
  </g>

  <path d="M58 2928H1142" stroke="{p['ink']}" stroke-width="3"/>
  {text(58, 3002, 'RIGHT NOW', cls='serif ink', size=55, weight=700)}
  {text(1142, 2996, c['still_editing'], cls='sans blue', size=20, weight=650, anchor='end', rotate=-1)}
  {info_box(58, 3054, 526, 322, 'LAST THING I TOUCHED', [trace.repository, *commit, observed(trace.observed_at)], p, 'orange', 29, inverse=True)}
  {info_box(614, 3054, 528, 322, 'CURRENT RABBIT HOLE', rabbit, p, 'blue', 28)}
  {info_box(58, 3404, 526, 260, 'CURRENT BET', bet, p, 'blue', 26)}
  {info_box(614, 3404, 528, 260, 'CHANGED MY MIND ABOUT', changed, p, 'orange', 26)}
  {text(58, 3719, ['OFFSCREEN  /  ' + c['offscreen'][0]], cls='mono muted', size=14, weight=800, letter_spacing=0.2)}
  {text(58, 3768, c['closing'], cls='serif ink', size=29, line_height=37, weight=700)}
  {text(1142, 3787, '— SAI', cls='mono orange', size=16, weight=800, anchor='end', letter_spacing=0.7)}
</svg>
'''


def render_mobile(theme: str, trace: PublicTrace, config: dict[str, Any]) -> str:
    p = PALETTES[theme]
    c = authored_copy(theme)
    width, height = 720, 5860
    rabbit = wrap(str(config["rabbit_hole"]), 29, 5)
    bet = wrap(str(config["current_bet"]), 30, 5)
    changed = wrap(str(config["changed_my_mind"]), 29, 5)
    commit = wrap(trace.message, 31, 4)

    questions = [
        ("01", "CURRENT", ["Can a model learn when its first", "answer is wrong—without being told?"], p["orange"]),
        ("02", "ARGUING WITH MYSELF", ["Does America's compute lead matter", "if Chinese labs keep finding", "better algorithms?"], p["blue"]),
        ("03", "AGENCY", ["What does a computer become", "when the interface disappears?"], p["blue"]),
        ("04", "PROBABLY TOO HARD", ["Can one ordinary camera turn", "a room into live geometry?"], p["orange"]),
        ("05", "TASTE IS TECHNICAL", ["Why do technically correct products", "still feel dead?"], p["orange"]),
        ("06", "KEEPS COMING BACK", ["How small can intelligence get before", "it stops feeling like intelligence?"], p["blue"]),
    ]
    card_y = [1760, 2040, 2350, 2630, 2910, 3190]
    cards = "".join(
        question_card(38, y, 644, 238, i, tag, lines, accent, p, 0, font_size=27)
        for (i, tag, lines, accent), y in zip(questions, card_y)
    )

    aria = esc(
        "Sai's mobile profile. A personal editorial page about the questions he obsesses over, "
        "how he works, and what he is doing right now."
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="{aria}">
  <defs><style>{style(p)}</style></defs>
  <rect width="{width}" height="{height}" fill="{p['bg']}"/>
  {grain(width, height, theme, p['ink'], 240)}
  {crop_marks(width, height, p)}
  <rect class="motion" x="0" y="-8" width="{width}" height="5" fill="{p['blue']}" opacity="0.15"><animate attributeName="y" values="-8;{height + 8}" dur="24s" repeatCount="indefinite"/></rect>

  {text(38, 68, f"SAI / ISSUE 05 / {c['copy_label']}", cls='mono muted', size=14, weight=800, letter_spacing=0.5)}
  {eclipse(585, 250, 125, p, p['bg'])}
  {text(38, 168, ['I FOLLOW', 'QUESTIONS'], cls='serif ink', size=78, line_height=76, weight=700)}
  {text(38, 342, ['PAST THE POINT', 'WHERE THEY STAY'], cls='serif ink', size=53, line_height=59, weight=700)}
  {text(38, 485, 'REASONABLE.', cls='serif orange', size=76, weight=700)}
  {text(302, 540, c['top_note'], cls='sans blue', size=18, weight=650, rotate=-1.6)}
  <path d="M300 552c87-9 166 10 342-2" fill="none" stroke="{p['blue']}" stroke-width="3" stroke-linecap="round"/>
  {text(38, 608, 'SAICHARAN RAMINENI / CS @ UCF / BUILDS TOO MUCH', cls='mono muted', size=13, weight=800)}
  <path d="M38 642H682" stroke="{p['ink']}" stroke-width="3"/>

  {text(38, 718, 'NOT A BIO', cls='mono orange', size=15, weight=800)}
  {text(38, 767, c['bio'], cls='serif ink', size=30, line_height=39, weight=700)}
  {text(38, 948, c['bio_sub'], cls='sans muted', size=19, line_height=28, weight=550)}
  <g transform="rotate(-0.7 360 1230)">
    <rect x="38" y="1056" width="644" height="330" fill="{p['inverse']}"/>
    {text(68, 1101, 'BAD HABIT', cls='mono', size=13, weight=800, fill=p['inverse_ink'])}
    {text(68, 1163, ['I start with the version I actually want.', 'Then I learn whatever I need', 'to make it exist.'], cls='serif', size=31, line_height=43, weight=700, fill=p['inverse_ink'])}
    <path d="M68 1334h245" stroke="{p['orange']}" stroke-width="9"/>
  </g>
  {text(271, 1428, c['habit_note'], cls='sans blue', size=17, weight=650, rotate=1)}

  <path d="M38 1500H682" stroke="{p['line']}" stroke-width="2"/>
  {text(38, 1571, ['THINGS I THINK', 'ABOUT TOO MUCH'], cls='serif ink', size=48, line_height=51, weight=700)}
  {cards}
  {text(38, 3474, c['list_note'], cls='sans blue', size=18, weight=650, rotate=-1)}
  <path d="M38 3488c114-9 190 9 338-2" fill="none" stroke="{p['blue']}" stroke-width="3"/>

  <path d="M38 3550H682" stroke="{p['ink']}" stroke-width="3"/>
  {text(38, 3622, ['HOW I', 'ACTUALLY WORK'], cls='serif ink', size=52, line_height=54, weight=700)}
  {text(38, 3750, 'OBSESS → BUILD → MEASURE → BREAK → DELETE → REBUILD', cls='mono orange', size=13, weight=800)}
  <g transform="translate(38 3812)">
    <rect width="644" height="478" fill="{p['paper']}" stroke="{p['line']}" stroke-width="2"/>
    {text(27, 52, c['candid_left'], cls='sans ink', size=26, line_height=55, weight=600)}
    <path d="M27 229H617" stroke="{p['line']}" stroke-width="2"/>
    {text(27, 284, c['candid_right'], cls='sans ink', size=26, line_height=55, weight=600)}
    <path d="M27 438h166" stroke="{p['orange']}" stroke-width="8"/><path d="M424 438h193" stroke="{p['blue']}" stroke-width="8"/>
  </g>

  <path d="M38 4366H682" stroke="{p['ink']}" stroke-width="3"/>
  {text(38, 4438, 'RIGHT NOW', cls='serif ink', size=54, weight=700)}
  {text(682, 4433, c['still_editing'], cls='sans blue', size=18, weight=650, anchor='end')}
  {info_box(38, 4492, 644, 360, 'LAST THING I TOUCHED', [trace.repository, *commit, observed(trace.observed_at)], p, 'orange', 29, inverse=True)}
  {info_box(38, 4882, 644, 310, 'CURRENT RABBIT HOLE', rabbit, p, 'blue', 28)}
  {info_box(38, 5222, 310, 360, 'CURRENT BET', bet, p, 'blue', 24)}
  {info_box(372, 5222, 310, 360, 'CHANGED MY MIND ABOUT', changed, p, 'orange', 24)}
  {text(38, 5636, ['OFFSCREEN', *c['offscreen']], cls='mono muted', size=13, line_height=22, weight=800)}
  {text(38, 5702, c['closing'], cls='serif ink', size=27, line_height=36, weight=700)}
  {text(682, 5810, '— SAI', cls='mono orange', size=15, weight=800, anchor='end')}
</svg>
'''


def render_nav(label: str, index: str, accent: str) -> str:
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 96" role="img" aria-label="{esc(label)}">
  <style>
    .bg {{ fill: #eee6d7; }} .ink {{ fill: #11100e; }} .muted {{ fill: #675f54; }}
    @media (prefers-color-scheme: dark) {{ .bg {{ fill: #0b0a09; }} .ink {{ fill: #eee7dc; }} .muted {{ fill: #9f9688; }} }}
    text {{ font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    .mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}
  </style>
  <rect class="bg" x="1" y="1" width="418" height="94" stroke="{accent}" stroke-width="2"/>
  <text x="19" y="28" class="mono muted" font-size="12" font-weight="700">{esc(index)}</text>
  <text x="19" y="68" class="ink" font-size="22" font-weight="750">{esc(label)}</text>
  <path d="M365 58h28m-10-10 10 10-10 10" fill="none" stroke="{accent}" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
</svg>
'''


