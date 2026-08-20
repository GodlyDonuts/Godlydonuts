#!/usr/bin/env python3
"""Refresh the live panel in Sai's GitHub profile."""

from __future__ import annotations

import argparse
import json
import os
import re
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET

API_VERSION = "2022-11-28"
SVG = "http://www.w3.org/2000/svg"
PROFILE_REPOS = {"godlydonuts"}
ET.register_namespace("", SVG)


@dataclass(frozen=True)
class Trace:
    repository: str
    message: str
    observed_at: str


def request_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "GodlyDonuts-profile-renderer",
        "X-GitHub-Api-Version": API_VERSION,
    }
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=20) as response:
        return json.load(response)


def normalize_message(raw: str) -> str:
    lines = [" ".join(line.split()) for line in raw.splitlines() if line.strip()]
    if not lines:
        return "A public change landed"
    message = lines[1] if lines[0].lower().startswith("merge pull request") and len(lines) > 1 else lines[0]
    return re.sub(r"\s*\(#\d+\)$", "", message).strip()[:130] or "A public change landed"


def fetch_trace(user: str) -> Trace:
    encoded_user = urllib.parse.quote(user, safe="")
    repos = request_json(
        f"https://api.github.com/users/{encoded_user}/repos"
        "?type=owner&sort=pushed&direction=desc&per_page=100"
    )
    candidates = [
        repo
        for repo in repos
        if isinstance(repo, dict)
        and not repo.get("fork")
        and not repo.get("archived")
        and str(repo.get("name", "")).lower() not in PROFILE_REPOS
        and repo.get("pushed_at")
    ]
    if not candidates:
        raise ValueError("no eligible public repositories")

    repo = max(candidates, key=lambda item: str(item["pushed_at"]))
    full_name = str(repo["full_name"])
    branch = str(repo.get("default_branch") or "main")
    encoded_repo = "/".join(urllib.parse.quote(part, safe="") for part in full_name.split("/"))
    encoded_branch = urllib.parse.quote(branch, safe="")
    commits = request_json(
        f"https://api.github.com/repos/{encoded_repo}/commits"
        f"?sha={encoded_branch}&author={encoded_user}&per_page=8"
    )
    if not commits:
        commits = request_json(
            f"https://api.github.com/repos/{encoded_repo}/commits?sha={encoded_branch}&per_page=8"
        )
    if not commits:
        raise ValueError(f"no commits returned for {full_name}")

    chosen = next(
        (
            item
            for item in commits
            if not str((item.get("commit") or {}).get("message") or "")
            .splitlines()[0]
            .lower()
            .startswith("merge pull request")
        ),
        commits[0],
    )
    commit = chosen.get("commit") or {}
    author = commit.get("author") or {}
    committer = commit.get("committer") or {}
    return Trace(
        repository=str(repo["name"]),
        message=normalize_message(str(commit.get("message") or "")),
        observed_at=str(committer.get("date") or author.get("date") or repo["pushed_at"]),
    )


def fallback_trace(config: dict) -> Trace:
    fallback = config["fallback"]
    return Trace(
        repository=str(fallback["repository"]),
        message=normalize_message(str(fallback["message"])),
        observed_at=str(fallback["observed_at"]),
    )


def observed_date(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        return parsed.strftime("%Y.%m.%d")
    except ValueError:
        return value[:10].replace("-", ".")


def wrap(text: str, width: int, max_lines: int) -> list[str]:
    lines = textwrap.wrap(
        " ".join(text.split()),
        width=width,
        break_long_words=False,
        break_on_hyphens=False,
    ) or [""]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    return lines


def clip(text: str, max_chars: int) -> str:
    compact = " ".join(text.split())
    if len(compact) <= max_chars:
        return compact
    return compact[: max_chars - 1].rstrip(" ._-") + "…"


def find_id(root: ET.Element, element_id: str) -> ET.Element:
    for element in root.iter():
        if element.get("id") == element_id:
            return element
    raise ValueError(f"missing element with id={element_id!r}")


def set_lines(element: ET.Element, lines: list[str], x: str, dy: int) -> None:
    element.text = "\n    "
    for child in list(element):
        element.remove(child)
    for index, line in enumerate(lines):
        span = ET.SubElement(
            element,
            f"{{{SVG}}}tspan",
            {"x": x, "dy": "0" if index == 0 else str(dy)},
        )
        span.text = line
        span.tail = "\n    "


def render(path: Path, trace: Trace, config: dict, *, mobile: bool) -> bool:
    tree = ET.parse(path)
    root = tree.getroot()
    desc = find_id(root, "desc")
    desc.text = (
        f"Sai's latest public change is in {trace.repository}: {trace.message}. "
        f"He is thinking about {config['rabbit_hole']}."
    )

    find_id(root, "observed-date").text = observed_date(trace.observed_at)
    find_id(root, "repository").text = clip(trace.repository, 22 if mobile else 24)

    if mobile:
        set_lines(find_id(root, "commit"), wrap(trace.message, 31, 2), "46", 25)
        set_lines(find_id(root, "rabbit-hole"), wrap(str(config["rabbit_hole"]), 29, 3), "26", 29)
        set_lines(find_id(root, "current-bet"), wrap(str(config["current_bet"]), 29, 2), "26", 29)
        set_lines(find_id(root, "changed-mind"), wrap(str(config["changed_my_mind"]), 31, 2), "26", 28)
    else:
        set_lines(find_id(root, "commit"), wrap(trace.message, 27, 2), "70", 27)
        set_lines(find_id(root, "rabbit-hole"), wrap(str(config["rabbit_hole"]), 38, 2), "430", 30)
        set_lines(find_id(root, "current-bet"), wrap(str(config["current_bet"]), 35, 2), "430", 30)
        set_lines(find_id(root, "changed-mind"), wrap(str(config["changed_my_mind"]), 34, 2), "430", 27)

    ET.indent(tree, space="  ")
    content = ET.tostring(root, encoding="unicode") + "\n"
    current = path.read_text(encoding="utf-8")
    if current == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="GodlyDonuts")
    parser.add_argument("--config", type=Path, default=Path("data/profile.json"))
    parser.add_argument("--output", type=Path, default=Path("assets"))
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    trace = fallback_trace(config)
    if not args.offline:
        try:
            trace = fetch_trace(args.user)
        except (OSError, ValueError, KeyError, urllib.error.URLError) as exc:
            print(f"warning: using fallback public state: {exc}")

    changed = [
        name
        for name, mobile in (("now.svg", False), ("now-mobile.svg", True))
        if render(args.output / name, trace, config, mobile=mobile)
    ]
    print("updated: " + ", ".join(changed) if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
