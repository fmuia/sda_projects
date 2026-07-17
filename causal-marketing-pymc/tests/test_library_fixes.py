"""Regression guards for the library defects found in the 2026-07-14 correctness audit.

Every test here FAILS on the code as it stood before its fix. That is the point: each one pins a
bug that was silent, shipped numbers into the book, and would otherwise come back.
"""
import subprocess
import sys
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from cmp import cache, dgp, estimators as est


# ---------------------------------------------------------------------------------------------
# The fit cache key ignored the MODEL. Changing a prior/likelihood/DGP while the declared `inputs`
# stayed the same served the OLD posterior back, silently — so every diagnostic downstream graded
# a model that no longer existed, and it looked clean.
# ---------------------------------------------------------------------------------------------
REPO = Path(__file__).resolve().parent.parent
_PROBE = (
    "import numpy as np\n"
    "from cmp import cache, estimators as est, dgp\n"
    "df,_,_,t = dgp.geo_panel(seed=3); s = df.values.T\n"
    "fn = lambda: est.synthetic_control(s[0], np.delete(s,0,axis=0), slice(0,40), slice(40,60), seed=1)\n"
    "print(cache._code_fingerprint(fn))\n"
)


def _fingerprint_in_subprocess() -> str:
    r = subprocess.run([sys.executable, "-c", _PROBE], capture_output=True, text=True, cwd=REPO)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_cache_key_tracks_the_model_source():
    """Edit the model on disk; the cache key MUST move. This is the guard for the worst bug in the
    audit: a silent stale posterior is indistinguishable from a fresh one."""
    path = REPO / "src" / "cmp" / "estimators.py"
    original = path.read_text()
    before = _fingerprint_in_subprocess()
    try:
        path.write_text(original.replace(
            "def synthetic_control(target, donors, pre, post, seed=1, draws=1000, tune=1000, chains=4, target_accept=0.95):",
            "def synthetic_control(target, donors, pre, post, seed=1, draws=1000, tune=1000, chains=4, target_accept=0.95):\n"
            "    # a changed prior would live here",
            1))
        after = _fingerprint_in_subprocess()
    finally:
        path.write_text(original)
    assert before != after, (
        "the cache key did not change when the model's source changed — an edited model will "
        "silently load a STALE posterior"
    )
    assert _fingerprint_in_subprocess() == before, "restoring the source did not restore the key"


def test_cache_code_fingerprint_actually_finds_the_model():
    """A fingerprint of the empty string would 'pass' the test above by accident. It must be a hash
    of real source."""
    df, _te, _lw, _t = dgp.geo_panel(seed=3)
    s = df.values.T
    fn = lambda: est.synthetic_control(s[0], np.delete(s, 0, axis=0), slice(0, 40), slice(40, 60), seed=1)
    import hashlib
    empty = hashlib.sha256(b"").hexdigest()[:12]
    assert cache._code_fingerprint(fn) != empty, "walked no source at all — the guard is vacuous"


def test_cache_fingerprint_does_not_collide_on_truncated_pandas_repr():
    """pandas TRUNCATES its repr (head/tail with an ellipsis). Two frames differing only in the
    middle used to hash identically and share a cached fit."""
    a = pd.DataFrame({"x": list(range(100))})
    b = a.copy()
    b.loc[50, "x"] = -999                       # only the truncated middle differs
    assert cache._fingerprint(a) != cache._fingerprint(b), (
        "two different DataFrames produced the same cache key — repr() truncation strikes again"
    )
    assert cache._fingerprint(a) == cache._fingerprint(a.copy()), "fingerprint is not stable"


# ---------------------------------------------------------------------------------------------
# sc_weights_slsqp returned its equal-weight STARTING POINT while reporting success.
#
# SLSQP's convergence test is absolute (`ftol` on the objective). The geo panel sits at a level of
# ~100-500, so the sum-of-squares objective starts at O(1e4) and SLSQP quits after ~5 iterations,
# reporting success without moving. The old guard checked only `res.success`, which is not a
# convergence test — so the "synthetic control" was the equal-weight average of the donor pool.
# Dozens of placebo fits were degenerate, and they inflated the reported gap-error autocorrelation
# from its true ~0.33 to 0.93.
# ---------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------
# dgp: the latent confounder was DRAWN ONLY when its coefficient was non-zero. That draw consumes
# RNG state, so the strength-0 world was not the strength-0 *version* of the same world — it was a
# different dataset. Every confounding sweep starting at zero compared across unrelated panels, and
# its baseline point was not the control it was presented as.
# ---------------------------------------------------------------------------------------------
def test_zero_confounding_is_the_same_customers_with_the_confounding_switched_off():
    a = dgp.uplift_customers(n=800, regime="observational", confounder_strength=0.0, seed=5)
    b = dgp.uplift_customers(n=800, regime="observational", confounder_strength=1.5, seed=5)
    # the customers themselves are drawn BEFORE the latent, so they must be identical
    for col in ("recency", "frequency", "monetary", "tenure", "engage", "tau", "mu0"):
        assert np.allclose(a[col].values, b[col].values), (
            f"'{col}' differs between confounder_strength 0 and 1.5 at the same seed — the RNG "
            f"stream diverged, so the sweep's baseline is a different dataset, not a control"
        )


# NOTE: price_panel deliberately does NOT share its stream across strengths — see the note in
# dgp.py. nb03 uses two fixed discrete strengths for two separate demonstrations and never sweeps
# from zero, so alignment there would perturb Chapter 5 for no benefit. Only uplift_customers, which
# IS swept from zero (nb01, nb09), needs and gets the alignment guarded above.


def _panel(seed, lift=0.0):
    df, _te, _lw, treated = dgp.geo_panel(n_weeks=60, launch_week=40, n_dmas=30,
                                          lift_pct=lift, seed=seed)
    sales = df.values.T
    ti = list(df.columns).index(treated)
    return sales[ti], np.delete(sales, ti, axis=0)


def test_sc_weights_actually_fit_and_beat_equal_weights():
    """The fit must beat the equal-weight centroid it starts from. This is the check the old
    implementation lacked, and it is the only one that means anything."""
    pre = slice(0, 40)
    for seed in range(6):
        target, donors = _panel(seed)
        T, D = target[pre], donors[:, pre]
        w = est.sc_weights_slsqp(T, D)

        equal = np.full(D.shape[0], 1 / D.shape[0])
        loss = lambda ww: float((T - ww @ D) @ (T - ww @ D))
        assert loss(w) < loss(equal) * 0.5, (
            f"seed {seed}: the fit did not materially beat equal weights "
            f"({loss(w):.1f} vs {loss(equal):.1f}) — SLSQP is stuck at its starting point again"
        )
        assert not np.allclose(w, equal, atol=1e-6), f"seed {seed}: weights never left w0"


def test_sc_weights_are_on_the_simplex():
    pre = slice(0, 40)
    target, donors = _panel(0)
    w = est.sc_weights_slsqp(target[pre], donors[:, pre])
    assert np.all(w >= -1e-9), "negative weight — not on the simplex"
    assert np.isclose(w.sum(), 1.0, atol=1e-6), f"weights sum to {w.sum()}, not 1"


def test_sc_weights_scale_invariant():
    """The bug was a SCALING bug, so the fitted weights must not depend on the units of the panel.
    Multiply the whole panel by 1000 (euros -> thousandths) and the weights must not move."""
    pre = slice(0, 40)
    target, donors = _panel(1)
    w_small = est.sc_weights_slsqp(target[pre], donors[:, pre])
    w_big = est.sc_weights_slsqp(target[pre] * 1000.0, donors[:, pre] * 1000.0)
    assert np.allclose(w_small, w_big, atol=1e-4), (
        "weights changed when the panel was rescaled — the objective is not properly normalised, "
        "which is the exact bug this guards"
    )


def test_sc_weights_degenerate_fit_is_loud_not_silent():
    """A donor pool that genuinely cannot beat its own centroid must WARN (or raise under
    strict=True) rather than hand back equal weights dressed up as a fit."""
    rng = np.random.default_rng(0)
    # donors carrying no signal about the target: nothing can beat the centroid
    target = rng.normal(100, 5, 40)
    donors = np.tile(rng.normal(100, 5, 40), (8, 1))     # 8 identical donors -> no fit possible
    with pytest.raises(RuntimeError, match="did not improve on equal weights"):
        est.sc_weights_slsqp(target, donors, strict=True)


def test_placebo_gap_error_autocorrelation_is_not_the_artifact():
    """The book reports the gap-error autocorrelation on placebo worlds as its evidence that an iid
    likelihood is wrong for a 20-week TOTAL. With the stuck fits it read 0.93 (an artifact of the
    equal-weight 'fits'). Converged, it is ~0.3 — and, crucially, it does NOT decay with lag, which
    is the signature of a persistent level offset rather than short memory. That flatness is the
    mechanism: Var(sum) picks up n^2 Var(offset), not n sigma^2.
    """
    pre, post = slice(0, 40), slice(40, 60)
    E = []
    with warnings.catch_warnings():
        warnings.simplefilter("error", RuntimeWarning)     # any degenerate fit fails this test
        for s in range(12):
            target, donors = _panel(400 + s)
            gap, _w = est.sc_effect_slsqp(target, donors, pre, post)
            E.append(gap[post])
    E = np.asarray(E)

    # about zero, NOT demeaned: in a placebo world the error's true mean is zero, and demeaning a
    # 20-week window would absorb exactly the persistent offset we are trying to expose.
    rho = [float(np.mean(E[:, :-k] * E[:, k:]) / np.mean(E ** 2)) for k in (1, 8)]
    assert 0.15 < rho[0] < 0.6, f"lag-1 autocorrelation {rho[0]:.2f} outside the converged range"
    assert rho[1] > 0.15, (
        f"lag-8 autocorrelation {rho[1]:.2f} has decayed away — the persistent-offset mechanism "
        f"the chapter teaches would not hold"
    )
    assert abs(rho[1] - rho[0]) < 0.25, (
        "the autocorrelation decayed materially with lag; the chapter's claim is that it does NOT, "
        "because the error is a random level shift"
    )


# ---------------------------------------------------------------------------------------------
# iv_2sls hard-coded homoskedastic errors, in a module whose whole discipline is that an estimator
# may not default its covariance choice in silence.
# ---------------------------------------------------------------------------------------------
def test_iv_2sls_covariance_is_a_choice_and_the_sandwich_is_right():
    from cmp import classical as cl

    rng = np.random.default_rng(3)
    n = 20000
    Z = rng.integers(0, 2, n).astype(float)
    U = rng.normal(size=n)
    X = ((0.3 + 1.1 * Z + 0.8 * U + rng.logistic(size=n)) > 0).astype(float)
    Y = 50 + 15 * X + 12 * U + rng.normal(0, 1 + 6 * Z)      # heteroskedastic in Z
    d = pd.DataFrame({"encouragement": Z, "ad_exposure": X, "sales": Y,
                      "region": rng.integers(0, 12, n)})

    # a single binary instrument makes 2SLS the Wald ratio, whose robust SE has an exact
    # delta-method form. The sandwich must reproduce it.
    m = Z == 1
    y1, y0, x1, x0 = Y[m], Y[~m], X[m], X[~m]
    n1, n0 = int(m.sum()), int((~m).sum())
    num, den = y1.mean() - y0.mean(), x1.mean() - x0.mean()
    wald = num / den
    v_num = y1.var(ddof=1) / n1 + y0.var(ddof=1) / n0
    v_den = x1.var(ddof=1) / n1 + x0.var(ddof=1) / n0
    c_nd = np.cov(y1, x1, ddof=1)[0, 1] / n1 + np.cov(y0, x0, ddof=1)[0, 1] / n0
    se_ref = abs(wald) * np.sqrt(v_num / num ** 2 + v_den / den ** 2 - 2 * c_nd / (num * den))

    r = cl.iv_2sls(d, outcome="sales", endog="ad_exposure", instrument="encouragement", cov="HC1")
    assert np.isclose(r.estimate, wald, rtol=1e-6)
    assert np.isclose(r.se, se_ref, rtol=2e-2), (
        f"the HC1 sandwich ({r.se:.4f}) does not match the delta-method robust SE ({se_ref:.4f})"
    )
    assert "HC1" in r.cov

    rc = cl.iv_2sls(d, outcome="sales", endog="ad_exposure", instrument="encouragement",
                    cov="cluster", cluster="region")
    assert rc.extra["n_clusters"] == 12
    assert "cluster" in rc.cov

    with pytest.raises(ValueError, match="requires cluster"):
        cl.iv_2sls(d, outcome="sales", endog="ad_exposure", instrument="encouragement",
                   cov="cluster")


# ---------------------------------------------------------------------------------------------
# The CATE learners could only be scored at the rows they were fitted to, so every uplift and
# policy number in the cookbook was in-sample.
# ---------------------------------------------------------------------------------------------
def test_learners_can_score_held_out_rows():
    d = dgp.uplift_customers(n=400, regime="observational", seed=7)
    feats = ["recency", "frequency", "monetary", "tenure", "engage"]
    X, T, y = d[feats].values, d["T"].values, d["y"].values
    tr, te = slice(0, 300), slice(300, 400)
    P = dict(m=10, draws=50, tune=50, chains=1)

    cate = est.t_learner(X[tr], T[tr], y[tr], seed=1, X_score=X[te], **P)
    assert cate.shape[1] == 100, "X_score did not change the number of scored rows"

    cate_s = est.s_learner(X[tr], T[tr], y[tr], seed=1, X_score=X[te], **P)
    assert cate_s.shape[1] == 100


def test_report_begin_retires_stale_keys(tmp_path, monkeypatch):
    """A key a notebook stops emitting must NOT keep its macro."""
    from cmp import report

    monkeypatch.setenv("CMP_RESULTS_DIR", str(tmp_path))
    monkeypatch.setenv("CMP_FAST", "0")

    report.begin("nb07")
    report.value("nb07.kept", 1.0)
    report.value("nb07.retired", 2.0)
    assert "nb07.retired" in report.load()

    # a later run that no longer emits `retired`
    report.begin("nb07")
    report.value("nb07.kept", 1.0)
    store = report.load()
    assert "nb07.kept" in store
    assert "nb07.retired" not in store, (
        "a retired key kept its macro — the shard was read-modify-written, which is the one way a "
        "stale number can survive the injection pipeline"
    )


def test_report_begin_does_not_touch_the_companion_notebook():
    """nb07.begin() must not delete nb07b's floats — they are separate key-spaces."""
    from cmp import report
    assert report._nb_of("nb07b.sc") == "nb07b"
    with pytest.raises(ValueError):
        report.begin("nb7")          # malformed id must be rejected, not silently glob-delete
