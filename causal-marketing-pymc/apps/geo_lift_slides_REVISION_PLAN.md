# geo_lift_slides.html revision — plan + state (2026-07-16)

## 2026-07-19 · BOX/BULLETS GRAMMAR REFORMAT (user directive) — DONE, verified
User: on slides, an important concept = a callout BOX with ONE streamlined sentence; details/
definitions = BULLETS, one sentence each (+ optional short example); same for text around
figs/equations; NO running paragraphs; NO em-dashes; balance elements to fit one screen. This is
FORM, not word-count (a shorter paragraph is still wrong). Captured as the `slide-grammar` skill
(.claude/skills/slide-grammar/) + [[causal-marketing-pymc-slide-grammar]] memory.
- ALL 48 content slides reformatted src-side: every `<p>` blob -> box or bullets; overloaded
  callouts split (headline sentence stays, supporting points become bullets outside, nuance to a
  mathfold); figure captions/eq lead-ins cut to one line; bold handle + COLON replaces the em-dash.
- Em-dashes 31 -> 0 (prose, callout titles, h2s, endnote-flag, one JS comment); en-dashes kept
  (names/ranges: Bernstein-von Mises, EUR239-276k).
- Balance: slide 3 -> fig-left/reading-right (cols c32); slide 21 -> fig beside setup bullets;
  slide 20 punchline box moved above its fold. Two inherently-dense slides keep 1-2 trailing
  elaboration elements a hair below the fold (14: fold+punchline; 32: 2 eye-calibration bullets) --
  core content fully visible; can split/fold further on request.
- Preserved everything: all live-figure span IDs, {{tokens}}, equations, figures, polls, tables,
  and every geo_claims.yaml required-text substring.
- VERIFIED: build clean; verify_geo_deck.py 304 checks / 0 failures (all numbers intact); whole-deck
  mjx-merror = 0; console clean on load; screenshots reviewed 2,3,4,5,8,10,14,20,21,32,43,47.

## 2026-07-19 · IV-deck classical-standard port (user directive) — DONE, verified
User: port the clarity/detail register of the IV deck's classical part (the A1-A8 "world described
precisely" narrative) into the geo deck's classical slides; case as backbone; define-before-use.
Seven surgical edits, all inside existing slides (no insertions, numbering unchanged, no shipped
number changed):
- S3 rebuilt as the A1 "world inventory": what the file contains (Y_jt defined w/ units, 30x60=1,800
  observed numbers, the four design facts, who assigned treatment: the marketing team, not a coin);
  what is NOT in the file and never will be (the 20 counterfactual weeks, the sales machinery),
  symbol-free since PO notation arrives at S7; two load-bearing measured constants span-filled
  (panelBase EUR126k/wk; NEW preSd EUR9.2k/wk pre-launch sd, "will matter in Act II"); the two-
  honest-computations close (B/A +7.2 vs wave-removed step ~10k: same file, two answers, nothing in
  the file arbitrates). PLANTED-TRUTH BULLET REMOVED from S3 (define-before-use: it used the
  simulation before S4 introduces it, and spoiled poll S6). panelRead wave string de-overclaimed
  ("whether that step is the campaign ... is the question Act II answers").
- S4: new callout "Which of these is ever observed?" (only Y_jt lands in the file; alpha/gamma/f/eps
  exist in the simulator's code and in reality, in no dataset); new closing line stating the planted
  truth in business units via NEW spans dgmTruthWk (~14.2k/wk) / dgmTruthTot (~284k) filled from
  DATA.true_total, + "from here on we pretend not to know it".
- S13: new callout "None of these numbers ships a warning label" (A3 port: exact arithmetic, errors
  are wrong claims about Y(0) not noise, 200 weeks still charges the tide to the campaign, cure is
  a better claim not a bigger sample).
- S14: new "Read the equation in words" bullet under the mismatch decomposition.
- S15: new "Notice what is absent from B: the amount of data" bullet (weeks shrink noise only;
  n shrinks only the 1/n; the 1 is the treated draw, nothing averages over one treated market).
- S16: cannot-adjust bullet expanded to the full A4 argument (controlling conditions on RECORDED
  variables; f_t/gamma_1 never written to disk; adjusting for observables removes only the part
  flowing through them) + structure-not-measurement rescue bullet.
- JS (panel IIFE): preSd computed from DATA.treated pre-window; dgmTruth spans filled there too.
Verified: node --check OK; headless 46/46, 0 mjx-merror, 0 console errors, all new spans filled
(preSd 9.2 / truth 14.2 / total 284 / base 126 checked against baked DATA in python); em-dash sweep
clean; raw-euro-in-math audit clean (all hits are pre-existing \text{euro}); screenshots 3/4/13/14/15/16
reviewed (no overflow, no collisions).

## 2026-07-17 CASE RE-PRICE: CAMPAIGN_COST 90 -> 75 (user decision; 90% bar kept) — DONE end-to-end
- WHY: user wanted a default where the campaign clearly pays in expectation (~+EUR10-20k net) yet
  stays below a GO. At 75: P(pays)=0.78, E[net]=+16.7k, iROAS 3.47, headroom 67 (11% above), VOI ~2k,
  k_needed ~4 (feasible), verdict TEST FURTHER; rescaled-to-design P=0.83, label HOLDS; iid P=0.72
  (agreement-by-coincidence teaching point). Straddle [68,117] unchanged, still straddles 75.
- PIPELINE: nb07 CAMPAIGN_COST=75 + FULL re-exec (nbclient, kernel cmp-core, cached fits: 260/262/72
  reproduced); nb07 markdown cells 1,7,20,21,23,24,26,27,40 rewritten to the 75-world (new stories:
  scale-robustness instead of label-flip; feasible-test-vs-VOI "two ledgers"; iid-agreement
  coincidence); 2 verdict-carrying figure captions in cell 42 fixed + re-exec; chapter geo_lift.tex:
  15 edits (epigraph, sweep roles re-wired: 75=interior case / 90=knife-edge, felt-stakes, euro
  section, TEST-FURTHER subsection, sizing two-ledgers, real-data same-label/opposite-anatomy,
  takeaway 8); offprint rebuilt 59pp clean, verdict spot-checked in PDF.
- DECK: N.sweep_* re-baked from new shard; DATA.tri_be=214.3, tri_P recomputed [0.88,0.72,0.73];
  45 text edits across slides 2,24,25,26,27,28,29,30,34,35,36,39,41,43,46; poll E correct answer
  C->A (~4 markets) with two-ledgers reveal; S34 h2 + skew caption new lesson (price-slide, not
  tail-paradox); S39 anatomy callout (wide-margin/wide-posterior vs whisker/tight); funnel JS cost
  75; tri BE label computed from DATA. Verified: node OK, console clean, 0 mjx-merror, 46/46,
  0 em-dash, screenshots 26/29/30/31/34/35/36/39/41/46 reviewed.
- THETA quadruple-check (same pass): Bayes toy now feeds MEASURED data: ybar=13.0 (=260/20, gap
  series mean; was 14.2 = the unobservable planted truth) and sigma=4.5 MEASURED from the gap series
  (was an invented 8); all derived claims (posterior sd 1.0, data weight 98%) span-filled from the
  same computation; wrong "outvoted 4-to-1" claim replaced.

## 2026-07-17 second pass (user's per-slide comments, slides 1-10) — DONE, verified
- Follow-up 5 (2026-07-17, 10-item pass; 46 slides). Items 1-5,7-9 DONE; items 6+10 BLOCKED on a
  case-design decision (see below).
  (3) Back-door primer slide REMOVED (orphaned once the frame moved to n=1 mismatch); its svgDag0
      IIFE deleted; the conditional back-door callout on the DAG slide made self-contained.
  (4) REORDER (user-specified): SC is now introduced and built BEFORE the rivals are graded.
      New Act II: 7 PO -> 8 Abadie -> 9 Matching loadings -> 10 Estimator -> 11 Constraint ->
      12 Fit the blend -> 13 Every shortcut (four estimators) -> 14 Confounding graph ->
      15 DiD algebra -> 16 Blend on the graph -> 17 Identification. Done by script (order asserted);
      every cross-ref repaired: "preview: the estimator this act builds" -> "the one you just fitted",
      "the previous slide's Limit 1" -> self-contained, "next two slides: algebra then dials" ->
      "the next slide proves it in algebra", Abadie gained a bridging sub (follows PO now, not naive).
  (1) Placebo fig rebuilt: histogram of the 29 placebo totals + rug + zero + best-placebo marker +
      green real metro, real axes/ticks/labels (was a bare dot strip, no axes). Prose numbers
      (best placebo EUR109k, +/-EUR50k) now span-filled from the same data the figure draws.
  (2) Inversion slide rebuilt around the actual inversion: eqbox now shows
      H+q05 <= 260 <= H+q95  <=>  260-q95 <= H <= 260-q05 (underbraced both sides), prose explains
      the shift-invariance assumption; figure got 3 labelled lanes (A null / B slid cloud with the
      shaded 90% band + H+q05/H+q95 edge labels / C accepted set), shared numeric axis, in-figure
      verdict; H default 284 -> 300 to match the prose example. Figure arithmetic verified against
      the shard: [194.5, 334.9] -> EUR195k/EUR335k.
  (5) Spillover slide rewritten: concrete story (metro's TV reaches the commuter belt, which IS the
      donor pool), phi defined, chain leak->synthetic up->gap down, "bias toward zero", why no
      diagnostic can see it (leak starts at launch so pre-fit stays green), defence is design;
      shipped number is a FLOOR.
  (7) NEW slide 29 "What you say to the board (classical)" after the classical verdict: exit-ramp
      deliverable (spoken sentence + board table, all classical), closing callout names the three
      things it cannot answer (P(pays), headroom price, is-a-study-worth-it) -> hands to Act V.
  (8) theta BUG FIXED: the Bayes toy used ybar=14.2, the PLANTED TRUTH, as if it were data. Now
      ybar=DATA.real_tot/20=13.0 (the gaps the analyst actually observes). Slide now states theta =
      weekly lift in the warm-up, and flags that the real estimand is the 20-week total tau and that
      the toy's iid assumption is the one the endnote breaks.
  (9) Indicator made consistent with slide 4: 1{m tau > c} -> 1_{{m tau > c}}.
  Verified: node OK, console clean, 0 mjx-merror, 46/46, 0 em-dash, div-balance asserted per slide,
  screenshots 20/21/23/29/31 reviewed.
- Follow-up 4 (ACT II RESTRUCTURE, 44 -> 46 slides): user flagged terrible S9 layout, undefined tau,
  missing DiD algebra, SC used before introduced, footnote-itis, error not plotted.
  (a) S9 relaid out (text+eqbox left, problem-only DAG right; new #svgDagP has NO synthetic node,
      grey Y_j "donor sales"); tau -> tau-bar defined (avg weekly effect; tau = 20*tau-bar).
  (b) NEW slide 10 "Push the world to its limits, on paper": user-supplied DiD algebra:
      tau-hat^DiD = tau-bar + B + noise, Var(B) = s^2/3 (1+1/n) [sum of squared factor drifts];
      Limit 1 s->0 sufficient / Limit 2 sigma_eta->0 not sufficient (only the walk term drops);
      noise survives both ("systematic bias vanishes", never "DiD = truth"); SC forward promise.
  (c) Interactive (now 11): ERROR PLOTTED as red segments between truth line and each bar with
      "error +x.x" labels (user: "see the error in a plot, not a footnote"); caption content
      promoted to bullets; SC eqbox labeled "(preview: the estimator the rest of this act builds)".
  (d) NEW slide 17 "What the fitted blend does to the graph" after Fit-the-blend: repair DAG
      (#svgDag with green node) + footprint-matching bullets + "one cure, both readings" moved here.
      svgDag IIFE refactored to one drawer, two targets.
  (e) Footnote policy: valuable content moved out of .cap into bullets on S3 (definitions/wave story)
      and S16 mixer ("this is where the headline number is born": tau-hat = sum of post gap = eur260k,
      live in the readout; answers "where does 260k come from").
  Verified: node OK, console clean, 0 mjx-merror, 46/46, 0 em-dash, screenshots 3/9/10/11/16/17 reviewed.
- Follow-up 3 (REFRAME, supersedes follow-up 2's placement): user challenged the back-door-first
  frame; assessment agreed: the deck's DGP has NO assignment mechanism, so f_t->X is asserted, not
  shown. S9 rebuilt mismatch-first: "notice what this graph does NOT contain: an arrow into X";
  eqbox tau-hat^{T-C} = tau + level gap + (gamma_1-gamma-bar)^T f-bar_post + noise (underbraced);
  DiD kills level gap only; n=1 leaves nothing to average; ties to S10's s->0 slider. Back-door
  demoted to a conditional callout ("if the metro was picked for its character": plausible, not
  established, data cannot settle it). DAG labels: "(confounder)"->"(shared drivers)",
  "subtracts the back-door"->"subtracts the shared flow". S8 sub repositioned as the general
  concept + handoff ("the next slide asks how much of it our campaign actually contains").
  S2: "because it looked promising" REVERTED (not in the case); transport callout made conditional.
  Two-arrow randomization point MOVED to S36's "Why this dataset" callout (where randomization is
  introduced; 50-geo averaging + back-ref to the S9 mismatch term). Chapter-side overclaim logged
  in LIST_TO_FIX (2026-07-17 back-door-framing entry). Verified: node OK, console clean,
  0 mjx-merror, 44/44, screenshots S8/S9/S36 reviewed.
- Follow-up 2: S9 randomization callout reworked to the TWO-ARROW decomposition (user-supplied
  framing): coin flip deletes f_t->X only; f_t->Y_t survives (it IS the outcome model); new eqbox
  tau-hat = tau + (gamma_1 - gamma-bar)^T f_post + noise; mismatch averages out over 50 geos,
  not over 1; SC attacks the surviving arrow (matches loadings, kills the mismatch term), never
  asks how X was assigned; "bias column vs variance column", both = Act VI. Back-door language now
  reserved for the chosen-market case only.
- Follow-up: S2 bullet now says the metro was chosen "because it looked promising", plus a callout
  answering "isn't the test biased then?": within-metro estimate unbiased (fit conditions on
  pre-launch character; anticipation is the one poison, placebo-in-time hunts it), rollout
  extrapolation optimistic (pilot effect = ceiling; NO-GO reinforced, GO discounted). The chapter-side
  version of this paragraph is logged in book/LIST_TO_FIX.md (2026-07-17 transportability entry).
- S2: reordered data -> three questions -> method; BOTH punchline callouts removed (user: discovery
  journey, and the margin-trap-as-revelation framing reads as naive); replaced by a no-spoiler route line.
- S3: numeric axis ticks + faint grid (new shared helpers __ticks/__grid used by panel/dgp/naive figs);
  "treated metro" label moved to legend band (was overlapping lines); caption now DEFINES naive
  before/after and the planted effect; WRONG readout "the treated bump nearly disappears" replaced:
  the truth (computed from DATA) is BA +7.2 vs planted 14.2, the wave DIPPED post-launch and hides
  half the effect; ticking the box reveals a ~+10k/wk step (computed live, span-filled).
- S4: "Why simulate" callout moved to top; compact+expanded DGP merged into one equation; indicator
  now \mathbf{1}_{\{t\ge T_0\}} (subscript); U(1-s,1+s)^3 cube removed (worded per-ingredient);
  eqbox .lbl subtexts promoted to prose/bullets; endnote teases removed.
- S5: sub explains the sandbox is its own draw (why it differs from S3); caption states dashed blue
  = potential outcome from re-running with lift off (NOT synthetic control); new callouts define the
  readout (true lift = avg of planted 12%-rate weekly effects; BA and its % error) and spread s.
- S6 POLL WAS NUMERICALLY BROKEN (claimed observed +12%; data says +5.7%; answer arithmetic didn't
  hold). Rebuilt: observed +7.2k (+6%) vs true 14.2k, correct answer "double the bump", reveal
  teaches naive bias runs in either direction. Numbers span-filled from DATA by the panel IIFE.
- S7: Y_{1t} -> Y_t with "(market index dropped)" note; lbl promoted; endnote tease removed.
- S8: lbl promoted to prose (two-languages bridge sub added in the earlier pass).
- S9: right column rewritten: f_t -> X justified as how firms choose markets; new callout answers
  "couldn't we randomize?" (yes: closes the back-door, Act VI does it; but 1 treated unit =
  unbiased-yet-imprecise, so SC still needed); merged identification one-liner.
- S10: static bars replaced by a TUNABLE live fig: same sandbox generator/seed as S5, sliders for
  loading spread s + macro sigma_eta, all four estimators re-scored live, SC weights refit by
  exponentiated gradient (600 iters, validated in node: s=0 -> DiD error ~0.8 i.e. noise-only);
  four baked case numbers (N.naive_*) quoted under each formula via span-fill.
- Convention note: eqbox .lbl subtexts are now BANNED on slides 1-10 per user feedback; slides 11-44
  still carry them, sweep pending user confirmation.
- Verified: node --check clean, headless console clean, 0 mjx-merror, 44/44, 0 em-dashes,
  screenshots of slides 2-10 reviewed.

## 2026-07-17 follow-up pass (external review + user notes) — DONE, verified
- BUG (all figures): the theme initializer set data-theme without invoking window.__redraw, so every
  SVG drew with LIGHT palette colors and dark-mode users saw invisible ink strokes (the "white curve
  missing" on slides 3/5) until any redraw. Fixed: __redraw runs once after the initial theme is applied.
- Slide 4: DGP expanded term-by-term (underbraced trend 0.4t, the two sines 8sin(2πt/26)+4sin(2πt/13),
  macro walk as Σηs with Var = t·ση²), constants verified against src/cmp/dgp.py; two-column layout.
- Slides 3/5 differentiated: new subs, "analyst's view (frozen, no truth)" vs "model-owner's view (live, truth on)".
- Slide 8: "same problem, second language" bridge sub (PO table = what, DAG = why).
- Slide 23: "do not memorise the euros that follow" pointer to the deliverable board table.
- Slide 33 poll answer FIXED: old text sized on a €25k/€9k sd that matches no shard; now sized on the
  shipped AR(1) width (sales sd €72k = nb07.bayes_sd, profit sd ≈ €25k, factor ~16, k≈250), with the
  charitable iid width (€9k profit sd, k≈36) kept as the a-fortiori bound. Both infeasible.
- Slide 37: new callout reconciling sim NO-GO (P=0.45) vs real TEST FURTHER (P=0.81 = nb07b.p_profit_ar):
  precision (50 treated geos averaged, read daily), not economics (iROAS 2.89/2.98 vs same 2.86 bar).
- Verified: node --check, headless console clean, 0 mjx-merror, 44/44 slides, em-dash sweep 0,
  screenshots of slides 3/4/5/8/23/33/37 reviewed; svgDgp treated stroke now #dbe4ee at load in dark theme.
- Numbering note: the deck counter and URL hash are 1-indexed (title = 1); the external review counted
  title = 0, so review slide n = deck slide n+1.

Working file: `apps/geo_lift_slides.html` (the slide deck; the scroll version is untouched).
Data file: `book/build/lecture_geo_data.json` — ALREADY re-baked with all new fields (see below).
Bake script: scratchpad `bake_lecture_extras.py` (session ad1bb8e7…/scratchpad). Ran successfully with `.venv/bin/python`.

**STATE: COMPLETE (2026-07-16, second session).** All 25 feedback items implemented: 44 slides,
10 new (backdoor primer, loadings demo, OLS/n_eff, t-test-fails, three-distributions, sim-recap,
real-data EDA, plus the earlier DAG/falsification/real-data set), 6 new JS figures + 5 upgraded
(inversion accepted-set bar, placebo-time anticipation toggle, verdict-colored profit mass,
posterior-predictive overlay, legend swatches), DATA + logos injected, zero em-dashes, zero
MathJax errors, node --check clean, headless Chrome console clean, 20 slides screenshot-verified.
real_tot re-patched to 260 after the re-bake (the bake preserves it now only if you don't re-run
extract_lecture_data.py; if you do, patch real_tot back to 260 before injecting).

## User feedback being implemented (2026-07-16 message, ~25 items)
0. Remove ALL em-dashes (visible text AND JS-generated strings; done in every rewritten slide, global sweep still pending).
1. Title: authors + credentials + emails, PyMC/PyMC-Labs logos, method name huge, chips removed. DONE (logos pending injection).
2. Boardroom: 3 questions stacked/prominent, bullets+bold, margin-trap punchline reframed as
   "revenue vs profit is a P&L reading error, not statistics". DONE.
3/4. DGM split into equations slide + simulator slide; svgDgp gets axis labels + legend band (JS edited). DONE.
7. NEW generic back-door primer slide (Z=season TV example) before the SC DAG slide (needs new fig `svgDag0`). Markup DONE.
8. Naive estimators: 4 formulas each in own eqbox w/ readable explanation; computation explained. DONE (dropped naiveTbl table; JS has null guard).
9. Factor model as component bullets (δ, λ, μ defined; "shocks" defined) + NEW toy loadings-match slide (needs `svgLoad` + slider `loadW`). Markup DONE.
10. Estimator unpacked as bullets + NEW "what the constraint buys" slide (needs `svgOls`, `svgNeff`,
    spans olsPre/clPre/olsPost/clPost/olsNeg/olsMin/olsSum filled from DATA). Markup DONE.
11. Mixer: implied-lift definition added to caption. DONE.
12. Identification: colored PASS/UNTESTABLE table. DONE.
13. NEW "significance the usual way" slide (t-test undefined at n_T=1) + reworded poll B. DONE (no fig needed).
14. Placebo-in-space: all symbols defined, "planted"/"real" explained. DONE.
15. Inversion: 4-step recipe + fig header explains green-line-is-data; JS must add accepted-set bar
    (green stretch [real−q95, real−q05]) and taller viewBox 235. Markup DONE, JS PENDING.
16. Placebo-in-time: computation explained + NEW checkbox `ptAnt` ("broken world: sales leak 6 weeks early")
    + readout `ptRead`. Markup DONE, JS PENDING (inject anticipation ramp into gap series, stylized).
17. Spillover: computation explained (re-simulated worlds, refit per φ). DONE.
18. Stats summary decompressed. DONE.
20. Margin trap: two eqboxes with full-size prose, no tiny annotations; fixes overflow. DONE.
21. Decision space: two lines (net-zero €91k vs straddle zone 0.35×[195,335]=[68,117]) explained above fig. DONE.
22. Classical verdict: `€` inside math caused "Math input error" → now `\text{€}260\mathrm{k}`; clean hierarchy;
    + NEW "Three worlds, one classical report" slide (needs `svgTri` from DATA.tri_*). Markup DONE, JS PENDING.

## STILL TO DO — markup
- Slide 23 (Bayes primer): define θ = weekly lift τ_wk; posterior vs posterior-predictive (add overlay checkbox);
  benchmark prose (posterior sd 8/√20≈1.8 swamps prior sd 8).
- Slide 26 P(profit>c): split the ugly identity (definition first, number in prose); slider color coding
  (shaded mass + readout green/amber/red by GO/TEST/NO-GO); house bar stays 0.9 (matches chapter).
- Slide 27 poll: define k = number of markets in the follow-up test (1/√k).
- Real-data act: NEW "what the simulation proved" recap slide + NEW EDA intro slide
  (Google geo experiment: 100 geos, 50/50 randomized, 93 days, launch day 42, 28-day campaign, $50k spend;
  fig `svgReal` from DATA.re_treat/re_ctrl/re_launch/re_coolend); enrich referee + off-switch slides
  (numbers from book/build/results/nb07b.json — never hand-type).
- Endnote slides + close: em-dash sweep only.

## STILL TO DO — JS (all appended near other IIFEs; style: clr/COL/lin/path/el helpers)
- svgDag0 (generic Z→X, Z→Y DAG; reuse arr/node helpers pattern from svgDag)
- svgLoad (toy 1-factor demo: factor = smooth wave seeded mulberry32; treated=1.2×f+level; A=0.8, B=1.6;
  blend=(1−w)A+wB; divider at week 40; readout blend loading + tracking error; slider loadW/loadWv)
- svgOls (treated pre + y0_true post (dashed ink), synth_cl blue, ols_synth red; launch line;
  fill spans: DATA.cl_pre_rmse etc.)
- svgNeff (sorted |w| bars: w_cl_all blue vs OLS-illustration; simplest: two bar rows w_cl_all vs w_ar1_all? NO —
  this fig is "the weights OLS chose": bar chart of OLS weights incl. negatives (need ols weights per donor?
  NOT baked — either bake `ols_w_all` sorted, or draw from ols_n_neg/min/max/sumabs as schematic;
  PREFER: add `"ols_w_all": sorted w_ols` to bake script and re-run, it's cheap)
- svgTri (DATA.tri_x, tri_pdfs[3], tri_P, tri_be=257.1; three colored curves + break-even line + P labels)
- svgReal (daily mean sales/geo: re_treat vs re_ctrl, launch + cooldown-end verticals)
- svgInv: viewBox now 235 → add accepted-set bar at bottom: lo=real−q(pl,.95), hi=real−q(pl,.05);
  green segment on H axis + marker at current H; keep existing lanes.
- svgPtime: add ptAnt checkbox listener; when on, add ramp (e.g. +linear 0→8k over weeks 34-39) to a COPY of
  gap series, recolor fake-window annotation red, readout via ptRead.
- svgSkew: color shaded mass + readout by verdict (P≥.9 green GO / ≥.5 amber TEST / else red NO-GO).
- svgBayes: optional posterior-predictive overlay checkbox (sd = sqrt(sPost²+sig²)).
- svgDgp: DONE (axis labels, legend band, H=260).
- Poll E answer: k defined. Legend strings with '—' glyphs (svgBayes '— likelihood' etc.) → use line swatches.

## FINAL SWEEPS (order matters)
1. Re-run bake script IF adding ols_w_all (append field; keep everything else).
2. Re-inject DATA: python re.sub between /*__DATA__*/ and /*__ENDDATA__*/ with json.dumps of
   book/build/lecture_geo_data.json. (Forgetting this killed the deck once: undefined DATA.gap_ft.)
3. Inject N additions if any (re_* numbers can go in DATA instead).
4. Inject logos: replace __PYMC_B64__ with scratchpad pymc_banner.svg.b64, __LABS_B64__ with pymclabs.svg.b64.
   Check dark/light rendering (labs logo may be white-on-transparent → white chip background already in CSS).
5. Em-dash global sweep: grep -n "—" on the file OUTSIDE the MathJax blob line (line ~179); rewrite each.
6. MathJax audit: grep for raw € inside \( \) or \[ \] (causes Math input error); use \text{€}.
7. Verify: extract JS → node --check; Chrome headless console (--headless=new --enable-logging=stderr --v=1);
   screenshot EVERY slide (#1..#~44) both themes spot-check; check equation fit (fitEq) on dense slides.

## Answers owed to the user in the wrap-up message
- Slide 8 "is it in the chapter?": yes, §9.5 classical baseline / naive-estimator table; numbers are the
  N.naive_* macros baked from the same panel (BA 7.2 / T−C 19.3 / DiD 10.3 / SC 13.1 vs truth 14.2).
- Slide 26 "GO threshold 75% instead of 90%?": verdict at €90k unchanged (P=0.45 < 0.75 → still NO-GO);
  headroom price rises €66k→€76k (baked: headroom90=66, headroom75=76; chapter quotes ~€67k from MCMC draws).
  The chapter's decision and every table stay as-is; only the headroom sentence would change if the bar changed.
  The "no feasible k" poll answer is ALSO bar-dependent (at 0.75 a ~70-market test would suffice in principle).

## 2026-07-18 · Facure-benchmark pass (assessment + fixes)

Assessment vs Facure's handbook (simplicity/flow) + five axes; then fixes, all deck-only (no shipped number changed, no notebook re-exec needed):

**Same world everywhere (user directive).** Slides 5 and 13 now render the BAKED CASE PANEL from DATA at default dial settings (green badge "showing the case dataset"), with `isCase()` guards; any slider move switches to the live mulberry32(20260716) generator (orange badge "re-simulated world") and a "back to the case" button returns. Slide 5 default readout = true €14.2k/wk, B/A €7.2k/wk (matches slides 3/6); slide 13 default bars = N.naive_* (7.2/19.3/10.3/13.1) vs truth 14.2 (matches its own boxes). The old "sibling world" paragraph rewritten.

**Number fixes (triple-check vs shards).** s17 LOO range 255-266 -> 239-276 (nbSevenLooLo/Hi); s29 stale "45% chance" example -> 78%; s23 leak-figure endpoint labels now use N.sp_clean/sp_contaminated (260/236, kills the 260.5->261 double-rounding); DATA.headroom90 66->67 (dead data, aligned to shard); s16 fh stale "Slide 9's graph" -> "Slide 14's graph"; s38 stale "slide-9 mismatch term" -> "Act II's factor-mismatch term". Everything else verified against nb07/nb07b shards (~40 identities checked, all pass).

**Facure-inspired pedagogy.** s8 factor model UNIFIED to slide-4 notation (alpha_j + gamma_j^T f_t; delta_t/lambda/mu demoted to a "papers' notation" line in the pedigree box); s10 gains the "regression flipped" bridge callout (donors=variables, pre-weeks=observations); s20 gains the Abadie placebo pre-fit filtering bullet (0 dropped of 29, p=0.033 at 2x/5x/20x thresholds - real shard values p_filter_*); s41 retitled "...now with the probability".

**Layout system.** De-columned s4/s8/s31 (cols kept only where genuinely comparative: s13 quartet, s15 two limits, s23/s14/s16 fig+reading, s32, s38, s39, s44); 8 load-bearing eqbox .lbl subtexts promoted to bold bullets (s32 x2, s33 BvM, s36 headroom-invoice + VOI, s40 hull, s44 x2 coverage, s45 n2-n3); pure symbol glossaries kept as .lbl (s18, s34, s45 state-space). First mathfold uses: s2 (the one poison), s15 (Var(B) prefactor derivation), s31 (two caveats). s2 Q&A and s38 "why this dataset" boxes bulletized.

**Verified:** node --check OK; headless: 46 slides, 0 mjx-merror, 0 console errors; per-slide div/ul/details balance OK; em-dash sweep clean; screenshots reviewed (2,5,8,13,23,44).

**Open (chapter-side, not deck):** none from this pass. Realism/consultant-fidelity research (GeoLift/Google/Measured benchmarks) delivered in chat 2026-07-18; possible future endnote "how this runs in practice" NOT added pending user decision.
