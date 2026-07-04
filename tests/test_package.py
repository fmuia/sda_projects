"""Unit / smoke tests for the shared cmp package (core env, pymc>=6).

The most important test here is `test_bart_cate_is_nonzero`: it guards the
#1 pymc-bart gotcha — counterfactual scoring silently returns frozen (all
zero) effects unless the BART node is resampled with sample_vars. If that
regresses, every uplift notebook silently produces zeros, so we assert a
known-nonzero effect is actually recovered.
"""
import numpy as np
import pytest

from cmp import dgp, estimators as est, metrics, policy

TINY = dict(draws=60, tune=60, chains=1, m=20)


# --------------------------------------------------------------------------
# dgp
# --------------------------------------------------------------------------
def test_uplift_shapes_and_regimes():
    df = dgp.uplift_customers(n=200, regime="observational", seed=1)
    assert len(df) == 200
    assert set(df.attrs["feature_cols"]).issubset(df.columns)
    # randomized regime has ~constant propensity
    dfr = dgp.uplift_customers(n=200, regime="randomized", seed=1)
    assert np.allclose(dfr["propensity"], 0.5)


def test_uplift_confounder_shifts_naive_estimate():
    """A hidden confounder should bias the naive diff-in-means upward."""
    base = dgp.uplift_customers(n=2000, regime="observational", confounder_strength=0.0, seed=1)
    conf = dgp.uplift_customers(n=2000, regime="observational", confounder_strength=8.0, seed=1)

    def naive(d):
        return d.loc[d["T"] == 1, "y"].mean() - d.loc[d["T"] == 0, "y"].mean()

    assert naive(conf) > naive(base)


def test_geo_panel_shape():
    sales_df, eff, launch, treated = dgp.geo_panel(n_weeks=40, launch_week=28, n_dmas=10)
    assert sales_df.shape == (40, 10)
    assert (eff[:launch] == 0).all() and (eff[launch:] != 0).any()


# --------------------------------------------------------------------------
# estimators — the gotcha guard
# --------------------------------------------------------------------------
@pytest.mark.parametrize("learner", [est.t_learner, est.s_learner])
def test_bart_cate_is_nonzero(learner):
    """GOTCHA GUARD: BART counterfactual CATE must be non-zero on a known
    non-zero effect. If sample_vars=['mu'] regresses, this returns all 0."""
    rng = np.random.default_rng(0)
    n = 200
    X = rng.normal(size=(n, 2))
    T = rng.integers(0, 2, n).astype(float)
    tau_true = 5.0
    y = X[:, 0] + tau_true * T + rng.normal(0, 0.5, n)
    cate = learner(X, T, y, seed=1, **TINY)
    assert cate.shape == (TINY["draws"] * TINY["chains"], n)
    assert abs(cate.mean()) > 1.0, "CATE collapsed toward zero — pymc-bart gotcha!"


def test_bcf_recovers_positive_effect():
    df = dgp.uplift_customers(n=300, regime="observational", seed=7)
    X = df[df.attrs["feature_cols"]].values
    from sklearn.linear_model import LogisticRegression
    phat = LogisticRegression(max_iter=500).fit(X, df["T"]).predict_proba(X)[:, 1]
    cate = est.bcf(X, df["T"].values, df["y"].values, phat, seed=1, **TINY)
    assert cate.shape[1] == 300
    # true ATE is positive here
    assert cate.mean() > 0


def test_synthetic_control_recovers_lift():
    sales_df, eff, launch, treated = dgp.geo_panel(n_weeks=40, launch_week=28, n_dmas=12, seed=3)
    sales = sales_df.values.T
    pre, post = slice(0, launch), slice(launch, 40)
    sc = est.synthetic_control(sales[0], sales[1:], pre, post, seed=1, draws=200, tune=200, chains=2)
    est_total = sc["effect_samples"][:, post].sum(1).mean()
    true_total = eff[post].sum()
    # within a factor of ~2 of the truth (SC is mildly conservative)
    assert 0.4 * true_total < est_total < 1.6 * true_total


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------
def test_interval_coverage_calibrated():
    rng = np.random.default_rng(0)
    tau = rng.normal(5, 2, 500)
    # perfectly calibrated samples centred on truth
    samples = tau[None, :] + rng.normal(0, 1, (400, 500))
    cov = metrics.interval_coverage(samples, tau, level=0.90)
    assert 0.80 < cov <= 1.0
    overall, by_dec = metrics.interval_coverage(samples, tau, level=0.90, by_decile=True)
    assert len(by_dec) >= 8


def test_pehe_zero_when_perfect():
    tau = np.arange(50.0)
    samples = np.tile(tau, (10, 1))
    assert metrics.pehe(samples, tau) < 1e-9


# --------------------------------------------------------------------------
# policy
# --------------------------------------------------------------------------
def test_profit_curve_and_voi():
    rng = np.random.default_rng(0)
    tau = rng.normal(10, 5, 300)
    samples = tau[None, :] + rng.normal(0, 2, (200, 300))
    frac, cum, stop = policy.profit_curve(samples.mean(0), tau, cost=8.0)
    assert 0 <= stop < len(tau)
    voi = policy.value_of_information(samples, cost=8.0)
    assert voi["total"] >= 0
    assert voi["voi_on_straddlers"] <= voi["total"] + 1e-6


def test_go_no_go():
    samples = np.random.default_rng(0).normal(500, 50, 2000)
    d = policy.go_no_go(samples, cost=300.0)
    assert d["decision"] == "GO"
    assert d["P_value_gt_cost"] > 0.9
