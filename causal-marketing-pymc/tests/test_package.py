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


# nb07's actual panel. The AR(1) tests below MUST use it rather than a small toy panel:
# with only 12 donors over 40 weeks the donor pool happens to span the treated market
# almost perfectly, the residual really is near-iid (rho ~ 0.08), and the AR(1) model
# correctly reports that there is nothing to fix. Asserting "the fix widens the interval"
# on a panel with no autocorrelation would be testing the fix on a world that does not
# have the disease — the test would fail for the right reason, and we would learn nothing.
NB07_PANEL = dict(n_weeks=60, launch_week=40, n_dmas=30, seed=5)


def _nb07_panel():
    sales_df, eff, launch, treated = dgp.geo_panel(**NB07_PANEL)
    sales = sales_df.values.T
    W = NB07_PANEL["n_weeks"]
    return sales, eff, slice(0, launch), slice(launch, W)


def test_sc_ar1_recovers_lift_and_detects_autocorrelation():
    """The AR(1) synthetic control must (a) still recover the lift, and (b) actually
    find the autocorrelation that the iid model assumes away. geo_panel's macro factor
    is a cumsum (a random walk), and whatever share of it the donor weights fail to match
    is left in the residual as a persistent, slowly-wandering offset."""
    sales, eff, pre, post = _nb07_panel()
    sc = est.synthetic_control_ar1(sales[0], sales[1:], pre, post, seed=1,
                                   draws=300, tune=300, chains=2)
    est_total = sc["effect_samples"][:, post].sum(1).mean()
    true_total = eff[post].sum()
    assert 0.4 * true_total < est_total < 1.6 * true_total
    # The point of the model: it should detect persistence, not assume it away.
    assert sc["rho_samples"].mean() > 0.3, "AR(1) failed to pick up residual persistence"


def test_iv_binary_treatment_recovers_effect_and_endogeneity():
    """The probit-first-stage IV must recover the planted effect on a BINARY treatment,
    and must detect the endogeneity (rho > 0) that makes naive OLS wrong. rho is the
    Bayesian image of the Cov(X, U) that the OVB formula prices."""
    df, true_effect = dgp.iv_ad_exposure(n=3000, true_effect=15.0, seed=37)
    r = est.iv_binary_treatment(df, outcome="sales", treatment="ad_exposure",
                                instrument="encouragement", seed=1,
                                draws=400, tune=400, chains=2)
    beta = r["beta_samples"]
    assert 11.0 < beta.mean() < 19.0, f"failed to recover ~15, got {beta.mean():.1f}"
    # Positive endogeneity is what pushes naive OLS ABOVE the truth in this DGP.
    assert r["rho_samples"].mean() > 0.05


def test_iv_binary_treatment_rejects_continuous_treatment():
    """Silently fitting a probit to a continuous regressor would be a wrong answer with
    no error message — the worst kind. It must refuse."""
    df, _ = dgp.iv_ad_exposure(n=200, seed=1)
    df = df.copy()
    df["ad_exposure"] = np.linspace(0, 3, len(df))       # not 0/1
    with pytest.raises(ValueError, match="0/1 treatment"):
        est.iv_binary_treatment(df, outcome="sales", treatment="ad_exposure",
                                instrument="encouragement", draws=10, tune=10, chains=1)


def test_sc_ar1_total_is_wider_than_iid():
    """THE regression guard for the nb07 fix.

    An iid likelihood prices the H-week cumulative total at Var = H*sigma^2. Under a
    persistent error the truth grows toward H^2*sigma^2, so the iid model is
    over-confident about exactly the number the euro decision consumes. The AR(1)
    model must therefore produce a materially WIDER posterior on the post-period
    total. If this ever flips, the AR(1) residual is no longer being propagated
    forward and nb07's headline claim is false.

    Measured on this panel: iid sd ~27k against a true sampling sd of ~59k (2.2x
    over-confident); AR(1) sd ~72k. Across 24 panels the nominal-90% interval on the
    total covers the truth 50% of the time under iid and 88% under AR(1).
    """
    sales, eff, pre, post = _nb07_panel()
    kw = dict(seed=1, draws=300, tune=300, chains=2)
    iid = est.synthetic_control(sales[0], sales[1:], pre, post, **kw)
    ar1 = est.synthetic_control_ar1(sales[0], sales[1:], pre, post, **kw)

    sd_iid = iid["effect_samples"][:, post].sum(1).std()
    sd_ar1 = ar1["effect_samples"][:, post].sum(1).std()
    assert sd_ar1 > 1.5 * sd_iid, (
        f"AR(1) total sd ({sd_ar1:.0f}) should be much wider than iid ({sd_iid:.0f}); "
        "the post-period residual is probably not being propagated."
    )


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


def test_pathmc_segment_cate_recovers():
    """nb02's headline claim, as a content guard (not just 'the notebook runs'):
    the structural model recovers the planted per-segment email effects (€7 low /
    €16 high at mean engagement) with each truth inside its HDI, and the segments
    separate. Small fast fit; pathmc is a core-env dependency."""
    pathmc = pytest.importorskip("pathmc")
    df, true = dgp.segment_customers(n=1200, seed=3)
    df["is_high"] = (df["prior_value"] == "high").astype(float)
    spec = ("spend ~ b_e*email + b_v*is_high + b_ev*email:is_high "
            "+ b_eg*email:engagement + b_g*engagement + b_tr*trend")
    m = pathmc.model(spec, data=df)
    m.fit(random_seed=1, progressbar=False, draws=300, tune=300, chains=2, cores=1)
    hi = m.cate("spend", "email", condition={"is_high": 1.0, "engagement": 0.5}, values=(0, 1))
    lo = m.cate("spend", "email", condition={"is_high": 0.0, "engagement": 0.5}, values=(0, 1))
    assert hi.mean() > lo.mean()                       # the two segments separate
    hlo, hhi = hi.hdi(); llo, lhi = lo.hdi()
    assert hlo <= true["high"] <= hhi                  # €16 recovered (truth in HDI)
    assert llo <= true["low"] <= lhi                   # €7 recovered (truth in HDI)


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


# --------------------------------------------------------------------------
# metrics / estimators — value (not just ordering) guards on the fragile stats
# --------------------------------------------------------------------------
def test_auuc_perfect_and_reversed():
    """Oracle-normalized Qini coefficient has fixed endpoints: auuc(tau, tau) == 1
    (perfect ranking) and a reversed ranker scores below 0."""
    tau = np.random.default_rng(0).normal(5, 3, 500)
    assert abs(metrics.auuc(tau, tau) - 1.0) < 1e-6
    assert metrics.auuc(-tau, tau) < 0.0


def test_qini_observed_endpoint_is_naive_uplift():
    """The observable Qini (no tau_true) ends at n_treated*(mean_treated -
    mean_control) — the naive randomized uplift scaled to the base."""
    rng = np.random.default_rng(1)
    n = 2000
    T = rng.integers(0, 2, n).astype(float)
    y = 2.0 * T + rng.normal(0, 1, n)
    _, cum = metrics.qini_observed(rng.normal(0, 1, n), T, y)
    approx = int(T.sum()) * (y[T == 1].mean() - y[T == 0].mean())
    assert abs(cum[-1] - approx) < 1e-6


def test_first_stage_F_matches_closed_form():
    """first_stage_F equals the textbook R²-based homoskedastic F on fixed data."""
    rng = np.random.default_rng(2)
    z = rng.normal(0, 1, 400)
    t = 0.8 * z + rng.normal(0, 1, 400)
    F = est.first_stage_F(z, t)
    n = len(t); Z = np.column_stack([np.ones(n), z])
    b, *_ = np.linalg.lstsq(Z, t, rcond=None)
    r2 = 1 - ((t - Z @ b) ** 2).sum() / ((t - t.mean()) ** 2).sum()
    F_ref = (r2 / 1) / ((1 - r2) / (n - 2))
    assert abs(F - F_ref) < 1e-6 and F > 10


def test_sc_weights_slsqp_recovers_single_donor():
    """Target == one donor exactly → SLSQP puts ~all weight on it, and the weights
    are a valid simplex (non-negative, sum to 1) after the clip/renormalize guard."""
    rng = np.random.default_rng(3)
    donors_pre = rng.normal(0, 1, (5, 30))
    target_pre = donors_pre[2].copy()
    w = est.sc_weights_slsqp(target_pre, donors_pre)
    assert abs(w.sum() - 1.0) < 1e-6 and (w >= -1e-9).all()
    assert w[2] > 0.9


def test_placebo_in_space_all_filtered_raises():
    """When the RMSE gate discards every placebo, placebo_in_space raises rather
    than silently returning a garbage p-value from an empty pool."""
    sales = np.random.default_rng(4).normal(0, 1, (6, 40))
    with pytest.raises(ValueError):
        est.placebo_in_space(sales, treated_idx=0, pre=slice(0, 20), post=slice(20, 40),
                             pre_rmse=1e-12, rmse_multiple=1.0)
