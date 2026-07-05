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


def qini_curve(cate_point: np.ndarray, tau_true: np.ndarray):
    """Oracle-truth Qini/uplift curve: cumulative incremental true effect
    captured as we target in descending order of estimated CATE. Because we
    know `tau_true`, this is the exact realised uplift, not an estimate.

    Returns (frac, cum_model, cum_random, cum_oracle) — the model policy, the
    random-targeting diagonal, and the best-possible (oracle) curve."""
    n = len(tau_true)
    frac = np.arange(1, n + 1) / n
    order = np.argsort(-cate_point)
    cum_model = np.cumsum(tau_true[order])
    cum_oracle = np.cumsum(np.sort(tau_true)[::-1])
    cum_random = frac * tau_true.sum()
    return frac, cum_model, cum_random, cum_oracle


def auuc(cate_point: np.ndarray, tau_true: np.ndarray, normalized: bool = True) -> float:
    """Area Under the Uplift Curve above the random line. If normalized,
    expressed as a fraction of the oracle's area (1.0 = perfect ranking,
    0.0 = no better than random). The single-number summary of how well the
    model *ranks* customers by effect."""
    frac, cum_model, cum_random, cum_oracle = qini_curve(cate_point, tau_true)
    _trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))  # numpy 2.x renamed trapz
    area_model = _trapz(cum_model - cum_random, frac)
    area_oracle = _trapz(cum_oracle - cum_random, frac)
    if normalized:
        return float(area_model / area_oracle) if area_oracle != 0 else float("nan")
    return float(area_model)


def uplift_by_decile(cate_point: np.ndarray, tau_true: np.ndarray, n_bins: int = 10):
    """Average TRUE effect within each decile of predicted CATE (decile 1 =
    highest predicted). A well-ranking model shows a monotone staircase; the
    top deciles are where targeting pays. Returns a DataFrame."""
    order = np.argsort(-cate_point)
    tau_ord = tau_true[order]
    pred_ord = cate_point[order]
    splits = np.array_split(np.arange(len(tau_true)), n_bins)
    rows = []
    for i, idx in enumerate(splits, 1):
        rows.append({
            "decile": i,
            "pred_cate": float(pred_ord[idx].mean()),
            "true_effect": float(tau_ord[idx].mean()),
            "n": len(idx),
        })
    return pd.DataFrame(rows)


def reliability_curve(cate_point: np.ndarray, tau_true: np.ndarray, n_bins: int = 10):
    """Calibration of the point estimate: binned predicted CATE vs binned
    realised true effect. On the 45-degree line = well-calibrated magnitudes
    (not just ranking). Returns (pred_binned, true_binned)."""
    bins = pd.qcut(cate_point, n_bins, labels=False, duplicates="drop")
    dfb = pd.DataFrame({"pred": cate_point, "true": tau_true, "bin": bins})
    g = dfb.groupby("bin").mean()
    return g["pred"].values, g["true"].values


def sharpness(cate_samples: np.ndarray, level: float = 0.90) -> float:
    """Average width of the per-unit credible interval — how *decisive* the
    posterior is. Sharp + calibrated is the goal; sharp + miscalibrated is
    overconfidence. Report alongside coverage, never alone."""
    alpha = 1 - level
    lo, hi = np.quantile(cate_samples, [alpha / 2, 1 - alpha / 2], axis=0)
    return float(np.mean(hi - lo))


def e_value(estimate: float, cost: float = 0.0) -> float:
    """VanderWeele-Ding E-value on a risk-ratio-like scale: the minimum
    strength of association (on the RR scale) that an unmeasured confounder
    would need with BOTH treatment and outcome to explain away the estimate
    down to the `cost` threshold. Larger = more robust. We map an additive
    effect to an approximate RR via (estimate/(estimate-cost)) guarded to >1."""
    rr = max(abs(estimate) / max(abs(estimate - cost), 1e-6), 1.0 + 1e-6)
    return float(rr + np.sqrt(rr * (rr - 1)))


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
