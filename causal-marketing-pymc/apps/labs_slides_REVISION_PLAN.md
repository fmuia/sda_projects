# Business-applications closer deck (`apps/labs_slides.html`) — COMPLETE

The third deck: five real PyMC Labs engagements linked back to Ch 9 (synthetic control) and
Ch 13 (IV), closing the SDA Bocconi session. **DONE 2026-07-19: 14 slides, verified.**
Built to the `lecture-deck` + `slide-grammar` standards (adapted arc; see "Genre" below).
Plan of record: ~/.claude/plans/ok-so-organization-wise-mellow-church.md (approved).

## Files
- `apps/labs_slides.html` — the deck (2.3 MB, self-contained). Build: `make html-labs`.
- `apps/labs_slides_src.html` — editable template (edit this, then rebuild).
- `apps/build_labs_slides.py` — bake + inject: `{{labs.*}}` tokens, `/*__DATA__*/` bundle,
  `<!--SOURCES_ROWS-->` provenance table, `/*__MATHJAX__*/` from `apps/vendor/`.
- `apps/labs_deck_data.json` — **this deck's "shards"**: every number/quote pinned to a public
  source_url + retrieval date (2026-07-19) + the exact page quote. Numbers come from PyMC Labs
  blog posts (+ the Criteo dataset page), NOT notebook shards — book/build/ is not needed.
- `apps/labs_claims.yaml` + `apps/verify_labs_deck.py` — claims registry + verifier (geo-style,
  runs automatically inside `make html-labs`). 118 checks green.
- `scratchpad/assemble_labs_src.py` (+ 2 fragments) — ONE-TIME chrome splicer that generated
  labs_slides_src.html from iv_slides_src.html's chrome. The src is now canonical; re-running
  the assembler overwrites it from the fragments (only do this deliberately).

## Final state: 14 slides, 3 engagement moments, 4 live/SVG figures
Act I The claim (1-3): Title · purchase-order framing (qbig) · **Poll A "you are the consultant"**
  (Colgate triage; correct C = project the counterfactual; reveal eliminates A/B/D).
Act II The counterfactual, sold (4-5): Colgate ITS case (svgCounter schematic; 50% truth →
  94% CI 49-59%) · **open probe "what would break it?"** (reveal: overlapping launches, 64-76%
  vs 100%; ties to Ch 9 spillover).
Act III The loop (6-7): mmm_roas_lift inversion (svgRoas with "add two lift tests" toggle;
  93.39 vs 171.41) · HelloFresh + Bolt (svgLoop triangle; 60% variance cut; CausalImpact
  validation; TV-skepticism anecdote).
Act IV What it earns (8): **Poll B "price the engagement"** (Nürnberger CPL; correct C = more
  than 27%; reveal = GDPR mechanism + "Trust is not created by R² values" quote).
Act V The IV side (9-10): do-operator wedge demo (svgWedge DAG, two roads; large-gap-vs-zero,
  6.2% [-4.1% to 16.5%]) · industrial instrument supply (3 cards: thousands of tests / 1-10M
  obs per test, 22 s for 100M rows / Criteo 13,979,592).
Act VI Provenance (11-12): CausalPy (4 designs; launch post does NOT list IV — deck says the IV
  estimator "joined the package later") + pymc-marketing + webinar agenda · pattern synthesis +
  Decision Lab table ("No valid model found. Run a geo-holdout experiment.").
Close (13) · Backup Sources (14, table auto-generated from labs_deck_data.json at build time).

## Verification (all PASSED 2026-07-19)
1. `node --check` on the extracted main script: OK.
2. Headless `--dump-dom`: 14 slides, counter "1 / 14", **0 mjx-merror**, **0 JS errors**.
3. Screenshots read at 1440x900 for all 14 slides + dark-theme spot checks (6, 9). One layout
   fix applied: S6's figure shrunk (viewBox 240→200, sub line dropped) so bullet 3 sits above
   the fold.
4. Sweeps: **0 em-dashes** in src (en-dashes in "5–6 hours" are the page's own range typography,
   allowed); no raw currency inside math (no math beyond chrome in this deck).
5. `verify_labs_deck.py`: **118 checks, 0 warnings, 0 failures** — claim texts on data-t-anchored
   slides, DATA-vs-pin equality (ROAS), pin hygiene (url+quote+retrieved), token residue,
   automated em-dash sweep, 2600-char hard budget.
6. Poll end-to-end in a real browser (injected harness): Poll A select-wrong→reveal marks
   correct/wrong + shows answer; Poll B same; open probe reveals; ROAS toggle updates readout.

## Content rules specific to this deck
- **Never hand-type a number**: add a pin to `labs_deck_data.json` (text + source_url + quote +
  retrieved), reference it as `{{labs.key}}`, and register it in `labs_claims.yaml`. The build
  hard-fails on unknown tokens; the verifier fails on unpinned claims.
- Pinning corrections vs the earlier digest (do NOT reintroduce):
  - The do-operator post gives NO percentage for the naive gap ("a large apparent difference"
    only; the digest's "40%" is NOT on the page).
  - CausalPy's launch post lists 4 designs, no IV (verified absence).
  - Nürnberger is "more than 27%" over June-November (not "six months", not plain "27%").
  - The lift-test example values are unitless (no dollar signs) — deck omits them.
  - The mmm_roas_lift "direct opposite" sentence has an em-dash on the page; the slide re-renders
    it with a colon (claims check the dash-free fragments).
- The S4 chart is labelled **schematic** (badge + caption): deterministic formula series from
  build_labs_slides.py, a drawing of the method, not client data. Keep that labelling.
- The honesty quote ("more honesty... you see the uncertainty") is UNATTRIBUTED in the article —
  keep it credited to "the case write-up", never to a named person.

## If you revise
- Edit `apps/labs_slides_src.html`, then `make html-labs` (build + verify in one target).
- Verify harness: node --check; Chrome `--headless=new ... --dump-dom`; per-slide screenshots
  via `file://...#N` (1-indexed); poll harness pattern in the session notes.
- Timing: designed as a 10-15 min closer. If the session runs long, the cut is slide 5 (the
  open probe): the deck reads cleanly without it (S4's grading bullet keeps the honesty beat).
