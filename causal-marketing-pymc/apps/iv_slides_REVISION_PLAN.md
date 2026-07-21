# IV slide deck (`apps/iv_slides.html`) — PEDAGOGICAL REBUILD (v2, 2026-07-18)

Chapter 13 (instrumental variables) as a geo-style interactive HTML slide deck. **Rebuilt from
scratch on 2026-07-18** after Francesco rejected the v1 structure ("difficult to imagine something
worse"): the v1 deck was a business drama that used IV concepts as plot devices; a first-time
student could not learn IV from it. The v2 teaching spine follows the canonical textbook order
(Facure's *Causal Inference for the Brave and True* ch. 8–9, Huntington-Klein's *The Effect*
ch. 19), with the ad-exposure case as the running example throughout.

Approved directives (2026-07-18):
1. the case is the spine; explain everything carefully, minimal business jargon;
2. Bayes is not the focus but must NOT be over-compressed (kept a 6-slide arc inside Part 5);
3. real data must be emphasized, not compressed (Part 6 expanded to 6 slides).

## 2026-07-21 (latest) · `iv_slides_sh` live polish round (Francesco reviewing slide by slide)
Applied to `iv_slides_sh_src.html` only; 26 slides after the pass (the earlier "27" count was off by one). Do not undo:
- **Slide 4**: backdoor-path definition moved to the LEFT column under the confounder definition (visual balance); U node in svgFork (and both svgDag DAGs) recolored grey → RED with white text, matching the later DAGs; U is red in every diagram now.
- **Slide 5**: the Y-vs-U scatter REPLACED by a two-panel bar figure: left = the two sales averages with a dashed baseline + orange bracket ("gap €23.7"), right = average intent per group, hidden behind a dashed "U is in no log file" placeholder until the checkbox reveals it (−0.46 vs +0.23). Gap label sits RIGHT of the bracket (overlap fixed).
- **Slide 7**: the decomposition's first underbrace is the REAL math, E[Y(1)|X=1] − E[Y(0)|X=1], labeled "effect of the ad on the exposed"; new first bullet ties its second entry to the PO table's N/A cell.
- **Slide 11**: "Graded in the simulated world" bullet DELETED (claim verified true anyway: Y~X+Z gives 24.1 vs naive 23.7; only Y~X+U recovers 15.3); "Why the engine stalls here" box now closes the LEFT column.
- **Slide 13**: the randomizer DELETES the U→X arrow (structural removal, vs conditioning which only blocks): ghost is now a dashed no-arrowhead stub + ✕ + "removed" label, caption says "removed, not merely blocked"; ✕ recentred on the arrow.
- **Slide 15**: 4 condition cards + orphan "what they buy" bullet consolidated into ONE 4-row table (condition | claim | checkable? | what it buys).
- **Slide 16**: NEW "Definition · first stage" key box (the name no longer lives only in eqbox subtext); hierarchy = model → measured π (with gloss line) → 2 bullets; the F-test extracted into a "The gate" callout under the svgFS bars (right column). Slide 18 got the matching "Definition · reduced form" box.
- **Deck-wide**: "in words" phrasing BANNED → "Interpretation of \(\pi\):" etc. (5 occurrences replaced; rule added to the slide-grammar memory).
- **Slide 17**: the 3 bullets (tiny leak / defence / counterexample) moved under the live leak slider; left = 2 condition boxes + formula + "No test will catch it".
- **Slide 20**: message sharpened ("The division is not a modelling choice. It is the only effect size the two measurements allow."); right column leads with "Forget the formula and grade any candidate..."; verdict bullet: "the division is the only survivor, not a choice".
- **Slide 25**: the "Unit check" bullet (a late rules-change, rejected) REPLACED by the computed net: β̂_IV − c = €16.5 − €10 = €6.5 via the {{nb11.net}} token, plus the interval-floor read (€12.7 still pays); the price-map dot now carries a live "net €+6.5" label (the plot always WAS the net: blue line = β̂ − c).
- **AR slide FOLDED into Weak instruments** (deck 26 → 25 slides): the whole Anderson–Rubin block (svgAR fig + slider + interrogation eqbox + bullets, "when it earns its keep" merged into the last bullet) now lives in a collapsed `details.mathfold` "Deep dive" at the bottom of the weak-instruments slide; the F callout points to "the deep dive below".
- **SVG TEXT COLOR BUG (root cause of "colors suck")**: the stylesheet rule `svg text{fill:var(--muted)}` overrides fill ATTRIBUTES (CSS beats presentation attributes), so every figure's text labels rendered muted grey since day one. Fixed in `el()`: text elements get `fill` as an INLINE STYLE. Probe-verified (computed fills now match the code). The same latent bug lives in `iv_slides_src.html` and the geo deck: port the one-line el() fix when next touched.
- **CI fold added to "The IV estimate"** (Francesco: "no mention of intervals... can't we build CIs with frequentist techniques?" then "add it as a foldable appendix"): mathfold "Deep dive · the confidence interval around €16.5" with the eqbox β̂ ± 1.645·SE = 16.5 ± 1.645·2.31 = [12.7, 20.4] (NEW token {{nb11.iv_se}}), interpretation + wider-than-naive bullets, and NEW static fig svgCI grading both 90% intervals against the planted truth (naive [22.9, 24.5] misses, IV [12.7, 20.4] contains it). This finally introduces the interval the price map, negotiation poll, and weak-instruments slide all rely on.
- **Compliers/LATE slide REBUILT** (Francesco: most important, message unclear, ugly colors): sub is now the message ("Whom does the €16.5 describe? Only the users the lottery could move."); NEW "Definition · LATE" key box + explicit eqbox β̂_IV = δ/π estimates E[Y(1)−Y(0) | complier] with a gloss tying it to the naive slide's untouchable contrast; bullets = 3 groups (handles colored to match slices) + monotonicity caveat; manager callout kept. svgStrata recolored navy/orange/grey (compliers = orange protagonist), slice text white (ink on grey), sub-labels were using nonexistent `c.muted` (undefined fill bug) → c.ink, readout green → orange.

## 2026-07-21 (later) · NEW DECK `iv_slides_sh` — management-first, plot-heavy rework
Second comment pass. Rather than editing `iv_slides.html` again, a NEW deck was forked:
- `apps/iv_slides_sh_src.html` (template) → `apps/iv_slides_sh.html` via `apps/build_iv_slides_sh.py`
  (`make html-iv-slides-sh`); same token/DATA/MathJax pipeline, same shards. 51 slides, 6 polls,
  verified (node --check OK, headless 51/51, 0 mjx-merror, 0 unresolved tokens, all new figs draw).
The original `iv_slides.html` is left as-is.

### 2026-07-21 · Part 1-2 restructure (Francesco's follow-up comments) — 27 slides
Approved discussion outcome, applied:
- **"The data" slide DELETED** (histogram removed with it). Its surviving facts (n, who assigns
  what, U never observed, sd €17.1, the contribution definition of Y) live as bullets on the
  new slide 4.
- **New Part 1 order:** case → pitch poll → "The variables and the confounder" (X/Y/U defined
  through the svgFork DAG; confounder + backdoor definition boxes) → naive comparison → gap poll
  → selection bias → simulated world → endogeneity → size of bias → limits of adjustment →
  what-would-fix-it poll. Cause → number → damage.
- **The lottery is introduced ONLY in Part 2**, on a NEW dedicated slide right after the ideal
  experiment (concrete before abstract): what we ran, the Z row joining the data table, the
  exposure equation gaining γZ, and the svgDag fork-vs-instrument figure (moved from the
  definition slide, caption rewritten without condition names). "Our instrument" slide DELETED
  (its scouting q-biz folded into "The instrument, defined", which is now single-column:
  definition + 4 condition cards + opposite-of-a-control + scouting line).
- **Simulated world shows the two-equation Part 1 world** (no Z, no γ slider on svgLab; γZ
  arrives with the lottery slide's equation update). Callout says the equations "generate the
  dashboard you saw", which stays literally true.
- **Limits of adjustment rebuilt**: the close-the-backdoor callout moved here from the old
  confounding slide (teach the fix where it is attempted); svgAdj redrawn to the correct
  convention (W BOXED "held fixed", block marks on the W-paths, arrows never dashed away:
  conditioning blocks paths, does not delete causes); NEW live toggle svgAdjDemo "pretend intent
  were logged": stratifying the simulated world on U recovers €15.5 vs planted €15 (verified in
  node), untick and the right bar is a dashed "requires the U column: not in the data" ghost.
  Punchline sharpened: the method is fine, the missing column is the problem.

### 2026-07-21 · triple-check correctness review (3 independent reviewers) — ALL FINDINGS FIXED
Three parallel reviews (econometric claims; figure code vs claims; internal consistency) over the
28-slide deck. Core econometrics verified sound (PO decomposition exact; OVB = selection-bias term
exact for binary X; δ=βπ; strata arithmetic; poll indices; no banned vocabulary; no dangling
references). 20 findings fixed:
- **Revenue vs contribution (the one WRONG):** Y now defined on the data slide as contribution
  euros ("sales" for short), case/poll wording follows, and the price-map unit check teaches the
  conversion instead of contradicting it.
- **κ vs λ:** sliders relabeled "intent's pull on sales κ" (they were mislabeled "targeting");
  the size-of-bias lesson now names both knobs (λ targeting, κ leak).
- **Overclaims softened:** negotiation-poll reveal reframed as a no-regret cap vs a break-even
  gamble (no "guarantee", no probability-on-a-parameter); verdict now says more measurement is
  "worth close to nothing here", not "cannot change the decision"; LATE "exactly the users a
  higher bid would newly expose" → "the same kind of marginal user"; always-takers "our money" →
  "the lottery"; F>10 rationale distinguishes weak-IV threshold from bare significance;
  monotonicity card de-circularized; Δ decomposition unhatted; "cancels" → "contributes zero".
- **Figure truthfulness:** svgWald prints €3.48 ÷ 0.2106 = €16.5 (was €3.5 ÷ 0.21 = €16.5, false
  at displayed precision); svgAR band now drawn from the baked ar_lo/ar_hi (was a second,
  disagreeing JS interval); svgWeak replicates run at full n=3000 (were n=1500, overstating
  instability ~2x at any drawn F), band = middle 90% of 20 repeats (was min/max of 8), x = median
  replicate F; svgData bars zero-based with € ticks (was an undisclosed €30 baseline); svgEndo
  bottom panel plots Y − βX ("sales with the ad effect removed") so "ad or no ad" is true;
  svgFit2 fit tolerance tightened; svgLab histogram window widened to [0,120]; svgStrata caption
  discloses live-draw rounding vs text tokens.
- **Consistency:** β̂_IV glossed at first use (conditions slide); false "first/second definition"
  ordinals removed; figure label "Wald" (never introduced in prose) → "IV estimate"; one precision
  deck-wide ({{nb11.iv_est}}, the wald token no longer used); 13 orphaned figure IIFEs + unused
  const N deleted (the code layer no longer carries 2SLS/Bayes/Criteo strings).
Known accepted: title slide shares data-sec with Part 1 (matches the geo deck); the read-the-gap
poll names selection bias one slide before its formal definition (intentional name-then-define).
Rebuilt + verified: 28/28, 0 mjx-merror, 0 unresolved tokens, all 20 live figures draw, division
and AR labels now match the prose.

**CORRECTED same day: the keep-list is the deck.** The first cut of `_sh` kept all 51 slides and
only refactored; Francesco: "I said explicitly what to keep and what is not interesting." Now the
deck is **28 slides**: title + the rebuilt spine (case → data → naive/PO table → poll → selection
bias → confounding → simulated world → endogeneity → size of bias → limits of adjustment → poll →
ideal experiment → instrument → our instrument → relevance → conditions 2+3 → reduced form → IV
estimate → why the division is forced) + the explicit keeps (weak instruments, Anderson and Rubin,
compliers/LATE, checklist, price map, negotiation poll, verdict-and-recommendation as the closing
slide). CUT: 2SLS (even the practice note), grading day, precision-is-not-validity, the
strong-enough poll, ALL of Part 6 (Criteo), deliverable/takeaways/close, the Bayes deep dive, both
backups. 4 polls, 25 shard tokens. Unused figure IIFEs remain in the JS, guarded and inert.

The directives encoded in `_sh` (per Francesco's slide-by-slide comments):
1. **Plots everywhere, math demoted.** Eleven NEW figures: svgHist (sales histogram, sd shown),
   svgLab (live histograms by exposure with κ/γ sliders on the simulated-world slide), svgSplit
   (three candidate decompositions of the €23.7 bar, "the dashboard cannot tell them apart"),
   svgEndo (exposure share + avg sales by intent quintile = Cov>0 as a picture), svgBias (naive
   bar split truth vs bias, live κ, replaces the old marker plot), svgAdj (DAG: W-backdoors closed,
   U-backdoor open), svgIdeal (two DAGs, the U→X arrow cut), svgZX (mini first-stage DAG next to
   the regression), svgExcl2 (contamination as a stacked bar, live s), svgWald (the division as
   flow boxes), svgFit2 (prediction line vs measured line, crossing = the estimate); svgStrata
   rebuilt taller with per-segment annotations. Equations now geo-style: bare eqbox (compact
   symbol-glossary lbl at most), interpretation in bullets ("read π in words: ...").
2. **Layouts unblocked**: slide 2 = single flow (4 fact cards → pitch → decision), no forced
   two-column compression; confounding rebalanced; laboratory decompressed by the live fig.
3. **Descriptive titles only** ("The cast of four" → "The data"); no "the customer's life",
   no "is (not) our dial"; the lottery introduced as three short bullets, never one long sentence.
4. **Potential outcomes made explicit**: naive-comparison slide carries the observed/N/A table;
   NEW slide "Selection bias" AFTER the read-the-gap poll with the decomposition
   Δ_naive = effect + E[Y(0)|X=1] − E[Y(0)|X=0] and svgSplit.
5. **Polls are engagement, not exams**: "commit to a number" (spoiled by the planted €15) →
   "what would fix it?" (which data addition identifies the effect; answer: randomized exposure);
   "what can the data check?" DELETED (its scorecard moved into the checklist slide);
   "the recommendation" → "the negotiation" (highest rate you would still sign: the interval floor).
6. **Estimator arc ends at the division**: Wald slide + why-forced slide are the destination;
   2SLS demoted to one practice-note slide ("the software does the division", SE warning kept).
   Side-channel renamed d → s so it cannot collide with the reduced form δ. F introduced as "the
   significance test every such number carries" (quoted, never derived). β re-glossed wherever it
   reappears. LATE slide rebuilt around "the marginal customer is exactly whom a higher bid buys";
   checklist gains the honest-scorecard callout; price map gets the three-zone reading.
Parts 6 (real data), Close, Deep dive · Bayes, Backup: carried over unchanged from iv_slides.

## 2026-07-21 · Francesco's comment pass (APPLIED) — frequentist-complete main deck, Bayes demoted to appendix
Full revision from Francesco's slide-by-slide comments. The deck is now **51 slides** (39 main + 9
"Deep dive · Bayes" + 2 backup + title), rebuilt and verified (node --check OK, headless DOM 51/51,
0 mjx-merror, 0 unresolved tokens, 73 shard tokens).

Structural changes (do not undo):
1. **Bayes is an appendix.** The 8-slide Bayes arc (interval-cannot-say, Bayes-in-one-slide, model,
   knob, BvM, P(pays), poll buy-evidence, VOI) plus the off-switch moved AFTER the Close as
   "Deep dive · Bayes", framed "most likely not lectured". The main deck is a complete frequentist
   treatment: verdict slide now carries the full recommendation (buy at cost, cap at the interval
   floor €iv_lo, re-measure only if the rate climbs toward it). Deliverable/takeaways/close are
   posterior-free; the ONLY Bayes mention before the appendix is one pointer on the Close slide.
   2SLS KEPT (it is the frequentist workhorse: correct SEs, covariates, what software runs).
2. **Part 6 stripped of Bayes**: probit row out of the PROVED table, Bayesian row out of the
   referee table AND the svgRef figure (2 bars now, respaced), market-taught card 2 rewritten.
3. **Slide 2 de-spoiled** (no "catch" callout, the confusing "arithmetic about two groups" bullet
   gone) + NEW Poll "the pitch" (pollF) right after it; NEW Poll "read the gap" (pollG, the
   Δ_naive decomposition) after the naive-comparison slide. 7 polls total.
4. **Title slide = geo deck's**: title-grid + course line ("A guest lecture for Prof. Michele
   Russo's course") + geo author bios + decorative intervals-aside SVG.
5. **Register**: the word "coin" is BANNED (prose, labels, figure JS): Z is "the (serving-priority)
   lottery", generic randomness is "randomization / random draw", nb11.coinflip renders as
   "break-even". Titles are titles (short noun phrases; explanations moved to .sub); subtitles are
   clarifications, never operative content. No forward references to later parts anywhere (the
   single allowed pointer: Close slide "a Bayesian deep dive and two backup slides follow").
   No em-dashes, no prose semicolons (bullet separators only). "One warning that saves careers"
   → "Do not hand-roll the standard error".
6. **Content upgrades**: cast slide introduces the lottery in prose BEFORE the table and defines
   €17.1 as the sd of Y; table headers left-aligned over left-aligned columns (deck-wide);
   naive-comparison slide decompressed with a "Definition · selection bias" box; confounding slide
   gains "Definition · backdoor path" + a "close the backdoor" callout explaining
   conditioning/matching/propensity as one move; σ defined as the logistic function on the
   laboratory slide; OVB slide gains a "What the formula teaches" box (systematic, grows with
   targeting, n absent); adjustment slide gains the two-identical-rows intuition callout.

## 2026-07-20 · slide-grammar pass (user directive) — verified already compliant, NO edits
Ran the `slide-grammar` skill against the deck. Finding: it is ALREADY fully in the grammar from the
v2 rebuild + classical deepening: 0 em-dashes, 58 callout boxes, 126 bullets, definition-first
register. Every remaining `<p>` is grammar-sanctioned (one-clause equation lead-in, one-sentence
`q-biz` punchline, muted footnote caption e.g. sampler-health, or the three deliberate board-ready
quote sentences on "The deliverable"); none is a running paragraph, so converting any would be churn,
not improvement. Balance (grammar rule 6) spot-checked by screenshot at 1600x1000 on the densest
slides: cast-of-four table (3), 2SLS (20), probit-code (33): all fit one screen. Conclusion: no
source change; the deck passes the grammar as shipped.

## Files
- `apps/iv_slides.html` — the deck (2.4 MB, self-contained). Build: `make html-iv-slides`.
- `apps/iv_slides_src.html` — editable template (edit this, then rebuild).
- `apps/build_iv_slides.py` — bake + inject (tokens from shards, `/*__DATA__*/`, MathJax).
- `book/build/lecture_iv_data.json` — baked bundle.

## Final state: 48 slides (46 main + 2 backup), 5 polls, 20 figures
CLASSICAL DEEPENING (2026-07-19): Francesco supplied a full A1–A8 derivation-level treatment of
the classical part ("this is the level of clarity and detail I want... case as backbone... never
use concepts before defining them") and Parts 1–3 were rebuilt to it: +3 new slides (cast of
four, endogeneity-precisely, why-adjustment-cannot-save-it), OVB now the derived plim formula,
four IV conditions (monotonicity added), reduced form carries the substitution derivation
delta = beta*pi and the ITT name, the Wald slide gets the covariance form, 2SLS gets the
purified-Xhat logic and the CORRECTED hand-rolled-SE warning (too WIDE: se_hand 2.95 vs correct
2.31, factor 1.27; the old "too small" claim was wrong). 69 tokens (new: n, ppc_obs_sd,
naive_lo/hi, fs_shift, se_hand, se_correct, se_hand_ratio).
Part 1 · The problem (1–10): Title · The case · The cast of four (NEW: Y/X/Z/U table,
  observed/never-observed, €17.1 spread) · dashboard-number-formally (svgData) ·
  Confounding-defined (svgFork) · The laboratory (DGP) · Endogeneity-precisely (NEW: v=κU+ε,
  Cov(X,v)=κCov(X,U)>0, "the disease", endogenous defined) · Size-of-the-bias = derived plim
  OVB formula + precision trap (svgSim) · Why-adjustment-cannot-save-it (NEW: Cov(X,v|W)=0
  needs a recorded W; "you cannot adjust for what you did not record") · Poll commit.
Part 2 · The idea (11–16): ideal experiment (Cov(X,v)=0 form) · instrument-defined (svgDag,
  FOUR conditions in a 2x2 card grid + what-each-buys) · instruments-in-the-wild · relevance
  (svgFS + the regression form X=b0+πZ+u) · exogeneity+exclusion (svgExcl + discount-code
  counterexample) · Poll what-can-data-check (four conditions).
Part 3 · The estimator (17–21): reduced form (svgRF + substitution derivation δ=βπ + ITT +
  both-correct-neither-answers) · Divide δ/π solved from δ=βπ · fit-the-Wald (svgFit + covariance
  form Cov(Y,Z)/Cov(X,Z) with per-condition reading) · 2SLS stage-by-stage (purified Xhat,
  just-identified, SE-too-wide warning) · Grading day (svgGrade).
Part 4 · When it breaks (22–27): tight-interval-wrong-number (svgSig) · Poll strong-enough ·
  weak instruments (svgWeak live) · Anderson–Rubin (svgAR live) · compliers/LATE (svgStrata live) ·
  checklist table + sentence-that-loses-money.
Part 5 · The decision (28–37): decision space (svgDec live) · Poll sign-it · classical verdict ·
  three-worlds (svgThree) · Bayes-in-one-slide (svgBayes live) · probit model + code + ρ ·
  BvM (svgBvM) · P(pays) (svgPay live) · Poll buy-evidence · VOI.
Part 6 · Real data (38–43): leaving-the-laboratory (PROVED/OPEN) · Criteo intro + cast-mapping
  table · balance photograph (svgBal) · the referee (svgRef) · the off-switch ·
  what-the-market-taught (synthesis).
Close (44–46): deliverable · takeaways · close. Backup (47–48): forensic · routes not taken.

Key pedagogical moves vs v1 (do not undo):
- Classical part is derivation-level (2026-07-19 directive): every object defined at first
  appearance (cast-of-four slide), endogeneity stated as the inequality Cov(X,v)>0 BEFORE the
  bias formula, plim OVB derived not asserted, adjustment killed on its own slide, δ=βπ derived
  by substitution before the divide, covariance form shown with per-condition reading.
- 2SLS hand-rolled SE warning says too WIDE (factor {{nb11.se_hand_ratio}}), backed by tokens;
  do not revert to the folklore "too narrow".
- OVB bias formula slide (6) BEFORE any IV content; predicted {{nb11.ovb}} vs observed naive.
- First stage (11) and reduced form (14) each get their OWN slide, one number each, before the
  division (15), which is worked arithmetic: {{nb11.reduced}}/{{nb11.first}} = {{nb11.wald}}.
- LATE/compliers moved AFTER the estimator (23), per every textbook.
- Definition-first register: `callout key` "Definition · X" boxes; metaphors demoted.
- svgSim labels say "the dashboard"/"the coin method", NOT OLS/2SLS (undefined at slide 6).
- svgRF pins the drawn δ to DATA.scalars.reduced so figure and prose agree exactly.
- Margin-trap slide KILLED (svgMargin IIFE still present, guarded, harmless); one-line unit
  caveat lives in a callout on slide 25. Endnote poll killed. BvM kept in main (31).

## Verification (all PASSED 2026-07-18)
node --check main script OK · headless DOM: 45 slides, counter 1/45, 0 mjx-merror, 0 JS errors ·
all 45 slides screenshotted and read · 0 em-dashes · 0 raw € in math · 63 shard tokens, all
resolved (new: nb11.true, reduced, ovb, ols_predicted, wald, st_share_*, f_leak, nb11b.base…).

## If you revise
- Insert slides before `<!-- SLIDES-END ... -->`, figures before `/* FIGURES-END ... */`; rebuild.
- Title slide (~100 KB of base64 logos) sits between the head and slide 2; splice AFTER its
  `</section>`, never regex across it.
- Verify: node --check; `--headless=new --dump-dom`; screenshots via `scratchpad/cdp_slides.py`
  (must navigate about:blank then file://...#N; needs --remote-allow-origins=*).
- Never hand-type a number ({{nb11.*}} tokens; build hard-fails on unknowns). No em-dashes.
  No raw € inside math (\text{€} is fine).

## Known, accepted
- Live sims are one mulberry32 draw (seed 264275 matches the shards: naive 23.7 / wald 16.5 /
  F 156 / 56→77); tiny divergences vs shard tokens are expected, EXCEPT svgRF where δ is pinned.
- Poll 3 remains the classical GO; "classical decides, Bayes prices" invariant preserved.
