# Unified Lecture — Narrative & Slide-by-Slide Emphasis (Management-Class Version)

**Audience:** general management on an MBA course, *not* analysts. Rule for every slide: lead with the
decision, keep the plot on screen, push the math into a folded subsection at the bottom. This file is
the presenter cheat-sheet AND the build spec for the merged deck.

**What this deck is:** three existing decks fused into ONE continuous arc — the labs "Causal Inference
in the Wild" deck (`labs_slides.html`) moved to the FRONT as the business hook, handing off to the
**SHORT** geo-lift deck (`geo_lift_sh.html`, the classical synthetic-control arc, Acts I–IV, a €4M
rollout), then to the **SHORT** instrumental-variables deck (`iv_slides_sh.html`, what one ad exposure
is worth when the platform picked who sees it). Target ~90 min (the full 1.5h session), 67 slides.
Parts 1–2 are the first ~55 min; a break; Part 3 is the last ~30 min. The spoken script is
`apps/geo_lift_lecture_speech.md`.

**The one-line spine of the whole session** (return here whenever a slide feels lost):
*"Every marketing decision is a counterfactual — what would have happened anyway? — anchored by an
experiment, and decided in euros with its uncertainty on the table. Real clients buy exactly that; here
is how you build one — twice."*

**The three-beat rhythm that repeats in every case and every act:** counterfactual → calibration →
decision-under-uncertainty. Part 1 shows real companies living it; Part 2 builds one, end to end, on the
hardest observational case and stops at the honest classical verdict ("measure first"); Part 3 builds
one more, for the case where you cannot even run the geo test, and the anchor is a scrap of randomness
you already own. NOTE: both worked examples are CLASSICAL — they deliver intervals and verdicts, not a
full P(pays). The probability layer is previewed (slide 3, Colgate's 49–59% interval, slide 35's tease)
and is the forward promise the later Bayesian material completes; do not sell "78% chance it pays" as
if these decks derived it.

---

## Legend (markers used on every slide)

- 🎯 = the ONE thing to land
- 💬 = a sentence worth saying close to verbatim
- 📐 = the math to FOLD (push to a collapsed subsection at the bottom; reveal only if asked)
- 🖼 = a meme / cartoon / figure to engage the room (all OPTIONAL, all tasteful — swap freely)
- ✋ = a poll or open-floor engagement beat
- ⏭ = skip / go fast for managers
- 🔗 = a callback/forward-link that stitches the three parts into one lecture

---

## THE STITCHING RULE (why the three parts feel like one)

Labs was authored as a CLOSER. Moved to the front, every backward callback became a forward promise.
Those are already fixed in the deck; the ones still worth saying out loud:

| Reads as (old callback) | Say instead (unified teaser) |
|---|---|
| "the counterfactuals you built today" | "the counterfactual we build after this hook" |
| "this morning's method" (synthetic control) | "the method we learn next" |
| "the IV estimator you ran this afternoon" | delivered in Part 3 — the finale now says "you just used" |
| "the sentence both lectures opened with" | "the sentence this whole session is about" |

And the BONUS of the order: later slides CALL BACK to the opening cases (🔗) — Colgate at the
counterfactual, the second-launch probe at SUTVA and again at IV's endogeneity, HelloFresh at "measure
it" and at IV's "instrument supply". Those callbacks are the glue.

---
---

# PART 1 — CAUSAL INFERENCE IN THE WILD (the hook · ~11 min)

*Purpose: earn attention before any math. Who is talking (one slide), one slide of method vocabulary,
then real companies, real money. Plant the three concepts the worked examples then build properly: the
counterfactual, calibration-by-experiment, uncertainty on the table.*

### 1 · Title (session opener)
- 🎯 Set the frame, modestly — no "by the end you will…" promises. These are questions real companies
  paid to have answered; today we walk through how that is actually done, and we build the machinery
  **twice** (a €4M rollout, then the price of one ad exposure).
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
- ⏭ Keep to ~60–75s. It is context, not the hook — land it and move on.

### 3 · Bayesian vs frequentist, in one slide (NEW slide) ⏭
- 🎯 Vocabulary insurance, ~60s: they will hear both words all session, and the difference decides which
  KIND of answer they may ask for. Frequentist = how a procedure behaves over many repeats → a range /
  confidence interval. Bayesian = probability over the unknown given the data in hand → a distribution,
  the "78% chance it pays" language.
- 💬 "You allocate money in the Bayesian language — odds — but the fastest standard tools speak the
  frequentist one. Both of today's builds stop at the honest frequentist answer: a range, and whether the
  price sits inside it. The probability layer is where the course goes next." (Plants slide 35's tease.)
- 📐 FOLD: the "the 95% interval is about the procedure, not this interval" catch — one line for the curious.
- ⏭ Do NOT teach philosophy. Name the two words, promise you'll flag which one you're speaking, move.

### 4 · Poll: you are the consultant (Colgate call) ✋ THE HOOK
- 🎯 The best hook in the deck BECAUSE they can't answer it yet. Colgate launched nationally, no holdout,
  no test market — which tool? Let them commit (A/B / DiD / project the counterfactual / instrument).
- ✋ Run it live. Most rooms split; that split IS the lesson. Reveal **C**: nothing to randomize, no control
  region, no instrument for a shelf that changed everywhere — what remains is *fit the world before the
  launch, project it forward, read the gap*.
- 💬 "If you're not sure — good. That gap is exactly what this session is for."
- 🖼 "This is fine" dog (national launch, no holdout, everything on fire) — the CMO's actual situation.
- 📐 Nothing. Keep it pure business.

### 5 · Colgate — incremental, or cannibalistic?
- 🎯 PLANT THE COUNTERFACTUAL (the spine of Part 2): the deliverable is *the world without the launch* —
  a number that exists in no file. Incremental (won from rivals/category) vs cannibalistic (stolen from
  your own shelf); the launch verdict is the split.
- 💬 Read the brief in their words: "estimate what the counterfactual sales would have been if the new
  product had not been introduced." That sentence is the whole course in one line.
- 🎯 The grading contract: on simulated data the model recovers a planted 50% as a 94% interval of 49–59%
  — "recover a known truth first, then trust it on the real thing." (This is exactly both worked examples' honesty.)
- 🖼 Two-Spider-Men-pointing meme: "sales with the launch" vs "sales without it" — only one is ever observed.
- 📐 FOLD: "multivariate Bayesian interrupted time series / nested-logit choice model." Name-drop only if asked.
- 🔗 Forward: "we build this exact object, slider by slider, in Part 2 — and a cousin of it in Part 3."

### 6 · What would break it? ✋ open floor + live widget
- 🎯 PLANT SPILLOVER (pays off at geo SUTVA slide 30) AND ENDOGENEITY (pays off at IV slide 46): the
  counterfactual can absorb the very effect it should isolate. Ask the room — as Colgate's CMO — to name
  one real event that breaks the estimate.
- ✋ 2-minute open floor, THEN reveal "a second launch": the model reported 64–76% against a planted 100%.
  💬 "An honest consultancy prints its misses in the same post as its wins."
- 🖼 Live "break it yourself" widget already in the deck: slide a second launch into the window, watch the
  read bend both ways (under- and over-credit). Let a student drive it.
- 📐 FOLD: pre-period trend+seasonality fit mechanics; keep only "the model learns 'normal' before the launch."
- 🔗 Forward: "hold onto 'a leak into the control' — it comes back at SUTVA, and its formal name,
  *endogeneity*, is the whole reason Part 3 exists."

### 7 · Why calibrate? A model alone can rank channels backwards ✋ live toggle
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

### 8 · HelloFresh runs the loop, at industrial scale
- 🎯 The pattern at scale: an always-on model, disciplined by a stream of experiments — a 60% cut in
  prediction variance. This is the "calibration is the product, not a luxury" beat.
- 💬 "The experiments a company already runs are its instrument supply." ← this line is the explicit bridge
  to Part 3 (IV): a randomized nudge is the instrument for the exposure you cannot randomize.
- 🖼 A "flywheel" / loop cartoon (model → experiment → better model). The deck already has the svgLoop triangle.
- 📐 FOLD: the throughput numbers (thousands of concurrent A/B/ABC/ABCD tests, 5–6h→5–6min, Criteo 13.98M
  users) — say "industrial scale," fold the digits.
- ⏭ Fast slide (~45s): the loop picture carries it.

### 9 · Poll: price the engagement (Nürnberger) ✋
- 🎯 The business payoff of getting attribution right: a German insurer swapped last-touch for a funnel-aware
  causal model and drove cost-per-lead down **more than 27%**. Poll the number first (they'll under-guess).
- 💬 The mechanism is the lesson: under GDPR, journeys looked artificially short, so last-touch under-credited
  the upper funnel and budget chased the wrong clicks. 💬 "Trust is not created by R² values. It is created
  when business reality matches model expectations." (Say it slowly — it's the client's own bar for belief.)
- 🖼 "Corporate needs you to find the difference between *revenue* and *profit* / *last-touch* and *causal*"
  — they're not the same picture. (Sets up the margin trap in Part 2.)
- 📐 Nothing on the slide; keep it a business win.

*(The old labs "tools were the product too" provenance slide MOVES to the finale — slide 64. With slide 2
covering who PyMC Labs is, keeping it here would say "open source" twice in five minutes.)*

### BRIDGE — Part 1 → Part 2 (say this out loud, ~20s)
💬 "Every one of those three was the same object: a counterfactual, calibrated by an experiment, priced as
a probability. Colgate built it in *time*. But the hardest, most common version is one market, no
experiment, and real money on a national rollout. For the next 40 minutes we build that one — start to
finish — and you'll see every idea from these three cases arrive with its proper name."

---
---

# PART 2 — SYNTHETIC CONTROL (the deep dive · ~44 min)

*The SHORT geo-lift deck (`geo_lift_sh.html`): the classical arc, Acts I–IV, business-first, math already
folded into `<details>` blocks. It STOPS at the classical verdict ("measure first"). Each act calls back
to Part 1's cases (🔗). Slide numbers below are the unified deck.*

### 10 · Part 2 divider / Title — "Synthetic Control"
- 🎯 Reset the frame: "One treated market, no experiment, €4M on the line: did the campaign work?" Keep the
  hero figure. 💬 "Colgate at least had a clean before-and-after. Take even that away — one market, no
  control, no experiment. This is the general case, and it's the most common one."

## ACT I — The question (~9 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 11 | The boardroom question | 🎯 Three questions IN ORDER: attribution → significance → decision. The metro was CHOSEN, not randomized — that's why it's hard. 💬 "Most companies jump to question 3 with an unchecked answer to question 1." 🔗 "Colgate's launch was national; here it's one metro — same missing number." | 📐 "unbiased" fold-out (only if asked). |
| 12 | The data (live) | 🎯 The counterfactual: the one number in no file — what the metro would have sold anyway. Show live that the naive bump changes when you subtract the crowd. 🖼 Rooster-takes-credit-for-sunrise ("the campaign made sales rise"). | 📐 The three technical readings, folded. |
| 13 | Poll: the 12% bump ✋ | 🎯 Naive before/after isn't "roughly right + noise": the tide can HIDE a real effect (as here) or inflate a fake one. Run the poll — commitment makes the teaching moment. | — |
| 14 | Potential outcomes | 🎯 Causal effect = gap between two histories; only one is observed. The 2×2: 3 cells are data, 1 is missing, every method fills that cell. Per-week vs 20-week total are different targets; the €4M rides on the total. 🖼 Doctor Strange "14,000,605 futures, we observe one." | 📐 Potential-outcome notation box — fold. |
| 15 | The data-generating model | 🎯 ONE honest confession: data is simulated SO every method can be graded against a known truth (~€284k) — the same recover-the-truth contract as Colgate. | 📐 The whole equation. "Four ingredients incl. per-market sensitivity" and move. |
| 16 | Simulate the world (live) | 🎯 ONE slider (macro shock): turbulence destroys before/after. 💬 "Compared to what?" 🖼 optional: stormy-sea "a rising tide lifts all boats" visual. | ⏭ Other sliders; the full "what sliders teach" list. |

## ACT II — The counterfactual (~11 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 17 | Abadie's idea: the synthetic twin | 🎯 THE core idea: no twin exists, so blend markets into one. Twin matches RESPONSES to shocks, not levels → survives storms. Anchors: Meta GeoLift, Google geo tools. 🖼 "assemble a twin from parts" cartoon, tasteful. | 📐 Factor-model equation; pedigree fold-out (one clause). |
| 18 | The estimator | 🎯 3 business facts: (1) fitted ONLY pre-launch = no peeking, (2) weights are a readable recipe (40%+32%+17%), (3) effect = subtraction. 🔗 "The honest, weights-on-the-table version of what Colgate's model did in time." | 📐 argmin / simplex formulas — folded on the slide. |
| 19 | Inside the convex hull (live) | 🎯 Coffee+milk can't make orange juice: a blend can't reach outside the donors' range → the method can REFUSE. 💬 SIGNATURE MANAGEMENT LINE: "Ask any vendor — when does your method refuse to answer? If 'never', walk away." 🖼 big red OFF switch / "computer says no". | 📐 "simplex", "hull" — use the demo, not the words. |
| 20 | What the constraint buys (live) | 🎯 Better fit to the past ≠ better model. Drop the constraint: OLS fits tighter, predicts worse, uses absurd weights (−80%). 💬 "Anyone selling a model on past fit is selling the wrong metric." 🖼 the overfitting meme (squiggly line through every point). | 📐 n_eff (inverse Herfindahl) block — fold. |
| 21 | Why not just forecast it? | 🎯 Forecasting ≠ counterfactual: "what comes next" vs "what would have happened in a world that never happened." You cannot cross-validate the counterfactual → pick defendable assumptions, not demo accuracy. Auditability is a business feature. 🖼 confidently-wrong-AI / "trust me bro" robot. | The sweep numbers (one clause: "clearly worse across 24 worlds"). |
| 22 | Every shortcut is an assumption | 🎯 KEY SLIDE of Act II. Every method = a hidden claim about the counterfactual. Live dials: DiD dies when markets react differently. 💬 "A wrong method does not look wrong, and more data does not fix it." | 📐 The formulas — point at the dials instead. |
| 23–24 | Before DiD: two one-difference estimators / When does DiD work? (algebra) | ⏭ Compress BOTH to: before/after fails when the world moves; controls fail on size; DiD needs parallel reactions and dies silently; SC chooses weights instead of hoping. 💬 KEEP: "More weeks of data buy precision around the same wrong number." | 📐 All derivations, Var(B), both fold-outs. |
| 25 | Identification: what must hold | 🎯 Due-diligence framing: 4 assumptions, 3 testable (PASS), 1 untestable (spillover) — flag it, it returns at SUTVA. 🔗 "The untestable one is the second-launch leak you named for Colgate." Managers get checklists and audits. | 📐 Gate arithmetic. |

## ACT III — Is it real, how big? (~8 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 26 | Poll: is it real? ✋ | 🎯 Open with the absorbed line: with ONE treated metro a t-test is not weak, it is UNDEFINED. Then let THEM invent permutation inference: 29 fake "treatments" measure the method's luck. Rank 1/30 → p ≈ 3%. 💬 "You just reinvented a rigorous test using common sense." 🖼 "is this a pigeon? / is this a real effect?" | The word "exchangeable". |
| 27 | Placebo-in-space (live) | 🎯 The picture: green line clear of the grey luck-cloud. 💬 "Real ≠ profitable" — hold applause for Act IV. | Abadie hygiene rule (one clause for analysts). |
| 28 | Interval by test inversion (live) | 🎯 Only the OUTPUT and its role: [€195k, €335k], built with NO model assumptions → it is the REFEREE all later models must answer to. | 📐 The whole inversion mechanics (steps ①–④, quantile algebra) — fold. |
| 29 | Falsification 1: placebo-in-time | 🎯 Fake launch 10 weeks early → finds nothing → pass. 💬 "Any vendor claiming lift should show their method finds zero where nothing happened." | Broken-world checkbox unless time allows. |
| 30 | Falsification 2: spillover (SUTVA) | 🎯 MANAGEMENT SLIDE, don't rush: the untestable leak (ads reach the commuter belt = your controls). 🔗 "This is the second-launch failure you named for Colgate, in space — and the endogeneity we meet head-on in Part 3." Two takeaways: bias only SHRINKS the number (conservative floor), and 💬 "Design beats analysis" — keep controls off the media footprint at TEST-DESIGN time. | 📐 φ sweep mechanics. |
| 31 | What the statistics says | 🎯 Bank the 3 numbers (p≈0.033 / €260k / [195, 335]). Then the trap: 💬 "260 for 75, 3.5×, roll it out — every number true, conclusion doesn't follow." Cliffhanger into money. | Truth-check detail (one clause: truth 284 is inside the interval). |

## ACT IV — The decision in euros (~12 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 32 | Poll: the margin ✋ | 🎯 Profit = margin × lift − cost ≈ €16k net. Option A (sales − cost = 185) is THE boardroom classic: revenue treated as profit. 🖼 "revenue vs profit — corporate needs you to find the difference" (callback to Nürnberger). | — |
| 33 | The margin trap (live) | 🎯 CHEAPEST LESSON OF THE DAY: break-even ROAS = 1/margin, not 1. Slide the margin: software 1.1 vs grocery 5.0 — same campaign, opposite verdicts. 💬 "ROAS > 1 is a vanity bar." | 📐 iROAS notation. |
| 34 | The decision space (live) | 🎯 "Looks profitable on average" ≠ "provably profitable": profit range [68, 117] straddles the 75 price. Our campaign lives in the dangerous zone. 🖼 the statistician who drowned crossing a river "1m deep on average." | 📐 The price-sweep table. |
| 35 | What you say to the board (classical) | 🎯 This memo answers the €75k PILOT only: ① real (p=0.033) ② big enough on the point (€16k net) ③ NOT confident (profit [68,117] straddles 75). Verdict: renegotiate or buy certainty with a bigger test. 💬 "This says nothing yet about the €4M — it is not the pilot multiplied." The one question it CAN'T answer ("78% chance it pays") is the forward tease to the probability view (slide 3's Bayesian word) we add later. | Table row-by-row. |
| 36 | What €4M actually buys | 🎯 THE FREQUENTIST VERDICT, no probability needed. Carry the INTERVAL not the point, be maximally generous (δ=1, perfect transport): even then the 90% profit band is [−€360k, +€2.25M] → STRADDLES ZERO. 💬 "At the most optimistic assumption we can write down, we cannot show the €4M pays." Below δ≈0.64 it provably loses. ✋ ENGAGEMENT: run naive +€860k and poll for approval BEFORE carrying the interval. | 📐 δ-decomposition (already folded in a `<details>` on the slide — leave it folded). |
| 37 | Measure it, don't guess it | 🎯 MOST PROTECTED SLIDE — never cut. The call: even the best case straddled zero → do NOT commit €4M on this evidence ("not yet, not on this"). WHY analysis can't fix it: the interval is wide because there is ONE treated market; only more treated markets narrow it. THE FIX: (1) 💬 "before you spend a million on evidence, spend an hour checking you haven't already bought it"; (2) MEASURE — 8 markets that look like the nation, national intensity, €1.07M, so measured lift IS national lift; (3) pre-commit the release rule or the test is theatre. 🔗 "This is HelloFresh's loop, bought once — the counterfactual, anchored by an experiment." ✋ "so what would you spend?" → honest "not €4M yet." | 📐 Sizing arithmetic, p-floor — folded. |

### BRIDGE — Part 2 → Part 3 (say this before the break, ~30s)
💬 "Synthetic control needed one thing to work: a clean group of untreated markets to build the twin from.
When you have that, you can rescue a decision even without an experiment. But sometimes the thing you want
to measure was assigned by someone whose whole job is to NOT be random — a platform choosing who sees an
ad. No clean control exists, and you can't run the test. After the break: the last and hardest case, and
its own tool." *(The finale now sits AFTER Part 3; Part 2 hands off to IV, not to the close.)*

---
---

# PART 3 — INSTRUMENTAL VARIABLES (the last tool · ~30 min)

*The SHORT IV deck (`iv_slides_sh.html`): one retailer, one ad platform, one decision — what is one ad
exposure worth when the platform picked who sees the ads? Entirely CLASSICAL (two averages, one division,
one F, one interval). Sections mirror the deck's data-sec groups: The problem → The idea → The estimator →
When it breaks → The decision. This is the endogeneity case Part 1's Colgate probe and Part 2's SUTVA
slide both pointed at. Slide numbers are the unified deck.*

### 38 · Part 3 divider / Title — "Instrumental Variables"
- 🎯 Reset, and pose the part in one image: the dashboard's number is TIGHT and WRONG; the lottery's number
  is WIDER and RIGHT, and still clears the price. Kicker "Part 3 · The natural experiment". 💬 "Same
  discipline — counterfactual, anchor, price — but the anchor comes from a surprising place: a scrap of
  randomness we already ran."
- 🖼 The hero figure (dashboard interval misses the truth; lottery interval covers it) carries it. No meme yet.

## IV · THE PROBLEM — why the dashboard lies (~13 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 39 | The case | 🎯 Set the decision cleanly: exposure = one user saw an ad, costs €10; the auction (not us) picks who; dashboard says exposed spent ~€24 more; pitch = "raise the budget"; decision = keep €10 / pay more / stop. One number settles it: euros of extra sales ONE exposure causes. 🔗 "Colgate's disease, a third time — compared to what?" | 📐 nothing; pure business setup. |
| 40 | Poll · the pitch ✋ | 🎯 Correct = C (not sound: exposed users may differ from unexposed, ad or no ad). A/B miss because the arithmetic IS right and it IS significant — that's not the problem. 💬 "The platform's whole job is to find buyers, so the exposed group was more likely to buy before any ad ran." 🖼 a pushy-salesperson / "trust me, raise the budget" meme. | — |
| 41 | Confounding, defined | 🎯 Name the three quantities: sales (outcome), exposure (0/1, auction-assigned), and INTENT — readiness to buy, real, drives buying AND drives who gets an ad, and NEVER logged. A hidden driver of both = a CONFOUNDER. That word is the takeaway. | 📐 SKIPPABLE MATH: the DAG + formal definitions — fold; say "confounder" and move. |
| 42 | The naive comparison (live) | 🎯 Write €24 down honestly: €68 − €44, two OBSERVED cells; it pretends the unexposed group's spend is a fair stand-in for the exposed group's missing "without-ad" spend. LIVE: tick "reveal the hidden driver" → the groups already differed in intent. 💬 "The arithmetic is right. The comparison is wrong." | 📐 potential-outcomes table Y(1)/Y(0) — on-slide, keep it visual. |
| 43 | Poll · read the gap ✋ | 🎯 Correct = B (€24 = the ad's effect + the groups' pre-existing difference, in unknown proportions). A books it all to the ad, D all to targeting; the data alone justify neither. 💬 "The only honest statement is the split — and splitting it is the whole rest of the part." | — |
| 44 | Selection bias, defined | 🎯 The split has a formula: naive gap = (effect of the ad on the exposed) + (SELECTION BIAS = the gap that would exist with NO ads, because the platform picked buyers). Our job = kill the second term. | 📐 SKIPPABLE MATH: the E[Y(0)|X] decomposition — fold; say it in words. |
| 45 | The simulated world | 🎯 Same honesty as geo: we PLANTED the true effect at €15, so every method is graded; the dashboard's €24 is already wrong by €9. LIVE (κ slider): push intent's pull up → groups drift apart, dashboard gap grows, planted truth never moves. ⏭ Fast (~45s). | 📐 the three generating equations — fold. |
| 46 | Endogeneity, precisely | 🎯 The whole disease as ONE inequality, translated: exposure is correlated with "every other reason this person spent" (intent), because the auction targets exactly those people. Name = ENDOGENEITY. 🔗 "This is the formal name for Colgate's 'leak into the control' and geo's spillover — a thing CHOSEN using info you can't see." | 📐 SKIPPABLE MATH: Cov(X,v)>0, v = κU+ε — fold; the picture (both bars rise with intent) carries it. |
| 47 | The size of the bias (live) | 🎯 The lie is computable, not vague: formula predicts ~€23.5, data delivered €23.7, truth €15. THREE lessons: (1) SYSTEMATIC not luck — dashboard can only OVERSTATE; (2) grows with targeting and with intent's pull — better platform, bigger lie; (3) sample size is NOWHERE in it → more data can't fix bias. | 📐 SKIPPABLE MATH: the bias formula — the live readout is the point. |
| 48 | The limits of adjustment | 🎯 NEVER CUT — the pivot. The standard fix (control/match on the confounder) is the RIGHT move and normally works: LIVE tick "pretend intent were logged" → recovers €15. Untick → intent is a feeling in a head, not in the logs, never will be. 💬 "You cannot control for a column you do not have." The toolkit runs out of road HERE. | 📐 the boxed-W backdoor DAG — on-slide. |
| 49 | Poll · what would fix it ✋ | 🎯 NEVER CUT — the hinge into IV. Correct = C (a batch of users whose exposure we assign at random). A = wrong number more precisely (bias isn't noise); B/D = more controls, auction reacts to live signals, backdoor stays open. 💬 "The instinct is right — but you can't randomize the ads; the platform owns that auction. So we need randomness we CAN get our hands on." | — |

## IV · THE IDEA — the instrument (~9 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 50 | The ideal experiment | 🎯 NEVER CUT. What randomizing exposure would buy: it doesn't BLOCK intent's arrow into exposure, it DELETES it → the naive comparison becomes right. We can't randomize exposure directly — but we only need something random that NUDGES it. 🔗 "Option C from the poll, made real." | 📐 X randomized ⇒ Cov(X,v)=0 ⇒ naive → β — one line. |
| 51 | The lottery | 🎯 NEVER CUT — the heart of the method. Before the campaign our own RNG ran a serving-priority LOTTERY: picked half the users, gave them a small auction-priority boost. Subtle and crucial: it shows NOBODY an ad — it only raises the ODDS of one. Winners chosen by our coin flip → blind to intent. 🖼 a "golden ticket" / rigged-in-our-favour-coin visual. | 📐 Pr(X=1)=σ(α₀+γZ+λU); new column Z — fold. |
| 52 | The instrument, defined | 🎯 The scrap of randomness has a name: an INSTRUMENT moves the treatment, is as-good-as-random vs the hidden confounder, and hits the outcome ONLY through the treatment. Four conditions: Relevance (testable), Exogeneity (by design), Exclusion (argued), Monotonicity (argued). 💬 "Two we get for free because we built the lottery; two we must argue. That scorecard is how you judge ANY IV study." | 📐 the four-row condition table — present the four names, fold the fine print. |
| 53 | Condition 1 · relevance | 🎯 The one condition DATA can settle: the FIRST STAGE = extra exposure the lottery created. Winners exposed ~21 points more than losers → π ≈ 0.21. Real, measured, strong. "If this were ~0 the method is dead — hold that for weak instruments." | 📐 SKIPPABLE MATH: X = b₀+πZ+u, π = 0.2106 — the two bars carry it. |
| 54 | Conditions 2 and 3 (live) | 🎯 The two you must ARGUE. Exogeneity (blind to intent) = free, we drew it. EXCLUSION is the honest one: the lottery must touch sales ONLY via exposure — a side-channel (faster page, shown price) leaks straight into the answer. 🔗 "The untestable assumption — exactly like geo's spillover. You DESIGN it out, you argue it in words." | 📐 the side-channel bias β̂_IV = β + s/π — LIVE demo is the point. |

## IV · THE ESTIMATOR — the division (~5 min, but slide 56 is the climax)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 55 | The reduced form | 🎯 Second measured number, same shape: the REDUCED FORM = the lottery's effect on SALES = the raw win/lose sales gap ≈ €3.48. Clean for the same reason π was (a random draw can't favour ready buyers). Hold the two clean numbers: 0.21 extra exposures, €3.48 extra sales per win. | 📐 SKIPPABLE MATH: δ = E[Y|Z=1]−E[Y|Z=0] = €3.48 — say it in words. |
| 56 | The IV estimate | 🎯 THE PAYOFF — NEVER CUT. One division: €3.48 of sales per win ÷ 0.21 exposures per win = **€16.5 per exposure**. Units ARE the intuition (euros/win ÷ exposures/win = euros/exposure). Intent divides out (can't correlate with a coin flip). 💬 "Dashboard said 24, truth is 15, the lottery says 16½ — the first number all session not poisoned by who the platform picked." | 📐 β̂_IV = δ/π — the arithmetic IS the slide. |
| 57 | Why the division is forced (live) | 🎯 ⏭ Fast reinforcement: the division isn't a modelling choice, it's the ONLY effect the two numbers allow. LIVE: drag a guess; rising line = its prediction (β̂×π), flat line = the fact (€3.48); they meet only at €16.5. | — |

## IV · WHEN IT BREAKS — the caveats (~4 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 58 | Weak instruments (live) | 🎯 The failure to RECOGNIZE: a WEAK instrument (tiny first stage) is worse than none. LIVE (drag lottery strength down): the interval explodes AND the centre creeps back toward the naive lie (dividing by ~0). 💬 "Looks like a method while quietly handing back the dashboard's number." The defence = the first-stage F (rule of thumb >10; ours 156). Always ask for it. | 📐 the F-vs-estimate sweep — the live band is the point. |
| 59 | Compliers and the LATE (live) | 🎯 Whose number is €16.5? Only the movable — the COMPLIERS (saw the ad because they won the lottery). Always-takers / never-takers: the lottery is silent about them. 💬 "The movable are exactly who your next euro of budget reaches — the right number for the decision." Name = LATE. | 📐 SKIPPABLE MATH: the three-slice split; "local average treatment effect" — fold. |
| 60 | The checklist | 🎯 NEVER CUT — the reusable scorecard. Four assumptions: Relevance (F=156, TESTABLE, passes) · Exogeneity (by design) · Exclusion (UNTESTABLE, argue) · Monotonicity (UNTESTABLE, plausible). 💬 "One number you can check, one design guarantee, two arguments in words. Ask a vendor for all four — if they show only the estimate, they showed you the least important part." | — |

## IV · THE DECISION — euros at last (~3 min)

| # | Slide (short-deck title) | Emphasize | Fold / skip |
|---|-------|-----------|-------------|
| 61 | The price map (live) | 🎯 NEVER CUT — the cleanest decision slide. One estimate → a MAP from price to verdict: below €12.7 GO (even the most pessimistic supported effect pays), €12.7–€20.4 TEST (interval straddles the price), above €20.4 NO-GO. LIVE: drag the price and watch the verdict flip. Today's €10 sits comfortably in GO. | 📐 the interval band + zones — the live figure carries it. |
| 62 | Poll · the negotiation ✋ | 🎯 Correct = C (€12.7, the interval FLOOR = the no-regret bid cap: below it every supported effect pays, whichever is true). B (€16.5, the point) is a coin-flip gamble. 💬 "You just priced a bid cap off a confidence interval." | — |
| 63 | The verdict and the recommendation | 🎯 NEVER CUT — the close of Part 3. On one page: effect €16.5 (δ/π), 90% [12.7, 20.4] (classical, AR agrees — the placebo-style referee, exactly as in geo), F=156, price €10, net €6.5. Verdict BUY. Three lines: keep buying at €10 · cap the bid at €12.7 · re-measure only if the rate climbs toward the floor. 💬 "Entirely classical, and it answered what the dashboard could not — by finding one scrap of randomness we controlled." | 📐 the summary table — on-slide. |

### BRIDGE — Part 3 → FINALE (say this, ~15s)
💬 "Three real cases, then two builds — a €4M rollout you learned to refuse, and an ad price you learned
to trust. Different tools, one pattern: a counterfactual, an anchor, a price. That's not a synthetic-control
trick or an IV trick — it's the shape under every real engagement, including the three we opened with."

---
---

# FINALE — the pattern, and the close (~2.5 min)

*The labs closing slides come HOME here — written as a synthesis, they belong at the very end. This is the
bookend: we opened with three cases, we close on the one pattern under all of them. Now that Part 3 has
run, this finale is the true session close.*

### 64 · The tools are open-source — and they are the syllabus (moved from Part 1)
- 🎯 Provenance beat, ~45s: CausalPy (synthetic control, ITS, DiD, RDD — AND the IV estimator you just used
  to price the ad exposure) and pymc-marketing are the tools behind everything you saw; one client's
  budget-allocation approach came back as a pull request (Bolt); the consultancy's own webinar agenda is
  literally this session's syllabus (geo tests, MMM, synthetic control, diff-in-diff, instrumental variables).
- Placement rationale: lands better here than in the hook — after both builds the audience knows what the
  tools actually DO. Cuttable first if time runs out.
- 🖼 Package logos (already in deck). No meme.

### 65 · The pattern in every engagement
- 🎯 Collapse the whole session to three lines: the deliverable is a counterfactual; an experiment anchors
  every observational model — and when you can't run one, you hunt a scrap of randomness the world already
  made (the instrument); uncertainty prices the decision (boards act on the interval and the headroom, not
  a point). 💬 "Twice today the honest interval overturned the confident point."
- 🖼 The Decision Lab gag table already in the labs deck: vanilla agent → "Confidently wrong."; PyMC Labs'
  honest system → "No valid model found. Run a geo-holdout experiment." 💬 "Even the machine's best answer
  was this lecture's advice: measure it."

### 66 · One breath (close)
- 🎯 Deliver the one-breath summary and STOP. 💬 "The toolkit a Bayesian consultancy sells: counterfactuals,
  anchored by experiments, decided with their uncertainty on the table. You've watched real clients buy it,
  and built two yourself — a €4M rollout you learned to refuse, and an ad exposure you learned to trust."
  Do not add content after it.
- Say-hello / repo line stays. This IS the end of the 1.5 hours.

### Backup · Sources (67)
- Auto-generated pin table from labs_deck_data.json + geo/IV claims. Backup only.

---
---

## The management take-homes (if you must cut, protect these)

1. **The counterfactual** (slides 5, 12, 14, 42): a campaign's — or an ad's — value is a missing number; "compared to what?" is always the question.
2. **Every method is a hidden claim** (slide 22): a wrong claim doesn't look wrong, and more data doesn't fix it.
3. **Calibration is the product** (slides 7–8, 37): an experiment anchors every model; it is not a luxury.
4. **When does the method refuse?** (slide 19): a tool that never says "I can't answer" is the one to distrust.
5. **Design beats analysis** (slides 25, 30, 54): the untestable assumption (spillover / exclusion) is controlled when you DESIGN the test or the instrument, not after.
6. **The margin trap** (slides 32–33): break-even ROAS = 1/margin. The single cheapest, most reusable lesson.
7. **Significance ≠ worthiness** (slides 31, 35, 37): "real" and "worth it" are different questions; the expensive mistakes live between them.
8. **The interval is the recommendation** (slides 36–37, 61): even the BEST case for the €4M straddles zero (measure first); the IV interval's FLOOR is the no-regret bid cap. A range beats a point.
9. **Endogeneity, and its cure** (slides 46, 48–49, 51, 56): when the thing you measure was CHOSEN using what you can't see, controls fail — you need a scrap of randomness (an instrument), and the whole method is then one honest division.
10. **A weak instrument is worse than none** (slide 58): near-zero first stage → the estimate quietly reverts to the biased dashboard number. Always ask for the first-stage F.

## If you are told "you have 60 minutes" on the day (Parts 1–2, hold Part 3 for a follow-up)

Cut in this order: finale slide 64 (provenance) → geo 23–24 (keep the one quoted line) → 20 → 15–16 (merge
to one sentence each) → 34 (fold its point into 35) → the second poll of whichever act is running long.
Never cut: 2–7 (who we are + the hook), 11–14, 17, 19, 22, 26–27, 30, 32–33, 35–37 (36–37 above all), 65–66.

## If Part 3 runs tight (~30 min for IV)

Fast/fold: 41 (name the confounder, fold the DAG), 44 (words not algebra), 45, 46 (one-line endogeneity),
47, 53 ("21 points more exposure"), 55 ("€3.48 per win"), 57, 59 (one sentence on "whose number").
Never cut: 39, 42, 48–52, 56 (the division), 60 (checklist), 61, 63 (the verdict).

## Meme / visual budget (keep it to ~8–10 across the whole 1.5h session — scarcity keeps them funny)

Highest-value, lowest-risk spots: slide 4 ("this is fine" CMO, no holdout) · slide 5 (two-Spider-Men
counterfactual) · slide 7 (overfitting / target-around-arrow) · slide 14 (Doctor Strange one-future) ·
slide 19 (big red OFF switch — the method refuses) · slide 33 (revenue vs profit "same picture") · slide 34
(river 1m deep on average) · slide 40 (pushy salesperson "raise the budget") · slide 51 (golden ticket /
rigged coin — the lottery in our favour). Everything else stays a clean figure. All optional; the polls and
live widgets are the primary engagement, memes are seasoning.
