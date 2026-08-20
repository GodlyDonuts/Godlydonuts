#!/usr/bin/env python3
"""Render Sai's GitHub profile as four authored responsive editions."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from profile.core import fallback_trace, fetch_public_trace
from profile.layout import render_desktop, render_mobile, render_nav


def write_if_changed(path: Path, content: str) -> bool:
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user", default="GodlyDonuts")
    parser.add_argument("--config", type=Path, default=Path("data/profile.json"))
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    if not isinstance(config, dict):
        raise ValueError("profile config must be an object")
    for key in ("rabbit_hole", "current_bet", "changed_my_mind"):
        if not str(config.get(key, "")).strip():
            raise ValueError(f"profile config requires {key}")

    trace = fallback_trace(config)
    if not args.offline:
        try:
            trace = fetch_public_trace(args.user, os.environ.get("GITHUB_TOKEN"))
        except (OSError, ValueError, KeyError, urllib.error.URLError) as exc:
            print(f"warning: using fallback public state: {exc}", file=sys.stderr)

    outputs = {
        Path("assets/profile-light.svg"): render_desktop("light", trace, config),
        Path("assets/profile-dark.svg"): render_desktop("dark", trace, config),
        Path("assets/profile-light-mobile.svg"): render_mobile("light", trace, config),
        Path("assets/profile-dark-mobile.svg"): render_mobile("dark", trace, config),
        Path("assets/nav-portfolio.svg"): render_nav("PORTFOLIO", "01", "#d85a2a"),
        Path("assets/nav-repositories.svg"): render_nav("REPOSITORIES", "02", "#0067d9"),
        Path("assets/nav-email.svg"): render_nav("EMAIL", "03", "#d85a2a"),
        Path("assets/nav-idea.svg"): render_nav("STRANGE IDEA", "04", "#0067d9"),
    }
    changed = [str(path) for path, content in outputs.items() if write_if_changed(path, content)]
    print("updated: " + ", ".join(changed) if changed else "unchanged")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
