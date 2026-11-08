# Profile as an experiment, not a landing page

The profile has two audiences. Someone scanning for thirty seconds should know what I build and where the real work lives. Someone staying for five minutes should be able to understand a technical idea, follow a source link, and judge the evidence.

## Interface constraints

GitHub profile READMEs render GitHub Flavored Markdown and a safe subset of HTML. They are **not** general-purpose webpages.

- Allowed building blocks we rely on: links, headings, `<picture>`, `<details>`, and self-contained SVGs referenced as images.
- SVG animation is deliberately decorative/explanatory. The first frame makes sense with motion disabled.
- No runtime JS, Canvas, WebGL, iframe, executable Markdown, or visitor-dependent server state.
- Desktop and mobile have separate SVG viewBoxes. Images have accessible alternatives; meaningful text is also present in the document.
- The black-hole hero is a recognizable part of the visual identity; the experiments are an explanation of the work beneath it.

## The first executable slice

**The workbench** is one self-contained animated SVG with three independently understandable diagrams:

1. **Backpropagation**: forward and backward flow; points to the [Psi](https://github.com/GodlyDonuts/psi) code.
2. **Revision**: draft, test, revise; points to the [Shohin](https://github.com/GodlyDonuts/shohin-ettr) experiments and controls.
3. **Expert routing**: the systems question behind MoE serving. This is explicitly labeled as a schematic, not a measured throughput claim.

The diagram uses existing brand colors instead of a widget service. There is no third-party uptime dependency.

## The farther edge

These are the next features worth testing. They are not implemented by this PR:

- **A reproducible trace**: generate tiny animated timelines from committed benchmark files (not invented scores or changing external stats). Every chart links to its methodology and raw data.
- **Patch provenance**: show a small automated trail of merged contributions into upstream libraries, with the actual PR/commit links and dates.
- **A research tree**: let visitors choose an experiment question and expand its inputs, ablations, failed paths, and evidence. Use native `<details>` so it still works on GitHub.
- **A visitor's choice**: split the reading path into a quick skim and a deep technical tour, without trapping people in excessive scroll.
- **An observatory link**: when someone wants actual pointer interaction, WebGL, or responsive 3D, send them to the full portfolio website instead of pretending the README can execute it.

## Guardrails

- A benchmark result must have a source, workload, hardware, date, and relevant correctness conditions.
- Never describe a private project as if its implementation or results were public.
- Prefer one technically meaningful diagram to six generic stats cards.
- Keep claims precise, terse, and in my voice.
- GitHub Actions cron jobs and GitHub image caching are best-effort; never call a panel real-time if it is a periodic snapshot.
- Run `python3 scripts/build_profile_art.py` after changing the source builder. The generated README must remain in sync with the generator.

This README should be a small demonstration of how I think, not a CV with decorations.
