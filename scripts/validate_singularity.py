#!/usr/bin/env python3
"""Decode delivered profile media and verify its README picture routing.

CI checks every encoded frame, rather than rerendering an expensive movie.
Coalesced holds are allowed outside the active choreography. The active movie
must retain its timing and visibly change at several independent points.
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from time import perf_counter
from urllib.parse import urlsplit

import numpy as np
from PIL import Image, features


ROOT = Path(__file__).resolve().parents[1]
EXPECTED_DURATION_MS = 18_000
ACTIVE_MS = (2_500, 15_500)
MOTION_SAMPLES_MS = (2_800, 5_500, 9_000, 12_000, 15_000)
VARIANTS = {
    "desktop": ((1120, 700), "singularity", 6 * 1024 * 1024),
    "mobile": ((640, 860), "singularity-mobile", 5 * 1024 * 1024),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


class Pictures(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.pictures: list[list[tuple[str, dict[str, str | None]]]] = []
        self.current: list[tuple[str, dict[str, str | None]]] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "picture":
            require(self.current is None, "README contains nested picture elements")
            self.current = []
        elif self.current is not None and tag in {"source", "img"}:
            self.current.append((tag, dict(attrs)))

    def handle_endtag(self, tag):
        if tag == "picture":
            require(self.current is not None, "Unmatched picture closing tag")
            self.pictures.append(self.current)
            self.current = None


def local_path(root: Path, url: str) -> Path:
    parts = urlsplit(url)
    require(not parts.scheme and not parts.netloc,
            f"Primary profile media must be repository-local: {url}")
    path = (root / parts.path.lstrip("/")).resolve()
    require(path.is_relative_to(root), f"Image path leaves the repository: {url}")
    require(path.is_file(), f"Referenced image is missing: {url}")
    return path


def source_path(root: Path, attrs: dict[str, str | None]) -> Path:
    srcset = attrs.get("srcset") or ""
    require(bool(srcset), "A picture source has no srcset")
    candidates = [part.strip().split() for part in srcset.split(",")]
    require(len(candidates) == 1 and len(candidates[0]) == 1,
            f"Use one unambiguous image per art-directed source: {srcset}")
    return local_path(root, candidates[0][0])


def media_matches(media: str, width: int, reduce_motion: bool) -> bool:
    """Evaluate the standard media-query subset used by this picture."""
    if not media.strip():
        return True
    terms = re.split(r"\s+and\s+", media.strip(), flags=re.IGNORECASE)
    matches = []
    for term in terms:
        motion = re.fullmatch(
            r"\(\s*prefers-reduced-motion\s*:\s*(reduce|no-preference)\s*\)",
            term, re.IGNORECASE)
        width_term = re.fullmatch(
            r"\(\s*(max|min)-width\s*:\s*(\d+(?:\.\d+)?)px\s*\)",
            term, re.IGNORECASE)
        if motion:
            matches.append(reduce_motion == (motion[1].lower() == "reduce"))
        elif width_term:
            threshold = float(width_term[2])
            matches.append(width <= threshold if width_term[1].lower() == "max"
                           else width >= threshold)
        else:
            raise ValueError(f"Unsupported or malformed picture media query: {media}")
    return all(matches)


def validate_readme(root: Path) -> dict:
    body = (root / "README.md").read_text(encoding="utf-8")
    require(not re.search(r"singularity(?:-mobile)?\.svg", body),
            "README still references the old live SVG animation")
    parser = Pictures()
    parser.feed(body)
    require(parser.current is None, "README contains an unclosed picture")
    relevant = [picture for picture in parser.pictures if any(
        "singularity" in (attrs.get("srcset") or attrs.get("src") or "")
        for _, attrs in picture)]
    require(len(relevant) == 1, "Expected one responsive singularity picture")
    picture = relevant[0]
    require(picture and picture[-1][0] == "img",
            "The picture must end with its fallback img")
    require(sum(tag == "img" for tag, _ in picture) == 1,
            "The picture must contain exactly one fallback img")
    require(len(picture[-1][1].get("alt") or "") >= 20,
            "The profile image needs meaningful alternative text")
    fallback = local_path(root, picture[-1][1].get("src") or "")
    sources = [(attrs, source_path(root, attrs))
               for tag, attrs in picture if tag == "source"]
    require(bool(sources), "Missing responsive picture sources")
    seen_animation = False
    for attrs, path in sources:
        if path.suffix == ".webp":
            seen_animation = True
        if re.search(r"prefers-reduced-motion\s*:\s*reduce\b",
                     attrs.get("media") or "", re.IGNORECASE):
            require(not seen_animation,
                    "Reduced-motion posters must precede animated sources")
            require(path.suffix == ".png",
                    "Reduced-motion sources must select static PNG posters")
        mime = attrs.get("type")
        expected_mime = {".webp": "image/webp", ".png": "image/png"}.get(path.suffix)
        require(mime is None or mime == expected_mime,
                f"Source MIME type disagrees with its image: {path.name}")

    selections = {}
    for width, variant in ((390, "mobile"), (1280, "desktop")):
        _, stem, _ = VARIANTS[variant]
        for reduced in (True, False):
            selected = next((path for attrs, path in sources if media_matches(
                attrs.get("media") or "", width, reduced)), fallback)
            expected = root / "assets" / (f"{stem}-poster.png" if reduced
                                           else f"{stem}.webp")
            require(selected == expected.resolve(),
                    f"At {width}px, reduced motion={reduced}: selected "
                    f"{selected.name}, expected {expected.name}")
            selections[f"{variant}_{'reduced' if reduced else 'animated'}"] = selected.name
    return selections


def thumbnail(image: Image.Image) -> np.ndarray:
    width = 280
    height = round(image.height * width / image.width)
    return np.asarray(image.convert("RGB").resize(
        (width, height), Image.Resampling.BILINEAR), dtype=np.int16)


def validate_poster(path: Path, expected_size: tuple[int, int]) -> dict:
    with Image.open(path) as poster:
        require(poster.format == "PNG", f"{path.name}: expected a PNG poster")
        require(getattr(poster, "n_frames", 1) == 1,
                f"{path.name}: reduced-motion poster must be static")
        require(poster.size == expected_size,
                f"{path.name}: wrong poster dimensions {poster.size}")
        poster.load()
        luminance = np.asarray(poster.convert("L"), dtype=np.float32)
        require(float(luminance.std()) > 6 and float(np.ptp(luminance)) > 32,
                f"{path.name}: poster is blank or has inadequate visual contrast")
    return {"bytes": path.stat().st_size, "width": expected_size[0],
            "height": expected_size[1]}


def validate_animation(path: Path, expected_size: tuple[int, int], budget: int) -> dict:
    size_bytes = path.stat().st_size
    require(0 < size_bytes <= budget,
            f"{path.name}: {size_bytes:,} bytes exceeds {budget:,}-byte budget")
    requested = sorted({ms for t in MOTION_SAMPLES_MS for ms in (t, t + 200)})
    samples = {}
    durations = []
    elapsed_ms = 0
    max_active_ms = 0
    started = perf_counter()
    with Image.open(path) as animation:
        require(animation.format == "WEBP", f"{path.name}: expected WebP")
        require(animation.is_animated, f"{path.name}: movie was saved as a still")
        require(animation.size == expected_size,
                f"{path.name}: wrong canvas {animation.size}, expected {expected_size}")
        require(animation.info.get("loop") == 0, f"{path.name}: loop must be infinite")
        require(360 <= animation.n_frames <= 540,
                f"{path.name}: expected 360–540 encoded frames, got {animation.n_frames}")
        for index in range(animation.n_frames):
            animation.seek(index)
            animation.load()  # WebP duration is populated only after decoding.
            duration = animation.info.get("duration")
            require(isinstance(duration, int) and duration > 0,
                    f"{path.name}: frame {index} has invalid duration {duration}")
            end_ms = elapsed_ms + duration
            if elapsed_ms < ACTIVE_MS[1] and end_ms > ACTIVE_MS[0]:
                max_active_ms = max(max_active_ms, duration)
                require(duration <= 67,
                        f"{path.name}: frame {index} holds for {duration}ms "
                        f"during active motion at {elapsed_ms}ms")
            hits = [point for point in requested if elapsed_ms <= point < end_ms]
            if hits:
                small = thumbnail(animation)
                for point in hits:
                    samples[point] = small
            durations.append(duration)
            elapsed_ms = end_ms
    require(abs(elapsed_ms - EXPECTED_DURATION_MS) <= 2,
            f"{path.name}: expected 18,000ms, got {elapsed_ms}ms")
    require(len(samples) == len(requested), f"{path.name}: missing motion samples")
    motion = {}
    for point in MOTION_SAMPLES_MS:
        difference = np.abs(samples[point + 200] - samples[point])
        mean_difference = float(difference.mean())
        changed_fraction = float((difference.max(axis=2) > 2).mean())
        require(mean_difference >= 0.025 and changed_fraction >= 0.0005,
                f"{path.name}: no visible motion near {point}ms "
                f"(mean change={mean_difference:.4f}, changed={changed_fraction:.5f})")
        motion[str(point)] = {"mean_pixel_change": round(mean_difference, 4),
                              "changed_fraction": round(changed_fraction, 5)}
    return {"bytes": size_bytes, "width": expected_size[0],
            "height": expected_size[1], "frames": len(durations),
            "duration_ms": elapsed_ms, "max_active_frame_ms": max_active_ms,
            "decode_seconds": round(perf_counter() - started, 3),
            "motion_samples": motion}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT,
                        help="Repository root (defaults to this script's repository)")
    parser.add_argument("--json", action="store_true", help="Print a JSON validation report")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        require(features.check("webp"), "Pillow requires libwebp decoding support")
        report = {"picture": validate_readme(root), "variants": {}}
        for name, (size, stem, budget) in VARIANTS.items():
            report["variants"][name] = {
                "animation": validate_animation(root / "assets" / f"{stem}.webp", size, budget),
                "poster": validate_poster(root / "assets" / f"{stem}-poster.png", size),
            }
    except (ValueError, OSError, EOFError) as error:
        print(f"Profile validation failed: {error}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for name, result in report["variants"].items():
            item = result["animation"]
            print(f"{name}: {item['width']}×{item['height']}, {item['frames']} frames, "
                  f"{item['duration_ms']}ms, {item['bytes']:,} bytes; "
                  f"active holds ≤{item['max_active_frame_ms']}ms")
        print("Full frame decode, motion samples, static posters, and picture routing passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
