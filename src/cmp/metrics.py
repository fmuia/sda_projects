"""Recovery + calibration metrics for CATE/ATE posteriors.

All CATE arguments are posterior sample arrays of shape (n_samples, n_units),
matching the uniform interface returned by `cmp.estimators`.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def pehe(cate_samples: np.ndarray, tau_true: np.ndarray) -> float:
    """Precision in Estimation of Heterogeneous Effect: RMSE of the
    posterior-mean CATE against the known true effect."""
    point = cate_samples.mean(axis=0)
    return float(np.sqrt(np.mean((point - tau_true) ** 2)))


def ate_bias(cate_samples: np.ndarray, tau_true: np.ndarray) -> float:
    return float(cate_samples.mean() - tau_true.mean())


def interval_coverage(
    cate_samples: np.ndarray,
    tau_true: np.ndarray,
    level: float = 0.90,
    by_decile: bool = False,
):
    """Fraction of units whose credible interval at `level` contains the
    true effect. With by_decile=True, also returns coverage broken out by
    decile of the true effect (a calibration-by-effect-size check) as a
    pandas Series indexed 0..9 (low -> high true effect).
    """
    alpha = 1 - level
    lo, hi = np.quantile(cate_samples, [alpha / 2, 1 - alpha / 2], axis=0)
    inside = (lo <= tau_true) & (tau_true <= hi)
    overall = float(inside.mean())
    if not by_decile:
        return overall
    decile = pd.qcut(tau_true, 10, labels=False, duplicates="drop")
    by_dec = pd.Series(inside, index=decile).groupby(level=0).mean()
    return overall, by_dec


def qini_curve(cate_point: np.ndarray, tau_true: np.ndarray, y=None, T=None):
    """Cumulative incremental true effect captured by targeting in
    descending order of estimated CATE (a validation-set Qini curve built
    directly on the known truth, since we have it here)."""
    order = np.argsort(-cate_point)
    cum_true_effect = np.cumsum(tau_true[order])
    frac = np.arange(1, len(tau_true) + 1) / len(tau_true)
    return frac, cum_true_effect


def corr_with_truth(cate_point: np.ndarray, tau_true: np.ndarray) -> float:
    return float(np.corrcoef(cate_point, tau_true)[0, 1])


def bakeoff_row(cate_samples: np.ndarray, tau_true: np.ndarray, label: str, regime: str, level: float = 0.90) -> dict:
    """One row of the estimator bake-off table: PEHE, correlation, ATE
    bias, and interval coverage, all against the known truth."""
    point = cate_samples.mean(axis=0)
    return {
        "regime": regime,
        "estimator": label,
        "PEHE": pehe(cate_samples, tau_true),
        "corr": corr_with_truth(point, tau_true),
        "ATE_bias": ate_bias(cate_samples, tau_true),
        f"cov{int(level * 100)}": interval_coverage(cate_samples, tau_true, level),
    }
