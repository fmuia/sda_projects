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
    # net value is euros (mean - cost); ROI is a ratio (net / cost) — must not be conflated.
    mean_v = float(samples.mean())
    assert abs(d["expected_net_value"] - (mean_v - 300.0)) < 1e-6
    assert abs(d["expected_roi"] - (mean_v - 300.0) / 300.0) < 1e-9
    assert d["expected_roi"] < 1.0          # a ratio (~0.67), not the ~200-euro net amount


# --------------------------------------------------------------------------
# depth diagnostics
# --------------------------------------------------------------------------
def test_auuc_ranks_between_zero_and_one():
    rng = np.random.default_rng(0)
    tau = rng.normal(5, 5, 500)
    good = tau + rng.normal(0, 1, 500)      # near-perfect ranker
    bad = rng.normal(0, 1, 500)             # random ranker
    assert metrics.auuc(good, tau) > metrics.auuc(bad, tau)
    assert metrics.auuc(good, tau) <= 1.01


def test_uplift_by_decile_is_monotone_for_good_ranker():
    rng = np.random.default_rng(0)
    tau = rng.normal(5, 5, 500)
    dec = metrics.uplift_by_decile(tau + rng.normal(0, 0.5, 500), tau)
    # top decile true effect should exceed bottom decile
    assert dec.true_effect.iloc[0] > dec.true_effect.iloc[-1]


def test_aipw_recovers_known_ate():
    d, true_ate = dgp.dag_control_demo(n=1500, seed=3)
    r = est.aipw_ate(d[["loyalty"]].values, d["email"].values, d["spend"].values, seed=1, n_boot=150)
    assert abs(r["ate"] - true_ate) < 1.5
    assert r["ci90"][0] < r["ate"] < r["ci90"][1]
    assert "n_clipped" in r                  # cross-fit version reports clipped (not dropped) units


def test_first_stage_F_separates_strong_from_weak():
    df, _ = dgp.iv_ad_exposure(n=1000, seed=1)
    strong = est.first_stage_F(df["encouragement"], df["ad_exposure"])
    weak = est.first_stage_F(np.random.default_rng(0).normal(size=1000), df["ad_exposure"])
    assert strong > 10 and weak < strong


def test_mccrary_flags_no_manipulation():
    df, _ = dgp.rdd_perk(n=2000, seed=1)
    _, _, _log_ratio, z = est.mccrary_density(df["spend"].values, 100.0, bandwidth=15)
    assert abs(z) < 3.0           # smooth density -> continuity null not rejected


def test_mccrary_flags_manipulation():
    df, _ = dgp.rdd_perk(n=2000, seed=1)
    r = df["spend"].values.copy()
    r[(r > 92) & (r < 100)] = 100.5   # sort just-below units to just-above the cutoff
    _, _, _lr, z = est.mccrary_density(r, 100.0, bandwidth=15)
    assert z > 3.0                # a pile-up above -> strongly flagged


def test_e_value_grows_with_effect():
    assert metrics.e_value(10, cost=0, sd=5) > metrics.e_value(2, cost=0, sd=5)


def test_e_value_requires_sd():
    # The E-value lives on the risk-ratio scale, so a raw euro effect must be
    # standardized first. sd is mandatory — the old no-sd ratio fallback was
    # directionally inverted (huge robustness for effects *near* the threshold).
    with pytest.raises(ValueError):
        metrics.e_value(6.0, cost=8.0)


def test_policy_comparison_oracle_is_best():
    rng = np.random.default_rng(0)
    tau = rng.normal(5, 6, 400)
    samples = tau[None, :] + rng.normal(0, 2, (200, 400))
    comp = policy.policy_comparison(samples, tau, cost=5.0)
    oracle = comp.loc[comp.policy == "oracle", "profit"].values[0]
    assert oracle >= comp["profit"].max() - 1e-6


def test_random_baseline_is_independent():
    # Regression guard for the RNG-coupling bug: if policy_comparison drew its
    # random mask from default_rng(seed), it would replay whatever a DGP seeded
    # on the same integer drew first. We make tau depend on that very stream so
    # a coupled mask would cherry-pick the high-tau units and beat a fair coin.
    seed, n = 7, 4000
    u = np.random.default_rng(seed).random(n)        # the DGP's would-be first draw
    tau = np.where(u < 0.5, 12.0, 2.0)               # coupled mask would grab the +12s
    samples = tau[None, :]
    comp = policy.policy_comparison(samples, tau, cost=5.0, seed=seed)
    treat_all = comp.loc[comp.policy == "treat-all", "profit"].values[0]
    rand = comp.loc[comp.policy == "random-50%", "profit"].values[0]
    frac = comp.loc[comp.policy == "random-50%", "frac_contacted"].values[0]
    assert 0.45 < frac < 0.55
    # a fair random half earns ~0.5*treat_all; the coupled bug earned far more
    assert abs(rand - 0.5 * treat_all) < 0.15 * abs(treat_all)
