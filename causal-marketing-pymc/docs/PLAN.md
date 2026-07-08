# Remediation plan — finishing the cookbook to the watertight bar

**What this is.** The single forward plan to take the repo from its current state (~55 of 210 verified
findings closed) to complete. It consolidates the [210 findings](ASSESSMENT.md) from the
`cookbook-deep-assessment` Workflow and the done/open split in [RECONCILIATION.md](RECONCILIATION.md) into
sequenced, numbered workstreams. It **extends** the original P0–P3 roadmap (all four tiers done) — think of
these as P4–P11.

**Grounding.** Done: 23/27 criticals, ~30/95 majors (incl. the whole convergence/FAST-mode class via the
FULL run), minors/polish untouched. Open: ~4 criticals (re-verify), ~65 majors, ~67 minors, 19 polish, and
the Workflow re-grade.

**Execution note (cost).** Phases P5–P9 change notebooks/DGP/estimators and therefore need re-execution +
PDF regen. **Batch them:** make the edits across phases, then do ONE FULL-mode run + PDF regen at the end
(the whole 12-notebook FULL run is only ~25 min; the dual-env driver + convergence readouts already exist).
FAST-smoke after each phase; hold the single expensive FULL run until the content is final — same discipline
we used before.

---

## P4 — Re-verify the 4 open criticals  *(must-do, cheap, no re-exec)*

The only criticals not in any applied-fix record. Confirm-or-fix each:

4.1 **nb01 / Anchor A — coverage-by-decile "76%".** The FULL run re-executed cell 15; read the *actual*
    committed coverage number and confirm the read-out states it honestly (not "near-nominal"). Fix wording if not.
4.2 **nb05 — pathmc collider printout.** Confirm the identify cell's committed output names `{loyalty}` and
    does not emit an "OK — no collider" line for a set containing a collider; tighten the narrative if it does.
4.3 **marimo `uplift_policy_explorer` — decision-table conflation.** Fix the row that conflates two targeting
    policies (mail-all-worth-it vs top-frac-by-rank) into one; make the table describe a single coherent policy.

*Closes:* 4 critical findings (3 unique).

---

## P5 — Validation depth  *(biggest major cluster; re-exec)*

Add the multi-seed recovery + calibration/coverage loop (the pattern already in nb00/01/07) to every notebook
missing it. Each already has a seeded DGP, so it's a small, uniform addition.

5.1 **nb02** — multi-seed CATE recovery + interval coverage across seeds.
5.2 **nb05** — multi-seed control-choice recovery; put uncertainty on the five-bar comparison (currently point estimates).
5.3 **nb08** — multi-seed DiD recovery (beyond the single 2×2).
5.4 **nb09** — multi-seed RDD recovery + polynomial-order robustness (claimed in README, not shown).
5.5 **nb10** — multi-seed ITS + multiple placebo-in-time dates (currently one).
5.6 **nb11** — multi-seed IV recovery.
5.7 **README** — once 5.1–5.6 land, correct/scope the universal "multi-seed recovery" claim (currently an overclaim).

*Closes:* ~6 majors + 1 README major + several validation-axis minors. Lifts Validation scores off 2 across the suite.

---

## P6 — `src/cmp` statistical fixes  *(shared, high-leverage; re-exec dependents)*

6.1 **`go_no_go` mislabels net value as "ROI."** Rename `expected_roi` → expected net value (€); optionally add a
    real ROI = value/cost. **Closes one root cause surfacing as a major in `policy.py`, nb07, and Anchor B.**
6.2 **AIPW is not cross-fit.** Implement K-fold cross-fitting of the outcome/propensity nuisances in `aipw_ate`
    (removes own-observation bias) and either enforce or stop advertising the trimming. Closes majors in
    `estimators.py` + Anchor A's "doubly-robust" critique.
6.3 **McCrary** — address the residual `+1`-smoothing / naming issues beyond the z-test already added.
6.4 **`bcf` docstring / tau BART note** — correct the pymc-bart forest-declaration caveat.

*Closes:* ~5–6 majors spanning multiple artifacts.

---

## P7 — Anchor-notebook method bugs  *(statistical; re-exec)*

7.1 **Placebo RMSE-ratio loop bug.** Each placebo unit's synthetic control is currently fit on *all other units
    including the treated one*. Exclude the treated unit. Affects nb07, Anchor B, and `placebo_in_space`.
7.2 **Anchor B robustness apples-to-oranges.** LOO compares SLSQP vs Bayesian fits; the launch-date sensitivity
    text contradicts its own result — reconcile both.

*Closes:* ~4 majors.

---

## P8 — Business / euro-decision depth  *(re-exec)*

8.1 **nb06** — replace the single 15% shift with a shift-size sweep + marginal (saturation-aware) ROI; fix the
    ROI-vs-ROAS naming; state honestly that even calibrated, TV's true ROI (0.84×) sits below break-even.
8.2 **nb11** — cost sweep + break-even (currently single COST=10 with saturated P(pays)=1.00).
8.3 **nb02** — cost sweep on the targeting decision (currently single COST=8).
8.4 **nb08 / nb10** — fix the euro-decision inputs (nb10 multiplies avg lift × traffic × value with questionable scaling) + add break-even.
8.5 **nb03** — surface the `opt_price` conditional-draw subtlety (median over elastic draws only).
8.6 **nb00** — add error bars to the cell-6 bars + fix the "€4.8 (unbiased)" wording; relabel the AIPW "credible
    interval" as a bootstrap CI; surface the LaLonde real-data result (committed PDF shows only the skip message).

*Closes:* ~8–10 majors + several business-axis minors.

---

## P9 — DGP / narrative / infrastructure majors  *(mixed; some re-exec)*

9.1 **DGP/narrative** — `dag_control_demo` docstring vs behaviour; `iv_ad_exposure` LATE-vs-ATE framing (nb11);
    nb08 event-study sold as a "formal check" when it's descriptive.
9.2 **`make_reports` NOISE filter fails open** — it strips any line starting with bare `Only`/`Chain`/`Computing`/
    `Sampling`/`>`, so a real result line could vanish from a PDF. Anchor the regex on known sampler-message
    prefixes, not generic tokens.
9.3 **Tests** — the notebook test asserts executability only; add lightweight statistical-content asserts
    (e.g. truth-in-interval on a fast seed). Lockfile the legacy env (currently unpinned ranges).
9.4 **README** — technique-index mislabels nb07 as "CausalPy / manual SC" (it uses `cmp.synthetic_control`).

*Closes:* ~6–8 majors.

---

## P10 — Minor + polish sweep  *(batch; light re-exec)*

Work the **69 minor + 19 polish** items artifact-by-artifact (narration tightening, figure/label polish,
docstring accuracy). Each artifact's list is in ASSESSMENT.md. Do this as one pass after P4–P9 so re-exec is shared.

*Closes:* 69 minor + 19 polish.

---

## P11 — Re-grade Workflow  *(needs explicit opt-in — 100+ agents)*

Re-run `cookbook-deep-assessment` (or a re-grade variant) to independently re-verify the fixes and re-score all
19 artifacts — the step the assessment explicitly defers ("grades held pending a full workflow re-grade").
Produces the updated scorecard and catches anything the fixes regressed or missed.

---

## Suggested order & checkpoints

1. **P4** (re-verify criticals) — do first, cheap, closes the credibility gap.
2. **P6 + P7** (shared stats fixes + the placebo bug) — high-leverage, fix once, benefits many notebooks.
3. **P5** (validation depth) — the largest single lift; uniform pattern.
4. **P8 + P9** (business depth + DGP/infra).
5. **One batched FULL-mode run + PDF regen** here (content now final).
6. **P10** (minor/polish sweep) — can fold into the same or a second batched run.
7. **P11** (re-grade Workflow) — final independent verification + new scorecard.

Commit per phase (FAST-smoke green); the expensive FULL run stays batched near the end.
