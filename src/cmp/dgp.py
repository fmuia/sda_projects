"""Seeded data-generating processes with a known ground truth.

Every generator returns data plus the true effect(s), so a notebook can
show "does the method recover the truth" before trusting it on real data.
Swap in real data by replacing the return of these functions with a
loaded DataFrame that has the same columns (see `cmp.data` for loaders).
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _sigmoid(z):
    return 1.0 / (1.0 + np.exp(-z))


# --------------------------------------------------------------------------
# 01 — uplift targeting (Anchor A)
# --------------------------------------------------------------------------
def uplift_customers(
    n: int = 1400,
    regime: str = "observational",
    confounder_strength: float = 0.0,
    cost: float = 8.0,
    seed: int = 7,
):
    """Discount-email customers with a known heterogeneous €-effect.

    regime="randomized": treatment is a coin flip -> unconfoundedness holds
    by design. regime="observational": marketers historically targeted
    engaged/recent customers (targeted selection) -> naive estimators are
    confounded. `confounder_strength` adds a further *unobserved* driver U
    of both treatment and outcome, for the sensitivity-to-hidden-confounding
    analysis (0 = no hidden confounder).

    Returns a DataFrame with columns [recency, frequency, monetary, tenure,
    engage, T, y, mu0, tau, propensity] and `cost` (the â‚¬ discount cost,
    for the euro-policy step).
    """
    rng = np.random.default_rng(seed)
    recency = rng.uniform(5, 330, n)
    frequency = rng.poisson(5, n).astype(float)
    monetary = rng.uniform(15, 180, n)
    tenure = rng.uniform(1, 60, n)
    engage = rng.beta(2, 3, n)

    mu0 = np.clip(20 + 1.4 * frequency + 0.25 * monetary + 12 * engage - 0.03 * recency, 0, None)
    persuadable = 42 * np.exp(-((recency - 120) / 70) ** 2) * _sigmoid(frequency - 3) * _sigmoid(9 * (engage - 0.28))
    sleeping = -24 * _sigmoid(9 * (0.22 - engage)) * _sigmoid(1.2 * (frequency - 6))
    tau = persuadable + sleeping

    if regime == "randomized":
        propensity = np.full(n, 0.5)
        T = rng.integers(0, 2, n).astype(float)
    elif regime == "observational":
        lin = 1.8 * (engage - 0.4) + 1.2 * ((150 - recency) / 150) + 0.15 * (frequency - 5)
        if confounder_strength > 0:
            U = rng.normal(size=n)
            propensity = _sigmoid(lin + 0.9 * confounder_strength * U)
        else:
            U = np.zeros(n)
            propensity = _sigmoid(lin)
        T = (rng.uniform(size=n) < propensity).astype(float)
    else:
        raise ValueError("regime must be 'randomized' or 'observational'")

    noise = rng.normal(0, 8, n)
    y = mu0 + tau * T + noise
    if regime == "observational" and confounder_strength > 0:
        y = y + confounder_strength * U  # hidden confounder also lifts spend directly

    df = pd.DataFrame(
        {
            "recency": recency, "frequency": frequency, "monetary": monetary,
            "tenure": tenure, "engage": engage, "T": T, "y": y,
            "mu0": mu0, "tau": tau, "propensity": propensity,
        }
    )
    df.attrs["cost"] = cost
    df.attrs["feature_cols"] = ["recency", "frequency", "monetary", "tenure", "engage"]
    return df


# --------------------------------------------------------------------------
# 07 — geo lift / synthetic control (Anchor B)
# --------------------------------------------------------------------------
def geo_panel(
    n_weeks: int = 60,
    launch_week: int = 40,
    n_dmas: int = 30,
    lift_pct: float = 0.12,
    seed: int = 3,
):
    """Weekly DMA sales panel with a common factor structure (trend, season,
    a macro shock) shared by treated + control DMAs, so a naive before/after
    or treated-vs-average-control comparison is confounded by that shared
    structure, but a synthetic control can reconstruct it.

    Returns (sales_wide DataFrame [dma x week], true_effect per week on the
    treated DMA, launch_week, treated_dma_label).
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_weeks)
    trend = 0.4 * t
    season = 8 * np.sin(2 * np.pi * t / 26) + 4 * np.sin(2 * np.pi * t / 13)
    macro = np.cumsum(rng.normal(0, 1.2, n_weeks))
    F = np.column_stack([trend, season, macro])

    levels = rng.uniform(80, 140, n_dmas)
    loads = rng.uniform(0.6, 1.4, (n_dmas, 3))
    sales = levels[:, None] + loads @ F.T + rng.normal(0, 3, (n_dmas, n_weeks))

    treated_idx = 0
    true_effect = lift_pct * (levels[treated_idx] + loads[treated_idx] @ F.T)
    true_effect = true_effect * (t >= launch_week)
    sales[treated_idx] += true_effect

    dma_labels = [f"dma_{i:02d}" for i in range(n_dmas)]
    df = pd.DataFrame(sales.T, index=t, columns=dma_labels)
    df.index.name = "week"
    return df, true_effect, launch_week, dma_labels[treated_idx]


# --------------------------------------------------------------------------
# 02 — segment effects
# --------------------------------------------------------------------------
def segment_customers(n: int = 1200, seed: int = 11):
    """Email lift that genuinely differs between high- and low-value
    segments (a real moderation effect), for pathmc random-slope CATE.
    """
    rng = np.random.default_rng(seed)
    prior_value = rng.choice(["low", "high"], size=n, p=[0.6, 0.4])
    is_high = (prior_value == "high").astype(float)
    trend = rng.normal(50, 10, n)
    email = rng.integers(0, 2, n).astype(float)

    b0, b_email, b_val, b_interact = 5.0, 3.0, 18.0, 9.0  # true effect: 3 (low) vs 12 (high)
    spend = (
        b0 + b_email * email + b_val * is_high
        + b_interact * email * is_high + 0.3 * trend
        + rng.normal(0, 6, n)
    )
    df = pd.DataFrame({"email": email, "prior_value": prior_value, "trend": trend, "spend": spend})
    true_effect = {"low": b_email, "high": b_email + b_interact}
    return df, true_effect


# --------------------------------------------------------------------------
# 03 — price elasticity by region
# --------------------------------------------------------------------------
def price_panel(n_regions: int = 12, n_weeks: int = 80, confounder_strength: float = 0.0, seed: int = 5):
    """Region x week log-log demand panel with a region-varying (random
    slope) elasticity, seasonality + competitor price as observed
    confounders, and an optional unobserved demand shock that endogenises
    price (price falls *because* demand is soft) via `confounder_strength`.
    """
    rng = np.random.default_rng(seed)
    true_elasticity = rng.normal(-1.4, 0.35, n_regions)  # fleet mean elasticity -1.4

    rows = []
    for r in range(n_regions):
        season = 0.3 * np.sin(2 * np.pi * np.arange(n_weeks) / 26)
        trend = 0.01 * np.arange(n_weeks)
        competitor_price = rng.normal(20, 2, n_weeks)
        demand_shock = rng.normal(0, 1, n_weeks) if confounder_strength > 0 else np.zeros(n_weeks)
        # Price responds to the (partly unobserved) demand shock: managers cut price
        # WHEN demand is soft (negative shock -> lower price). So price rises with the
        # shock; this positive Cov(log_price, shock) biases the OLS elasticity TOWARD
        # zero (the classic simultaneity bias), which partial pooling cannot fix.
        log_price = np.log(15) - 0.05 * competitor_price / 20 + confounder_strength * demand_shock + rng.normal(0, 0.05, n_weeks)
        log_q = (
            2.5 + true_elasticity[r] * log_price + 0.4 * (competitor_price - 20) / 20
            + season + trend + demand_shock + rng.normal(0, 0.08, n_weeks)
        )
        rows.append(pd.DataFrame({
            "region": f"region_{r:02d}", "week": np.arange(n_weeks),
            "price": np.exp(log_price), "demand": np.exp(log_q),
            "competitor_price": competitor_price, "season": season, "trend": trend,
        }))
    df = pd.concat(rows, ignore_index=True)
    return df, true_elasticity


# --------------------------------------------------------------------------
# 04 — funnel mediation
# --------------------------------------------------------------------------
def funnel(n: int = 1000, seed: int = 13):
    """Onboarding -> engagement -> activation -> conversion chain SCM, with
    known direct/indirect (mediated) effect sizes for the natural-effects
    decomposition.
    """
    rng = np.random.default_rng(seed)
    onboarding_score = rng.uniform(0, 1, n)
    channel_quality = rng.uniform(0, 1, n)

    e_on, e_ch = 2.2, 1.1
    engagement = e_on * onboarding_score + e_ch * channel_quality + rng.normal(0, 0.4, n)

    a_eng, a_ch = 1.6, 0.6
    activated = a_eng * engagement + a_ch * channel_quality + rng.normal(0, 0.4, n)

    c_act, c_eng = 0.9, 0.35
    converted = c_act * activated + c_eng * engagement + rng.normal(0, 0.3, n)

    df = pd.DataFrame({
        "onboarding_score": onboarding_score, "channel_quality": channel_quality,
        "engagement": engagement, "activated": activated, "converted": converted,
    })
    indirect = e_on * a_eng * c_act + e_on * c_eng  # onboarding -> engagement -> {activated, converted}
    direct = 0.0  # onboarding has no direct arrow into converted in this DAG
    true_effects = {"indirect_via_engagement_activated": e_on * a_eng * c_act,
                     "indirect_via_engagement_only": e_on * c_eng,
                     "total": indirect + direct}
    return df, true_effects


# --------------------------------------------------------------------------
# 05 — what to control for (DAG demo: confounder + collider + mediator)
# --------------------------------------------------------------------------
def dag_control_demo(n: int = 1500, seed: int = 17):
    """email -> spend, confounded by loyalty, mediated by opened_email
    (a post-treatment collider trap: opened_email is a common effect of
    email and an unobserved engagement trait, and also sits on the causal
    path). True ATE of email on spend is known.
    """
    rng = np.random.default_rng(seed)
    loyalty = rng.normal(0, 1, n)
    email = (rng.uniform(size=n) < _sigmoid(0.8 * loyalty)).astype(float)  # confounded assignment

    true_ate = 6.0
    engagement_trait = rng.normal(0, 1, n)  # unobserved, drives opened_email + spend (collider parent)
    opened_email = (rng.uniform(size=n) < _sigmoid(1.5 * email + 0.7 * engagement_trait)).astype(float)
    spend = 20 + 5 * loyalty + true_ate * email + 3 * engagement_trait + rng.normal(0, 4, n)

    # `responded` is a clean COLLIDER: caused by BOTH the treatment (email) and the
    # outcome (spend). email -> responded <- spend. Conditioning on it opens a
    # non-causal path and biases the email->spend estimate. This is the
    # "never control for a post-outcome variable" trap in its starkest form.
    responded = (rng.uniform(size=n) < _sigmoid(1.2 * email + 0.05 * (spend - spend.mean()))).astype(float)

    df = pd.DataFrame({
        "email": email, "loyalty": loyalty, "opened_email": opened_email,
        "responded": responded, "spend": spend,
    })
    return df, true_ate


# --------------------------------------------------------------------------
# 06 — incrementality MMM
# --------------------------------------------------------------------------
def mmm_weekly(n_weeks: int = 156, seed: int = 21):
    """Weekly sales with two channels: TV (a real, adstocked/saturated
    driver) and brand_search (which mostly *catches* demand that
    seasonality/consideration already created — a mediator trap for naive
    last-click attribution). Returns true weekly incremental contribution
    per channel.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_weeks)
    seasonality = 1 + 0.3 * np.sin(2 * np.pi * t / 52)
    tv_spend = np.clip(rng.normal(50, 15, n_weeks), 5, None)

    def adstock(x, lam):
        out = np.zeros_like(x)
        out[0] = x[0]
        for i in range(1, len(x)):
            out[i] = x[i] + lam * out[i - 1]
        return out

    def saturate(x, alpha, kappa):
        return alpha * x / (kappa + x)

    tv_ads = adstock(tv_spend, 0.5)
    tv_contribution = saturate(tv_ads, 40, 60)  # true incremental sales from TV

    consideration = 0.6 * tv_ads / tv_ads.max() + 0.5 * (seasonality - 1)
    brand_search_spend = np.clip(8 + 15 * consideration + rng.normal(0, 2, n_weeks), 1, None)
    # brand_search sales contribution is mostly *mediated* through consideration it didn't create:
    true_brand_search_contribution = np.zeros(n_weeks)  # true incremental effect of brand_search itself is ~0

    baseline = 120 * seasonality
    sales = (
        baseline + tv_contribution + true_brand_search_contribution
        + 8 * consideration  # consideration (driven by tv + season) lifts sales directly too
        + rng.normal(0, 5, n_weeks)
    )
    df = pd.DataFrame({
        "date_week": pd.date_range("2023-01-02", periods=n_weeks, freq="W-MON"),
        "tv": tv_spend, "brand_search": brand_search_spend,
        "seasonality": seasonality, "sales": sales,
    })
    true_contribution = {"tv": tv_contribution, "brand_search": true_brand_search_contribution}
    return df, true_contribution


# --------------------------------------------------------------------------
# 08 — loyalty rollout (DiD)
# --------------------------------------------------------------------------
def did_rollout(n_stores: int = 40, n_weeks: int = 24, launch_week: int = 12, true_effect: float = 400.0, seed: int = 23):
    """Store-level weekly revenue; loyalty app launched in half the stores
    at `launch_week`. Parallel pre-trends by construction (store fixed
    effects + a shared seasonal pattern), so DiD identifies `true_effect`.
    """
    rng = np.random.default_rng(seed)
    store_fx = rng.normal(5000, 800, n_stores)
    treated = np.zeros(n_stores, dtype=bool)
    treated[: n_stores // 2] = True
    rng.shuffle(treated)

    rows = []
    season = 200 * np.sin(2 * np.pi * np.arange(n_weeks) / 12)
    for s in range(n_stores):
        post = (np.arange(n_weeks) >= launch_week).astype(float)
        effect = true_effect * post * treated[s]
        revenue = store_fx[s] + season + effect + rng.normal(0, 250, n_weeks)
        rows.append(pd.DataFrame({
            "store": f"store_{s:02d}", "unit": s, "t": np.arange(n_weeks), "week": np.arange(n_weeks),
            "group": int(treated[s]),
            # CausalPy 0.8 DiD expects a `post_treatment` (bool) column referenced in the formula
            # and a `unit` column labelling each unique unit (used for plotting).
            "post_treatment": post.astype(bool), "post": post.astype(int), "revenue": revenue,
        }))
    df = pd.concat(rows, ignore_index=True)
    return df, true_effect


# --------------------------------------------------------------------------
# 09 — Gold-tier perk (RDD)
# --------------------------------------------------------------------------
def rdd_perk(n: int = 2000, cutoff: float = 100.0, true_jump: float = 0.14, seed: int = 29):
    """Annual spend (running variable) crossing â‚¬100 grants Gold tier;
    retention is smoothly increasing in spend *plus* a true discontinuous
    jump at the cutoff from the perk itself.
    """
    rng = np.random.default_rng(seed)
    spend = rng.gamma(shape=3.0, scale=45.0, size=n)
    treated = (spend >= cutoff).astype(float)
    baseline = 0.35 + 0.0025 * spend - 0.0000045 * spend**2
    retention_p = np.clip(baseline + true_jump * treated, 0.02, 0.98)
    retention = (rng.uniform(size=n) < retention_p).astype(float)
    df = pd.DataFrame({"spend": spend, "treated": treated, "retention": retention})
    return df, true_jump


# --------------------------------------------------------------------------
# 10 — site redesign (ITS)
# --------------------------------------------------------------------------
def its_redesign(n_days: int = 180, redesign_day: int = 120, true_lift: float = 0.03, seed: int = 31):
    """Daily conversion rate, redesigned on a known day for all traffic (no
    control group); pre-period trend + weekly seasonality continues, plus a
    true step lift after redesign.
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_days)
    trend = 0.10 + 0.00015 * t
    weekly = 0.01 * np.sin(2 * np.pi * t / 7)
    post = (t >= redesign_day).astype(float)
    conversion = trend + weekly + true_lift * post + rng.normal(0, 0.006, n_days)
    # Numeric weekly-Fourier seasonality (sin7/cos7) rather than a categorical
    # month: CausalPy fits ITS on the pre-period and extrapolates, so a
    # categorical whose post-period has unseen levels breaks patsy. Numeric
    # features extrapolate cleanly.
    df = pd.DataFrame({
        "t": t, "day": t,
        "sin7": np.sin(2 * np.pi * t / 7), "cos7": np.cos(2 * np.pi * t / 7),
        "conversion": conversion,
    })
    return df, true_lift, redesign_day


# --------------------------------------------------------------------------
# 11 — endogenous ad exposure (IV)
# --------------------------------------------------------------------------
def iv_ad_exposure(n: int = 3000, true_effect: float = 15.0, seed: int = 37):
    """Ad exposure is self-selected (engaged customers seek the brand out,
    so plain OLS of sales on exposure is biased upward); a randomized
    encouragement (e.g. a serving-priority lottery) is a valid instrument.
    """
    rng = np.random.default_rng(seed)
    engagement = rng.normal(0, 1, n)  # unobserved confounder
    encouragement = rng.integers(0, 2, n).astype(float)  # instrument: randomized

    exposure_p = _sigmoid(0.3 + 1.1 * encouragement + 0.8 * engagement)
    ad_exposure = (rng.uniform(size=n) < exposure_p).astype(float)
    sales = 50 + true_effect * ad_exposure + 12 * engagement + rng.normal(0, 6, n)

    df = pd.DataFrame({"encouragement": encouragement, "ad_exposure": ad_exposure, "sales": sales})
    return df, true_effect
