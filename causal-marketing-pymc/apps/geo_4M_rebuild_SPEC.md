# Implementation Spec v2 — Rebuilding the €4M Decision (slide 28 → 28a/28b/28c)

**For:** an LLM with file access to this repo.
**Task:** replace one slide with three, update dependent slides, update both narrative files,
update the claims registry, rebuild, verify.
**Do not** restructure anything else in the deck.

**v2 changes over v1** (all binding):

1. **The deck is generated.** All edits go to `apps/geo_slides_src.html`; the registry
   `apps/geo_claims.yaml` is law; `apps/verify_geo_deck.py` passing is the acceptance gate.
   v1 targeted the generated file and never mentioned the harness. (Part 0.1, 0.5, Part 5.)
2. **Numbers reconciled with the deck:** naive rollout net is **+€860k** (registered, from the
   actual series — not €850k recomputed from rounded €260k); pilot renegotiation target is
   **€67k** (registered headroom — not €68k). (Parts 2.4, 2.6.)
3. **One test recommendation across the deck.** The Act V / deliverable "~4-market test" and the
   new 8-market design are reconciled explicitly — the deck must not recommend two different
   tests. (New R7; Parts 2.6, 3.5, 3.6.)
4. **δ > 1 reconciled.** The kept 28a chart calls δ > 1 "unreachable"; the new 28b slider
   produces δ_plaus > 1 at sub-pilot intensity. One reconciling sentence each side. (Parts 2.4, 2.5.)
5. **Inference-floor claim corrected.** p ≥ 0.033 is true for the 1-treated pilot, not for the
   8-pair randomized design (floor ≈ 1/2⁸ ≈ 0.004). Reworded. (Part 2.6.)
6. **Option C de-strawmanned; options table settled by the deck's own VOI number** (≈€322k,
   registered), not by assertion. (Part 2.6.)
7. **Competitive response flagged as downside at national scale** — one line, teaches something,
   costs nothing. (Part 2.4.)
8. **Timing arithmetic sums.** Act IV is ~10 min in the speech guide (not v1's 15); goes to ~13,
   with named cuts totalling 3:00. (Part 4.1.)
9. **Slide numbering convention stated.** All numbers herein use the speech-file convention;
   every deck edit is anchored by `data-t`, never by position. (Part 0.2.)

---

# PART 0 — Pipeline and context. Read before touching anything.

## 0.1 The deck is GENERATED — the edit → build → verify loop

```
edit    apps/geo_slides_src.html          (the ONLY editable deck file)
build   .venv/bin/python apps/build_geo_slides.py     (or: make html-geo)
verify  .venv/bin/python apps/verify_geo_deck.py      (exit 0 required; FAILs block, WARNs explain)
```

- `apps/geo_lift_slides.html` is build output. **Never hand-edit it.** Any v1 instruction that
  names it means the src file.
- Scalars in prose are tokens `{{nb07.xxx}}` substituted from the executed shards at build time;
  an unknown token is a build error. New prose numbers that exist as shard tokens must use the
  token, not a typed literal.
- The claims registry header states the law: **"No new number enters the deck without an entry
  here."** Every number this spec introduces gets a registry entry (Part 0.5).

## 0.2 Slide numbering convention

The deck has 47 `<section>`s (45 content + title + close). The speech/emphasis files number
content slides excluding the title slide, so **speech "slide 28" = deck section 29**. All slide
numbers in this spec use the **speech convention**. It does not matter for deck edits: every
deck edit below is anchored by its `data-t` string. Do not locate any slide by position.

The slide being replaced: `data-t="The €4M call, without a posterior"`. The three new slides use
new `data-t` values (Parts 2.4–2.6) and keep the **existing** section label
`data-sec="Act IV · The decision in euros"` — the "scaled up" flavour goes in the `.kicker` line,
as the current slide already does. Do not invent a new `data-sec`; it would split the contents
overlay.

## 0.3 Established numbers — load-bearing, never change them

| Quantity | Value | Registry / source |
|---|---|---|
| Measured lift τ̂ (20 wk) | €260k (exact series sum ≈ 260.3) | shards; classical_total |
| 90% interval on τ | [€195k, €335k] | slide "Interval by test inversion" |
| Gross margin m | 0.35 | price_and_margin |
| Pilot cost c | €75k | price_and_margin |
| Break-even lift c/m | €214k (75/0.35 = 214.3) | margin-trap slide |
| Break-even iROAS 1/m | 2.86 | margin-trap slide |
| Achieved iROAS | 3.47 | margin-trap slide |
| p-value | 0.033 (rank 1/30) | significance slides |
| Markets | 30 (1 treated, 29 donors) | panel_shape |
| National budget | €4M; R = 4000/75 ≈ 53.3 | rollout_reach |
| Naive rollout net at δ=1 | **+€860k**, interval [−€360k, +€2.25M] | rollout_classical_net / _interval |
| Required δ central | **0.82** (registered 0.823) | rollout_delta_breakeven_classical |
| Required δ band edges | 0.64 / 1.10 | rollout_delta_zone_* |
| Pilot P(pays) | 0.78 | rollout_p_at_delta1 |
| Pilot headroom (renegotiation target) | **€67k** | headroom (shard nb07.headroom) |
| VOI, pilot buy | ≈ €2k | Act V slides |
| VOI vs the rollout (δ=0.8) | **≈ €322k** | rollout_voi_peak |
| Planted truth (simulation) | ≈ €284k | DGP slide |

Rule: where a spec table below says €260k / +€850k-style rounded arithmetic, the deck states the
**registered** value (+€860k, 0.82, €67k). The spec's illustrative tables (δ_plaus, banded
profits) are computed from τ ∈ {195, 260, 335} exactly as shown and registered as new entries.

## 0.4 Markup conventions — mirror the existing slide 28 exactly

- `<section class="slide" data-t="SHORT TITLE" data-sec="Act IV · The decision in euros">`,
  `.kicker`, `<h2>`, `.sub`, `.sbody`
- Colours **only** via CSS variables (`--navy --ink --muted --blue --orange --green --gold --red`
  etc.). Never hardcode hex; the dark theme at `:root[data-theme="dark"]` will break.
- Display math `\[ ... \]`, inline `\( ... \)`; `<div class="eqbox">` with `<span class="lbl">`
- Fold-outs: `<details class="mathfold"><summary><span class="tw">▸</span>…</summary><div class="mfbody">…</div></details>`
- Live demos badged `▶ LIVE`; reuse the existing slider/canvas machinery (`svgDelta`, `dzD`)
  for the demo moved to 28a; new ids for the 28b slider.

## 0.5 Registry work — do this alongside the slide edits, not after

**Re-anchor** the six entries whose `slides:` lists `"The €4M call, without a posterior"`
(`rollout_reach`, `rollout_classical_net`, `rollout_classical_interval`,
`rollout_delta_zone_provable`, `rollout_delta_zone_disproven`,
`rollout_delta_breakeven_classical`) to whichever of the three new `data-t` titles now displays
each number. Nothing else about those entries changes.

**Add new entries** (ids indicative; follow the file's format — `expr` may be pure constant
arithmetic where the number is arithmetic, `texts` for strings on multiple slides):

| id | text | check |
|---|---|---|
| delta_required_band | "[0.64, 1.10]" | expr `(75/0.35)/335` = 0.64; hi `(75/0.35)/195` = 1.10 |
| delta_plaus_corner_lo | "0.55" | expr `(1-0.772*0.4)*(4000/2250)**(0.6-1)` = 0.549, tol 0.01 |
| delta_plaus_central | "0.65" | expr `(1-0.772*0.3)*(4000/2250)**(0.7-1)` = 0.646, tol 0.01 |
| delta_plaus_corner_hi | "0.75" | expr `(1-0.772*0.2)*(4000/2250)**(0.8-1)` = 0.754, tol 0.01 |
| rollout_profit_band | "−€2.00M", "−€0.85M", "+€0.69M" | expr `0.35*d*(4000/75)*t - 4000` at the three corners |
| breakeven_budget_center | "€1.8M" | expr `2250*((1-0.772*0.3)/0.823)**(1/0.3)` ≈ 1787, tol 25 |
| breakeven_budget_band | "€0.7M", "€4.1M" | same solve at required 1.10 / 0.64 → ≈685 / ≈4150 |
| test_k_power | "k ≈ 4.3" / "≈ 8 at CV 0.4" | expr `((1.645+0.8416)*0.30/0.36)**2` = 4.3; CV 0.4 → 7.65 |
| test_cost | "€1.07M" | expr `8 * 4000/30` = 1067, tol 3 |
| per_market_intensity | "€133k", "1.78×" | expr `4000/30` = 133.3; `133.3/75` = 1.778 |

**Illustrative-input convention.** CV ∈ [0.2, 0.4] and β ∈ [0.6, 0.8] are stated assumptions,
not measurements. Register the numbers *derived* from them (above) with a comment block:
`# illustrative-input chain: CV/beta are client-owned assumptions declared on-slide; these
entries pin internal consistency, not truth.` The on-slide flags (R1) carry the epistemics; the
registry carries the arithmetic.

**DGP cross-check (bounded, 15 min).** The case is simulated with per-market sensitivity, so the
DGP implies an actual effect CV. Compute it (from the baked DATA bundle or nb07's DGP
parameters). If it falls inside [0.2, 0.4], add one clause on 28a: *"the simulation's own
heterogeneity sits inside this band."* If it falls outside, keep the band and flag CV explicitly
as an out-of-model client input. Either way the deck cannot be caught assuming a heterogeneity
its own simulation contradicts.

---

# PART 1 — Diagnosis (condensed; drives the structure)

Six defects in the current slide, each answered by the rebuild:

1. **δ is one scalar hiding three mechanisms** (selection / saturation / execution) with
   different evidence sources → 28a decomposes it.
2. **δ presented as unknowable when it is boundable** → 28a constructs a banded identified set.
3. **The verdict is unactionable** ("not provably profitable, so no") → 28c says what would be
   sufficient, at what cost, by what date.
4. **A structural property never surfaced:** required δ = c/(m·τ) is budget-invariant (R cancels),
   and equals break-even lift ÷ measured lift = 214/260 — the slide-25 margin trap returning
   → 28b's call-out box and identity.
5. **The remedies are buried in a fold-out** → promoted to 28c's body.
6. **The reasoning collapses to point estimates at the decisive moment** → the interval
   discipline of Part 2.2, which **changes the conclusion**: from "it loses money" to "the
   evidence cannot size the rollout within a factor of six — buy the information."

Keep: the δ formulation and profit equation; the 0.64 / 0.82 / 1.10 break-evens; the "chosen
pilot travels as a ceiling" phrasing; the live band-vs-δ chart (demoted to 28a).

---

# PART 2 — The fix

## 2.1 Structure

| Slide | data-t | Question it answers | Role |
|---|---|---|---|
| 28a | `What €4M actually buys` | "What does €4M actually buy?" | Decomposition |
| 28b | `Required vs plausible` | "So do we do it?" | **The recommendation** |
| 28c | `The test that removes δ` | "What would it take to know?" | Design |

28b is the destination. 28a makes it credible; 28c makes it actionable.

## 2.2 The interval discipline — read before implementing 28b

Every quantity on the path to the recommendation carries a band. No naked point estimates on 28b.

**(i) Required δ from the τ interval:** 214/τ at τ = 335 / 260 / 195 → **[0.64, 1.10]**,
central 0.82.

**(ii) Plausible δ from the two soft parameters** (selection = 1 − 0.772·CV, chosen market
≈ 78th percentile, linear approximation — flag it; saturation = 1.778^(β−1)):

| Scenario | CV | β | Selection | Saturation | δ_plaus at €4M |
|---|---|---|---|---|---|
| Pessimistic | 0.4 | 0.6 | 0.691 | 0.794 | **0.55** |
| Central | 0.3 | 0.7 | 0.768 | 0.841 | **0.65** |
| Optimistic | 0.2 | 0.8 | 0.846 | 0.891 | **0.75** |

**(iii) The two bands side by side — the headline visual.** Required [0.64, 1.10] vs plausible
[0.55, 0.75]; overlap only in **0.64–0.75**. The rollout cannot be ruled out; the weight of
evidence sits against it.

**(iv) Rollout profit at €4M, banded** (profit = 0.35·δ·53.33·τ − €4M):
pessimistic (0.55, 195) → **−€2.00M**; central (0.65, 260) → **−€0.85M**;
optimistic (0.75, 335) → **+€0.69M**.

**(v) Break-even budget, banded** (solve δ_plaus(B) = 214/τ, central CV/β):
τ = 335 → **€4.14M**; τ = 260 → **€1.78M**; τ = 195 → **€0.68M**.
**The supportable size spans [€0.7M, €4.1M] — a factor of six.** This is the single most
important number the analysis produces.

**The conclusion the intervals force:** not "€4M loses money" (too strong; the optimistic corner
is +€0.7M) but *"the evidence cannot size this rollout within a factor of six — that is not a
decision, it is a confession. Buy the information."* More defensible, harder to attack, easier
to sell: it is "not yet at this size," not "no."

## 2.3 Consulting-practice requirements — apply throughout

- **R1 — Assumptions are client-owned.** CV and β are *a structure to be filled in with the
  client*: "two numbers to agree with marketing and finance before the next board meeting — not
  numbers we can produce for you." On-slide, not in a fold-out.
- **R2 — Check prior evidence before recommending a new test.** Step zero on 28c, above the
  design: prior pilots, the MMM's response curve (which *is* β), agency benchmarks, historical
  spend variation. One meeting may close the whole gap.
- **R3 — Band the numbers; never over-precise.** "Roughly €0.7M–€4M, centred near €2M." False
  precision invites the client to litigate decimals.
- **R4 — Frame as a path, not a refusal**, with dates and an answer to "what runs meanwhile."
- **R5 — Present options honestly, price them, recommend one.** No strawman rows; the table is
  settled by the deck's own VOI number (≈€322k), not by assertion.
- **R6 — Language.** "Transportability" is fine in the lecture; the speech file notes that in a
  client room it is *"how much of this travels."*
- **R7 — One recommendation per deck.** The 8-market design must be THE test everywhere the deck
  recommends a test (28c, Act V €4M slide, the deliverable). The existing "~4 markets" stays only
  where it is a *power-only posterior calculation* (slide 33's poll), with the bridge stated:
  power alone says ~4–5; spanning the national mix at deployment intensity pushes it to 8.

## 2.4 SLIDE 28a — "What €4M actually buys"

`data-t="What €4M actually buys"` · `data-sec="Act IV · The decision in euros"` ·
kicker `Act IV · The decision in euros, scaled up`
**Heading:** `Scaling up is not multiplication` · **Deck line:** `€4M is 53 pilot-budgets. It is
not 53 pilots.`

**Block 1 — the naive computation, stated sympathetically.**

```
€4M ÷ €75k        = 53.3 pilot-equivalents
0.35 × 53.3 × τ̂  = €4.86M gross profit
− €4M             ≈ +€860k   →  approve
```

Use the registered value **+€860k** (entry `rollout_classical_net` — it is computed from the
actual series; do not retype €850k from rounded €260k). Label: *"This is the number in the
marketing deck. Every step is arithmetically correct."*

**Block 2 — the two margins.** Extensive: €4M ÷ 30 = **€133k per market**; 29 of them were never
pilot candidates; the treated metro was *chosen*. Intensive: €133k vs €75k = **1.78× intensity**
up a concave response curve — applies even to a perfectly representative market. Framing line:
**"Different problems, different fixes. Only the first is about which metro you picked."**

**Block 3 — the three components, with bands (R1, R3, v2 change 7).**

| Mechanism | What it is | Evidence source | Range |
|---|---|---|---|
| Selection | Chosen metro vs national mix | Covariates of the 30 markets; ask marketing why this one | 0.69 – 0.85 |
| Saturation | 1.78× intensity, concave response | Firm's own historical spend variation | 0.79 – 0.89 |
| Execution / competition | Agency attention, fatigue, auction response | Elicitation only | ≈ 1.0 — **treat as downside at scale** |
| **Combined at €4M** | | | **0.55 – 0.75** |

On the execution row, one flagged line: *"set to ≈1 here to keep two knobs, but competitors
ignore a metro pilot and respond to a national campaign — at scale this is downside, not noise."*

On-slide, not folded (R1): these ranges come from stated assumptions — effect CV 0.2–0.4,
response elasticity β 0.6–0.8 — not from this dataset. *"The structure is ours; the values are
yours."* Add the DGP cross-check clause per Part 0.5.

**Fold-out — "Where the ranges come from."** Selection: chosen market near the 78th percentile
of a normal effect distribution → national mean ≈ (1 − 0.772·CV) of it (first-order
approximation — say so); CV 0.2/0.3/0.4 → 0.85/0.77/0.69; checkable from the panel's covariates.
Saturation: lift ∝ spend^β ⇒ per-euro lift ∝ spend^(β−1); at 1.78× and β = 0.6/0.7/0.8 →
0.79/0.84/0.89; checkable from the firm's own spend variation.

**Live element.** Move the existing δ-band chart (ids `svgDelta`, `dzD`, `dzDv`, `dzRead`) here
unchanged, **except** the caption's "the grey strip past δ=1 is unreachable" becomes: *"past
δ=1 is unreachable **at this intensity** — a chosen pilot is a ceiling when you spend like the
pilot; the next slide varies the spend."* (Reconciles with 28b's slider, where δ_plaus > 1 at
sub-pilot intensity. Verify the chart still binds after relocation.)

**Emphasis-sheet line:** 🎯 *€4M is 53 pilot-budgets, not 53 pilots. Two different problems —
more markets, more money per market — and only one is about which metro you picked.*

## 2.5 SLIDE 28b — "Required vs plausible" — THE RECOMMENDATION SLIDE

`data-t="Required vs plausible"` · same `data-sec`/kicker as 28a
**Heading:** `The bands barely overlap` · **Deck line:** `Stop asking what δ is. Ask what δ
would have to be.`

The most important slide in the deck. **No naked point estimates anywhere on it.**

**Block 1 — the inversion.** You cannot estimate δ from one treated market. So invert: **what
would δ have to be for this to work, and is that credible?**

**Block 2 — required δ, and the identity.**

\[ \delta^{*} \;=\; \frac{c}{m\,\tau} \;=\; \frac{\tau_{\mathrm{BE}}}{\tau} \;=\; \frac{€214\mathrm{k}}{\tau} \]

In words on the slide: *required δ = break-even lift ÷ measured lift.* Same €214k as the margin
trap — the margin trap and the €4M decision are the same arithmetic. Required δ ∈ **[0.64,
1.10]**, central 0.82.

**Call-out box — the property that surprises everyone:** *Required δ does not depend on the
budget. €4M or €400M — R scales with the budget and cancels. Spending less does not lower the
bar. What it does is raise plausible δ, by reducing saturation.*

**Block 3 — the two bands (headline visual).** Horizontal bands on a δ axis 0.4–1.2: required
[0.64, 1.10] in `--blue`; plausible [0.55, 0.75] in `--orange`; overlap 0.64–0.75 shaded
`--gold`, annotated *"The rollout is not ruled out. It survives only in this sliver."* Two
bands, not two numbers.

**Block 4 — rollout profit at €4M, banded** (table from 2.2(iv)). On-slide statement: *"Central
case is a loss of €0.85M. The range runs from −€2.0M to +€0.7M. We cannot prove €4M loses
money — and nobody should commit €4M on that basis."*

**Block 5 — the break-even budget band** (table from 2.2(v)). Display prominently: **the
right-sized rollout is somewhere between €0.7M and €4.1M — a factor of six.** The framing line
the slide exists to deliver, verbatim:

> *"The evidence does not tell us the rollout is wrong. It tells us we cannot size it within a
> factor of six. That is not a decision — it is a confession, and it is the reason to buy
> information rather than commit capital."*

**Block 6 — ▶ LIVE: the budget slider (new; build it).**

- Control: national budget B, €0.5M–€6M, default €4M. New element ids (do not reuse `dzD`/`rollD`).
- Chart, x = B, y = δ: **required δ** as a flat band [0.64, 1.10], centre line 0.82 — flat
  because budget-invariant; make the flatness visually obvious. **Plausible δ** as a falling
  band \( \delta_{\text{plaus}}(B) = \text{sel} \times (B/2250)^{\beta-1} \) (B in €k;
  2250 = 30 × 75 = pilot-intensity-equivalent national budget), corners (0.691, 0.6) and
  (0.846, 0.8), centre (0.768, 0.7). Shade the overlap region.
- Readout panel: per-market spend · intensity multiple · δ_plaus band · required band · rollout
  profit band · whether the bands overlap at this B.
- Annotate the centre-line crossing ≈ €1.8M: *"central break-even — not a target."*
- Where the plausible band exceeds 1 (B below ≈ €2.25M), annotate: *"δ > 1: below pilot
  intensity you climb the concave curve — the ceiling argument holds only at equal spend."*

Anchor table (verify in the readout):

| B | €/market | Intensity | δ_plaus (central) | Required (central) |
|---|---|---|---|---|
| €4.0M | €133k | 1.78× | 0.65 | 0.82 |
| €3.0M | €100k | 1.33× | 0.70 | 0.82 |
| €2.5M | €83k | 1.11× | 0.74 | 0.82 |
| €1.8M | €60k | 0.80× | 0.82 | 0.82 |
| €1.0M | €33k | 0.44× | 0.98 | 0.82 |

**Block 7 — verdict, with the caveats that make it honest.**

> **Do not commit €4M.** Required δ [0.64, 1.10] and plausible δ [0.55, 0.75] overlap only
> marginally; central expected profit is −€0.85M.
> **The rollout is not a bad idea. €4M is an unsupportable size** — and the evidence cannot tell
> us the supportable one within a factor of six.
> Two caveats, on the slide (R3): (1) the break-even budget is where expected profit is *zero*,
> not where the rollout is attractive — do not read €1.8M as a target; (2) the model implies an
> interior optimum well below €1M, a sign the concavity is being extrapolated far outside its
> support on one data point — **use this model for direction, never for optimisation.**

**Fold-out — "What would make this wrong."** (1) If marketing picked the metro for operational
convenience rather than promise, the selection haircut largely vanishes and plausible δ rises
toward 0.85 — above the central requirement; *a five-minute conversation that moves the answer
more than any modelling.* (2) If "national" is a larger footprint than these 30 markets, €4M may
buy pilot-level intensity and the saturation haircut disappears. (3) β and CV are the two soft
inputs; both estimable from the client's own history. (4) Spillover biases τ̂ *downward* (the
SUTVA falsification slide), so true lift may exceed €260k — this pushes **toward** approval;
report it, do not only report conservative-sounding caveats.

## 2.6 SLIDE 28c — "The test that removes δ"

`data-t="The test that removes δ"` · same `data-sec`/kicker
**Heading:** `Do not estimate δ. Design it away.` · **Deck line:** `Before you buy evidence,
check you have not already bought it.`

**Block 0 — check for prior evidence FIRST (R2), above the design.** A firm with a €4M national
budget almost certainly has: prior geo pilots and their national follow-through · an MMM with a
fitted response curve — which *is* β · agency pilot-to-national benchmarks · historical spend
variation across markets — which also gives β. Both soft parameters may already exist inside the
client. On-slide: *"Step zero costs one meeting and may close the whole gap."*

**Block 1 — the design insight.** A multi-cell test **stratified across the national mix** does
not estimate δ — it **removes δ as a parameter**. With treated markets spanning the national
covariate distribution, you measure the national-mix-weighted effect directly. Nothing left to
transport. This is why the recommendation is a test, not a better model.

**Block 2 — sizing, from the economics.** MDE from the decision, not convention: distinguish
δ = 1 from δ = 0.64 — a 36% shortfall; the 5%/80% convention has no standing here. Use the right
variance: **between-market effect heterogeneity**, not within-market measurement noise (the
placebo cloud's ≈€30k sd would absurdly suggest one market suffices).

\[ k \;\ge\; \Bigl[\frac{(z_{0.95}+z_{0.80})\cdot \mathrm{CV}}{\Delta}\Bigr]^{2} = \Bigl[\frac{2.49 \times 0.30}{0.36}\Bigr]^{2} \approx 4.3 \]

**5 markets on power grounds; 8 in practice** — enough cells to span the covariate distribution:
a design constraint, not a statistical one; say so. At CV 0.4 the power requirement alone rises
to ≈8; state the sensitivity, not a single k. **Bridge line (R7):** *"the posterior arithmetic
earlier in the deck said ~4 markets close the probability gap — that is the power-only floor;
stratification and deployment intensity are what push it to 8."*

**Block 3 — constraints that bind.**

- **Randomise.** Matched pairs on pre-period trajectory — a model-free referee, exactly what the
  real-data act demonstrates.
- **Test at deployment intensity** (~€133k per market), so selection *and* saturation are
  measured in one test. 8 × €133k ≈ **€1.07M**.
- **Controls off the media footprint** — the untestable assumption from the identification and
  spillover slides; reduces the donor pool, costs power; flag at design time.
- **Inference floor — corrected wording (v2 change 5):** *"the pilot's design had a floor: one
  treated market among 30 means a permutation p can never beat 1/30 ≈ 0.033 — no duration fixes
  that, only more treated units. The 8-pair randomized design breaks the floor (2⁸ assignments
  → p as low as ≈ 0.004). That is what the extra markets buy statistically."* Do NOT present
  0.033 as a constraint on the new design.
- **Duration.** Flight plus cooldown long enough to verify no carryover — the real-data act
  shows the effect switching off with spend; measure it, don't assume it.

**Block 4 — options table (R5, honest version).**

| Option | Spend now | Time to answer | What you learn | Risk / cost |
|---|---|---|---|---|
| **A — Commit €4M now** | €4M | — | The answer, at full exposure | Central −€0.85M; range −€2.0M to +€0.7M |
| **B — Staged: €1.07M, 8 stratified markets at national intensity** ✔ | €1.07M | ~20 wk + 4 wk read | δ removed; national-mix effect measured directly | Delays full rollout one quarter |
| **C — Small national at €1.5M, measured** | €1.5M | ~20 wk | Something — but unstratified and at ≈ pilot intensity, so δ at €4M stays open | Likely repeats this exact meeting in six months |

**Settle the table with the deck's own number (R5):** *"Act V prices information against this
rollout at ≈ €322k. Option B's measurement overhead is a fraction of that — the €1.07M is real
advertising that works while it informs. Option A pays up to €2M to learn the same thing the
hard way; C spends €1.5M without closing the question."* One flagged sentence on delay: *"the
cost of waiting a quarter is real (seasonality, competitor moves) — banded honestly it is small
against a central-case loss of €0.85M, but check the fiscal calendar before presenting."*
**Recommend B.**

**Block 5 — the path, with dates (R4).** Week 0 — one meeting: pull prior pilots, MMM
elasticity, agency benchmarks (step zero). Week 1–2 — design and market selection; pre-commit
the release rule. Week 3–23 — 8-market test at national intensity, €1.07M. Week 24–27 — read
out; δ replaced by a measurement. Week 28 — release the remaining €2.9M, or resize, on the
pre-committed rule. *"You get the national campaign. You get it one quarter later, and you get
it at a size the evidence supports."* Answer the in-the-meantime question on the slide: existing
always-on activity continues unchanged; the test cells *are* national spend, geographically
staged.

**Block 6 — the pre-committed decision rule** (visually distinct box):

> *"Release the remaining budget if and only if the lower bound of the 90% interval on
> national-mix-weighted profit clears zero — at the budget the test's measured response curve
> supports."* Written before the data lands. Without this, the test is theatre.

**Block 7 — the recommendation in full.**

> **1.** Step zero: check internal evidence for β and CV before spending anything.
> **2.** Do not commit €4M — required and plausible δ overlap only marginally, and the
> supportable size is unresolved across a factor of six.
> **3.** Release €1.07M across 8 stratified markets at national intensity, randomised, with the
> release rule pre-committed.
> **4.** Separately: renegotiate the pilot. The evidence supports **€{{nb07.headroom}}k** (≈
> €67k), not €75k. *(Use the token; this is the deck's established headroom number — v1's €68k
> was a drift and is wrong.)*

**Fold-out — "What the client hands the board."** A two-page memo: pilot result with interval ·
required-vs-plausible bands as one chart · the options table · the pre-committed rule · the four
ways it could be wrong. Plus a one-page design spec with budget and dates.

---

# PART 3 — Dependent changes elsewhere (anchor every edit by data-t)

## 3.1 `data-t="The margin trap (live)"` — one sentence
After the break-even iROAS block: *"Hold onto €214k. It returns as the hinge of the €4M
decision."*

## 3.2 `data-t="What you say to the board (classical)"` — retarget the handoff
Closing line hands off to 28a: *"And this memo is about €75k. The question on the table is €4M —
and that is not the same question multiplied."*

## 3.3 `data-t="The €4M decision"` (Act V) — retarget its Act IV references (v2 change 3)
This slide's `.sub` currently banks the OLD Act IV verdict ("never provable, provably-not below
δ ≈ 0.64") and repeats "a number the data cannot supply, which is why it is a slider here and
not a footnote" — both now stale. Update the `.sub` to bank the NEW verdict: *"Act IV banked the
action: the bands barely overlap, the supportable size is open by a factor of six. The posterior
adds the two numbers the bands could not produce: the probability, and the price of
information."* Update the δ bullet: the data cannot supply δ, **but Act IV bounded it** — the
slider explores the band. Do not change the slide's numbers (P = 0.78, €2k, the VOI span — all
registered).

## 3.4 `data-t="Poll: buy more evidence?"` — no edit needed
Its "~4 markets close the 0.78→0.9 gap" stays: it is the power-only posterior calculation.
The bridge to 8 lives on 28c (Block 2) and in the speech file. Verify no other slide states a
market count for the recommended test.

## 3.5 `data-t="The deliverable"` — update the recommendation paragraph
Replace the recommendation sentences inside the quoted memo, **keeping every `{{nb07.*}}` token
intact** (p_ratio, cl_total, margin, cl_profit, headroom). New recommendation text:

> *"Do not commit €4M. The rollout requires 64–110% of the pilot's per-euro performance to
> travel, and plausibly delivers 55–75%; central expected profit is −€0.85M on a range of −€2.0M
> to +€0.7M, and the supportable size is unresolved between €0.7M and €4.1M. Release €1.07M
> across 8 stratified markets at national intensity first, with the release rule fixed in
> advance. For this buy alone: renegotiate toward €{{nb07.headroom}}k or accept the four-in-five
> bet explicitly."*

Also update the summary-table row "Value of perfect information": "≈ €2k (this buy) ·
~4-market test vs rollout" → "≈ €2k (this buy) · 8-market stratified test vs rollout (€1.07M)".

## 3.6 `data-t="Takeaways"` — replace takeaway 6
> **6 · When a number is not in your data, invert the question.** You cannot estimate how much a
> pilot travels. You can ask what it would have to be, and whether that is credible. Required
> δ = break-even lift ÷ measured lift. Move the probabilities point into the Bayesian coda.

## 3.7 Bayesian coda — one addition
On the most natural coda slide, note what Bayes adds *here*: a prior on δ (e.g. Beta centred on
the firm's historical pilot-to-national ratio) integrated into the rollout posterior converts
the required-vs-plausible band comparison into P(the €4M pays). State honestly that it changes
no decision — the overlap is already thin — but it turns a band comparison into a number the
board can rank against other campaigns.

## 3.8 Contents / navigation / registry
- Content slide count 45 → 47 (deck sections 47 → 49). Contents overlay regenerates; footer
  "n / N" updates; keyboard nav traverses cleanly.
- Grep the src for hardcoded references to the old title "The €4M call, without a posterior"
  and to "slide 28"; retarget each.
- Registry: re-anchor the six entries and add the new ones (Part 0.5). Run the verifier; zero
  FAILs, and no WARN introduced by this change.

---

# PART 4 — Narrative file updates

## 4.1 `geo_lift_lecture_speech.md`

Replace the single "Slide 28" section with three (28a ≈ 200 words, **28b ≈ 450 — the climax of
Act IV**, 28c ≈ 300). Renumber the subsequent slide headings (+2). Required engagement beats:

- **28a:** run the naive +€860k computation and *ask the room whether to approve it* before
  dismantling it — same device as the earlier polls.
- **28b:** before revealing plausible δ, make them shout a number; then show the two bands.
- **28b:** pause on the budget slider, ask *"so what would you spend?"* — the honest answer is a
  factor-of-six range: the moment the lecture turns from analysis into advice.
- **28c:** open on step zero: *"Before you spend a million on evidence, spend an hour checking
  you have not already bought it."*
- **28c:** close on pre-commitment — writing the rule before the data arrives is what separates
  a test from theatre.

Delivery note (R6): "transportability" is fine for the classroom; in a client room say *"how
much of this travels."*

**Timing (v2 change 8 — the guide says Act IV ~10 min, not 15).** Act IV 10 → 13 min. Recover
exactly 3:00, named: portfolio view (slide 36) 2:00 → 1:00 (**+60s**) · slide 37 "close the
synthetic case" [FAST] compressed to one spoken sentence (**+45s**) · "Three worlds" trimmed by
**30s** · real-data act trimmed by **45s**. Update the timing guide line at the top of the file.

**Slide 35 ("The €4M decision") section:** align with 3.3 — it now *builds on* Act IV's bands
rather than repeating "the data cannot supply δ"; the funded test is the 8-market design.

## 4.2 `geo_lift_lecture_emphasis.md`

Replace the slide-28 row with three rows; renumber subsequent rows (+2). Mark **28b as the
single most protected slide in Act IV** — never cut; if running long, reduce 28c to a verbal
summary rather than touching 28b. Add 28a and 28b to the never-cut list (and renumber that
list's slide numbers). Add two engagement checkpoints: approve-the-naive-number (28a);
shout-a-δ and what-would-you-spend (28b). **Update row 35:** "Fund the 4-market test from the
ROLLOUT ledger" → "Fund the 8-market stratified test from the rollout ledger (the ~4 was the
power-only floor — bridge stated on 28c)."

---

# PART 5 — Acceptance checks

**Harness gate (check FIRST — v2's reason for existing)**
- [ ] All edits in `apps/geo_slides_src.html`; `geo_lift_slides.html` untouched by hand
- [ ] `build_geo_slides.py` runs clean (no unknown tokens)
- [ ] `verify_geo_deck.py` exits 0: no FAILs, no new WARNs
- [ ] Six old-slide registry entries re-anchored to the new data-t titles
- [ ] Every new number on 28a/28b/28c has a registry entry (list in 0.5); illustrative-input
      comment present
- [ ] Prose scalars that exist as shard tokens use the token (headroom, p, cl_total…)

**Interval discipline**
- [ ] No naked point estimate on 28b; required shown as [0.64, 1.10]; plausible as [0.55, 0.75]
- [ ] Profit at €4M shown as [−€2.00M, +€0.69M], central −€0.85M
- [ ] Break-even budget shown as [€0.68M, €4.14M], central €1.78M
- [ ] 28b states €4M **cannot be proven to lose** — the conclusion is "cannot size," not "loses"

**Numerical consistency**
- [ ] Required δ = 214/τ → 0.64 / 0.82 / 1.10 exactly; identity 214/260 tied to the margin trap
- [ ] δ_plaus corners (CV, β) = (0.4, 0.6) → 0.55 · (0.3, 0.7) → 0.65 · (0.2, 0.8) → 0.75
- [ ] Saturation = 1.778^(β−1); selection = 1 − 0.772·CV, flagged as a linear approximation
- [ ] Budget-slider anchors match the table in 2.5; centre crossing ≈ €1.8M
- [ ] k ≈ 4.3 at CV 0.3, ≈ 8 at CV 0.4; test cost 8 × €133k ≈ €1.07M
- [ ] Naive block shows **+€860k** (registered), not €850k
- [ ] Renegotiation number is **€67k** via token, not €68k
- [ ] €260k, [195, 335], 0.35, €75k, €214k, 2.86, 3.47, p = 0.033, P = 0.78, €2k, ≈€322k
      unchanged everywhere

**Reconciliation (v2)**
- [ ] Exactly ONE recommended test across the deck: 8 stratified markets, €1.07M — 28c, Act V
      slide, deliverable, emphasis row all agree; slide 33's "~4 markets" bridged as power-only
- [ ] δ > 1: 28a caption says "unreachable at this intensity"; 28b slider annotates δ > 1 below
      €2.25M
- [ ] Inference floor: 0.033 attributed to the 1-treated pilot; 8-pair floor ≈ 0.004 stated as
      what the extra markets buy
- [ ] Act V "€4M decision" `.sub` and δ bullet no longer contradict the new Act IV
- [ ] DGP cross-check done; its one-clause outcome on 28a

**Consulting wrapper**
- [ ] R1 — CV and β presented as client-owned, on-slide
- [ ] R2 — step zero above the test design on 28c
- [ ] R3 — no false precision; budgets banded
- [ ] R4 — dated path + "what runs meanwhile" answered on-slide
- [ ] R5 — options table honest (C learns *something*), settled by the ≈€322k VOI number, delay
      cost flagged in one sentence
- [ ] R6 — client-language delivery note in the speech file
- [ ] R7 — competitive-response row flagged as downside at scale

**Rendering**
- [ ] Three slides render in light and dark theme; no hardcoded colours; MathJax renders; no
      overflow at 1500px and 1280px
- [ ] Fold-outs open/close; `.tw` chevron rotates
- [ ] Moved δ-band demo functions on 28a; new budget slider updates all readouts and shading
- [ ] Contents lists 47 content slides; footer count correct; keyboard nav clean

**Content**
- [ ] No slide exceeds ~150 words of body copy (the verifier's length budget stays quiet)
- [ ] Illustrative status of CV and β on-slide, not only folded
- [ ] Budget-invariance of required δ in its own call-out box
- [ ] Both 28b caveats present (break-even ≠ target; direction, not optimisation)
- [ ] 28b framing line verbatim: *"The evidence does not tell us the rollout is wrong. It tells
      us we cannot size it within a factor of six."*

**Narrative**
- [ ] Speech file: three sections, all five beats, renumbered headings, timing cuts sum to 3:00
- [ ] Emphasis file: three rows, 28b never-cut, checkpoints added, row 35's test updated,
      never-cut list renumbered
