# Final Independent Re-Grade (P11) — Causal-Inference-for-Marketing Cookbook

*SDA Bocconi MBA lecture material · PyMC / CausalPy / pymc-marketing / pathmc*
*Basis: a 17-artifact re-grade + 5 deep audits; every material finding adversarially re-verified (skeptics re-ran the DGP + estimator). Only CONFIRMED/PARTIAL findings are reported below — REFUTED findings were discarded.*

> **Update (2026-07-10) — the §6 punch-list is closed.** The 4 must-fix majors + 5 recommended minors + 2 companions from §6 were fixed after this report: the 4 affected notebooks were re-executed FULL, all 12 PDFs regenerated, and the suite is green (core 39 · legacy 4 · kernelspec 12). See the **P11 fixes** entry in [RECONCILIATION.md](RECONCILIATION.md). The findings below are retained as the point-in-time record of what the independent re-grade surfaced; the remaining minor/polish tail (§4–§5) is the documented, deferred remainder.

---

## 1. Verdict

**The cookbook is lecture-ready and, on the axis that is graded hardest, statistically watertight.** Across the twelve notebooks the mean watertight score is **4.0/5** (up from ~3.1 where prior axes were recorded), and the deep audits that matter most for this brief both PASS: the statistical-core audit found *"No genuine statistical defect (wrong math / broken estimator)"*, and the reproducibility audit confirms every seed-stable committed number re-derives to the digit and every headline fit is convergence-clean (the only exceptions are the benign pymc-bart BCF at r-hat 1.020, which is non-seed-reproducible and cross-checked against the AIPW CI, and nb06's *deliberately-broken* default-prior MMM in the fail→fix narrative). All **27/27 originally-critical defects are genuinely closed** and independently re-verified. The important caveat is that the fix work, while real, introduced a cluster of **narration-vs-output contradictions** — three of them major-severity — that survived verification: none corrupts a computed number (the surviving majors are a false-positive falsification verdict left un-reconciled, a "how to read this" cell describing a figure panel that a fix removed, an "UNBIASED" claim printed next to its own +1.5 bias, and a legacy test-suite that exists but is not wired into CI). These are cheap to fix but must be fixed, because they are precisely the *speaker-refuted-by-the-slide* errors a sharp MBA audience catches. Net: the statistics are sound and reproducible; the residual risk is presentational, concentrated in a short, well-localized punch-list.

---

## 2. Scorecard

Grades are **new (old)** per axis; **watertight is bolded** as the load-bearing axis. Code/infra artifacts are graded holistically.

| Artifact | Diag | Bus | Narr | Val | **Water** | Overall (was) |
|---|:--:|:--:|:--:|:--:|:--:|---|
| nb00 — Foundations | 4 (2) | 3 (2) | 5 (5) | 4 (3) | **5 (4)** | good (adequate) |
| nb01 — Uplift targeting (Anchor A) | 4 | 4 | 4 | 4 | **4** | good (adequate) |
| nb02 — Segment effects | 4 (2) | 5 (4) | 4 (4) | 4 (3) | **4 (4)** | good |
| nb03 — Price elasticity | 4 (2) | 4 (3) | 4 (4) | 4 (3) | **4 (3)** | good |
| nb04 — Funnel mediation (pathmc) | 3 (2) | 3 (2) | 4 (4) | 3 (3) | **3 (2)** | good (adequate) |
| nb05 — What to control for | 4 (3) | 4 (2) | 4 (4) | 4 (2) | **4 (2)** | good (adequate) |
| nb06 — Incrementality MMM | 3 | 4 | 4 | 3 | **4** | good (adequate) |
| nb07 — Geo-lift SC (Anchor B) | 5 (4) | 5 (4) | 5 (4) | 5 (4) | **4 (4)** | good |
| nb08 — Rollout DiD | 4 (3) | 4 (3) | 4 (4) | 4 (3) | **4 (3)** | good (adequate) |
| nb09 — Threshold perk RDD | 4 (3) | 4 (2) | 4 (4) | 4 (2) | **4 (4)** | good (adequate) |
| nb10 — Redesign ITS | 4 (2) | 4 (2) | 4 (4) | 4 (2) | **4 (2)** | good (adequate) |
| nb11 — Endogenous exposure IV | 4 (4) | 4 (3) | 4 (4) | 4 (3) | **4 (3)** | good (adequate) |
| src/cmp — statistical core | — | — | — | — | **holistic** | good (adequate) |
| src/cmp — simulators / policy / loaders / plots | — | — | — | — | **holistic** | good (adequate) |
| Tests, CI, build & reports infra | — | — | — | — | **holistic** | good (adequate) |
| marimo apps (3) | — | — | — | — | **holistic** | good (adequate) |
| README & repo claims | — | — | — | — | **holistic** | good |

**Average watertight (12 notebooks): 4.0/5.** On the 10 notebooks whose prior axes were recorded it rose from **3.1 → 4.0** (+0.9); nb04 (W3) is the sole notebook below 4, held there by the newly-introduced false-positive falsification verdict. Every artifact grades **good** overall; nb07 is near-flagship (D5 B5 N5 V5 W4). No artifact grades below good.

---

## 3. Reconciliation of the ledger

The fix ledger (`docs/RECONCILIATION.md`) claimed **27/27 criticals closed · ~87/95 majors closed · ~192/210 total closed · ~18 open**. The audits find this tally **broadly DEFENSIBLE, and airtight on the criticals — but the OPEN set is not complete.**

**Criticals — 27/27 CONFIRMED closed, none found still-open.** The fix-ledger-verification deep audit (verdict PASS) states: *"No claimed-closed critical or major was found still-open."* It re-ran the four highest-value P4 criticals against committed code: nb01's coverage now carries an honest run-stable under-coverage caveat; nb05's pathmc-vs-bar-chart discrepancy is resolved into the DAG-falsification lesson (`test_implications` p≈1.3e-19, DGP confirms `opened_email` is an unobservable collider via `engagement_trait`); the marimo uplift explorer splits confidence/rank-stop/oracle into three distinct computations; and nb02's planted truth is consistent DGP↔prose↔output. The statistical-core critical (e_value's inverted no-sd fallback) is deleted and now raises `ValueError` with a direction-pinning test; the src/cmp random-50% seed-collision critical is decoupled (`SeedSequence(seed).spawn(1)[0]`, random baseline now a true −€712 negative); the CI-is-dead critical is fixed on all three legs (root location, `main`-branch trigger, working-directory scoping). **Every claimed-closed critical holds.**

**Majors — the "~87 closed" holds for the overwhelming majority, but four majors survive verification and the ledger's open set missed three of them.** (The overclaim-sweep deep audit additionally rated two further items as *major* — nb01's 1.5-vs-2.0 tipping-point contradiction and nb09's fabricated four-cutoff placebo list — but per-artifact adversarial re-verification downgraded both to *minor* because in each the GO/NO-GO decision does not flip and the slip is documentation-only; the surviving-major count therefore stands at four, not six, and both are carried below as minors #7 and #20.) Each per-notebook reconciliation independently confirms its majors closed with seed-stable numbers re-derived to the digit. The exceptions:

- **Three NEW major defects the fixes introduced and the ledger did not list.** The per-artifact skeptics and the overclaim-sweep deep audit (verdict **CONCERN**) caught all three: nb04's added falsification test ships an unreconciled false-positive verdict *"graph is contradicted by the data"* (nb04 reconciliation: *"WHERE THE LEDGER MISSED … two new blemishes the ledger did not catch"*); nb10's missing-figure fix left cell 7/10 markdown narrating a 3-panel figure that now renders 2 (nb10 reconciliation: *"the OPEN set is INCOMPLETE"*); nb11's validation-fix cell prints *"the estimator is UNBIASED on average"* over its own reproduced +1.5 bias (nb11 reconciliation: *"The one genuine residual is NOT in the ledger"*, and validation-honesty deep audit confirms a real ≈3-SEM finite-sample 2SLS bias toward OLS).
- **One major the ledger over-claimed as closed.** The infra audit: adding `tests/test_estimators_legacy.py` is *"presented as closing the 'legacy stack untested' major, but that file is invoked by no CI step and is import-skipped in the core env"* — verified: `pytest tests/test_estimators_legacy.py` under the core env returns `1 skipped`, and the string `test_estimators_legacy` appears only in `Makefile` (`make test-legacy`), never in `ci.yml`. The four legacy truth-recovery guards (DiD/RDD/ITS/IV) run in no automated gate. Closure is only half-true.
- **One minor the ledger mis-states as done.** src/cmp: *"the RECONCILIATION mis-states as done ('cost_sweep 0-baseline')"* — `cost_sweep` got the zero-baseline fix but its sibling `profit_curve` (policy.py:20-24, named in the same original finding) did not.

**Total / open.** The ~192/210-closed and ~18-open counts are defensible in aggregate, but the true open set is **larger than 18**: it must additionally carry the 3 newly-introduced majors, the over-claimed infra major, and roughly a dozen newly-introduced minor/polish slips the fixes created (tipping 1.5-vs-2.0, "90% HDI" mislabel, shrinkage-formula regression, "opposite decision" overclaim, €836-vs-€61, stale 4-cutoff list, and the recurring fast-recovery-loop sampler-warning noise). **No new open *critical* exists** — the statistics reproduce and no committed computed number contradicts its prose. The gap is entirely at major-and-below and entirely presentational/plumbing.

---

## 4. Surviving defects, ranked most-severe first

Every row below survived adversarial verification (CONFIRMED unless marked PARTIAL). **Kind** = *fix-intro* (newly introduced by the fix work) vs *open* (pre-existing, still open). Disclosed-deferred items are pulled out into §5 and are **not** counted here as regressions.

### 4a. Genuine surviving defects

**MAJOR (4)**

| # | Artifact | Loc | Defect (one line) | Kind |
|---|---|---|---|---|
| 1 | nb04 | Cell 8 output | Added falsification test prints *"graph is contradicted by the data"* (1/3 implied independences rejected — a benign Type-I chance rejection of the truly-independent `channel_quality ⊥ onboarding_score`), never reconciled; flatly contradicts the notebook's *"we can trust it"* / *"recovers the truth"* thesis. | **fix-intro** |
| 2 | nb10 | Cell 10 & Cell 7 markdown | "How to read this" narrates a **3-panel** figure (*"Left — the cumulative impact … climbs steadily"*, Middle=placebo, Right=ACF) but cell 9 now renders **2 panels** (placebo + ACF); the "Left" prose points at a placebo bar chart. Same defect class as the original critical it was meant to fix. | **fix-intro** |
| 3 | nb11 | Cell 11 | *"the estimator is UNBIASED on average"* printed adjacent to its own output *"bias +1.5 … covers truth in 16/20 seeds"* — a genuine ~10% (≈3.2-SEM) finite-sample 2SLS bias toward OLS (Wald on identical seeds recovers 15.12), not sampling noise; cell 9 compounds it by calling the gap "finite-sample noise." | **fix-intro** |
| 4 | infra | `ci.yml`, `Makefile:57` | Legacy truth-recovery suite `test_estimators_legacy.py` (DiD/RDD/ITS/IV recover-the-truth guards) runs in **no CI job** and import-skips in the core env; a legacy wrapper returning a fitted-but-wrong object passes CI green. Ledger over-claimed this major closed. | **open** |

**MINOR (37)**

| # | Artifact | Loc | Defect (one line) | Kind |
|---|---|---|---|---|
| 5 | nb03 | Cell 4 | Shrinkage factor printed as `1 − τ/(τ+σ²/n)` with **τ unsquared** (an SD added to a variance); correct is `τ²/(τ²+σ²/n)`. The one printed math slip; git history shows the polish sweep dropped the squares an earlier revision had. | **fix-intro** |
| 6 | statcore | estimators.py:289 / test_package.py:176 | AIPW bootstrap `ci90` under-covers the true ATE (**76% vs 90%** at n=1500); the guarding test checks only point-in-own-CI + \|point−truth\|<1.5, never truth-coverage. Point estimate is unbiased/consistent; disclosed as a cross-check. | **open** |
| 7 | nb01 | Cell 31 vs Cell 28 | Decision paragraph says confounder tips the cost line at *"≈ 1.5"*; the notebook's own cell computes/prints and JSON stores **2.0** (at 1.5 the confounded ATE is still below €8). | **fix-intro** |
| 8 | nb02 | Cell 15 | Coverage intervals labeled *"90% HDI"* but computed from `c.hdi()`, whose pathmc default is **94%** (`DEFAULT_HDI_PROB=0.94`). | **fix-intro** |
| 9 | nb05 | Cell 18 | *"Same data, different control set, opposite decision"* precedes a table where **all five** sets (€9.45…€4.97) clear the €2 break-even and print **GO** — no flip actually occurs. | **fix-intro** |
| 10 | nb06 | Cell 15 | "Decision quantity WITH uncertainty" = **€836** at *average* ROAS, ~**13×** the notebook's own saturation-aware **€61** for the same 15% shift; P(Δ>0)=0.78 band is the ranking probability rescaled (hollow). PARTIAL (major→minor: both numbers are printed & labeled, narrative hedges). | **fix-intro** |
| 11 | nb02 | Cell 13 | *"tracks the true … line across the whole engagement range"* — the recovered engagement slope is €10.19 vs planted €8.0 (+27%); truth exits the fitted 90% band over the upper half of the range. | **fix-intro** |
| 12 | nb06 | Cell 13 | *"landing beside the true bars (green)"* — calibrated levels are 2.4×–4.4× truth, contradicting the same section's *"overstates LEVELS ~2.4×"*. | **fix-intro** |
| 13 | nb06 | Cell 10 | Calibrated fit prints rounded *"max r-hat 1.010"* while PyMC's *"rhat > 1.01 … problems during sampling"* warning fires two lines above; unreconciled (`.3f` rounding masks a sub-rounding excess). | **fix-intro** |
| 14 | nb07 | Cell 22/23 | Launch-sensitivity benchmark stays **flat at 17.0** for assume-earlier mis-dating instead of diluting to the estimate's averaging window; figure contradicts the dilution narration on the more common mis-dating direction. | **open** |
| 15 | nb10 | Cell 14 | Verdict summary calls the 1-month-persistence scenario a *"re-test"* while its own table classifies it *"roll back / renew"* (P(value>cost)=0.00). | **fix-intro** |
| 16 | nb01 | Cell 31 | Stale *"In FAST mode … a full-quality run tightens it"* caveat survives in a FULL (FAST=False) commit and misattributes intrinsic BCF top-decile under-coverage (committed 85%) to FAST coarseness. | **open** |
| 17 | nb03 | Cell 14 | Endogenous rerun hard-codes `draws=300, chains=2`; committed output carries an unaddressed *"rhat > 1.01"* warning immediately after the headline's clean-convergence banner. | **open** |
| 18 | nb03 | Cell 8/9 | "Unfair baseline" major closed by **disclosure only**; no-pool/complete-pool remain bivariate polyfits omitting Z, so the *"Partial pooling wins"* MAE figure still conflates pooling with covariate adjustment. | **open** |
| 19 | nb04 | Cell 5/6 | `effects_summary()` HDI table never renders (a `print` became the last statement, discarding the expression); cell-5 prose points readers to it. Loses the only per-coefficient diagnostic table. | **fix-intro** |
| 20 | nb09 | Cell 11 | How-to-read cell lists **four** placebo cutoffs (€70, €80, €120, €130); code/figure run only **two** (€70, €130). €80/€120 appear nowhere in code or output. | **fix-intro** |
| 21 | nb08 | Cell 11 | Multi-seed recovery loop hard-codes `fast=True` (2 chains/200 draws), flooding the committed FULL output with *"problems during sampling"* / *"ESS < 100"* blocks, disclosed only as "a small fast fit each." | **fix-intro** |
| 22 | nb11 | Cell 11 | Multi-seed cell hard-codes `fast=True`, so ~20 sampler warnings appear **even under CMP_FAST=0**; per-seed fits feeding bias/coverage are themselves under-converged (`.ipynb` not convergence-clean; PDF is stripped). | **open** |
| 23 | nb10 | Cell 12 | Fast-recovery loop leaves ~30–40 *"problems during sampling"* / ESS<100 warnings in committed output; markdown discloses only "a small fast fit each." | **open** |
| 24 | nb02 | Cell 15 | ~45 sampler-quality warning lines (16× rhat>1.01) in the committed recovery loop; PDF is clean via the NOISE filter, the `.ipynb` is not. | **fix-intro** |
| 25 | nb07 | Cell 9 | Multi-seed calibration loop runs under-converged `draws=300` mini-fits and ships ~11–15 uncaveated sampler warnings one cell after the headline reports a clean fit. | **fix-intro** |
| 26 | simpolicy | policy.py:20-24 | `profit_curve` still lacks the zero baseline (`argmax` forces ≥1 contact even when the optimum is to contact nobody); sibling `cost_sweep` was fixed — the two halves of one finding now disagree. Ledger mis-states as done. | **open** |
| 27 | statcore | estimators.py:140-170 | `s_learner`/`t_learner` return bare CATE arrays with no `idata`, so nb01's bake-off CATE surfaces expose no per-fit r-hat/ESS/divergence readout. | **open** |
| 28 | nb03 | Cell 14 | Endogeneity bar chart still has no "how to read this" cell (only the decision figure got one); the original pedagogical minor named both. | **open** |
| 29 | nb04 | Cell 13 | Rebuilt M-Y sensitivity sweep is means-only (no credible band) and sweeps only the engagement→converted edge, never activated→converted. | **open** |
| 30 | nb04 | Cell 14 | Caveat 4 (*"lean on pathmc's numbers, not hand-multiplied coefficients"*) is muddy: `effect(path)` **is** the product-of-coefficients; the valid nonlinear route (`do()`/`ate()`) is never named. | **open** |
| 31 | nb04 | Step 6 / Cell 13 | Opening "fixed budget to split across the funnel" is answered as a *ranking*, not an *allocation*: flat illustrative €100/SD cost, no budget-split/VOI, P(ROI>1)=1.0 for all three levers (uninformative). | **open** |
| 32 | nb05 | Cell 19-20 | LaLonde sign-flip claim is CMP_REAL-gated; committed output reads *"Real-data section skipped"*, so the ~$1,800 recovery appears only as prose; naive qualifier is hardcoded. | **open** |
| 33 | nb09 | Cell 15 | Go/no-go `0.9` decision bar and `N_AT_MARGIN=3000` headcount used unexplained in prose (core of the business major — cost sweep + "RD can't set the cutoff" box — is closed). | **open** |
| 34 | nb04 | whole nb | Validation is single-seed only (no multi-seed recovery/coverage); disclosed-consistent with peers, not a regression. | **open** |
| 35 | repro | nb01 BCF | Headline prints *"max r-hat 1.020"* — above the ~1.01 bar — with no prose caveat (pymc-bart, non-reproducible; NUTS scalars scoped; estimate cross-checked inside AIPW CI). | **open** |
| 36 | repro | make_reports.py:45-57 | Two NOISE regex alternatives (`Metropolis`, `We recommend running at least`) are over-broad — latent fail-open if such business sentences are ever added; **no committed line is currently harmed** (1084 stripped lines all genuine noise; item-5 canary survives). | **open** |
| 37 | infra | `synthetic_control_cp` | 4 of 5 CausalPy wrappers have truth-recovery tests; `synthetic_control_cp` has none in any environment. | **open** |
| 38 | infra | notebooks/*.ipynb | Zero in-cell `assert`s across all 12 notebooks; FAST runs test executability only. Guards moved to the package layer by design; a notebook composition/aggregation regression is undetectable by the suite. | **open** |
| 39 | infra | Makefile:51-52 | Local `make test` has no `kernels` prereq / no `CMP_STRICT_KERNELS`, so on a fresh machine all 12 notebook tests skip and the suite exits green. **CI is safe** (registers kernels + STRICT=1). | **open** |
| 40 | apps | uplift_policy_explorer.py | BCF coarse-posterior MAJOR only partially closed: CMP_FAST wiring is in, but no on-screen fast-posterior caveat / ESS-r-hat surfacing, and the committed snapshot is a fast build (622/1000 straddlers). | **open** |
| 41 | readme | README.md:207 | *"verbatim, including the technique→library→business-question mapping"* contradicts two disclosed library deviations in the same section (nb03 pathmc→hierarchical PyMC; nb07 CausalPy→Dirichlet-simplex SC). | **open** |

**POLISH (14)**

| # | Artifact | Loc | Defect (one line) | Kind |
|---|---|---|---|---|
| 42 | nb00 | Cells 3/4, figs 7/14 | Three-customer table's numeric punchline (observed −€4 vs true +€19) not computed; no dedicated "how to read this" cells under the two main figures (`grep "how to read"` = 0 vs siblings' 1–2). Mitigated by interpretive titles/prose. | **open** |
| 43 | nb01 | Cell 3 | Refixing "persuadable = τ>0" leaves the "sure thing / lost cause" type memberless (τ never exactly 0): four types taught, two printed. | **fix-intro** |
| 44 | nb01 | Cell 17 | 8× *"Only 80 samples per chain"* warnings in committed FULL output (deliberate short chains in the stability sweep; posterior means only). | **open** |
| 45 | nb02 | Cell 16 | *"the … SEND/TEST/SKIP table above"* — that table is produced in cell 17, immediately **below** (inverted cross-reference). | **fix-intro** |
| 46 | nb05 | Cell 18 | `sens.observed_ate_hdi` (already computed by pathmc) never printed; only the point €6.09 is shown. Partially compensated by the 30-seed ±2sd bars. | **open** |
| 47 | nb06 | Cells 7/10 | Stray `Output()` rich-progressbar remnant in committed output, now twice (one per fit). | **open** |
| 48 | nb08 | Cells 7-9 | No posterior predictive check anywhere (every other diagnostic is present). | **open** |
| 49 | nb10 | Cell 7 | Bayesian R² *"~0.74"* hard-coded in prose, echoed in no printed output (only the CausalPy figure header) → silent-drift risk. Low-confidence; figure value verified ~0.736. | **open** |
| 50 | simpolicy | policy.py:137-138 | Leftover inline comment claims the loop "expose[s] the CATE-driven decision uncertainty" — contradicts the corrected docstring (profit is deterministic; masks are fixed). | **open** |
| 51 | apps | uplift_policy_explorer.py:92 | Deployable "rank & stop" policy `argmax(cumsum(...))` has no zero baseline → can't choose "contact nobody"; latent (never hit at the capped cost slider). | **fix-intro** |
| 52 | statcore | estimators.py:36-77 | pymc-bart's BART Manager intermittently raises `EOFError` on fit — environmental/library flakiness, not a code defect; can surface as a transient rerun failure. | flakiness |
| 53 | statcore | estimators.py:270-273 | AIPW cross-fit degenerate-fold guard (all-treated/all-control training arm) untested; not reachable at committed n=1500/5-fold/balanced. Ledger-absent edge. | **open** (latent) |
| 54 | metrics | metrics.py:40-41 | `interval_coverage` by-decile uses `qcut(...,duplicates='drop')`; with heavily-tied `tau_true` the returned index wouldn't be 0..9. Clean for the committed continuous τ. Ledger-absent edge. | **open** (latent) |
| 55 | apps | confounding_sensitivity.py, synthetic_control_placebo.py | Committed marimo session-snapshot caches for the two figure-fix apps were never regenerated after the figure fix, so the committed `__marimo__` record still shows **empty plots** even though `marimo run` renders them correctly; stale committed-snapshot hygiene only — live app and every number unaffected. | **open** |

**Two recurring patterns worth naming.** (a) *Fast recovery-loop noise* (#21–25, plus #44): every multi-seed loop added to close a "single-seed validation" major hard-codes small fast fits and leaves sampler warnings in the committed `.ipynb` — the PDFs are clean via the NOISE filter, but the notebooks shown live are not. (b) *Prose drifted from the fixed figure/code* (#7, #8, #9, #15, #20, #45, plus majors #1/#2): several fixes updated the code/figure but not the surrounding markdown, producing the internal contradictions above.

### 4b. Deferred items that appear as surviving findings

These are the disclosed deferrals (see §5), verified as accurately still-open and honestly documented — **not regressions**:

| Artifact | Loc | Deferral | Disclosure |
|---|---|---|---|
| nb05 | Cell 0 / dgp.py:243-272 | Mediator & M-bias gallery roles never demonstrated in euros; *"(c) show the bias of each wrong choice in euros"* over-promises for 2 of 4 roles | `RECONCILIATION.md:212-213` (item #1) |
| nb06 | whole nb | No PPC, no multi-seed MMM stability, no adstock/saturation recovery vs DGP truth | `README:73` (item #2) |
| apps | synthetic_control_placebo.py:72,78 | Truly-treated `dma_00` stays in donor + placebo pools when another market is selected; no on-screen caveat | ledger item #6 |
| apps | confounding_sensitivity.py:54-63 | Single-seed tipping curve sits at percentile-0 of the seed distribution; ~86% of the first slider step's jump is a pure RNG-stream artifact at s=0, not confounding | ledger item #7 |

---

## 5. The deferred tail

The **~8 knowingly-deferred majors** remain the honest, documented remainder — each was independently re-checked and confirmed still-open **and** disclosed in-notebook / in-docstring / in-README, so none is a silent gap:

1. **nb05 — mediator / M-bias never demonstrated empirically.** Only confounder/collider/post-treatment roles are quantified in euros. Disclosed at `RECONCILIATION.md:212-213`; deferred because it requires changing `dag_control_demo`.
2. **nb06 — no multi-seed MMM stability / PPC / adstock recovery.** True ROAS and direction are checked; coverage/stability/parameter-recovery are not. Disclosed at `README:73` (*"the MMM is too costly to multi-seed"*).
3. **nb11 — LATE = ATE only because the planted effect is homogeneous.** Now stated explicitly in cell 7 (*"homogeneous effect ⇒ LATE=ATE ⇒ fair test"*); the +21pp first stage is labeled the complier share. Closed-by-disclosure.
4. **estimators.bcf — tau forest passes `Y=y`, not effect-scale.** Outcome-level prior; caveated in both the docstring and an inline comment. The statistical-core audit confirms this is the single disclosed deferral there.
5. **nb03 — euro decision lacks a 3-policy comparison + VOI.** The key gap (profit uplift with a 90% interval) is now present; the 3-policy/VOI depth is deferred.
6. **marimo synthetic_control_placebo — keeps the treated market in the donor pool.** Verified: selecting `dma_05` gives `dma_00` a synthetic weight 0.084 and `dma_00` passes the Abadie RMSE gate into the null. Disclosed deferral.
7. **marimo confounding_sensitivity — single-seed tipping point, no MC band.** Verified: seed 7 sits at the **minimum** of the 30-seed distribution, and the s=0 RNG-stream shift dominates the first step. Disclosed deferral.
8. **A small minor/polish tail** (the residual "how to read this" / cross-reference / cosmetic items above).

The fix-ledger-verification deep audit explicitly confirms: *"The ~8 disclosed-deferred majors … are all accurately still-open and honestly disclosed in-notebook."*

---

## 6. Bottom line

**Genuinely done.** The statistics are watertight and reproducible: 27/27 criticals closed and re-verified; no surviving defect is a wrong computed number; every seed-stable committed figure re-derives to the digit under the notebook's own env; every headline fit is convergence-clean except the two understood, disclosed exceptions (pymc-bart BCF 1.020; the deliberate nb06 fail-case). The statistical core, simulators/policy math, README claims, and CI-reachability are all verified sound (27/27 core + 4/4 legacy tests green; AIPW genuinely cross-fits; SLSQP clips to the simplex; McCrary is scale-invariant with a real binomial z; the NOISE filter no longer fails open on any committed line). Anchor B (nb07) is near-flagship.

**Must fix before the lecture (the three narration majors + one repo-health major).** All are cheap and high-value because they are *slide-refutes-speaker* contradictions in projected output:
1. **nb04 cell 8** — add one sentence reconciling the false-positive falsification verdict (chance rejection at α=0.05, 1 of 3 tests, no multiple-comparison correction), or re-seed so the true independence isn't rejected. As shipped it prints *"graph is contradicted by the data"* under a "we can trust it" thesis.
2. **nb10 cells 7 & 10** — rewrite the two markdown notes to match the 2-panel figure (placebo + ACF); delete the "Left — cumulative impact" panel description and the "shows up in this figure" claim.
3. **nb11 cell 11** — change *"the estimator is UNBIASED on average"* to "small residual finite-sample bias toward OLS (+€1.5, ~10%)"; fix cell 9's "finite-sample noise" wording.
4. **infra `ci.yml`** — add a CI step (or a legacy job) that invokes `test_estimators_legacy.py` so the legacy truth-recovery guards actually gate merges.

**Recommended before the lecture (student-catchable minors).** nb03 cell 4 shrinkage formula (restore the squares: `τ²/(τ²+σ²/n)`); nb01 tipping "≈1.5"→2.0; nb02 "90% HDI"→94%; nb05 "opposite decision" (either move the break-even near €5.5 to make a real flip or soften the claim); nb09 stale four-cutoff placebo list→two. Optionally, gate the multi-seed recovery loops on the FAST flag so the committed `.ipynb`s are as clean as their PDFs.

**Verdict stands: lecture-ready and statistically watertight, pending a short, well-localized narration/plumbing punch-list — nothing that corrupts a number.**