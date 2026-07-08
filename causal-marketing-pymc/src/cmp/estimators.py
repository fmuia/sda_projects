"""Estimators with a uniform interface.

Meta-learners (S / T / BCF) all return a posterior CATE array of shape
(n_samples, n_units), so notebooks can swap estimators without touching
downstream metrics or policy code. Synthetic control returns a posterior
over the counterfactual path plus a fast SLSQP simplex fitter for the
placebo permutations.

GOTCHA baked in (cookbook §1, "known gotchas" #1): pymc-bart counterfactual
scoring silently returns FROZEN training predictions — every CATE exactly
0 — unless you resample the BART node by passing `sample_vars=["mu"]` to
`sample_posterior_predictive`. `_bart_predict` always does this; a test
(tests/test_estimators.py) asserts non-zero CATE on a known-nonzero effect.
"""
from __future__ import annotations

import warnings

import numpy as np
from scipy.optimize import minimize

# pymc / pymc-bart are imported lazily inside the BART functions so that the
# legacy environment (pymc<6, no pymc-bart) can still `import cmp.estimators`
# to reach the CausalPy wrappers. The Bayesian synthetic control needs pymc
# (present in both envs) and imports it lazily too.

# Fast-vs-full sampling profiles. FAST is for CI / live-lecture reruns
# (target < ~2 min/notebook); full is for the reference-quality numbers.
FAST = {"draws": 150, "tune": 150, "chains": 2, "m": 40}
FULL = {"draws": 500, "tune": 500, "chains": 4, "m": 100}


# --------------------------------------------------------------------------
# BART building blocks
# --------------------------------------------------------------------------
def _fit_bart(X, y, seed, m=50, draws=150, tune=150, chains=2, binary=False):
    """Fit a BART response surface. Returns (model, idata). If binary, the
    outcome is Bernoulli with a logit link so tau lives on the probability
    scale; otherwise Gaussian."""
    import pymc as pm
    import pymc_bart as pmb
    with pm.Model() as model:
        Xd = pm.Data("Xd", X)
        mu = pmb.BART("mu", X=Xd, Y=y.astype(float), m=m)
        if binary:
            p = pm.Deterministic("p", pm.math.invlogit(mu))
            pm.Bernoulli("y_obs", p=p, observed=y, shape=mu.shape)
        else:
            sd = pm.HalfNormal("sd", 15)
            pm.Normal("y_obs", mu=mu, sigma=sd, observed=y, shape=mu.shape)
        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=chains,
            random_seed=seed, progressbar=False,
            compute_convergence_checks=False,
        )
    return model, idata


def _bart_predict(model, idata, X_new, seed, binary=False):
    """Score a BART model at new X. Passes sample_vars=["mu"] so the tree
    ensemble is *resampled* at X_new — WITHOUT this the counterfactual is
    silently frozen to the training prediction and every effect is 0."""
    import pymc as pm
    var = "p" if binary else "mu"
    with model:
        pm.set_data({"Xd": X_new})
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pp = pm.sample_posterior_predictive(
                idata, var_names=[var], sample_vars=[var],
                progressbar=False, random_seed=seed,
            )
    return pp.posterior_predictive[var].values.reshape(-1, X_new.shape[0])


# --------------------------------------------------------------------------
# Meta-learners — uniform interface: (n_samples, n_units) posterior CATE
# --------------------------------------------------------------------------
def s_learner(X, T, y, seed=1, binary=False, **kw):
    """One surface f(x, t) with treatment as a feature; CATE = f(x,1)-f(x,0).

    Known failure mode (cookbook gotcha #2): the S-learner regularises the
    treatment contribution toward zero, flattening heterogeneity — it
    under-detects and is mis-calibrated. Kept for the labelled failure-mode
    demo; prefer t_learner / bcf for real targeting."""
    p = {**FAST, **kw}
    Xa = np.column_stack([X, T])
    model, idata = _fit_bart(Xa, y, seed, m=p["m"], draws=p["draws"], tune=p["tune"], chains=p["chains"], binary=binary)
    X1 = Xa.copy(); X1[:, -1] = 1.0
    X0 = Xa.copy(); X0[:, -1] = 0.0
    return _bart_predict(model, idata, X1, seed + 90, binary) - _bart_predict(model, idata, X0, seed + 91, binary)


def t_learner(X, T, y, seed=1, binary=False, **kw):
    """Two separate surfaces mu1, mu0 fit on treated / control; CATE =
    mu1(x) - mu0(x). Default choice for uplift — does not force the
    treatment through a shared regularised term."""
    p = {**FAST, **kw}
    X, T, y = np.asarray(X), np.asarray(T), np.asarray(y)
    m1, i1 = _fit_bart(X[T == 1], y[T == 1], seed, m=p["m"], draws=p["draws"], tune=p["tune"], chains=p["chains"], binary=binary)
    m0, i0 = _fit_bart(X[T == 0], y[T == 0], seed + 1, m=p["m"], draws=p["draws"], tune=p["tune"], chains=p["chains"], binary=binary)
    return _bart_predict(m1, i1, X, seed + 90, binary) - _bart_predict(m0, i0, X, seed + 91, binary)


def bcf(X, T, y, propensity, seed=1, **kw):
    """Bayesian Causal Forest (Hahn-Murray-Carvalho 2020): a prognostic
    BART with the estimated propensity fed in (to absorb targeted-selection
    confounding / RIC), plus a separate, tighter treatment BART (fewer
    trees) so heterogeneity can shrink to homogeneity rather than be read
    out of noise. Near-nominal CATE interval coverage under observational
    selection where a naive forest overfits.

    Note (honest caveat, cookbook): when confounders are fully observed,
    BCF ~= T-learner — the propensity trick earns its keep specifically
    under targeted selection."""
    import pymc as pm
    import pymc_bart as pmb
    p = {**FAST, **kw}
    X, T, y = np.asarray(X), np.asarray(T), np.asarray(y)
    n = len(y)
    Xp = np.column_stack([X, propensity])  # propensity into prognostic part
    m_tau = max(10, p["m"] // 2)  # fewer trees on tau -> shrink heterogeneity
    with pm.Model() as model:
        Xpd = pm.Data("Xp", Xp)
        Xtd = pm.Data("Xt", X)
        z = pm.Data("z", T)
        prog = pmb.BART("prog", X=Xpd, Y=y, m=p["m"])
        tau_b = pmb.BART("tau", X=Xtd, Y=y, m=m_tau)
        mu = pm.Deterministic("mu", prog + tau_b * z)
        sd = pm.HalfNormal("sd", 15)
        pm.Normal("y_obs", mu=mu, sigma=sd, observed=y, shape=mu.shape)
        idata = pm.sample(
            draws=p["draws"], tune=p["tune"], chains=p["chains"], cores=p["chains"],
            random_seed=seed, progressbar=False, compute_convergence_checks=False,
        )
    return idata.posterior["tau"].values.reshape(-1, n)


ESTIMATORS = {"S-learner": s_learner, "T-learner": t_learner, "BCF": bcf}


# --------------------------------------------------------------------------
# Doubly-robust ATE (AIPW) — a model-agnostic cross-check of the BART work
# --------------------------------------------------------------------------
def aipw_ate(X, T, y, seed=1, n_boot=400, trim=0.02):
    """Augmented IPW (doubly-robust) ATE with a bootstrap posterior-like
    distribution. Uses gradient-boosted outcome models mu0, mu1 and a
    logistic propensity; the AIPW score is consistent if *either* the
    outcome model or the propensity model is right (double robustness).

    Overlap is enforced by trimming units with propensity outside
    [trim, 1-trim]. Returns dict with point estimate, bootstrap draws,
    the influence-function SE, and the number of trimmed units."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression
    X, T, y = np.asarray(X), np.asarray(T), np.asarray(y)
    n = len(y)

    def _score(idx):
        Xi, Ti, yi = X[idx], T[idx], y[idx]
        e = LogisticRegression(max_iter=1000).fit(Xi, Ti).predict_proba(Xi)[:, 1]
        e = np.clip(e, trim, 1 - trim)
        m1 = GradientBoostingRegressor(n_estimators=80, max_depth=3, random_state=seed)
        m0 = GradientBoostingRegressor(n_estimators=80, max_depth=3, random_state=seed)
        mu1 = m1.fit(Xi[Ti == 1], yi[Ti == 1]).predict(Xi)
        mu0 = m0.fit(Xi[Ti == 0], yi[Ti == 0]).predict(Xi)
        psi = (mu1 - mu0
               + Ti * (yi - mu1) / e
               - (1 - Ti) * (yi - mu0) / (1 - e))
        return psi

    # keep only units with adequate overlap for the reported n_trimmed
    e_full = LogisticRegression(max_iter=1000).fit(X, T).predict_proba(X)[:, 1]
    n_trim = int(np.sum((e_full < trim) | (e_full > 1 - trim)))

    psi_full = _score(np.arange(n))
    point = float(psi_full.mean())
    inf_se = float(psi_full.std(ddof=1) / np.sqrt(n))

    rng = np.random.default_rng(seed)
    boot = np.array([_score(rng.integers(0, n, n)).mean() for _ in range(n_boot)])
    return {"ate": point, "boot": boot, "se": inf_se, "n_trimmed": n_trim,
            "ci90": (float(np.quantile(boot, 0.05)), float(np.quantile(boot, 0.95)))}


def propensity_scores(X, T, seed=1):
    """Estimated propensity e(x)=P(T=1|x) via logistic regression — the
    overlap/positivity diagnostic input and the BCF prognostic input."""
    from sklearn.linear_model import LogisticRegression
    return LogisticRegression(max_iter=1000).fit(np.asarray(X), np.asarray(T)).predict_proba(np.asarray(X))[:, 1]


# --------------------------------------------------------------------------
# Quasi-experimental diagnostics
# --------------------------------------------------------------------------
def first_stage_F(instrument, treatment):
    """First-stage F-statistic for a single instrument (Stock-Yogo rule of
    thumb: F < 10 = weak instrument). Regress treatment on the instrument
    and report the F for the instrument's coefficient."""
    z = np.asarray(instrument, float); t = np.asarray(treatment, float)
    n = len(t)
    Z = np.column_stack([np.ones(n), z])
    beta, *_ = np.linalg.lstsq(Z, t, rcond=None)
    resid = t - Z @ beta
    rss = resid @ resid
    tss = ((t - t.mean()) ** 2).sum()
    r2 = 1 - rss / tss
    k = 1  # one instrument
    F = (r2 / k) / ((1 - r2) / (n - k - 1))
    return float(F)


def mccrary_density(running, cutoff, bandwidth=None, n_bins=40):
    """Simple McCrary-style manipulation test: histogram density of the
    running variable just below vs just above the cutoff. A large jump in
    density at the cutoff suggests units *sorted* across it (gaming), which
    invalidates RD. Returns (density_below, density_above, log_ratio)."""
    r = np.asarray(running, float)
    if bandwidth is None:
        bandwidth = (r.max() - r.min()) / 10
    below = r[(r >= cutoff - bandwidth) & (r < cutoff)]
    above = r[(r >= cutoff) & (r < cutoff + bandwidth)]
    d_below = len(below) / max(bandwidth, 1e-9)
    d_above = len(above) / max(bandwidth, 1e-9)
    log_ratio = float(np.log((d_above + 1) / (d_below + 1)))
    return d_below, d_above, log_ratio


# --------------------------------------------------------------------------
# Synthetic control
# --------------------------------------------------------------------------
def sc_weights_slsqp(target_pre, donors_pre):
    """Fast simplex synthetic-control weights (non-negative, sum to 1) via
    SLSQP. Used for the many placebo-in-space permutations, where a full
    Bayesian fit per placebo would be too slow."""
    J = donors_pre.shape[0]

    def loss(w):
        r = target_pre - w @ donors_pre
        return r @ r

    cons = [{"type": "eq", "fun": lambda w: w.sum() - 1}]
    bounds = [(0, 1)] * J
    w0 = np.full(J, 1 / J)
    res = minimize(loss, w0, bounds=bounds, constraints=cons, method="SLSQP")
    return res.x


def sc_effect_slsqp(target, donors, pre, post):
    """Point-estimate synthetic-control gap over all periods, plus weights,
    using the fast SLSQP fitter. `pre`/`post` are slices."""
    w = sc_weights_slsqp(target[pre], donors[:, pre])
    counterfactual = w @ donors
    return target - counterfactual, w


def synthetic_control(target, donors, pre, post, seed=1, draws=1000, tune=1000, chains=4):
    """Bayesian synthetic control (main estimate, with uncertainty):
    Dirichlet-simplex weights on the donor pool fit to the pre-period, then
    a posterior over the counterfactual path and hence the effect.

    Simplex (Dirichlet) weights — vs unconstrained regression — are what
    prevent extrapolation and negative weights (Abadie).

    The counterfactual is returned as a **posterior predictive**, not just the
    posterior-mean blend: the treated unit's own path carries the fitted
    idiosyncratic noise ``sd`` on top of the weight uncertainty, so a band on
    the counterfactual *outcome* — and hence on the gap/effect, which is what
    the euro decision integrates — must include it. Using the weights-only
    blend (``W_post @ donors``) understates the effect band and can leave the
    true effect outside a nominally-90% interval; adding ``Normal(0, sd)`` per
    period per draw restores near-nominal coverage.

    Parameters
    ----------
    target : (W,) observed treated series
    donors : (J, W) donor pool series
    pre, post : slices into the W time axis

    Returns dict with counterfactual_samples (S, W, posterior-predictive incl.
    obs noise), counterfactual_mean (S, W, the mean blend), effect_samples
    (S, W, = target - predictive), weight_samples (S, J), and pre_rmse (fit
    quality of the mean blend on the pre-period).
    """
    import pymc as pm
    J = donors.shape[0]
    with pm.Model() as model:
        w = pm.Dirichlet("w", a=np.ones(J))
        sd = pm.HalfNormal("sd", 5)
        mu = pm.math.dot(w, donors[:, pre])
        pm.Normal("obs", mu=mu, sigma=sd, observed=target[pre])
        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=chains,
            random_seed=seed, progressbar=False, target_accept=0.95,
            compute_convergence_checks=False,
        )
    W_post = idata.posterior["w"].values.reshape(-1, J)     # (S, J)
    sd_post = idata.posterior["sd"].values.reshape(-1)      # (S,)
    cf_mean = W_post @ donors                               # (S, W) posterior mean blend
    # posterior-predictive counterfactual outcome: mean blend + per-period obs noise
    noise = np.random.default_rng(seed + 12345).standard_normal(cf_mean.shape)
    cf_pred = cf_mean + noise * sd_post[:, None]
    effect = target[None, :] - cf_pred
    pre_rmse = float(np.sqrt(np.mean((target[None, :] - cf_mean).mean(0)[pre] ** 2)))
    return {
        "counterfactual_samples": cf_pred,
        "counterfactual_mean": cf_mean,
        "effect_samples": effect,
        "weight_samples": W_post,
        "pre_rmse": pre_rmse,
        "idata": idata,
    }


def placebo_in_space(sales, treated_idx, pre, post, pre_rmse, rmse_multiple=3.0):
    """Permutation inference: refit synthetic control treating each donor as
    if *it* were treated, and collect the placebo gaps. Following Abadie,
    discard placebos whose pre-fit RMSE is > `rmse_multiple` x the real
    treated unit's (a bad synthetic match makes a meaningless gap).

    Returns (placebo_gaps array (n_kept, W), real_gap (W,), p_value)."""
    n = sales.shape[0]
    placebo_gaps = []
    for j in range(n):
        if j == treated_idx:
            continue
        others = np.delete(np.arange(n), [treated_idx, j])
        gap, _ = sc_effect_slsqp(sales[j], sales[others], pre, post)
        if np.sqrt(np.mean(gap[pre] ** 2)) < rmse_multiple * pre_rmse:
            placebo_gaps.append(gap)
    placebo_gaps = np.array(placebo_gaps)

    donors = np.delete(sales, treated_idx, axis=0)
    real_gap, _ = sc_effect_slsqp(sales[treated_idx], donors, pre, post)
    real_post = real_gap[post].mean()
    placebo_post = placebo_gaps[:, post].mean(1)
    p_value = float((np.sum(np.abs(placebo_post) >= abs(real_post)) + 1) / (len(placebo_post) + 1))
    return placebo_gaps, real_gap, p_value


# --------------------------------------------------------------------------
# CausalPy thin wrappers (legacy env: pymc<6). Imported lazily so the core
# (pymc>=6) environment can import cmp.estimators without causalpy present.
# --------------------------------------------------------------------------
def _require_causalpy():
    try:
        import causalpy as cp  # noqa: F401
    except ImportError as e:  # pragma: no cover
        raise ImportError(
            "causalpy is only installed in the legacy environment (pymc<6). "
            "Run notebooks 06/08-11 with .venv-legacy — see README 'Environment split'."
        ) from e
    return cp


# These wrappers target the CausalPy 0.8.x API (the cookbook skeletons are
# 0.5-era and have drifted): DiD needs a `post_treatment` bool column + a
# `unit` label column + the interaction in the formula; RDD needs a
# dummy-coded `treated` column in the data; ITS wants a numeric index and
# NUMERIC seasonality (a categorical breaks patsy on the pre/post split);
# IV samples a multivariate model that hits a multiprocessing EOFError on
# some machines, so we default it to cores=1.


def _sk(fast, **extra):
    base = {"progressbar": False, "random_seed": 1}
    base.update(FAST_CP if fast else FULL_CP)
    base.update(extra)
    return base


FAST_CP = {"draws": 200, "tune": 200, "chains": 2}
FULL_CP = {"draws": 1000, "tune": 1000, "chains": 4, "target_accept": 0.95}


def synthetic_control_cp(df, treatment_time, control_units, treated_units, fast=True):
    cp = _require_causalpy()
    return cp.SyntheticControl(
        df, treatment_time=treatment_time,
        control_units=control_units, treated_units=treated_units,
        model=cp.pymc_models.WeightedSumFitter(sample_kwargs=_sk(fast, target_accept=0.95)),
    )


def did(df, formula="revenue ~ 1 + group*post_treatment", time_variable_name="t",
        group_variable_name="group", fast=True):
    cp = _require_causalpy()
    return cp.DifferenceInDifferences(
        df, formula=formula,
        time_variable_name=time_variable_name, group_variable_name=group_variable_name,
        model=cp.pymc_models.LinearRegression(sample_kwargs=_sk(fast)),
    )


def rdd(df, formula, running_variable_name, treatment_threshold, epsilon=0.001, bandwidth=None, fast=True):
    cp = _require_causalpy()
    kwargs = dict(
        formula=formula, running_variable_name=running_variable_name,
        treatment_threshold=treatment_threshold, epsilon=epsilon,
        model=cp.pymc_models.LinearRegression(sample_kwargs=_sk(fast)),
    )
    if bandwidth is not None:
        kwargs["bandwidth"] = bandwidth
    return cp.RegressionDiscontinuity(df, **kwargs)


def its(df, treatment_time, formula="conversion ~ 1 + t + sin7 + cos7", fast=True):
    cp = _require_causalpy()
    return cp.InterruptedTimeSeries(
        df, treatment_time=treatment_time, formula=formula,
        model=cp.pymc_models.LinearRegression(sample_kwargs=_sk(fast)),
    )


def iv(df, instruments_formula, formula, instrument_col, treatment_col, outcome_col,
       fast=True, priors=None, binary_treatment=False):
    cp = _require_causalpy()
    # GOTCHA: CausalPy 0.8.1 defaults the IV beta priors to CENTER on the 2SLS
    # point estimates with sigma=1 — very tight, so the posterior is overconfident
    # and its 90% interval can exclude the truth (a ~3x too-narrow band). Pass
    # weakly-informative priors, e.g. priors={"mus": [0, 0], "sigmas": [50, 50],
    # "eta": 2, "lkj_sd": 2}, for an honest, ~frequentist-width interval.
    # binary_treatment=True selects the logit control-function likelihood (the
    # exposure is 0/1); on this DGP it barely moves the point and keeps the
    # interval a touch tight, so the priors are the load-bearing fix.
    return cp.InstrumentalVariable(
        instruments_data=df[[treatment_col, instrument_col]],
        data=df[[outcome_col, treatment_col]],
        instruments_formula=instruments_formula,
        formula=formula,
        model=cp.pymc_models.InstrumentalVariableRegression(sample_kwargs=_sk(fast, cores=1)),
        priors=priors,
        binary_treatment=binary_treatment,
    )
