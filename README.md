<!-- SVG artwork and this README are maintained by scripts/build_profile_art.py. -->
<p align="center">
  <picture>
    <source media="(max-width: 760px) and (prefers-color-scheme: dark)" srcset="assets/hero-dark-mobile.svg" />
    <source media="(max-width: 760px) and (prefers-color-scheme: light)" srcset="assets/hero-light-mobile.svg" />
    <source media="(prefers-color-scheme: dark)" srcset="assets/hero-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="assets/hero-light.svg" />
    <img src="assets/hero-light.svg" width="100%" alt="Sai — Saicharan Ramineni. Computer Science at UCF, Orlando." />
  </picture>
</p>

<picture>
    <source media="(max-width: 760px)" srcset="assets/profile-intro-mobile.svg" />
    <img src="assets/profile-intro.svg" width="100%" alt="I work through papers and framework source by building and testing implementations. GPU kernels, small models, and the runtimes beneath them." />
  </picture>

<a href="https://github.com/GodlyDonuts?tab=repositories&amp;sort=updated"><picture>
    <source media="(max-width: 760px)" srcset="assets/activity-strip-mobile.svg" />
    <img src="assets/activity-strip.svg" width="100%" alt="Latest public change from a periodically refreshed GitHub snapshot." />
  </picture></a>

## inside the experiments

I learn by rebuilding things, testing the assumptions, and seeing where they break. Three problems I keep coming back to:

<picture>
    <source media="(max-width: 760px)" srcset="assets/experiment-console-mobile.svg" />
    <img src="assets/experiment-console.svg" width="100%" alt="An animated research console: a backward gradient, a model revising a draft, and tokens routing to experts. Schematic diagrams, not benchmark results." />
  </picture>

<details>
<summary><strong>01 / What does a backward pass actually do?</strong></summary>

[Psi](https://github.com/GodlyDonuts/psi) is my language-model training stack: custom autograd, gradient checks, and Metal/CUDA kernels. I wanted to understand the mechanics, not just call the API.

</details>

<details>
<summary><strong>02 / Can a small model learn to revise?</strong></summary>

[Shohin](https://github.com/GodlyDonuts/shohin-ettr) tests revision as part of the model's behavior. Experiments, controls, and negative results matter more to me than a polished demo.

</details>

<details>
<summary><strong>03 / Where does MoE inference waste time?</strong></summary>

I've been studying expert routing, queueing, and memory movement in GPU inference. The animation above is an illustration of the system, **not a benchmark or a claimed speedup**. This is an active area of investigation.

</details>

*Each animation is schematic. For reproducible claims, follow the project and upstream source links below.*

<a href="https://saicharanramineni.com/projects"><picture>
    <source media="(max-width: 760px)" srcset="assets/heading-work-mobile.svg" />
    <img src="assets/heading-work.svg" width="100%" alt="Selected work. Browse all projects." />
  </picture></a>

<a href="https://github.com/GodlyDonuts/psi"><picture>
    <source media="(max-width: 760px)" srcset="assets/work-psi-mobile.svg" />
    <img src="assets/work-psi.svg" width="100%" alt="Psi. A language model and its training stack. C++17 · autograd · Metal · CUDA Gradient checks, trained checkpoints, and documented kernel benchmarks." />
  </picture></a>

<a href="https://github.com/GodlyDonuts/shohin-ettr"><picture>
    <source media="(max-width: 760px)" srcset="assets/work-shohin-mobile.svg" />
    <img src="assets/work-shohin.svg" width="100%" alt="Shohin. Training models to revise their own drafts. An ongoing research project. Matched controls, results, limitations, and negative experiments." />
  </picture></a>

<a href="https://github.com/GodlyDonuts/sai"><picture>
    <source media="(max-width: 760px)" srcset="assets/work-sai-mobile.svg" />
    <img src="assets/work-sai.svg" width="100%" alt="Sai. A voice agent that operates a Mac. Screenshots in. Verified actions out. Visual control, per-action verification, and repeated-failure detection." />
  </picture></a>

<a href="https://saicharanramineni.com/"><picture>
    <source media="(max-width: 760px)" srcset="assets/work-gargantua-mobile.svg" />
    <img src="assets/work-gargantua.svg" width="100%" alt="Gargantua. The black hole behind my portfolio. Real-time WebGL · procedural plasma Curved light paths, optical bloom, and a camera driven by native scrolling." />
  </picture></a>

<a href="https://saicharanramineni.com/open-source"><picture>
    <source media="(max-width: 760px)" srcset="assets/heading-upstream-mobile.svg" />
    <img src="assets/heading-upstream.svg" width="100%" alt="Upstream contributions. Open the full record." />
  </picture></a>

<a href="https://github.com/pytorch/pytorch/commit/42a70784390a343ebd90e9e84b1bf5a5df4901f3"><picture>
    <source media="(max-width: 760px)" srcset="assets/upstream-pytorch-mobile.svg" />
    <img src="assets/upstream-pytorch.svg" width="100%" alt="PyTorch. Global scratch in the static Triton launcher. TorchInductor / GPU runtime Scratch allocation and metadata for restoring kernels from the FX graph cache." />
  </picture></a>

<a href="https://github.com/tensorflow/tensorflow/pull/125171"><picture>
    <source media="(max-width: 760px)" srcset="assets/upstream-tensorflow-mobile.svg" />
    <img src="assets/upstream-tensorflow.svg" width="100%" alt="TensorFlow. SELU gradient precision for negative inputs. Numerical correctness Float32 and float64 regression coverage in both graph and eager execution." />
  </picture></a>

<details>
  <summary><picture>
    <source media="(max-width: 760px)" srcset="assets/fold-now-mobile.svg" />
    <img src="assets/fold-now.svg" width="92%" align="middle" alt="Right now: recent public work and current questions" />
  </picture></summary>

<a href="https://github.com/GodlyDonuts?tab=repositories&amp;sort=updated"><picture>
    <source media="(max-width: 760px)" srcset="assets/now-mobile.svg" />
    <img src="assets/now.svg" width="100%" alt="Sai&#x27;s latest public change and current research questions." />
  </picture></a>

</details>

<details>
  <summary><picture>
    <source media="(max-width: 760px)" srcset="assets/fold-offscreen-mobile.svg" />
    <img src="assets/fold-offscreen.svg" width="92%" align="middle" alt="Offscreen: rockets, predictions, design and lifting" />
  </picture></summary>

<a href="https://saicharanramineni.com/"><picture>
    <source media="(max-width: 760px)" srcset="assets/offscreen-mobile.svg" />
    <img src="assets/offscreen.svg" width="100%" alt="Reusable rockets, the AI race, design, predictions, project names, and lifting." />
  </picture></a>

</details>

<p align="center"><a href="mailto:csramineni@gmail.com"><picture>
    <source media="(max-width: 760px)" srcset="assets/action-email-mobile.svg" />
    <img src="assets/action-email.svg" width="49%" alt="Email Sai" />
  </picture></a><!--
--><a href="https://saicharanramineni.com/"><picture>
    <source media="(max-width: 760px)" srcset="assets/action-portfolio-mobile.svg" />
    <img src="assets/action-portfolio.svg" width="49%" alt="Open the live portfolio" />
  </picture></a></p>

<p align="center"><a href="https://www.linkedin.com/in/saicharan-ramineni/"><picture>
    <source media="(max-width: 760px)" srcset="assets/action-linkedin-mobile.svg" />
    <img src="assets/action-linkedin.svg" width="49%" alt="LinkedIn" />
  </picture></a><!--
--><a href="https://saicharanramineni.com/projects"><picture>
    <source media="(max-width: 760px)" srcset="assets/action-projects-mobile.svg" />
    <img src="assets/action-projects.svg" width="49%" alt="All projects" />
  </picture></a></p>
