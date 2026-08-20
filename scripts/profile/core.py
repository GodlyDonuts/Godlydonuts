from __future__ import annotations

import html
import json
import random
import re
import textwrap
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Iterable

API_VERSION = "2022-11-28"
PROFILE_REPOS = {"godlydonuts"}


@dataclass(frozen=True)
class PublicTrace:
    repository: str
    message: str
    observed_at: str


PALETTES = {
    "light": {
        "bg": "#eee6d7",
        "paper": "#f8f3ea",
        "paper2": "#e5dccd",
        "ink": "#11100e",
        "muted": "#675f54",
        "line": "#bdb09d",
        "orange": "#d85a2a",
        "blue": "#0067d9",
        "inverse": "#11100e",
        "inverse_ink": "#f8f3ea",
    },
    "dark": {
        "bg": "#0b0a09",
        "paper": "#151310",
        "paper2": "#201c18",
        "ink": "#eee7dc",
        "muted": "#9f9688",
        "line": "#3a342d",
        "orange": "#ff6b2b",
        "blue": "#42a5ff",
        "inverse": "#eee7dc",
        "inverse_ink": "#0b0a09",
    },
}


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def request_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GodlyDonuts-profile-print",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def normalize_commit_message(raw: str) -> str:
    lines = [" ".join(line.split()) for line in raw.splitlines() if line.strip()]
    if not lines:
        return "New work landed"
    if lines[0].lower().startswith("merge pull request") and len(lines) > 1:
        message = lines[1]
    else:
        message = lines[0]
    message = re.sub(r"\s*\(#\d+\)$", "", message).strip()
    return message[:150] or "New work landed"


def fetch_public_trace(user: str, token: str | None) -> PublicTrace:
    encoded_user = urllib.parse.quote(user, safe="")
    repos = request_json(
        f"https://api.github.com/users/{encoded_user}/repos"
        "?type=owner&sort=pushed&direction=desc&per_page=100",
        token,
    )
    if not isinstance(repos, list):
        raise ValueError("repositories response was not a list")

    candidates = [
        repo
        for repo in repos
        if isinstance(repo, dict)
        and not repo.get("fork", False)
        and not repo.get("archived", False)
        and str(repo.get("name", "")).lower() not in PROFILE_REPOS
        and repo.get("pushed_at")
    ]
    if not candidates:
        raise ValueError("no eligible public repositories")

    repo = max(candidates, key=lambda item: str(item["pushed_at"]))
    full_name = str(repo["full_name"])
    branch = str(repo.get("default_branch") or "main")
    encoded_repo = "/".join(
        urllib.parse.quote(part, safe="") for part in full_name.split("/")
    )
    encoded_branch = urllib.parse.quote(branch, safe="")
    commits = request_json(
        f"https://api.github.com/repos/{encoded_repo}/commits"
        f"?sha={encoded_branch}&author={encoded_user}&per_page=8",
        token,
    )
    if not isinstance(commits, list) or not commits:
        commits = request_json(
            f"https://api.github.com/repos/{encoded_repo}/commits"
            f"?sha={encoded_branch}&per_page=8",
            token,
        )
    if not isinstance(commits, list) or not commits:
        raise ValueError(f"no commits returned for {full_name}")

    chosen = commits[0]
    for candidate in commits:
        raw = str((candidate.get("commit") or {}).get("message") or "")
        if raw and not raw.splitlines()[0].lower().startswith("merge pull request"):
            chosen = candidate
            break

    commit = chosen.get("commit") or {}
    author = commit.get("author") or {}
    committer = commit.get("committer") or {}
    return PublicTrace(
        repository=str(repo["name"]),
        message=normalize_commit_message(str(commit.get("message") or "")),
        observed_at=str(
            committer.get("date") or author.get("date") or repo.get("pushed_at") or ""
        ),
    )


def fallback_trace(config: dict[str, Any]) -> PublicTrace:
    fallback = config.get("fallback")
    if not isinstance(fallback, dict):
        raise ValueError("profile config requires fallback")
    return PublicTrace(
        repository=str(fallback.get("repository") or "shohin-ettr"),
        message=normalize_commit_message(
            str(fallback.get("message") or "New work landed")
        ),
        observed_at=str(fallback.get("observed_at") or ""),
    )


def observed(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(
            timezone.utc
        )
        return parsed.strftime("%d %b %Y / %H:%M UTC").upper()
    except ValueError:
        return value[:36].upper()


def wrap(value: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(
        " ".join(value.split()),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines


def text(
    x: float,
    y: float,
    lines: str | Iterable[str],
    *,
    cls: str,
    size: int,
    line_height: int | None = None,
    weight: int | str | None = None,
    anchor: str | None = None,
    letter_spacing: float | None = None,
    rotate: float | None = None,
    fill: str | None = None,
) -> str:
    if isinstance(lines, str):
        lines = [lines]
    line_height = line_height or int(size * 1.2)
    attrs = [f'x="{x}"', f'y="{y}"', f'class="{cls}"', f'font-size="{size}"']
    if weight is not None:
        attrs.append(f'font-weight="{weight}"')
    if anchor is not None:
        attrs.append(f'text-anchor="{anchor}"')
    if letter_spacing is not None:
        attrs.append(f'letter-spacing="{letter_spacing}"')
    if rotate is not None:
        attrs.append(f'transform="rotate({rotate} {x} {y})"')
    if fill is not None:
        attrs.append(f'fill="{fill}"')
    body = "".join(
        f'<tspan x="{x}" dy="{0 if i == 0 else line_height}">{esc(line)}</tspan>'
        for i, line in enumerate(lines)
    )
    return f"<text {' '.join(attrs)}>{body}</text>"


def grain(width: int, height: int, theme: str, ink: str, count: int) -> str:
    rng = random.Random(3011 if theme == "light" else 3012)
    marks = []
    for _ in range(count):
        x = rng.randrange(12, width - 12)
        y = rng.randrange(12, height - 12)
        r = rng.choice([0.55, 0.75, 0.95, 1.2])
        opacity = rng.choice([0.06, 0.08, 0.10, 0.13])
        marks.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{ink}" opacity="{opacity}"/>'
        )
    return "".join(marks)


def style(p: dict[str, str]) -> str:
    return f"""
      .serif {{ font-family: Georgia, \"Times New Roman\", serif; }}
      .sans {{ font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; }}
      .mono {{ font-family: \"SFMono-Regular\", Consolas, \"Liberation Mono\", Menlo, monospace; }}
      .ink {{ fill: {p['ink']}; }} .muted {{ fill: {p['muted']}; }}
      .orange {{ fill: {p['orange']}; }} .blue {{ fill: {p['blue']}; }}
      @media (prefers-reduced-motion: reduce) {{ .motion {{ display: none; }} }}
    """


def crop_marks(width: int, height: int, p: dict[str, str]) -> str:
    return f"""
      <g stroke="{p['line']}" stroke-width="2">
        <path d="M24 56V24H56 M{width - 56} 24H{width - 24}V56 M24 {height - 56}V{height - 24}H56 M{width - 56} {height - 24}H{width - 24}V{height - 56}"/>
        <path d="M{width / 2} 24v25 M{width / 2} {height - 49}v25"/>
      </g>
    """


def eclipse(cx: int, cy: int, radius: int, p: dict[str, str], bg: str) -> str:
    return f"""
      <g transform="translate({cx} {cy})">
        <circle class="motion" cx="10" cy="0" r="{radius}" fill="none" stroke="{p['blue']}" stroke-width="{max(8, radius // 16)}" opacity="0.82">
          <animate attributeName="cx" values="10;17;6;10" dur="8s" repeatCount="indefinite"/>
        </circle>
        <circle r="{radius}" fill="{p['orange']}"/>
        <circle cx="{-int(radius * 0.17)}" r="{radius}" fill="{bg}" stroke="{p['ink']}" stroke-width="4"/>
        <path d="M{-radius - 21} 0H{radius + 21}M0 {-radius - 21}V{radius + 21}" stroke="{p['line']}" stroke-width="1.5" stroke-dasharray="8 10"/>
      </g>
    """


def question_card(
    x: int,
    y: int,
    w: int,
    h: int,
    index: str,
    tag: str,
    lines: list[str],
    accent: str,
    p: dict[str, str],
    rotate: float = 0,
    font_size: int = 27,
) -> str:
    cx, cy = x + w / 2, y + h / 2
    tag_color = "orange" if accent == p["orange"] else "blue"
    return f"""
      <g transform="rotate({rotate} {cx} {cy})">
        <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{p['paper']}" stroke="{p['line']}" stroke-width="2"/>
        <rect x="{x}" y="{y}" width="9" height="{h}" fill="{accent}"/>
        {text(x + 28, y + 38, index, cls='mono muted', size=14, weight=800)}
        {text(x + w - 24, y + 38, tag, cls=f'mono {tag_color}', size=12, weight=800, anchor='end')}
        {text(x + 28, y + 92, lines, cls='sans ink', size=font_size, line_height=font_size + 8, weight=650)}
        <path d="M{x + 28} {y + h - 30}H{x + w - 28}" stroke="{p['line']}" stroke-width="1.5" stroke-dasharray="5 7"/>
      </g>
    """


def info_box(
    x: int,
    y: int,
    w: int,
    h: int,
    label: str,
    lines: list[str],
    p: dict[str, str],
    accent_class: str,
    size: int,
    inverse: bool = False,
) -> str:
    bg = p["inverse"] if inverse else p["paper"]
    fg = p["inverse_ink"] if inverse else p["ink"]
    border = p["inverse"] if inverse else p["line"]
    accent = p[accent_class]
    return f"""
      <g>
        <rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{bg}" stroke="{border}" stroke-width="2"/>
        <rect x="{x}" y="{y}" width="{w}" height="7" fill="{accent}"/>
        {text(x + 26, y + 43, label, cls='mono', size=13, weight=800, letter_spacing=0.45, fill=accent)}
        {text(x + 26, y + 91, lines, cls='serif', size=size, line_height=size + 8, weight=700, fill=fg)}
      </g>
    """


