# The singularity film

A finished profile is pulled apart by its own gravity. The original headline, project names, code terms, and rules become the orbiting debris. The same pieces return to their original positions before the loop repeats.

The profile serves a rendered 18-second, 30 fps animated WebP. All geometry, lighting, camera movement, trails and typography are calculated during the build. A visitor's browser decodes one image; it does not run the scene renderer.

## Why the renderer changed

The previous desktop SVG contained 673 SMIL animation tracks, 125 clip paths and 135 `<use>` instances. Mobile still contained 523 tracks. Each card shard cloned a complete card and animated several nested transforms. Small source files hid substantial continuous browser work.

The new playback removes that live SVG scene entirely. The file is larger than the old vector source, so both delivered variants have explicit download budgets. WebP decoding still uses browser resources; a 30 fps source is not a promise that every device will display every frame.

The film also fixes the visual discontinuity in the old design: the real profile no longer vanishes and gets replaced by unrelated badge labels. Every large visible word and glyph fragment originated in the opening profile.

## Choreography

- **0–1.4 seconds:** the finished editorial profile.
- **1.4–4 seconds:** the singularity forms; the layout strains inward before turning.
- **4–7 seconds:** accelerating capture, sheared headline fragments, baked exposure trails and luminous accretion.
- **7–11.5 seconds:** coherent orbits with depth, shadow occlusion and a subtle camera advance. Major project names occupy separated orbital phases.
- **11.5–12.5 seconds:** motion slows into the turnaround.
- **12.5–18 seconds:** the same continuous trajectories reverse into the original profile. The final hold is identical to the opening composition.

Desktop is 1120×700. Mobile is a separate 640×860 composition with two-column project typography and taller debris orbits. It is not a crop of the desktop scene.

This is original motion design, not a physical Kerr simulation. The interactive black-hole experience remains on the portfolio website.

## Files

| File | Role |
| --- | --- |
| `scripts/build_singularity.py` | Deterministic offline scene renderer and WebP encoder |
| `scripts/requirements-art.txt` | Pillow and NumPy build/validation dependencies |
| `assets/fonts/` | Bundled DejaVu fonts and their license |
| `assets/singularity.webp` | Desktop animation |
| `assets/singularity-mobile.webp` | Mobile animation |
| `assets/singularity-poster.png` | Desktop static profile |
| `assets/singularity-mobile-poster.png` | Mobile static profile |
| `scripts/build_profile_art.py` | Lightweight README and legacy panel generation |
| `scripts/validate_singularity.py` | Full media decode, motion, timing and routing checks |

The README uses `<picture>`. Reduced-motion sources come first and choose a static PNG of the same composition. The mobile source selects the portrait animation; the desktop WebP source handles wider screens. The final PNG `<img>` also works as a format fallback. Real project, contact and contribution links remain ordinary GitHub links below the film.

GitHub renders WebP images inline: [GitHub's WebP announcement](https://github.blog/changelog/2025-08-28-added-support-for-webp-images/). Media-conditioned sources are standard [`<picture>` behavior](https://developer.mozilla.org/en-US/docs/Web/HTML/Reference/Elements/picture).

## Rebuild

```sh
python3 -m pip install -r scripts/requirements-art.txt

# Fast visual review: opening posters and an eight-frame storyboard.
python3 scripts/build_singularity.py --preview

# Render and encode both variants. Intermediate PNG frames stay in previews/.
python3 scripts/build_singularity.py --workers 4 --quality 64

# Rebuild the README without rerendering the film.
python3 scripts/build_profile_art.py

# Decode every delivered frame and verify behavior.
python3 scripts/validate_singularity.py --json
git diff --check
```

`--variant desktop` or `--variant mobile` renders only one composition. `--output-dir` stages candidate media outside `assets/`. `--render-animation` on `build_profile_art.py` explicitly requests the expensive render; ordinary profile refreshes do not render the movie.

The generator uses a fixed seed and bundled fonts. Pixel and encoded-byte reproducibility also depend on the installed Pillow, FreeType and libwebp versions. It uses no network, GPU, headless browser, externally hosted images, JavaScript, trackers or generative-image service.

## Validation

CI runs on relevant changes to main, pull requests and manual dispatch. It fully decodes both movies, checks their dimensions and 18,000 ms durations, and permits encoded frame coalescing only when it does not introduce stalls in the active section. It compares image samples at several points to catch accidentally frozen playback. It also checks the static posters and actual source selection for desktop/mobile with and without reduced motion.

Budget ceilings are 6 MiB for desktop and 5 MiB for mobile. They are upper limits, not render targets. The old requirement to have at least 100 live motion elements was removed: more animation nodes are not evidence of better motion.

Finally, inspect the actual GitHub README in both desktop and narrow viewports. Local decoding validates the media; the GitHub check validates the delivered experience.
