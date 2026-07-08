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
| 🔴 Critical | 27 | **23** | **4** (3 unique) | 4 are in *no* applied-fix record — need re-verification |
| 🟠 Major | 95 | ~30 | ~65 | incl. ~12 convergence/FAST-mode majors closed by the FULL run |
| 🟡 Minor | 69 | ~2 | ~67 | explicitly deferred ("deferred as minor") |
| ⚪ Polish | 19 | 0 | 19 | never scheduled |
| **Total** | **210** | **~55** | **~155** | + the Workflow re-grade (process step) not run |

So: **the criticals are ~85% closed; the majors ~1/3; minors/polish untouched.** Calling the project "done"
was wrong — roughly **three-quarters of the reviewed findings remain open.**

## The 4 open criticals (not in any applied-fix record)

These were never explicitly fixed by P0–P3. Current code looks *plausibly* correct in each case, but none
was verified as resolved — they need a targeted re-check (or the re-grade Workflow):

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
