# Revision plan — Ch1, Ch3, Ch9, Ch13 as MBA lectures

**Date:** 2026-07-15
**Scope:** Chapter 1 (foundations / nb00), Chapter 3 (uplift / nb01), Chapter 9 (geo lift / synthetic
control / nb07 + 07b), Chapter 13 (endogenous exposure / IV / nb11 + 11b). Make it uniform across the
whole book afterwards.
**Source:** two independent multi-agent reviews (3-chapter review, 41 agents; Ch1 + benchmark review,
17 agents), every finding adversarially re-checked, load-bearing numbers re-run in code.
**Companion file:** `book/LIST_TO_FIX.md` is the running backlog. This file is the actionable plan.

---

## STATUS — 2026-07-15 (end of session)

**DONE (prose pass, all four chapters compile as offprints):**
- Both criticals: Ch9 epigraph (decision-first, matches §9.8) + takeaway 4; Ch13 likelihood-vs-prior
  contradiction purged across §13.6/§13.7/§13.8.
- All "backward"/erratum + scorekeeping voice removed book-wide (verified: grep is clean).
- Forward framing rebuilds: Ch9 §9.6–9.8 ("Honest uncertainty on the N-week total", decision-question
  subsections), Ch3 §3.7, Ch13 §13.8/§13.11 titles.
- Per-chapter appendices created: 1.A (Formal machinery), 3.A (BART tolerances), 9.A (Formal
  machinery), 13.A (the three-suspects forensic).
- "Setup and notation" renames (Ch1, Ch9). Surgical correctness: eq:iv:ssr cross-term, IV symbol
  alignment (γ=instrument, λ=propensity conf., κ=outcome conf.), bare-12→κ, Ch9 convex-hull on the
  full feature vector, ACF-as-cross-panel-statistic disclosure, §9.9 re-pricing mechanism (narrowing),
  §9.7 like-with-like sd. Ch1 R1 density pass, §1.2/§1.5 dedup, €8-cost SEND/HOLD flip at Table 1.4.
- Built offprints: ch01 39pp · ch03 31pp · ch09 37pp · ch13 39pp (all exit 0).

**DEFERRED to next session — 3 items, each needs a slow notebook re-run (TODO(reexec) markers in place):**
1. `iv.tex:1509` — inject the diffuse-SD collapse number (one MCMC refit, nb11, legacy env).
2. `uplift.tex:142 & :198` — emit `tab:up:params` and `tab:up:types` from nb01.
3. `geo_lift.tex:735` — emit a macro for the cross-panel mean AR(1) posterior sd (~94).
4. Ch3 held-out re-scoring (nb01; ~20–40 min BCF/BART) — OR add an in-sample disclosure sentence.
5. Ch9 35% margin recompute (nb07) — parameter in the notebook, 35% fixed in the chapter; NOTE it
   shifts §9.9 from "marginal miss" to a clearer no-go (a stronger margin-trap lesson) — review.

**NOT yet done:** full-book build (deferred until all chapters final); a human read-through of the
rebuilt prose; the citation-precision fixes (LaLonde→Dehejia-Wahba / PSID; Criteo v2.1 card) if the
Ch1 agent's pass did not fully land them (verify).

---

## 0. The target state — the five rules (from Francesco, 2026-07-15)

Every chapter must satisfy all five:

- **R1 — Plain, direct prose; self-contained sections.** Short sentences. No clause-stacking. State
  every implication (never make the reader infer "so what"). Each section: **define → show how to use
  it (example) → apply it.**
- **R2 — A per-chapter appendix (1.A, 3.A, 9.A, 13.A)** holds the formal machinery: definitions,
  assumptions, test statistics/formulas, derivations, deep diagnostics — each taught with a worked
  example. The main text stays decision-focused and points to the appendix.
- **R3 — "Setup and notation"** is the define-then-use opener (not "The words this/the chapter
  assumes"). Full definitions live in the appendix.
- **R4 — Classical → Bayesian → discrepancy, never adversarial.** Do the classical analysis to its
  result + decision; then a "A Bayesian view" section to its result + decision; then a short, calm
  note on where they agree/differ and why. No scorekeeping ("Bayes buys nothing", "as first written",
  "the chapter where Bayes buys the least"). No erratum/"backward" voice anywhere.
- **R5 — Pedagogy + MBA business value drive everything;** the through-line is always the euro decision.

---

## 1. What is VERIFIED CORRECT — do not touch

Independently re-run in code, so the revision must preserve these:

- **IV backbone (Ch13):** Wald = 2SLS to 1e-13; F = 156; complier share 21.0%; probit repair
  (+1.5/80% → +0.88/90%) all reproduce from the executed artifacts.
- **IV bias attribution (Ch13) is the right answer:** the mis-scaled error-SD prior is the sole driver
  (joint-Gaussian MLE = 2SLS → the likelihood adds zero bias to β; the ρ prior is inert). The
  *conclusion* is sound — only the *telling* is broken (see §13 below).
- **Synthetic control (Ch9):** the SLSQP fix is real (24/24 placebo fits beat the equal-weight
  centroid — no stuck fits); the gap-error autocorrelation is ≈0.3 and flat (not the old 0.93); the
  shard is FULL (24 panels, 6000 draws).
- **Uplift (Ch3):** identification correct; every classical SE is the right one (Welch, HC1,
  cross-fitted influence function, paired bootstrap); every DGP-derived number ties to the cent.
- **All prose numbers are macro-injected**; no number is mischaracterized in words.

### 1b. Public datasets agree with the literature (all COMPATIBLE)

| Dataset | Ours | Published | Verdict |
|---|---|---|---|
| **Google geo** (nb07b) | iROAS 2.94 / $147k | TBR iROAS 2.86 / $143k | Compatible — overlaps tightly |
| **LaLonde/NSW** (nb00) | benchmark ~$1,800; adjusted +$1,548; naive −$635 | Dehejia–Wahba ATT $1,794, CI [551, 3038] | Compatible — reproduced to the dollar |
| **Criteo** (nb11b) | 13,979,592 rows; 85/15; 4.7%/0.29% | v2.1 "unbiased" card, verbatim | Compatible — exact match |

**Three citation-precision fixes** these surfaced (small, but worth making):
1. **LaLonde (Ch1):** attribute the $1,794/$1,800 benchmark to **Dehejia–Wahba**, not LaLonde 1986
   (whose own full-sample headline was ~$886). Name the control group **PSID** (currently "survey
   controls") — it strengthens the overlap argument.
2. **Criteo (Ch13/nb11b):** our numbers match the **v2.1 "unbiased" re-release card**, not the 2018
   paper's original CRITEO-UPLIFT1 table (25.3M rows, 11 features). Cite the card/version, and note
   that subsampling to a balanced arm shifts the base rates.
3. **Google geo (Ch9/nb07b):** the TBR figure 2.86 comes from a **public replication of Google's own
   reference code** on the canonical data, not a number Google printed (KWV 2017's worked example is a
   different, anonymized experiment). Soften "the published TBR iROAS" to reflect that provenance.

---

## 2. Cross-cutting issues (apply to all four chapters)

- **Remove all "backward" / erratum voice.** No "as first written", "an earlier draft… went wrong",
  "the temptation is to say X… it does not", "the prior is not the culprit", "the chapter used to
  give". Present each technique forward, as it should be understood.
- **Demote the classical-vs-Bayesian duel.** It is supporting rigor (honest uncertainty for the
  decision, `P(effect > cost)`), never a section's headline. Reframe every "what did Bayes buy" section
  around the decision.
- **Business realism — the margin.** Two chapters treat incremental revenue as profit (100% gross
  margin): Ch9 §9.9 and Ch3's euro decision. Introduce a stated gross margin (Ch9 §9.11 already does
  this correctly). **Open decision: pick one canonical margin (e.g. 35%) or make it a parameter
  students set.**
- **Per-chapter appendix + "Setup and notation"** everywhere (R2, R3).
- **Prose density pass** (R1) on the worst offenders, chapter by chapter.

---

## 3. Chapter 13 — IV (the most correctness-sensitive)

**Verdict:** the decision spine (defensible bid cap) is already good; the Bayesian middle
(§13.6–§13.8, §13.11) is internally contradictory and reads as a methods-paper post-mortem.

### Correctness (must fix)
- **[CRITICAL] Internal contradiction on the bias cause.** §13.6 still says *"the culprit is not the
  prior. It is the likelihood."* (iv.tex:641–642) and *"The prior is not where this model's problem
  lives. The likelihood is."* (:668–670); §13.8 repeats it (:917–919, "the defeat was the
  likelihood's"); the likelihoods-table caption says *"The likelihood did all of it."* §13.7 then
  proves the opposite (the SD prior). **Purge every likelihood-culprit claim. State one forward
  attribution everywhere:** the linear-probability likelihood is innocent for β (its MLE is 2SLS
  exactly); the ρ prior is inert; the mis-scaled error-SD prior is the driver.
- **[MAJOR] The decisive experiment is never actually run.** The "diffuse the SD prior → β collapses to
  16.5" claim (iv.tex:860–867) is a **hardcoded string**; nb11 cell 24 only fits the flat-ρ variant.
  Add a real diffuse-SD refit cell (wide error-SD prior, e.g. HalfNormal(25), everything else fixed),
  emit a macro, and inject the true number (≈16.8, removing ~80% of the excess over 2SLS). Legacy env,
  `CMP_REFIT=1`.
- **[MAJOR] eq:iv:ssr is mathematically wrong** (iv.tex:504–513): the SSR decomposition omits the cross
  term `2b·Σ xᵢeᵢ` and is false on the chapter's own seed-37 data. Correct the identity and explain the
  "too wide" direction by the real mechanism (positive endogeneity → Cov(X,u) > 0).
- **[MINOR] likelihoods-table caption** claims to "isolate the likelihood" but the two rows differ in
  likelihood **and** priors — regenerate the caption to say so.
- **[MINOR] params-table symbol collision** (α_z in the body vs γ in the caption) — regenerate with
  the body's symbols.
- **[MINOR] bare constant "12"** inside eq:iv:endog — name it γ.
- **[MINOR] bias 0.88 → 0.71 "it shrinks"** is not statistically distinguishable (SE ~0.5 on 5 panels)
  — state that honestly.
- **[BUILD] `macros.tex` may be stale vs `nb11.json`** (the shard already carries the corrected
  `gauss_bias_source`/`gauss_flat_*`). Regenerate before `make book`, or it may not compile.

### Framing / structure (R2, R4)
- Move the "three-suspects" forensic (likelihood vs ρ-prior vs SD-prior, the MLE=2SLS algebra, the
  flat-ρ and diffuse-SD refits) into **Appendix 13.A**. Keep one forward paragraph in the body: "the
  off-the-shelf default ships biased and under-covering here; a binary-aware model fixes it; the true
  cause is a silent, mis-scaled default prior, which is why we always check coverage and price it."
- Delete erratum voice: §13.7 box "as an earlier draft of this section did, blaming the likelihood"
  (:879–880); §13.11 "not the one this chapter used to give" (:1304–1305).
- Recast §13.6 intro ("the detour… is the chapter's thesis", :602–603) and §13.8/§13.11 titles ("Bayes
  does not win", "where Bayes buys the least") so the decision is the headline.
- §13.2 monotonicity "the tempting explanation… is wrong" (:174–176): recast as a direct positive
  claim.
- §13.5 → §13.6: adopt the R4 arc — classical (2SLS/Wald → cap) → "A Bayesian view" (joint model → cap)
  → short discrepancy note.

---

## 4. Chapter 9 — geo lift / synthetic control (the biggest framing rebuild)

**Verdict:** technically excellent and business-rich at the bookends (§9.1, §9.9, §9.11); the middle
third (§9.6–§9.8) is organized as an iid-vs-AR(1) / Bayes-vs-classical duel and carries erratum voice.
This is the chapter the framing rules were written for.

### Correctness (must fix)
- **[CRITICAL] Epigraph contradicts the body.** It says the AR(1) repair works *"without moving the
  estimate at all"* and the Bayesian arm "returns the same number", but the iid mean €229k → AR(1) €262k
  is a ~1.2-sd move, and §9.8 correctly argues the opposite. Rewrite the epigraph and takeaway 5 to
  §9.8's (correct) account: the AR(1) re-weighting nudges the estimate from €229k onto the classical
  €260k **and** widens the band.
- **[MAJOR] `fig:sc:gap` is mislabeled:** §9.6 discusses it as the iid recovery (86%) but it plots the
  AR(1) fit. Either plot the iid recovery in §9.6, or relabel the figure as the shipped AR(1) fit.
- **[MAJOR] §9.7 "slightly narrow" is apples-to-oranges** (:706–714): it compares one display panel's
  AR(1) sd (72) to the cross-panel referee (87). Compare like with like — cross-panel mean AR(1) sd (94)
  vs 87 → if anything slightly conservative; attribute the small sub-nominal coverage to the +28 bias.
- **[MAJOR] §9.9 "re-pricing" mechanism is stated backwards** (:937–941): replacing the AR(1) posterior
  (sd 72) with the design sd (50) is a **narrowing**, not a widening; the small rise in P is a
  de-skewing artifact. Correct the explanation.
- **[MAJOR] 100% gross margin** in the §9.9 euro decision (and the VOI / test-sizing that follow):
  compare `margin·τ` to cost, report break-even iROAS = 1/margin and a margin sweep, exactly as §9.11
  does.
- **[MAJOR] 24-panel coverage carries no Monte-Carlo error** (±6–10pp): state the binomial SE on each
  coverage number; lead with the robust claim (iid 50% is a broken instrument) and present 83/88/90 as
  "indistinguishable at 24 panels."
- **[MINOR] The "ACF" is an uncentered cross-panel statistic**, not a within-series ACF — disclose that
  in the caption (it is the between-panel offset-variance ratio).
- **[MINOR] Assumption 1 (convex hull)** is stated on the three loadings only; the DGP has a separate
  additive baseline `c_i ~ U(80,140)`. State it on the full (baseline, loadings) vector.
- **[MINOR] AR(1)-vs-flatness tension:** §9.7 says the fingerprint is flatness/non-decay and names AR(1)
  as the wrong class ("it dies out"), then uses AR(1). Reconcile — frame the residual as a local-level /
  random-per-panel intercept (the source of the non-decaying offset), or state plainly why an AR(1) with
  ρ≈0.5 is the pragmatic stand-in.
- **[MINOR] Notebook staleness:** nb07 cell 31 says "24 of 29 donors" (actual 29/29) and cell 33 builds
  a two-p-value reconciliation (actual: both 0.033, no tension). Rewrite to match the executed run.

### Framing / structure (R2, R3, R4)
- **Rewrite the epigraph decision-first** (mirror Ch3/Ch13): €300k TV test in one of 30 markets → SC
  prices the 20-week lift ≈ €260k vs €300k → P(pays back)=0.21, NO-GO, worth €192k of headroom → one
  "second finding" clause about pricing the uncertainty of a summed, autocorrelated total.
- **Rename §9.2 "The words this chapter assumes" → "Setup and notation."**
- **Delete the §9.2 "blows up" box** framing; present the simplex forward: it buys a guarantee about the
  object (a defensible blend of real markets carried forward), not a better fit on any panel.
- **Reframe §9.6–§9.8 forward under a decision head** ("How much do we trust the €260k the rollout turns
  on?"). Present iid → AR(1) and the design-based cross-check as supporting honest-uncertainty steps.
  Drop "in this chapter it is wrong… §9.7 convicts it" (§9.6) and the prosecution register.
- **Move to Appendix 9.A:** the three-referee subtlety (which sampling distribution grades which
  posterior), the GLS-reweighting/AR(1) stationary-initial-condition math, the full ACF derivation.
- Retitle §9.11's "the chapter's finding, confirmed" subsection to a decision-anchored head.

---

## 5. Chapter 3 — uplift (strong; localized fixes)

**Verdict:** the first six sections are a model forward, decision-first lecture. The problems are
concentrated in §3.7 (the largest section) and in one real correctness gap.

### Correctness (must fix)
- **[MAJOR] Headline metrics are in-sample (optimistic).** PEHE/AUUC/coverage/policy are scored on the
  1,600 customers the models were fit to; the library's `X_score=` out-of-sample path is never wired.
  The optimism (~0.8 PEHE) is **larger** than the head-to-head gaps the chapter adjudicates (0.29 PEHE,
  0.031 AUUC), so the fine "BCF beats GBM-T" verdicts could be artifacts. **It does not flip the go/no-go
  decision.** Fix: wire a held-out split (or K-fold cross-fit) via `X_score=` / `propensity_score=`,
  re-run all grades, the ladder, and the euro table out-of-sample. Core env. If compute forbids a live
  re-run, at minimum disclose in-sample and widen the tolerances by the measured optimism.

### Business (must fix)
- **[MAJOR] 100% margin:** τ is spend uplift and "profit" is Σ(τ−c). State that τ and Y are in
  contribution-margin euros, or add a gross-margin multiplier `m` so realised profit = Σ(m·τᵢ − c).

### Framing / structure (R2, R4)
- **[MAJOR] Reframe §3.7 around the decision.** It is currently a Bayes-vs-classical scorecard ("what did
  BCF's machinery buy / cost", "the ledger"). Retitle around the decision (which model to trust for
  `P(τᵢ > c)`; is BCF's machinery earning its keep with confounders observed?). Move the euro payoff
  (tab:up:rules) into §3.8. Move the paired-bootstrap + PGBART-wobble tolerance construction to
  **Appendix 3.A**.
- Delete erratum voice in §3.7: "an earlier draft of this chapter went wrong" (:688), "the ledger"
  scorecard (:887–899), "the double standard, named so it is not repeated."
- Trim the epigraph's methodology-heavy last third to one decision-relevant line.

### Smaller (minor / nit — batch these)
- r-hat 1.04 on the headline BCF fit is waved through; either raise draws to ≤1.02 or add coverage to
  the multi-seed sweep.
- Add a **worked micro-example** (Principle 3): 5–6 customers across the four types with planted τᵢ,
  τᵢ−c, and the mail/don't-mail decision, with an on-page identity.
- Add a **params table** for the DGM constants (Principle 4).
- Reconcile the three near-identical peak figures (rule value €5,120 vs sweep €5,143 vs curve €5,139).
- The rules-caption identity does not close on the page (1600·(8−5.95) = −3,280 vs stated −3,277) —
  show ATE to enough precision.
- Consider surfacing a real-data readout (Hillstrom) into the body, not a footnote — but the current
  cheap-email regime makes treat-all optimal, so attach a plausible cost first.

---

## 6. Chapter 1 — foundations (the reference; now also revised)

**Verdict:** "the intellectually strongest chapter in the book; its euro through-line is exemplary and
should be the template every other chapter copies." But under the five rules it reads as a dense
monograph, not a forward MBA lecture. Confirmed-major items:

### Structure (must fix)
- **[MAJOR, R2] Create Appendix 1.A ("Formal machinery").** No per-chapter appendix exists today. Move
  there, each WITH the worked example already in nb00: (1) potential-outcomes formalism + consistency +
  ATE/ATT/CATE; (2) the selection-bias decomposition, derived; (3) d-separation and fork/chain/collider;
  (4) the g-formula; (5) the estimator-ladder derivations (naive/regression/IPW/AIPW) and their SEs;
  (6) the diagnostics (SMD, overlap, PPC). Main text keeps the plain-language statement + the euro
  result and points to 1.A.
- **[MAJOR, R3] Rename §1.2 "The words the cookbook assumes" → "Setup and notation."** Compress it to
  the running example, the symbol table (unit/T/Y/x, the four estimands, e(x), the naive difference),
  and one-line glosses; push formal definitions to 1.A.
- **[MAJOR, R5] Restore the euro through-line across the technical core.** It goes dormant from §1.3
  (DGM) through §1.5 (DAGs). Give the one-confounder / ladder world an explicit contact cost (e.g. €8,
  where naive €9.26 says SEND and true €6 says HOLD) and state the flip at Table 1.4.
- **[Fix duplication]** §1.2 and §1.5 both teach fork/chain/collider and the g-formula. Consolidate:
  definitions to 1.A, §1.5 applies them.

### Correctness
- **[Stale number] nb00 cell 36 markdown says "naive €11.4 against an €8 cost"** but the executed run
  computes €9.7. Replace €11/€11.4 with the injected €9.7 (still > €8, so the decision framing holds).
- **[Citation]** attribute the LaLonde benchmark to Dehejia–Wahba; name the PSID control group (see §1b).

### Prose (R1)
- Targeted density pass on the worst offenders (the opener quote, the contribution-margin sentence):
  split multi-clause em-dash sentences; lead with the decision.

---

## 7. Execution plan and sequencing

**Two kinds of work:**

- **Prose-only** (no re-execution): all framing/erratum removal, the R2 appendix reorganisation, the
  R3 renames, the R1 density passes, the correctness *wording* fixes (Ch9 §9.7/§9.9 explanations,
  Ch13 contradiction purge, citation fixes, eq:iv:ssr correction). This is the bulk of the work and can
  land first.
- **Notebook + re-execution** (moves numbers → then regenerate macros + rebuild):
  1. **Ch13/nb11** — add the diffuse-SD refit cell; emit the macro. Legacy env, `CMP_REFIT=1`.
  2. **Ch3/nb01** — wire `X_score=` / holdout; re-run grades, ladder, euro table. Core env.
  3. **Ch9/nb07** — put a margin into the euro decision (+ VOI/test-sizing); fix cell 31/33 staleness.
     Core env.
  4. **Ch1/nb00** — fix the €11.4→€9.7 prose; emit any new Appendix-1.A figures if needed. Core env,
     `CMP_REAL=1` for the LaLonde section.
  5. **Regenerate `macros.tex` (fixes the Ch13 build-integrity flag) and rebuild the book.**

**Suggested order:** Ch13 contradiction + Ch9 epigraph (the two criticals) → the notebook/re-exec
changes → the framing rebuilds (Ch9 middle, Ch3 §3.7, Ch13 middle) → the appendix reorganisations →
the R1/R3 passes → Ch1 last (it is the reference; changing it sets the template) → full rebuild.

---

## 8. Open decisions for Francesco

1. **Margin:** one canonical gross-margin value across chapters (e.g. 35%, as §9.11 uses), or a
   parameter the student sets? (Recommend: one canonical value, stated once, reused.)
2. **Ch3 out-of-sample:** wire a true held-out re-run (moves the headline slightly, needs re-exec) or
   only disclose "in-sample" and widen the tolerances (cheaper, no re-exec)? (Recommend: wire it.)
3. **Appendix placement:** a per-chapter appendix printed at the end of each chapter (so offprints stay
   standalone), confirmed? (Recommend: yes — matches the standalone-offprint requirement.)
4. **Ch1 depth:** how hard to simplify the reference chapter's prose — a light density pass, or a full
   restructure to the appendix model? (Recommend: R2/R3 structural moves + a light R1 pass; keep its
   content.)
5. **Scope of this pass:** these four chapters only now, the other nine later — confirmed.
