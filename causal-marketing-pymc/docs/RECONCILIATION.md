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
| 🟠 Major | 95 | ~56 | ~39 | + **P9** make_reports fail-open filter, notebook-test content asserts, nb08 event-study CIs, nb11 LATE=ATE, README nb07/nb06; + **P8** business/euro depth (6 notebooks) |
| 🟡 Minor | 69 | ~7 | ~62 | + P8.1 nb06 ROI-vs-ROAS naming; P8.4 nb08 break-even language qualified; P8.5 nb03 decision-figure cell; P7 LOO baseline; P4 dgp docstring |
| ⚪ Polish | 19 | 0 | 19 | never scheduled |
| **Total** | **210** | **~90** | **~120** | + the Workflow re-grade (process step) not run |

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

## Open majors — the actionable remaining work (~65)

Grouped by theme (each item is a verified major; full text + verifier in ASSESSMENT.md under its artifact):

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
