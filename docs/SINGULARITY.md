# The GitHub singularity

The profile is an original piece of GitHub-native motion design: an intentionally polished README becomes unstable, fractures, and collapses into its own central singularity.

## Storyboard (32-second looping timeline)

1. **0–3 s: pristine.** A serious editorial developer profile appears, with a large SAI wordmark and sections for Psi, Shohin, GPU/MoE research and upstream framework contributions.
2. **3–8 s: fracture.** The actual SVG profile sections, not generic rectangular filler, are clipped into many small pieces. Each piece follows its own Bézier capture trajectory while stretching and turning inward. The SAI wordmark also breaks into horizontal strips.
3. **8–30 s: orbital debris.** Dozens of fragments from the work become particles and typographic debris circling a graphic event horizon. Tokens such as CUDA, autograd, MoE, PyTorch, Shohin, Psi, JAX, BF16 and memory movement appear in several differently paced ellipses.
4. **30–32 s: reset.** The scene fades into a restored profile and the cycle starts again.

The black hole is an **illustration of gravity**, not a physically modeled Kerr render; the real WebGL Gargantua belongs on the portfolio website.

## How it works

- `scripts/build_singularity.py`: standalone, deterministic Python standard-library animation generator. Produces desktop and mobile SVGs.
- `scripts/build_profile_art.py`: preserves the original panel generation, invokes the new generator and builds the short profile README.
- `assets/singularity.svg`, `assets/singularity-mobile.svg`: self-contained SVG with SMIL motion timelines, internal `<use>`/clip references, and static reduced-motion alternatives.
- `README.md`: one responsive illustration plus a small set of genuine source links and an expandable record of work. Old static panel assets are retained in the repository.

No remote image hosts, image-generation endpoints, JavaScript, WebGL, SVG scripts or runtime dependencies are used. There are no fabricated benchmarks and no embedded analytics.

**Important GitHub limitation:** the singularity cannot reach out of an `<img>` to manipulate GitHub's surrounding page. The visual trick works by drawing a complete miniature README *inside* the SVG, then shattering that composition. The real links stay as HTML below the visual.

## Editing and verification

```bash
python3 scripts/build_profile_art.py
git diff --check
```

The pull-request validation workflow checks regeneration, SVG XML, presence of real source links, animation element count, reduced-motion fallback and an asset-size budget.

For visual testing, open the README on GitHub on desktop and mobile, and verify the initial state, the mid-collapse state and the stabilized orbit. Whether playback begins immediately or is deferred can depend on the viewer/browser, and reduced-motion users intentionally see the static design.

The source links are meant to remain functional even when the profile illustration has collapsed beyond readability.
