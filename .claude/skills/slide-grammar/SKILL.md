---
name: slide-grammar
description: >
  Restyle an EXISTING HTML slide deck so every slide reads to one grammar: important concepts as
  one-sentence emphasized BOXES, details/definitions as one-sentence BULLETS, no running paragraphs,
  no em-dashes, and elements balanced to fit one screen. Changes FORM, not content: no concept,
  equation, figure, poll, or number is removed. Use when the user says "apply the slide grammar",
  "restyle / reformat / clean up the slides", "no paragraphs on the slides", "make deck X read like
  the geo-lift slides", "box the key points and bullet the details", or gives that feedback on a
  deck. This is the RESTYLE counterpart to the `lecture-deck` skill (which BUILDS a deck); use that
  one to author a new deck, this one to reformat an existing `apps/*_slides.html`.
---

# Slide grammar: restyle a deck to boxes + bullets

You are reformatting an existing, working deck (typically `apps/<name>_slides.html`, edited via its
`apps/<name>_slides_src.html` template and rebuilt). The prose is already good; the job is to make
each slide **instantly readable and well balanced** by converting paragraphs into a fixed grammar.
This was earned as explicit user feedback: a shorter paragraph is still a paragraph, and is wrong.
Do it **slide by slide with judgment**, never as a global find-replace.

## The grammar (apply to every slide)

1. **Important concept or punchline → a BOX, one streamlined sentence.** The deck's `.callout`
   family is the box: `.callout.key` (green) for the load-bearing idea, `.callout.watch` (orange)
   for a caution/tension, plain `.callout` (blue) otherwise. Keep the `.ct` label; the body is **one
   emphasized sentence**. Aim for ~1 concept box + ~1 punchline box per slide, no more.
2. **Details / definitions / points to stress → BULLETS, one sentence each.** Lead with a **bold
   2-4 word handle**, then a colon, then one sentence; add at most one short example clause. Never
   the claim + justification + implication mini-paragraph — the justification is the speaker's line.
   Example: `<li><b>The design:</b> a €75k campaign from week 40 for 20 weeks; the other 29 ran nothing.</li>`
3. **Text around figures and equations obeys the same rule.** Figure `.cap` = one line (what to look
   at); equation lead-in = one clause ("Fit the weights on the pre-period only:"); an equation read
   "in words" = one bullet. No prose blobs above or below a figure/eqbox.
4. **No running `<p>` paragraphs.** Every multi-sentence `<p>` becomes a box (if it is the idea) or
   bullets (if it is detail). Second-order nuance goes into a `details.mathfold` (its body is
   excluded from the length budget), not onto the visible slide.
5. **NO em-dashes (—), anywhere.** Use a colon after a bold handle, or a comma/semicolon/period/`·`.
   Sweep the whole file, not just the slides you touch (`grep -n $'—' file`), but rewrite each by
   hand — a few live inside equation `.lbl` labels and need care.
6. **Balance the elements on the available space — the slide should fit ONE screen.** Anchor with a
   concept box near the top, the figure in the middle, a punchline box at the bottom; use `.cols`
   (2-col) or `.cols.c32` (3:2) when content is comparative or to spend horizontal space instead of
   vertical. Cap ~4-5 visible bullets; push the rest to a fold. Verify by screenshot, not by eye.

## The box-split (the most common fix)

A callout that today wraps a `.ct` title + three sentences or a nested `<ul>` is a box doing three
jobs. Split it: the headline sentence **stays** in the box; the supporting sentences become
**bullets outside** the box; deep nuance goes into a `details.mathfold`. One box = one idea.

## What you must NOT break (verify after every slide)

- **Live-figure span IDs.** Charts fill `<span id="...">·</span>` and read control IDs via JS
  (`getElementById`, null-guarded). Preserve every `id=` and every `<span>` placeholder verbatim —
  keep the span even if you reword around it, or the number vanishes. Preserve the whole
  `<div class="fig">…</div>` block (svg id, `.controls`, sliders, buttons, readout).
- **`{{token}}` build placeholders** and **`data-t` / `data-sec` / `data-depth`** attributes.
- **Claim strings.** If the deck ships a `*_claims.yaml` checked by a verifier, some slides must
  contain exact `text:` substrings (usually numbers like `€75k`, `35%`, `12%`, `t=0,\dots,59`).
  Grep the claims file for the slide's `data-t` anchor before rewording; keep those substrings.
- **Equations, figures, polls, and every displayed number.** This is a reformat, not a rewrite.
- **The per-slide length budget** (the verifier's `CHAR_BUDGET`, e.g. 2600 visible chars, folds
  excluded). Reformatting reduces it; staying under is automatic, but confirm.

## Balancing figure-heavy slides (they overflow)

A hero chart (`viewBox` height ~250-260) renders ~460-480px tall; a full-width figure plus a
bottom reading row will push the payoff below the fold. Two clean fixes, pick per slide:
- **Figure-left / reading-right**: wrap the figure and its bullets+box in `<div class="cols c32">`
  (figure in the 3fr column, the reading in the 2fr). Best when the reading is a few bullets + a box.
- **Trim to fit**: drop a redundant `.cap` (if a live readout already says it), tighten a wrapping
  bullet to one line, fold a secondary bullet. Best when the figure must stay full-width (e.g. a
  wide interactive with sliders). Recover ~40-80px and re-shoot.

## Workflow (per act, then per dense slide)

1. **Map slides to titles**: `grep -n 'class="slide' <src>` — anchor by `data-t`, never by index.
2. **Reformat the source template** (`apps/<name>_slides_src.html` if the deck is generated;
   otherwise the HTML itself). Edit one slide's `<section>` at a time.
3. **Rebuild** if generated: `.venv/bin/python apps/build_<name>_slides.py` (it injects tokens,
   the DATA bundle, figures, MathJax). A stale/missing token or DATA key fails the build loudly.
4. **Verify**: `.venv/bin/python apps/verify_<name>_deck.py` if present (checks claims, N-map, and
   the length budget) — must end `0 failures`.
5. **Screenshot and READ every changed slide** (this is not optional — balance is only visible here):
   `"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new --disable-gpu \
     --hide-scrollbars --window-size=1600,1000 --virtual-time-budget=11000 \
     --screenshot=out.png "file://$PWD/apps/<name>_slides.html#<N>"` (hash `#N` is 1-indexed, title=1).
   Look for: content clipped below the fold (rebalance), a box with more than one sentence, a bullet
   that wrapped to a mini-paragraph, `≈ ≈` / doubled glyphs from a span that already carries the sign.
6. **MathJax + em-dash sweep**: `--dump-dom` and `grep -c mjx-merror` (want 0 per slide);
   `grep -c $'—' <src>` trends to 0 as you finish acts.
7. For a long pass, keep progress in the deck's `*_REVISION_PLAN.md` so it is resumable.

## Worked before/after

Before (a `<p>` blob):
> The second honest computation: subtract the crowd. Removing the cross-market average reveals a step
> of ≈ ⟨span⟩/week, noticeably larger than before/after. Same file, two defensible computations, two
> different answers, and nothing in the file arbitrates. Building the arbiter is what this lecture does.

After (bullet + box):
> `<li><b>Subtract the crowd:</b> remove the shared wave and the step is ≈ <span id="panelStep"></span>/week, larger.</li>`
> Box (`.callout.watch`, one sentence): **Two defensible computations, two different numbers, and nothing arbitrates — building the arbiter is the lecture.** → rewrite the em-dash: "…nothing arbitrates; building the arbiter is the lecture."

The span survives; the concept is boxed and emphasized; the details are one-line bullets; nothing is lost.
