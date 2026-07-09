"""Statistical-content (truth-recovery) guards for the LEGACY-env estimators
— the CausalPy DiD / ITS / IV wrappers behind notebooks 08, 10, 11.

`tests/test_notebooks.py` only asserts the notebooks *execute*; a DGP or wrapper
could regress and still "run" while silently recovering garbage. Here we assert
each quasi-experimental estimator actually recovers the planted effect with the
truth inside its 90% interval, on a fast seed — the same recover-the-truth
contract the notebooks show.

These import `causalpy`, so they run only in the legacy env (`.venv-legacy`,
pymc<6) and are skipped (import-skipped) in the core env. Run them with:
    .venv-legacy/bin/python -m pytest tests/test_estimators_legacy.py
"""
import numpy as np
import pytest

pytest.importorskip("causalpy")   # legacy env only; skipped under core (pymc>=6)

from cmp import dgp, estimators as est


def test_did_recovers_step():
    """nb08: the Bayesian DiD recovers the €400/store/week rollout effect.
    Mirrors the notebook's 2x2 collapse + standardize-then-back-transform (the
    fix for CausalPy's O(1)-scaled default priors)."""
    df, true_effect = dgp.did_rollout(n_stores=40, n_weeks=24, launch_week=12, seed=5)
    agg = df.groupby(["unit", "group", "post_treatment"])["revenue"].mean().reset_index()
    agg["t"] = agg["post_treatment"].astype(int).astype(float)
    sd = agg["revenue"].std()
    agg["revenue_z"] = (agg["revenue"] - agg["revenue"].mean()) / sd
    r = est.did(agg, formula="revenue_z ~ 1 + group*post_treatment", fast=True)
    impact = np.asarray(r.causal_impact).ravel() * sd
    lo, hi = np.quantile(impact, [0.05, 0.95])
    assert lo <= true_effect <= hi, f"€{true_effect} outside 90% CI [{lo:.0f}, {hi:.0f}]"


def test_its_recovers_step():
    """nb10: the interrupted time series recovers the planted +3pp step."""
    df, true_lift, rday = dgp.its_redesign(n_days=180, redesign_day=120, seed=31)
    r = est.its(df, treatment_time=rday, formula="conversion ~ 1 + t + sin7 + cos7", fast=True)
    impact = r.post_impact.mean(dim=["treated_units", "obs_ind"]).values.ravel()
    lo, hi = np.quantile(impact, [0.05, 0.95])
    assert lo <= true_lift <= hi, f"{true_lift:.3f} outside 90% CI [{lo:.3f}, {hi:.3f}]"


def test_iv_recovers_late_with_weak_priors():
    """nb11: with weakly-informative priors the Bayesian IV covers the true €15
    LATE. Guards the fix for CausalPy's default N(2SLS, 1) priors, whose ~3x
    too-narrow interval excludes the truth."""
    df, te = dgp.iv_ad_exposure(n=3000, true_effect=15.0, seed=37)
    r = est.iv(
        df, "ad_exposure ~ 1 + encouragement", "sales ~ 1 + ad_exposure",
        instrument_col="encouragement", treatment_col="ad_exposure", outcome_col="sales",
        fast=True, priors={"mus": [0, 0], "sigmas": [50, 50], "eta": 2, "lkj_sd": 2},
    )
    post = r.idata.posterior["beta_z"].sel(covariates="ad_exposure").values.ravel()
    lo, hi = np.quantile(post, [0.05, 0.95])
    assert lo <= te <= hi, f"€{te} outside 90% CI [{lo:.1f}, {hi:.1f}]"
