---
name: chapter-magnificence
description: >
  Bring a causal-marketing-pymc book chapter to "magnificence" and verify it fits the whole.
  Drives one chapter (its .tex AND its companion notebook) to the full bar — all five quality
  axes, plus simple first-read prose, a natural logical flow, a plot for every concept and
  equation, a dedicated appendix section per statistical concept, consistent notation, and a
  contained "what Bayes adds" flavour — then checks notation/voice/cross-ref COHERENCE against
  the chapters already finished and COVERAGE against book/COURSE_MAP.md. Use when the user says
  "make chapter X magnificent", "bring chapter X to the bar", "polish/upgrade/finish chapter X",
  "magnify chapter X", "prep chapter X for the lecture", or asks to assess a chapter against the
  magnificence standard. Also use to just ASSESS (report the gap without editing) when asked.
---

# Chapter magnificence

Bring one chapter of the SDA Bocconi causal-marketing book to the standard below, keep it
coherent with the chapters already done, and keep the whole book's coverage honest against the
course. The book is the companion to Michele Russo's *Causal Inference & XAI for Business*; the
immediate priority is the two guest-lecture chapters, **Ch. 9 (synthetic control)** and
**Ch. 13 (IV)**.

## Inputs

- **Which chapter** (e.g. `geo_lift` / Ch. 9, `iv` / Ch. 13). Resolve file: `book/chapters/<name>.tex`
  and notebook(s) via `book/COURSE_MAP.md`.
- **Mode**: `assess` (report the gap, no edits) or `magnify` (assess, then do the work). Default
  `magnify`. If the user only asks "is chapter X magnificent / assess X", use `assess`.

## Before you touch anything — load the standard

Read, in this order, and hold them as the rubric:
1. `book/BOOK_SPEC.md` — architecture, the no-retyped-number rule, the chapter template, the epigraph rule, the intellectual spine.
2. `book/COURSE_MAP.md` — what this chapter must cover, its Bayes-flavour note, its status, the coverage gaps.
3. `book/NOTATION.md` — the canonical symbols; the deliberate exceptions; the cross-chapter clashes to avoid.
4. `book/REVISION_PLAN.md` §0 (the five rules R1–R5) and §1 (VERIFIED CORRECT — do not touch) and the chapter's own section.
5. `book/LIST_TO_FIX.md` — the eight principles (2026-07-14 "Ch. 1 REBUILT" entry) and any open item touching this chapter.
6. Relevant `memory/` notes (env split, depth bar, BART non-reproducibility, cache-key bug, likelihood fixes).
7. The chapter `.tex` in full, and its companion notebook(s) in full.

Never restate these standards inside the chapter; apply them.

---

## The magnificence bar

A chapter is magnificent only when it clears **all** of the following. Score each item
pass / partial / fail with a one-line reason; the assessment output is this checklist filled in.

### The five axes (the user's axes)

1. **Quality & excellence.** Every number injected from the executed notebook via `cmp.report`
   — nothing hand-typed (BOOK_SPEC's rule; the `\input{build/...}` macros/tables/floats).
   No stale numbers; the offprint compiles clean. Professional register: captioned floats
   referenced by number, numbered equations, named/numbered `assumption` environments, cited
   provenance. Concrete epigraph carrying real macro numbers (never atmospheric).
2. **Depth & coverage.** Covers everything in the chapter's **Must cover** row of COURSE_MAP.md,
   at or beyond the course's depth. Identification stated in potential-outcome notation with each
   assumption named, formalised, and marked testable/untestable. Classical baseline done *first*
   and completely (the course is frequentist — this is the shared ground). A `What can go wrong`
   section with the failure modes demonstrated. A real-data section graded against a benchmark.
3. **Business value.** Decision-first: opens on the decision and what a wrong answer costs;
   closes in euros with `P(effect > c)`, the policy, VOI, and a headroom curve. The euro
   through-line never goes dormant in the technical middle.
4. **Technical correctness.** Estimators, SEs and diagnostics are the right ones and are
   verified (cross-checked in code where load-bearing; matches published data where real).
   Metrics are **out-of-sample / honest** where the method demands it (the course teaches
   honesty/cross-fitting/holdout — do not ship in-sample CATE metrics). No claim rests on a
   non-reproducible number (BART: cite the injected value, never argue a BART delta in prose).
5. **Pedagogical value.** Teaches, does not report: every diagnostic gets *what it is → the math
   → how it could fail → what it says here*. Define-then-use throughout. `intuition` and `recap`
   boxes used sparingly and well.

### The craft requirements (new, and non-negotiable for the guest chapters)

6. **Simple, first-read prose (R1).** Short, plain-English sentences. No clause-stacking, no
   em-dash pileups, no sentence a reader must re-read. State every implication — never make the
   reader infer the "so what". A domain-literate MBA should follow it at first read.
7. **Natural logical flow.** The chapter and *each section* march in one obvious order: decision →
   setup/notation → identification → classical estimator + result → diagnostics → what Bayes adds
   → the euro decision → what can go wrong → real data → takeaways. Every section opens by saying
   what it will establish and closes having established it. No forward-reference to an undefined
   term (run a first-use-vs-definition sweep).
8. **A plot for every concept and every equation.** Each displayed equation and each named
   concept has a figure that *shows* it, with the stated number readable off the plot. Figures are
   emitted from the notebook via `cmp.report.figure` in book style and `\input` as floats — never
   hand-drawn, never uncaptioned. The caption states the takeaway.
9. **A dedicated appendix section per statistical concept.** Every statistical concept the body
   introduces gets its own `\subsection*{\thechapter.A.k\quad ...}` in the per-chapter appendix,
   expanded with a worked example AND a plot. The body keeps the plain statement + the euro
   result + a pointer; the appendix carries the derivation, the example, and the figure. (Ch. 13
   already has 13.A.1–13.A.12; Ch. 9's appendix is under-built — bring it up.)
10. **Consistent notation.** Conforms to `book/NOTATION.md`. No symbol means two things a reader
    meets close together. Document any field-standard exception in NOTATION.md rather than drifting.
11. **Bayes as a contained flavour (R4).** The classical/design-based method is the star (the
    course is frequentist). Bayes lives in one clearly-bounded "What Bayes adds" section (or a
    liftable block) — it earns its place by supplying `P(effect > c)` and honest uncertainty, and
    it never becomes the chapter's headline or its middle third. Present it calm and forward
    (classical → Bayesian → short discrepancy note), never adversarial, never erratum-voiced.
12. **Companion notebook is magnificent and marimo-ready.** The notebook mirrors the chapter's
    flow, emits every macro/table/figure the chapter `\input`s, runs FAST and FULL, and is
    structured so results are **loaded/cached, not sampled live** (PyMC cannot run in the browser;
    the marimo lecture version must show precomputed posteriors). No number lives only in prose.

---

## Process

### Phase 1 — Assess (always)
Fill in the 12-item checklist above for the chapter as it stands, pass/partial/fail with reasons.
For a large chapter, fan out read-only subagents (one per axis or per section) to gather evidence
in parallel, then synthesise. Produce the **gap list**: the concrete, ordered set of changes to
reach the bar. If mode is `assess`, stop here and emit the report.

### Phase 2 — Plan
Turn the gap list into a work plan separated into:
- **Prose-only** edits (flow, simplification, define-then-use, notation, moving derivations to the
  appendix, the Bayes-flavour rebalance). These land first and need no re-execution.
- **Notebook edits** that move or add numbers/figures (new concept plots, appendix example
  figures, out-of-sample re-scoring, a new macro). These require re-execution; batch them.
State which env each notebook needs (`cmp-core` vs `cmp-legacy`, per COURSE_MAP / memory) and
whether `CMP_REFIT=1` / `CMP_FULL` / `CMP_REAL=1` is required.

### Phase 3 — Execute prose
Rewrite for R1 flow and simplicity; enforce define-then-use; move every derivation into a per-
concept appendix subsection; add `intuition`/`recap` where they earn it; rebalance Bayes into one
contained section; fix notation to NOTATION.md. Keep every existing injected macro; do not hand-
type any number.

### Phase 4 — Execute notebook + figures
For every concept/equation still missing a plot, add a notebook cell that computes it and emits
`cmp.report.figure(...)` (and `cmp.report.table` / `cmp.report.value` as needed) under a stable
key; `\input` the float where the concept is introduced and again (a different view or the worked
example) in its appendix section. Wire any out-of-sample re-scoring the honesty check demands.
Re-execute the affected notebooks in the right env (nbclient + restore kernelspec — plain
`nbconvert` is broken here, per memory), regenerate `build/macros.tex`, and rebuild.

### Phase 5 — Coherence check (against already-magnificent chapters)
Read the chapters marked `magnificent` in COURSE_MAP.md and verify this chapter:
- uses the **same notation** for every shared symbol (NOTATION.md);
- uses the **same voice and register** (plain, forward, no erratum voice, boxes used the same way);
- has **consistent cross-references** (every `\cref`/`\Cref` resolves; forward promises are
  redeemed; a concept defined elsewhere is cited, not redefined or contradicted);
- makes **no claim that contradicts** a finished chapter (e.g. the shared "classical & Bayesian
  usually agree; where Bayes lost it was a misspecified likelihood/prior, not the paradigm" spine);
- reuses **shared decision framing** (`P(effect>c)`, VOI, headroom) identically.
Report every mismatch and fix it (or, if the *other* chapter is wrong, log it in LIST_TO_FIX).

### Phase 6 — Coverage check (against COURSE_MAP.md)
Confirm the chapter now covers its **Must cover** row. For any course topic it still omits, either
add it, relocate it (note where), or record it under COURSE_MAP's coverage-gaps with a decision.
Do not silently drop a topic the students saw in the lecture.

### Phase 7 — Verify and report
Build the offprint (`book/build.py` / the chapter's `\includeonly` path) and confirm it compiles.
Then emit the report (below) and update the chapter's **Status** in COURSE_MAP.md
(`in-progress` → `magnificent` only if every item passes).

---

## Guardrails

- **Never hand-type a number.** Every figure in prose is a `\input` macro from the executed
  notebook. A missing macro is a compile error — that is the feature, not a reason to type it.
- **Never write a BART-derived literal or argue a BART delta in prose.** `pymc-bart` is not seed-
  stable here; cite the injected value and the computed "too close to call" verdict.
- **After any `dgp.*` change, re-execute with `CMP_REFIT=1`** (the fit cache is data-blind — see
  LIST_TO_FIX). Prefer `nbclient` + kernelspec restore over `nbconvert`.
- **Do not touch the items in REVISION_PLAN §1 (VERIFIED CORRECT)** except to preserve them.
- **Bayes stays a flavour.** If a magnify pass makes the Bayesian section the headline again,
  it has failed requirement 11.
- **Keep offprints standalone.** Per-chapter appendix prints at the chapter's end.

## Output report

```
# Magnificence report — Ch. N (<name>)

Verdict: <magnificent | near (k gaps) | not yet (k gaps)>

## Scorecard (12 items)
<item>: pass|partial|fail — <one line>
... ×12

## Gap list (ordered) / Changes made
P1 ... / [done] ...
P2 ... / [done] ...

## Coherence with finished chapters
<notation | voice | cross-refs | no-contradiction | shared framing>: ok | <fix>

## Coverage vs COURSE_MAP
Must-cover: <complete | missing: ...>
Course topics deferred/relocated: ...

## Build
offprint: <compiles | error>
COURSE_MAP status set to: <...>

## Notebook / marimo readiness
<cached-results | live-sampling-to-fix>; macros regenerated: y/n
```
