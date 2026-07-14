# Causal inference for marketing — a PyMC-ecosystem cookbook

Runnable, business-first notebooks that teach causal inference for marketing with the
PyMC ecosystem. Built for a guest lecture at **SDA Bocconi** (MBA-level, heterogeneous
treatment effects) and doubling as a durable internal toolkit.

Every notebook **leads with the decision** and treats uncertainty as a decision input —
not a statistics lecture. Credible intervals show up as *"how sure are we, and does it
change what we'd do?"* Each technique is validated against a **known simulated truth**
first, so you can see the method actually recover the answer before trusting it on real
data.

---

## Two artifacts

| | what it is |
|---|---|
| **`notebooks/`** (+ `reports/*.pdf`) | The lab. Runnable, exploratory; the PDFs are nbconvert transcripts, used as lecture hand-outs. |
| **`book/`** → `book/build/book.pdf` | **The Book.** A self-contained, typeset treatment — numbered chapters, sections and equations, `booktabs` tables, captioned vector figures, named assumptions, a bibliography, and per-chapter offprints. Built from the *executed* notebooks. |

### The book's one load-bearing rule

**Every number in the book is injected from an executed notebook. Nothing is retyped.**

    notebooks (executed) --cmp.report--> book/build/results/nbNN.json --> macros.tex --> book.pdf

The notebooks *emit* their results (`cmp.report.value/table/figure`); the book *injects* them
as LaTeX macros (`\nbSevenBayesSd`). Two properties follow, and both are the point:

- a **stale** number is impossible — the macro is whatever the notebook last printed;
- a **missing** number is a hard build failure, not a silent blank. The build refuses to ship
  a PDF with a hole in it, because a hole is louder than a stale number.

This exists because entire review rounds of this project were spent chasing prose that had
drifted from the output it described. Hand-copying results into a second narrative would have
industrialised that failure. (The single honest exception is flagged in place: Chapter 1's
LaLonde \$1,800 experimental benchmark is *cited from the literature*, not computed here.)

```bash
make book          # -> book/build/book.pdf  +  book/build/ch09_geo_lift.pdf, ...
```

A fresh clone must execute the notebooks at `CMP_FAST=0` first — `book/build/` is generated,
never committed. Architecture and the chapter template: **`book/BOOK_SPEC.md`**.

---

## The learning path

Read in this order — each step assumes the previous one:

1. **[00 · Foundations](notebooks/00_foundations.ipynb)** — the vocabulary the rest
   assumes (potential outcomes, confounding, the do-operator, DAGs, ATE vs CATE), built
   from scratch with one tiny end-to-end example. *(From `docs/causal_inference_primer.pdf`.)*
2. **Cookbook index** — the table below. One marketing decision per technique.
3. **⭐ [Anchor A · Uplift targeting](notebooks/01_uplift_targeting.ipynb)** — the HTE
   spine. Who to email, full depth: estimator bake-off, identification & sensitivity,
   euro policy with value-of-information.
4. **⭐ [Anchor B · Geo-lift synthetic control](notebooks/07_geo_lift_synthetic_control.ipynb)**
   — the program-evaluation spine. Did the regional campaign work, full depth: naive
   estimators failing, placebo inference, euro rollout decision.
5. **The rest** — techniques 02–06 and 08–11, each a self-contained decision.
6. **Real-data companions** — [07b](notebooks/07b_geo_lift_real_data.ipynb) and
   [11b](notebooks/11b_endogenous_exposure_real_data.ipynb) rerun the two
   quasi-experimental workhorses on public real datasets (Google's geo experiment,
   Criteo's 13.98M-user incrementality tests), replacing the planted truth with
   real-data anchors: a randomized benchmark and a full-file Wald estimate.

Prefer to poke at it live? The three **[interactive apps](#interactive-apps-marimo)**
(marimo) let you drag sliders and watch the decision move.

---

## Every notebook follows the same contract

A fixed pedagogical contract, so once you've read one you can read any of them:

0. **Step 0 — the classical read.** Before any sampler: the same estimand, the same
   identification, estimated with the simplest *correct* classical estimator — a point
   estimate and an interval, with an explicitly chosen covariance (HC1 / cluster / HAC /
   bootstrap). No likelihood, no priors, no chains. This is the honest benchmark the
   Bayesian model has to justify itself against, and it is why `cmp.classical` exists.
1. **Business question** — a concrete marketing decision, in plain language.
2. **Simulate a ground truth** — a seeded process with a *known* effect (the core
   teaching device; there's a hook to swap in real data — and notebooks 07b/11b take it,
   replacing this step with public real datasets plus an honest account of what can still
   be validated).
3. **Identify** — the estimand and the identification assumptions; DAG where relevant.
   *Kept separate from estimation.*
4. **Estimate** — fit with the mapped PyMC-ecosystem library; get a posterior.
5. **Validate** — recover-the-truth check + interval calibration.
   **5x — point estimate vs posterior.** The head-to-head: where the two arms agree
   (usually), where they differ, and *why*. It is allowed to conclude that Bayes bought
   nothing, and in several notebooks it does.
6. **Decide, in euros** — turn the effect into profit / ROI / P(worthwhile) / go-no-go.
7. **Caveats** — the honest failure modes and assumptions.

### What Step 0 turned up

The classical arm performs far better than expected, and the notebooks now say so:

- **Mostly the two agree** — Bernstein–von Mises: weak priors plus decent *n* means the
  credible interval ≈ the confidence interval. On the Criteo data (11b) 2SLS and the
  posterior agree to **0.04 pp — one hundredth of a standard error** — at 0.97× width.
- **Where Bayes lost, the cause was a misspecified likelihood, not the paradigm.** In 07 an
  iid likelihood on autocorrelated data under-prices a 20-week sum by **2.8×** (50% coverage
  against a design-based 88%), because Var(Σe) → n²σ², not nσ². In 08 the error runs the
  **other** way — an interval **6×** too *wide*. A paradigm cannot be systematically
  overconfident and underconfident at once; a *specification* can.
- **Why classical wins there:** it either uses no likelihood at all (randomization/placebo
  inference) or a variance estimator *engineered to be agnostic* about the error structure
  (HC / cluster / HAC / bootstrap). That is the frequentist toolkit's core competence.
- **The prior does almost nothing. The likelihood is the whole ballgame.**
- **What survives everywhere:** `P(effect > cost)` — which the classical arm structurally
  cannot produce, and which every euro decision consumes. The rule the notebooks land on:
  *use the posterior for the decision, and design-based inference for your confidence in it.*

The two anchors additionally carry the full **three depths**: (a) estimator bake-off &
failure modes, (b) identification rigour & sensitivity, (c) euro policy with parameter
sweeps and value-of-information.

**Every notebook is deep on four axes**, not just the anchors:

- **Technical diagnostics** — the signature check for each method: Qini/AUUC & uplift-by-decile
  (01), AIPW doubly-robust cross-checks (00, 01) & posterior predictive checks (01), event-study
  pre-trends & a live staggered-adoption/TWFE-bias demo (08), McCrary-style density check + bandwidth +
  placebo-cutoff + polynomial-order robustness (09), placebo-in-time & residual autocorrelation
  (10), first-stage F + reduced-form/Wald + exclusion-restriction stress test (11), Abadie
  RMSE-ratio placebo & leave-one-out donor robustness (07).
- **Business decision richness** — policy comparisons (treat-all/random/model/oracle) on realised
  profit, multi-parameter sweeps, value-of-information test-sizing, break-even tables, a
  posterior-gated budget-reallocation decision (06), the pooled<segment<individual<oracle
  targeting ladder (02).
- **Conceptual narration** — estimand ladders, assumption-by-assumption tables, worked math, DAG
  galleries, and cross-links between notebooks.
- **Rigorous validation** — calibration by decile + reliability curves + interval sharpness (01),
  **multi-seed recovery + interval-coverage** across fresh samples (00, 01, 02, 05, 07, 08, 09, 10, 11 —
  each reports recovery bias and how often its interval covers the truth), and sensitivity *ranges* —
  E-values and 2-D contours (01, 05) — rather than single points; the quasi-experimental notebooks add
  placebo / falsification checks. (03 validates via shrinkage + a failed-calibration honesty note, 04 via
  path-effect recovery, 06 via the naive-vs-adjusted confounding contrast — the MMM is too costly to
  multi-seed — so those three carry method-appropriate validation instead of the seed loop. The
  real-data companions validate against what real data offers instead of a planted truth: 07b grades
  synthetic control against the experiment's own matched-pairs randomization plus pseudo-cell placebo
  permutation, 11b grades the subsample IV against the 13.98M-row Wald anchor plus disjoint-fold
  stability.)

---

## Technique index

| # | Notebook | Marketing decision | Library | Env |
|---|----------|--------------------|---------|-----|
| 00 | [Foundations](notebooks/00_foundations.ipynb) | — the vocabulary — | numpy (no PyMC — on purpose) | core |
| 01 | ⭐ [Uplift targeting](notebooks/01_uplift_targeting.ipynb) | Who should get the €10 discount? | pymc-bart (BART / BCF) | core |
| 02 | [Segment effects](notebooks/02_segment_effects.ipynb) | Does the offer work better for some segments? | pathmc (do-operator, CATE) | core |
| 03 | [Price elasticity](notebooks/03_price_elasticity.ipynb) | Region-by-region pricing | pathmc / hierarchical (random slopes) | core |
| 04 | [Funnel mediation](notebooks/04_funnel_mediation.ipynb) | Which funnel stage to invest in? | pathmc (mediation / path effects) | core |
| 05 | [What to control for](notebooks/05_what_to_control_for.ipynb) | Which variables belong in the model? | pathmc (DAG, colliders, sensitivity) | core |
| 06 | [Incrementality MMM](notebooks/06_incrementality_mmm.ipynb) | Is spend *causing* sales? Budget allocation | pymc-marketing (causal MMM) | legacy |
| 07 | ⭐ [Geo-lift synthetic control](notebooks/07_geo_lift_synthetic_control.ipynb) | Did the regional campaign work? | cmp.synthetic_control (Dirichlet-simplex SC, **not** CausalPy) | core |
| 07b | ⭐ [Geo-lift on real data](notebooks/07b_geo_lift_real_data.ipynb) | 07's question on **Google's real geo experiment** ($50k, 100 geos) — SC graded against the randomized answer | cmp.synthetic_control + `cmp.data.load_google_geo` | core |
| 08 | [Rollout DiD](notebooks/08_rollout_did.ipynb) | Did the loyalty rollout work? | CausalPy (difference-in-differences) | legacy |
| 09 | [Threshold perk RDD](notebooks/09_threshold_perk_rdd.ipynb) | Does the "€100 → Gold" perk retain people? | CausalPy (regression discontinuity) | legacy |
| 10 | [Redesign ITS](notebooks/10_redesign_its.ipynb) | Did the site redesign help? (no control group) | CausalPy (interrupted time series) | legacy |
| 11 | [Endogenous exposure IV](notebooks/11_endogenous_exposure_iv.ipynb) | Ad exposure is self-selected — the true effect | CausalPy (instrumental variables) | legacy |
| 11b | [Endogenous exposure on real data](notebooks/11b_endogenous_exposure_real_data.ipynb) | 11's question on **Criteo's 13.98M-user experiment** — IV graded against the full-file Wald anchor | CausalPy IV + `cmp.data.load_criteo_uplift` | legacy |

*(Numbering matches `docs/causal_marketing_cookbook.pdf` 1:1; the `b` notebooks are real-data
companions to the two quasi-experimental workhorses. They fetch public datasets on first run —
07b two ~230 KB CSVs, 11b a one-time 311 MB download — cached under `~/.cache/cmp`; every other
notebook stays fully offline.)*

The shared package **`src/cmp`** keeps notebooks thin: `dgp` (seeded simulators),
`estimators` (S/T-learner, BCF, AIPW doubly-robust, synthetic control, CausalPy wrappers,
first-stage F, simplified McCrary-style density — uniform interface), `metrics` (PEHE, coverage, Qini/AUUC,
uplift-by-decile, reliability, sharpness, E-value), `policy` (profit curve, sweeps, VOI,
policy comparison, break-even), `plots` (shared styling incl. Qini/reliability/forest/PPC),
`data` (optional real-dataset loaders).

---

## Quickstart

```bash
# 1. core environment (pymc>=6): foundations, uplift, pathmc, synthetic control, apps
uv sync

# 2. legacy environment (pymc<6): causalpy + pymc-marketing notebooks (06, 08-11, 11b)
make env-legacy

# 3. register both as Jupyter kernels
make kernels

# 4. open the learning path
uv run jupyter lab notebooks/00_foundations.ipynb
```

Then pick a kernel per notebook: **`Python (cmp core, pymc6)`** for 00–05 & 07,
**`Python (cmp legacy, pymc5)`** for 06 & 08–11 (each notebook already declares the
right one).

**FAST vs full.** Every notebook has a `FAST` switch (env var `CMP_FAST`, default `1`):
few draws/trees so it runs in **< ~2 min** for CI and live reruns. Set `CMP_FAST=0` for
full-quality runs that reproduce the reference figures.

Run the tests (executes every notebook headless + the package unit tests):

```bash
make test          # everything
make test-fast     # package unit tests only (fast)
```

---

## Running on real public data (you don't provide anything)

Notebooks default to **simulated** data so we can *validate* each method against a known truth and so the
repo runs offline. But three notebooks also fetch a **real public dataset** (over the network, from a
public URL — nothing to download or supply) to show the same method on real numbers. They're **gated on an
env var** so the offline test suite stays deterministic:

```bash
CMP_REAL=1 jupyter lab notebooks/01_uplift_targeting.ipynb   # then run the "6b" real-data cell
```

| notebook | real dataset (fetched via `cmp.data`) | what it shows |
|---|---|---|
| 01 uplift | **Hillstrom / MineThatData** — 64k customers, real *randomized* email A/B test | run the uplift pipeline on real data (no ground-truth CATE, since real customers have one future) |
| 00 foundations · 05 control | **LaLonde / NSW** job-training benchmark | naive vs adjusted estimate — the canonical "wrong controls flip the sign" demo |
| (loader only) | **IHDP** — semi-synthetic, *known* true effects (`cmp.data.load_ihdp`) | a loader is provided for grading CATE recovery on real covariates — **not** wired into a gated notebook cell (bring-your-own benchmark), unlike the two rows above |

Every other notebook explains, in its intro, exactly **what real data would look like** for that technique
and where to get it (your own CRM / sales panel / event logs; public analogues like Card–Krueger for DiD or
California Prop 99 for synthetic control) — because for those setups there is no single clean public dataset
that maps 1:1.

## Interactive apps (marimo)

Reactive explorables. For the uplift and confounding apps the expensive posterior is computed
**once** and the sliders only re-derive the decision, so they respond instantly; the synthetic-control
app re-fits on each interaction, but that's a fast SLSQP point fit plus placebo refits (~0.2 s), not a
posterior. Each also opens as a plain
notebook (`marimo edit`), and can be exported to in-browser **WASM** for the live
lecture (`marimo export html-wasm`).

```bash
make app-uplift        # discount cost / confidence bar / base size → profit, targets, €VOI
make app-confounding   # unobserved-confounder strength → ATE drift past the cost line & the decision flip
make app-sc            # pick treated market & launch week → synthetic fit, placebo spaghetti, permutation p
```

---

## Environment split — why two environments?

**This is the single biggest engineering decision in the repo, so it's stated up front.**
As of build time (2026-07), the PyMC ecosystem is genuinely split across the `pymc 5 → 6`
boundary:

- **`pymc-bart`, `bambi`, `pathmc`** require **pymc ≥ 6**.
- **`causalpy` (0.8.1)** and **`pymc-marketing` (0.19.4)** still pin **pymc < 6**.

`statsmodels` is a dependency of **both** environments: it is what `cmp.classical` (Step 0)
is built on, so every notebook needs it regardless of which side of the pymc split it sits on.

No single environment can satisfy both. Rather than hold the whole repo back to pymc 5
(losing pymc-bart 0.12 / pathmc) or vendor patched forks, this repo ships **two
environments**:

| Env | pymc | Built by | Powers |
|-----|------|----------|--------|
| **core** (`.venv`) | ≥ 6 | `uv sync` (from `pyproject.toml`) | notebooks 00–05, 07, 07b · all apps · package tests |
| **legacy** (`.venv-legacy`) | < 6 | `make env-legacy` (from `requirements-legacy.txt`) | notebooks 06, 08–11, 11b |

`cmp.estimators` imports pymc/pymc-bart **lazily** so the package imports cleanly in
both. Each notebook declares its kernel, and the test suite routes each to the right one
— so `make test` drives both from a single command. When causalpy / pymc-marketing move
to pymc 6, the two environments collapse into one (delete `requirements-legacy.txt` and
bump the pins).

---

## Design decisions (recorded as made, per the brief)

- **Cookbook source was a PDF, not the expected `.md`** — content extracted from
  `docs/causal_marketing_cookbook.pdf`; the notebook set and framing follow it verbatim,
  including the technique→library→business-question mapping.
- **Two-environment split** (above) — the one unavoidable deviation from a single pinned
  env, forced by the ecosystem's pymc-5/6 boundary.
- **The pymc-bart counterfactual gotcha is encapsulated and tested.** Scoring BART
  counterfactuals silently returns *frozen* (all-zero) effects unless the tree node is
  resampled with `sample_vars=["mu"]`. `cmp.estimators._bart_predict` always does this,
  and `tests/test_package.py::test_bart_cate_is_nonzero` fails loudly if it regresses.
- **BCF is the default for the observational uplift work**, T-learner the default for
  the randomized case; the **S-learner is kept only as a labelled failure-mode demo**
  (it flattens heterogeneity — shown explicitly in Anchor A's bake-off).
- **Notebook 03 (price elasticity) uses an explicit hierarchical PyMC model** rather than
  pathmc's partial-pooling, because pathmc 0.1.1 doesn't expose per-region random slopes
  cleanly. The identification framing (log-log demand, backdoor set) is unchanged; the
  shrinkage is fully visible. Endogenous price is shown biasing elasticity *toward zero*
  (classic simultaneity), which pooling can't fix — the bridge to IV (nb 11).
- **Notebook 06 (MMM) is honest about MMM's weakness.** The causal MMM ranks the channels
  correctly (TV above brand_search) but its *absolute* levels run high: the **true ROAS of
  both channels is below the 1× break-even** (TV ≈ 0.85×, brand_search ≈ 0.14×) while the
  MMM reports TV at ≈ 2.08×, so the notebook trusts the **ranking, not the levels**. Computed
  draw-wise, the posterior backs "TV beats brand_search" with only **P ≈ 0.78**, below the 0.8
  action bar, so the honest call is **test before reallocating**, not "shift budget now." It
  leads with the robust naive-vs-adjusted confounding contrast (OLS), reports **ROAS**
  (revenue-per-euro, with a margin break-even — 30% margin needs 3.3×, which even TV's estimate
  fails), and says to **calibrate MMM levels with a geo experiment (Anchor B)**. Real practice.
- **Notebook 07 (Anchor B) is a manual Bayesian synthetic control, not CausalPy.** CausalPy
  0.8.x cannot install in the core (pymc ≥ 6) env, so Anchor B uses `cmp.synthetic_control` —
  a Dirichlet-simplex donor-weight model fit in raw PyMC — rather than a library wrapper. The
  `cmp.estimators` CausalPy SC wrapper exists but is unused here; the technique-index table
  reflects this (the row reads `cmp.synthetic_control`, not CausalPy).
- **CausalPy APIs were pinned to 0.8.x reality**, which has drifted from the cookbook's
  0.5-era skeletons: DiD needs a `post_treatment` bool + a `unit` label and the 2×2
  (pre/post-collapsed) data form (collapsing to two periods is also the Bertrand–Duflo–
  Mullainathan 2004 serial-correlation guard, not merely an API shape); RDD needs a dummy-coded `treated` column and a
  bandwidth; ITS needs numeric (not categorical) seasonality to survive the pre/post
  patsy split; IV runs with `cores=1` to dodge a multiprocessing `EOFError`. All baked
  into `cmp.estimators`.
- **Anchor B lands on a genuinely borderline "TEST FURTHER" decision** (P(lift>cost)≈0.6)
  rather than a tidy GO — synthetic control's mild conservatism pulls the estimate onto
  the break-even line. Left honest, because it's a better lesson than a manufactured win:
  *the interval, not the point estimate, drives the call.*
- **Simulated data is the default everywhere** so the whole repo runs offline and
  reproducibly. `cmp.data` provides opt-in loaders (Hillstrom email uplift; Lalonde/NSW;
  IHDP) with licensing notes — fetched, never vendored.

---

## Source materials (`docs/`)

The authoritative content this repo ports and extends:

- `causal_inference_primer.pdf` — foundations → basis for notebook 00.
- `causal_marketing_cookbook.pdf` — the 11 techniques, master index for the notebook set.
- `uplift_in_depth.{py,pdf}` — reference implementation for Anchor A.
- `geolift_in_depth.{py,pdf}` — reference implementation for Anchor B.

## Reference points

Rubin (potential outcomes) · Pearl (do-calculus, backdoor/front-door, mediation) ·
Imbens–Angrist (LATE) · Chipman–George–McCulloch (BART) · Hahn–Murray–Carvalho 2020
(BCF) · Künzel et al. 2019 (meta-learners) · Abadie et al. (synthetic control) ·
Goodman-Bacon / Callaway–Sant'Anna (staggered DiD) · Cinelli–Hazlett 2020 (sensitivity).

## License

MIT. Simulated data and code are free to reuse; public datasets referenced in
`cmp.data` carry their own licenses (noted in the loaders).
