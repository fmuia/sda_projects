# Canonical notation

The one symbol table the whole book obeys. The `chapter-magnificence` skill checks every
chapter against it, and a chapter is not "magnificent" until it conforms or documents a
deliberate, field-standard exception here. The priority is that a **student moving between
Michele Russo's lecture deck and our chapters sees one coherent symbol system**, and that our
two guest-lecture chapters (Ch. 9 synthetic control, Ch. 13 IV) agree with each other.

Two rules govern exceptions:
1. **Field convention wins over global uniformity.** IV names the structural effect `β`;
   synthetic control names the lift `τ`. Forcing one letter on both would fight every textbook
   and the course itself. Where a symbol is standard in its subfield *and* matches the course,
   keep it — and record it below so it is a choice, not a drift.
2. **Never reuse one letter for two different objects a reader meets close together.** Within a
   chapter this is absolute; across the two guest chapters it is strongly preferred.

---

## Core symbols (every chapter)

| Symbol | Meaning | Notes |
|---|---|---|
| `i` | unit index (customer, market, user) | |
| `t` | time index (week, day) | |
| `Y`, `Y_i`, `Y_{it}` | observed outcome | |
| `Y_i(1)`, `Y_i(0)` | potential outcomes | parenthesis form, matches the course |
| `\tau_i = Y_i(1)-Y_i(0)` | individual causal effect | the course also writes `\delta_i`; **we standardise on `\tau_i`** and note the course's `\delta` once, at first use, in Ch. 1 |
| `X`, `x` | features / covariates (and, in IV, the treatment — see below) | |
| `Z` | instrument | IV only |
| `U` | unobserved confounder / intent | |
| `\varepsilon` | idiosyncratic noise | |
| `\E[\cdot]`, `\Prob(\cdot)` | expectation, probability | |
| `e(x)=\Prob(T{=}1\mid X{=}x)` | propensity score | |
| ATE, ATT, CATE `\tau(x)`, LATE | estimands | see the estimand note below |
| `c` | per-unit cost / decision threshold (bare) | Ch. 13 uses `c`; Ch. 9 uses bare `c` for cost, distinct from its subscripted baseline `c_i` |
| `\Prob(\text{effect} > c)` | the decision quantity | the one thing the Bayesian layer adds; identical framing in both chapters |

**Treatment indicator.** The book uses `T\in\{0,1\}` in the customer chapters (Ch. 1, 3) and
`X\in\{0,1\}` for exposure in Ch. 13, matching each field and the course (the deck uses `D`
generally but `X` for IV). This is the one place the book and the course differ on a core symbol
(`T`/`D`). **Action:** Ch. 1 carries a one-line note — "the lecture writes the treatment `D`;
we write `T`" — and no chapter silently switches. Ch. 9 has no unit-level treatment indicator
(one treated market), so it is unaffected.

**Estimand names.** ATE, ATT, CATE `\tau(x)`, LATE. The course additionally uses **ATU**
(= ATC, effect on the untreated); the book does not. If a chapter needs it, use **ATU** (the
course's label) and state `ATU = ATC` once.

---

## Ch. 9 — synthetic control (guest lecture)

| Symbol | Meaning |
|---|---|
| `i=0` | the treated market; donors `j=1,\dots,J` |
| `w_j`, `w\in\Delta` | donor weights on the unit simplex `\Delta` (`w_j\ge0`, `\sum w_j=1`) |
| `\widehat{Y}_{0,t}(0)=\sum_j w_j Y_{jt}` | the synthetic counterfactual (hat on the letter, not the group) |
| `\tau_t = Y_{0t}-\sum_j w_j Y_{jt}` | per-week lift; total `\tau=\sum_{t\ge T_0}\tau_t` |
| `T_0` | launch week |
| `g_t, s_t, m_t` | shared trend, season, macro random walk |
| `\lambda_i` | market `i`'s factor loadings |
| `\rho` | AR(1) coefficient of the residual |
| `\rho_k` | measured autocorrelation at lag `k` (distinct from the AR(1) parameter `\rho`) |
| `\omega`, `\sigma_\omega, \sigma_\varepsilon` | persistent-offset draw and sd, weekly-noise sd (offset renamed from `c`/`\sigma_c` 2026-07-16 to clear the clash with cost `c`) |
| `m` | gross margin (bare); distinct from the macro walk `m_t` by its subscript, the same pattern as `c`/`c_i` |
| `b = c/m` | break-even lift; break-even iROAS is `1/m` |
| iROAS | incremental return on ad spend, `\tau/c` |
| `\varphi` | spillover fraction (leak of the lift into neighbouring donors) |
| `\alpha` | Dirichlet concentration on the weights (Ch. 13's `\alpha_0,\alpha_1` are probit coefficients; no co-occurrence) |
| `\sigma_\tau` | illustrative-only normal sd of the total (§9.5, explicitly not a shipped number) |
| `d_p`, `P`, `N`, `T` | real-data DiD: pair difference, number of pairs, treated geos, campaign **days**. `T` = days is a documented exception to the core `T\in\{0,1\}`; Ch. 9 has no unit-level treatment indicator, so no in-chapter clash |

**Deliberate exceptions / clashes to watch (flagged, not yet resolved):**
- **Treated index `0` vs the course's `1`.** The book uses `i=0` (Pythonic, matches the
  notebook). The deck uses unit `1`. *Resolved 2026-07-16:* kept `0`; §9.2 now carries the
  one-sentence note ("the lecture deck writes the treated unit as market 1").
- **`\kappa`** is the campaign lift *fraction* in Ch. 9 but the confounder→outcome coefficient
  in Ch. 13. **Decision: keep `\kappa` in both** — it is field-standard in each (a proportional
  lift multiplier; an OVB coefficient) and the two never co-occur (different chapters). This is a
  documented exception under rule 1, chosen over an unnatural `\ell`.
- **Cost `c` vs baseline `c_i`.** Ch. 9's DGM uses `c_i` for a market's additive baseline level,
  and the decision rule uses a bare `c` for the campaign cost. They co-occur in the chapter but
  are always distinguished by the subscript (`c_i`/`c_0` vs bare `c`). Acceptable; do not "unify".
  (A third bare-`c`, the persistent-offset draw in Appendix 9.A.11, was renamed `\omega`
  2026-07-16, so bare `c` now means cost alone.)
- **`\lambda`** = factor loadings (Ch. 9) vs confounder→exposure coefficient (Ch. 13);
  **`\rho`** = AR(1) coeff (Ch. 9) vs endogeneity correlation (Ch. 13). Both are field-standard
  and appear in different chapters; **acceptable**, but do not let either leak across.

---

## Ch. 13 — instrumental variables (guest lecture)

| Symbol | Meaning |
|---|---|
| `X_i\in\{0,1\}` | exposure (the endogenous treatment) |
| `Z_i` | the instrument (randomized encouragement / eligibility) |
| `U_i` | unobserved intent |
| `\beta` (`=\beta_{\text{LATE}}` here) | structural effect of exposure; the LATE |
| `\pi` | first stage `\E[X\mid Z{=}1]-\E[X\mid Z{=}0]` = complier share |
| `\delta` | reduced form `\E[Y\mid Z{=}1]-\E[Y\mid Z{=}0]` |
| `\gamma` | instrument strength (first-stage coefficient in the DGP) |
| `\alpha_0,\ \alpha_1` | probit first-stage intercept and slope on `Z` in the binary-aware repair (`\S`13.6). Distinct from the DGP's logistic first stage, whose intercept is also written `\alpha_0`; both are "the first-stage intercept," so no reader meets a clash. |
| `\lambda` | `U\to X` coefficient; `\kappa` | `U\to Y` coefficient |
| `\rho` | endogeneity (error correlation) |
| `F` | first-stage F-statistic |
| `c`, `v` | cost per exposure; value per unit of outcome (so `v\beta` is euros) |

This matches the course's Session 5 notation directly (`X` treatment, `Z` instrument, `U` in the
error, `\beta` effect, `\pi` first stage, `\delta` reduced form, monotonicity `X_i(1)\ge X_i(0)`).
Keep it.

---

## Shared decision framing (both guest chapters, identical)

- **The rule is a probability, never a confidence bar.** `\Prob(\text{effect}>c)` with the GO /
  TEST-FURTHER / NO-GO thresholds (0.9 / 0.5). Ch. 9's effect is `\tau`; Ch. 13's is `v\beta`.
  Same rule, one unit conversion.
- **VOI** uses the same definition in both: `\E[\max(\text{effect}-c,0)]-\max(\E[\text{effect}]-c,0)`.
- **Headroom curve**: sweep a hypothetical `c`, read where `\Prob(\text{effect}>c)` crosses 0.9.
