# The book — architecture and chapter template

**Goal.** A self-contained, professionally typeset book (TOC, numbered chapters/sections/
equations, captioned figures and `booktabs` tables, bibliography, index) whose *results* come
from the executed notebooks. Plus standalone per-chapter PDFs from the same source. The
per-notebook `reports/*.pdf` (notebook transcripts) stay as they are — they are lecture
hand-outs. The book is the artifact.

**The reports are NOT the book.** `reports/*.pdf` are nbconvert renders: read-out prose,
`print()` blocks in monospace, JSON dicts, matplotlib titles. A book needs different content
organisation, not a better template.

## The rule that makes this safe

Rounds 2 and 3 of the depth upgrade were largely about prose that had drifted from output
(`€15.3k` vs `15.2`; "ESS in the hundreds" vs 3268; a decision-flipping "33 markets" vs "27").
Hand-copying numbers into a second narrative would industrialise that failure.

**So: every number in the book is injected from the executed notebook. Nothing is retyped.**

    notebooks (the lab)                         book/ (the artifact)
      cmp.report.value("nb07.sc_total", …) ──►  build/results.json ──► build/macros.tex
      cmp.report.table(df, "nb07.compare") ──►  build/tables/*.tex   (booktabs)
      cmp.report.figure(fig, "nb07.sc")    ──►  build/figures/*.pdf  (vector, book style)
                                                        │
                                          chapters/*.tex ──► xelatex ──► book.pdf + ch*.pdf

- A stale number becomes impossible; a **missing** one becomes a compile error (a feature).
- Macros are named `\nbSevenScTotal` style, auto-generated — never hand-written.
- Figures are re-emitted in **book style** (larger fonts, no titles — the caption does that
  work, consistent palette, vector PDF).
- **Results are SHARDED per notebook** — `build/results/nb07.json`, `nb08.json`, … A notebook
  writes only its own shard; `report.load()` merges them at build time. This is not tidiness: the
  chapters are built by many notebooks executing concurrently, and a single `results.json` would
  be a read-modify-write race in which one notebook's emit silently drops another's keys. Never
  reintroduce a shared store.

## Book structure

    Front matter: title, preface (who it is for, how to read), notation, reproduction
    Part I  · Foundations
       1. Potential outcomes, confounding, DAGs                      (nb00)
       2. Point estimate vs posterior — the spine of the book        (nb00 §7.1)
    Part II · Methods  (one chapter per notebook)
       3. Uplift targeting (01) · 4. Segment effects (02) · 5. Price elasticity (03)
       6. Funnel mediation (04) · 7. What to control for (05) · 8. Incrementality / MMM (06)
       9. Geo lift: synthetic control (07 + 07b real-data section)   <-- PILOT
      10. Staggered rollout: DiD (08) · 11. Threshold perks: RDD (09)
      12. Redesign: ITS (10) · 13. Endogenous exposure: IV (11 + 11b real-data section)
    Appendices: A the data-generating models · B the `cmp` API · C environments & reproduction
    Bibliography · Index

Real-data companions (07b, 11b) fold into their parent chapter as a "On real data" section —
they are not separate chapters.

## Uniform chapter template (scientific register, NOT notebook register)

    N.1  The decision                 the business problem, and what a wrong answer costs
    N.2  The data-generating model    display math; what is planted and why (or: the real dataset)
    N.3  Identification               estimand in potential-outcome notation; assumptions,
                                      named, formalised, discussed one by one
    N.4  The classical baseline       Step 0: the simplest correct estimator, point estimate
                                      + interval, correct SEs. No likelihood, no priors.
    N.5  The Bayesian model           likelihood + priors (justified), the sampler
    N.6  Diagnostics and validation   convergence, PPC, placebos, recovery, sensitivity
    N.7  Point estimate vs posterior  the honest comparison: where they agree (usually), where
                                      they differ and WHY, what Bayes bought and what it did not
    N.8  The decision, in euros       P(effect > cost) and the policy
    N.9  What can go wrong            the failure modes, demonstrated
    N.10 Takeaways
    (Notes: the runnable notebook, seeds, FAST/FULL — a short pointer, not a section.)

## The chapter epigraph — CONCRETE, never atmospheric

Every chapter opens with a short italic epigraph before N.1. **It must be specific enough that
it could only introduce THIS chapter.** The V0 pilot's epigraph was rejected as "handwavy and
vague", and the failure mode is worth naming precisely: it gestured at a mood ("the diagnosis is
precise, and it is the spine of this book") instead of stating what happened.

An epigraph must state, in three or four sentences:
1. **the concrete situation** — what was bought, in what quantity, at what price;
2. **the decision that hangs on it** — the euro question, with the number;
3. **the finding** — what this chapter actually discovers, stated as a result, not a promise.

It carries **real numbers, injected as macros** — an epigraph is prose and is therefore subject
to the no-retyped-number rule like everything else.

> **Bad (the V0):** *"This chapter builds it, prices it, and then discovers that the Bayesian
> interval around it is badly too narrow. The diagnosis is precise, and it is the spine of this
> book: the likelihood was wrong, not the paradigm."* — promises a finding, states none; the
> reader learns nothing they could disagree with.
>
> **Good:** *"A €300k television campaign ran in one of thirty markets. It has no control group
> and never will. Synthetic control prices the lift at €318k against a planted €339k — and then
> reports a posterior standard deviation of €21k for a quantity whose true sampling variability
> is €59k, so its 90% band covers the truth half the time. The error is not the prior; it is an
> iid likelihood applied to a random walk, and §9.7 measures it."*

Never write an epigraph that would survive being pasted into a different chapter.

## Register (what makes it a book, not a transcript)

- Third-person, scientific prose. No "we print below", no "read-out", no "How to read this".
- Results appear as **captioned tables and figures**, referenced by number in the text
  ("Table 9.2 shows..."), never as pasted stdout.
- Equations numbered and referenced. Assumptions stated as named, numbered environments
  (`\begin{assumption}`).
- Every claim that carries a number cites the macro; every figure has a caption that states
  the takeaway (the caption does the work the notebook's "read-out" prose used to do).
- Method provenance cited properly (Abadie; Bertrand-Duflo-Mullainathan; Imbens-Angrist;
  Pearl; Callaway-Sant'Anna; Müller on misspecified posteriors; Gelman).

## The intellectual spine (do not lose it)

The book's thesis, earned across all 14 chapters and stated in Ch.2:
- Classical and Bayesian answers **usually agree** (Bernstein-von Mises) — say so.
- Where Bayes lost, the cause was a **misspecified likelihood, not the paradigm** (Ch.9/nb07:
  an iid likelihood under-prices an autocorrelated 20-week sum 2.8x; Ch.10/nb08 erred the
  *opposite* way — proof it is specification, not paradigm).
- The classical robustness toolkit (HC/cluster/HAC/bootstrap/randomization inference) exists
  precisely to be **agnostic about the error structure**. That is why it wins when the model
  is wrong.
- The **prior does almost nothing** in these problems — the **likelihood is the whole ballgame**.
- What survives everywhere: `P(effect > cost)`, which the classical arm structurally cannot
  produce and which every euro decision consumes. Guidance: *use the posterior for the
  decision, and design-based inference for your confidence in it.*
