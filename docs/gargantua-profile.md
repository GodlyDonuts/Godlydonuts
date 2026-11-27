# Gargantua in the GitHub profile

## What the viewer sees

The profile embeds an **eight-second animated WebP** produced from my original `Gargantua_Loop_1080p.mp4` Blender render. A reduced-motion preference switches to a still poster frame.

- `assets/gargantua-loop.webp` — real 8 s excerpt, 720 px wide, 10 fps, 1,385,442 bytes.
- `assets/gargantua-poster.webp` — still from the same footage, 30,742 bytes.
- Both files are encoded with FFmpeg from the original source footage stored in the **private** `GodlyDonuts/gargantua` repository. The original Blender, Next.js app, shaders and high-resolution footage remain private.

The image is **not** simulated by a Cloudflare Worker and it is **not** a WebGL renderer in GitHub. It's intentionally faithful to the visual source. Clicking either the animation or hero opens the [interactive portfolio](https://saicharanramineni.com/), where real browser-side graphics can run.

## Why not Gemini's proposed Worker?

The Worker idea is cheap, but that particular code draws manually constructed SVG paths and ellipses rather than integrating the existing Gargantua Kerr geodesics or its plasma. Calling those paths "RK4 geodesics" would misrepresent the result. A remote SVG also isn't guaranteed to refresh on every GitHub visit, because of GitHub's image proxy and browser caches. A pretty SVG alone cannot run the Next.js/WebGL2 app inside Markdown.

GitHub supports inline images (including WebP) and normal links, but not arbitrary JavaScript or iframe-based interactive web apps inside a profile README.

## Visual and technical QA

1. Review this PR's rendered README to confirm the image plays and scales at a normal desktop width.
2. Test a narrow/mobile screen and light/dark modes. Both are supported by the browser's image renderer.
3. Turn on operating system **Reduce Motion** and confirm the poster replaces the animation in `<picture>`.
4. Click the preview or original hero; it should open the interactive portfolio.
5. Verify `scripts/build_profile_art.py` reproduces the exact committed README after running it.
6. Asset validation checks the RIFF/WebP headers, animation chunk, payload limits, and the original output hashes.

## Rebuilding

The original render source and export are documented in the private `gargantua` repository at:

`scripts/export-readme-preview.sh` on branch `experiment/readme-gargantua-preview-20261108`.

That script uses FFmpeg to produce an animation and a poster from the existing 1080p footage, and records SHA-256 hashes. For future edits, rerun this export on a machine or runner with access to the private video, and replace both assets here.

There is **no Cloudflare account**, external API key, cross-account secret, background service, user data collection, or dynamic endpoint required for the embedded preview.

A proper live WebGL Gargantua deployment would need a separate host (portfolio, Vercel, or Pages), with GitHub linking to it. This PR solves the *GitHub README display* portion, not the hosting of the independent Next.js app.
