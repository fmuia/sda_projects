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
