# IV slide deck (`apps/iv_slides.html`) — COMPLETE

Chapter 13 (instrumental variables) as a geo-style interactive HTML slide deck, to the standard of
`apps/geo_lift_slides.html`. Built with the `lecture-deck` skill. **DONE 2026-07-17: 41 slides, verified.**

## Files
- `apps/iv_slides.html` — the deck (2.4 MB, self-contained). Build: `make html-iv-slides`.
- `apps/iv_slides_src.html` — editable template (edit this, then rebuild).
- `apps/build_iv_slides.py` — bake + inject: `{{nb11.*}}`/`{{nb11b.*}}` tokens from shard `text`;
  `/*__DATA__*/` from the baked bundle; `/*__MATHJAX__*/` from `apps/vendor/`.
- `book/build/lecture_iv_data.json` — baked bundle (1200 posterior draws + all nb11/nb11b numeric
  scalars + the DGP params). Draws source: `apps/iv_lecture_data.json`.

## Final state: 41 slides
Act I question (1-6): Title · Boardroom · Data-live · DGP-eqs · Simulate-live(κ,γ) · Poll1.
Act II method (7-15): potential-outcomes · back-door+DAGs · naive-graded · instrument · compliers-live ·
  2SLS=Wald · exclusion-buys-live · fit-Wald-live · ID table (PASS/BY-DESIGN/UNTESTABLE).
Act III is-it-real (16-20): significance-the-usual-way · Poll2 · weak-IV sweep-live · AR test-inversion-live ·
  three-numbers + the sentence that loses money.
Act IV euros (21-24): Poll3 · margin trap-live · decision space-live · **classical verdict banked**.
Bridge (25): three worlds, one classical report.
Act V Bayes (26-31): Bayes-in-one-slide-live · the row that cannot be true + probit repair + PyMC code + ρ ·
  BvM · P(β>c)-live · Poll4 · headroom & VOI.
Act VI real data (32-35): what the simulation proved (PROVED/OPEN) · Criteo + balance EDA · the referee ·
  **the off-switch** (the "better" probit misprices Criteo).
Deliverable (36-37): board sentences + numbers table · 7 takeaways.
Endnotes (38-41): Poll5 (trust the tight interval) · the forensic (error-scale prior guilty) ·
  routes not taken (AR / Abadie κ / Lee bounds) · Close.

5 polls, 16 live/SVG figures: svgData svgSim svgDag svgGrade svgStrata svgExcl svgFit svgSig svgWeak
svgAR svgMargin svgDec svgThree svgBayes svgBvM svgPay svgBal svgRef.

## Verification (all five, PASSED 2026-07-17)
1. `node --check` on the extracted main script: OK.
2. Headless `--dump-dom`: 41 slides, counter "1 / 41", **0 mjx-merror**, 344 mjx-container, **0 JS errors**.
3. Screenshots read (1440x900 per hash): title, data, DGP, sim, DAG, compliers, 2SLS, exclusion, fit,
   ID table, significance, weak sweep, AR, margin, Bayes updater, model+code, P(pays), referee, close.
4. Sweeps: **0 em-dashes** (src and final), **0 raw euro inside inline math**.
5. Numbers: **56 shard tokens**, all resolved; derived numbers (naive_err/wald_err/post_err/wedge) use
   tokens, not hand-typed. Seed **264275** makes the live sim reproduce the shards exactly
   (naive 23.7 / 2SLS 16.5 / F 156 / first stage 56->77).

## If you revise
- Insert slides before `<!-- SLIDES-END ... -->`, figures before `/* FIGURES-END ... */`, then rebuild.
- Verify harness: `node --check`; Chrome `--headless=new ... --dump-dom`; screenshots via
  `scratchpad/cdp_slides.py "<fileurl>" <prefix> "n1,n2,..."` (navigates about:blank then file://...#N;
  the forced reload is REQUIRED because the deck reads location.hash only on load).
- Never hand-type a number: add a `{{nb11.key}}` token (the build hard-fails on unknown tokens).
- No em-dashes anywhere. No raw euro inside `\(..\)` (inside `\text{}` is fine).

## Known, accepted
- The live sim/AR are one JS draw (mulberry32 != numpy), so tiny divergences vs the shard are expected
  and honest (AR set renders 12.8-20.0 vs the chapter's 12.6-20.2). Prose always cites the shard tokens.
- Act IV reframes the skill's "margin trap" to preserve the chapter's verdict: the base case is margin
  100% (the chapter's β is already value per exposure, net €6.5), and the slider shows where a
  revenue-denominated β would flip. Poll 3 is the classical GO (the €13.7 cap poll moved to Act V,
  keeping the "classical decides, Bayes prices" invariant).
