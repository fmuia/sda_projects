# Unified Lecture — Full Speech (Management-Class Version)

The spoken script for `apps/unified_slides.html` (40 slides): Part 1 "Causal Inference in the
Wild" (real PyMC Labs engagements, the hook) → Part 2 "Synthetic Control" (the short classical
arc, Acts I–IV) → the finale (the pattern, one breath). Slide numbers match the deck's counter.
The per-slide priorities live in `apps/geo_lift_lecture_emphasis.md`; this file is what you say.

**Audience adjustment.** Written for a general management class, not an analytics class. Every
slide is presented as a **business decision problem first**. The math on the slides is optional
depth: whenever a slide is math-heavy, the script gives a short business translation to say out
loud, plus one sentence to hand the math to the curious ("the formula is in the fold for those
who want it"). You never need to derive anything live.

**Language.** Short sentences. Plain words. No idioms. Read it as written or in your own words.

**Timing guide (~55 min).** Part 1 ~10 min (title+labs ~2, poll 2.5, Colgate 2, break-it 2,
calibrate 1.5, HelloFresh 0.75, Nürnberger 2) · Act I ~9 · Act II ~11 · Act III ~8 ·
Act IV ~12 (the €4M pair, slides 35–36, is the climax: protect it) · Finale ~2.5.
A third part (instrumental variables) will follow in the 1.5h session; this script leaves the
close open for it.

Slides marked **[FAST]** can be covered in 30–60 seconds for this audience.
Slides marked **[SKIPPABLE MATH]** can be summarized in one sentence; the fold stays closed.

---
---

# PART 1 — CAUSAL INFERENCE IN THE WILD

## Slide 1 — Title

> Good morning. Before any theory, I want to show you what this subject looks like when real
> companies pay for it. Three client stories, ten minutes. Then we take the hardest version of
> their problem and build the machinery ourselves, end to end, on a four-million-euro decision.
>
> Nothing today needs a statistics background. It needs the willingness to ask one question,
> stubbornly: compared to what?

## Slide 2 — PyMC Labs: what we do

> One minute on who is talking, because it explains why these stories exist.
>
> PyMC Labs is a Bayesian modeling consultancy. Two things at once: we build custom
> decision-making models for companies where off-the-shelf tools fall short, and we maintain
> the open-source libraries this field runs on — PyMC, PyMC-Marketing, CausalPy.
>
> The business model matters for how you read the cases. We sell senior modeling expertise, not
> software licenses. Engagements come in three shapes — you see them in the table: a fixed-scope
> project when a company has one high-value decision problem; an advisory retainer when a firm
> is building its own team; and training when an analytics team is standardizing on the tools.
> The libraries are free. They build trust and reach. The consulting monetizes the expertise
> behind them. Small senior teams, no junior pyramid, and the client keeps the model at the end —
> not a black box.
>
> The client list for today is on the slide: Colgate-Palmolive, HelloFresh, a German insurer
> called Nürnberger Versicherung. You meet three of them in the next ten minutes. [The fold has
> the full areas-of-interest list, for later.]

## Slide 3 — Poll: you are the consultant

> Now you are the consultant, and the phone rings. [Read the poll.] Colgate-Palmolive:
> "Our new toothpaste launched nationally last quarter. No holdout, no test market. Is it
> stealing share from competitors, or from our own brands?" Four instruments on the slide.
> Which do you reach for first?
>
> [Collect hands on each option. Then reveal.]
>
> C. And here is why the others fail. An A/B test needs something left to randomize — the
> launch already happened, everywhere. Difference-in-differences needs a region without the
> product — there is none. An instrument for shelf placement — the shelf changed in every store
> at once. When the world gives you no comparison group, one move remains: learn the world
> before the launch, project it forward, and read the gap. That projection is called a
> counterfactual, and it is the single product every case today has in common.
>
> If you were not sure which to pick — good. That gap is exactly what this session is for.

## Slide 4 — Colgate: incremental, or cannibalistic?

> Here is the brief in the client's own words: "estimate the counterfactual sales of all
> products, had the new product not been introduced." Read that twice. The client is asking to
> buy a number that exists in no file, no dashboard, no report anywhere on earth: what would
> have happened without the launch.
>
> Why does it matter? Two words on the slide. **Incremental** sales are won from competitors or
> category growth — those justify the launch. **Cannibalistic** sales are stolen from your own
> shelf — those just moved euros between your own products. The launch verdict is the split.
>
> And notice the professional discipline, because it returns all day: before trusting the model
> on real data, they graded it on simulated data where the answer was planted. Planted truth:
> fifty percent incremental. The model's interval: 49 to 59 percent. It recovers the truth, so
> it earns the right to be believed. Remember this contract — recover a known truth first.
> We will hold every method today to it.
>
> [If asked for the method's name: "a multivariate Bayesian interrupted time series, later a
> nested-logit choice model — the names matter less than the projection idea."]

## Slide 5 — What would break it? (open floor + live widget)

> Before you trust that number, earn your fee. You are Colgate's CMO. Name one real-world event
> that would make this estimate wrong. [Open floor, two minutes. Typical answers: a competitor
> launch, a price change, a pandemic, a second launch of our own.]
>
> [Reveal.] The model itself confessed one: **a second product launch** inside the estimation
> window. When that happened, the same machinery reported 64 to 76 percent against a planted
> truth of one hundred. Why? The counterfactual learned "normal growth" from a window that
> already contained another launch — it absorbed part of the very effect it was meant to isolate.
>
> [Hand a student the widget: tick "a second product launches nearby", slide the month.] Watch
> the readout bend: inside the window it under-credits; near the edge it over-credits. Same
> machinery, wrong world, wrong number — and no error message anywhere.
>
> Two things to keep. First: an honest consultancy prints this failure in the same post as the
> win. When you buy analytics, ask for the failure cases; if there are none, walk away. Second:
> hold onto the phrase "something leaked into my comparison". It comes back this afternoon with
> a formal name, and it is the one assumption no statistical test can rescue.

## Slide 6 — Why calibrate? A model alone can rank channels backwards

> Second case, and first a warm-up from the tools themselves. A marketing-mix model — MMM on
> the slide — explains total sales as the sum of each channel's contribution, fitted on the
> spend history you already have. Every large advertiser runs one.
>
> Here is the published tutorial demo. Fit on observational spend alone, the model reported
> channel one earning 93 and channel two earning 171 — sorry, the reverse: it ranked them
> **backwards**. The truth was the direct opposite of what the dashboard said. And nothing on
> the dashboard warns you. The fit was good. The intervals were tight. The ranking was wrong.
>
> [Tick the toggle: "add two lift tests per channel".] A lift test is a small experiment: nudge
> one channel's spend by a known amount, measure the sales it causes. Feed two of those per
> channel into the model, and the ranking flips to the truth.
>
> The lesson of the whole session in one line: **the experiment is the model's anchor.** A model
> without an anchor can be confidently wrong. Hold that thought; the entire second half is about
> how to build the anchor when you only get one.

## Slide 7 — HelloFresh runs the loop, at industrial scale **[FAST]**

> Does anyone run this loop for real? HelloFresh does, at industrial scale. An always-on
> marketing-mix model, calibrated by a continuous stream of field experiments — the panel's own
> agenda says "calibrated to ensure consistency with incrementality measurements" — and the
> calibration cut prediction variance by sixty percent. The picture is the whole slide: the
> model asks for ground truth, the experiment supplies it, the counterfactual reads it out.
>
> One sentence to remember for the final part of this session: the experiments a company
> already runs are its **instrument supply**. When you cannot randomize the thing you care
> about, a randomized nudge nearby can stand in for it. That is the doorway to instrumental
> variables, and we walk through it later today.

## Slide 8 — Poll: price the engagement (Nürnberger)

> Last case, and this one has a number with an invoice attached. Nürnberger Versicherung, a
> German insurer. Their steering metric was last-touch attribution — credit the click that came
> last. They replaced it with a funnel-aware causal model. [Read the poll.] Over six months of
> model-guided spend, what happened to their cost per lead?
>
> [Collect. Reveal.]
>
> Down more than 27 percent. In the client's words, "very, very good". The mechanism is the
> management lesson: under GDPR consent rules, customer journeys appeared artificially
> shortened, so last-touch systematically under-credited the upper funnel — video, display —
> and budget chased the wrong clicks. The causal model measured what the upper funnel actually
> causes downstream, and the client is scaling it into full production.
>
> And listen to the client's bar for belief, on the slide: "Trust is not created by R-squared
> values. It is created when business reality matches model expectations." No statistical
> pitch ever beats that sentence. Keep it.
>
> **[The bridge — say this over the slide before advancing.]** Three cases, one shape. A
> counterfactual — the world without the launch, the campaign, the exposure. An experiment that
> anchors the model. And a decision priced in euros, with its uncertainty on the table. Colgate
> built the counterfactual in *time*: before the launch versus after. The hardest and most
> common version of the problem is built in *space*: one market got the campaign, and you must
> decide about a nation. No experiment, real money. For the next forty minutes we build exactly
> that one, end to end, and every idea from these three cases will come back with its proper name.

---
---

# PART 2 — SYNTHETIC CONTROL

## Slide 9 — Part 2 divider

> Now the deep dive. I will not teach you statistics. I will teach you how to make one specific
> business decision: whether to spend four million euros on a national marketing campaign, when
> the only evidence you have is one regional pilot. The method is called synthetic control. It
> is the engine inside the geo-testing tools used by Meta and Google. But the method is not the
> point. The point is the decision.
>
> Colgate at least had a clean national before-and-after. Now take even that away.

# ACT I — THE QUESTION

## Slide 10 — The boardroom question

> Here is the situation. You are on the board. A campaign ran in one metro region for twenty
> weeks. It cost 75 thousand euros. Sales went up. Marketing is happy, and now they ask for
> 4 million euros to take the campaign national. You must decide.
>
> What do you actually have? Thirty markets, sixty weeks of weekly sales data. One metro got
> the campaign. The other twenty-nine did nothing. And one detail that matters a lot: the metro
> was **chosen** by the marketing team. It was not picked at random. This is not an A/B test.
>
> To decide, you must answer three questions, in this order.
> One: how much of the sales increase did the campaign actually **cause**? That is attribution —
> the Colgate question again: what would have happened anyway?
> Two: is that increase more than luck? That is significance.
> Three: is the profit worth the price? That is the decision.
>
> Notice the order. Most companies jump straight to question three with a number from question
> one that was never checked. Today we do it properly, and each question needs a different tool.

*[If asked about the fold on "unbiased": "The slide has a precise note on when this measurement
can be trusted. Short version: the method learns the metro's normal behavior from before the
launch, so it does not matter why the metro was chosen — unless the choice used secret knowledge
about the future. We test for that later."]*

## Slide 11 — The data (live)

> This is the raw data. Every line is one market's weekly sales. The white line is our metro.
> At week 40 the campaign starts.
>
> [Run the live demo: show the before/after means, then subtract the cross-market average.]
>
> The simplest possible analysis: compare average sales before the launch with after. You get a
> bump. But watch what happens when I subtract the average of all the other markets — the crowd.
> The bump changes size. That is the whole problem in one picture: part of what you see is the
> campaign, and part is the tide — the economy, the season, everything that moved every market
> at once.
>
> And here is the one number you do not have, and never will: what this metro **would have sold
> without the campaign**. In no file, no dashboard, no report. Everything in Part 2 is a way to
> estimate that one missing number. You already know its name: the counterfactual.

## Slide 12 — Poll: the 12% bump

> Before I show you any method, commit. [Read the poll.] Sales averaged a certain level before
> launch and a higher level after — a bump of about six percent. What is the campaign's true
> weekly effect? Around 2 thousand per week — most of the bump is just trend? Around 7 thousand
> — the simple comparison is roughly right? Or around 14 thousand — double the bump?
>
> [Collect hands. Reveal.]
>
> About double. The economy happened to **dip** right after the launch. The tide went out, and
> it hid half of the campaign's effect. This is the first management lesson of the day: a naive
> before/after comparison is not "roughly right with some noise". It is charged with everything
> else that happened in the world. This time the tide hid a real effect. Next time it will
> flatter a dead one, and you will pay for a campaign that did nothing.

## Slide 13 — Potential outcomes

> The one piece of theory you need today. It fits on this slide.
>
> Our metro has two possible histories for the campaign weeks. History one: sales **with** the
> campaign. History two: sales **without** it. The campaign's true effect is the gap between
> the two histories. That is all "causal effect" means.
>
> The problem: only one history ever happens. Look at the table: three of the four cells are
> real data. The fourth — the metro's sales without the campaign, after launch — is missing.
> Every method you have ever heard of, A/B tests included, is a different way to fill that one
> missing cell.
>
> One more distinction that matters for the money: the effect **per week** and the **total**
> over twenty weeks are different numbers with different uncertainties. The 4-million decision
> rides on the total. Keep that in mind.

*[SKIPPABLE MATH — the notation fold: "precise definitions for those who like them; you will
not need them to follow."]*

## Slide 14 — The data-generating model **[FAST / SKIPPABLE MATH]**

> One honest confession: today's data is simulated. We built the world ourselves. Why? Because
> in a simulated world we **know** the true answer — we planted a 12 percent lift — so we can
> grade every method against the truth. It is exactly Colgate's discipline from this morning:
> recover a planted truth first, then trust the method.
>
> The formula says the world has four ingredients: each market has its own size, a shared trend,
> a shared season, a shared economic wave — and each market feels these shared forces with its
> **own sensitivity**. That last part makes the problem hard, and you will see why.
>
> What matters for today: the planted truth is about 284 thousand euros of extra sales over
> twenty weeks. Remember 284. Every method gets graded against it.

## Slide 15 — Simulate the world (live) **[FAST]**

> [Play with one slider only — the macro shock.]
>
> Ten seconds of demonstration. The dashed blue line is the counterfactual itself — the metro
> in the world without the campaign. In real life this line does not exist. Watch when I make
> the economy more turbulent: the naive before/after estimate becomes garbage, because the tide
> dominates. "Sales went up after we launched" is not evidence. The question is always:
> compared to what?

# ACT II — THE COUNTERFACTUAL

## Slide 16 — Abadie's idea: the synthetic twin

> So how do we fill the missing cell? The idea is genuinely simple.
>
> If our metro had an identical twin — same size, same seasonality, same sensitivity to the
> economy — we could just watch the twin. The twin got no campaign. Its sales during those
> twenty weeks are our answer.
>
> No single market is a perfect twin. But a **blend** can be. Forty percent of market eight,
> plus 32 percent of market twenty, plus 17 percent of market three behaves almost exactly like
> our metro. That blend is the synthetic control — a manufactured twin.
>
> The key property, in business terms: the twin is built to **react to shocks** the same way
> our metro reacts. When the economy dips or the season turns — even in ways nobody predicted —
> the twin dips and turns with it. Whatever gap remains between metro and twin is the campaign.
>
> Strong pedigree: called the most important innovation in policy evaluation in fifteen years,
> and it is the engine inside Meta's GeoLift and Google's geo tools — the tools your media
> agencies already use.

## Slide 17 — The estimator **[SKIPPABLE MATH]**

> This slide is the recipe in formulas. Three business facts, then you may ignore the algebra.
>
> Fact one: the twin is fitted **only on data from before the launch**. The method never sees
> the campaign period while it learns, so it cannot cheat. Same discipline you demand from any
> forecast: no peeking.
>
> Fact two: the blend must be a real recipe — weights positive, summing to one hundred percent.
> You get statements like "40 percent market eight plus 32 percent market twenty". A manager
> can read that, question it, audit it. No market enters at minus 80 percent. It is the
> weights-on-the-table version of what Colgate's projection did in time.
>
> Fact three: after fitting, the effect is a subtraction — actual sales minus twin sales,
> summed over the campaign weeks. Nothing exotic.

## Slide 18 — Inside the convex hull (live) **[FAST]**

> [Drag the treated market in and out of the hull — thirty seconds.]
>
> One picture on why the "real recipe" rule matters. A blend of real markets can only reproduce
> a market that lives **inside** the range of its donors. You can mix coffee and milk; no mix of
> coffee and milk gives you orange juice. When the target sits outside that range, an
> unconstrained model still produces a number — by extrapolating. The constrained one **refuses**.
>
> And the refusal is a feature, not a bug. It is the method telling you: widen the donor pool,
> do not trust me here. So make this a procurement question. Ask any vendor: when does your
> method refuse to answer? If the answer is "never", walk away.

## Slide 19 — What the constraint buys (live) **[FAST]**

> Here we removed the recipe rule and let an ordinary regression do what it wants. Look: the
> unconstrained model fits the past **better** — and predicts the missing counterfactual
> **worse**. It used absurd weights: minus 80 percent of one market, 190 percent of another.
> It memorized noise.
>
> The management lesson: a tighter fit to history is not a better model, and is often a worse
> one. Anyone selling you a model on "look how well it fits the past" is selling the wrong
> metric. You saw the same inversion this morning — the MMM with the backwards ranking fitted
> its history beautifully.

## Slide 20 — Why not just forecast it?

> Somebody always asks: why this old-fashioned blend? Why not gradient boosting, Prophet, a
> neural network? We ran that race. The fancy forecaster fits the past better — again. Its
> campaign estimate lands in the same place as the simple twin. And across twenty-four fresh
> simulated worlds it reconstructs the missing counterfactual clearly worse on average, with
> weights no planner can audit.
>
> The deep reason is a business reason. A forecaster answers: "what comes next, in a world like
> the past?" Our question is: "what would **this** market have done in a world that never
> happened?" You cannot cross-validate that answer — the truth is never observed. So accuracy
> on the past cannot pick your tool. You must pick the tool whose **assumptions you can defend
> in the boardroom**. The simple auditable blend wins the causal job even when it loses the
> forecasting beauty contest.

## Slide 21 — Every shortcut is an assumption (live)

> The slide I most want you to remember from Act II. Four common ways to measure the same
> campaign: before/after; treated versus the average of other markets; difference-in-
> differences — the consultant's favorite; and synthetic control.
>
> Each is really a hidden **claim** about the missing counterfactual. Before/after claims the
> world would have stood still. Treated-versus-control claims other markets are just like
> yours. Difference-in-differences claims all markets ride the economy in parallel. Synthetic
> control claims a blend of markets can mimic yours.
>
> [Live demo: move the two dials.]
>
> Watch the errors as I change the world. When markets react to the economy differently — the
> normal case — before/after and diff-in-diff drift away from the truth. Synthetic control
> stays close, because it matched how the metro **responds**, not just its level.
>
> And the uncomfortable fact: none of these numbers arrives with a warning label. A wrong
> method does not look wrong. More data does not fix it — a wrong claim stays wrong at any
> sample size. The cure is a better claim, not a bigger spreadsheet.

## Slides 22–23 — The one-difference estimators / DiD algebra **[SKIPPABLE MATH]**

> These two slides do in algebra what the dials just showed in pictures: exactly when
> before/after, treated-versus-control, and difference-in-differences give the wrong answer.
> The executive summary is enough:
>
> Before/after fails whenever the world does not stand still — so, almost always. Comparing to
> other markets fails because markets differ in size. Difference-in-differences fixes size but
> still requires every market to ride the economy in parallel — and that assumption dies
> quietly, no alarm. The one bias diff-in-diff cannot remove is precisely the one synthetic
> control removes by construction, because it **chooses** the comparison weights instead of
> hoping equal weights work.
>
> One line worth repeating to any analyst who reports to you: more weeks of data buy precision
> around the **same wrong number**. If the method is biased, patience does not help. Ask which
> assumption the comparison rests on. No answer — the number is decoration.

## Slide 24 — Identification: what must hold

> Every method rests on assumptions. The professional standard: list them, test what can be
> tested. Read this as a due-diligence checklist.
>
> One: the twin must track the metro before launch. Testable — it passes, with a quantitative
> gate. Two: sales must not react **before** the campaign — no leaked launch, no stockpiling.
> Testable with a placebo you will see shortly — passes. Three: the campaign must not touch the
> comparison markets. Ads do not respect borders. This one is **untestable** with statistics —
> it is Colgate's second-launch leak, in space. Mark it; it returns in ten minutes. Four: the
> metro must be reconstructable from the donors, and no single market may hold the answer
> hostage — drop any donor, the answer barely moves. Passes.
>
> Three passes, one honest "cannot test". Remember which one.

# ACT III — IS IT REAL, AND HOW BIG?

## Slide 25 — Poll: is it real?

> The twin says: about 260 thousand euros of extra sales over twenty weeks. New question: real,
> or a lucky metro? Normally you would run a significance test. Here you cannot: every standard
> test measures luck across **many treated units**, and we have one treated metro. You cannot
> measure variation across one thing. The standard machinery is not weak here — it does not
> exist.
>
> And you can invent the replacement yourselves. [Read the poll.] Take each of the 29 markets
> that ran **no campaign**. Pretend, one at a time, that it was the treated one. Run the whole
> twin machinery on it. It should show roughly zero — nothing happened there. Whatever "effect"
> it shows anyway is pure luck: the noise level of our method.
>
> Thirty markets, thirty measured "effects", twenty-nine of them known to be luck. Where does
> our metro's 260 thousand rank?
>
> [Collect. Reveal.]
>
> Rank one of thirty. The most extreme of all. And the rank **is** the test: if the campaign
> truly did nothing, our metro would be just another market, and the chance of ranking first by
> luck is one in thirty — about three percent. You have just reinvented a rigorous statistical
> test using nothing but common sense.

## Slide 26 — Placebo-in-space (live)

> The idea, drawn. The grey cloud: 29 fake "effects" — the luck of the method, measured
> directly. The green line: our metro at 260, standing clear outside the whole cloud.
>
> Conclusion: the effect is real, with about a three percent chance we are fooling ourselves.
> One caveat for your analysts: a comparison market that fits badly can fake a big effect, so
> bad-fit placebos are dropped before ranking — the standard hygiene rule is on the slide.
>
> But hold the applause. "Real" is not "profitable". That is question three, and we are not
> there yet.

## Slide 27 — Interval by test inversion (live) **[SKIPPABLE MATH]**

> One more product from the same placebo idea, then money. We have a point estimate, 260. A
> board should never accept a point without a range. The range: 195 to 335 thousand, with 90
> percent confidence.
>
> How it is built, in one sentence: for every possible "true" effect, we ask whether that truth
> could plausibly have produced our 260 given the luck we measured — and the survivors form the
> range. The mechanics are on the slide for the curious; the demo lets you drag the hypothesis.
>
> Why care about this particular range: it was built with **no model of the noise** — no bell
> curve, no software assumptions, only the placebo logic you invented by hand. That makes it
> the referee for every fancier number that comes later. Any model that contradicts this range
> has explaining to do.

## Slide 28 — Falsification 1: placebo-in-time **[FAST]**

> Two stress tests before the money. First: pretend the launch happened ten weeks earlier, and
> re-run everything. A real method should find **nothing** there — nothing happened. It finds
> nothing: about 1.7 thousand, inside noise. Pass.
>
> What this rules out: leaked launches, stockpiling, sales reacting early. Make it a habit: any
> vendor claiming a lift should show you their method finds zero where nothing happened.

## Slide 29 — Falsification 2: spillover (SUTVA)

> The second stress test is the one I flagged as untestable — the disease you named for Colgate
> this morning, now in space. Our metro's TV and outdoor ads reach the commuter belt. Those
> neighboring markets are in our comparison pool. So the campaign quietly lifts the very
> markets we use as "untreated". The twin gets inflated, and the measured effect **shrinks**.
>
> We cannot test for this in the data — the leak starts exactly at launch, so every check stays
> green. What we can do is simulate it deliberately and measure the damage: with a realistic
> leak, our 260 becomes 236. Two takeaways.
>
> First: the bias only pushes the number **down**. Our estimate is a conservative floor — if the
> campaign clears its cost at 260, a leak cannot overturn the decision.
> Second, and more important: the fix is not statistical, it is managerial. When you **design**
> a geo test, keep the control markets off the campaign's media footprint. The best analysis
> cannot repair a badly designed test. Design beats analysis. Every time.

## Slide 30 — What the statistics says

> Act III complete. Three numbers to carry.
> Is it real? Yes — three percent chance of self-deception.
> How big? 260 thousand euros of incremental sales.
> Give or take? 195 to 335, at 90 percent confidence.
>
> And a satisfying check only a simulation allows: the planted truth, 284, sits inside the
> range. The machinery is honest.
>
> Now — the sentence that loses money in real boardrooms: "The campaign drove 260 thousand of
> sales for 75 thousand of spend. That is a 3.5x return. Roll it out." Every number in that
> sentence is true. The conclusion still does not follow. Why not? Act IV.

# ACT IV — THE DECISION IN EUROS

## Slide 31 — Poll: the margin

> [Read the poll.] The campaign cost 75 thousand. It generated 260 thousand of incremental
> sales. Gross margin is 35 percent. What did the campaign **earn**?
>
> [Collect. Reveal.]
>
> About 16 thousand net. Margin times lift, minus cost: 35 percent of 260 is 91, minus 75 —
> about 16. If you answered "185 — sales minus cost", you made the boardroom classic: you
> treated revenue as profit. The company keeps only the margin on the extra sales; it pays the
> campaign invoice in full. Nürnberger's last-touch trap was a cousin of this one: the
> comfortable metric, wrong by construction.

## Slide 32 — The margin trap (live)

> The general rule — the cheapest lesson of the day. "Return on ad spend" compares incremental
> **sales** to cost, so its break-even is not 1. It is 1 divided by your gross margin. At our
> 35 percent margin: 2.86. You need 214 thousand of incremental sales just to get your 75 back.
>
> [Move the margin slider.]
>
> A software company at 90 percent margin breaks even at 1.1. A grocery chain at 20 percent
> needs 5.0. The **same campaign with the same measured lift** is a good buy for one business
> and a money-loser for the other. If your agency reports "ROAS above 1" as success, that is a
> vanity bar. The real bar is 1 over margin. Ours: 3.47 achieved against 2.86 required. It paid.

## Slide 33 — The decision space (live) **[FAST]**

> Now bring the uncertainty back. Expected profit says the campaign pays at any price below 91
> thousand. But the 90-percent range on profit runs 68 to 117 — and our price, 75, sits
> **inside** it. Translation: probably paid, but a loss is still consistent with the evidence.
> [Slide the price control.] Between "looks profitable on average" and "provably profitable"
> there is a wide dangerous zone, and our campaign lives in it.

## Slide 34 — What you say to the board (classical)

> The memo a competent analyst delivers with classical tools only.
> Real? Yes. Big enough on the point estimate? Yes — about 16 thousand net.
> Confident? **No.** The profit range straddles the price.
>
> Verdict on the €75k pilot: probably a profitable buy, not a confident one. Renegotiate the
> price, or buy certainty with a bigger test. And say the second sentence out loud: this memo
> says **nothing yet about the €4M** — the rollout is not the pilot multiplied.
>
> One more thing, in the last box. There are questions this memo cannot answer, in principle:
> "what is the **probability** the campaign pays?", "what is the highest price this evidence
> would still justify?", "is a follow-up study worth its cost?". Classical statistics answers
> yes/no about where a range sits; it has no language for "78 percent chance". Managers
> allocate money in exactly that language. That language exists — it is the Bayesian layer of
> this same toolkit, and it is where this course goes next. Today we stop at the honest
> classical verdict, which is already worth real money — watch.

## Slide 35 — What €4M actually buys

> We still owe the board the real question: the four million. Here is the number in the
> marketing deck: 4 million is 53 pilot budgets; 53 times the pilot's lift, at our margin,
> nets about **plus 860 thousand**. Every step is correct.
>
> [Poll the room: who approves the €4M? Same device as slides 12 and 31 — let them commit.]
>
> Now do the one thing the marketing deck did not: carry the **interval**, not the point. And
> be maximally generous — assume the campaign works nationally exactly as well as in the metro.
> Perfect transport, every euro. Even then, the 90 percent profit interval on the 4 million
> runs from **minus 360 thousand to plus 2.25 million**. It straddles zero. At the most
> optimistic assumption we can write down, we cannot show the 4 million pays.
>
> And that assumption is a ceiling. Two forces only pull it down: 4 million over 30 markets is
> 133 thousand per market — nearly double the pilot's intensity, and advertising has
> diminishing returns; and one metro is not the country. [Drag δ down.] Below about 64 percent
> surviving, the rollout provably loses.
>
> That is the whole frequentist verdict, and it needs no probability model: at its best case
> the 4 million is not provably profitable, and it can provably lose. **Do not commit the 4
> million on this evidence.** The next slide is what you do instead.

## Slide 36 — Measure it, don't guess it

> The answer is not "yes" and not "no" — it is "not on this evidence". And notice why the
> evidence cannot decide: the interval is wide because there is **one** treated market. You
> cannot think your way out of that. Re-running the model, adding weeks, arguing about
> assumptions — none of it narrows the interval. Only more treated markets do.
>
> [Ask: so what would you spend? Take answers. The honest one is "not four million yet" — that
> is the lesson, not a dodge.]
>
> Two moves. First, step zero — it gets a laugh because it is so obvious and so often skipped:
> before you spend a million on evidence, spend an hour checking you have not already bought
> it. A firm with a 4-million budget has prior pilots, a media-mix model, agency benchmarks.
> The answer may be in a drawer.
>
> Second, if it is not: measure it, do not model it. Run the campaign in **eight markets chosen
> to look like the nation**, at full national intensity — about 133 thousand each, 1.07 million
> total. Because the cells span the country, the measured lift **is** the national lift, with
> an interval tight enough to clear the 4 million or kill it. And recognize the shape: this is
> HelloFresh's loop from this morning, bought once — the model asked for ground truth, and we
> went and bought the experiment.
>
> The discipline that separates a test from theatre: write the release rule **before** the data
> lands. "Release the remaining 2.9 million only if the measured profit interval clears zero."
> One quarter later you have a national campaign at a size the evidence supports.
>
> [Delivery notes: "transportability" is classroom language — in a client room say "how much of
> this travels". The fold prices this information at about 320 thousand euros using the course's
> Bayesian machinery — far above the test's true cost — but the decision to test was already
> made here, classically.]

---
---

# FINALE — THE PATTERN

## Slide 37 — The tools were the product too **[FAST]**

> Almost done. Three footnotes that are really credentials.
>
> Everything you just used exists as open source, industrialized by the same consultancy:
> CausalPy carries synthetic control, interrupted time series, difference-in-differences and
> regression discontinuity — today's method and its whole quasi-experimental family. Its launch
> example is the sentence this session opened with: exposure you cannot randomize, causal
> impact you still need. PyMC-Marketing is the MMM library behind the calibration story — and
> one client's budget-allocation approach came back as a pull request, which is what a healthy
> open-source business looks like. And the consultancy's own webinar agenda — geo tests, MMM,
> synthetic control, diff-in-diff, instrumental variables — is literally this session's
> syllabus. You did not take a course *about* the industry today. You took the industry's course.

## Slide 38 — The pattern in every engagement

> Compress the whole session to three lines.
> The deliverable is a **counterfactual** — a world minus the launch, the campaign, the
> exposure — priced in euros.
> An **experiment anchors** every observational model. Calibration is the product, not a luxury.
> And **uncertainty prices the decision** — a board acts on the probability it pays and on the
> headroom, not on a point estimate.
>
> One last exhibit, because it is 2026: we ran a vanilla coding agent on deliberately
> adversarial marketing data. It fit a model and confidently recommended budget reallocations.
> Confidently wrong. The honest system explored eleven model specifications, none converged,
> and returned: "No valid model found. Run a geo-holdout experiment." Even the machines, at
> their best, arrive at Part 2's closing advice: run the experiment.

## Slide 39 — One breath

> One breath, and we stop. What a Bayesian consultancy actually sells: counterfactuals,
> calibrated by experiments, priced as probabilities. You have now watched real clients buy it,
> and you have built one yourself.
>
> Every number today is pinned to a public source — the list is on the backup slide. The
> notebooks behind this session are the course repository. Both of us consult for PyMC Labs:
> say hello.
>
> [When Part 3 (instrumental variables) runs in the same sitting, do NOT stop here: say "after
> the break, the last tool — what to do when even the geo test is impossible" and hold this
> slide's close for the very end of the 1.5 hours.]

## Slide 40 — Sources (backup)

> [Only if asked.] Every fact from Part 1, pinned to its public post with the exact quote and
> retrieval date; Part 2's numbers are baked from the executed course notebooks and verified
> against a claims registry at build time. Nothing on these slides was typed by hand.

---
---

# If you are told "you have 45 minutes" on the day

Cut in this order: slide 37 (provenance) → 22–23 to their one quoted line → 19 → 14–15 to one
sentence each → 33 (fold its point into 34) → the second poll of whichever act runs long.
Never cut: 2–6 (who we are + the hook), 10–13, 16, 18, 21, 25–26, 29, 31–32, 34–36 (35–36
above all), 38–39.

# The engagement beats (do not silently skip)

Polls: 3 (route the call) · 8 (price the engagement) · 12 (the 12% bump) · 25 (rank the metro)
· 31 (the margin) · 35 (approve the €4M — hands, before the interval). Open floor: 5 (what
would break it). Live widgets to hand to a student: 5 (second launch), 6 (lift-test toggle),
15 (macro shock), 21 (estimator dials), 27 (drag the hypothesis), 32 (margin slider),
35 (drag δ). The polls are the lecture's spine: commitment before revelation, every time.
