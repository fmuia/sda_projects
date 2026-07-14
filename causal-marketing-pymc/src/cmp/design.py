"""Experiment design — the part that happens BEFORE any data exists.

Power, minimum detectable effect, sample size, and the two ways teams manufacture
false wins (peeking, and metric-shopping). Everything here is deliberately
frequentist and deliberately simple: these are *design* calculations, made when
there is no data to put a likelihood on, and a closed form you can defend in a
planning meeting beats a sampler nobody in the room can audit.

Deliberately dependency-light (numpy + scipy only) so this module also runs in the
browser under Pyodide — `apps/experiment_design.py` is the interactive companion,
and it must stay WASM-safe. See `cmp.classical` for the *analysis* counterparts.
"""
from __future__ import annotations

import numpy as np
from scipy import stats
from scipy.optimize import brentq

__all__ = [
    "mde_proportion", "sample_size_proportion", "power_proportion",
    "mde_mean", "sample_size_mean",
    "peeking_false_positive_rate", "cuped_adjust",
]


# --------------------------------------------------------------------------
# Two-proportion tests (conversion, click, churn — the usual A/B outcome)
# --------------------------------------------------------------------------
def _z(alpha: float, power: float) -> tuple[float, float]:
    return stats.norm.ppf(1 - alpha / 2), stats.norm.ppf(power)


def power_proportion(p0: float, delta: float, n_per_arm: float,
                     alpha: float = 0.05) -> float:
    """Power of a two-sided two-proportion test — the primitive everything else
    inverts.

    The test statistic is standardized by the POOLED variance (that is what the
    null says the world looks like), but under the alternative the two arms really
    do have different variances, so the alternative's spread is the UNPOOLED one.
    Conflating the two is the classic way to overstate power by several points:

        reject when |p1 - p0| > z_{a/2} * sqrt(2*pbar*(1-pbar)/n)      [null's scale]
        but the estimate is actually spread as sqrt((v0 + v1)/n)        [truth's scale]

    This matches R's `power.prop.test`. `mde_proportion` and `sample_size_proportion`
    are numeric inversions of THIS function, so the three can never disagree — a
    closed form for each would have to re-derive the same algebra and, in an earlier
    draft of this module, silently disagreed by ~4 points of power.
    """
    p1 = p0 + delta
    if not (0 < p1 < 1):
        raise ValueError(f"p0 + delta = {p1:.3f} is outside (0, 1)")
    za = stats.norm.ppf(1 - alpha / 2)
    pbar = (p0 + p1) / 2
    se_null = np.sqrt(2 * pbar * (1 - pbar) / n_per_arm)
    se_alt = np.sqrt((p0 * (1 - p0) + p1 * (1 - p1)) / n_per_arm)
    crit = za * se_null
    return float(stats.norm.cdf((abs(delta) - crit) / se_alt)
                 + stats.norm.cdf((-abs(delta) - crit) / se_alt))


def sample_size_proportion(p0: float, delta: float, alpha: float = 0.05,
                           power: float = 0.80) -> float:
    """Users PER ARM needed to detect an absolute lift `delta` at the target power.

    Note the ~1/delta^2 scaling: halving the lift you want to catch roughly
    QUADRUPLES the users you need. This single fact kills more experiment programmes
    than any other, and it is why "let's just test it" is never free.

    Solved by inverting `power_proportion` (Brent), so it is exactly consistent with
    it rather than approximately so.
    """
    if delta == 0:
        return float("inf")
    lo, hi = 2.0, 1e9
    f = lambda n: power_proportion(p0, delta, n, alpha) - power
    if f(hi) < 0:
        return float("inf")                       # unreachable power at any feasible n
    if f(lo) > 0:
        return lo
    return float(brentq(f, lo, hi, xtol=1e-4))


def mde_proportion(p0: float, n_per_arm: float, alpha: float = 0.05,
                   power: float = 0.80) -> float:
    """Smallest ABSOLUTE lift detectable with `power` at `alpha`, given n per arm.

    This is the honest headline for any test that "found nothing": *we could detect
    a lift of X or larger; we did not, so the effect — if any — is probably below X.*
    A null result reported without its MDE is not a finding, it is a shrug.

    Also an inversion of `power_proportion`, for the same reason.
    """
    f = lambda d: power_proportion(p0, d, n_per_arm, alpha) - power
    lo, hi = 1e-9, min(0.99 - p0, 1.0) - 1e-9
    if f(hi) < 0:
        return float("nan")                       # even a huge lift is undetectable at this n
    return float(brentq(f, lo, hi, xtol=1e-10))


# --------------------------------------------------------------------------
# Continuous outcomes (revenue, order value, time-on-site)
# --------------------------------------------------------------------------
def mde_mean(sd: float, n_per_arm: int, alpha: float = 0.05,
             power: float = 0.80) -> float:
    """MDE for a two-sample difference in means with known/estimated sd."""
    za, zb = _z(alpha, power)
    return float((za + zb) * sd * np.sqrt(2.0 / n_per_arm))


def sample_size_mean(sd: float, delta: float, alpha: float = 0.05,
                     power: float = 0.80) -> float:
    """Users per arm to detect a mean difference `delta` at a given sd."""
    za, zb = _z(alpha, power)
    return float(2 * (za + zb) ** 2 * sd ** 2 / delta ** 2)


# --------------------------------------------------------------------------
# How tests get broken
# --------------------------------------------------------------------------
def peeking_false_positive_rate(n_per_arm: int, n_looks: int, p0: float,
                                alpha: float = 0.05, n_sims: int = 2000,
                                seed: int = 0) -> float:
    """Simulate the true false-positive rate of a team that peeks `n_looks` times
    and ships at the first significant result — when the treatment does NOTHING.

    The alpha you *declare* is a per-look error rate. The alpha you *incur* is the
    probability that ANY look crosses the line, and those chances accumulate. Ten
    looks turn a nominal 5% into roughly 20%: one in five "wins" is noise.

    Returns the realised false-positive rate (compare it to `alpha`).
    """
    rng = np.random.default_rng(seed)
    checkpoints = np.linspace(n_per_arm / n_looks, n_per_arm, n_looks).astype(int)
    increments = np.diff(np.concatenate([[0], checkpoints]))
    za = stats.norm.ppf(1 - alpha / 2)

    cum_a = np.zeros(n_sims)
    cum_b = np.zeros(n_sims)
    hit = np.zeros(n_sims, dtype=bool)
    seen = 0
    for inc in increments:
        cum_a += rng.binomial(inc, p0, size=n_sims)
        cum_b += rng.binomial(inc, p0, size=n_sims)   # SAME rate: no effect, by construction
        seen += inc
        pa, pb = cum_a / seen, cum_b / seen
        se = np.sqrt(pa * (1 - pa) / seen + pb * (1 - pb) / seen)
        se = np.where(se == 0, np.inf, se)
        hit |= np.abs((pb - pa) / se) > za            # a peeker stops at the FIRST win
    return float(hit.mean())


def cuped_adjust(y, t, x):
    """CUPED — variance reduction using a PRE-experiment covariate.

    The highest-return trick in industrial A/B testing, and it is one line of
    algebra: replace the outcome y with

        y_cuped = y - theta * (x - mean(x)),    theta = Cov(y, x) / Var(x),

    where `x` is measured BEFORE randomization (last month's spend, prior visits).
    The adjusted outcome has the same expectation in each arm — so the treatment
    effect is unchanged and unbiased — but a smaller variance, by a factor of
    (1 - rho^2) where rho = corr(y, x). A covariate correlated 0.7 with the outcome
    cuts the variance in half, which is the same as doubling your sample for free.

    `x` MUST be pre-treatment. Adjusting for anything measured after randomization
    reintroduces exactly the selection bias the coin flip removed — the same error
    as conditioning on a post-treatment variable (see notebook 05).

    Returns (y_adjusted, theta, variance_reduction_fraction).
    """
    y = np.asarray(y, dtype=float)
    x = np.asarray(x, dtype=float)
    theta = float(np.cov(y, x, ddof=1)[0, 1] / np.var(x, ddof=1))
    y_adj = y - theta * (x - x.mean())
    reduction = 1.0 - np.var(y_adj, ddof=1) / np.var(y, ddof=1)
    return y_adj, theta, float(reduction)
