"""Tests for cmp.design — power, MDE, sample size, peeking, CUPED.

These are closed forms, so we test them against the properties that make them
*true*, not against numbers copied out of the implementation: MDE and sample size
must invert each other, power must hit its target at the sample size that claims
to deliver it, and the peeking simulation must reproduce the ~4x inflation that is
the entire reason the section exists.
"""
import numpy as np
import pytest

from cmp import design as d


def test_mde_and_sample_size_are_inverses():
    """The two most-used functions must agree, or one of them is lying in a
    planning meeting. n(delta = MDE(n)) == n."""
    p0, n = 0.05, 20_000
    mde = d.mde_proportion(p0, n, alpha=0.05, power=0.80)
    n_back = d.sample_size_proportion(p0, mde, alpha=0.05, power=0.80)
    assert n_back == pytest.approx(n, rel=1e-6)


def test_power_at_the_prescribed_sample_size_is_the_target():
    """If sample_size says n gives 80% power, power() must return ~80% at that n."""
    p0, delta = 0.05, 0.01
    n = d.sample_size_proportion(p0, delta, alpha=0.05, power=0.80)
    # The sample-size formula uses the pooled 2p(1-p) variance; power() uses each
    # arm's own p(1-p). They agree to within a fraction of a point, not exactly.
    assert d.power_proportion(p0, delta, n, alpha=0.05) == pytest.approx(0.80, abs=0.02)


def test_sample_size_scales_as_roughly_one_over_delta_squared():
    """Halving the detectable lift must ~quadruple the sample. This is the single
    fact that kills experiment programmes; if it regresses, the notebook lies.

    "Roughly" is not hedging — it is the exact truth. The 1/delta^2 rule comes from
    the textbook formula, which holds the outcome variance fixed. Really the variance
    moves with p1 = p0 + delta (a bigger lift means a higher-variance treated arm), so
    the observed ratio is ~3.7x, not exactly 4x. The notebook says "roughly quadruples"
    for precisely this reason; this test pins the honest number so nobody "corrects"
    the prose to a 4x it does not deliver.
    """
    p0 = 0.05
    n1 = d.sample_size_proportion(p0, 0.02)
    n2 = d.sample_size_proportion(p0, 0.01)
    assert 3.5 < n2 / n1 < 4.1


def test_matches_r_power_prop_test():
    """Cross-validated against R's power.prop.test(p1=0.05, p2=0.06, power=0.8),
    which returns n = 8145 per group. An independent implementation in another
    language is the best available oracle for a closed form like this."""
    n = d.sample_size_proportion(0.05, 0.01, alpha=0.05, power=0.80)
    assert n == pytest.approx(8145, rel=0.01)


def test_mde_shrinks_with_sample_and_grows_with_power():
    p0 = 0.05
    assert d.mde_proportion(p0, 40_000) < d.mde_proportion(p0, 10_000)
    assert d.mde_proportion(p0, 10_000, power=0.95) > d.mde_proportion(p0, 10_000, power=0.80)


def test_mean_variants_invert_too():
    sd, n = 12.0, 5_000
    mde = d.mde_mean(sd, n)
    assert d.sample_size_mean(sd, mde) == pytest.approx(n, rel=1e-6)


# --------------------------------------------------------------------------
# peeking
# --------------------------------------------------------------------------
def test_single_look_respects_alpha():
    """One look, no effect -> the false-positive rate IS alpha. This is the
    control condition: if it fails, the simulation itself is broken."""
    fpr = d.peeking_false_positive_rate(n_per_arm=8_000, n_looks=1, p0=0.10,
                                        alpha=0.05, n_sims=4000, seed=1)
    assert 0.03 < fpr < 0.07


def test_peeking_inflates_the_false_positive_rate():
    """Ten looks on a treatment that does NOTHING should roughly quadruple the
    5% error rate. This is the headline number of the peeking section."""
    fpr = d.peeking_false_positive_rate(n_per_arm=8_000, n_looks=10, p0=0.10,
                                        alpha=0.05, n_sims=4000, seed=1)
    assert fpr > 0.12, f"expected substantial inflation, got {fpr:.1%}"
    assert fpr < 0.35, f"implausibly high; check the simulation ({fpr:.1%})"


def test_more_looks_means_more_false_positives():
    kw = dict(n_per_arm=8_000, p0=0.10, alpha=0.05, n_sims=3000, seed=2)
    assert (d.peeking_false_positive_rate(n_looks=20, **kw)
            > d.peeking_false_positive_rate(n_looks=5, **kw))


# --------------------------------------------------------------------------
# CUPED
# --------------------------------------------------------------------------
def test_cuped_reduces_variance_by_rho_squared():
    """The theory says variance falls by (1 - rho^2). Check it on data where we
    control rho exactly."""
    rng = np.random.default_rng(0)
    n = 20_000
    x = rng.normal(0, 1, n)
    rho = 0.7
    y = rho * x + np.sqrt(1 - rho ** 2) * rng.normal(0, 1, n)
    _, _, reduction = d.cuped_adjust(y, np.zeros(n), x)
    assert reduction == pytest.approx(rho ** 2, abs=0.02)


def test_cuped_preserves_the_treatment_effect():
    """Variance reduction must not move the estimate — otherwise it is not a free
    lunch, it is a bias."""
    rng = np.random.default_rng(1)
    n = 20_000
    t = rng.binomial(1, 0.5, n)
    x = rng.normal(50, 10, n)                       # pre-experiment covariate
    true_effect = 2.0
    y = 0.8 * x + true_effect * t + rng.normal(0, 5, n)

    raw = y[t == 1].mean() - y[t == 0].mean()
    y_adj, _, reduction = d.cuped_adjust(y, t, x)
    adj = y_adj[t == 1].mean() - y_adj[t == 0].mean()

    assert raw == pytest.approx(true_effect, abs=0.25)
    assert adj == pytest.approx(true_effect, abs=0.25)
    assert adj == pytest.approx(raw, abs=0.15)      # same answer...
    assert reduction > 0.5                          # ...with far less noise
