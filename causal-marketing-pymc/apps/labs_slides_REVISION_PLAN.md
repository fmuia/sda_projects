# Business-applications closer deck (`apps/labs_slides.html`) — COMPLETE (rev 2)

The third deck: real PyMC Labs engagements linked back to Ch 9 (synthetic control) and
Ch 13 (IV), closing the SDA Bocconi session. Built to the `lecture-deck` + `slide-grammar`
standards (adapted arc; see "Genre" below).

## 2026-07-21 REVIEW ROUND 1 (Alexander, slide-by-slide critique) — DONE, verified
- **Title**: "Causal Inference, Invoiced" (too tacky) -> **"Causal Inference in the Wild"**;
  subtitle -> "Drawing from real PyMC Labs client engagements." (reviewer's wording).
  Footer + <title> tag renamed; "The pattern on every invoice" retitled to
  "The pattern in every engagement" (the invoice metaphor left with the old title).
- **Five examples -> three**: kept **Colgate-Palmolive** (carries the triage poll + the
  open probe), **HelloFresh** (one merged slide: the calibration loop AND the
  industrial-scale/instrument-supply story, so the Ch 13 link survives), **Nürnberger**
  (carries the estimate poll). CUT: Bolt (name remains only as a half-clause of
  pymc-marketing provenance), the streaming service, and the whole do-operator
  "wedge" slide. The mmm_roas_lift inversion slide STAYS: it is PyMC Labs' own tutorial
  demo (not a client engagement), the deck's only interactive, and the "why Ch 9 exists"
  bridge; flag to the reviewer, cuttable in round 2.
- **14 -> 11 slides** (10 presented + the Sources backup): Title · triage poll · Colgate ·
  probe · inversion · HelloFresh · Nürnberger poll · provenance · pattern · Close · Sources.
  The old "purchase order" framing slide was cut; its thesis lives in the triage poll's
  sub line and the Close box. Acts renumbered (old Act VI -> Act V · Provenance).
- **Pins**: 10 entries removed from labs_deck_data.json (do_* wedge facts, streaming
  scale facts, Bolt validation + honesty quote, HF inference-speedup + TV anecdote) so the
  auto-generated Sources slide stays truthful; recover from git history if cases return.
  Claims rewired: cast_of_clients/bolt_loop/honesty_quote/do_operator_null/scale_cards
  removed; hellofresh_loop + hellofresh_scale anchored to the new merged slide.
- **Re-verified (all)**: build + verifier **90 checks, 0 failures**; node --check OK;
  headless DOM 11 slides, counter 1/11, 0 mjx-merror, 0 JS errors; 0 em-dashes; polls A/B,
  probe, ROAS toggle green in the browser harness; all 11 slides screenshotted and read.

## 2026-07-21 REVIEW ROUND 2 (Alexander) — DONE, verified
- **Probe slide names its number**: "the previous slide's number" -> "The incrementality
  estimate you just saw (the share of the new product's sales that are genuinely new, not
  cannibalized) decides the launch review."
- **Widget mechanism explained**: two bullets between poll and figure: the model learns
  "normal growth" from the pre-launch window and extrapolates it; a second launch inside the
  window becomes part of "normal" (projection too fast -> under-credit), after the launch it
  inflates the observed line (-> over-credit).
- **Acts renamed to the client engagements** (data-sec + kickers + TOC): Opening ·
  Case 1 · Colgate-Palmolive (poll, case, probe) · Case 2 · HelloFresh (calibration warm-up,
  loop) · Case 3 · Nürnberger Versicherung (poll) · Closing (provenance, pattern, close) ·
  Backup.
- **The inversion slide got a home + provenance**: retitled "Why calibrate? A model alone can
  rank channels backwards", framed as Case 2's warm-up, sub states it is PyMC Labs' published
  calibration tutorial (badge "baked from the tutorial"); claims re-anchored to the new data-t.
- **Acronyms glossed at first use**: MMM ("a marketing-mix model (MMM) explains total sales as
  the sum of per-channel contributions..."), ROAS ("return on ad spend (ROAS, sales per unit
  of spend)"), CPL ("cost per lead (CPL)").
- Re-verified: 90 checks 0 failures; node --check OK; 11 slides / 0 mjx-merror / 0 JS errors;
  0 em-dashes; slides 4 (both widget states) and 5 screenshotted and read.

## 2026-07-21 round 2b: lift tests + incrementality defined — DONE, verified
- **Incrementality** defined at first use, as the Colgate slide's sub (its title uses the words):
  "Incremental: sales won from competitors or category growth. Cannibalistic: sales taken from
  your own products. The launch verdict is the split."
- **Lift test** defined at first use on the calibration warm-up, as a new "The experiment"
  bullet: nudge one channel's spend by a known amount, measure the sales change it causes:
  a small randomized ground-truth reading for that channel.
- ROAS figure compressed (viewBox 200 -> 172) so the 4-bullet slide still ends with the
  inversion callout above the fold. Re-verified: 90 checks 0 failures, 11 slides, 0 errors;
  slides 3 and 5 screenshotted and read.

## 2026-07-21 round 2c: provenance slide polish — DONE, verified
- CausalPy + PyMC-Marketing logos added as white .logo-chip rows (flat_logo.png from each
  package's docs/_static, downscaled to 120px height, PNG base64; dark-mode safe like the
  title chips).
- The "Provenance" callout box dropped; "The agenda test" bullet renamed "Webinars and
  content" (reviewer's wording). 90 checks green; slide screenshotted.

## 2026-07-21 addendum: second interactive (the "break it yourself" widget) — DONE, verified
- The probe slide (4) now carries a live figure (svgBreak): a checkbox + month slider inject a
  second product launch into the schematic world; the analyst's counterfactual is a pre-period
  trend+seasonality fit that is EXACT in the clean world (readout: measured/true lift = 100%,
  green) and bends once the ramp enters the fit window. At month -10 the readout lands at 68%,
  inside the real engagement's pinned 64-76%; near the window edge or post-period it OVER-credits
  (~180%/~124%): the number bends in either direction. No new numbers invented: the 64-76% / 100%
  pins annotate the widget; the schematic stays labelled schematic.
- The probe's watch-callout folded into the poll answer to make room; slide verified above the
  fold in both states (default + revealed/active). Deck stays at 11 slides; interactive figures
  now 2 (ROAS calibration toggle + this) plus the two polls and the probe.
- Re-verified: 90 checks 0 failures; node --check OK; 11 slides / 0 JS errors; widget states
  tested in the browser harness (off=100%, t6=68%, t14=181%, t20=124%).

## 2026-07-19 initial build — 14 slides, 5 examples, verified (superseded by rev 2)
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
  runs automatically inside `make html-labs`). 90 checks green (rev 2).
- `scratchpad/assemble_labs_src.py` (+ 2 fragments) — ONE-TIME chrome splicer that generated
  labs_slides_src.html from iv_slides_src.html's chrome. The src is now canonical; re-running
  the assembler overwrites it from the fragments (only do this deliberately).

## Final state (rev 2): 11 slides, 3 engagement moments, 3 live/SVG figures
Act I The claim (1-2): Title ("Causal Inference in the Wild") · **Poll A "you are the
  consultant"** (Colgate triage; correct C = project the counterfactual; sub line carries
  the deck's thesis).
Act II The counterfactual, sold (3-4): Colgate ITS case (svgCounter schematic; 50% truth →
  94% CI 49-59%) · **open probe "what would break it?"** (reveal: overlapping launches, 64-76%
  vs 100%; ties to Ch 9 spillover).
Act III The loop (5-6): mmm_roas_lift inversion (svgRoas with "add two lift tests" toggle;
  93.39 vs 171.41) · HelloFresh merged slide (svgLoop triangle; 60% variance cut; panel
  calibration agenda; thousands of concurrent tests, 5–6 h → 5–6 min; Criteo 13,979,592 as
  "this regime"; instrument-supply callout = the Ch 13 link).
Act IV What it earns (7): **Poll B "price the engagement"** (Nürnberger CPL; correct C = more
  than 27%; reveal = GDPR mechanism + "Trust is not created by R² values" quote).
Act V Provenance (8-9): CausalPy (4 designs; launch post does NOT list IV — deck says the IV
  estimator "joined the package later") + pymc-marketing (Bolt PR half-clause) + webinar
  agenda · "The pattern in every engagement" synthesis + Decision Lab table.
Close (10) · Backup Sources (11, table auto-generated from labs_deck_data.json at build time).

## Verification (rev 2, all PASSED 2026-07-21)
1. `node --check` on the extracted main script: OK.
2. Headless `--dump-dom`: 11 slides, counter "1 / 11", **0 mjx-merror**, **0 JS errors**.
3. Screenshots read at 1440x900 for all 11 slides (rev-1 pass additionally spot-checked dark
   theme; chrome unchanged since).
4. Sweeps: **0 em-dashes** in src (en-dashes in "5–6 hours" are the page's own range typography,
   allowed); no raw currency inside math (no math beyond chrome in this deck).
5. `verify_labs_deck.py`: **90 checks, 0 warnings, 0 failures** — claim texts on data-t-anchored
   slides, DATA-vs-pin equality (ROAS), pin hygiene (url+quote+retrieved), token residue,
   automated em-dash sweep, 2600-char hard budget.
6. Poll end-to-end in a real browser (injected harness): Poll A reveal marks correct/wrong +
   shows answer; Poll B same; open probe reveals; ROAS toggle updates readout.

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
- Timing: designed as a ~10 min closer at 11 slides. If the session runs long, the cut is
  slide 4 (the open probe): the deck reads cleanly without it (the Colgate slide's grading
  bullet keeps the honesty beat).
