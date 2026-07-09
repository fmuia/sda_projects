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
| 🟠 Major | 95 | ~44 | ~51 | + **P8.5** nb03 opt_price boundary/conditional-draw subtlety now surfaced |
| 🟡 Minor | 69 | ~5 | ~64 | + P8.5 nb03 decision-figure "how to read this" cell; P7 LOO same-fitter baseline; P4 dgp docstring |
| ⚪ Polish | 19 | 0 | 19 | never scheduled |
| **Total** | **210** | **~76** | **~134** | + the Workflow re-grade (process step) not run |

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
