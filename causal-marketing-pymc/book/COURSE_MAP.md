# Course ↔ book map

The single source of truth for **what each chapter must cover to be complete as course
material**, and which chapters are done. The `chapter-magnificence` skill reads this file for its
coverage/completeness check and updates the **Status** column when a chapter passes.

**Context.** The book is the companion to *Causal Inference & XAI for Business* (SDA Bocconi, MBA
in Business Analytics), taught by **Michele Russo**. Francesco (PyMC Labs) delivers a **guest
lecture on Chapters 9 (synthetic control) and 13 (instrumental variables)**. Those two are the
current priority and must be magnificent first. The course is **frequentist**; the book adds a
**contained "what Bayes adds" flavour** (never the headline) plus, in Ch. 2, the general bridge.

The course material lives in `course/` (git-ignored, not ours to redistribute): six session decks
`Session1_v0.pdf … Session6_v0.pdf` and one R companion notebook `Notebook1_Experiments.html`. It
is a **v0 draft** (placeholder figures, typos) — treat it as a moving target.

Legend for **Status**: `todo` · `in-progress` · `magnificent` (passed the skill) · `n/a`.

---

## The course, session by session

| # | Session title | Core content |
|---|---|---|
| S1 | Why Causality Is the Business Question | description/prediction/intervention; correlation vs causation (confounding, selection, reverse causation); **Simpson's paradox**; **Pearl's ladder of causation**; potential outcomes, the fundamental problem; ATE/ATT/ATU/CATE; selection-bias decomposition; SUTVA, unconfoundedness, overlap; **point vs partial identification, Manski bounds**; estimand-before-method. *No estimation.* |
| S2 | Experiments: The Gold Standard and Its Limits | randomisation (Fisher/Neyman); A/B design; **power, MDE, sample size**; **peeking / optional stopping**; **CUPED / variance reduction**; **SRM**; Fisher exact vs Welch; ITT vs per-protocol; internal/external validity; SATE/PATE; guardrails. Companion notebook (R): the "Northwind" A/B test. |
| S3 | Causal Diagrams and Matching | **DAGs, d-separation, backdoor & front-door**; good/bad controls, control taxonomy, **Table-2 fallacy**, **M-bias**; matching, subclassification, **propensity score, IPW, doubly-robust**; regression-as-matching, **OVB, FWL**; **sensitivity: Oster's δ, Rosenbaum bounds Γ, E-value**; balance/overlap, love plot. |
| S4 | DiD, Synthetic Control, RDD | DiD, parallel trends, TWFE, event study, **staggered adoption** (Goodman-Bacon, Callaway–Sant'Anna), triple diff, honest DiD; **synthetic control** (only ~3 slides); RDD sharp/fuzzy, continuity, **McCrary density**, bandwidth/CCT, kink. |
| S5 | Instrumental Variables and the Turn to Heterogeneity | endogeneity's four faces; **2SLS, Wald**; three conditions (relevance/exclusion/exogeneity) + **monotonicity**; **first-stage F, weak instruments, Anderson–Rubin**; over-ID/Sargan–Hansen; **LATE, principal strata, complier share, Abadie's κ**; conditional IV; attrition/**Lee bounds**; then CATE `τ(x)`, four segments, Qini, prediction≠effect. Running example: **price elasticity via cost shock**. |
| S6 | Causal Machine Learning, and Causal AI | **meta-learners S/T/X/R**; **causal forests (honest)**; **DML** (Neyman-orthogonality, cross-fitting); DR-learner/AIPW; **XAI: variable importance, PDP/ICE, SHAP critique**; uplift, Qini, scores→policy; **causal AI: policy trees, off-policy evaluation, causal discovery, LLMs**. |

---

## The book, chapter by chapter — mapping and status

★ = current guest-lecture priority.

| Ch | File / notebook | Maps to | Must cover (from the course) | Bayes flavour | Status |
|---|---|---|---|---|---|
| 1 | `foundations` / nb00 | S1 (+ parts S2, S3) | PO, fundamental problem, selection-bias decomposition, ATE/ATT/CATE, SUTVA/unconf/overlap, DAGs (fork/chain/collider), backdoor, g-formula, estimator ladder (naive/reg/IPW/AIPW), LaLonde. **Add:** Simpson's paradox (named), ladder of causation (named), a nod to partial identification. | none (foundations) | in-progress |
| 2 | `point_vs_posterior` / nb00 §7 | S1 (identification/uncertainty) | **the Bayes bridge chapter** — bootstrap vs posterior, Bernstein–von Mises, CI vs credible interval, `P(effect>c)`; partial-identification framing. | **this is the bridge** (out of current scope, but keep) | todo |
| 3 | `uplift` / nb01 | S5 (heterogeneity) + S6 (uplift) | CATE, meta-learners S/T/X, Qini/AUUC, prediction≠effect, four segments, scores→policy. **Add / consider:** R-learner, honest causal forests, policy-learning nod. | contained (BCF + `P(τ_i>c)`) | in-progress |
| 4 | `segment_effects` / nb02 | S5/S6 (CATE, hierarchy) | conditional effects, hierarchical/partial pooling, segment estimands. | natural (hierarchy) | todo |
| 5 | `price_elasticity` / nb03 | S5 (IV/price) + S2 (dose-response) | simultaneity of price & quantity, **IV via cost shock** (the course's IV running example), dose-response, elasticity; **power/MDE** live here. | contained | todo |
| 6 | `mediation` / nb04 | S3 (mediator, front-door) | mediator vs confounder, direct/indirect, **front-door criterion**. | contained | todo |
| 7 | `what_to_control` / nb05 | S3 (matching) + S6 (DML) | DAGs applied, good/bad controls, PS/IPW/DR, OVB, **M-bias, Table-2 fallacy**, **DML**, sensitivity (Oster/Rosenbaum/E-value). | contained | todo |
| 8 | `mmm` / nb06 | (no direct session) | incrementality, MMM, adstock/saturation; touches S2 (Lewis–Rao ad ROI) & S5. Marketing-specific extension. | natural (priors on curves) | todo |
| ★9 | `geo_lift` / nb07 + 07b | **S4 (synthetic control)** | donor pool, simplex/convex hull, pre-fit gate, **placebo-in-space permutation p-value**, placebo-in-time, randomization interval, spillover/SUTVA, real geo experiment (Google). Book goes **far** beyond the deck's 3 slides — good. **Added 2026-07-16 (full revision):** three-DAG identification figure (SC removes the backdoor / IV bypasses it), TBR provenance note, appendix 9.A.14–17 (margin algebra, matched-pairs SE, effective donors, coverage MC error), variance-growth + GLS-reweighting + pair-scatter + hull-failure figures. | contained: AR(1) honest-total-uncertainty + `P(pays)` as a **flavour section**, not the spine | magnificent (re-verified 2026-07-16, six-auditor pass) |
| 10 | `did` / nb08 | S4 (DiD) | parallel trends, TWFE, event study, **staggered adoption caveats** (must not present naive TWFE for staggered timing), cluster/BDM SEs. | contained | todo |
| 11 | `rdd` / nb09 | S4 (RDD) | sharp/fuzzy, continuity, **McCrary**, bandwidth/CCT, covariate continuity, placebo cutoffs, donut. | contained | todo |
| 12 | `its` / nb10 | S4 (time-RDD bridge) | interrupted time series; the "time as running variable" link the deck draws. | contained | todo |
| ★13 | `iv` / nb11 + 11b | **S5 (IV)** | endogeneity, **Wald/2SLS**, relevance/exclusion/exogeneity/monotonicity, **first-stage F & weak IV**, **LATE/principal strata/complier share**, exclusion pricing, Criteo. Added 2026-07-16: **Anderson–Rubin, Abadie's κ, Lee bounds, the four faces of endogeneity** (each an appendix subsection 13.A.13–16 with a worked example + figure, named in the body), plus **VOI**. | contained: joint-model `P(β>c)` + `ρ` as a **flavour section**, not the middle third | magnificent |

---

## Coverage gaps — course topics without a solid book home

The skill flags these; each needs a decision (add / relocate / declare course-only).

1. **Experiment design (S2)** — power, MDE, peeking, CUPED, SRM, Fisher-vs-Neyman. Currently
   scattered into Ch. 5. The course spends its **entire second session + its only notebook** here.
   *Decision needed:* a dedicated experiments chapter/section, or an explicit "see the course."
2. **Partial identification / Manski bounds (S1, S3, S5)** — largely absent. Natural home: Ch. 2.
3. **Sensitivity toolkit by name (S3)** — Oster's δ, Rosenbaum Γ (E-value is in Ch. 3). Home: Ch. 7.
4. **Causal AI / policy learning / off-policy evaluation / causal discovery / LLMs (S6)** — absent.
   Likely **course-only** for a causal-*marketing* cookbook; state it, don't leave it silent.
5. **XAI / explainability — variable importance, PDP/ICE, SHAP critique (S6; course title!)** —
   absent. Decide: a short chapter, or course-only.
6. **Simpson's paradox & the named ladder of causation (S1, S3)** — the *concepts* are in Ch. 1
   (strata/g-formula, seeing-vs-doing), but not the named devices/examples the students saw.

## Book content with no course session (fine — enrichment)

- **The entire Bayesian layer** (posteriors, credible intervals, `P(effect>c)`, BCF, AR(1),
  probit IV). This is the book's identity and the reason for the guest lecture — keep it a
  *flavour* per chapter, with Ch. 2 carrying the general bridge.
- **Worked real datasets** (LaLonde, Google geo, Criteo, Hillstrom) — the course only name-checks
  evidence; the book runs it.
- **Simulation-based coverage/calibration studies, VOI** — beyond the course; keep.

---

## Guest-lecture note (Ch. 9 & Ch. 13)

Both chapters, and their notebooks (nb07/07b `cmp-core`; nb11/11b `cmp-legacy`), are destined to
become **marimo** lecture notebooks. Constraint from the repo: **PyMC cannot run in the browser
(WASM)**, so the marimo versions must present **precomputed / cached** posteriors and figures —
the notebook must be structured so every displayed result is loaded, not sampled live. The skill's
notebook step enforces this.
