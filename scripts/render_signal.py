#!/usr/bin/env python3
"""Render the self-updating signal card used by the GitHub profile README.

The output is deterministic for a given public GitHub state and signal config.
A scheduled workflow polls public activity and commits only when the rendered
card actually changes.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_VERSION = "2022-11-28"
PROFILE_REPO_NAMES = {"godlydonuts"}


@dataclass(frozen=True)
class PublicTrace:
    repository: str
    message: str
    observed_at: str


def _request_json(url: str, token: str | None) -> Any:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GodlyDonuts-profile-signal",
        "X-GitHub-Api-Version": API_VERSION,
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def _fetch_public_trace(user: str, token: str | None) -> PublicTrace:
    encoded_user = urllib.parse.quote(user, safe="")
    repos_url = (
        f"https://api.github.com/users/{encoded_user}/repos"
        "?type=owner&sort=pushed&direction=desc&per_page=100"
    )
    repos = _request_json(repos_url, token)
    if not isinstance(repos, list):
        raise ValueError("GitHub repositories response was not a list")

    candidates = [
        repo
        for repo in repos
        if isinstance(repo, dict)
        and not repo.get("fork", False)
        and not repo.get("archived", False)
        and str(repo.get("name", "")).lower() not in PROFILE_REPO_NAMES
        and repo.get("pushed_at")
    ]
    if not candidates:
        raise ValueError("No eligible public repositories were returned")

    repo = max(candidates, key=lambda item: str(item["pushed_at"]))
    full_name = str(repo["full_name"])
    default_branch = str(repo.get("default_branch") or "main")
    encoded_repo = "/".join(urllib.parse.quote(part, safe="") for part in full_name.split("/"))
    encoded_branch = urllib.parse.quote(default_branch, safe="")
    commits_url = (
        f"https://api.github.com/repos/{encoded_repo}/commits"
        f"?sha={encoded_branch}&per_page=1"
    )
    commits = _request_json(commits_url, token)
    if not isinstance(commits, list) or not commits:
        raise ValueError(f"No commits returned for {full_name}")

    commit = commits[0].get("commit", {})
    raw_message = str(commit.get("message") or "A new trace appeared").splitlines()[0]
    author = commit.get("author") or {}
    committer = commit.get("committer") or {}
    observed_at = str(committer.get("date") or author.get("date") or repo["pushed_at"])

    return PublicTrace(
        repository=str(repo["name"]),
        message=_normalize_message(raw_message),
        observed_at=observed_at,
    )


def _normalize_message(message: str) -> str:
    normalized = " ".join(message.split())
    return normalized[:140] if normalized else "A new trace appeared"


def _format_observed(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        parsed = parsed.astimezone(timezone.utc)
        return parsed.strftime("%Y.%m.%d / %H:%M UTC")
    except ValueError:
        return value[:32]


def _wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(
        text,
        width=width,
        break_long_words=True,
        break_on_hyphens=False,
        replace_whitespace=True,
    ) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines


def _load_config(path: Path) -> dict[str, Any]:
    config = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("Signal config must be a JSON object")
    return config


def _fallback_trace(config: dict[str, Any]) -> PublicTrace:
    fallback = config.get("fallback")
    if not isinstance(fallback, dict):
        raise ValueError("Signal config requires a fallback object")
    return PublicTrace(
        repository=str(fallback.get("repository") or "unknown-orbit"),
        message=_normalize_message(str(fallback.get("message") or "Signal unavailable")),
        observed_at=str(fallback.get("observed_at") or "unknown"),
    )


def _render(trace: PublicTrace, config: dict[str, Any]) -> str:
    question = " ".join(str(config.get("question") or "What is worth building next?").split())
    counterweight = " ".join(
        str(config.get("counterweight") or "Make the claim earn its confidence.").split()
    )

    message_lines = _wrap(trace.message, width=54, max_lines=2)
    question_lines = _wrap(question, width=78, max_lines=2)

    def esc(value: str) -> str:
        return html.escape(value, quote=True)

    message_tspans = "\n".join(
        f'        <tspan x="465" dy="{0 if index == 0 else 27}">{esc(line)}</tspan>'
        for index, line in enumerate(message_lines)
    )
    question_tspans = "\n".join(
        f'        <tspan x="48" dy="{0 if index == 0 else 25}">{esc(line)}</tspan>'
        for index, line in enumerate(question_lines)
    )

    aria = esc(
        f"Live signal. Current orbit {trace.repository}. Latest transmission: "
        f"{trace.message}. Open question: {question}"
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 320" role="img" aria-label="{aria}">
  <defs>
    <linearGradient id="beam" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#f59e0b" stop-opacity="0"/>
      <stop offset="0.5" stop-color="#f59e0b" stop-opacity="0.72"/>
      <stop offset="1" stop-color="#f59e0b" stop-opacity="0"/>
    </linearGradient>
    <filter id="glow" x="-100%" y="-100%" width="300%" height="300%">
      <feGaussianBlur stdDeviation="3.5" result="blur"/>
      <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
    <clipPath id="clip"><rect width="1200" height="320" rx="22"/></clipPath>
    <style>
      .bg {{ fill: #0a0d12; }}
      .line {{ stroke: #303846; }}
      .grid {{ stroke: #1d232d; }}
      .primary {{ fill: #f5f3ee; }}
      .secondary {{ fill: #939cab; }}
      .quiet {{ fill: #5f6877; }}
      .accent {{ fill: #f59e0b; }}
      text {{ font-family: Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
      .mono {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }}
      @media (prefers-color-scheme: light) {{
        .bg {{ fill: #f4f0e8; }}
        .line {{ stroke: #c9c0b1; }}
        .grid {{ stroke: #ded7ca; }}
        .primary {{ fill: #111318; }}
        .secondary {{ fill: #5d6570; }}
        .quiet {{ fill: #8f887e; }}
      }}
      @media (prefers-reduced-motion: reduce) {{ .motion {{ display: none; }} }}
    </style>
  </defs>

  <g clip-path="url(#clip)">
    <rect class="bg" width="1200" height="320"/>
    <g class="grid" stroke-width="1" opacity="0.58">
      <path d="M0 64.5H1200M0 176.5H1200M0 256.5H1200"/>
      <path d="M400.5 0V320M800.5 0V320"/>
    </g>

    <rect class="motion" x="-220" y="0" width="220" height="320" fill="url(#beam)" opacity="0.34">
      <animate attributeName="x" values="-220;1200" dur="8s" repeatCount="indefinite"/>
    </rect>

    <circle cx="48" cy="38" r="4" class="accent" filter="url(#glow)">
      <animate class="motion" attributeName="opacity" values="0.3;1;0.3" dur="1.6s" repeatCount="indefinite"/>
    </circle>
    <text x="64" y="43" class="mono accent" font-size="11" letter-spacing="2.2">LIVE SIGNAL / PUBLIC TRACE</text>
    <text x="1152" y="43" text-anchor="end" class="mono quiet" font-size="10" letter-spacing="1.35">THIS PANEL CHANGES WHEN I DO</text>

    <text x="48" y="94" class="mono quiet" font-size="10" letter-spacing="2">CURRENT ORBIT</text>
    <text x="48" y="139" class="primary" font-size="31" font-weight="650">{esc(trace.repository)}</text>
    <text x="48" y="165" class="mono secondary" font-size="10" letter-spacing="1.2">OBSERVED {esc(_format_observed(trace.observed_at))}</text>

    <text x="465" y="94" class="mono quiet" font-size="10" letter-spacing="2">LATEST TRANSMISSION</text>
    <text x="465" y="128" class="secondary" font-size="20" font-weight="500">
{message_tspans}
    </text>

    <g transform="translate(1080 105)" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" opacity="0.88">
      <path d="M0 30h8l8-18 10 38 10-25 10 10h10l8-21 9 34 10-18h17"/>
      <path class="motion" d="M0 30h8l8-18 10 38 10-25 10 10h10l8-21 9 34 10-18h17" filter="url(#glow)">
        <animate attributeName="stroke-dasharray" values="0 180;90 90;180 0" dur="3.6s" repeatCount="indefinite"/>
      </path>
    </g>

    <text x="48" y="211" class="mono quiet" font-size="10" letter-spacing="2">OPEN QUESTION</text>
    <text x="48" y="241" class="primary" font-size="18" font-weight="530">
{question_tspans}
    </text>
    <text x="1152" y="288" text-anchor="end" class="mono secondary" font-size="10" letter-spacing="1.15">{esc(counterweight.upper())}</text>

    <rect x="0.75" y="0.75" width="1198.5" height="318.5" rx="21.25" fill="none" class="line" stroke-width="1.5"/>
  </g>
</svg>
'''


def _write_if_changed(path: Path, content: str) -> bool:
    current = path.read_text(encoding="utf-8") if path.exists() else None
    if current == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="GodlyDonuts")
    parser.add_argument("--config", type=Path, default=Path("data/signal.json"))
    parser.add_argument("--output", type=Path, default=Path("assets/signal.svg"))
    parser.add_argument(
        "--offline",
        action="store_true",
        help="Render from the deterministic fallback without contacting GitHub.",
    )
    args = parser.parse_args()

    config = _load_config(args.config)
    trace = _fallback_trace(config)

    if not args.offline:
        try:
            trace = _fetch_public_trace(args.user, os.environ.get("GITHUB_TOKEN"))
        except (OSError, ValueError, KeyError, urllib.error.URLError) as exc:
            print(f"warning: using fallback public trace: {exc}", file=sys.stderr)

    changed = _write_if_changed(args.output, _render(trace, config))
    print(f"{'updated' if changed else 'unchanged'}: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
