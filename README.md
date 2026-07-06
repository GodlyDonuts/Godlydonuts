<!--
  ██ SETUP CHECKLIST — delete this comment once done ██
  1. This file replaces README.md in your profile repo: GodlyDonuts/Godlydonuts
  2. Commit header.svg to that same repo at  assets/header.svg  (path must match the <img> below)
  3. Fill in the two placeholders in the link row: YOUR-LINKEDIN and YOUR-EMAIL
  4. Optional: if you want Shohin quiet until release, delete the "Now" section — everything else stands alone
  5. Pin these repos (Profile → Customize your pins): psi, Hacklytics-GoldenByte, Mycelia, parameter-golf
-->

<img src="assets/header.svg" width="100%" alt="Terminal session — whoami: sai, cs @ ucf, I build ML systems from first principles. cat now.txt: pretraining a 135M-param reasoning model from scratch on 8×H100. ls proof/: tensorflow-prs, handwritten-autograd, hackathon-wins, 1.0610-bpb." />

<p align="center">
  <a href="https://saicharanramineni.com"><b>portfolio</b></a> ·
  <a href="https://www.linkedin.com/in/YOUR-LINKEDIN"><b>linkedin</b></a> ·
  <a href="mailto:YOUR-EMAIL"><b>email</b></a>
</p>

CS @ UCF (Burnett Honors College). I like the layer *under* the model — training stacks, GPU kernels, tokenizers, data pipelines — and I'd rather write these systems than read about them.

### Now

Pretraining **Shohin** — a 135M-parameter language model built from scratch (custom tokenizer → custom data pipeline → 8×H100 training run), targeting state-of-the-art reasoning at the ≤150M scale. Release and writeup soon.

### Selected work

**[psi](https://github.com/GodlyDonuts/psi)** — a small language model *and* the training stack it runs on, written from scratch in C++. Own reverse-mode autograd (gradient-checked against finite differences to ~1e-12), own GPU kernels, no PyTorch or any other ML framework anywhere in the stack.

**[Crisis Topography](https://github.com/GodlyDonuts/Hacklytics-GoldenByte)** — voice-commanded 3D geospatial crisis-intelligence platform: agentic orchestration over Databricks analytics and a self-hosted Actian vector store (18k+ embeddings, sub-100ms retrieval). 🥉 **3rd overall @ Hacklytics 2026** (Georgia Tech, 1,200+ builders).

**[Mycelia](https://github.com/GodlyDonuts/Mycelia)** — distributed compute marketplace: Next.js, Aurora DSQL, double-entry escrow ledger, MCP-native agent integration.

### Open source

Merged PRs in **TensorFlow** core — [a segfault guard in `TensorListSetItem`](https://github.com/tensorflow/tensorflow/pull/121708) and [a float32 `erfinv` precision fix near ±1](https://github.com/tensorflow/tensorflow/pull/121644) — plus [Unsloth](https://github.com/unslothai/unsloth/pulls?q=is%3Apr+author%3AGodlyDonuts+is%3Amerged), [LiteLLM](https://github.com/BerriAI/litellm/pulls?q=is%3Apr+author%3AGodlyDonuts+is%3Amerged), [torchtitan](https://github.com/pytorch/torchtitan/pulls?q=is%3Apr+author%3AGodlyDonuts+is%3Amerged), and [wit-bindgen](https://github.com/bytecodealliance/wit-bindgen/pulls?q=is%3Apr+author%3AGodlyDonuts+is%3Amerged).

**[→ every merged PR, live from GitHub search](https://github.com/search?q=is%3Apr+is%3Amerged+author%3AGodlyDonuts&type=pullrequests)** — no curation, just the query.

### Competitions

| | |
|---|---|
| **OpenAI Parameter Golf** | [1.0610 val bits-per-byte](https://github.com/GodlyDonuts/parameter-golf) · briefly #1 on the live leaderboard |
| **Amazon Nova AI Hackathon** | Best Agentic AI · 13,000+ participants |
| **Hacklytics 2026** (Georgia Tech) | 3rd overall · 1,200+ participants |
| **NVIDIA Nemotron Challenge** (Kaggle) | z3-based cipher solvers + templated search for bit-manipulation puzzles |

### Stats

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api?username=GodlyDonuts&show_icons=true&hide_border=true&theme=github_dark&bg_color=00000000">
    <img height="170" src="https://github-readme-stats.vercel.app/api?username=GodlyDonuts&show_icons=true&hide_border=true&bg_color=00000000" alt="GitHub stats">
  </picture>
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://github-readme-stats.vercel.app/api/top-langs/?username=GodlyDonuts&layout=compact&hide_border=true&theme=github_dark&bg_color=00000000">
    <img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username=GodlyDonuts&layout=compact&hide_border=true&bg_color=00000000" alt="Top languages">
  </picture>
</p>

<p align="center">
  <b>Open to ML-infra / systems internships.</b><br>
  <sub>Everything above links to a receipt — claims are cheap, merged PRs aren't.</sub>
</p>
