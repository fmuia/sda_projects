"""Prior-scale experiments for the Ch. 13 joint-Gaussian Bayesian IV (nb11).

One worker, one fitted panel: simulate the nb11 ad-exposure market, fit CausalPy's
joint-Gaussian IV with the error-scale prior rate (`sd_dist = Exponential(rate)`)
as the only knob, and return a small dict of scalars. The forensic in Appendix 13.A
established the mechanism by DIFFUSING that prior (rate 2 -> 0.05); these workers
measure the dose-response — beta as a continuous function of the rate — and the two
repairs a practitioner would actually use: match the rate to sd(Y) (arm C), or
standardise Y and leave the shipped prior alone (arm B).

Caching lives INSIDE the worker, so a notebook cell and a driver script calling
`sweep_fit(...)` with the same arguments share one cache entry — the fingerprint
covers this module's source, not the caller's lambda.
"""
from __future__ import annotations

import numpy as np

from . import classical as cl
from . import dgp
from . import estimators as est
from .cache import load_or_run

N_PANEL = 3000
TRUE_EFFECT = 15.0


def _phi_cf(df) -> float:
    """Control-function slope: regress X on Z, then Y on (X, v-hat); the v-hat
    coefficient is the euro value of one unit of self-selection — the same
    composite the joint Gaussian expresses as rho * sigma_Y / sigma_X."""
    z = df["encouragement"].to_numpy(float)
    x = df["ad_exposure"].to_numpy(float)
    y = df["sales"].to_numpy(float)
    Z = np.column_stack([np.ones_like(z), z])
    v = x - Z @ np.linalg.lstsq(Z, x, rcond=None)[0]
    X2 = np.column_stack([np.ones_like(x), x, v])
    return float(np.linalg.lstsq(X2, y, rcond=None)[0][2])


def _ppc_outside_unit(idata, df, sigma_x) -> float:
    """P(replicated exposure outside [0,1]) under the joint Gaussian, computed in
    closed form from the posterior rather than by simulation: the first-stage mean
    takes exactly two values (Z is 0/1), so the outside-mass is a two-term mixture
    of Gaussian tails per draw."""
    from scipy.stats import norm

    bt = idata.posterior["beta_t"].values.reshape(-1, 2)  # (draws, [intercept, Z])
    w1 = float(df["encouragement"].mean())
    out = 0.0
    for z, w in ((0.0, 1.0 - w1), (1.0, w1)):
        mu = bt[:, 0] + bt[:, 1] * z
        out += w * (norm.cdf((0.0 - mu) / sigma_x) + norm.sf((1.0 - mu) / sigma_x))
    return float(out.mean())


def _error_cov(idata) -> np.ndarray:
    """Per-draw 2x2 error covariance, rows/cols ordered (sales, exposure) — the
    model stacks (mu_y, mu_t). Rebuilt from the Cholesky factor if `cov` is absent."""
    post = idata.posterior
    if "cov" in post:
        return np.asarray(post["cov"].values).reshape(-1, 2, 2)
    ch = np.asarray(post["chol_cov"].values)
    flat = ch.reshape(-1, *ch.shape[2:])
    if flat.ndim == 2 and flat.shape[1] == 3:  # packed [L00, L10, L11]
        L = np.zeros((len(flat), 2, 2))
        L[:, 0, 0], L[:, 1, 0], L[:, 1, 1] = flat[:, 0], flat[:, 1], flat[:, 2]
    else:
        L = flat.reshape(-1, 2, 2)
    return L @ np.swapaxes(L, 1, 2)


def sweep_fit(rate: float, seed: int, *, standardise: bool = False,
              coef_sd: float = 50.0, fast: bool = True) -> dict:
    """Fit one panel at one error-scale prior rate; return scalars only.

    `standardise=True` is arm B: sales enters the model as (Y - mean)/sd and every
    euro-denominated output below is mapped back through that sd, so the returned
    numbers are always in euros and directly comparable across arms.
    """
    key = "11_iv_scale_sweep"
    inputs = dict(rate=round(float(rate), 6), seed=seed, standardise=standardise,
                  coef_sd=coef_sd, n=N_PANEL, fast=fast, model="causalpy-gaussian")
    return load_or_run(key, lambda: _sweep_fit_impl(rate, seed, standardise, coef_sd, fast),
                       inputs=inputs, verbose=False)


def tight_coef_fit(rate: float, seed: int, *, fast: bool = True) -> dict:
    """E4 arm: the library-default coefficient priors (centred on this panel's own
    2SLS estimates, sd = 1) with the error-scale prior held at `rate` — the
    false-precision pathology isolated from the scale-prior bias. Compare against
    `sweep_fit(rate, seed)` (same scale prior, weak N(0, 50^2) coefficients): the
    means should nearly agree while the interval widths should not."""
    key = "11_iv_tightcoef"
    inputs = dict(rate=round(float(rate), 6), seed=seed, n=N_PANEL, fast=fast,
                  model="causalpy-gaussian-tightcoef")
    return load_or_run(key, lambda: _tight_coef_impl(rate, seed, fast),
                       inputs=inputs, verbose=False)


def _tight_coef_impl(rate, seed, fast):
    import logging

    pml = logging.getLogger("pymc")
    lvl = pml.level
    pml.setLevel(logging.CRITICAL + 1)
    try:
        df, true_effect = dgp.iv_ad_exposure(n=N_PANEL, true_effect=TRUE_EFFECT, seed=seed)
        z = df["encouragement"].to_numpy(float)
        x = df["ad_exposure"].to_numpy(float)
        y = df["sales"].to_numpy(float)
        # Reproduce CausalPy's default prior centres: first-stage OLS of X on Z,
        # then the 2SLS second stage of Y on the fitted X.
        Z = np.column_stack([np.ones_like(z), z])
        fs = np.linalg.lstsq(Z, x, rcond=None)[0]
        Xhat = np.column_stack([np.ones_like(z), Z @ fs])
        ss = np.linalg.lstsq(Xhat, y, rcond=None)[0]

        r = est.iv(df, "ad_exposure ~ 1 + encouragement", "sales ~ 1 + ad_exposure",
                   instrument_col="encouragement", treatment_col="ad_exposure",
                   outcome_col="sales", fast=fast,
                   priors={"mus": [list(fs), list(ss)], "sigmas": [1, 1],
                           "eta": 2, "lkj_sd": rate})
        beta = r.idata.posterior["beta_z"].sel(covariates="ad_exposure").values.ravel()
        lo, hi = (float(q) for q in np.quantile(beta, [0.05, 0.95]))
        conv = est.convergence_report(r.idata, var_names=["beta_z", "beta_t"])
        return dict(rate=float(rate), seed=seed, beta=float(beta.mean()), lo=lo, hi=hi,
                    covers=bool(lo <= true_effect <= hi), width=hi - lo,
                    prior_centre=float(ss[1]),
                    max_rhat=float(conv["max_rhat"]),
                    divergences=int(conv["n_divergences"] or 0))
    finally:
        pml.setLevel(lvl)


def _sweep_fit_impl(rate, seed, standardise, coef_sd, fast):
    import logging

    pml = logging.getLogger("pymc")
    lvl = pml.level
    pml.setLevel(logging.CRITICAL + 1)  # NUTS notices log at ERROR; silence for the loop
    try:
        df, true_effect = dgp.iv_ad_exposure(n=N_PANEL, true_effect=TRUE_EFFECT, seed=seed)

        # Classical anchors for this panel — deterministic given the seed.
        naive = float(np.polyfit(df["ad_exposure"], df["sales"], 1)[0])
        iv2 = cl.iv_2sls(df, outcome="sales", endog="ad_exposure", instrument="encouragement")
        fstat = float(est.first_stage_F(df["encouragement"], df["ad_exposure"]))
        phi_cf = _phi_cf(df)

        scale = 1.0
        fit_df = df
        if standardise:
            scale = float(df["sales"].std(ddof=0))
            fit_df = df.assign(sales=(df["sales"] - df["sales"].mean()) / scale)

        r = est.iv(fit_df, "ad_exposure ~ 1 + encouragement", "sales ~ 1 + ad_exposure",
                   instrument_col="encouragement", treatment_col="ad_exposure",
                   outcome_col="sales", fast=fast,
                   priors={"mus": [0, 0], "sigmas": [coef_sd, coef_sd],
                           "eta": 2, "lkj_sd": rate})
        beta = r.idata.posterior["beta_z"].sel(covariates="ad_exposure").values.ravel() * scale
        Sig = _error_cov(r.idata)
        ok = np.isfinite(Sig).all(axis=(1, 2))
        sy = np.sqrt(Sig[ok, 0, 0]) * scale
        sx = np.sqrt(Sig[ok, 1, 1])
        rho = Sig[ok, 0, 1] / np.sqrt(Sig[ok, 0, 0] * Sig[ok, 1, 1])
        phi = rho * sy / sx
        conv = est.convergence_report(r.idata, var_names=["beta_z", "beta_t"])

        lo, hi = (float(q) for q in np.quantile(beta, [0.05, 0.95]))
        b2 = float(iv2.estimate)
        return dict(
            rate=float(rate), seed=seed, standardise=standardise, coef_sd=coef_sd,
            beta=float(beta.mean()), lo=lo, hi=hi, covers=bool(lo <= true_effect <= hi),
            sigma_y=float(sy.mean()), sigma_x=float(sx.mean()), rho=float(rho.mean()),
            phi=float(phi.mean()), phi_cf=phi_cf,
            naive=naive, tsls=b2, tsls_lo=float(iv2.ci[0]), tsls_hi=float(iv2.ci[1]),
            fstat=fstat,
            # position on the OLS->2SLS line: s = 1 is fully corrected, s = 0 is naive
            s=float(1.0 - (beta.mean() - b2) / (naive - b2)),
            ppc_out=_ppc_outside_unit(r.idata, df, float(sx.mean())),
            max_rhat=float(conv["max_rhat"]), divergences=int(conv["n_divergences"] or 0),
        )
    finally:
        pml.setLevel(lvl)
