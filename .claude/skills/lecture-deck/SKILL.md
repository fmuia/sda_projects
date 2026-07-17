---
name: lecture-deck
description: >
  Build an interactive single-file HTML slide deck for one chapter of the causal-marketing-pymc
  book, to the standard set by apps/geo_lift_slides.html (Ch. 9, synthetic control): a 45-60 min
  MBA lecture that is business-first, poll-driven, live-figure interactive, LaTeX-typeset,
  self-contained, and whose every number is baked from the notebooks (never typed). Use when the
  user says "create the HTML lecture / slide deck for chapter X", "slides for chapter X like the
  geo-lift ones", "lecture deck for <topic>", or asks to extend/revise an existing deck in apps/.
  Also use to just PROPOSE (outline + polls + interactives, no build) when asked for a proposal.
---

# Lecture deck for a book chapter

Produce `apps/<chapter>_slides.html`: one self-contained HTML file, one slide on screen at a
time, ~40-50 slides, ~45-60 minutes of teaching. The canonical reference implementation is
**`apps/geo_lift_slides.html`** (Ch. 9). Do not design infrastructure from scratch: clone that
file's head (CSS + inline MathJax + helpers + deck nav) and replace the slides and figures.
Every rule below was earned through explicit user feedback on that deck; none is optional.

## Objectives (what a deck IS)

- **A business decision, dramatized.** The lecture opens with money on the line and a decision
  someone must sign, and every method exists only because the decision needs it. Statistical
  machinery is introduced at the moment the business question makes it necessary, never before.
- **An MBA course that is still a real data-science course.** Full equations, real derivations,
  honest diagnostics — but each is motivated, defined symbol-by-symbol, and paired with a plot.
- **Interactive.** The student can *do* things: simulate the world, fit the model by hand,
  break an assumption on purpose and watch the check fire. Prefer a slider to a paragraph.
- **Graded against truth.** Simulated data is a feature: the truth is planted, so every
  estimator gets marked. Then the deck must *close the sandbox honestly* and replay the method
  on real data against a design-based referee.
- **Poll-driven.** Class polls make students commit to a number/intuition BEFORE the reveal;
  the reveal teaches the mechanism, not just the answer.

## Inputs and process

1. **Inputs**: chapter name → `book/chapters/<name>.tex`, its notebook(s) via
   `book/COURSE_MAP.md`, and shard(s) `book/build/results/nbXX.json`. Read the chapter fully
   first; the deck's logic must be *adherent to the chapter's logic* (same arc, same numbers,
   same verdict), compressed and dramatized, not a new analysis.
2. **Propose before building** (unless told to skip): a one-screen outline of the act
   structure, the list of polls (question + options + correct answer + what the reveal
   teaches), and the list of interactive figures (what the slider does, what insight it
   produces). Get approval, then build.
3. **Bake the data** (see Data discipline).
4. **Build** by cloning the reference deck's infrastructure.
5. **Verify** (see Verification protocol) before declaring anything done.
6. For long builds, keep a resumable state file `apps/<chapter>_slides_REVISION_PLAN.md`
   (what is done / pending / gotchas) so a fresh session can continue.

## Narrative architecture

Adapt to the chapter, but this arc is the default and its invariants are mandatory:

- **Title** — the METHOD name huge (h1.method), the business question as subtitle, authors with
  credentials + emails, PyMC / PyMC Labs logos on white chips. No meta-chips, no keyboard hints.
- **Act I · The question** — the boardroom decision (the three questions stacked large:
  attribution / significance / worth-the-price), the raw data (live), the data-generating model
  (equations slide, THEN a separate live-simulator slide), a commit-to-a-number poll.
- **Act II · The method** — the counterfactual/missing-data framing; confounding on a graph
  (generic back-door primer with a marketing example BEFORE the chapter-specific DAG); naive
  estimators as explicit claims about the counterfactual, each formula in its own box, graded
  against truth; the chapter's estimator precisely (every symbol a bullet); what its
  constraints/assumptions buy (show the ablation: drop the constraint and watch it fail);
  a hands-on "fit it yourself" interactive; an identification checklist as a colored
  PASS / FAIL / UNTESTABLE table.
- **Act III · Is it real, how big** — first "how significance is normally tested and why that
  fails here", then the chapter's inference tool (poll first where possible), the interval,
  and falsifications — including a toggle that VIOLATES an assumption in a stylized world so
  the student sees the check fire. Close the act with the three-numbers summary and the
  "sentence that loses money".
- **Act IV · The decision in euros** — the margin trap (profit vs revenue is a P&L reading
  error, NOT a statistics problem — frame it exactly that way), break-even in both lift and
  iROAS language, the decision space vs price, and the **classical verdict, banked**: the
  action is decided here, before any posterior. This invariant ("classical decides, Bayes
  prices") is non-negotiable and mirrors the book's arm structure.
- **Bridge to Bayes** — show the gap, don't assert it: e.g. three distributions consistent
  with the same classical report giving three different P(pays). The posterior enters as the
  named object that fills the gap.
- **Act V · Adding a probability** — a ten-minute Bayes primer with a live prior×likelihood→
  posterior updater (define θ concretely; include a posterior-predictive toggle and
  eye-calibration benchmarks); the chapter's Bayesian model (equations + the actual PyMC
  code block); why the paradigms agree on the point (BvM); the decision integrals
  P(profit>c), headroom, VOI, each with every symbol defined; a buy-more-evidence poll with
  every variable (like k) defined in the question.
- **Act VI · On real data** — four beats: (1) close the synthetic case as a PROVED/OPEN table
  ending on the honest objection ("your method recovered a truth in a world built for it");
  (2) introduce the real dataset CAREFULLY with design facts and an EDA figure of raw data;
  (3) the referee comparison (model vs design-based benchmark); (4) the honest-failure /
  off-switch story if the chapter has one — "the most important output is 'I can't'".
- **The deliverable + takeaways** — the exact sentences said to the board, a board-numbers
  table, and 5-7 transferable cards.
- **Endnote(s)** — advanced diagnostics (model misspecification, calibration, the
  more-precise-route-not-taken) flagged `endnote-flag` "Advanced note", and the deck must be
  able to say truthfully: *the verdict above does not depend on this*.
- **Close** — a one-breath recap of the whole argument.

## Hard rules (each one was explicit user feedback — violating them fails review)

1. **No em-dashes.** Anywhere: prose, JS strings, SVG text, TOC names. Rewrite with `:`, `,`,
   `;`, `·`, or parentheses. SVG legends use line-swatch `<line>` elements, never dash glyphs.
2. **One concept per slide**, with its equations AND its plot. If a slide serves two concepts,
   split it. Dense supporting math goes in a `details.mathfold` box, never omitted.
3. **Nothing scrolls horizontally.** Equations auto-shrink via `fitEq()`; slides may scroll
   vertically (`.sbody`); short slides vertically center (`justify-content:safe center`).
4. **Every symbol defined where used.** Unpack multi-part equations into one eqbox per idea
   plus bullets naming each component. Equation-box `.lbl` annotations carry real content at
   readable size; anything decision-relevant is promoted to full prose.
5. **Never hand-type a number.** All quantities come from the baked JSON (`DATA`/`N`) or are
   computed live in JS from baked series. Headline numbers must match the book's text macros.
6. **Real LaTeX**: the inline MathJax build (tex-svg, ~2.1MB, `fontCache:'local'`), inherits
   `currentColor` so it is theme-correct. **No raw `€`/`$` inside math** — use `\text{€}`;
   a raw one renders "Math input error".
7. **Every plot has axis labels and a legend**, drawn in reserved margin bands (top band
   mT≈30 for legends) so nothing overlaps the data lines. Check overlaps in screenshots.
8. **Polls**: question with concrete numbers, 3-4 options, commit → reveal; the answer
   paragraph teaches the mechanism and names the concept the student just re-derived.
9. **Prose style**: bullets + bold key terms over paragraphs; the business questions stacked
   prominently on their own lines; punchlines stated plainly (a measurement mistake is called
   a measurement mistake, not dressed as statistics).
10. **Pass/fail semantics get colors**: `.tag.go/.test/.nogo` chips in tables and readouts;
    live readouts recolor with the verdict as sliders move.
11. **Self-contained single file**: no CDN, no network. Logos and images as base64 data URIs.
12. **Advanced material is demoted**: flagged endnote after the verdict, never mid-argument.

## Infrastructure (clone, don't rebuild)

From `apps/geo_lift_slides.html` keep verbatim: CSS variable system (light + dark via
`:root[data-theme]`), slide/deck/nav/TOC/theme machinery, `fitEq`/`fitSlide`, SVG helpers
(`el`, `COL`, `cssv`, `clr`, `lin`, `path`, `fmt`, `window.__redraw`), `.eqbox`, `.callout`,
`.poll`, `.fig`, `details.mathfold`, `table.mini`, title/author/logo styles, print CSS.

- **Figures** are vanilla-JS IIFEs, one per `<svg id="svgXxx">`, always guarded
  `const svg=document.getElementById(...); if(!svg)return;` — so half-built decks still load.
  Register every redraw in `window.__redraw` (theme changes re-render).
- **`COL()` palette keys**: blue, orange, green, grey, ink, navy, rule, red, faint, gold,
  muted. Use only these; a missing key silently renders black.
- **Data injection markers**: `const DATA = /*__DATA__*/{}/*__ENDDATA__*/;` and
  `const N = /*__NUMS__*/{}/*__ENDNUMS__*/;`. Inject with a python `re.sub` between the
  markers. **Re-inject after ANY change to the JSON** — a stale DATA with missing keys kills
  the whole script (deck shows "1 / 1", empty TOC).
- **CSS scoping trap**: plot sizing must target `.fig .canvas>svg`, never `.fig svg` — the
  broad selector grabs MathJax's inline SVGs in captions and blows a glyph up to full width.
- Logos: PyMC banner (github pymc-devs) + `pymc-labs.com/logo.svg`, base64 on white
  `.logo-chip` backgrounds so they work in both themes.

## Data discipline

- Write a bake script (scratchpad) that regenerates everything into
  `book/build/lecture_<chapter>_data.json` (put it in `book/build/`, NOT `build/results/`,
  which the book build guards). Pattern: same DGP seed as the notebook, `load_or_run` for
  cached MCMC fits, subsample posteriors to ~1200 draws (`sub()`), round series to 1dp.
- **Environments**: `.venv` = core/pymc6 (nb 00-05, 07, 07b); `.venv-legacy` = pymc5
  (nb 06, 08-11, 11b) — check the Makefile header, pick per notebook.
- Real-data loaders cache under `~/.cache/cmp/`. Shards `book/build/results/nbXX.json` are the
  source for headline numbers; cross-check every headline the deck states against the shard's
  `text` field (rounding drift is real: e.g. a baked 260.5 rendering as "€261k" against the
  book's 260 — patch the baked value to the book's displayed number and record the patch).
- Never hard-code BART-derived quantities (pymc-bart is not seed-stable): compute them in the
  bake and accept they move, or quote the shard.
- Calibrate any illustrative distributions/toy demos offline in the bake script and ship the
  curves as data; do not "eyeball" parameters in JS.

## Verification protocol (all five, every time, before "done")

1. **JS syntax**: extract the main `<script>` body to a file, `node --check`.
2. **Headless console + DOM**: `chrome --headless=new --enable-logging=stderr --v=1
   --virtual-time-budget=12000 --dump-dom` → assert slide count, counter "n / n", ZERO
   `Uncaught|TypeError|ReferenceError`, and ZERO `<mjx-merror` in the DOM (the string
   "Math input error" appears once inside MathJax's own source; only `mjx-merror` tags count).
3. **Screenshots you actually read**: `--screenshot --window-size=1440,900` per slide via URL
   hash `#n`; view every NEW or CHANGED slide. Look for: equation overflow, top-cramming,
   legend/label collisions, unreadable colors, broken interactives' default state.
4. **Sweeps**: grep the file (excluding the MathJax blob line) for `—`; regex-audit for raw
   `€` inside `\(...\)`/`\[...\]`.
5. **Numbers**: diff every headline number on the slides against the shard/book text.

Never re-execute notebooks with `jupyter nbconvert` (broken here); if a notebook must re-run,
use the nbclient harness and restore the kernelspec.

## Revising an existing deck

Feedback arrives as numbered per-slide comments. Map slide numbers to `data-t` titles FIRST
(grep `class="slide"`), keep a todo per item, and treat every comment as also implying its
generalization ("this annotation is too small" means fix the pattern everywhere). After any
slide insertion, all user-cited numbers shift: re-map before editing further. Update the
REVISION_PLAN state file as you go; it is what makes interruption survivable.
