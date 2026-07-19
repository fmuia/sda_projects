# List to fix

Running log of things to revisit and modify once the notebooks reach a more
final version. Each entry records **where**, **what**, a **proposed fix**, and
**status**. Newest at the top.

Status legend: `open` · `in-progress` · `done` · `wontfix`

---

## 2026-07-19 — Ch. 13 IV deck: classical part deepened to derivation level (45 → 48 slides)

Francesco supplied a full A1–A8 classical treatment as the target register ("this is the level of
clarity and detail I want... use the case as the backbone... don't use concepts before defining
them"). Parts 1–3 rebuilt to it. **Status: done.**

- 3 new slides: **the cast of four** (Y/X/Z/U table, observed/never-observed, who assigns what,
  the €{{nb11.ppc_obs_sd}} sales spread); **endogeneity precisely** (v = κU + ε, Cov(X,v) =
  κ·Cov(X,U) > 0 as "the disease", *endogenous* defined); **why adjustment cannot save it**
  (all adjustment needs Cov(X,v|W)=0 for a recorded W; "you cannot adjust for what you did not
  record").
- Upgrades: OVB slide now the derived plim formula + the precision trap (naive band
  {{nb11.naive_lo}}–{{nb11.naive_hi}} misses 15); instrument slide lists FOUR conditions
  (monotonicity added) + what-each-buys; relevance adds the regression form X = b0 + πZ + u;
  reduced form derives δ = βπ by substitution and names the ITT; svgFit slide adds the covariance
  form with the per-condition reading; 2SLS adds purified-X̂ logic, "just-identified", and the
  **corrected** hand-rolled-SE warning: too WIDE ({{nb11.se_hand}} vs {{nb11.se_correct}}, factor
  {{nb11.se_hand_ratio}}); the earlier "too small" claim contradicted the notebook and is gone.
- 69 tokens; verified: 48 slides, 0 mjx-merror, 0 JS errors, 0 em-dashes, changed slides
  screenshotted. HTML-only edits (no figure JS touched).

## 2026-07-18 — Ch. 13 IV slide deck REBUILT on the textbook spine (`apps/iv_slides.html`, `make html-iv-slides`)

Francesco rejected the 2026-07-17 v1 deck outright ("a student hearing about IV for the first time
learns 0") and pointed at the online books. Diagnosis he confirmed: v1 was a business drama using
concepts as plot devices; the canonical teaching order (confounding → OVB formula → borrowed
randomness → instrument → first stage → reduced form → divide → 2SLS → weak IV → LATE) was
scrambled; slides carried 3–4 concepts stated by metaphor; Bayes+endnotes outweighed the core
mechanics. **Rebuilt end to end, 41 → 45 slides. Status: done.**

- New spine per Facure (*Brave and True* ch. 8–9) and Huntington-Klein (*The Effect* ch. 19), the
  case kept as the running example. His three amendments honoured: careful plain prose with
  business jargon defined inline; Bayes kept a 6-slide arc inside Part 5 (not one slide, not the
  headline); real data EXPANDED to a 6-slide Part 6 (Criteo intro + cast-mapping table and a
  synthesis slide are new).
- New teaching slides: the omitted-variable-bias formula (predicted {{nb11.ovb}} vs observed
  naive); first stage alone (svgFS); reduced form alone (svgRF, drawn δ pinned to the shard
  scalar); divide-by-hand ({{nb11.reduced}}/{{nb11.first}} = {{nb11.wald}}); ideal-experiment;
  instruments-in-the-wild (quarter of birth, draft lottery); poll "what can the data check".
  LATE moved after the estimator. svgSim labels de-jargonised ("the dashboard"/"the coin method").
  Margin-trap slide and endnote poll killed; forensic + routes-not-taken now explicit Backup.
- Verified: 45 slides, 0 mjx-merror, 0 JS errors, node --check OK, 0 em-dashes, 63 tokens all
  resolved, all 45 slides screenshotted. Authoritative detail + do-not-undo list:
  `apps/iv_slides_REVISION_PLAN.md`.

---

## 2026-07-16 — Ch. 9 HTML slide deck REBUILT to the IV-lecture bar (`apps/geo_lift_slides.html`, `make html-geo`)

Francesco dropped the marimo route for Ch. 9 and pointed at his WIP deck ("too little data science,
LaTeX does not render properly, not high quality enough"). Rebuilt as a GENERATED artifact, one
self-contained 3.0 MB file, 28 → **43 slides**, `open apps/geo_lift_slides.html`. **Status: done.**

- **The deck is now built, not hand-edited:** `apps/build_geo_slides.py` (make target `html-geo`)
  assembles `apps/geo_slides_src.html` (THE file to edit from now on). Three inputs, none retyped:
  (1) `{{nb07.*}}`/`{{nb07b.*}}` tokens resolved from the executed shards — 106 distinct tokens,
  unknown token = build failure, FAST shard = build failure; (2) `apps/geo_lecture_data.json`, a
  lecture bundle written by a new final cell in nb07 (series, weights, placebo totals, ≤1500
  posterior draws per fit, ACF — the live SVG charts read only this, plus `DATA.scalars` merged
  from the shards by the builder); (3) eleven book figures (`book/build/figures/*.pdf`) rasterised
  at build time and inlined (coverage, growth, weightprofiles, naivebars, placebotime,
  spillover_curve, and the five nb07b real-data figures).
- **LaTeX fixed for real:** all pseudo-HTML math converted to true TeX (`\(..\)` / `\[..\]`),
  rendered by MathJax tex-svg vendored into `apps/vendor/` and inlined — offline, no fonts, no CDN.
  Treated index corrected 1 → 0 throughout to match the chapter.
- **Tokenisation caught three stale hand-typed numbers** in the WIP (LOO range "€255–266k" vs
  shards' 239–276; "3.2" pre-RMSE; "€18k/€45k") — the same drift class the book macros exist to
  kill; they now self-correct on rebuild.
- **New data science (+15 slides):** Act VI gains the 24-panel coverage failure (50/83/88 with the
  ±7–10pp MC-error honesty), the four-claimants width table, n/n²/n³ variance growth, and the
  corroboration-not-recovery estimate move; new **Act VII — What can go wrong** (naive-estimator
  poll + bars, placebo-in-time, spillover attenuation with the planted-bias formula); new
  **Act VIII — Real data: the exam** (randomized referee + 2.4× pairing gain, the anchor exam with
  divergence counts, the hull-failure gate refusal, the off-switch, the dollar margin trap, and the
  sim-NO-GO-vs-real-TEST-FURTHER precision contrast). Old verdict act renumbered to Act IX.
- Verified by headless-Chrome screenshots across the deck: math, dark theme, live charts (placebo
  cloud, mixer, cost sweep) and embedded figures all render; console clean.
- Note: `apps/geo_lift_lecture.html` (the older scroll-format WIP) is untouched and now superseded;
  delete or rebuild it the same way if wanted.

---

## 2026-07-16 — Ch. 9 FULL REVISION (six-auditor pass): tex + nb07 + nb07b, re-exec FULL, offprint 59 pp

A from-scratch six-agent assessment (correctness, coverage, prose/flow, figures/appendix/notation,
notebooks, cross-chapter coherence) of the already-"magnificent" chapter, then a full fix pass.
**Status: done** — offprint `ch09_geo_lift.pdf` 59 pp, 0 undefined refs, 0 em-dashes, macros.tex
2380 numbers, both notebooks re-executed FULL on `cmp-core` (kernelspec guard passes).

**Correctness (tex):** 🔴 Takeaways 7/8 wrote `P(τ>cost)` for the profit-scale quantity (0.45 is
P(0.35·τ>90); P(τ>90)≈1) — fixed; "a third the width" (actually 62%) → "barely three-fifths";
4 crefs sent the pre-fit gate to `sec:sc:valid` (it lives in `sec:sc:model`); §9.8 cited itself
twice; "most extreme on both statistics" on real data (raw-gap p=2/201 → second) fixed; hand-typed
"€80–170k band / €3k" → `\nbSevenParLevelLo/Hi`, `\nbSevenParNoiseSd`; "almost exactly" for a
94-vs-87 comparison → "within ten per cent".

**Prose/flow (tex):** epigraph 12 sentences → 6 (all macros kept); ~15 R1 rewrites (VOI subtlety,
division-of-labour closer, limits paragraph, cost-sweep, DiD naive, STS…); define-then-use closed
for RMSE, AR(1), iROAS, ACF, placebo-in-time, "randomization interval" christened; duplications cut
(interpretability trade, "decision banked" ×5→3, simplex box, resolution-edge); §9.12 What-can-go-
wrong got its missing opener; Assumption 9.4 got its testable/untestable verdict; de-meta'd ("this
book", "The lecture point"→"Why grade the method on an experiment", "indictment"→"criticism");
"suspect the likelihood" rule broadened to "suspect the specification" with \refiv pointers (the
Ch. 13 prior case falsified the universal form).

**New content:** three-DAG identification figure (`fig:sc:dags`, TikZ; closes the old Fix-5 SC
panel; tikz+calc now in preamble with DagRed/DagGreen + dag styles); TBR provenance paragraph in
§9.13 (replication-of-reference-code caveat, no retyped number); deck-index note in §9.2 (treated
0 vs deck's 1); Appendix grew A.14 margin algebra, A.15 matched-pairs SE, A.16 effective donors,
A.17 coverage MC error (+ a §9.8 body sentence: 50% broken, 83/88/90 indistinguishable at ±7–10pp);
appendix pointers now numbered (9.A.10 etc.) and A.1/A.6/A.8/A.12/A.13 gained body pointers;
offset draw renamed `c`→`ω` (σ_c→σ_ω) killing the 3rd bare-c (NOTATION.md updated + 9 new symbols
recorded); standalone-safe `\refiv/\refdid/\reffound` fallbacks (did.tex's \refgeo pattern) so the
offprint prints words, not "??".

**nb07:** the stale €300k/seed-3 markdown across §6/Depth B/final-decision cells rewritten to the
executed €90k/35% world (P=0.45, net +€1.7k, headroom €67k, VOI €8k, 29/29 filter, both p=0.033);
three print() strings now adjudicate from computed values; "§4/§5/§5z" placeholders purged from 5
emitted captions; `iid_vs_shipped` caption no longer claims "both centre on the planted truth";
new figures `fig:sc:growth` (n/n²/n³ variance growth, measured 20-wk point between offset and
level curves) and `fig:sc:glsweights` (GLS week re-weighting); new macros `cov_se_iid/arone/ri`.
All headline numbers reproduced exactly on the cold refit (262/229/260, 0.45, 50/83/88, ρ=0.54).

**nb07b:** the shipped AR(1) fit now samples at `target_accept=0.99` (was 0.95 hard-coded —
`est.synthetic_control_ar1` gained a pass-through param, default unchanged): divergences 22 → 3,
now emitted (`ar_divergences`) and discussed beside the iid fit's 1; decision numbers unmoved
($149k, P=0.81, TEST FURTHER, interval brackets the $147k anchor); new figures `fig:sc:realpairs`
(the 50 pair differences + 2.4× pairing gain) and `fig:sc:hullfail` (the gate refusing geo 1);
stale 35.5%→36.0 (shipped value), "~3,300" ESS parenthetical dropped.

**Infra note:** a stray `lecture_geo_data.json` (an app data bundle, no `_meta`) was sitting in
`book/build/results/` and tripped build.py's FULL-stamp guard — moved to `book/build/`. If an app
build regenerates it into results/, fix that writer's destination.

---

## 2026-07-16 — Cross-chapter findings surfaced by the Ch. 9 full revision (OUT of that revision's scope)

A six-agent coherence audit of Ch. 9 against Ch. 13 / Ch. 2 / BOOK_SPEC found the two guest chapters
in strong agreement (identical VOI, parallel boxes, 0 em-dashes, no κ/λ/ρ leakage, all cross-refs
resolve) but flagged drift in the chapters NOT under revision. Each item below names its file; none
touches `geo_lift.tex` (its side was fixed in the revision).

1. **[HIGH] `point_vs_posterior.tex:529–531` states a wrong mechanism.** "the probability rises
   because the posterior mean sits below the cost line" — Ch. 9's macros have ExpProfit 92 > Cost 90;
   the probability rises on widening because the *median/mass* sits below cost (P=0.45<0.5), not the
   mean. Fix the sentence. **open**
2. **[HIGH] `point_vs_posterior.tex:491–497` still tells the pre-restructure story** ("the point
   estimate barely moves at all" for the AR(1) repair). Ch. 9 now teaches the corrected account: iid
   €229k → AR(1) €262k (>1 posterior sd), landing *beside* classical €260k by a different weight
   profile ("corroboration, not recovery"). The 1%-apart figure is classical-vs-shipped only. Reword
   claim 2. Also `:534` has the same P(τ>cost) scale slip Ch. 9's takeaways had — should be
   P(profit>cost). **open**
3. **[MED] Decision-rule vocabulary: `iv.tex` never states the GO / TEST-FURTHER / NO-GO trichotomy**
   NOTATION.md §"Shared decision framing" promises (it expresses the same 0.9/0.5 thresholds as a bid
   cap and a coin-flip price). Either add one mapping sentence to Ch. 13 or amend NOTATION.md to
   record the price-form as the documented equivalent. **open**
4. **[MED] "Headroom" means two objects:** Ch. 9 = the 0.9-crossing price itself (matches NOTATION.md);
   `iv.tex:878` = the cap−cost differential. Reword the Ch. 13 sentence ("clears the planned price by
   €3.7"). **open**
5. **[MED] `BOOK_SPEC.md` spine drift:** ":123 the prior does almost nothing / the likelihood is the
   whole ballgame" is falsified as universal guidance by Ch. 13's measured prior-driven failure —
   adopt the "specification, not paradigm" phrasing (did.tex already has it; Ch. 9 now says "suspect
   the specification"); ":117 under-prices … 2.8x" is stale (current \nbSevenUnderprice = 2.2); the
   "Good" example epigraph (:93–97) quotes V0-era numbers no current macro matches — mark
   illustrative-historical. Ch. 2's takeaway 6 ("do not adjust the prior. Interrogate the
   likelihood", :514–517) needs the same softening. **open**
6. **[MED] `iv.tex` reuses κ within one chapter** (U→Y coefficient AND Abadie's κ weights,
   eq:iv:kappa) — NOTATION.md rule 2 violation; add a disambiguating clause in 13.A.14 and record
   the exception. **open**
7. **[LOW] `iv.tex:1107, 1403–1411`:** delta-method passages write the reduced form as τ̂ where the
   chapter's own symbol is δ (and τ is the causal-effect symbol book-wide) — change to δ̂. **open**
8. **[LOW] `iv.tex:626`** renames exposure mid-chapter ("Write T_i = X_i") — document in NOTATION.md
   or revert to X. **open**
9. **[LOW] `iv.tex:899`** says "the same quantity the geo-lift chapter uses" with no \cref;
   did.tex's `\refgeo` standalone-safe macro is the pattern to copy. Also `iv.tex:26`: epigraph
   starts a sentence with lowercase `\cref` — use `\Cref`. **open**

---

## 2026-07-16 — Ch. 9 §9.6–9.11 RESTRUCTURE: the Bayesian arm as persistence-aware fix

Francesco's plan: rebuild the Bayesian sections so "persistence-aware" is the *concept* and AR(1)
the *instrument*, with caveats aired **in the main text** because the decision was already banked
classically (§9.5). Split the old four sections into six: **§9.6 Why add a posterior** (motivation,
the p-value-gives-no-probability point, the sequencing contract), **§9.7 The model** (Dirichlet +
iid likelihood + prior-robustness + pre-fit/donor validation), **§9.8 The interval is broken, and
why** (coverage failure → offset/ACF/n² diagnosis), **§9.9 The fix: an AR(1) residual**
(GLS reweighting, the three things, the wrong-ACF-shape caveat, verdict invariance), **§9.10 euros**,
**§9.11 The more precise route: structural time series** (prose-only forward pointer, no state-space
run). Status: **done**; offprint `ch09_geo_lift.pdf` 54 pp, 0 undefined macros, re-exec FULL.

Two review-driven corrections folded in beyond the plan:
- **Corroboration, not recovery.** The AR(1) fix does *not* move the estimate "onto" the classical
  number — it moves iid €229k → AR(1) €262k, which lands *beside* classical €260k by a **different
  weight profile** (3.3 vs 23.4 effective donors). Overclaim fixed in §9.8 "agree", §9.9 item 1,
  Takeaways, and Appendix 9.A.10. New figure `fig:sc:weightprofiles` makes the two profiles visible.
- **Show, don't assert (2 figures).** ACF figure now overlays the *shipped* ρ=0.54 decay (vanishes
  by lag 8, `\nbSevenRhoEightImplied`≈0.01) against the flat measured ACF, so the caveat is seen not
  claimed. Weight-profile figure added. Also: n²/n³ ordering sentence (constant offset vs
  near-integrated) links §9.8→§9.11; VOI loop from §9.5's €98k hook closed to §9.10.

`cmp.report.table` unchanged; added one macro `nb07.rho_eight_implied`. `report.table` still supports
the `position=` param from the §9.5 pass.

---

## 2026-07-16 — Ch. 9 §9.5 RESTRUCTURE: the classical decision as one tight argument

Francesco's plan: rebuild the classical decision-making (§9.5) into one ordered argument — derive the
placebo interval cleanly, make the margin trap the centrepiece, then span the decision space with a
small set of cost cases. **Classical arm only; §9.6/§9.8/§9.9 (Bayesian) untouched; every number from
the placebo/randomization interval alone, no posterior.** All done; offprint 52 pp, 0 undefined macros.

**New §9.5 flow** (was: Fitting / Where-an-interval / Inversion / Deciding):
- **Part 1** split into three steps: *The placebo distribution* (29 donors refit, both Abadie
  refinements as separate points, filter non-binding); *The permutation p-value, and its floor*
  ($1/(J{+}1)=1/30=0.033$, treated ranks 1/30 = on the floor, can't go lower); *The interval by
  inverting the test* — constant-additive-effect assumption up front, the percentile-flip shown
  algebraically ($\hat\tau\in[\tau_0+q_{05},\tau_0+q_{95}] \Leftrightarrow \tau_0\in[\hat\tau-q_{95},
  \hat\tau-q_{05}]$), numbers €260−(+65)=195 / €260+75=335, asymmetry noted (midpoint €265≠€260).
- **Part 2** *The margin trap* (centrepiece): revenue≠profit; break-even two ways (lift €257k, iROAS
  2.86); the trap sentence ("€1k net is not the opportunity, it's the thin true edge behind an
  impressive gross number").
- **Part 3** *The decision at €90k*: the 3-step verdict (real? / clears break-even? / margin safe?) →
  NO-GO; ends naming the one thing classical can't do (a single how-close number → §9.9), no Bayesian
  number cited.
- **Part 4** *Spanning the decision space: a cost sweep*: the two thresholds are **different** — net
  crosses zero at €91k (=m·τ̂), the straddle band is €68k–€117k (=m·[195,335]); five cases (€55/75/90/
  98/125k), each a distinct lesson (clean GO / mean-+-but-straddles / knife-edge / mean-−-but-tail-
  profits / clean NO-GO). €98k is the **VOI hook** (NO-GO with residual upside) — flagged in the .tex
  as `% VOI hook` for the Bayesian pass. Normal-approx σ_τ≈€43k mentioned once, explicitly
  illustrative-only (right-skew); the classical arm stops at the interval.
- **Part 5** felt-stakes remark box (×30 → €2.7M/€7.8M/€35k, ratios identical, marked cosmetic).

**4 new nb07 assets** (cell 45): `fig:sc:inversion` (number-line, placebo cloud → inverted onto the
estimate, the percentile-flip arrows — the pedagogical unlock), `fig:sc:marginfunnel` (waterfall
€260k→€91k→€1k), `fig:sc:costsweep` (net-vs-cost line + shaded straddle band + 5 case markers — the
structural payoff), `tab:sc:costsweep` (5 rows). New macros: sweep_{go,lo,hi,ng,ke}_{c,be,net},
placebo_qlo/qhi/qlo_mag, sigma_tau_approx, felt_{n,spend,lift,net}. (Digit-tailed keys are illegal —
`placebo_q05`→`placebo_qlo`.)

**Library:** `cmp.report.table` gained an optional `position` param (default `"tb"`, unchanged). The
cost-sweep table uses `position="H"` so a float-dense section can't exile it (it had drifted to the
appendix `\clearpage` at p41, which also jammed `tab:naive` behind it in the FIFO table queue; `[H]`
fixed both). 17 report/table/library tests still pass.

---

## 2026-07-17 — Ch. 13 (IV) interactive slide deck (`apps/iv_slides.html`, `make html-iv-slides`)

Built with the `lecture-deck` skill to the `geo_lift_slides.html` standard, after Francesco asked for
"something similar" to the Ch.9 deck. **41 slides, DONE and verified.** Acts: the question (live κ/γ
simulator) · the method (back-door DAGs, compliers-live, 2SLS=Wald, break-exclusion-live, fit-the-Wald-
by-hand, ID table) · is-it-real (weak-IV sweep-live, **Anderson-Rubin by test inversion, live**) · the
euro decision (margin trap, decision space, **classical verdict banked**) · Bayes (probit repair + PyMC
code + ρ, BvM, P(β>c), VOI) · real data (Criteo balance, the **+28.7pp design anchor referee**, and the
**off-switch**: the "better" probit misprices Criteo) · deliverable, takeaways, endnotes, close.
5 polls, 18 live SVG figures. All numbers are `{{nb11.*}}`/`{{nb11b.*}}` shard tokens (56 of them);
the live JS sim uses seed 264275 so its default reproduces the shards (naive 23.7 / 2SLS 16.5 / F 156).
Verification: node --check OK · 41 slides, 0 mjx-merror, 0 JS errors · 0 em-dashes · screenshots read.
Detail + the two documented arc deviations: `apps/iv_slides_REVISION_PLAN.md`. **Status:** done; expect a
per-slide review pass from Francesco (as Ch.9's deck got), which the plan file is set up to absorb.

---

## 2026-07-16 — Ch. 13 (IV) standalone HTML lecture (`apps/iv_lecture.html`, `make html-iv`)

Francesco asked for "an html along the lines of the one in the course folder"
(`course/Notebook1_Experiments.html`, a Quarto page) instead of marimo. Built a single self-contained
3.2 MB HTML that opens in any browser offline — Quarto look (sticky TOC + scroll-spy, metadata header,
numbered sections, callout boxes) and still interactive: `apps/build_iv_html.py` pre-renders each slider
state (κ/γ/cost) to a matplotlib PNG frame, inlines all as base64, and vanilla JS swaps the image on the
range input. No server, no JS compute — numbers stay the notebook's. **Status:** done.

---

## 2026-07-16 — Ch. 13 (IV) marimo lecture rebuilt to the course-HTML bar (`apps/iv_lecture.py`)

v1 of the lecture was thin (Francesco: "very poor content+layout, would end in 10 min; have you seen
the course HTML?"). The bar is `course/Notebook1_Experiments.html` — a Quarto lecture with numbered
sections, callout boxes, a narrative case, DAGs, boxed definitions. **All done**; app executes clean
(`marimo export html` runs all cells, 9/9 figures render), live on :2721, WASM take-home self-contained.

1. **Concept-first, case-driven, ~45 min:** 10 parts, each teaching the concept (boxed definition +
   one-line intuition) then working it on ONE running case (a retailer pricing a single ad exposure).
   Boxes via `mo.callout`: define / idea / manager's-takeaway / where-teams-slip.
2. **DAGs** (a reusable `draw_dag()`): the confounding fork, a valid instrument (read by its absences),
   and the exclusion-violation red edge. **Definitions** stated explicitly for confounding, instrument,
   LATE, 2SLS/Wald, posterior, external anchor.
3. **Progressive stepper reveal** replacing the accordion (Francesco: hard to follow live):
   `mo.state` + Back/Reveal-next/Show-all/Restart, nav at top and bottom, locked parts shown muted.
4. **Real-data Criteo part** (my earlier suggestion, now built): naive +38.9 pp vs 2SLS/Bayes both on
   the +28.7 pp 13.98M-row design anchor; €92k/quarter overpayment. Plus the fixed-posterior caption,
   subtitle now tied to the case, and the WASM export.
5. **`apps/build_iv_lecture_data.py`** (`make data-iv`): merges the nb11 draws with nb11/nb11b scalar
   results and embeds a zlib+base64 blob in the .py so `make site` ships a self-contained page (numbers
   sourced from the notebooks, not retyped).

**Status:** done. Superseded `apps/instrumental_variables.py` (v0 toy) still on disk — `rm` is
permission-blocked in this environment; delete it by hand.

---

## 2026-07-16 — Ch. 13 (IV) magnify pass: prose, coverage, VOI, self-verify

Full magnify of `chapters/iv.tex` + nb11, taken from an assessment that found the technical spine
already watertight (the old CRITICAL contradiction and the `eq:iv:ssr` error were already fixed in
source). All **done**; nb11 re-executed FULL on `cmp-legacy` (warm cache for the MCMC fits; the new
cells are closed-form), offprint rebuilt clean (47 pp, 0 undefined macros/citations, the only
undefined refs are the cross-chapter `ch:foundations`/`ch:pe`, which resolve in the full book).

1. **Em-dashes: 182 → 0** (plain, direct English per Francesco), matching the finished Ch. 9. Macro
   multiset (313 uses) and refs/cites (277) verified byte-identical before/after; en-dashes
   (Bernstein--von Mises etc.) correctly preserved. Epigraph tightened to short sentences.
2. **Four Session-5 concepts the deck names but the chapter had dropped**, each now an appendix
   subsection with a computed worked example + figure, AND named in the body with a pointer:
   **13.A.13 Anderson–Rubin** (`fig:iv:ar`, macros `ar_lo/ar_hi`; AR set ≈ Wald CI at strong F),
   **13.A.14 Abadie's κ** (`fig:iv:abadie`; κ-weighted complier intent −0.21 vs answer-key −0.22 vs
   sample 0.00; E[κ]=first stage), **13.A.15 Lee bounds** (`fig:iv:lee`; attrition overlay, bounds
   [−1.86, 7.11] bracket the truth, naive-on-reporters 2.34 biased), **13.A.16 four faces of
   endogeneity** (`fig:iv:faces`; OVB/simultaneity/meas-error/selection, each biased in its own
   direction). New bib keys `anderson1949`, `lee2009`, and **`abadie2003kappa`** (the existing
   `abadie2003` is Abadie–Gardeazabal synthetic control — do NOT cite it for κ).
3. **VOI added** (`eq:iv:voi`, §13.9, macros `voi`/`voi_coin`): €0.00 at the €10 plan (decision not
   close), €0.88 at the coin-flip price — same definition as Ch. 9, closing the shared-framing gap.
4. **MLE = 2SLS now asserted in code** (nb11 cell "Step 0": control-function β vs 2SLS `< 1e-8`;
   `cf_maxdiff` = 3e-13 across 24 panels), cited in 13.A.5 — the forensic linchpin is self-verifying.
5. Nits: "The ledger" heading → "What it did not buy" (purge scorekeeping voice); the two
   margin-overflow equations (`eq:iv:vocab_*` align 34 pt, `eq:iv:probit_priors` 15 pt) fixed;
   `α_0/α_1` documented in `NOTATION.md`.

**Status:** done. COURSE_MAP flipped to `magnificent`. Likely to draw a PDF digest pass from
Francesco (as Ch. 9 did); treat that as the real acceptance gate.

---

## 2026-07-16 — Ch. 9 digest pass #4: independent technical review (8 points + 2 minors)

An independent review of the compiled PDF found the core thesis correct but flagged genuine internal
contradictions and conceptual soft spots. All verified against source and **fixed** (nb07 re-executed
FULL twice; offprint rebuilt clean, 49 pp; 0 undefined macros). Highlights:

1. **🔴 lift-vs-profit scale confusion (3 bugs, load-bearing).** The decision quantity is
   `P(profit>cost)=P(0.35·τ>90)=P(τ>257)=0.45`, but three places computed `P(lift>cost)=P(τ>90)≈0.99`:
   (a) the param-table campaign-cost row (`(total_post_ar1>CAMPAIGN_COST).mean()`), (b) `decision_hist`
   got raw lift + a €90 line, (c) the headroom panel's y-label + caption crossing were lift-scale (192)
   though `p_beats` was already profit-based (67). Fixed in nb07 cell 42: histogram now plots
   `MARGIN*total_post_ar1`, y-label `P(profit>cost)`, caption crossing `MARGIN*q10=67`, table row
   `(MARGIN*total_post_ar1>CAMPAIGN_COST).mean()=0.45`. The headline macro `p_go` was always correct
   (computed on profit) — only the figure/table/caption were off. **done**.
2. **Fig `sc:gap` caption contradicted §9.8** ("fixing the likelihood moved the interval, not the
   estimate"). Reconciled: AR(1)-vs-classical agree, but iid→AR(1) *does* move the estimate €33k
   (≈€1.6k/wk, invisible per-week, material summed). **done**.
3. **"Classical & Bayesian agree" quietly excluded the iid arm** (€229k vs classical €260k, a 12% gap).
   Added a paragraph to §9.8: the likelihood moves the *centre* too (GLS reweighting, App 9.A.10), the
   iid fit mis-centred; "sampler adds no causal content" holds, "likelihood touches only width" does not.
   **done**.
4. **VOI baseline mis-stated.** Eq (9.21) is risk-neutral EVPI with baseline = "act on the mean" =
   *invest* (mean €2k > cost), not "hold". Rewrote: named the risk-neutral baseline, noted the €0.9
   rule is a risk-averse proxy (so it holds), and that the two framings differ by exactly `exp_net`. **done**.
5. **AR(1) is the wrong ACF *shape*.** Diagnosis is a *flat* ACF (near-integrated); AR(1)'s ACF decays
   geometrically. Sharpened the transferable-rule paragraph: AR(1) matches the sum's *variance*, not the
   ACF's *shape*; the flat ACF points at a local-level/random-walk component (`brodersen2015`). **done**.
6. **Offset model is n², true error is n³.** The mismatch's `m_t` piece is integrated: `Σm_t` has
   variance ~n³σ_η²/3, not n². Added to App 9.A.11 — explains why structural €45k < measured €59k. **done**.
7. **sd 72 vs 94 unexplained.** Clarified: €72k is this panel's AR(1) posterior sd (Table 9.6), €94k is
   the cross-panel average (the object to compare against the €87k seed spread). **done**.
8. **Prior-sweep shown on the discarded iid fit.** Added caveat: point is about the prior not that fit
   (carries to AR(1) unchanged); α still moves effective donor count (stability/interpretability lever),
   just not the headline total. **done**.
   Minors: App 9.A.13 "coincide"→BvM is about the *centres* coinciding, widths in the same ballpark
   (both narrow, same iid error model); added an explicit sim (NO-GO, 0.45) vs real (TEST FURTHER, 0.81)
   contrast in §9.11 — precision from aggregating 50 geos (sd ~5% vs ~27%) lifts the verdict. **done**.

---

## 2026-07-15 — Ch. 9 digest pass #3: six PDF comments (the "magnificent" verdict was premature)

Francesco read the compiled PDF again and flagged six problems; the earlier "magnificent" claim was
wrong. All six are **done** (offprint rebuilt clean, 48 pp; nb07 re-executed FULL on `cmp-core`, warm
cache, 11 s; no model/DGP change so no `CMP_REFIT`). Verified by rendering pp. 12–14, 21–22 to PNG.

1. **Redundancy still visible.** Removed the three real duplications: the estimator equation was
   *displayed twice* (§9.2 `eq:sc:vocab_synth/gap` and again as `eq:sc:gap` in §9.4 Identification) —
   deleted the §9.4 re-display, repointed its 3 refs to the §9.2 labels; the permutation mechanism was
   *re-explained* in §9.5 after being defined in §9.2 — cut to a pointer; the "total is what the
   business buys" motivation appeared in both §9.2 and §9.4 — kept in §9.2, §9.4 now the pure PO
   restatement. **Status:** done.
2. **Code block overflowed the margin + wanted a colour.** Root cause: raw `verbatim`. Added a
   `listings` style + `pycode` environment to `preamble.tex` (tinted `codebg` panel, framed, house-
   colour syntax, `breaklines`); converted the §9.6 PyMC snippet and shortened one comment so nothing
   wraps. Reusable book-wide. **Status:** done.
3. **ACF plot (`fig:sc:acf`) looked weird** (5 categorical bars at lags 1,2,3,5,8; 60 % empty space; a
   0-line legend proxy). Redesigned in nb07 cell 42: contiguous lags **1..8**, y-axis trimmed, and two
   *reference curves* overlaid — a flat dashed line at the persistent-offset level (`rho_implied`
   0.28) and a dotted geometric decay `rho[0]^k` — so the reader SEES the bars track "flat" and refuse
   "decay". Caption rewritten. (cell 14 `rho` lags → `range(1,9)`.) **Status:** done.
4. **"Is there no way to decide without Bayes?"** No — and the chapter now says so outright. New
   §9.5 subsection **"Deciding on the classical evidence alone"**: significance + point estimate +
   design-based interval vs break-even, reaching the verdict in three steps and closing "No posterior
   was consulted, and none was needed." §9.6 opening now says the call is already made. **Status:** done.
5. **Does the pre-fit gate jeopardise the example?** No — the *decision-critical classical fit passes*
   it (cl_pre_rmse 3.23 < gate_ref 4.37); only the regularized Bayesian blend (5.06) fails, and it
   agrees with the classical fit to within €1k, so it inherits its credibility. Reframed §9.7 (gate),
   §9.10 (limits) and takeaway 2; the gate's real teeth are shown on the real-data largest-market case
   (§9.11), where it correctly refuses. **Status:** done.
6. **Conclusions were a mess** ("does it hold only for Bayesian / on AR(1)?"). Restructured the whole
   decision arc: classical decides (§9.5) → Bayes adds one probability (§9.6) → AR(1) makes the
   *posterior's width* honest, not the decision (§9.8) → §9.9 is the clean comparison ("same action,
   now carrying a probability"). Replaced the scattered §9.8 "What the posterior gives the decision"
   with **"Does the AR(1) repair change the decision? No"** — a bulleted robustness list showing the
   verdict holds across classical / iid / AR(1) / re-priced arms. **Status:** done.

**New macros (nb07):** `breakeven_lift` 257, `cl_profit` 91, `cl_net` +1, `cl_profit_lo/hi` 68/117,
`ri_iroas_lo/hi` 2.17/3.73 — all used by the classical-decision subsection. macros.tex now 2331 nums.

---

## 2026-07-15 — Ch. 9 digest pass #2: 18 PDF-review points from Francesco

Second round of Ch. 9 (`book/chapters/geo_lift.tex` + nb07/07b) fixes, from Francesco reading
the compiled PDF. Recorded verbatim-in-substance with the resolution/target for each. Point 4
duplicates **Fix 1** below (em-dashes); point 12 is the **margin trap** (already agreed —
"mirror the real data", cost →≈€90k + 35 % margin). Batched: prose-only points land without
re-execution; figure/macro points share one FULL re-exec of nb07 (`cmp-core`, warm cache).

**Progress (2026-07-15, later same day):**
- **Done:** **pt12** margin trap — final resolution is a *subtle NO-GO*, not a knife-edge: cost €90k,
  35 % margin, apparent profit €170k (revenue − cost), iROAS 2.89 vs break-even 2.86, expected profit
  €92k barely over the €90k cost, but P(profit>cost)=0.45 → NO-GO (flips to TEST FURTHER only at the
  wider design scale, 0.54 — the break-even signature). New macros `iroas/breakeven_iroas/margin/
  exp_profit/apparent_profit`; nb07 re-exec FULL; abstract + §9.8 + §9.9 + takeaways rewritten around
  "read the probability, not the mean" (mean +€2k but P<0.5, right-skew); offprint builds 38 pp.
  **pt1** hats (`\widehat{Y}_{...}`), **pt3** SUTVA gloss, **pt5** adversarial/erratum voice removed
  (§9.5 intro & title, §9.6 "Bayesian layer kept light" / "As throughout this book"), **pt7** σ-prior
  numbers macro-ified (`par_level_lo/hi`, `par_noise_sd`), **pt14** DiD recall (§9.10 + §9.11,
  `\cref{ch:did}`).
- **ALL 18 DONE (2026-07-15).** pt2 de-dup (§9.4 estimator + §9.5 permutation compressed to pointers);
  pt4 em-dashes = 0 in `geo_lift.tex` AND in all rendered captions (only the invisible `% Generated by`
  comment header still carries one, book-wide); pt6 PyMC `verbatim` snippet + SLSQP acronym + RMSE
  formula (`eq:sc:rmse`); pt8 "The iid interval is too narrow" subsection + `fig:sc:iidshipped`;
  pt9 `fig:sc:priorsens` (3 Dirichlet concentrations, refit); pt10 `nb07_gap` now overlays classical
  SLSQP + Bayesian AR(1); pt11 §9.7/§9.8 restructured (escape-hatch roadmap, referee digression moved
  to appendix, AR(1) made skippable); pt13 `fig:sc:naivebars`/`placebotime`/`spillover`; pt15
  divergences 56→1 (target_accept=0.99 on the iid fit); pt16 `fig:sc:realposterior`; pt17 Appendix
  9.A now A.1–A.13 (SLSQP, RMSE, simplex, Dirichlet, PPC, permutation, placebo-in-time, randomization
  interval, referee, GLS, offset, VOI, BvM) each with a figure/worked example; pt18 nb07+nb07b
  re-executed FULL on `cmp-core`. Offprint `book/build/ch09_geo_lift.pdf` builds clean, 47 pp.
  COURSE_MAP status flipped to **magnificent**.
- **Follow-ups (2026-07-15, same day):** (a) **§9.11 line-level prose pass** — explicit "three things"
  roadmap in the intro; the real-data posterior `fig:sc:realposterior` moved up into "The contestant"
  where the model first meets the anchor (was buried at section end, hence "I don't see a posterior");
  margin derivation de-duplicated against §9.9; the dense dollar-decision subsection signposted into
  its two questions (does it pay / is the interval honest). (b) **Book-wide layout:** added
  `\raggedbottom` to `book/preamble.tex`. Floats were already `[tb]` with loosened fractions, but the
  `book`/`scrbook` default `\flushbottom` was stretching glue to force-justify page bottoms, opening
  random gaps around floats; `\raggedbottom` lets pages end naturally. Verified on the offprint
  (figures anchor top/bottom, text closes over them, no mid-page gaps). Applies to the whole book on
  next `make book`.

1. **Hats on the main letter.** `\hat{Y}_{...}` not `\hat{Y_{...}}`. (4 `\widehat{Y_{0,t}(0)}`
   occurrences: lines 92, 337, 573, 581 — and NOTATION.md.) — prose. **Status:** open
2. **Redundancy in definitions / permutation / p-value / placebos across §9.2, §9.4, §9.5.**
   The estimand+estimator+simplex are defined in §9.2 then restated in §9.4; the permutation
   p-value/placebo are defined in §9.2 then re-explained in §9.5. De-duplicate: define once,
   reference after. — prose. **Status:** open
3. **SUTVA used without explaining it** (Assumption 5, §9.4). Add a one-line plain-English gloss
   at first use (+ appendix per pt 17). — prose. **Status:** open
4. **Remove all em-dashes** — *see Fix 1 below* (183→159 remaining). **Status:** open
5. **Remove adversarial / erratum voice.** Kill lines like "Before any sampler, the discipline of
   this book is to ask what a competent analyst produces without one" (§9.5 intro), "The estimator,
   without a likelihood" (§9.5), "It is the book's Bayesian layer, kept deliberately light" (§9.6).
   Just write the section. — prose. **Status:** open
6. **Name the library + show a code snippet near the Bayesian model (§9.6, ~"9.13").** Define the
   **SLSQP** acronym where Fig 9.4 uses it. Define **RMSE** (avg over pre-period dates t<T₀).
   — notebook (snippet listing) + prose + appendix (pt 17). **Status:** open
7. **Hardcoded σ numbers in §9.6 (~"9.17").** "€80–170k band", "€3k idiosyncratic noise", "€5k"
   scale are literals — macro-ify the data-derived ones (`nb07.*`). — notebook macro + prose.
   **Status:** open
8. **iid vs shipped fit → its own subsection, slightly expanded, not crucial, + a plot.** Currently
   scattered from §9.6 through §9.7/§9.8. Consolidate; add a figure contrasting the two bands.
   — prose + notebook figure. **Status:** open
9. **Drop "As throughout this book"; show a prior-sensitivity study** and explain why the prior
   matters less than the likelihood here. — notebook figure (refit under alt priors) + prose.
   **Status:** open
10. **Show the classical curve in Fig 9.6** (`nb07_gap`) alongside the Bayesian gap. — notebook.
    **Status:** open
11. **§9.7 + §9.8 too scattered.** More clarity/explicitness/visualization; AR(1) must not
    distract and its conclusions should hold independently. Restructure. — prose (+ maybe a
    summary figure). **Status:** open
12. **DGP gives a foregone strong NO-GO — make it interesting.** = the **margin trap**: cost
    →≈€90k, 35 % margin, iROAS≈2.9 vs break-even 2.86 → **subtle NO-GO** (apparent €170k profit, but
    P(paid)=0.45). (Agreed: mirror real data; no DGP/seed change, cache stays warm.) — notebook +
    abstract/§9.9/takeaways prose. **Status:** done
13. **Explanatory plots + examples in each subsection of §9.10** (What can go wrong: naive,
    anticipation, spillover). Currently tables only. — notebook figures. **Status:** open
14. **DiD used without defining (~"9.23", §9.11 `eq:sc:did`; also §9.10).** Add a one-line recall
    (Ch. 10 owns it fully). — prose. **Status:** open
15. **Divergences?** Simulated fit = 0 (clean). Real-data fit = **56** (`nbSevenBDivergences`),
    discussed w/ SLSQP cross-check at §9.11. Verify the treatment is adequate / consider
    `target_accept` bump or reparam. — notebook + prose. **Status:** open
16. **Real-data discussion too handwavy; no posterior shown.** Add structure + a posterior plot of
    the dollar total (§9.11). — notebook figure + prose. **Status:** open
17. **Appendix audit — one section per technical concept, with example + plot.** Missing: classical
    optimization (SLSQP/constrained LS), permutation test & p-value, placebo-in-time, pre-fit gate,
    RMSE, randomization interval by inversion, Dirichlet, posterior predictive, VOI, Bernstein–von
    Mises. (Currently 9.A only has referee / AR(1)-as-GLS / persistent-offset.) — prose + notebook
    figures. **Status:** open
18. **Update the notebook to its final lecture form.** — notebook. **Status:** open

---

## 2026-07-15 — Ch. 9 digest pass: numbered fixes from Francesco

Running numbered list of changes requested by Francesco while digesting Chapter 9
(`book/chapters/geo_lift.tex`) for the SDA Bocconi lecture. Newest fix at the bottom of
this sub-list so the numbering stays stable. Some fixes below target **Ch. 1
(foundations)** or **Ch. 13 (IV)** where the concept actually lives — each fix names its
target file/section explicitly. Fixes 2–5 originate from a lecture-slide review during the
Ch. 9 digest (slides: "Correlation and causation diverge in both directions", "Confounding:
the business case").

### Fix 1 — remove all em-dashes from the chapter

- **Location:** `book/chapters/geo_lift.tex` (entire chapter; **183** LaTeX `---` occurrences
  as of 2026-07-15).
- **What / why:** Francesco wants no em-dashes in the chapter. They are used heavily throughout
  (prose, intuition/recap boxes). Figure/table numbers are injected macros and are unaffected.
- **Proposed fix:** replace every `---` with the appropriate alternative rather than a blanket
  swap — a comma for a parenthetical aside, a colon where the dash introduces a consequence,
  parentheses for a true aside, or a sentence split where the dash joins two independent clauses.
  Confirm with `grep -c -- '---' geo_lift.tex` returning 0. (Tables are `\input`, so no
  `booktabs` rules live in this file to catch.)
- **Status:** open

### Fix 2 — teach "correlation and causation diverge in BOTH directions" (causation without correlation)

- **Location:** **Ch. 1 (`book/chapters/foundations.tex`)**, the "correlation is not causation"
  framing near §1.2/§1.3 (wherever the naive difference is first motivated). Also surfaces as a
  lecture-intro slide.
- **What / why:** the book (like most treatments) teaches only the familiar direction — correlation
  without causation (confounding). The **converse** is missing and is the more surprising half for an
  MBA audience: a genuine, large causal effect can leave **no observable correlation** when an agent
  actively controls the outcome. The signature case is a **controller offsetting disturbances**: the
  action's variation is absorbed into the disturbance it cancels, so the outcome goes flat and
  action↔outcome co-movement vanishes even though the action does all the work.
- **Precise content to add:**
  - The mechanism, one line of math: with `Y = βX + γD + ε` and a controller setting
    `X = −(γ/β)D` to hold `Y` steady, `Y ≈ ε` (flat), so `Corr(X,Y) → 0` while `β` (the effect) is
    unchanged. Perfect control ⇒ exactly zero correlation with a fully non-zero effect.
  - **Milton Friedman's thermostat** as the canonical hook (name it): furnace roars on cold days,
    idles on warm ones, room temperature barely moves ⇒ `Corr(furnace, temperature) ≈ 0` or even
    negative, yet the furnace is the whole cause of comfort. Same shape: pilot vs wind, cruise
    control vs hills, **central bank moving rates to offset shocks so inflation sits near target**
    (this is the slide's example — keep it).
  - The **magnitude** corollary (both slide bullets): absence of correlation ≠ absence of effect;
    correlation magnitude ≠ effect magnitude (attenuation shrinks it, confounding inflates it,
    control zeroes it). Correlation is a property of the *distribution the system produced*; the
    effect is a property of *what an intervention would do*.
  - Marketing version to land it in-domain: a mature brand that spends **more** defensively when it
    forecasts a weak quarter ⇒ spend and sales look flat or negatively correlated though spend
    works; only a design that severs the "spend responds to forecast" loop (experiment, or synthetic
    control against unmanaged markets) recovers the effect. **This is the deepest reason Ch. 9 exists**
    — you cannot read a lift off co-movement in either direction.
- **Asset:** optional small twin-panel plot (already sketched on the slide): controlled action swings
  wide, outcome pinned flat, `Corr ≈ 0.04`.
- **Status:** open

### Fix 3 — expand "seeing is not doing" with the barometer + graph-surgery precision

- **Location:** **Ch. 1 (`book/chapters/foundations.tex`)**, §1.4 subsection "Seeing is not doing".
  **NB: overlaps the existing 2026-07-14 entry "§1.4 'Seeing is not doing': expand the do() vs
  observe intuition"** — fold this in there rather than duplicating; this fix just pins the two
  precise points that must land.
- **What / why:** two precise points, currently fuzzy:
  1. **`do()` deletes arrows *into* the intervened node; observing does not.** Barometer graph
     `B ← P → S` (pressure `P` common cause of needle `B` and storm `S`; no `B → S`). *Seeing* a low
     needle is informative about storms via the backdoor `B ← P → S`. *Forcing* the needle,
     `do(B=low)`, deletes the arrow `P → B`, so `B` carries no information about `P` and hence none
     about `S`: the weather is unmoved. Randomization is literally performing `do()` (coin flip
     overrides natural assignment, deletes incoming arrows).
  2. **Conditioning ≠ deleting arrows.** This is the precise correction for a common student error
     (and worth stating explicitly in the DAG subsections). Conditioning on a confounder **blocks the
     backdoor path *through* it** (a fork is blocked by conditioning on the middle node); it does not
     delete arrows. For a pure confounder the end result matches `do()` (you recover `X → Y`), but the
     mechanism differs, and the difference is what matters once colliders/mediators appear. State:
     "conditioning holds the confounder fixed so it cannot generate spurious co-movement; `do()`
     deletes the incoming arrows."
- **Status:** open

### Fix 4 — add "Confounding: the business case" with the two remedies worked out

- **Location:** **Ch. 1 (`book/chapters/foundations.tex`)**, the confounding / §1.4 material; also a
  lecture slide ("Confounding: the business case", ad spend → sales).
- **What / why:** make the confounding story a concrete business case and, crucially, spell out the
  **two remedies** and their shared precondition — this is the hinge that sets up the whole
  SC-vs-IV lecture.
  - **The fork is the bias:** the confounder (brand strength & seasonality) drives *both* arrows —
    `C → spend` (budgets raised in anticipation of strong demand) **and** `C → sales` (strong seasons
    sell more on their own). It is the coexistence of the two arrows, not `C → spend` alone, that
    inflates the naive slope. (If `C` moved spend but not sales, there'd be no confounding — it would
    be a clean instrument.)
  - **Remedy 1 — hold the confounder fixed (condition/adjust):** compare high- vs low-spend weeks
    *within* the same season and the same brand-strength band (week-of-year fixed effects; a
    brand-tracker / baseline-demand control). Picture = the slide's Simpson's-style fire-engine plot:
    pooled slope spuriously positive, within-severity-band slopes flat; severity is the confounder.
    **Catch:** you can only hold fixed what you can *measure*; an unobserved planner signal leaves
    residual confounding.
  - **Remedy 2 — find variation in spend unrelated to the confounder (exogenous variation):** the
    designed experiment (geo test / randomized holdout — Ch. 9), or a natural experiment / instrument
    (ad-platform outage, pacing glitch, regulatory block, auction-price shock from unrelated
    advertisers, capacity-sequenced rollout — Ch. 13).
  - **The shared precondition, with the one exception (important nuance the slide states loosely):**
    both observational remedies "require knowing what the confounders are" — adjustment needs them
    *measured*; an instrument needs the unrelatedness *defended* against them. The **single exception
    is a fully randomized experiment**, which breaks the arrow from *every* confounder at once,
    observed or not — which is exactly why the geo experiment is the gold standard in Ch. 9 and why,
    once the coin flip is gone, you are back to needing to know your confounders and building the
    counterfactual by hand.
- **Status:** open

### Fix 5 — map synthetic control and IV onto the DAG (with the three-DAG figure)

- **Location:** primarily **Ch. 9 §9.4 Identification (`geo_lift.tex`, `sec:sc:ident`)** for the SC
  panel and **Ch. 13 Identification (`iv.tex`)** for the IV panel; plus a short shared "two remedies →
  two methods" bridge (either the end of Ch. 1 §1.4 or the top of each method chapter). The figure is
  designed and delivered (SVG/HTML: `confounding_sc_iv_dags.svg`) — author it as a **TikZ** figure in
  the book (it is a schematic DAG, not an injected `cmp` data figure), reusing the slides' convention:
  **red dashed = backdoor/confound, navy = causal effect, green = exogenous instrument, dashed node =
  unobserved.**
- **What / why:** state precisely, in DAG terms, what each method does to the confounded picture
  `spend ← C → sales`:
  - **Synthetic control = the "hold the confounder fixed" remedy for *unobserved* confounders.** The
    real confounders are latent shared factors (trend, season, macro) you never observe, but they are
    **shared across units and stable over time**. So instead of conditioning on `C` directly, build a
    donor blend whose factor loadings match the treated unit's; the synthetic twin then carries the
    *same* `C`, and `τ̂ = Y₀ − Ŷ₀(0)` cancels it — backdoor closed by **matching on the confounder's
    footprint through the donor pool**. This is *why the pre-fit is everything*: a good pre-period
    match is the evidence that the twin shares the treated unit's confounders. (Connect explicitly to
    `as:sc:hull` and `as:sc:prefit`.)
  - **IV = the "find clean variation" remedy: bypass, don't block.** Add a node `Z` with `Z → spend`,
    `Z ⟂ C` (independence / as-good-as-random) and **no `Z → sales` except through spend**
    (exclusion). Read the effect off only the `Z`-driven slice of spend, which is unrelated to the
    confounder: effect = (Z-driven change in sales) ÷ (Z-driven change in spend). The confounding
    arrows stay in place; IV just refuses to use any spend variation except the exogenous piece.
  - **The one-line contrast to print under the figure:** the disease is the backdoor
    `spend ← C → sales`; **synthetic control removes the backdoor** (a twin that shares `C`),
    **IV bypasses it** (a source of variation `C` doesn't touch). Same disease, two cures — the two
    halves of the lecture.
- **Also fold in Fix 3's precision here:** SC "conditions on `C`" by *matching*, not by deleting
  arrows — keep the conditioning-blocks-the-path language consistent.
- **Suggested TikZ skeleton (three side-by-side DAGs; body to refine to house style):**
  ```
  % Panel 1 — confounded: C at top; X=spend, Y=sales at bottom.
  %   C -> X (red, dashed), C -> Y (red, dashed), X -> Y (navy).
  % Panel 2 — SC: C (dashed/unobserved) at top; Campaign -> Y0 (navy);
  %   C -> Y0 (red, dashed), C -> Yhat (red, dashed) "same loadings";
  %   caption: tau = Y0 - Yhat, shared C cancels.
  % Panel 3 — IV: C at top; Z (green) -> X (navy path) -> Y;
  %   C -> X (red, dashed), C -> Y (red, dashed);
  %   annotate "Z indep C" and "no Z->Y (exclusion)".
  ```
- **Status:** open

---

## 2026-07-15 — 🔴 CACHE: the fit key does not include the DATA, so a DGP change can serve a poisoned fit

- **Location:** `src/cmp/cache.py` (`load_or_run` / `_code_fingerprint`), interacting with every fit
  keyed on `inputs=dict(seed=..., fast=..., model=...)` that does NOT pass the data.

- **What / why.** The 2026-07-15 code-fingerprint fix hashes the source of the cmp functions the
  fit's callable *reaches*. But a DGP is typically called OUTSIDE the fit lambda — the data `X, y`
  is built first, then handed to a `pm.Model`, then `lambda: pm.sample(model)` is cached. That
  lambda's call graph is `pm.sample`, not `dgp.*`, so a change to the DGP does not change the code
  fingerprint. And the `inputs` dict carries only `seed`/`fast`/`model`, not the data. So **if the
  data changes but the seed does not, `load_or_run` serves the OLD fit** — computed on the old data.

- **How it bit (concretely, this session).** A transient over-reach in `dgp.price_panel` changed
  nb03's panel; nb03 ran and cached its hierarchical fit on that wrong data; the over-reach was then
  reverted. Every subsequent nb03 run served the poisoned fit (same key), giving elasticities near
  −0.5 where the truth is −1.4 and the classical OLS recovers −1.45. Only `CMP_REFIT=1` cleared it.
  The MODEL was correct throughout — a standalone refit recovers the truth (mu_beta −1.44, R-hat
  1.005). It was purely a stale-cache-across-a-data-change failure.

- **Why nb00/01/05 (uplift DGP also changed) are NOT poisoned:** their fits were EXCLUDED from cache
  adoption and hit a cache miss on the new fingerprint format, so they refit fresh on the corrected
  data. nb03 was the only one adopted, and adoption renamed the poisoned file onto the new key.

- **Proposed fix:** fold a hash of the observed data into the fit key. Either (a) require every
  `load_or_run(..., inputs=...)` for a fit to include the outcome/design arrays (so `_fingerprint`
  hashes them — it already handles ndarrays and, since the 2026-07-14 fix, pandas), or (b) fold the
  `dgp` module's source hash into `_code_fingerprint` unconditionally (over-broad: any dgp edit
  refits everything, but safe). Add a guard: a fit whose recovered parameter is wildly off the
  classical point estimate should warn.

- **Operational rule until fixed:** after ANY change to a `dgp.*` generator, re-execute the affected
  notebooks with `CMP_REFIT=1`, not plain re-execution.

- **Status:** open (nb03 force-refit clears the immediate damage; the key itself is still data-blind)

---

## 2026-07-15 — 🔴 CRITICAL (Ch. 13): the Gaussian IV model's bias is blamed on the LIKELIHOOD. It provably does not come from there. It is the PRIOR on rho.

- **Location:** `book/chapters/iv.tex` §13.6–§13.7 (≈ lines 638–645, 790–809), and the claim at
  ≈ :570–572 that the probit-vs-Gaussian comparison is *"a clean experiment in which the prior, the
  data, the instrument and the estimand are all held fixed and **only the likelihood moves**."*

- **What the chapter says.** That the joint-Gaussian arm's bias and 80 % under-coverage are caused by
  its **linear-probability first stage** — "the Bayesian model's own error, caught in the act by the
  PPC".

- **Why that is FALSE — and this is a proof, not an opinion.** `eq:iv:joint` factors as
  f(X)·f(Y|X), and f(Y|X) is the **control-function regression**, which for a just-identified linear
  IV is *algebraically identical to 2SLS*. Verified numerically on the chapter's own simulator
  (`dgp.iv_ad_exposure`, 40 seeds, n = 3000, truth 15):
  ```
  2SLS/Wald            mean 15.212   bias +0.212
  joint-Gaussian MLE   mean 15.212   bias +0.212
  naive OLS            mean 23.141   bias +8.141
  max |MLE - 2SLS| over 40 seeds = 3.5e-13
  ```
  **The Gaussian density on a binary X contributes exactly ZERO bias to beta.** The PPC is a correct
  diagnostic of a real support violation — that violation is simply *not what biases beta*.

- **What almost certainly does it: the prior.** `Sigma ~ LKJCholeskyCov(eta = 2)` (`eq:iv:priors`),
  which the chapter itself says *"pulls rho gently toward zero"* (:596). beta is **exactly linear** in
  the control-function coefficient lambda = rho·sigma_Y/sigma_X, with beta(lambda_MLE) = 2SLS and
  beta(0) = naive OLS. Shrinking rho therefore slides beta from 2SLS toward OLS. On seed 37:
  2SLS = 16.55, naive = 23.67; retaining ~83 % of lambda_MLE gives **17.73 = the reported
  `nb11.gauss_mean`**. Right direction, right magnitude, and it explains `gauss_seed_bias = +1.50`
  (upward, *toward OLS*) and the 80 % coverage.

- **And the "clean experiment" is not clean.** `eq:iv:priors` has `Sigma ~ LKJ(eta=2)`;
  `eq:iv:probit_priors` has `rho ~ Uniform(-0.95, 0.95)`. **The prior on the one parameter that
  controls the bias was NOT held fixed** — the probit repair silently removed the shrinkage. §13.6's
  "prior, priced rather than warned about" experiment only varied the *coefficient* priors, never the
  LKJ, so the prior was never actually exonerated on the parameter that matters.

- **Proposed fix (needs a refit, not a prose edit):**
  1. Refit `eq:iv:joint` with `rho ~ Uniform(-0.95, 0.95)` (or LKJ eta = 1) — one-line prior swap —
     and re-run the 20-seed bias/coverage study.
  2. If the bias and under-coverage largely vanish (expected), §13.6/§13.7's thesis must be rewritten
     as **"the prior on rho, not the likelihood"**. That is a *better* chapter — it is the one place in
     the book where the prior demonstrably does real damage, which the book's own spine claims is rare.
  3. If the bias survives, the chapter still needs a new explanation, because the likelihood is
     provably not it.
  4. Whatever the outcome, fix the "only the likelihood moves" sentence: hold the rho prior fixed
     across the two likelihoods, or stop calling it a clean experiment.

- **DO NOT SHIP §13.7 AS IT STANDS.** It teaches a false causal attribution, and the book's whole
  thesis is that you must diagnose *which* component failed.

- **Status:** open — found by the adversarial referee, 2026-07-15. Not yet fixed.

---

## 2026-07-14 — 🔴 CRITICAL (library + Ch. 9): `sc_weights_slsqp` silently returns its equal-weight STARTING POINT, and a headline chapter number is an artifact of it

- **Location:** `src/cmp/estimators.py:360` (`sc_weights_slsqp`). Consumed by the placebo-in-space
  permutations, the LOO/donor-robustness checks and the launch-date sensitivity in nb07 / nb07b.

- **The bug:** the function guards only `if not res.success`. But SLSQP frequently returns
  **`success = True` while never moving off `w0 = 1/J`** — it terminates at the starting point and
  reports convergence. The returned "fit" is then just the equal-weight average of the donor pool.
  **Reproduced:** across seeds 0–5 alone, **36 placebo fits** report success with weights identical
  to `w0` to 1e-6, and a pre-period RMSE identical to the equal-weight start (e.g. seed 0, market 0:
  12.1 either way). The `not res.success` warning never fires, so nothing downstream notices.

- **What it corrupts — and this is a number the book prints:** nb07 cell 13/14 claims the
  out-of-sample gap error is autocorrelated at **≈ 0.93 at every lag out to 8 weeks**, and that claim
  is the stated motivation for the AR(1) likelihood. It is an **artifact of the stuck fits**: on the
  converged worlds the ACF is **≈ 0.28 / 0.36 / 0.24 / 0.30 / 0.35**; the broken worlds alone give
  0.99. Affects `nb07.rho_one`, `nb07.rho_eight`, the `fig:sc:acf` caption, and the surrounding
  markdown. Probably also explains "5 of 29 donors dropped by the 5x pre-fit filter".

- **What SURVIVES:** the chapter's thesis is unharmed. The persistence is real, the iid likelihood is
  still wrong, and the **AR(1) posterior is fitted on the real panel, not via SLSQP** — `rho_post`
  = 0.54, 90 % [0.21, 0.87], which is consistent with ~0.3 and *not* with 0.93. The coverage repair
  (50 % → 88 %) stands. **The lesson survives; the number 0.93 does not.**

- **Proposed fix:**
  1. In `sc_weights_slsqp`, detect the non-move: compare the achieved loss against the loss at `w0`
     and against a cheap reference (e.g. NNLS or a multi-start), and **raise or warn** when the
     optimizer has not improved on its start. Consider a better `w0` (a random or NNLS-based start)
     and/or a multi-start loop. `res.success` alone is not a convergence test.
  2. Add a regression guard: assert that on a panel with a known good synthetic, the fitted pre-RMSE
     is materially below the equal-weight pre-RMSE.
  3. Re-emit `rho_one` / `rho_eight` from the **converged** worlds only, and rewrite nb07's cell-13/14
     markdown and the `fig:sc:acf` caption around ~0.3, not 0.93.

- **Status:** open — FOUND during the Ch. 9 upgrade; NOT yet fixed. It is a shared-library change that
  moves numbers, so it must land BEFORE the full re-execution.

---

## 2026-07-14 — Ch. 9: the simplex argument as currently written is FALSE on this panel — do not repeat it

- **Location:** `book/chapters/geo_lift.tex` §9.3 ("The estimator"), the paragraph beginning "The
  simplex is not decoration", and any figure caption arguing the same.

- **What / why:** the chapter says that dropping the simplex constraint gives a synthetic that "may
  sit outside the range of every real market". **Measured, on this panel, that is not what happens.**
  Unconstrained least squares gives 12 negative weights (min −0.79) but **no weight above 1**
  (max +0.94), and the unconstrained synthetic **never leaves the donors' pointwise min–max envelope**
  (0 of 60 weeks). Worse for the story as told: the unconstrained 20-week total (**€267k**) lands
  *closer* to the planted **€284k** than the simplex fit's **€260k**, and the spurious-lift spread ties.

- **What IS true and measured:** the unconstrained fit fits the pre-period **better** (RMSPE 1.79 vs
  3.23) and predicts **worse out of sample** (6.8 vs 4.1 against the true untreated path; 6.30 vs 3.89
  across the converged zero-lift worlds — **1.6x**). That is the honest case for the constraint: it is
  a guarantee about the *object* — an interpolation you can defend — not a promise to win any given
  panel. Write that, and do not write "the unconstrained fit blows up".

- **Status:** **done** (2026-07-15 — verified in `book/chapters/geo_lift.tex`). §9.2 "The simplex:
  interpolation, not extrapolation" now makes exactly the corrected argument: it reports that the
  unconstrained fit tracks the pre-period *better* (RMSE `\nbSevenRmspeUnconstrained` vs
  `\nbSevenRmspeSimplex`) and predicts *worse* out of sample (`\nbSevenHullOosRatio`× on zero-lift
  placebo worlds), and the intuition box "The constraint is a promise about the object, not about the
  panel" replaces the old "the unconstrained fit blows up" framing. The §9.3 "The estimator"
  paragraph carries the same corrected language. No occurrence of "may sit outside the range of every
  real market" remains.

---

## 2026-07-14 — Ch. 1 REBUILT to the new standard (reference implementation) — and the debt it created

- **Status:** `done` for Chapter 1 (`book/build/ch01_foundations.pdf`, 36 pp). The eight principles
  below are now the bar; Ch. 9 and Ch. 13 are being brought to it next (entry below).

- **What "the standard" now means, concretely** (this is the checklist for every other chapter):
  1. **Define-then-use.** A §N.2 vocabulary section, built on the chapter's own running example,
     before any term is used. Ch. 1 is exempt from the uniform method-template for this reason, and
     says so in its file header.
  2. **Teach, don't report.** Every diagnostic: what it is → the math → *how it could fail* → what it
     says here. A test that cannot fail is not a test, and a diagnostic reported without its failure
     mode is a decoration.
  3. **A worked micro-example** for the chapter's hardest object, with an identity that holds
     *exactly* on the page and is asserted in code (Ch. 1: the six-row oracle table, where
     naive €47.27 = ATT €20.84 + selection bias €26.43).
  4. **No bare constants inside displayed equations.** Named symbols; values and *justifications* in a
     parameter table whose "why this value" column is checkable against a number elsewhere in the
     chapter.
  5. **A visual for every function and every quantitative claim**, with the stated number readable
     *off the plot* (Ch. 1: the τ histogram now shades and labels the 29 % / 30 % regions).
  6. **Intuition and recap boxes** (`\begin{intuition}{...}` / `\begin{recap}`, defined in
     `preamble.tex`). Used sparingly — a box used for everything stops being read.
  7. **The real-data section as a guided walkthrough**, one idea per step (Ch. 1: LaLonde in six).
  8. **Every number injected.** Unchanged, and it is what caught the €3.25-vs-€3.26 slip.

- **DEBT — Chapter 13 is now load-bearing for Chapter 1.** Ch. 1 has **removed LATE from its estimand
  catalogue** and defers compliers/principal strata *entirely* to Ch. 13, on the grounds that LATE
  cannot be defined honestly before instruments exist. Until Ch. 13's vocabulary section lands, Ch. 1
  contains a forward promise nothing redeems.

- **Also landed, book-wide (affects every chapter):** floats are now emitted `[tb]` instead of
  `[htbp]` (`cmp.report.table`, `book/build.py`) with the float fractions loosened in
  `preamble.tex` — a float placed "here" strands itself mid-page. Figures re-anchor on the next
  build; **tables only re-anchor when their notebook re-executes**, since placement is baked in at
  emit time. So the book's layout stays non-uniform until the pending full re-execution.

---

## 2026-07-14 — IN PROGRESS: Ch. 9 (nb07 + 07b) and Ch. 13 (nb11 + 11b) to the Ch. 1 standard

- **Scope:** notebooks 07, 07b, 11, 11b **and** `book/chapters/geo_lift.tex`, `book/chapters/iv.tex`.
  Both the lab and the book, per the eight principles above. Per-chapter §N.2 vocabulary (each
  chapter readable standalone — the offprints are how chapters reach students).

- **Measured gap** (these chapters are the *deepest* in the book; the gap is not depth):
  **34 bare numeric literals** inside geo_lift.tex's displayed equations, **48** in iv.tex, and
  **zero** teaching boxes in either.

- **Ch. 9 — new assets:** panel sample rows; **the donor-weights worked example** (the counterfactual
  as a weighted average, computed by hand for one named week, with the weights-sum-to-one and
  contributions-sum-to-synthetic identities asserted); a **simplex figure** (constrained vs
  unconstrained weights — dropping the constraint fits the pre-period better and *extrapolates*);
  a **placebo-in-space figure** with the permutation p readable off the plot; a parameter table.
  §9.10 (07b, Google geo) becomes a six-step walkthrough — it has a randomized referee, so it is the
  same exam LaLonde sits.

- **Ch. 13 — new assets:** the **principal-strata worked table** (both potential *treatments* X(0),
  X(1); the four types; the defier row empty *by construction*, so monotonicity is seen rather than
  assumed; and Wald = reduced form ÷ first stage = the complier average, asserted); a **Wald-as-two-
  slopes figure**; a parameter table.

- **Ch. 13 also closes a known MAJOR gap:** 11b asserts that nb11's linear-probability first-stage
  error is "drowned" at Criteo scale but **never fits the probit to check** — while its sibling 07b
  does exactly the analogous check for nb07's AR(1) repair. The probit refit is added and both
  posteriors graded against the 13.98M-row Wald anchor.

- **Execution note — the cache-key bug applies here.** These notebooks' *models* change in this pass,
  and the cache key does not fingerprint model code, so a plain re-execution would silently load
  posteriors for models that no longer exist. **These four must run with `CMP_REFIT=1`.**
  nb11/11b are `cmp-legacy` (pymc 5); nb07/07b are `cmp-core`. Caches are warm (Criteo + Google geo
  present), so no downloads.

- **Status:** in-progress — **Ch. 9 book-side assets have landed** (verified in `geo_lift.tex`,
  2026-07-15): the §9.2 vocabulary section, `tab:sc:panel` (panel sample rows), `tab:sc:donorcalc`
  (donor-weights worked example with the weights-sum-to-one / contributions-sum-to-synthetic
  identities), `fig:sc:simplex`, `fig:sc:placebodist` + `fig:sc:placebo`, `tab:sc:params`, the §9.10
  (07b) guided walkthrough, and intuition/recap teaching boxes are all present; the DGM equations use
  named symbols with a "why this value" parameter table (the 34-bare-literals gap is closed in the
  `.tex`). **Still open:** the Ch. 13 (iv.tex) side of this entry, and confirmation that every
  injected number comes from a `CMP_REFIT=1` re-execution of nb07/07b/nb11/11b (the numbers cannot be
  verified from the `.tex` alone — see the `sc_weights_slsqp` and cache-key entries, which must land
  before that re-execution).

---

## 2026-07-14 — STRUCTURAL (root cause): front-load the "notebook 0" vocabulary primer that the book currently buries

- **Location:** Book structure / Part I. The source material already exists:
  - `notebooks/00_foundations.ipynb` opens as *"00 · Foundations — the words the cookbook assumes … the notebook that comes **before** everything else. It builds the core vocabulary — potential outcomes, counterfactuals, confounding, selection bias, randomization, identification, the do-operator, DAGs, ATE vs ATT vs CATE — from nothing … No new theory here — it mirrors `docs/causal_inference_primer.pdf`."* Vocabulary is built **first** (Cell 1: unit/treatment/outcome → potential outcomes → the fundamental problem; then confounding, etc.), *then* demonstrated.
  - `docs/causal_inference_primer.pdf` (the primer nb00 mirrors) exists.
  - `book/BOOK_SPEC.md` maps nb00 → **Chapter 1** and applies the uniform *method-chapter* template: N.1 The decision → N.2 The data-generating model → N.3 Identification → …

- **What / why (this is the root cause):** The book flattened nb00's vocabulary-first material into the uniform chapter template, which front-loads *"The decision"* and *"The data-generating model"* **ahead of** *"Identification."* So the running example — fig. 1.1, the naive difference of means, the estimator ladder, the "average effect" — is introduced **before** the vocabulary that defines it. The primer layer that was designed to come first isn't present in the book as a front-loaded unit. Essentially every "used before defined" item in this list is a symptom of this one structural gap.

- **Proposed fix (agreed):** add the primer back at the very front, at MBA level.
  - **Guiding principle (agreed):** the running marketing example can double as the vehicle that *introduces* each concept — no need for an abstract primer divorced from the example. The rule is simply **define-then-use: never use a concept before it has been defined**, with the one example carrying the definitions.
  - **Preferred:** a short **Chapter 0 / Part I opener — "Vocabulary: the words the cookbook assumes"**, mirroring nb00's opening + `docs/causal_inference_primer.pdf`: define potential outcomes, the fundamental problem, ATE/ATT/CATE, confounding & selection bias, randomization, identification, the **naive difference of means** and its **standard error**, the **estimator ladder**, and DAGs — all *before* any running example uses them.
  - **Alternative (local):** exempt the Foundations chapter from the method-chapter template and reorder so Identification (§1.3) precedes the DGM (§1.2). Cleaner to add a dedicated primer, which also matches the original design intent ("the notebook that comes before everything else").
  - **"Bring it to the right level":** pitch for an MBA audience — minimal notation, one worked intuition per term, defer formal phrasing.
  - **Small worked examples with plots (agreed):** give each concept a compact, self-contained toy example that produces a figure, so it lands visually and not just verbally. Candidates: a 2×2 potential-outcomes table with the unobserved half greyed out (the fundamental problem); a scatter showing selection bias as loyal-vs-casual imbalance; coin-flip vs. targeted assignment side by side; one bar of the naive difference against the true ATE; the estimator ladder recovering a known effect rung by rung. (Consistent with the standalone "add a plot wherever a function is introduced" entry.)
  - **This reconciles the build-pipeline caveat:** because those examples compute numbers/figures, the primer should be **backed by an executed notebook** (a small primer notebook, or nb00's opening cells) that emits figures through the `cmp` pipeline — not hand-written front-matter. That keeps every number/figure under the "injected from an executed notebook" rule.
  - Doing this should close most of the Chapter-1 forward-reference items **at the root**; keep the review pass for the residue and later chapters.

- **Status:** open

---

## 2026-07-14 — STRUCTURAL: the chapter is too prose-heavy — restructure the rest of Ch. 1 (§1.5–§1.10) for active learning, not a wall of text

- **Location:** `book/chapters/foundations.tex`, especially §1.5 "The classical baseline: the estimator ladder," §1.6 "Diagnostics and validation," §1.7 "What can go wrong," §1.9 "The decision, in euros," §1.10 "Takeaways" — and the pattern repeats across the book.

- **What / why (reader verdict, emphatic):** the back half is largely uninterrupted prose. For an MBA reader meeting this material for the first time, **a wall of text is the wrong format**, however well-written — the concepts don't land without worked examples, visible math, figures, and structure. This is the **umbrella issue**; the "teach, don't just report," "add a visual," and "show-don't-tell (LaLonde)" entries each fix a slice of it. This entry is the systemic version: it's not one section, it's the register of the whole chapter.

- **Proposed fix — convert prose into a learning format throughout:**
  - **Worked examples with the computation shown**, not summarized — every estimator/test applied on the one-confounder data with the numbers on the page.
  - **Math shown step by step** — derive each ladder rung; write the estimator, its SE, the null a diagnostic checks.
  - **A figure or table beside each claim** (per "add a visual"); one idea per block.
  - **Structure:** short subsections, callout / intuition boxes, "what this buys / what can still break" recaps; repeat core concepts as they recur.
  - **Per section:** §1.5 derive naive → regression → IPW → AIPW, each applied + a plot; §1.6 teach each diagnostic (concept + math + applied + intuition); §1.7 show each failure mode with worked numbers/plots; §1.9 show the `P(effect > cost)` computation and the resulting policy explicitly; §1.10 takeaways as crisp bullets tied to the shown results.

- **Status:** open

---

## 2026-07-14 — Book-wide REVIEW PASS: terms used before they are defined (forward references)

- **Location:** Book-wide. A dedicated read-through is needed to catch every place a concept is invoked before it has been introduced. `\cref{}` forward-pointers exist in some cases, but the *term* is still used as if the reader already knows it, which breaks a first read.

- **What / why:** Recurring class of problem — the exposition assumes vocabulary it hasn't built yet. Needs a systematic sweep (ideally chapter by chapter, tracking first-use vs. definition of each key term), not just ad-hoc catches. **Likely root cause:** the missing front-loaded vocabulary primer — see the STRUCTURAL entry above; fixing that should close most of the Chapter-1 instances at once.

- **Known instances so far:**
  - **§1.2 "The one-confounder world"** (`book/chapters/foundations.tex`, ~line 101): opens with *"The estimator ladder of [§1.5] …"* — the **estimator ladder** is used here but not defined until §1.5 "The classical baseline: the estimator ladder." Has a `\cref`, but the concept is invoked cold.
  - **§1.2, below eq (1.3)**: *"planted average effect"* / **average effect** used before §1.3 defines the causal effect at all — see the dedicated entry below.
  - **Fig. 1.1 (§1.2)**: the plotted **naive difference of means** and the **±1 SE** error bars are used before §1.3 "The naive difference, decomposed" defines the naive contrast and its standard error — see the dedicated entry below.
  - **Eq (1.11), §1.3**: **LATE** is defined via **compliers**, but "complier" (and "instrument"/"encouragement") is never defined in Chapter 1 — the definition only appears in Ch. 13 (IV). See the dedicated entry below.
  - **Assumption 1.4, §1.3**: **"backdoor path" / "backdoor criterion"** used before **DAGs** are introduced in §1.4. See the DAG entry above.
  - _(add more as found)_

- **Proposed fix:**
  - Run a forward-reference audit: for each key term, record first-use section vs. definition section; flag every first-use that precedes its definition.
  - For each flagged case, either (a) add a one-line inline gloss at first use, (b) reorder so the definition comes first, or (c) reword to avoid the term until it's introduced. A bare `\cref` forward-pointer is not sufficient on its own for a term a first-time reader needs.

- **Status:** open

---

## 2026-07-14 — Book-wide PRINCIPLE: teach, don't just report — every test / diagnostic / method gets concept + math + application + intuition

- **Location:** Book-wide. Reader feedback generalizing the LaLonde note to the whole chapter and the rest of the book.

- **What / why:** the register too often **names a test and reports its result** — "the overlap diagnostic passes," "the placebo is clean," "R-hat < 1.01" — without teaching what the test *is*, what it's testing, the math behind it, how it's computed, and the intuition for why it works. We are teaching: the reader must see *how each concept/test is actually applied*, step by step, with repetition where it recurs.

- **For every test / diagnostic / estimator, include:** (a) what it is and what question it answers; (b) the math (the statistic, the formula, the null it checks); (c) how it's applied *here* — the concrete computation on this dataset, shown; (d) the intuition (why a pass/fail means what it means); *then* (e) the result. Not just (e).

- **Concrete instances (non-exhaustive):** §1.6 Diagnostics — overlap/balance (what an SMD is, the threshold, how it's computed), "bias is what survives repetition" (the multi-seed logic); placebo tests, recovery checks, sensitivity/robustness sweeps; PPC and R-hat/ESS wherever the Bayesian workflow appears; the estimator-ladder rungs (naive / regression / IPW / AIPW) — each derived and applied, not just tabulated; HAC / cluster / bootstrap SEs; permutation / randomization inference; first-stage / weak-instrument diagnostics (Ch. 13).

- **Proposed fix:** adopt as a standing writing rule (alongside "define-then-use" and "add a visual"); do a per-chapter pass converting every "mention + result" into "concept + math + applied computation + intuition + result."

- **Status:** open

---

## 2026-07-14 — Teach the frequentist-vs-Bayesian (bootstrap vs posterior) distinction in depth — using the examples that already exist; consider per-chapter appendices

- **Location:** primarily Ch. 2 "Point estimate vs posterior" (the spine), hooked from Ch. 1 §1.5 (the bootstrap mention), with payoff examples in Ch. 9 (nb07) and Ch. 13 (nb11).

- **DECISION (Francesco, 2026-07-14):** do **not** invent a new example to force this distinction. The baseball / hierarchical-shrinkage idea for Ch. 2 is **rejected** — hierarchical modelling is already covered in **Ch. 4 (nb02)**. **Notebooks 7 (synthetic control, synthetic data) and 11 (IV) are the focus of the lecture; nb7 stays synthetic.** If, after the nb7 fix, nb7/nb11 don't cleanly showcase the Bayes-vs-classical distinction, **that is acceptable — we live with it.** Still write the *conceptual* depth (bootstrap / BvM / `P(effect>cost)`), but source any worked illustration from nb7/nb11, not a new dataset.

- **What / why:** the bootstrap-vs-Bayes question — *"the two distributions look identical; how do we distinguish them?"* — is central and currently under-explained. Needs a proper treatment: (i) what the bootstrap is (resample → refit → percentile); (ii) **why the clouds coincide** — Bernstein–von Mises: large `n` + flat prior + correct likelihood → posterior ≈ sampling distribution of the estimator; (iii) **how they differ** — a distribution over *the estimator across hypothetical datasets* (`θ` fixed) vs over *the parameter given one dataset* (data fixed); confidence vs credible interval; the prior; and behaviour under misspecification; (iv) the decision consequence — only the posterior yields `P(effect > cost)`.

- **Structure option (Francesco's idea — adopt it):** **per-chapter appendices.** The book currently has only global appendices (A DGP, B cmp API, C environments). A methodological aside like this — or derivations, the bootstrap, BvM — could live in a *chapter* appendix so the main text stays readable while the rigor stays available. Consider adopting per-chapter appendices as a standing device.

- **Examples already in the book — surface them explicitly, teach with the numbers, cross-reference from Ch.1/Ch.2:**
  - **Ch. 13 IV (nb11) — clearest ADVANTAGES of Bayes:**
    - `P(β > c)`: *"What this classical apparatus cannot produce, at any level of effort, is P(β > c)"* (`iv.tex` ~404) — the decision rule *is* that probability; a confidence interval is a property of the procedure, not a probability about `β`.
    - Estimates the **endogeneity `ρ`** itself with a credible interval — names what 2SLS only projects away (*"2SLS removes the endogeneity by projection… no `ρ` to report at any width; the joint model estimates it"*; posterior `ρ` = *"evidence the classical arm cannot produce"*, `iv.tex` ~568–582).
    - Bonus: clean **prior-vs-likelihood** lesson — the LKJ library-default prior can put the truth *outside* the interval (defaulting failure) while a weakly-informative prior contains it; the probit-vs-LPM point (*"a posterior inherits every claim in its likelihood"*) = "prior does little, likelihood is the ballgame."
  - **Ch. 9 geo/SC (nb07) — ⚠️ the iid-underpricing discrepancy is PENDING A FIX (Francesco, 2026-07-14) and will be resolved.** Do **not** rely on nb07 as a standing Bayes-vs-frequentist discrepancy until the fixed version is checked — after the fix the arms may agree rather than show a ~2.8× underpricing. If the iid-vs-repaired contrast is removed entirely, do **not** manufacture a replacement example (per the DECISION above) — accept that nb7 may simply not be the distinction showcase, and we live with it. NOTE: BOOK_SPEC's thesis currently cites this exact nb07 result as flagship evidence for "misspecified likelihood, not paradigm" — confirm the thesis example survives the fix, or update BOOK_SPEC. **The Ch. 13 advantage example (`P(β>c)`, `ρ`) stands regardless.**
    - Open question for the rewrite: after the fix, is the iid-vs-repaired contrast **kept as a teaching device** (shipped number uses the repair; the contrast still illustrates the point) or **removed**? That decides whether nb07 remains the distinction example.
  - **Ch. 2 `point_vs_posterior`** is the dedicated spine that should carry the core treatment.

- **Proposed fix:** write the full treatment (bootstrap + BvM + the four distinguishers + `P(effect>cost)`) in Ch. 2; hook it from Ch. 1 §1.5's bootstrap line; make Ch. 9 and Ch. 13 explicitly cash it out as "the distinction" and "the advantage" respectively; put the derivations/depth in a chapter appendix. Also an instance of "teach, don't just report" (the §1.5 bootstrap is currently a one-liner).

- **Status:** open

---

## 2026-07-14 — §1.4: make the PURPOSE of the DAG section explicit (reader: "not clear how it's used / what's the point")

- **Location:** `book/chapters/foundations.tex`, §1.4 "The graph: seeing, doing, and what to condition on."

- **What / why:** the section presents graphs and rules but never states *why we're drawing graphs at all* or how they plug into the workflow, so the payoff is invisible. **The purpose: the DAG is the tool that decides what to adjust for.** Assumptions 1.2 (unconfoundedness) and 1.4 (valid adjustment set) both require knowing *which* variables belong in `X` — but "adjust for the confounders" is circular until something says what a confounder is. The DAG is that something: it turns the abstract assumption into an actionable rule (block backdoor paths; don't condition on mediators/colliders) and shows that the tempting "control for everything we have" *backfires* (fixes confounders, breaks mediators and colliders).

- **It's used immediately and later:** Table 1.1 *is* the backdoor adjustment executed by hand; the collider-priced subsection shows the euro cost of a wrong graph (analysing only responders manufactures an effect from nothing); and "what to control for" is the whole of Chapter 7, which this sets up.

- **Proposed fix:** open §1.4 with one short paragraph stating the job — *"before we can adjust, we must decide what to adjust for; the graph is how"* — and close it by cashing out: the graph told us to condition on loyalty (→ Table 1.1) and told us NOT to condition on "opened" or "responded" (→ the collider price). Make the arc explicit: **assumption (need a valid `X`) → tool (DAG / backdoor) → execution (Table 1.1) → cost of error (collider).** Ties to the "define DAGs early," "Three graphs / define adjust," and "Seeing is not doing" entries.

- **Status:** open

---

## 2026-07-14 — §1.8 LaLonde: rewrite as a guided, show-don't-tell walkthrough (define problem → explore data → graphs → reconnect to the chapter's math)

- **Location:** `book/chapters/foundations.tex`, §1.8 "On real data: LaLonde" (~lines 610–665), with `tab:fnd:lalonde` (naive −$635 / adjusted +$1,548 / benchmark +$1,800; 185 trainees vs 429 survey controls; 8 covariates; +$2,183 swing; within $252) and `fig:fnd:lalonde` (overlap: 60 % of controls below `e(x)=0.10` vs 5 % of trainees).

- **What / why:** Reader feedback — currently a **dense block of prose that's hard to follow for a learner**. This is the payoff of the whole chapter (the real-data proof), so it should be the *most* carefully taught section: **show each concept applied, don't just state it, and repeat as needed.**

- **Proposed structure (one idea per step; lead each with the question it answers; reconnect every step to earlier math):**
  1. **Define the problem plainly.** NSW had a randomized arm → true effect known (≈ +$1,800 on 1978 earnings). Throw away the experimental controls, replace with survey controls (CPS/PSID) = the analyst-without-an-experiment. Can adjustment recover the benchmark? *Reconnect:* this is grading on real data via a randomized benchmark (within-study design) — link to the "cannot be graded on real data" entry (§1.2 vs §1.8).
  2. **Explore the dataset.** Units (185 trainees vs 429 survey controls), treatment (job training), outcome (1978 earnings), the 8 covariates (age, education, race, marital, 1974/75 earnings). **ADD a covariate balance table** (means treated vs control + standardized mean differences) and **covariate-distribution plots** (prior earnings, age) so the selection is *visible*: trainees far more disadvantaged.
  3. **Seeing (naive = −$635).** *Reconnect to eq (decomp):* `naive = ATT + selection bias`; here `E[Y(0)|T=1] ≪ E[Y(0)|T=0]` (trainees' untrained baseline far below survey controls'), so selection bias is large & negative and flips the sign. Same head-start decomposition as §1.3, now on real data and negative. **Show the baseline-earnings gap explicitly.**
  4. **Doing (adjust = +$1,548).** Condition on the 8 covariates = the backdoor / g-formula "adjust" defined in §1.4; block the backdoor paths through prior earnings/age/etc. **Show the +$2,183 swing across zero and a naive → adjusted → benchmark bar chart** (benchmark as a line).
  5. **Why not exact — positivity fails.** Run the overlap diagnostic (`fig:fnd:lalonde`): 60 % of controls below `e(x)=0.10` vs 5 % of trainees. *Reconnect to Assumption 1.3 (positivity/overlap):* adjustment extrapolates across thin support; g-formula not licensed there → the $252 shortfall → why the field moved to trimming/matching (Dehejia–Wahba) and doubly-robust. **ADD a propensity-score histogram by arm.**
  6. **Restate the lesson** + why LaLonde is the canonical exam (both a randomized benchmark and an observational arm on the same treatment/population; marketing data never has the benchmark).

- **Assets:** reuse `tab:fnd:lalonde` + `fig:fnd:lalonde`. **ADD (emit from nb00, `CMP_REAL`):** covariate balance/SMD table; covariate-distribution plots (treated vs control); propensity-score histogram by arm; naive→adjusted→benchmark bar with benchmark line. All numbers via `cmp`.

- **Explicit cross-references to reconnect:** eq (decomp) / selection bias / `E[Y(0)|T=1]` (§1.3); backdoor + g-formula + the definition of "adjust" (§1.4); positivity (Assumption 1.3); the grading entry (§1.2 vs §1.8).

- **Style:** show don't tell; repeat core concepts as they recur; one idea per step. This is a *teaching* section, not a summary.

- **Status:** open

---

## 2026-07-14 — §1.4 "Seeing is not doing": expand the do() vs observe intuition (one of the most important points in the book)

- **Location:** `book/chapters/foundations.tex`, §1.4 "The graph…", subsection **"Seeing is not doing"** (~lines 318–333). Currently ~two sentences of definition (observe `X=x` selects units that arrived there; `do(X=x)` reaches in and sets it), then straight to the backdoor formula. Far too terse for how load-bearing the idea is.

- **What / why:** the observe-vs-intervene distinction is the conceptual pivot of the whole book — every euro decision is a `do()`, dashboards only ever show seeing, and confusing the two is the field's most expensive error. It deserves real intuition, not a definition and a formula.

- **Intuition to fold in:**
  - **A memorable non-marketing hook — the barometer.** A falling barometer predicts a storm, so *seeing* a low reading is informative; but *forcing* the needle down (`do(barometer=low)`) does nothing to the weather. Common cause (pressure) drives both; seeing tells you about pressure, doing severs it. Confounding in one image. (Rooster/sunrise works too.)
  - **Marketing version on the running example:** *seeing* "emailed customers spend more" (€9.26) mixes the email's effect with the fact that loyal customers were the ones emailed; *doing* — email a randomly chosen customer, overriding the targeting rule — isolates the €6. The gap is the loyalty the targeting rule let ride along.
  - **Graph surgery (the mechanical picture):** `do(T=t)` = delete every arrow pointing *into* `T` (its natural causes are overridden), fix `T=t`, read off `Y`. Observing leaves the graph intact and filters. The cut `loyalty → T` arrow *is* the €9.26-vs-€6 gap.
  - **Decision framing:** "Should *we* send it?" sets `T=1` by fiat — a `do()`, not "what do emailed customers look like?" Dashboard = seeing; decision = doing.
  - **Randomization = physically performing `do()`:** the coin flip overrides natural assignment and deletes the incoming arrows to `T`, so an RCT measures `P(Y|do(T=t))` directly. Observational backdoor adjustment is just reconstructing doing from seeing by conditioning on the severed confounders.
  - **Seeing can flip the sign:** LaLonde's naive estimate is negative, the true effect positive — the do-operator says which direction is real.

- **Show the €9.26-vs-€6 gap EXPLICITLY (not just assert it) — and name the backdoor.** The current text asserts *"seeing gives €9.26 and doing is worth €6"* but never shows why, and never says what the backdoor is. The one-confounder world is `T ~ Bernoulli(σ(0.8·L))`, `Y = 20 + 5L + 6T + 3G + ε`. **The single backdoor path is `T ← loyalty (L) → Y`** — `L` raises both the send probability (`0.8·L`) and spend (`5·L`). `G` is *not* a confounder (it moves only `Y`; included as a deliberate foil). So **doing = €6** (the coefficient on `T`), **seeing = €9.26**, and the **€3.26 gap is exactly the backdoor association through loyalty**. Make it concrete: decompose `€9.26 = €6 (causal) + €3.26 (backdoor)`, draw the `T ← L → Y` DAG with the backdoor arrow highlighted, and pair it with the seeing-vs-doing bars; blocking the path (stratify by loyalty = Table 1.1's quintiles) closes the €3.26 back to €6. **Confounding shown as a number: the gap *is* the backdoor.**

- **Proposed fix:** actually *explain all of the above inline in the chapter* — rewrite "Seeing is not doing" to lead with the barometer hook and the graph-surgery picture *before* eq (backdoor), so the formula formalizes an idea already understood; add supporting figures (intact DAG vs mutilated/"arrows-into-`T`-deleted" DAG side by side; the `T ← L → Y` backdoor with its €3.26 highlighted; seeing-vs-doing bars). Ties to the "define DAGs early / add a visual / Table 1.1 plots" items.

- **Status:** open

---

## 2026-07-14 — §1.4 "Three graphs…": define "adjust", and teach DAGs from scratch (math + email example) for a first-time reader

- **Location:** `book/chapters/foundations.tex`, §1.4 "The graph…", subsection **"Three graphs, and only one calls for adjustment"** (~lines 335–359). Uses bold **"Adjust." / "Do not adjust"** for confounder / mediator / collider, but **never defines what "adjust" means**, and is too terse / math-light for someone meeting DAGs for the first time.

- **What / why:** "adjust" = "condition on" = "control for" is the load-bearing verb of the section and is used undefined. A first-time reader doesn't know it means *stratify by / include as a regressor / reweight* — i.e. the backdoor-adjustment operation. The section also states the three structures as assertions without the math of *why* conditioning helps in one and hurts in the other two. Target reader (Francesco's framing): **someone reading about DAGs for the first time, learning them through the email example.**

- **Content to add (teach it, don't assert it):**
  - **DAG basics:** node = variable, arrow `A→B` = direct cause, acyclic = no loops. **Association flows along paths** (any trail of arrows, direction-agnostic); a path is **open** or **blocked**; conditioning changes which.
  - **Define "adjust" once, operationally *and* in math:** stratify / regress / reweight, all equivalent; formally the g-formula `ATE = Σₓ {E[Y|T=1,X=x] − E[Y|T=0,X=x]} P(X=x)` — inner `E[·|X=x]` = the conditioning, outer `Σₓ…P(X=x)` = averaging over the **population** mix. Contrast with the naive contrast, which averages over the **within-arm** mix (the bias).
  - **Three structures on emails, each with the conditioning math:**
    - **Confounder `T ← L → Y`** (loyalty): backdoor, open by default → adjust. `Y = 20+5L+6T+3G+ε`: with `L` in the regression `β≈6`, without it `β≈9.26`. Legal because `{Y(0),Y(1)} ⊥ T | L`.
    - **Mediator `T → M → Y`** (`M` = opened): causal path, open by default → conditioning removes part of the effect → do **not** adjust (Ch. 6 for direct/indirect).
    - **Collider `T → C ← Y`** (`C` = responded): blocked by default → conditioning **opens** it and manufactures association → do **not** condition (analysing only responders is the trap).
  - **The unifying rule (d-separation, lightly):** a path is blocked if it passes a chain/fork you condition on, or a collider you don't. Same operation, opposite effect by structure — which is why "control for everything" fixes case 1 and breaks cases 2–3.
  - Small DAG figure per structure (ties to "define DAGs early / add a visual").

- **Proposed fix:** rewrite the subsection at true-beginner level on the email example, defining "adjust" up front and giving the conditioning math for each structure. The DAG *basics* ideally live in the front primer (see the "define DAGs early" entry); this subsection then applies them. Complements the "Seeing is not doing" expansion.

- **Status:** open

---

## 2026-07-14 — §1.3 assumptions: rewrite for clarity + add worked examples (Assumptions 1.1 SUTVA, 1.2 unconfoundedness)

- **Location:** `book/chapters/foundations.tex`, §1.3 Identification, subsection "The assumptions, when there is no coin flip" (`as:fnd:sutva` … `as:fnd:backdoor`, ~lines 232–287). *(These live in §1.3, not §1.2.)*

- **Assumption 1.1 (SUTVA), `as:fnd:sutva`:** the paragraph is **not understandable as written** — "no interference" and "one version of treatment" are stated too compactly/abstractly. Rewrite in plain English, led by a concrete example: *interference* — if an emailed customer forwards the offer to a non-emailed friend who then buys, that friend's outcome depends on someone else's treatment, breaking "own treatment only"; *one version* — if "the email" was really three different creatives, "emailed" isn't one well-defined thing. Keep the "untestable, discharged by knowing how the campaign ran" point, but lead with the example.

- **Assumption 1.2 (Unconfoundedness), `as:fnd:unconf`:** already better (has a plain-English gloss), but add an explicit example so the conditional-independence statement lands — e.g. *"among customers with the same recency/frequency/engagement, whether they happened to be emailed tells you nothing more about what they would have spent — everything that made them likelier to be emailed is already in X."* Pair with a violation (a hidden 'about-to-churn' signal the analyst can't see that drives both send and spend).

- **Proposed fix:** reword both to lead with a one-sentence plain meaning + a concrete marketing example, then the formal statement, then the testable/untestable tag. Assumption 1.3 (positivity) already follows this shape (the "always-emailed region" example) — use it as the model.

- **Status:** open

---

## 2026-07-14 — Define DAGs (and "backdoor path") early and use them throughout; Assumption 1.4 uses them before they exist

- **Location:** `book/chapters/foundations.tex`. Assumption 1.4 "A valid adjustment set" (`as:fnd:backdoor`, ~line 280) invokes **"backdoor path"** and **"Pearl's backdoor criterion"** — but DAGs are only introduced in **§1.4 "The graph…"** (line 315), which comes *after*. Forward-reference again.

- **What / why:** the backdoor vocabulary (paths, forks, chains, colliders, blocking) is used before the reader has a DAG to hang it on. More broadly — **Francesco wants to use DAGs at every reasonable opportunity** across the book (they're the clearest way to show confounders / mediators / colliders), which requires defining them once, up front, then reusing.

- **For the record — backdoor path:** in a DAG, a path between `T` and `Y` that begins with an arrow *into* `T` (`T ← …`) — a non-causal route through a common cause, e.g. `T ← loyalty → Y`. It creates spurious `T–Y` association. A valid adjustment set blocks every backdoor path (condition on confounders) while containing no descendants of `T` (no mediators/colliders) — Pearl's backdoor criterion; what remains is the causal path `T → Y`.

- **Proposed fix:** introduce DAGs once, early (ideally the front primer): nodes = variables, arrows = direct causes, acyclic; fork / chain / collider; blocking and backdoor paths — with a small worked graph on the running example (`loyalty → email`, `loyalty → spend`). Then Assumption 1.4 reads as a named tool, and DAGs can be used freely everywhere after. Add small DAG figures wherever confounding / mediation / collider structure is discussed (ties to the "add a visual" convention).

- **Status:** open

---

## 2026-07-14 — Table 1.1 (strata / g-formula by hand): add supporting plots

- **Location:** `book/chapters/foundations.tex`, §1.3, **Table 1.1 = `tab:fnd:strata`** (`nb00_strata`, `\input` line 312), explanation ~lines 302–310. The table cuts loyalty into five quintiles and shows the within-quintile emailed−not difference (≈ the planted €6 in each), the strata-weighted average, the pooled naive (€9.26), and the "% emailed" climbing across quintiles.

- **What / why (good point):** the "seeing vs doing" lesson is exactly what a plot nails — the numbers are convincing but a figure makes the mechanism visible.

- **Proposed fix:** add one or two figures beside the table: (a) within-quintile treated−control differences as bars, with a line at the true €6 and a line at the pooled €9.26 — shows stratification recovers the truth while pooling doesn't; (b) "% emailed" per quintile as a bar/line — the confounding mechanism made visible (the emailed share climbing with loyalty *is* the whole explanation). A strata bar figure already exists in the nb00 cell — emit it via `cmp` so it stays tied to the table's numbers. (Ties to the "add a visual" convention.)

- **Status:** open

---

## 2026-07-14 — §1.2: show what the dataset actually looks like (a few sample rows)

- **Location:** `book/chapters/foundations.tex`, §1.2 "The data-generating model" (customer-file description + eqs 1.1–1.6). The DGM is currently given only as equations and prose; the reader never sees a concrete row of the simulated customer file.

- **What / why:** A short sample of the actual dataset — a handful of customers with their features and outcomes — makes the abstract DGM tangible *before* any estimation; the reader sees the columns they'll reason about. Pairs naturally with the `E[Y(0)|T=1]` worked-rows example (below) and the "make it visible" theme.

- **Proposed fix:** add a small `booktabs` table of ~5–8 sample rows from the nb00 customer file — columns like recency `R`, frequency `F`, monetary `M`, engagement `E`, baseline `μ₀(x)`, planted effect `τ(x)`, assignment `T`, observed spend `Y` (and, for a teaching/oracle version, `Y(0)` and `Y(1)` with the unobserved branch greyed). Emit it from nb00 via `cmp.report.table` so the rows are the real simulated data, not hand-typed. Consider one row per illustrative type (a persuadable, a sleeping dog, a loyal always-emailed customer) so the table also previews the heterogeneity.

- **Status:** open

---

## 2026-07-14 — §1.3: give E[Y(0) | T=1] a precise definition + a few-row worked example

- **Location:** `book/chapters/foundations.tex`, §1.3 "The naive difference, decomposed" (`eq:fnd:decomp`, ~lines 190–213). The text names `E[Y(0)|T=1]` as *"the mean untreated outcome among the treated — the one quantity nobody observes"* and uses it as the bridge term in the decomposition, but never shows it concretely.

- **What / why:** `E[Y(0)|T=1]` is the subtlest object in the chapter — a *counterfactual* mean (the treated group's outcome had they not been treated), unobservable by construction. A row-level example makes both it and the selection-bias decomposition tangible for an MBA reader. Same "make it visible / worked example" theme as the plots items.

- **Precise definition:** `E[Y(0)|T=1]` = the expected untreated potential outcome `Y(0)` averaged over the subpopulation that actually received treatment (`T=1`) — i.e. the mean outcome the treated group *would* have had, counterfactually, without treatment (the treated group's own baseline). Purely counterfactual: for treated units we observe `Y = Y(1)`, never `Y(0)`, so it is **not identified from the treated arm** without an assumption (randomization or unconfoundedness). Its twin `E[Y(0)|T=0]` is the controls' baseline and **is** observed (`= E[Y|T=0]`). The naive contrast substitutes the second for the first; `selection bias = E[Y(0)|T=1] − E[Y(0)|T=0]` is exactly that substitution error, and it is zero under randomization since `T ⟂ Y(0)`.

- **Worked example (starred = counterfactual, never observed):**

  | Customer | Segment | Y(0) | Y(1) | T | Observed Y |
  |---|---|---|---|---|---|
  | A | loyal | 30\* | 36 | 1 | 36 |
  | B | loyal | 26\* | 32 | 1 | 32 |
  | C | loyal | 28\* | 34 | 1 | 34 |
  | D | casual | 10 | 16\* | 0 | 10 |
  | E | casual | 12 | 18\* | 0 | 12 |
  | F | casual | 14 | 20\* | 0 | 14 |

  - `E[Y(0)|T=1]` = (30+26+28)/3 = **28** — loyal group's *unobserved* baseline.
  - `E[Y(0)|T=0]` = (10+12+14)/3 = **12** — casual controls' *observed* baseline.
  - selection bias = 28 − 12 = **16**; ATT = 34 − 28 = **6**; naive = 34 − 12 = **22**.
  - identity: 22 = 6 + 16 = ATT + selection bias. The €16 overstatement is exactly the wrong baseline (12 instead of 28).

- **Plain-English reading of selection bias** (`E[Y(0)|T=1] − E[Y(0)|T=0]`): the **head start (or handicap) the treated group already had** before any treatment — the gap in baseline outcomes between treated and controls that would exist even if *no one* had been treated. It answers "were the two groups comparable to begin with?" Positive bias = you treated the units already destined to do better, so the naive comparison credits the treatment for a gap it never created. In the example: the emailed loyalists would have outspent the casual controls by €16 *with no email at all* — pure incomparability, baked into who was chosen, nothing to do with whether the email works. Worth stating this sentence in the text, not just the formula.

- **Why randomization kills it (concise):** a coin flip makes `T` independent of everything the customer carries in — in particular of the baseline `Y(0)`. Independence means treated and controls share the *same* baseline distribution, so `E[Y(0)|T=1] = E[Y(0)|T=0] = E[Y(0)]` and the selection-bias term is **exactly zero**. No group has a head start because who gets treated has nothing to do with who was going to do well. The naive difference then collapses to the ATT (= ATE). (§1.3 "Randomization, and what it buys" already makes this point — keep the one-line intuition alongside the algebra.)

- **Proposed fix:** add a compact oracle-table example in §1.3 (a few rows, both potential outcomes, treated `Y(0)` cells greyed as "counterfactual") that computes `E[Y(0)|T=1]`, `E[Y(0)|T=0]`, selection bias, ATT and verifies eq (decomp). Numbers must come from nb00 (which already knows `Y(0) = Y − τT`), not be hand-typed. Optional companion figure: the two baselines as points with the selection-bias gap annotated.

- **Status:** open

---

## 2026-07-14 — Eq (1.11), §1.3: LATE is defined via "compliers," but compliers are never defined in Chapter 1

- **Location:** `book/chapters/foundations.tex`, §1.3 Identification, the estimand catalogue eqs (1.8)–(1.11). Eq (1.11) (`eq:fnd:late`): `LATE = E[Y(1) − Y(0) | compliers]`, glossed only as *"the effect on the units an instrument moves."*

- **What / why:** "compliers" (and, implicitly, "instrument" / "encouragement") appear in the conditioning set of eq (1.11) with **no definition**; the one-line gloss doesn't say who compliers are. The actual definition — the principal-strata classification (always-takers / never-takers / compliers / defiers), the monotonicity / no-defiers assumption, and "the instrument defines the complier population" — only arrives in **Ch. 13 (IV)**, `book/chapters/iv.tex` (strata table ~line 154; `eq:iv:late`; "The LATE theorem, in two lines"). A Chapter-1 reader meets LATE with an undefined term. Same forward-reference class.

- **For the record — what a complier is:** in an encouragement design, an instrument `Z` (often randomized) nudges treatment-taking `X`. Classify units by `X(1)` vs `X(0)`: **always-takers** take treatment regardless of `Z`; **never-takers** never do; **compliers** take it when encouraged and not otherwise (the ones `Z` moves); **defiers** do the opposite (assumed away by monotonicity). LATE = the average effect on compliers only. IV speaks only for them because `Z` doesn't change always-/never-takers' status; the first stage `E[X|Z=1] − E[X|Z=0]` *is* the complier share, and it's instrument-specific (a different instrument defines a different complier group).

- **Proposed fix (updated — preferred):** LATE/compliers belongs **where instruments are introduced (Ch. 13, IV)**, not the front primer. Unlike ATE/ATT/CATE — which are self-contained in the §1.3 catalogue — LATE needs the whole instrument + principal-strata apparatus, so it can't be cleanly defined before instruments exist. Options: (a) **drop LATE from the §1.3 estimand catalogue** and introduce it in Ch. 13 alongside instruments and the strata table; or (b) keep a **one-line placeholder** in §1.3 with a light gloss (*"compliers — customers who act on the encouragement but would not otherwise; defined with instruments in Ch. 13"*) plus an explicit forward-reference. Either way the *full* definition (four strata, monotonicity, "the instrument defines the compliers") lives with instruments in Ch. 13. Minimum acceptable: don't leave "compliers" bare in eq (1.11).

- **Status:** open

---

## 2026-07-14 — Fig. 1.1: the plotted quantity ("naive difference of means") isn't defined where the figure appears

- **Location:** `book/chapters/foundations.tex`, §1.2, fig. 1.1 (`fig:fnd:confounding`; float `build/floats/nb00_confounding.tex`; plotting code in `notebooks/00_foundations.ipynb`).

- **What is actually plotted (for the record):** two bars of the **naive difference of means**, `τ̂_naive = Ȳ_treated − Ȳ_control = Ê[Y|T=1] − Ê[Y|T=0]`, computed separately in the randomized world (€4.8) and the observational world (€11.4). Error bars are **±1 standard error** of that difference (Welch-type SE from the notebook's `naive_se`). Two horizontal reference lines: dashed black at the **true ATE (€5.6)**, dotted blue at the **€8 contact cost**. y-axis label: *"naive difference of means (€, bars ±1 SE)."* It is rung 1 of the estimator ladder applied to the two worlds.

- **Definitions issue (yes — same class):**
  - The **naive difference of means / naive estimator** `τ̂_naive` is not defined in the main text until §1.3 "The naive difference, decomposed" (eq. decomp), yet fig. 1.1 and the €4.8/€11.4 numbers appear in §1.2. The y-axis label itself uses an undefined term.
  - The **true ATE €5.6** reference line inherits the "average effect used before defined" gap (see entry below).
  - The **±1 SE** error bars invoke a standard error before that notion is introduced.

- **Aside / cross-ref:** the **€8 contact-cost line numerically coincides with the €8 noise SD** in eq (1.1), `N(0, 8²)`. A reader can conflate the two 8's — a further reason to name and justify constants (see the hardcoded-constants entry).

- **Proposed fix:** give a one-line inline definition of the naive difference of means (`τ̂_naive = Ê[Y|T=1] − Ê[Y|T=0]`) at or before fig. 1.1, or move the figure to after §1.3's definition; make sure the truth line and SE bars rest on notions already introduced at that point; and disambiguate the two 8's.

- **Status:** open

---

## 2026-07-14 — §1.2: "planted average effect €5.6" used before the effect is defined, and its computation is unexplained

- **Location:** `book/chapters/foundations.tex`, §1.2, the sentence just below eq (1.3): *"The planted average effect is €5.6 in both worlds. Nothing about the effect changes between eq. (1.2) and eq. (1.3); only the mechanism that assigns it changes, and that alone is enough to move the naive estimate from €4.8 to €11.4 (fig. 1.1)."*

- **What / why:**
  - The main text introduces eq (1.1) with only *"a planted per-customer effect τ(x)"* — the **functional form of τ(x) is never shown in the main text** (it lives in the DGP appendix, eq (up_tau): the "persuadables minus sleeping dogs" bump). So the reader has no way to see what is being averaged.
  - The notion of a causal **effect** / **average effect** (potential outcomes, ATE = E[Y(1) − Y(0)]) is not defined until §1.3 "Identification." The sentence uses "average effect" roughly a page *before* the machinery that defines it.
  - **How €5.6 is computed is never stated.** It is the empirical mean of the planted per-customer effect τ(x) over the simulated customer file — i.e. `mean(τ(xᵢ))` across the nb00 customers. It is identical in both worlds because τ(x) is a property of the customers, not of the assignment rule; only `T`'s distribution changes between (1.2) and (1.3). None of this is on the page.

- **Proposed fix (pick one):**
  - Add a short clause defining the average effect as the population mean of the per-customer effect, `τ̄ = E[τ(x)]`, computed by averaging the planted τ(x) over the customer file — and note it is *known* precisely because τ(x) was planted. Forward-reference §1.3 for the formal potential-outcomes definition and the DGP appendix eq (up_tau) for the exact τ(x).
  - Or reorder so a minimal definition of "effect" / "average effect" precedes this sentence.
  - Either way, make explicit *why* the number is invariant across (1.2)–(1.3) (τ(x) unchanged; only assignment changes) rather than asserting it.

- **Status:** open

---

## 2026-07-14 — Book-wide: no bare hardcoded constants inside equations

- **Location:** Book-wide. First concrete example: the noise SD `ε ~ N(0, 8²)` in eq (1.1), §1.2, `book/chapters/foundations.tex`. Same pattern elsewhere in §1.2 alone: eqs (1.4)–(1.5) one-confounder world (`5·L`, `6·T`, `3·G`, `N(0, 4²)`), collider eq (1.6) (`N(0, 5²)`), and the assignment coefficients in eq (1.3) (`1.8`, `1.2`, `0.15`, `0.4`, `150`, `5`) and eq (1.4) (`0.8`). Recurs in every chapter's DGP equations.

- **What / why:** Bare literals baked into equations (the `8` in the noise SD, the logistic coefficients, etc.) look ugly typeset in an equation and, more importantly, are **unjustified** — why 8 and not 5 or 12? A reader can't tell whether the value matters or was arbitrary.

- **Proposed fix:**
  - Replace bare numbers with named symbols defined once (e.g. `σ_ε`, `β_L`, `β_T`, …) so the equations read cleanly and the numeric values live in one place (a parameter table or the DGP appendix).
  - Justify each chosen value in text — tie it to something interpretable: a signal-to-noise ratio, a plausible euro scale, an implied R², or a target gap (e.g. "noise SD set so the naive-vs-true gap is ≈ X"). Not just "8 because."
  - Apply the convention everywhere numbers are hardcoded into DGP / model equations across the book.

- **Status:** open

---

## 2026-07-14 — Book-wide: add a visual wherever a function/equation OR a quantitative claim is introduced

- **Location:** Book-wide. First concrete example: §1.2 eqs (1.1)–(1.3) in `book/chapters/foundations.tex` — the uplift model (1.1) `Y = μ₀(x) + τ(x)T + ε`, the randomized assignment (1.2), and the observational/logistic assignment (1.3).

- **What / why (functions):** Equations are abstract; a small figure beside each gives an immediate visual sense of what the function actually does, which is the whole pedagogical point for an MBA audience. E.g. for eq (1.3), plot the send probability `σ(·)` as a function of engagement/recency/frequency; for (1.1), show the spend distribution and the planted effect; for (1.2)–(1.3), show the two assignment mechanisms side by side so the confounding is visible.

- **What / why (quantitative claims — not just functions):** whenever prose states a **share / percentage / comparison**, it should have a visual realization, ideally with the stated number *readable off the plot* rather than only asserted in the caption. Concrete case raised by Francesco: the sentence below eq (1.11) — *"29 % of customers individually clear the cost bar, while 30 % are actively harmed by the email"* (`\nbZeroShareAboveCost`, `\nbZeroShareNegative`). The base figure **already exists** (`fig:fnd:tau` / `nb00_tau_spread`: histogram of τ(x) with ATE, €8 cost, and zero lines) **but only asserts the two numbers in its caption — nothing on the plot marks them.** Enhance it: shade and label the region right of the cost line (29 %, profitable) and the region left of zero (30 %, harmed) so both numbers are readable straight off the histogram.

- **Proposed fix:** Adopt a standing convention — every time a functional form **or a quantitative claim** is introduced, accompany it with a compact visual: a marginal curve / distribution / mechanism sketch for a function; a shaded-region histogram, a bar, or a dot-with-interval for a share / percentage / comparison. Prefer **shade + annotate** so the stated figure is legible on the plot itself. Roll out across all chapters, not just Chapter 1.

- **Status:** open

---

## 2026-07-14 — Ch. 1 §1.2 vs §1.8: "cannot be graded on real data" is stated as a blanket claim

- **Location:** `book/chapters/foundations.tex`
  - §1.2 "The data-generating model" (opening, ~line 62): *"A causal method cannot be graded on real data, because on real data the counterfactual is missing."* Framed with no exception.
  - §1.2 (~line 63–64): methods are *"graded against worlds whose answers are known by construction, and only then **trusted** on a world whose answer is not."*
  - §1.8 "On real data: LaLonde" (~line 610–665): calls LaLonde *"the exam a causal method has to sit"* and reports how close each estimator lands against the randomized benchmark — i.e. it **grades** on real data.

- **What / why it needs a fix:** The blanket §1.2 claim is only exceptionless at the level of *verifying an individual estimate against a missing counterfactual*. As written it collapses two things a sharp MBA student will separate:
  1. **Grading against a randomized benchmark (within-study comparison).** LaLonde (§1.8) and the Ch. 9 geo experiment both do exactly this — the *average* effect is known on real data via randomization, so the observational estimators can be graded. This is real-data grading of the ATE; the per-unit counterfactual is still missing.
  2. **Falsification / one-sided grading.** Negative controls, placebo-in-time/space, synthetic-control pre-period fit, IV overidentification tests — these can *fail* a method on real data without certifying it. Directly relevant to the synthetic-control and IV lectures.
  - There is also a wording slippage: §1.2 files LaLonde under *"trusted"* (world whose answer is *not* known), but §1.8 says LaLonde's answer **is** known (from the randomized arm) and treats it as a graded exam.

- **Proposed fix:**
  - Narrow the §1.2 claim to something like *"cannot be graded on the real data you actually have for the decision"* or *"on real data without a randomized benchmark."*
  - Introduce the three-tier framing explicitly: (1) simulated worlds — answer known *by construction*; (2) within-study benchmarks (LaLonde, geo) — answer known *by randomization*, still a grade; (3) genuine deployment — no benchmark, only falsification + assumptions.
  - Reconcile the "trusted" vs "exam/graded" language between §1.2 and §1.8 so the two passages don't appear to contradict.
  - Optionally add a one-line forward reference in §1.2 to the falsification tests used later (placebos, overID) as the second real-data grading route.

- **Status:** open

---

## 2026-07-17 — Ch. 9: the back-door framing overclaims; the primary problem is n=1 factor mismatch

- **Location:** `book/chapters/geo_lift.tex`, subsection "What the estimator does to the confounding, on a graph" (~line 353) and `fig:sc:dags` (left panel).
- **What / why:** The passage asserts that the latent factors "drive both the decision to advertise in a market like this one *and* that market's sales" — i.e. an \(f_t \to X\) assignment arrow. But the chapter's own DGP has **no assignment mechanism**: the treated market is fixed by construction, so within the simulated world that arrow does not exist and the back-door story is asserted, not shown. The unconditional identification problem in this category of case is the **n = 1 factor mismatch**: for a fixed treated unit, any naive comparison keeps \((\alpha_1-\bar\alpha) + (\gamma_1-\bar\gamma)^{\top}\bar f_{\text{post}}\), a structural term with nothing to average against, *however* the market was chosen (even by coin flip; randomization deletes \(f_t \to X\) but leaves \(f_t \to Y\), and with one treated unit the surviving arrow does not wash out). Selection-on-outlook (Abadie's endogenous-adoption motivation) is a *plausible aggravation* that upgrades the fork to a genuine back-door — a conditional aside, not the frame.
- **Proposed fix:** Reorder the argument: (1) mismatch-term decomposition first (it also motivates the DiD failure and the loading-matching cure directly); (2) back-door as the conditional case "if the market was chosen on its character", noting the same matching closes it; (3) optional: the two-arrow decomposition under randomization (cuts \(f_t \to X\), leaves \(f_t \to Y\)) as the bridge to the real-data act's "randomization buys unbiasedness, the model buys precision". The slide deck (2026-07-17 pass, slides 8-9 and the real-experiment slide) now carries exactly this structure and can serve as the template.
- **Status:** open

---

## 2026-07-17 — Ch. 9: pilot-market selection and the rollout extrapolation (transportability gap)

- **Location:** `book/chapters/geo_lift.tex` — the estimand discussion (§ opening / potential outcomes) and/or the takeaways; surfaced by a user question on the slide deck ("if the metro was picked because it looked promising, isn't the test biased anyway?").
- **What / why:** The chapter identifies the effect *in the treated metro* (that is the estimand) and then lets the board read it as evidence for a *national rollout*, but never states the transport assumption or the selection direction. Two separable facts an MBA will conflate: (1) choosing the pilot on pre-launch character does **not** bias the within-metro estimate (SC conditions on exactly those characteristics; only selection on *future* market-specific shocks would poison it, which placebo-in-time hunts); (2) it **does** bias the rollout extrapolation upward: a pilot picked for promise is an optimistic draw, so the pilot effect is a ceiling for the other markets. The asymmetry is decision-relevant and currently implicit: a pilot NO-GO is reinforced by the selection; a pilot GO must be discounted before scaling. (This chapter's NO-GO verdict is therefore *conservative* under the objection — worth one paragraph saying so.)
- **Proposed fix:** One short paragraph (estimand section or takeaways): name the estimand as the treated-metro effect, state the homogeneity/transport assumption a rollout adds, give the direction of the selection bias, and the NO-GO-reinforced / GO-discounted reading. The slide deck (2026-07-17 pass) already carries this as a callout on the boardroom slide; the chapter should carry the canonical version.
- **Status:** open

---

<!-- New entries above this line. Template:

## YYYY-MM-DD — <short title>

- **Location:** <file / section / line>
- **What / why:** <description>
- **Proposed fix:** <what to change>
- **Status:** open

-->

## 2026-07-19 — ✅ CACHE: `_code_fingerprint` was nondeterministic across interpreters — FIXED

- **Location:** `src/cmp/cache.py` (`_code_fingerprint`).
- **What.** The walk iterated an **unsorted `set` of `co_names`**; under per-process hash
  randomization the source chunks concatenated in a different order in every fresh interpreter, so
  the same function produced a different fingerprint per kernel/script and every new process
  silently re-fit already-cached work. Exposed when nb11's new sweep cell re-sampled 220 fits a
  driver had just cached. **Fixed** by sorting the names; regression guard
  `tests/test_cache.py::test_code_fingerprint_is_stable_across_interpreters` (subprocesses with
  different `PYTHONHASHSEED`s must agree).
- **Consequence:** entries written before the fix under random-order fingerprints are orphaned
  (they were unreachable across sessions anyway). nb11 was re-warmed the same day; other notebooks
  refit once on their next FULL run.
