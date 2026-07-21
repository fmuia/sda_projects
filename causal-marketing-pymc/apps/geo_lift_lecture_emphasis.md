# Unified Lecture — Narrative & Slide-by-Slide Emphasis (Management-Class Version)

**Audience:** general management on an MBA course, *not* analysts. Rule for every slide: lead with the
decision, keep the plot on screen, push the math into a folded subsection at the bottom. This file is
the presenter cheat-sheet AND the build spec for merging the two decks.

**What this deck is:** the two existing decks fused into ONE continuous arc — the labs "Causal Inference
in the Wild" deck (`labs_slides.html`) moved to the FRONT as the business hook, handing off to the
**SHORT** geo-lift deck (`geo_lift_sh.html`, the classical-arc business-first version, Acts I–IV only —
NOT the full 44-slide deck) as the deep worked example. Target ~55 min, 39 slides + a sources backup. A third part
(Instrumental Variables, short deck in progress) will be appended later to make a 1.5h session, so leave
the session-level close open (see FINALE).

**The one-line spine of the whole session** (return here whenever a slide feels lost):
*"Every marketing decision is a counterfactual — what would have happened anyway? — anchored by an
experiment, and decided in euros with its uncertainty on the table. Real clients buy exactly that; here
is how you build one."*

**The three-beat rhythm that repeats in every case and every act:** counterfactual → calibration →
decision-under-uncertainty. Part 1 shows real companies living it; Part 2 builds one, end to end, on the
hardest case and stops at the honest classical verdict ("measure first"). NOTE: the short geo deck is
CLASSICAL — it delivers an interval and a straddle, not a full P(pays). The probability layer is previewed
in the Part 1 cases (Colgate's 49–59% interval) and is the forward promise the later Bayesian/IV material
completes; do not sell "78% chance it pays" as if this deck derived it.

---

## Legend (markers used on every slide)

- 🎯 = the ONE thing to land
- 💬 = a sentence worth saying close to verbatim
- 📐 = the math to FOLD (push to a collapsed subsection at the bottom; reveal only if asked)
- 🖼 = a meme / cartoon / figure to engage the room (all OPTIONAL, all tasteful — swap freely)
- ✋ = a poll or open-floor engagement beat
- ⏭ = skip / go fast for managers

---

## THE REWIRING RULE (critical — read before touching slides)

Labs was authored as a CLOSER. Moved to the front, every backward callback becomes a forward promise.
Fix these at slide-adjust time (they are the whole reason the merge needs care):

| Labs currently says (callback) | Unified deck should say (teaser) |
|---|---|
| "the counterfactuals you built today" | "the counterfactual we build in the next 40 minutes" |
| "this morning's method" (synthetic control) | "the method we learn next" |
| "the IV estimator you ran this afternoon" | "the IV method we close the session with" (Part 3) |
| "the Criteo experiment you saw this afternoon" | "an experiment like the one we meet on real data later" |
| "the sentence both of today's lectures opened with" | "the sentence this whole session is about" |
| "nb10's / nb04's machinery" (notebook refs) | drop the nb numbers for managers; name the idea |

And the BONUS of the new order: the geo slides may now CALL BACK to the opening cases (Colgate at the
counterfactual, the second-launch probe at SUTVA, HelloFresh at "measure it"). Those callbacks are marked
🔗 below — they are the glue that makes this one lecture instead of two.

---
---

# PART 1 — CAUSAL INFERENCE IN THE WILD (the hook · ~10 min)

*Purpose: earn attention before any math. Who is talking (one slide), then real companies, real money.
Plant the three concepts the geo lecture then builds properly: the counterfactual, calibration-by-experiment,
uncertainty on the table.*

### 1 · Title (session opener)
- 🎯 Set the frame, modestly — no "by the end you will…" promises. These are questions real companies
  paid to have answered; today we walk through how that is actually done.
- Authors: use the **geo-lift author descriptions** verbatim. Francesco Muia — "PhD in Theoretical
  Physics, EMBA. Consultant for PyMC Labs and Brown University.", email **francesco.muia@ai-and-analytics-solutions.com**.
  Alexander Fengler — "PhD in Computational Cognitive Science. Postdoc at Brown University, consultant
  for PyMC Labs.", email alexander.fengler@pymc-labs.com. Keep the PyMC / PyMC Labs logo chips.
- 💬 "Three real companies, one hard question each. Same question underneath all three."
- 🖼 Optional cold-open image: a boardroom / "where's the ROI?" cartoon. Low-key; the poll is the real hook.

### 2 · PyMC Labs: what we do (NEW slide)
- 🎯 One minute, two beats. Beat 1 — who is talking: a Bayesian modeling consultancy that builds custom
  decision-making models where off-the-shelf tools fall short, AND maintains the open-source libraries the
  field runs on (PyMC, PyMC-Marketing, CausalPy). Beat 2 — how it makes money: senior modeling expertise,
  not seats or software licenses; revenue is services-led; open source is the top of the funnel (the
  libraries build trust and reach, the consulting monetizes the expertise behind them).
- Table (the three engagement shapes): **Project consulting** = fixed-scope build of a custom model (an
  MMM, a demand forecaster, a pricing model) for a company with a specific high-value decision problem ·
  **Advisory / retainer** = ongoing access to modelers guiding an in-house team · **Enablement & training**
  = workshops and embedded upskilling for analytics teams standardizing on PyMC.
- 💬 "Small teams of senior people, no junior-heavy pyramid: we start from the client's actual decision,
  encode the domain knowledge and the uncertainty explicitly, and hand back models the client can own and
  extend — not black boxes."
- Clients: no logo wall — name the engagements of THIS session (Colgate-Palmolive, HelloFresh, Nürnberger
  Versicherung; Bolt in a half-clause): "you meet three of them in the next ten minutes."
- 📐 FOLD: areas of interest (MMM & media measurement, causal inference, demand forecasting & pricing,
  experimentation at scale) + sectors (consumer/CPG, retail & e-commerce, tech, finance).
- ⏭ Keep to ~60–75s. It is context, not the hook — land it and hit the poll.

### 3 · Poll: you are the consultant (Colgate call) ✋ THE HOOK
- 🎯 The best hook in the deck BECAUSE they can't answer it yet. Colgate launched nationally, no holdout,
  no test market — which tool? Let them commit (A/B / DiD / project the counterfactual / instrument).
- ✋ Run it live. Most rooms split; that split IS the lesson. Reveal **C**: nothing to randomize, no control
  region, no instrument for a shelf that changed everywhere — what remains is *fit the world before the
  launch, project it forward, read the gap*.
- 💬 "If you're not sure — good. That gap is exactly what this session is for."
- 🖼 "This is fine" dog (national launch, no holdout, everything on fire) — the CMO's actual situation.
- 📐 Nothing. Keep it pure business.

### 4 · Colgate — incremental, or cannibalistic?
- 🎯 PLANT THE COUNTERFACTUAL (the spine of Part 2): the deliverable is *the world without the launch* —
  a number that exists in no file. Incremental (won from rivals/category) vs cannibalistic (stolen from
  your own shelf); the launch verdict is the split.
- 💬 Read the brief in their words: "estimate what the counterfactual sales would have been if the new
  product had not been introduced." That sentence is the whole course in one line.
- 🎯 The grading contract: on simulated data the model recovers a planted 50% as a 94% interval of 49–59%
  — "recover a known truth first, then trust it on the real thing." (This is exactly the geo deck's honesty.)
- 🖼 Two-Spider-Men-pointing meme: "sales with the launch" vs "sales without it" — only one is ever observed.
- 📐 FOLD: "multivariate Bayesian interrupted time series / nested-logit choice model." Name-drop only if asked.
- 🔗 Forward: "we build this exact object, slider by slider, in Part 2."

### 5 · What would break it? ✋ open floor + live widget
- 🎯 PLANT SPILLOVER (pays off at geo SUTVA slide): the counterfactual can absorb the very effect it should
  isolate. Ask the room — as Colgate's CMO — to name one real event that breaks the estimate.
- ✋ 2-minute open floor, THEN reveal "a second launch": the model reported 64–76% against a planted 100%.
  💬 "An honest consultancy prints its misses in the same post as its wins."
- 🖼 Live "break it yourself" widget already in the deck: slide a second launch into the window, watch the
  read bend both ways (under- and over-credit). Let a student drive it.
- 📐 FOLD: pre-period trend+seasonality fit mechanics; keep only "the model learns 'normal' before the launch."
- 🔗 Forward: "hold onto 'a leak into the control' — it comes back as the one assumption we can't test."

### 6 · Why calibrate? A model alone can rank channels backwards ✋ live toggle
- 🎯 PLANT CALIBRATION (the middle beat of the spine): fit on observational spend alone, the model ranked
  channel x1 above x2 — 93.4 vs 171.4, the exact opposite of the truth. 💬 "A confident model, ranked
  backwards. Nothing on the dashboard tells you."
- 🖼 The "overfitting / drawing the target around the arrow" meme, or the classic "correlation ≠ causation"
  gag — a model fit to history that has learned the wrong thing.
- ✋ Live toggle already in the deck: "add two lift tests per channel" flips the ranking to the truth. Drive it.
- 💬 "The experiment is the model's anchor. Hold that thought — the entire second half is about building
  the right anchor when you only get ONE."
- 📐 FOLD: what an MMM is (sum of per-channel contributions); ROAS = sales per unit spend; lift test =
  nudge one channel, measure the caused change. One line each, folded.

### 7 · HelloFresh runs the loop, at industrial scale
- 🎯 The pattern at scale: an always-on model, disciplined by a stream of experiments — a 60% cut in
  prediction variance. This is the "calibration is the product, not a luxury" beat.
- 💬 "The experiments a company already runs are its instrument supply." ← this line is the bridge to
  Part 3 (IV): a randomized encouragement is the instrument for the exposure you cannot randomize.
- 🖼 A "flywheel" / loop cartoon (model → experiment → better model). The deck already has the svgLoop triangle.
- 📐 FOLD: the throughput numbers (thousands of concurrent A/B/ABC/ABCD tests, 5–6h→5–6min, Criteo 13.98M
  users) — say "industrial scale," fold the digits.
- ⏭ Fast slide (~45s): the loop picture carries it.

### 8 · Poll: price the engagement (Nürnberger) ✋
- 🎯 The business payoff of getting attribution right: a German insurer swapped last-touch for a funnel-aware
  causal model and drove cost-per-lead down **more than 27%**. Poll the number first (they'll under-guess).
- 💬 The mechanism is the lesson: under GDPR, journeys looked artificially short, so last-touch under-credited
  the upper funnel and budget chased the wrong clicks. 💬 "Trust is not created by R² values. It is created
  when business reality matches model expectations." (Say it slowly — it's the client's own bar for belief.)
- 🖼 "Corporate needs you to find the difference between *revenue* and *profit* / *last-touch* and *causal*"
  — they're not the same picture. (Sets up the margin trap in Part 2.)
- 📐 Nothing on the slide; keep it a business win.

*(The old labs "tools were the product too" provenance slide MOVES to the finale — slide 37. With the new
slide 2 covering who PyMC Labs is, keeping it here would say "open source" twice in five minutes.)*

### BRIDGE — Part 1 → Part 2 (say this out loud, ~20s)
💬 "Every one of those three was the same object: a counterfactual, calibrated by an experiment, priced as
a probability. Colgate built it in *time*. But the hardest, most common version is one market, no
experiment, and real money on a national rollout. For the next 40 minutes we build that one — start to
finish — and you'll see every idea from these three cases arrive with its proper name."

---
---

# PART 2 — SYNTHETIC CONTROL (the deep dive · ~44 min)

*The SHORT geo-lift deck (`geo_lift_sh.html`): the classical arc, Acts I–IV, business-first, math already
folded into `<details>` blocks. It keeps its full short-deck arc and STOPS at the classical verdict
("measure first"). Each act now calls back to Part 1's cases (🔗). Slide numbers below are the unified deck.*

### 9 · Part 2 divider / Title — "Synthetic Control"
- 🎯 Reset the frame: "One treated market, no experiment, €4M on the line: did the campaign work?" Keep the
  hero figure. 💬 "Colgate at least had a clean before-and-after. Take even that away — one market, no
  control, no experiment. This is the general case, and it's the most common one."

## ACT I — The question (~9 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 10 | The boardroom question | 🎯 Three questions IN ORDER: attribution → significance → decision. The metro was CHOSEN, not randomized — that's why it's hard. 💬 "Most companies jump to question 3 with an unchecked answer to question 1." 🔗 "Colgate's launch was national; here it's one metro — same missing number." | 📐 "unbiased" fold-out (only if asked). |
| 11 | The data (live) | 🎯 The counterfactual: the one number in no file — what the metro would have sold anyway. Show live that the naive bump changes when you subtract the crowd. 🖼 Rooster-takes-credit-for-sunrise ("the campaign made sales rise"). | 📐 The three technical readings, folded. |
| 12 | Poll: the 12% bump ✋ | 🎯 Naive before/after isn't "roughly right + noise": the tide can HIDE a real effect (as here) or inflate a fake one. Run the poll — commitment makes the teaching moment. | — |
| 13 | Potential outcomes | 🎯 Causal effect = gap between two histories; only one is observed. The 2×2: 3 cells are data, 1 is missing, every method fills that cell. Per-week vs 20-week total are different targets; the €4M rides on the total. 🖼 Doctor Strange "14,000,605 futures, we observe one." | 📐 Potential-outcome notation box — fold. |
| 14 | The data-generating model | 🎯 ONE honest confession: data is simulated SO every method can be graded against a known truth (~€284k) — the same recover-the-truth contract as Colgate. | 📐 The whole equation. "Four ingredients incl. per-market sensitivity" and move. |
| 15 | Simulate the world (live) | 🎯 ONE slider (macro shock): turbulence destroys before/after. 💬 "Compared to what?" 🖼 optional: stormy-sea "a rising tide lifts all boats" visual. | ⏭ Other sliders; the full "what sliders teach" list. |

## ACT II — The counterfactual (~11 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 16 | Abadie's idea: the synthetic twin | 🎯 THE core idea: no twin exists, so blend markets into one. Twin matches RESPONSES to shocks, not levels → survives storms. Anchors: Meta GeoLift, Google geo tools. 🖼 "assemble a twin from parts" cartoon, tasteful. | 📐 Factor-model equation; pedigree fold-out (one clause). |
| 17 | The estimator | 🎯 3 business facts: (1) fitted ONLY pre-launch = no peeking, (2) weights are a readable recipe (40%+32%+17%), (3) effect = subtraction. 🔗 "The honest, weights-on-the-table version of what Colgate's model did in time." | 📐 argmin / simplex formulas — folded on the slide. |
| 18 | Inside the convex hull (live) | 🎯 Coffee+milk can't make orange juice: a blend can't reach outside the donors' range → the method can REFUSE. 💬 SIGNATURE MANAGEMENT LINE: "Ask any vendor — when does your method refuse to answer? If 'never', walk away." 🖼 big red OFF switch / "computer says no". (This is where the short deck teaches the off-switch.) | 📐 "simplex", "hull" — use the demo, not the words. |
| 19 | What the constraint buys (live) | 🎯 Better fit to the past ≠ better model. Drop the constraint: OLS fits tighter, predicts worse, uses absurd weights (−80%). 💬 "Anyone selling a model on past fit is selling the wrong metric." 🖼 the overfitting meme (squiggly line through every point). | 📐 n_eff (inverse Herfindahl) block — fold. |
| 20 | Why not just forecast it? | 🎯 Forecasting ≠ counterfactual: "what comes next" vs "what would have happened in a world that never happened." You cannot cross-validate the counterfactual → pick defendable assumptions, not demo accuracy. Auditability is a business feature. 🖼 confidently-wrong-AI / "trust me bro" robot. | The sweep numbers (one clause: "clearly worse across 24 worlds"). |
| 21 | Every shortcut is an assumption | 🎯 KEY SLIDE of Act II. Every method = a hidden claim about the counterfactual. Live dials: DiD dies when markets react differently. 💬 "A wrong method does not look wrong, and more data does not fix it." | 📐 The formulas — point at the dials instead. |
| 22–23 | Before DiD: two one-difference estimators / When does DiD work? (algebra) | ⏭ Compress BOTH to: before/after fails when the world moves; controls fail on size; DiD needs parallel reactions and dies silently; SC chooses weights instead of hoping. 💬 KEEP: "More weeks of data buy precision around the same wrong number." | 📐 All derivations, Var(B), both fold-outs. |
| 24 | Identification: what must hold | 🎯 Due-diligence framing: 4 assumptions, 3 testable (PASS), 1 untestable (spillover) — flag it, it returns at SUTVA. 🔗 "The untestable one is the second-launch leak you named for Colgate." Managers get checklists and audits. | 📐 Gate arithmetic. |

## ACT III — Is it real, how big? (~8 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 25 | Poll: is it real? ✋ | 🎯 Open with the absorbed line: with ONE treated metro a t-test is not weak, it is UNDEFINED. Then let THEM invent permutation inference: 29 fake "treatments" measure the method's luck. Rank 1/30 → p ≈ 3%. 💬 "You just reinvented a rigorous test using common sense." 🖼 "is this a pigeon? / is this a real effect?" | The word "exchangeable". |
| 26 | Placebo-in-space (live) | 🎯 The picture: green line clear of the grey luck-cloud. 💬 "Real ≠ profitable" — hold applause for Act IV. | Abadie hygiene rule (one clause for analysts). |
| 27 | Interval by test inversion (live) | 🎯 Only the OUTPUT and its role: [€195k, €335k], built with NO model assumptions → it is the REFEREE all later models must answer to. | 📐 The whole inversion mechanics (steps ①–④, quantile algebra) — fold. |
| 28 | Falsification 1: placebo-in-time | 🎯 Fake launch 10 weeks early → finds nothing → pass. 💬 "Any vendor claiming lift should show their method finds zero where nothing happened." | Broken-world checkbox unless time allows. |
| 29 | Falsification 2: spillover (SUTVA) | 🎯 MANAGEMENT SLIDE, don't rush: the untestable leak (ads reach the commuter belt = your controls). 🔗 "This is the second-launch failure you named for Colgate, in space." Two takeaways: bias only SHRINKS the number (conservative floor), and 💬 "Design beats analysis" — keep controls off the media footprint at TEST-DESIGN time. | 📐 φ sweep mechanics. |
| 30 | What the statistics says | 🎯 Bank the 3 numbers (p≈0.033 / €260k / [195, 335]). Then the trap: 💬 "260 for 75, 3.5×, roll it out — every number true, conclusion doesn't follow." Cliffhanger into money. | Truth-check detail (one clause: truth 284 is inside the interval). |

## ACT IV — The decision in euros (~12 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 31 | Poll: the margin ✋ | 🎯 Profit = margin × lift − cost ≈ €16k net. Option A (sales − cost = 185) is THE boardroom classic: revenue treated as profit. 🖼 "revenue vs profit — corporate needs you to find the difference" (callback to Nürnberger). | — |
| 32 | The margin trap (live) | 🎯 CHEAPEST LESSON OF THE DAY: break-even ROAS = 1/margin, not 1. Slide the margin: software 1.1 vs grocery 5.0 — same campaign, opposite verdicts. 💬 "ROAS > 1 is a vanity bar." | 📐 iROAS notation. |
| 33 | The decision space (live) | 🎯 "Looks profitable on average" ≠ "provably profitable": profit range [68, 117] straddles the 75 price. Our campaign lives in the dangerous zone. 🖼 the statistician who drowned crossing a river "1m deep on average." | 📐 The price-sweep table. |
| 34 | What you say to the board (classical) | 🎯 This memo answers the €75k PILOT only: ① real (p=0.033) ② big enough on the point (€16k net) ③ NOT confident (profit [68,117] straddles 75). Verdict: renegotiate or buy certainty with a bigger test. 💬 "This says nothing yet about the €4M — it is not the pilot multiplied." The one question it CAN'T answer ("78% chance it pays") is the forward tease to the probability view we add later. | Table row-by-row. |
| 35 | What €4M actually buys | 🎯 THE FREQUENTIST VERDICT, no probability needed. Carry the INTERVAL not the point, be maximally generous (δ=1, perfect transport): even then the 90% profit band is [−€360k, +€2.25M] → STRADDLES ZERO. 💬 "At the most optimistic assumption we can write down, we cannot show the €4M pays." Below δ≈0.64 it provably loses. ✋ ENGAGEMENT: run naive +€860k and poll for approval BEFORE carrying the interval. | 📐 δ-decomposition (already folded in a `<details>` on the slide — leave it folded). |
| 36 | Measure it, don't guess it | 🎯 MOST PROTECTED SLIDE — never cut. The call: even the best case straddled zero → do NOT commit €4M on this evidence ("not yet, not on this"). WHY analysis can't fix it: the interval is wide because there is ONE treated market; only more treated markets narrow it. THE FIX: (1) 💬 "before you spend a million on evidence, spend an hour checking you haven't already bought it"; (2) MEASURE — 8 markets that look like the nation, national intensity, €1.07M, so measured lift IS national lift; (3) pre-commit the release rule or the test is theatre. 🔗 "This is HelloFresh's loop, bought once — the counterfactual, anchored by an experiment." ✋ "so what would you spend?" → honest "not €4M yet." | 📐 Sizing arithmetic, p-floor — folded. |

### BRIDGE — Part 2 → FINALE (say this, ~15s)
💬 "Notice what that last instinct was: don't argue about the number, go get a cleaner one. Counterfactual,
then experiment, then price the decision. That is not a synthetic-control trick — it is the pattern under
every real engagement, including the three we opened with."

---
---

# FINALE — the pattern, and the close (~2 min)

*The labs closing slides come HOME here — written as a synthesis, they belong at the end. This is the
bookend: we opened with three cases, we close on the one pattern under all of them. When Part 3 (IV) is
appended later, this finale slides to after IV; for the labs+geo build it closes the session.*

### 37 · The tools are open-source — and they are the syllabus (moved from Part 1)
- 🎯 Provenance beat, ~45s: CausalPy (synthetic control, ITS, DiD, RDD) and pymc-marketing are the tools
  behind everything you just saw; one client's budget-allocation approach came back as a pull request
  (Bolt); the consultancy's own webinar agenda is literally this session's syllabus (incl. the IV close).
- Placement rationale: it lands better here than in the hook — after Part 2 the audience knows what the
  tools actually DO. Cuttable first if time runs out.
- 🖼 Package logos (already in deck). No meme.

### 38 · The pattern in every engagement
- 🎯 Collapse the whole session to three lines: the deliverable is a counterfactual; an experiment anchors
  every observational model; uncertainty prices the decision (boards act on headroom and P(pays), not a point).
- 🖼 The Decision Lab gag table already in the labs deck: vanilla agent → "Confidently wrong."; PyMC Labs'
  honest system → "No valid model found. Run a geo-holdout experiment." 💬 "Even the machine's best answer
  was this lecture's advice: run the experiment."

### 39 · One breath (close)
- 🎯 Deliver the one-breath summary and STOP. 💬 "The toolkit a Bayesian consultancy sells: counterfactuals,
  anchored by experiments, decided with their uncertainty on the table." Do not add content after it.
- Say-hello / repo line stays. (When IV is added, hold this slide for the very end of the 1.5h.)

### Backup · Sources
- Auto-generated pin table from labs_deck_data.json + geo claims. Backup only.

---
---

## The management take-homes (if you must cut 10 minutes, protect these)

1. **The counterfactual** (slides 4, 11, 13): a campaign's value is a missing number — "compared to what?" is always the question.
2. **Every method is a hidden claim** (slide 21): a wrong claim doesn't look wrong, and more data doesn't fix it.
3. **Calibration is the product** (slides 6–7, 36): an experiment anchors every model; it is not a luxury.
4. **When does the method refuse?** (slide 18): a tool that never says "I can't answer" is the one to distrust.
5. **Design beats analysis** (slides 24, 29): the untestable assumption (spillover) is controlled when you DESIGN the test.
6. **The margin trap** (slides 31–32): break-even ROAS = 1/margin. The single cheapest, most reusable lesson.
7. **Significance ≠ worthiness** (slides 30, 34, 36): "real" and "worth it" are different questions; the expensive mistakes live between them.
8. **The interval is the recommendation** (slides 35–36): even the BEST case for the €4M straddles zero — the analysis itself says "measure first." A wide interval from one treated unit is fixed by more units, not more analysis.

## If you are told "you have 45 minutes" on the day

Cut in this order: finale slide 37 (provenance) → geo 22–23 (keep the one quoted line) → 19 → 14–15 (merge
to one sentence each) → 33 (fold its point into 34) → the second poll of whichever act is running long.
Never cut: 2–6 (who we are + the hook), 10–13, 16, 18, 21, 25–26, 29, 31–32, 34–36 (35–36 above all), 38–39.

## Meme / visual budget (keep it to ~6–8 across the whole session — scarcity keeps them funny)

Highest-value, lowest-risk spots: slide 3 ("this is fine" CMO, no holdout) · slide 4 (two-Spider-Men
counterfactual) · slide 6 (overfitting / target-around-arrow) · slide 13 (Doctor Strange one-future) ·
slide 18 (big red OFF switch — the method refuses) · slide 32 (revenue vs profit "same picture") · slide 33
(river 1m deep on average). Everything else stays a clean figure. All optional; the polls and live widgets
are the primary engagement, memes are seasoning.
