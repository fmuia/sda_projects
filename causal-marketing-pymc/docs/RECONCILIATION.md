# Reconciliation ledger — comprehensive review vs. what's committed

**Purpose.** The comprehensive Workflow review ([ASSESSMENT.md](ASSESSMENT.md)) surfaced **210 verified
findings** (27 critical · 95 major · 69 minor · 19 polish). This ledger reconciles them against what the
fix work (P0–P3 + the FULL-mode run + convergence reporting + the nb06 rewrite) actually closed, so the
remaining scope is explicit. Built by hand from the applied-fix tables + current code/notebook state.

> **Two structural gaps up front:**
> 1. **The Workflow re-grade was never run.** The assessment explicitly holds grades "pending a full
>    workflow re-grade" ([line 53](ASSESSMENT.md#L53)) / "a full re-grade awaits a workflow re-run"
>    ([line 22](ASSESSMENT.md#L22)). Re-running the comprehensive review to re-verify + re-score is a
>    named deliverable that has not been done. (It's a 100+-agent Workflow.)
> 2. **The roadmap (P0–P3) was a *prioritized subset*, not the whole plan.** It targeted the criticals and
>    a slice of majors. Most majors + nearly all minors/polish were never scheduled.

## Headline

| Severity | Total | Closed | Open | Notes |
|---|:--:|:--:|:--:|---|
| 🔴 Critical | 27 | **27** | **0** | the last 4 were re-verified + fixed in **P4** (all needed real fixes) |
| 🟠 Major | 95 | **~87** | **~8** | **re-triaged against current code — the ~32 was stale.** P3 CI + FULL run + nb06 rewrite + P5/P8/P9 closed most; a dedicated **majors pass** (6-agent re-triage + fixes) then closed nb04 falsification+naive-OLS, nb02 test_implications, nb00 overlap/balance, nb09 placebo-cutoff contamination + perk-cost sweep, nb07 Depth-A read-out + launch-date benchmark, AIPW-independence & treat-none wording, legacy-lock/CI parity, RDD + fragile-stat tests. AIPW cross-fit / mccrary z-test / go_no_go ROI were already done. |
| 🟡 Minor | 69 | **~62** | ~7 | + **P10** full notebook sweep (all 11 re-exec'd FULL): "90% CI"→credible-interval, pp-vs-%, estimand-vs-estimator (07), number-conditioned verdicts (01), ρ-extraction (11), pre-RMSE PASS/FAIL gate + DiD comparator (07), confounder reframes, LATE-at-cutoff footnotes |
| ⚪ Polish | 19 | **~16** | ~3 | + **P10** notation/label/figure polish across the suite (𝔼[·] notation, DAG arrowheads, axis labels, band-level labels, legend precision, warnings scoping, stray-`Output()` strip) |
| **Total** | **210** | **~192** | **~18** | remaining ≈ 8 majors (below) + a small minor/polish tail; + the Workflow re-grade (process step) not run |

> **P5 done (validation depth — the biggest cluster).** Added a **"5b · Recovery across many seeds"** section
> to **nb02, nb05, nb08, nb09, nb10, nb11** — each refits on many fresh samples (small fast per-seed fits, so
> the loops stay cheap even at FULL) and reports **recovery bias + how often its interval covers the truth**.
> Results (FULL): nb02 CATE **19/20** coverage (bias ±0.05); nb05 the DAG-endorsed `{loyalty}` is the only
> **unbiased** set (−0.08) while collider/over-control sets carry a *persistent* bias (−0.49 to −1.04, with ±2sd
> bars now on the five-bar chart); nb08 DiD **20/20** (€403, bias +3); nb09 RDD **23/25 ≈ 92%** (near-nominal);
> nb10 ITS **17/20** (+3.00pp, bias −0.00) **plus a placebo-DATE sweep** (4 pre-period fakes, all ≈0); nb11 IV
> **16/20** (mean €16.5 across seeds — the honest calibration view showing the committed seed-37 €18 is one
> draw, the estimator is unbiased on average). README's multi-seed claim broadened to the 9 notebooks that now
> carry it (03/04/06 use method-appropriate validation instead, stated honestly). Batched FULL run: core
> (nb02/05) + legacy (nb08/09/10/11), ~7 min; sampler noise from the loops is stripped by the (now
> fail-safe) NOISE filter, so PDFs show only the clean summaries. **Closes ~7 majors + validation-axis minors;
> lifts the Validation axis off "2" across the suite.**

> **P10 DONE (minor + polish sweep — the whole tail).** Triaged all 88 minor/polish items against current
> state (16 non-notebook already closed by earlier phases), then closed the rest in three batches.
> **Batch 3 (`b09dc1a`, code side, no re-exec):** `src/cmp` — S-learner scores both counterfactuals in ONE
> posterior-predictive call (within-draw paired CATE), `sc_weights_slsqp` clips to simplex + warns on
> non-convergence, `cost_sweep` 0-baseline so a high cost reports "contact nobody", `policy_comparison`
> docstring four→five, `recovery_scatter` spans truth+estimates (no silent crop), `draw_dag` bigger
> arrowheads, `placebo_spaghetti`/`sc_counterfactual_plot` axis-label params, `forest_plot` log-x + annot,
> **new `metrics.qini_observed`** (Radcliffe Qini on real RCT data, no τ); `make_reports` anchor-star →
> "" (was duplicating "ANCHOR"); confounding app notes OLS≠ATE at zero confounding; SC app surfaces the
> p-value denominator (kept donors + 1/(N+1) floor); README nb00 label + DiD-2×2 reframe. Earlier
> batches (`dafe8e3`, `c22184a`, `8411fdd`) covered the rest of the non-notebook cluster.
> **Batch 4 (notebooks, FULL re-exec):** all 11 notebooks (00–05, 07 via .venv; 08–11 via .venv-legacy;
> 06 markdown/output-only, no re-exec) — the "90% CI"→**credible interval** family (08/09/10/11), pp-vs-%
> (10/11), **estimand-vs-estimator** split + two assumption rows + a materialized **pre-RMSE PASS/FAIL gate**
> + a **DiD-vs-avg-control comparator bar** + same-fitter placebo reference + a filter-cutoff sensitivity
> sweep (07), **number-conditioned verdicts** replacing hardcoded ones (01: BCF∈AIPW-CI check, PPC 90%
> coverage, seed-bias vs 2·sd), behavioural-vs-profitable **persuadable** cut + decile-midpoint x-axis +
> observable-Qini wiring (01), **endogeneity ρ extracted** from the LKJ covariance (11: ρ=+0.22, explains
> OLS>IV), cross-world→treatment-induced-confounding rename (04), E-value risk-ratio conversion (05),
> confounder-vs-precision-covariate reframes (03), LATE-at-cutoff footnotes (09), how-to-read cells
> (09/10), plus notation/label/figure polish throughout. Re-exec: core + legacy in parallel, all 11 clean;
> convergence readouts confirm r-hat ≤ 1.010; PDFs regenerated with **0 sampler-noise leaks**.
> **Deferred (2, documented):** nb06's saturation-curve-panel M-M rework + ROAS-forest log-scale — both need
> the ~38-min FULL MMM re-run; low-value polish, not worth the cost now.

> **P9 done (DGP / narrative / infrastructure majors).** (9.2) The `make_reports` NOISE filter no longer
> **fails open** — it keyed on bare tokens (`Only`/`Chain`/`Computing`/`>`/`took`/`tree depth`/`jitter`) that
> also matched real result lines and silently deleted them from PDFs; re-anchored on full sampler-message
> prefixes, verified to strip all 48 committed sampler lines and 0 of 11 look-alike result lines (old filter
> stripped all 11). (9.3) Added truth-recovery **content tests** (nb02 pathmc segment CATE in the core suite;
> DiD/ITS/IV in a new legacy suite `test_estimators_legacy.py` + `make test-legacy`, pytest added to the legacy
> env) so the notebooks are guarded on *recovery*, not just *executes-clean*; and **lockfiled** the legacy env
> (`requirements-legacy.lock`, 172 pins). (9.1) nb08's event study is no longer sold as a "formal check" while
> being descriptive — added **per-week 90% CI bands** (0/12 pre-launch leads exclude 0) and fixed the "€22
> average" (it's the mean *absolute* deviation; centred leads average 0 by construction) with a noise
> benchmark; nb11's **LATE-vs-ATE** seam is closed (homogeneous DGP → LATE=ATE stated, +21pp first stage
> labeled the complier share). (9.4) README nb07 relabeled `cmp.synthetic_control` (not CausalPy) + stale nb06
> bullet refreshed. (9.1a dag_control_demo docstring was already fixed in an earlier pass.) **P9 complete.**

> **P8.1 done (nb06 MMM euro-decision depth) — completes P8.** The decide step was a single 15% shift on
> *average* ROAS with an implicit-100%-margin break-even. Now: (1) **ROI→ROAS relabel** (what the MMM gives is
> revenue-per-euro, not profit ROI) with a **margin break-even** panel — break-even ROAS = 1/margin (30% margin
> → 3.3×); (2) a **saturation-aware marginal ROAS** (Michaelis-Menten fit to the fitted weekly
> spend/contribution — marginal **0.23×** vs average 2.08×, steep saturation); (3) a **shift-size sweep** (0–40%)
> with a genuine **interior peak near 22%** — beyond that, over-investing in TV *loses*, the diminishing-returns
> story working; (4) the watertight **ranking-vs-levels** conclusion: **TRUE ROAS is TV 0.85× / bs 0.14×, both
> below 1×**, so the MMM recovers the RANKING (TV≫bs, reallocate toward TV) but overstates LEVELS ~2.4× — even
> TV's estimated 2.08× fails a 30%-margin break-even, so the absolute "is TV worth it?" belongs to nb07's geo
> test, not this MMM. Re-run at FULL (legacy env, **2284s** — the two MMM fits are the repo's slowest; fully
> reproducible: default TV 10,390/bs 36,007 and calibrated 12,820/2,262 reproduced to the digit). **P8 complete
> (6/6).**

> **P8.4 done (nb08 + nb10 euro-decision depth):** both single-scenario decide steps now carry a decision
> *surface*, not a foregone P=1.00. **nb08 (DiD):** step 3 now states β₃ identifies the **ATT — the effect on
> the pilot stores**; the decide step adds a **transfer-discount × cost sweep** (P(app pays) as the non-pilot
> stores realise 100/75/50% of the pilot lift, across running costs €80–€300) that genuinely flips — at 50%
> transfer the roll-out becomes *pilot-further* once cost passes ~€150 — plus the max bearable cost at 90%
> confidence per scenario, and the break-even sentence is re-qualified as a 95%-posterior-probability claim
> (not a hard ceiling). The DiD posterior (€393, CI [274,515]) already covered truth €400 from an earlier
> standardization fix. **nb10 (ITS):** the naive "60-day lift × 365 days flat" is replaced by a **novelty
> persistence-decay sweep** (half-life ∈ {∞,180,90,30} days; effective days = Σ 0.5^(t/h)) against an explicit
> €600k amortized redesign cost — KEEP under any realistic persistence, but a harsh **1-month novelty half-life
> (€426k < €600k) flips to roll-back/renew (P=0.00)**, so the decision-relevant uncertainty is now persistence,
> not "did it work". Added the break-even lift (0.51pp vs estimated 3.0pp) and printed P(helped) as ">0.99
> (4000 draws)". Both re-run at FULL (legacy env, ~10-12s, CausalPy reproducible). Not added: nb08/nb10
> multi-seed & sensitivity (P5) and nb08's event-study "formal check" overclaim (P9.1).

> **P8.3 done (nb02 segment euro-decision depth):** the decision lived at a single COST=8. Added (1) a **cost
> sweep** of the four-policy ladder (€5–€12) whose punchline is that the **pooled rule collapses first** — it
> mails everyone until cost passes the ATE (€10.8) then flips to mailing *no-one*, forfeiting the high-value
> profit that segment/individual targeting keep earning; and (2) the **break-even engagement** send rule as a
> posterior functional g\* = (COST − be − bev·is_high)/beg with a 94% HDI. **Watertight caveat:** the fitted
> low-value crossing is g\*≈0.53, HDI [0.46, 0.61], which sits just *below* the true 0.625 — I framed this
> honestly (not as clean recovery) as error propagation: it echoes the same ~€0.7 low-value CATE overshoot
> already visible as the solid-vs-dashed gap in the moderation panel, amplified because a break-even is a
> **ratio** of two estimated coefficients — the reason to carry the HDI. Re-run at FULL (core env, 16s, pathmc
> reproducible: ATE 10.80 / CATE 7.69·15.82 / r-hat 1.000 all unchanged). VOI (a lesser sub-item of the same
> finding) not added — nb02 already has the four-policy realised-profit ladder.

> **P8.2 done (nb11 IV euro-decision depth):** the single fixed COST=10 with a **saturated P(pays)=1.00** is
> now a **break-even cost sweep** — cell 11 gained a middle panel plotting P(effect > c) across a cost grid
> and the print (a) *explains* the 1.00 ("saturated, not assumed: the whole posterior [€14.3, €21.1] sits
> above €10"), (b) reads off the **max viable cost-per-exposure at 90% confidence = €15.0** (the posterior's
> 10th percentile — the budget cap the opening promised, ~€5 headroom), and (c) marks the €17.8 coin-flip.
> The opening's unfulfilled **"frequency caps"** promise (the DGP has no frequency structure) is reframed to
> the budget/cost-per-exposure the sweep actually delivers, and every "frequency cap" reference is removed
> (cells 0, 9, 11). Bonus: the orphaned "7-step contract." line (a polish item) is dropped. Re-run at FULL in
> the legacy env (CausalPy, 74s; reproducible — IV €17.7, CI [14.3, 21.1] covers €15, r-hat 1.010/ESS 903/0
> div, all unchanged). The overconfident-CI **critical** + weak-prior fix were already applied in an earlier pass.

> **P8.6 done (nb00 foundations depth):** cell 6's two naive-estimate bars now carry **±1 SE error bars** and
> the print separates the two ways an estimate misses the truth — the randomized €4.8 is **1.2 SE** from the
> €5.6 truth (pure sampling *noise*, unbiased, shrinks like 1/√n) while the observational €11.4 is **9.0 SE**
> away (*bias*, does not shrink with n) — same SE (~€0.6), opposite cause; that contrast IS the lesson (was:
> a bare "€4.8 (unbiased)" label under a bar sitting below the truth line). The **LaLonde payoff** is now
> surfaced in the lecture PDF via a markdown result table (**naive −\$635 → adjusted +\$1,548**, toward the
> ≈+\$1,800 experimental truth; verified against the live fetch, n=614/185 treated) — previously the committed
> artifact showed only the `CMP_REAL=1` skip message, so the real-data punchline never appeared. Notebook
> re-run at FULL (CMP_FAST=0, 13s, no BART → fully reproducible: cell-13 ladder unchanged, AIPW 87% coverage);
> PDF regenerated. The AIPW "credible interval"→"bootstrap CI" relabel and the ladder-interval-excludes-truth
> majors were already closed in an earlier pass (cell 12/13); the `aipw_ate` docstring was fixed in P6.

> **P8.5 done (nb03 opt_price subtlety):** the naive `opt_price` column (a conditional-on-elastic median that
> contradicted the row's own elasticity plugged into $P^\star=c\beta/(\beta+1)$) had already been reworked into a
> per-draw scale-free **profit uplift %**; P8.5 adds the missing interpretation cell that (1) states the uplift is a
> posterior mean **over every draw with non-elastic draws zeroed** — an expected uplift discounted by P(elastic), not
> "the uplift once we act" (region_00: printed 34% ≈ 53% conditional on being elastic), and (2) explains the
> **boundary blow-up** ($P^\star\to\infty$ as $\beta\to-1^-$; at region_00's β=−1.07, P\*≈€122) so the per-draw mean
> ≠ the closed form at the mean elasticity (Jensen), which is itself why low-confidence regions are routed to a
> **controlled test**. Markdown-only (no re-exec; nb03 is reproducible); PDF regenerated. Also closes the related
> minor (decision figure had no "how to read this" cell).

> **P7 done (Anchor-B method bugs):** the inline RMSE-ratio placebo loop now **excludes the treated unit**
> from every placebo's donor pool (`np.delete(..., [treated_idx, j])`, mirroring `placebo_in_space`) — its
> post-period carried the real lift and contaminated placebo counterfactuals; the treated still ranks 1/30
> (p=0.033), so the fix is mechanically correct without changing the call. Added the discard count (kept
> 20/29) and labeled the two p-value conventions (add-one permutation vs Abadie rank). LOO bars now use a
> **same-fitter SLSQP baseline** (€318k) instead of the Bayesian one (€305k), so the range measures donor
> sensitivity, not fitter mismatch. Rewrote the "estimate barely moves" launch-date claim (it shifts ~18% at
> ±3 weeks) as a *mechanical dilution* — the peak at the true launch week is itself a diagnostic.

> **P6 done (src/cmp statistical fixes):** `go_no_go` now reports `expected_net_value` (€) and a true
> `expected_roi` ratio (was a euro amount mislabeled "ROI" — misread as ~499%; surfaced in policy.py + nb07 +
> Anchor B). `aipw_ate` now **cross-fits** the nuisances (K-fold out-of-fold scoring — removes own-observation
> bias, licenses the IF SE) and the docstring says "clips" not "trims"; verified it still recovers + covers
> truth (nb00 bias −0.10, 87% coverage; nb01 CI covers). McCrary relabeled a *simplified* binomial check
> (nb09 + README + docstring); bcf's `Y=y` tau-prior caveat + stale coverage claim documented. nb07's cell-22
> `roi = lift/cost` relabeled **ROAS** (distinct from the net-ROI ratio). **Also re-fixed a P4.1 regression:**
> the nb01 coverage caveat had hard-coded "89%/near-nominal", which the fresh (non-reproducible pymc-bart)
> run contradicted at 76% — rewritten to be **run-stable** (acknowledges under-coverage, cites no fixed %).

> **P4 done (all 3 open criticals were real, not false alarms):** (1) nb01 coverage caveat contradicted its own
> FULL output (claimed "below nominal" at ~89% coverage) → rewritten to match; (2) nb05 pathmc green-lit a
> biased set `{opened_email, loyalty}` → added a `test_implications()` falsification (1/4 violation, p≈1e-19)
> turning it into the "falsify the DAG" lesson + fixed the dgp docstring; (3) marimo decision table conflated
> the confidence-rule count with the rank-policy stop → split into 3 clearly-labelled policies (+ deployable
> vs oracle stop). **Criticals now 27/27.**

So: **the criticals are ~85% closed; the majors ~1/3; minors/polish untouched.** Calling the project "done"
was wrong — roughly **three-quarters of the reviewed findings remain open.**

## The 4 open criticals (not in any applied-fix record) — ✅ RESOLVED in P4

*(Retained for the record. All three unique issues below were re-verified and fixed in P4 — see the P4 note
above. Each was a genuine defect, not a false alarm.)* These were never explicitly fixed by P0–P3:

1. **nb01 / Anchor A — coverage-by-decile "90% coverage 76%"** (crit #4, #20; same issue). The calibration
   diagnostic catches a real under-coverage failure; the P2 roadmap listed "an honest reading" of it but the
   applied table does not confirm it landed. Read-out now has "one honest caveat" — verify it addresses the 76%.
2. **nb05 — pathmc collider printout vs bar chart** (crit #8). Committed output allegedly said
   `control for {opened_email, loyalty}: OK` (contradicting the collider warning). Current identify cell
   returns `{loyalty}` and warns on `responded` — looks fixed, but the committed *output* wasn't re-verified.
3. **marimo `uplift_policy_explorer` — decision table conflates two targeting policies** (crit #27). Not in
   any fix record; the P0 app fix only covered the *blank-figure* issue in the other two apps.

## What IS closed (for the record)

- **All 27 criticals except the 4 above** — via P0 (numbers/narrative), P1 (truth-recovery), the nb06
  rewrite, and P3 (CI). Re-verified by re-execution.
- **The entire convergence / FAST-mode class** — the FULL-mode run + `convergence_report` readouts closed
  every "no convergence diagnostics", "r-hat > 1.01 FAST warnings", "compute_convergence_checks=False", and
  "committed outputs are FAST-mode" major across nb01–11, src/cmp, Anchor B, and the reports pipeline.
- **~18 content majors** — nb01 (contour, policy table, PPC), nb04 (direct edge/NDE), nb05 (contour, E-value
  axis, euro decision), nb09 (bandwidth honesty, McCrary z-test), nb00/03/07 (business depth), plots mojibake,
  CI deps + kernelspec guard + strict kernels.

## Open majors — the actionable remaining work (~8)

> **Re-triaged against current code (6-agent majors pass).** The theme list below is
> **superseded/historical** — most of A–G is now CLOSED, verified in-code. The genuinely
> remaining majors are just these, each deferred for a stated reason:
>
> 1. **nb05 — mediator / M-bias never demonstrated empirically.** Needs a new DGP variable (a true
>    email→spend mediator + an M-structure collider); deferred because it changes `dag_control_demo`,
>    which nb00 also uses.
> 2. **nb06 — no multi-seed MMM stability / PPC / adstock-param recovery.** Each extra seed is a full
>    (minutes-long) MMM fit; deferred as too costly for the lecture notebook (ranking robustness is
>    already argued from the calibrated fit + the true-ROAS comparison, and a per-draw Δsales P(Δ>0) was
>    added in the majors pass).
> 3. **nb11 / dgp — IV LATE = ATE only because the planted effect is homogeneous.** A heterogeneous-
>    complier demo (returning true_ate ≠ true_late) needs a new DGP; the notebook now *discloses* this.
> 4. **estimators.bcf — τ forest passed `Y=y`** (prior at the outcome level, not the ~0 effect scale). The
>    docstring already caveats it; the code change (`Y = y - y.mean()`) is deferred as a risky core-BART
>    change that would re-churn the flagship nb01.
> 5. **nb03 — euro decision lacks a 3-policy comparison + VOI** (per-region profit-uplift % is present).
> 6–7. **marimo apps** — (a) `synthetic_control_placebo`: the truly-treated dma_00 stays in the donor/
>    placebo pool when a *different* market is selected; (b) `confounding_sensitivity`: the tipping point
>    is a single-seed artifact with no Monte-Carlo band. Deferred pending a marimo-runtime session (they
>    don't ship in the lecture PDFs and can't be verified headless here).
>
> Everything else in A–G below was closed by P3/P5/P8/P9 + the majors pass (AIPW cross-fitting, mccrary
> z-test, go_no_go net-value/ROI split, placebo-loop treated-exclusion, SC observation-noise, event-study
> CIs, convergence reporting, CI relocation + legacy lockfile parity, nb04 falsification, nb09 placebo
> cutoffs + perk-cost sweep, …). The theme list is kept below for provenance only.

Grouped by theme (each item is a verified major; full text + verifier in ASSESSMENT.md under its artifact) — **SUPERSEDED, historical:**

**A. Validation depth — multi-seed recovery / calibration missing (the biggest gap).** P1/P2 added it to
nb00/01/07 only. Still single-seed, no recovery/coverage check: **nb02, nb05, nb08, nb09, nb10, nb11**
(one major each). The README claims universal "multi-seed recovery" — an overclaim (README major).

**B. Business / euro-decision depth.** Single fixed cost, no sweep/margin/VOI: **nb02** (single COST=8),
**nb06** (single 15% shift), **nb08**, **nb10** (euro decision inputs), **nb11** (single COST=10, saturated
P(pays)=1.00), **nb03** (opt_price conditional-draw subtlety).

**C. `src/cmp` statistics still soft.**
- **`go_no_go` labels expected *net value* as "ROI"** — surfaces as a major in **policy.py**, **nb07**, and
  **Anchor B** (three places, one root cause). Not fixed.
- **AIPW is not cross-fit** — outcome/propensity models fit on the full sample (no cross-fitting), and the
  "trimming" described in the docstring/return isn't enforced as claimed (estimators.py). Two majors.
- **McCrary `+1` smoothing / naming** issues beyond the z-test already added (estimators.py).
- **`bcf` tau BART note** — pymc-bart forest declaration caveat.
- Thin test coverage exactly where the stats are fragile.

**D. Anchor-notebook method bugs (statistical).**
- **Placebo RMSE-ratio loop** fits each placebo's synthetic control on *all other units including the
  treated one* — surfaces in **nb07** and **Anchor B** (and relates to `placebo_in_space`).
- **AIPW "doubly robust" framing** (Anchor A) — same estimator as fits on full sample.
- **Anchor B**: LOO robustness compares SLSQP vs Bayesian fits (apples-to-oranges); launch-date sensitivity
  contradicts its own text.

**E. nb06 residuals.** Even after the fail→fix rewrite: **ROI-vs-ROAS naming** (it's revenue-per-euro), and
**true TV ROI is below break-even (0.84×)** while the MMM reports it above — the absolute-verdict tension the
review flagged. The rewrite fixed the *ranking* and is honest about levels, but these specific majors may
persist. Verify against the rewritten cells.

**F. DGP/narrative majors.** `dag_control_demo` docstring vs behaviour (opened_email mediator claim);
`mmm_weekly` planted economics put true TV ROI below break-even (now moot given the rewrite, verify);
`iv_ad_exposure` LATE-vs-ATE framing in nb11; nb08 event study "formal check" overclaim.

**G. Infra majors still open.** Notebook test asserts *executability only, not statistical content*; legacy
env has no lockfile (unpinned ranges); the `make_reports` NOISE filter **fails open** (could silently delete
a real result line beginning with `Only`/`Chain`/`Computing`/`Sampling`/`>`).

## Minor (~67 open) + polish (19 open)

Not scheduled by any tier. They span narration tightening, figure polish, docstring accuracy, and small
robustness nits across all 19 artifacts. See ASSESSMENT.md per-artifact sections (each lists its minors +
one polish item). Representative: the `make_reports` NOISE filter fragility (also a major), marimo app
comment/label clarity, README technique-index mislabel (nb07 "CausalPy/manual SC" — actually cmp SC).

## Suggested sequencing to actually finish the plan

1. **Re-verify the 4 open criticals** (cheap; either confirm-closed or fix).
2. **Theme A (validation depth)** — add the multi-seed recovery + coverage loop to nb02/05/08/09/10/11
   (each has a seeded DGP; it's the same pattern already in nb00/01/07). Highest value, closes ~6 majors +
   the README overclaim.
3. **Theme C (`go_no_go` "ROI", AIPW cross-fitting)** — small src/cmp fixes that each close majors in 2–3 places.
4. **Theme D (placebo loop bug)** — a real statistical bug in the Anchor B method.
5. **Themes B/E/F/G** — business depth, nb06 residuals, DGP narrative, infra.
6. **Re-run the comprehensive re-grade Workflow** to re-score and catch anything the fixes missed.
