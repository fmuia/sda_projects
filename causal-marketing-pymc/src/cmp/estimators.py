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
(tests/test_package.py::test_bart_cate_is_nonzero) asserts non-zero CATE on a known-nonzero effect.
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
            # BART is PGBART (particle sampler); a blanket r-hat over per-unit tree
            # predictions is not a meaningful diagnostic and would warn on nearly
            # every fit. Divergences are still recorded in sample_stats, and callers
            # surface scoped r-hat/ESS on the continuous scalars via convergence_report.
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
# Convergence reporting (assessment "pattern E"): surface r-hat / ESS /
# divergences in the notebook itself. This is an explicit stdout readout on
# purpose — PyMC's own convergence warnings go to stderr, which the PDF report
# generator strips, so an auto-warning would never reach the lecture artifact.
# --------------------------------------------------------------------------
def convergence_report(idata, var_names=None):
    """Compact MCMC convergence readout: max r-hat and min bulk/tail ESS over
    `var_names`, plus the sampler's divergence count, with a one-line `summary`
    string ready to print.

    Why `var_names` is scoped: for the BART meta-learners the posterior holds a
    per-unit tree prediction of shape (draws, n), and PGBART is a non-gradient
    particle sampler — a blanket r-hat over hundreds of per-unit predictions
    almost always trips 'r-hat > 1.01' for *some* unit and is not the standard
    BART diagnostic. We instead monitor the NUTS-sampled continuous scalars
    (obs-noise `sd`, hyperparameters); the multi-seed truth-recovery cell is the
    operational convergence check for the CATE surface itself. Divergences come
    from sample_stats and are present whether or not pm.sample ran its own check.
    """
    import arviz as az
    post = idata.posterior
    n_chains = int(post.sizes.get("chain", 1))
    ndiv = None
    if hasattr(idata, "sample_stats") and "diverging" in idata.sample_stats:
        ndiv = int(idata.sample_stats["diverging"].values.sum())
    out = {"n_chains": n_chains, "n_divergences": ndiv,
           "max_rhat": float("nan"), "min_ess_bulk": float("nan"),
           "min_ess_tail": float("nan")}
    if n_chains >= 2:
        try:
            if var_names is None:
                # auto-scope: monitor scalars / small-vector params, skip per-observation
                # deterministics (e.g. MMM per-week channel contributions), whose blanket
                # r-hat is not the meaningful convergence target — same rationale as BART.
                names = []
                for nm, da in post.data_vars.items():
                    sz = 1
                    for dim in da.dims:
                        if dim not in ("chain", "draw"):
                            sz *= int(post.sizes[dim])
                    if sz <= 50:
                        names.append(nm)
                var_names = names or None
            d = az.summary(idata, var_names=var_names, kind="diagnostics")
            out["max_rhat"] = float(d["r_hat"].max())
            out["min_ess_bulk"] = float(d["ess_bulk"].min())
            out["min_ess_tail"] = float(d["ess_tail"].min())
        except Exception as e:                       # never let a diagnostic break a run
            out["error"] = str(e)[:120]
    rhat_s = f"{out['max_rhat']:.3f}" if out["max_rhat"] == out["max_rhat"] else "n/a (1 chain)"
    ess_s = f"{out['min_ess_bulk']:.0f}" if out["min_ess_bulk"] == out["min_ess_bulk"] else "n/a"
    div_s = "n/a" if ndiv is None else str(ndiv)
    out["summary"] = f"max r-hat {rhat_s} - min ESS {ess_s} - divergences {div_s}"
    return out


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
    # Score both counterfactuals in ONE posterior-predictive call so each draw's
    # tree ensemble hits X1 and X0 together — CATE is then a within-draw contrast.
    # Two separate calls (different seeds) would add *independent* predictive
    # noise to the two arms, inflating the variance of what is meant to be a
    # paired difference. (t_learner can't do this — its arms are two models.)
    n = X1.shape[0]
    both = _bart_predict(model, idata, np.vstack([X1, X0]), seed + 90, binary)
    return both[:, :n] - both[:, n:]


def t_learner(X, T, y, seed=1, binary=False, **kw):
    """Two separate surfaces mu1, mu0 fit on treated / control; CATE =
    mu1(x) - mu0(x). Default choice for uplift — does not force the
    treatment through a shared regularised term."""
    p = {**FAST, **kw}
    X, T, y = np.asarray(X), np.asarray(T), np.asarray(y)
    m1, i1 = _fit_bart(X[T == 1], y[T == 1], seed, m=p["m"], draws=p["draws"], tune=p["tune"], chains=p["chains"], binary=binary)
    m0, i0 = _fit_bart(X[T == 0], y[T == 0], seed + 1, m=p["m"], draws=p["draws"], tune=p["tune"], chains=p["chains"], binary=binary)
    return _bart_predict(m1, i1, X, seed + 90, binary) - _bart_predict(m0, i0, X, seed + 91, binary)


def bcf(X, T, y, propensity, seed=1, return_full=False, **kw):
    """Bayesian Causal Forest (Hahn-Murray-Carvalho 2020): a prognostic
    BART with the estimated propensity fed in (to absorb targeted-selection
    confounding / RIC), plus a separate, tighter treatment BART (fewer
    trees) so heterogeneity can shrink to homogeneity rather than be read
    out of noise. Under observational selection this regularises the CATE
    where a naive forest overfits; the evidence for calibration is the
    multi-seed recovery + coverage-by-decile check in nb01 (near-nominal at
    full sampling), not an a-priori guarantee.

    Parameterisation caveat: pymc-bart centres each forest's prior at the mean
    of its `Y`. Here the treatment forest is passed `Y=y`, so its prior sits at
    the outcome level rather than on the ~0 effect scale; the data dominate at
    these sample sizes (multi-seed ATE bias ≈ 0), but a 0-centred tau prior is
    the cleaner BCF form and would tighten regularisation further.

    Note (honest caveat, cookbook): when confounders are fully observed,
    BCF ~= T-learner — the propensity trick earns its keep specifically
    under targeted selection.

    With return_full=True, returns a dict {cate, mu, sd, idata, convergence}
    where `mu` is the fitted conditional-mean posterior (prognostic + tau*T,
    shape (S, n)) and `sd` the observation-noise posterior (S,) — everything
    needed for a genuine posterior-predictive check, y_rep = Normal(mu, sd)."""
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
        tau_b = pmb.BART("tau", X=Xtd, Y=y, m=m_tau)   # Y=y sets the response scale; prior centres on outcome, not 0 (docstring caveat)
        mu = pm.Deterministic("mu", prog + tau_b * z)
        sd = pm.HalfNormal("sd", 15)
        pm.Normal("y_obs", mu=mu, sigma=sd, observed=y, shape=mu.shape)
        idata = pm.sample(
            draws=p["draws"], tune=p["tune"], chains=p["chains"], cores=p["chains"],
            # BART/PGBART: see _fit_bart — scoped convergence is reported below on the
            # continuous `sd` scalar (plus divergences), not blanket per-unit r-hat.
            random_seed=seed, progressbar=False, compute_convergence_checks=False,
        )
    tau = idata.posterior["tau"].values.reshape(-1, n)
    if return_full:
        return {
            "cate": tau,
            "mu": idata.posterior["mu"].values.reshape(-1, n),
            "sd": idata.posterior["sd"].values.reshape(-1),
            "idata": idata,
            "convergence": convergence_report(idata, var_names=["sd"]),
        }
    return tau


ESTIMATORS = {"S-learner": s_learner, "T-learner": t_learner, "BCF": bcf}


# --------------------------------------------------------------------------
# Doubly-robust ATE (AIPW) — a model-agnostic cross-check of the BART work
# --------------------------------------------------------------------------
def aipw_ate(X, T, y, seed=1, n_boot=400, trim=0.02, n_folds=5):
    """Augmented IPW (doubly-robust) ATE via **cross-fitting** (Chernozhukov et
    al., double ML). The gradient-boosted outcome models mu0, mu1 and the
    logistic propensity are fit on K−1 folds and evaluated *out-of-fold*, so an
    adaptive learner never scores the observations it was trained on — this is
    what removes the own-observation plug-in bias and licenses the
    influence-function SE with boosted-tree nuisances. The AIPW score is
    consistent if *either* the outcome or the propensity model is right.

    Propensities are **clipped** to [trim, 1−trim] for a stable IPW correction:
    this winsorizes the weights, it does NOT drop units, so the estimand remains
    the full-population ATE. `n_clipped` reports how many units sit at the clip
    boundary (diagnostic only; kept in the estimate).

    The propensity is a logistic-in-raw-features fit — the same specification
    family the BART notebooks feed to BCF — so AIPW is a *methodologically*
    different cross-check (doubly-robust, boosted-tree outcomes), not a fully
    independent one. Returns a dict with the point estimate, a bootstrap
    distribution of the influence-function mean, the IF SE, n_clipped, and ci90."""
    from sklearn.ensemble import GradientBoostingRegressor
    from sklearn.linear_model import LogisticRegression
    X, T, y = np.asarray(X), np.asarray(T), np.asarray(y)
    n = len(y)

    def _crossfit_psi():
        """Out-of-fold AIPW scores: for each fold, nuisances are fit on the
        complement and evaluated on the held-out fold."""
        order = np.random.default_rng(seed).permutation(n)
        psi = np.empty(n)
        for te in np.array_split(order, min(n_folds, n)):
            tr = np.setdiff1d(np.arange(n), te)
            e = LogisticRegression(max_iter=1000).fit(X[tr], T[tr]).predict_proba(X[te])[:, 1]
            e = np.clip(e, trim, 1 - trim)
            m1 = GradientBoostingRegressor(n_estimators=80, max_depth=3, random_state=seed)
            m0 = GradientBoostingRegressor(n_estimators=80, max_depth=3, random_state=seed)
            mu1 = m1.fit(X[tr][T[tr] == 1], y[tr][T[tr] == 1]).predict(X[te])
            mu0 = m0.fit(X[tr][T[tr] == 0], y[tr][T[tr] == 0]).predict(X[te])
            Tt, yt = T[te], y[te]
            psi[te] = (mu1 - mu0 + Tt * (yt - mu1) / e - (1 - Tt) * (yt - mu0) / (1 - e))
        return psi

    psi = _crossfit_psi()
    point = float(psi.mean())
    inf_se = float(psi.std(ddof=1) / np.sqrt(n))

    # diagnostic: units whose full-sample propensity is at the clip boundary (kept, not dropped)
    e_full = LogisticRegression(max_iter=1000).fit(X, T).predict_proba(X)[:, 1]
    n_clipped = int(np.sum((e_full < trim) | (e_full > 1 - trim)))

    # bootstrap the influence-function mean (resample the out-of-fold scores)
    rng = np.random.default_rng(seed + 1)
    boot = np.array([psi[rng.integers(0, n, n)].mean() for _ in range(n_boot)])
    return {"ate": point, "boot": boot, "se": inf_se,
            "n_clipped": n_clipped, "n_trimmed": n_clipped,   # n_trimmed kept as a back-compat alias
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
    and report the F for the instrument's coefficient.

    This is the classical **homoskedastic** F (derived from R²). On real,
    heteroskedastic data prefer a robust/effective F (Montiel Olea–Pflueger);
    an F > 10 here is *necessary, not sufficient* for a strong instrument."""
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
    """**Simplified** McCrary-style manipulation check (a symmetric-window
    binomial test, not the full McCrary 2008 estimator). Compares the
    running-variable density just below vs just above the cutoff: local
    *sorting* across the threshold (gaming) shows up as a pile-up on one side,
    which invalidates RD. Within a narrow window each side we test the
    density-continuity null (≈ equal mass just below and just above) with a
    **binomial z-test**, so "no manipulation" is judged by significance
    (|z| < ~2), not an eyeballed ratio. The log-ratio is a ratio of properly
    normalized densities (scale-invariant — no additive smoothing).

    The full McCrary (2008) test fits a *local-linear* density on each side of
    the cutoff and reports the log-difference of the two intercepts with a Wald
    SE; this binomial version is the Cattaneo-style local-constant approximation
    — adequate for a "did anyone pile up at the threshold?" screen, but cite it
    as a simplified check, not the local-linear estimator.

    Returns (density_below, density_above, log_ratio, z_stat). `n_bins` is kept
    for backward-compatible call sites but unused; the window is set by `bandwidth`."""
    r = np.asarray(running, float)
    if bandwidth is None:
        bandwidth = (r.max() - r.min()) / 20      # a narrow window near the cutoff
    n_below = int(np.sum((r >= cutoff - bandwidth) & (r < cutoff)))
    n_above = int(np.sum((r >= cutoff) & (r < cutoff + bandwidth)))
    d_below = n_below / max(bandwidth, 1e-9)
    d_above = n_above / max(bandwidth, 1e-9)
    log_ratio = float(np.log(max(d_above, 1e-9) / max(d_below, 1e-9)))
    n = n_below + n_above
    z = float((n_above / n - 0.5) / np.sqrt(0.25 / n)) if n > 0 else 0.0
    return d_below, d_above, log_ratio, z


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
    # SLSQP can return weights slightly outside [0,1] / not summing to 1, or fail
    # to converge. These weights feed the placebo p-values, LOO and launch-date
    # sensitivity, so clip to the simplex and fall back to equal weights rather
    # than silently propagate an infeasible solution.
    w = np.clip(res.x, 0.0, 1.0)
    s = w.sum()
    w = w / s if s > 0 else np.full(J, 1 / J)
    if not res.success:
        warnings.warn(f"sc_weights_slsqp did not converge ({res.message!r}); "
                      "returning clipped/renormalized weights.", RuntimeWarning)
    return w


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
            # Pure NUTS (Dirichlet weights + HalfNormal sd): standard r-hat/ESS
            # apply to every parameter, so let pm.sample run its own checks and
            # surface a scoped readout below via convergence_report.
            random_seed=seed, progressbar=False, target_accept=0.95,
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
        "convergence": convergence_report(idata, var_names=["w", "sd"]),
    }


def synthetic_control_ar1(target, donors, pre, post, seed=1, draws=1000, tune=1000,
                          chains=4):
    """Bayesian synthetic control with **AR(1) errors** — the correctly-specified
    counterpart to `synthetic_control`.

    Why this exists
    ---------------
    `synthetic_control` puts an *iid* Normal likelihood on the pre-period fit and
    then draws *independent* noise per post-period week. That is wrong here, and
    not by a little. The donor pool can rarely match the treated unit's factor
    loadings exactly, and one of the shared factors is a **random walk** (the macro
    shock in `dgp.geo_panel`). Whatever macro loading the weights fail to match is
    left in the residual, so the residual is itself near-random-walk: strongly
    positively autocorrelated, not iid.

    That mistake is invisible in the *weekly* effect and fatal in the **cumulative
    total**, which is the number the euro decision actually integrates. For an iid
    error, Var(sum of H weeks) = H*sigma^2. For a positively autocorrelated error it
    grows toward H^2*sigma^2 — because the errors do not cancel, they persist. An
    iid likelihood therefore reports a total that is far too confident: in this DGP
    it under-prices the 20-week total's sd by ~3x and the nominal 90% interval
    covers the truth only about half the time.

    The model
    ---------
    Same simplex (Dirichlet) weights, but the residual e_t = y_t - w.donors_t is
    given an AR(1) law, e_t = rho*e_{t-1} + eps_t, eps ~ N(0, sigma). Substituting
    e_t out gives a likelihood written entirely in observed quantities,

        y_0     ~ Normal(mu_0, sigma / sqrt(1 - rho^2))          (stationary start)
        y_t     ~ Normal(mu_t + rho*(y_{t-1} - mu_{t-1}), sigma)  for t >= 1

    which is what we hand to PyMC (a `Potential` on a deterministic residual would
    also work, but this keeps every term an honest `observed=`).

    The counterfactual, honestly propagated
    ---------------------------------------
    The post-period counterfactual residual is **simulated forward** from the last
    observed pre-period residual — e_{T+h} = rho*e_{T+h-1} + eps — rather than drawn
    fresh each week. This is the whole point: it is what makes the errors persist
    across the post window, so the cumulative total's uncertainty grows correctly
    and the interval earns its nominal coverage. Conditioning on the last pre-period
    residual (instead of starting from the stationary distribution) is also what
    keeps the *early* post weeks appropriately tight.

    The pre-period counterfactual band is the one-step-ahead predictive, so the
    pre-period gap hovers around zero with an honest band rather than collapsing to
    exactly zero.

    Returns the same dict shape as `synthetic_control`, plus `rho_samples`, so the
    two are drop-in comparable in the notebook.
    """
    import pymc as pm

    J = donors.shape[0]
    y_pre = np.asarray(target[pre], dtype=float)      # (T,)
    D_pre = np.asarray(donors[:, pre], dtype=float)   # (J, T)

    with pm.Model() as model:
        w = pm.Dirichlet("w", a=np.ones(J))
        sigma = pm.HalfNormal("sigma", 5)
        # Stationary AR(1). Bounded away from |1| so sigma/sqrt(1-rho^2) stays finite;
        # the posterior in this DGP piles up near the upper end, which is the finding.
        rho = pm.Uniform("rho", -0.98, 0.98)

        mu = pm.math.dot(w, D_pre)                    # (T,) mean blend, pre-period

        # t = 0: stationary marginal of the AR(1) residual.
        pm.Normal("obs0", mu=mu[0], sigma=sigma / pm.math.sqrt(1.0 - rho ** 2),
                  observed=y_pre[0])
        # t >= 1: one-step-ahead conditional. Note the residual y_{t-1} - mu_{t-1}
        # is a function of w, so this term is what ties rho to the weights.
        pm.Normal("obs", mu=mu[1:] + rho * (y_pre[:-1] - mu[:-1]), sigma=sigma,
                  observed=y_pre[1:])

        idata = pm.sample(
            draws=draws, tune=tune, chains=chains, cores=chains,
            random_seed=seed, progressbar=False, target_accept=0.95,
        )

    W_post = idata.posterior["w"].values.reshape(-1, J)        # (S, J)
    sig_post = idata.posterior["sigma"].values.reshape(-1)     # (S,)
    rho_post = idata.posterior["rho"].values.reshape(-1)       # (S,)
    S = W_post.shape[0]

    cf_mean = W_post @ np.asarray(donors, dtype=float)         # (S, W) mean blend, all weeks
    target = np.asarray(target, dtype=float)
    W_len = cf_mean.shape[1]
    idx = np.arange(W_len)
    pre_idx, post_idx = idx[pre], idx[post]

    rng = np.random.default_rng(seed + 12345)
    cf_pred = cf_mean.copy()

    # --- pre-period: one-step-ahead predictive band --------------------------------
    # e_t | e_{t-1} ~ N(rho*e_{t-1}, sigma), with the *observed* previous residual.
    resid_pre = target[None, pre_idx] - cf_mean[:, pre_idx]    # (S, T) per-draw residual
    eps = rng.standard_normal((S, len(pre_idx)))
    cf_pred[:, pre_idx[0]] = (
        cf_mean[:, pre_idx[0]]
        + eps[:, 0] * sig_post / np.sqrt(1.0 - rho_post ** 2)   # stationary at t=0
    )
    cf_pred[:, pre_idx[1:]] = (
        cf_mean[:, pre_idx[1:]]
        + rho_post[:, None] * resid_pre[:, :-1]
        + eps[:, 1:] * sig_post[:, None]
    )

    # --- post-period: PROPAGATE the residual forward (the actual fix) ---------------
    # Start from the last residual we actually observed (the treated unit is still
    # untreated at the end of the pre-period), then run the AR(1) recursion. The
    # errors persist, so the *cumulative* effect's uncertainty compounds correctly.
    e = resid_pre[:, -1].copy()                                # (S,) last observed residual
    for h, t in enumerate(post_idx):
        e = rho_post * e + rng.standard_normal(S) * sig_post
        cf_pred[:, t] = cf_mean[:, t] + e

    effect = target[None, :] - cf_pred
    pre_rmse = float(np.sqrt(np.mean((target[None, :] - cf_mean).mean(0)[pre] ** 2)))
    return {
        "counterfactual_samples": cf_pred,
        "counterfactual_mean": cf_mean,
        "effect_samples": effect,
        "weight_samples": W_post,
        "rho_samples": rho_post,
        "sigma_samples": sig_post,
        "pre_rmse": pre_rmse,
        "idata": idata,
        "convergence": convergence_report(idata, var_names=["w", "sigma", "rho"]),
    }


def iv_binary_treatment(df, *, outcome: str, treatment: str, instrument: str,
                        seed: int = 1, draws: int = 1000, tune: int = 1000, chains: int = 4,
                        target_accept: float = 0.9):
    """Bayesian IV with a **probit first stage** — for a BINARY endogenous treatment.

    Why this exists (the nb11 counterpart of `synthetic_control_ar1`)
    ----------------------------------------------------------------
    CausalPy's Bayesian IV fits a joint *Gaussian* to (treatment, outcome). When the
    treatment is binary — exposed / not exposed — that is a linear probability model
    in disguise, and it is misspecified in a way you can see: its posterior predictive
    puts ~a third of the replicated "exposures" outside [0, 1], i.e. at values the
    variable cannot take. The 2SLS/Wald *point* estimate does not care (with a binary
    instrument it is just a ratio of two slopes, and it is consistent regardless), but
    the Bayesian posterior does: it inherits a small bias and under-covers.

    The model — a recursive (triangular) system with a latent probit index
    ---------------------------------------------------------------------
        T* = a0 + a1*Z + u,     T = 1{T* > 0},      u ~ N(0, 1)
        Y  = b0 + b*T  + e,                         e ~ N(0, sigma)
        corr(u, e) = rho        <- the endogeneity. rho != 0 IS the confounding.

    `u` has its variance fixed to 1 because a probit index is only identified up to
    scale — the usual normalization, not a modelling choice.

    The likelihood, honestly factored
    ---------------------------------
    Y is continuous and T is binary, so the joint density of one observation is
    f(y, t) = f(e) * P(T = t | e), with e = y - b0 - b*t pinned by the outcome equation
    (Jacobian 1). Conditioning the latent index error on e is what carries the
    endogeneity:

        u | e ~ N(rho * e / sigma,  1 - rho^2)
        P(T = 1 | e) = Phi( (a0 + a1*Z + rho*e/sigma) / sqrt(1 - rho^2) )

    so the log-likelihood is  logN(e; 0, sigma) + t*log(p) + (1-t)*log(1-p). That is
    the whole model; there is no control-function two-step and no plug-in residual.

    `b` is the ATE of the (constant-effect) treatment. With a binary instrument and a
    binary treatment this is also the LATE, which is the estimand notebook 11 targets.

    Returns dict with beta_samples (the effect), rho_samples, first_stage_samples,
    idata and a convergence report.
    """
    import pymc as pm
    import pytensor.tensor as pt

    y = np.asarray(df[outcome], dtype=float)
    t_obs = np.asarray(df[treatment], dtype=float)
    z = np.asarray(df[instrument], dtype=float)

    uniq = np.unique(t_obs)
    if not set(uniq).issubset({0.0, 1.0}):
        raise ValueError(
            f"iv_binary_treatment needs a 0/1 treatment; '{treatment}' takes values {uniq[:5]}. "
            "For a continuous endogenous regressor use the joint-Gaussian IV (cmp.estimators.iv)."
        )

    with pm.Model() as model:
        # Outcome equation. Weakly informative on the scale of the data — NOT centred on
        # the 2SLS point (see nb11's "PRIORS, PRICED" block for what that would cost).
        b0 = pm.Normal("b0", 0.0, 50.0)
        beta = pm.Normal("beta", 0.0, 50.0)          # the causal effect
        sigma = pm.HalfNormal("sigma", 25.0)

        # First stage, on the probit index scale.
        a0 = pm.Normal("a0", 0.0, 5.0)
        a1 = pm.Normal("a1", 0.0, 5.0)               # instrument strength

        # Endogeneity. rho != 0 is exactly what makes OLS wrong.
        rho = pm.Uniform("rho", -0.95, 0.95)

        e = y - b0 - beta * t_obs                    # pinned by the outcome equation
        index = a0 + a1 * z + rho * e / sigma        # E[u | e], shifted index
        p = pm.math.invprobit(index / pm.math.sqrt(1.0 - rho ** 2))
        p = pt.clip(p, 1e-9, 1 - 1e-9)

        pm.Potential("loglik",
                     pm.logp(pm.Normal.dist(0.0, sigma), e).sum()
                     + (t_obs * pt.log(p) + (1.0 - t_obs) * pt.log(1.0 - p)).sum())

        idata = pm.sample(draws=draws, tune=tune, chains=chains, cores=chains,
                          random_seed=seed, progressbar=False, target_accept=target_accept)

    post = idata.posterior
    return {
        "beta_samples": post["beta"].values.ravel(),
        "rho_samples": post["rho"].values.ravel(),
        "a1_samples": post["a1"].values.ravel(),
        "sigma_samples": post["sigma"].values.ravel(),
        "idata": idata,
        "convergence": convergence_report(idata, var_names=["beta", "rho", "a1", "sigma"]),
    }


def placebo_in_space(sales, treated_idx, pre, post, pre_rmse=None, rmse_multiple=3.0):
    """Permutation inference: refit synthetic control treating each donor as
    if *it* were treated, and collect the placebo gaps. Following Abadie,
    discard placebos whose pre-fit RMSE is > `rmse_multiple` x the real
    treated unit's (a bad synthetic match makes a meaningless gap).

    `pre_rmse` defaults to the real treated unit's own **SLSQP** pre-fit RMSE,
    so the Abadie filter compares like with like — the same fitter used for the
    placebos. Pass a value only to override with an external reference (e.g. a
    Bayesian fit's RMSE); mixing fitters can over- or under-filter. Raises
    ValueError if every placebo is discarded (widen `rmse_multiple`).

    Returns (placebo_gaps array (n_kept, W), real_gap (W,), p_value)."""
    n = sales.shape[0]
    donors = np.delete(sales, treated_idx, axis=0)
    real_gap, _ = sc_effect_slsqp(sales[treated_idx], donors, pre, post)
    if pre_rmse is None:                       # same-fitter (SLSQP) reference — see docstring
        pre_rmse = float(np.sqrt(np.mean(real_gap[pre] ** 2)))
    placebo_gaps = []
    for j in range(n):
        if j == treated_idx:
            continue
        others = np.delete(np.arange(n), [treated_idx, j])
        gap, _ = sc_effect_slsqp(sales[j], sales[others], pre, post)
        if np.sqrt(np.mean(gap[pre] ** 2)) < rmse_multiple * pre_rmse:
            placebo_gaps.append(gap)
    if not placebo_gaps:
        raise ValueError(
            "all placebos were filtered out by the RMSE gate — raise rmse_multiple "
            "or check the donor pool (too few comparable donors)."
        )
    placebo_gaps = np.array(placebo_gaps)
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
    # and its 90% interval can exclude the truth (nb11's "PRIORS, PRICED" block
    # fits both and prints the widths: the default band is several times too
    # narrow on that DGP and misses the planted effect). Pass
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
