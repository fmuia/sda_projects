"""cmp.classical must recover planted effects and — the part that actually matters —
report *correct* standard errors. A wrong SE is a confident lie, so each estimator is
checked against a DGP whose truth we know, and the covariance choices are checked to
behave the way theory says they must (clustering widens a serially-correlated panel;
2SLS SEs exceed naive second-stage OLS SEs; a weak instrument is flagged).
"""
import numpy as np
import pandas as pd
import pytest

from cmp import classical as cl


def test_diff_in_means_recovers_randomized_ate():
    rng = np.random.default_rng(0)
    n = 4000
    t = rng.binomial(1, 0.5, n)
    y = 10 + 3.0 * t + rng.normal(0, 2, n)          # true ATE = 3
    r = cl.diff_in_means(y, t)
    assert abs(r.estimate - 3.0) < 0.2
    assert r.ci[0] < 3.0 < r.ci[1]
    assert r.significant


def test_ols_recovers_effect_and_closes_the_backdoor():
    rng = np.random.default_rng(1)
    n = 4000
    z = rng.normal(size=n)                           # confounder
    t = rng.binomial(1, 1 / (1 + np.exp(-z)))        # z -> t
    y = 5 + 2.0 * t + 3.0 * z + rng.normal(0, 1, n)  # z -> y ; true effect = 2
    df = pd.DataFrame({"y": y, "t": t, "z": z})
    naive = cl.ols(df, "y ~ t", target="t")
    adj = cl.ols(df, "y ~ t + z", target="t")
    assert naive.estimate > 2.5                      # confounded upward
    assert abs(adj.estimate - 2.0) < 0.15            # backdoor closed
    assert adj.ci[0] < 2.0 < adj.ci[1]


def test_cluster_se_is_wider_than_iid_under_serial_correlation():
    """The Bertrand-Duflo-Mullainathan (2004) point, and the reason cov='cluster' is not
    optional on panels: when the within-unit shocks are SERIALLY CORRELATED, an iid SE
    treats each unit-period as fresh information, wildly overstating how much independent
    data there is — so the interval comes out far too narrow. Clustering on the unit must
    widen it.

    (Note the effect needs the right setup to show: a constant unit *level* shift is
    differenced out by the DiD interaction and clustering would actually SHRINK the SE.
    It is autocorrelated shocks, with the unit fixed effects absorbed, that bite.)
    """
    rng = np.random.default_rng(2)
    units, T, rho = 50, 30, 0.9
    rows = []
    for u in range(units):
        e = 0.0
        g = int(u < units // 2)
        for t in range(T):
            e = rho * e + rng.normal(0, 1)           # AR(1) shock within the unit
            post = int(t >= T // 2)
            rows.append({"u": u, "t": t, "g": g, "post": post,
                         "y": 10 + 2.0 * g * post + e})
    df = pd.DataFrame(rows)
    spec = "y ~ g:post + C(u) + C(t)"                # unit + time FE absorbed
    iid = cl.ols(df, spec, target="g:post", cov="nonrobust")
    clu = cl.ols(df, spec, target="g:post", cov="cluster", cluster="u")
    assert clu.se > 1.5 * iid.se                     # iid is badly anti-conservative here
    assert clu.extra["n_clusters"] == units
    assert "cluster" in clu.cov


def test_did_2x2_recovers_att():
    rng = np.random.default_rng(3)
    units, T = 60, 12
    rows = []
    for u in range(units):
        level = rng.normal(0, 3)
        for t in range(T):
            g = int(u < units // 2)
            post = int(t >= T // 2)
            rows.append({"u": u, "t": t, "g": g, "post": post,
                         "y": 20 + level + 0.5 * t + 4.0 * g * post + rng.normal(0, 1)})
    df = pd.DataFrame(rows)
    r = cl.did_2x2(df, outcome="y", unit="u", time="t", treated="g", post="post")
    assert abs(r.estimate - 4.0) < 0.6
    assert r.ci[0] < 4.0 < r.ci[1]
    assert "cluster" in r.cov


def test_event_study_pre_periods_are_flat_and_post_periods_load():
    rng = np.random.default_rng(4)
    units = 40
    rows = []
    for u in range(units):
        g = int(u < units // 2)
        level = rng.normal(0, 2)
        for k in range(-4, 5):
            eff = 3.0 if (g and k >= 0) else 0.0
            rows.append({"u": u, "k": k, "g": g, "y": 10 + level + eff + rng.normal(0, 0.5)})
    df = pd.DataFrame(rows)
    es = cl.event_study(df, outcome="y", unit="u", rel_time="k", treated="g")
    pre = es[(es.k < 0) & (~es.is_base)]
    post = es[es.k >= 0]
    assert (pre.estimate.abs() < 0.5).all()          # no pre-trend
    assert (post.estimate > 2.0).all()               # effect switches on
    assert (es.loc[es.is_base, "estimate"] == 0).all()


def test_2sls_beats_biased_ols_and_reports_first_stage_F():
    rng = np.random.default_rng(5)
    n = 5000
    u = rng.normal(size=n)                           # unobserved confounder
    z = rng.normal(size=n)                           # instrument
    x = 0.8 * z + 1.2 * u + rng.normal(0, 0.5, n)    # endogenous regressor
    y = 1.0 + 2.0 * x + 3.0 * u + rng.normal(0, 1, n)   # true effect = 2
    df = pd.DataFrame({"y": y, "x": x, "z": z})
    ols_b = cl.ols(df, "y ~ x", target="x")
    iv = cl.iv_2sls(df, outcome="y", endog="x", instrument="z")
    assert ols_b.estimate > 2.5                      # OLS biased up by the confounder
    assert abs(iv.estimate - 2.0) < 0.25             # 2SLS recovers the truth
    assert iv.extra["first_stage_F"] > 100
    assert not iv.extra["weak"]


def test_hand_rolled_second_stage_se_is_too_wide_not_too_narrow():
    """Pins the direction of a classic trap — and of a docstring bug a notebook caught by
    computing instead of trusting the prose.

    Running 2SLS "by hand" (OLS of y on X_hat) gives the right point estimate but the wrong
    SE, because the residual is formed against X_hat instead of X:
        y - X_hat b = (y - X b) + (X - X_hat) b   =>   SSR_naive >= SSR_correct
    The hand-rolled version therefore charges itself for first-stage prediction error and
    comes out TOO WIDE (conservative) — not too narrow, as the folklore often has it.
    """
    import statsmodels.api as sm
    rng = np.random.default_rng(5)
    n = 5000
    u = rng.normal(size=n)
    z = rng.normal(size=n)
    x = 0.8 * z + 1.2 * u + rng.normal(0, 0.5, n)
    y = 1.0 + 2.0 * x + 3.0 * u + rng.normal(0, 1, n)
    df = pd.DataFrame({"y": y, "x": x, "z": z})

    correct = cl.iv_2sls(df, outcome="y", endog="x", instrument="z")
    x_hat = sm.OLS(x, sm.add_constant(z)).fit().fittedvalues
    naive = sm.OLS(y, sm.add_constant(x_hat)).fit()

    assert abs(naive.params[1] - correct.estimate) < 1e-6      # same point estimate...
    assert naive.bse[1] > correct.se                            # ...but a too-WIDE SE
    assert naive.bse[1] / correct.se > 1.2


def test_2sls_flags_a_weak_instrument():
    rng = np.random.default_rng(6)
    n = 800
    u = rng.normal(size=n)
    z = rng.normal(size=n)
    x = 0.02 * z + u + rng.normal(0, 1, n)           # nearly irrelevant instrument
    y = 2.0 * x + 3.0 * u + rng.normal(0, 1, n)
    df = pd.DataFrame({"y": y, "x": x, "z": z})
    iv = cl.iv_2sls(df, outcome="y", endog="x", instrument="z")
    assert iv.extra["first_stage_F"] < 10
    assert iv.extra["weak"]


def test_rd_local_linear_recovers_the_jump():
    rng = np.random.default_rng(7)
    n = 6000
    x = rng.uniform(-1, 1, n)
    y = 1.0 + 2.0 * x + 0.5 * (x >= 0) + rng.normal(0, 0.3, n)   # jump = 0.5 at 0
    df = pd.DataFrame({"y": y, "x": x})
    r = cl.rd_local_linear(df, outcome="y", running="x", cutoff=0.0, bandwidth=0.5)
    assert abs(r.estimate - 0.5) < 0.1
    assert r.ci[0] < 0.5 < r.ci[1]
    assert r.extra["bandwidth"] == 0.5


def test_segmented_its_recovers_level_and_slope_with_hac():
    rng = np.random.default_rng(8)
    T = 300
    t = np.arange(T, dtype=float)
    post = (t >= 150).astype(float)
    since = np.clip(t - 150, 0, None)
    y = 100 + 0.2 * t + 5.0 * post + 0.1 * since + rng.normal(0, 1, T)
    df = pd.DataFrame({"y": y, "t": t})
    r = cl.segmented_its(df, outcome="y", time="t", intervention=150, maxlags=7)
    assert abs(r["level"].estimate - 5.0) < 1.0
    assert abs(r["slope"].estimate - 0.1) < 0.05
    assert "HAC" in r["level"].cov


def test_mediation_product_recovers_indirect_and_direct():
    rng = np.random.default_rng(9)
    n = 4000
    tt = rng.binomial(1, 0.5, n)
    m = 1.0 + 2.0 * tt + rng.normal(0, 1, n)           # a = 2
    y = 3.0 + 1.5 * tt + 4.0 * m + rng.normal(0, 1, n)  # c = 1.5, b = 4 => NIE = 8
    df = pd.DataFrame({"y": y, "t": tt, "m": m})
    r = cl.mediation_product(df, outcome="y", treatment="t", mediator="m", n_boot=300, seed=1)
    assert abs(r["nie"].estimate - 8.0) < 0.5
    assert abs(r["nde"].estimate - 1.5) < 0.3
    assert r["nie"].ci[0] < 8.0 < r["nie"].ci[1]
    assert "bootstrap" in r["nie"].cov


def test_no_pooling_is_noisier_on_thin_groups_than_complete_pooling():
    """The bias-variance bracket partial pooling interpolates between."""
    rng = np.random.default_rng(10)
    rows = []
    for g, n_g in enumerate([500, 500, 20, 15]):       # two fat groups, two thin ones
        for _ in range(n_g):
            t = rng.binomial(1, 0.5)
            rows.append({"g": g, "t": t, "y": 5 + 2.0 * t + rng.normal(0, 3)})
    df = pd.DataFrame(rows)
    np_ = cl.no_pooling(df, formula="y ~ t", target="t", group="g")
    cp = cl.complete_pooling(df, formula="y ~ t", target="t")
    thin = np_[np_.n < 50].width.mean()
    fat = np_[np_.n > 100].width.mean()
    assert thin > fat                                  # thin groups -> wild, wide estimates
    assert (cp.ci[1] - cp.ci[0]) < fat                 # pooling buys precision (at a bias risk)


def test_classical_result_states_what_it_cannot_say():
    """The interpretive guardrail: the notebooks must never read a CI as a posterior."""
    r = cl.diff_in_means([1, 2, 3, 4, 5, 6], [0, 0, 0, 1, 1, 1])
    msg = r.cannot_say()
    assert "does NOT say" in msg and "posterior" in msg
    assert "procedure" in msg


def test_bootstrap_ci_is_still_a_confidence_interval():
    rng = np.random.default_rng(11)
    x = rng.normal(5, 2, 500)
    r = cl.bootstrap_ci(x, np.mean, n_boot=300, name="mean")
    assert abs(r.estimate - 5) < 0.3
    assert r.ci[0] < 5 < r.ci[1]
    assert "bootstrap" in r.cov
